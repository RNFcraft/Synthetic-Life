from dataclasses import replace
import os,subprocess,sys

import pytest

from config import Settings
from consciousness.cognit import Cognit
from consciousness.language import GroundingContextEntry,GroundingContextSnapshot,LanguageFrame,LanguageUtteranceFrame
from consciousness.native_engine import RuntimeEventType
from consciousness.relation import RelationType
from persistence import load_container,save_container
from simulation import ContinuousRuntime,Simulation
from tests.test_v054_embodied_grounding import _observe


def _core(runtime):return runtime.simulation.core


def _relation(runtime,source,target,kind=RelationType.SEQUENTIAL):
    return next((r for r in _core(runtime).graph.outgoing(source) if r.target_id==target and r.relation_type is kind),None)


def _ground_words(tokens=("dax","wug","blicket")):
    settings=replace(Settings(),language_min_support=1,language_min_lift=0.,language_min_background_seconds=0.)
    runtime=ContinuousRuntime(700,settings);runtime.run_to_quiescence();core=_core(runtime);targets=[]
    for n,token in enumerate(tokens,1):
        target=core.graph.add_cognit(Cognit(core.graph.next_id,kind="GENERAL",confidence=.8)).id;targets.append(target);core.grounding_context.latest=None;core.grounding_context.historical.clear();core.grounding_context.accounted_until=0.;core.grounding_context.observe(GroundingContextSnapshot(0.,n,(GroundingContextEntry(target,1.),)));core.process_language(LanguageFrame(n,0.,token))
    core.grounding_context.latest=None;core.grounding_context.historical.clear();core.grounding_context.accounted_until=0.
    return runtime,targets


def test_utterance_frame_validation_and_single_token_compatibility():
    assert LanguageUtteranceFrame(1,2.,(" dax ","wug")).tokens==("dax","wug")
    with pytest.raises(ValueError):LanguageUtteranceFrame(1,0.,())
    with pytest.raises(ValueError):LanguageUtteranceFrame(1,0.,("two tokens",))
    with pytest.raises(TypeError):ContinuousRuntime(701).inject_utterance("dax")
    runtime=ContinuousRuntime(701);runtime.run_to_quiescence();before=_core(runtime).cognitive_tick;message=runtime.inject_utterance(("dax",));runtime.run_to_quiescence()
    assert message==1 and _core(runtime).cognitive_tick==before+1 and runtime.last_utterance_result is None and not _core(runtime).language.sequence_support
    with pytest.raises(ValueError):runtime.inject_utterance(tuple(f"w{i}" for i in range(runtime.simulation.settings.language_max_tokens_per_utterance+1)))


def test_frontier_one_work_item_same_worldtime_and_order():
    runtime=ContinuousRuntime(702);runtime.run_to_quiescence();start_tick=_core(runtime).cognitive_tick;message=runtime.inject_utterance(("dax","wug"),runtime.world_time)
    event=runtime.scheduler.pop_ready(runtime.world_time)[0];assert event.type==RuntimeEventType.LANGUAGE_INPUT;runtime._process(event);assert runtime.language_frontier.next_token_index==0
    event=runtime.scheduler.pop_ready(runtime.world_time)[0];runtime._process(event);assert runtime.language_frontier.next_token_index==1 and _core(runtime).cognitive_tick==start_tick+1
    event=runtime.scheduler.pop_ready(runtime.world_time)[0];runtime._process(event);assert runtime.language_frontier.phase=="COMPOSE" and _core(runtime).cognitive_tick==start_tick+2
    event=runtime.scheduler.pop_ready(runtime.world_time)[0];runtime._process(event);assert runtime.language_frontier is None and _core(runtime).cognitive_tick==start_tick+3
    result=runtime.last_utterance_result;assert result.message_id==message and result.world_time==runtime.world_time and result.ordered_symbol_ids==tuple(_core(runtime).language.symbols[x] for x in ("dax","wug"))


def test_directional_sequence_learning_no_cross_utterance_and_permutation():
    def run(order):
        runtime=ContinuousRuntime(703)
        for _ in range(3):runtime.inject_utterance(order);runtime.run_to_quiescence()
        return runtime
    forward=run(("dax","wug"));reverse=run(("wug","dax"));fd,fw=(_core(forward).language.symbols[x] for x in ("dax","wug"));rd,rw=(_core(reverse).language.symbols[x] for x in ("dax","wug"))
    assert _relation(forward,fd,fw) is not None and _relation(forward,fw,fd) is None
    assert _relation(reverse,rw,rd) is not None and _relation(reverse,rd,rw) is None
    separate=ContinuousRuntime(704)
    for token in ("dax","wug"):separate.inject_language(token);separate.run_to_quiescence()
    assert not separate.simulation.core.language.sequence_support


def test_queued_utterances_complete_without_token_interleaving():
    runtime=ContinuousRuntime(713);runtime.run_to_quiescence();runtime.inject_utterance(("dax","wug"));runtime.inject_utterance(("blicket","zorp"));runtime.run_to_quiescence();symbols=_core(runtime).language.symbols
    assert [symbols[x] for x in ("dax","wug","blicket","zorp")]==sorted(symbols.values())
    assert _core(runtime).language.sequence_support=={symbols["dax"]:{symbols["wug"]:1},symbols["blicket"]:{symbols["zorp"]:1}}


def test_sequence_evidence_order_invariance_and_duplicate_tokens():
    curricula=(("dax","wug"),("dax","blicket"),("dax","wug")),(("dax","wug"),("dax","wug"),("dax","blicket"))
    states=[]
    for curriculum in curricula:
        runtime=ContinuousRuntime(705)
        for utterance in curriculum:runtime.inject_utterance(utterance);runtime.run_to_quiescence()
        source=_core(runtime).language.symbols["dax"];states.append((_core(runtime).language.to_dict(),sorted((r.target_id,r.strength,r.confidence,r.prediction_probability,r.support) for r in _core(runtime).graph.outgoing(source))))
    assert states[0]==states[1]
    duplicate=ContinuousRuntime(706)
    for _ in range(2):duplicate.inject_utterance(("dax","dax"));duplicate.run_to_quiescence()
    symbol=_core(duplicate).language.symbols["dax"];assert _core(duplicate).language.sequence_support[symbol][symbol]==2 and _relation(duplicate,symbol,symbol) is not None


def test_first_occurrence_composes_grounded_constituents_before_sequence_birth():
    runtime,(a,b,_)=_ground_words();core=_core(runtime);dax,wug=(core.language.symbols[x] for x in ("dax","wug"));assert _relation(runtime,dax,wug) is None and not core.language.sequence_support
    trials=dict(core.language.grounded_trials);evidence={k:dict(v) for k,v in core.language.evidence.items()};runtime.inject_utterance(("dax","wug"));runtime.run_to_quiescence();result=runtime.last_utterance_result
    assert a in result.token_results[0].wave.active_ids and b in result.token_results[1].wave.active_ids and {a,b}.issubset(result.composed_active_ids)
    assert core.language.grounded_trials==trials and core.language.evidence==evidence and core.language.sequence_support[dax][wug]==1 and _relation(runtime,dax,wug) is None


def test_real_embodied_first_occurrence_composition():
    runtime=ContinuousRuntime(720,replace(Settings(),object_count=0,max_objects=0,language_min_background_seconds=.3));runtime.run_to_quiescence();core=_core(runtime);t=0.;generation=0
    for label in "ABABAB":generation+=1;t+=1.2;_observe(runtime,label,t,generation)
    for _ in range(5):
        for label,token in (("A","dax"),("B","wug")):generation+=1;t+=1.2;_observe(runtime,label,t,generation);core.process_language(LanguageFrame(generation,t+.1,token))
    generation+=1;t+=1.2;rep_a=_observe(runtime,"A",t,generation);generation+=1;t+=1.2;rep_b=_observe(runtime,"B",t,generation);dax,wug=(core.language.symbols[x] for x in ("dax","wug"));assert _relation(runtime,dax,wug) is None
    cue_time=t+.1;core.grounding_context.accrue(cue_time);core.grounding_context.latest=None;core.grounding_context.historical.clear();core.grounding_context.accounted_until=cue_time;core.continuous_frontier=None;runtime.scheduler.restore(cue_time,runtime.scheduler.next_id,[]);runtime.inject_utterance(("dax","wug"),cue_time);runtime.run_to_quiescence();result=runtime.last_utterance_result
    assert result.token_results[0].wave.active_ids&(rep_a-rep_b) and result.token_results[1].wave.active_ids&(rep_b-rep_a) and result.composed_active_ids&rep_a and result.composed_active_ids&rep_b


def test_novel_combination_unknown_neutrality_and_order_distinction():
    runtime,(a,_,c)=_ground_words();core=_core(runtime);runtime.inject_utterance(("dax","blicket"));runtime.run_to_quiescence();first=runtime.last_utterance_result
    assert a in first.composed_active_ids and c in first.composed_active_ids
    runtime.inject_utterance(("blicket","dax"));runtime.run_to_quiescence();reverse=runtime.last_utterance_result;assert first.ordered_symbol_ids==tuple(reversed(reverse.ordered_symbol_ids)) and first.sequence_edges!=reverse.sequence_edges
    before=set(core.graph.nodes);runtime.inject_utterance(("dax","zorp"));runtime.run_to_quiescence();unknown=core.language.symbols["zorp"];assert unknown not in runtime.last_utterance_result.composed_active_ids and a in runtime.last_utterance_result.composed_active_ids and unknown not in before


def test_frozen_embodied_context_shared_by_all_tokens_and_no_action_goal_effect():
    runtime,(a,b,_)=_ground_words(("dax","wug","blicket"));core=_core(runtime);c=core.graph.add_cognit(Cognit(core.graph.next_id,kind="GENERAL")).id;core.grounding_context.observe(GroundingContextSnapshot(0.,4,(GroundingContextEntry(c,.75),)));before_trials=dict(core.language.grounded_trials);before_evidence={k:dict(v) for k,v in core.language.evidence.items()};before_sequence=runtime.simulation.event_sequence.value;before_goal=core.state.goal
    runtime.inject_utterance(("dax","wug"),0.);runtime.run_to_quiescence()
    for token in ("dax","wug"):
        assert core.language.grounded_trials[token]==before_trials[token]+1 and core.language.evidence[token][c]==(1,.75)
        assert all(core.language.evidence[token][target]==value for target,value in before_evidence[token].items())
    assert runtime.simulation.event_sequence.value==before_sequence and core.state.goal is before_goal


def test_capacity_and_sequence_candidate_bounds():
    settings=replace(Settings(),max_cognits=3,language_max_sequence_candidates_per_symbol=2,language_sequence_min_support=1,max_relations=2,max_new_relations_per_tick=1);runtime=ContinuousRuntime(707,settings)
    for n in range(8):runtime.inject_utterance(("dax",f"w{n}"));runtime.run_to_quiescence()
    core=_core(runtime);source=core.language.symbols["dax"];assert len(core.graph.nodes)<=3 and len(core.language.sequence_support.get(source,{}))<=2 and core.graph.relation_count<=2 and core.backend.full_graph_sync_calls==0
    assert any(x is None for x in runtime.last_utterance_result.ordered_symbol_ids)


def test_seworld_v7_mid_utterance_exact_continuation_and_v6_migration(tmp_path):
    runtime=ContinuousRuntime(708);runtime.run_to_quiescence();runtime.inject_utterance(("dax","wug","blicket"));runtime._process(runtime.scheduler.pop_ready(runtime.world_time)[0]);runtime._process(runtime.scheduler.pop_ready(runtime.world_time)[0]);runtime._process(runtime.scheduler.pop_ready(runtime.world_time)[0]);assert runtime.language_frontier.next_token_index==2
    path=tmp_path/"mid.seworld";runtime.save_world(path);loaded=ContinuousRuntime.load_world(path);runtime.run_to_quiescence();loaded.run_to_quiescence()
    assert runtime.scheduler_state()==loaded.scheduler_state() and _core(runtime).cognitive_tick==_core(loaded).cognitive_tick and _core(runtime).language.to_dict()==_core(loaded).language.to_dict() and runtime.last_utterance_result==loaded.last_utterance_result and loaded.language_frontier is None
    legacy=ContinuousRuntime(714);legacy.run_to_quiescence();legacy.inject_language("legacy",legacy.world_time+.5);current=tmp_path/"current.seworld";legacy.save_world(current);data=load_container(current,"world",{"META","STATE","CONT","NBRN"});data["META"]["version"]=6;language=data["CONT"]["language"];language.pop("active_frontier",None);language.pop("last_utterance_result",None);language.pop("utterances_processed",None);language.pop("tokens_processed",None)
    for key in ("sequence_support","sequence_trials","sequence_materialized","sequence_relations_materialized"):language["lexicon"].pop(key,None)
    old=tmp_path/"v6.seworld";save_container(old,"world",data,{"NBRN"});migrated=ContinuousRuntime.load_world(old);assert migrated.language_frontier is None and isinstance(next(iter(migrated.language_inbox.values())),LanguageFrame)
    upgraded=tmp_path/"upgraded.seworld";migrated.save_world(upgraded);assert load_container(upgraded,"world",{"META","STATE","CONT","NBRN"})["META"]["version"]==8


def test_sebrain_v6_sequence_transfer_and_v5_migration(tmp_path):
    runtime=ContinuousRuntime(709)
    for _ in range(2):runtime.inject_utterance(("dax","wug"));runtime.run_to_quiescence()
    path=tmp_path/"sequence.sebrain";runtime.simulation.save_brain(path);fresh=Simulation(710,backend="native");fresh.load_brain(path);assert fresh.core.language.sequence_support==_core(runtime).language.sequence_support and fresh.core.language.sequence_materialized==_core(runtime).language.sequence_materialized
    legacy,_=_ground_words(("dax","wug"));legacy_path=tmp_path/"pass1.sebrain";legacy.simulation.save_brain(legacy_path);sections=load_container(legacy_path,"brain",{"META","COGN","RELA","PATT","SPAT","BELS","LEAR","LANG","NBRN"});sections["META"]["version"]=5;lex=sections["LANG"]["lexicon"]
    for key in ("sequence_support","sequence_trials","sequence_materialized","sequence_relations_materialized"):lex.pop(key,None)
    old=tmp_path/"v5.sebrain";save_container(old,"brain",sections,{"LANG","NBRN"});migrated=Simulation(711,backend="native");migrated.load_brain(old);assert migrated.core.language.sequence_support=={} and migrated.core.language.sequence_materialized=={}


def test_language_utterance_pythonhashseed_determinism():
    code='''import json\nfrom simulation import ContinuousRuntime\nr=ContinuousRuntime(712)\nfor u in (("dax","wug"),("dax","blicket"),("dax","wug")):\n r.inject_utterance(u);r.run_to_quiescence()\nprint(json.dumps([r.simulation.core.language.to_dict(),r.scheduler_state(),r.last_utterance_result.ordered_symbol_ids,sorted(r.last_utterance_result.composed_active_ids)],sort_keys=True,separators=(",",":")))'''
    outputs=[]
    for seed in ("1","77"):
        env=os.environ.copy();env["PYTHONHASHSEED"]=seed;outputs.append(subprocess.check_output([sys.executable,"-c",code],env=env,text=True).strip())
    assert outputs[0]==outputs[1]
