from dataclasses import replace
import json,os,subprocess,sys

from config import Settings
from consciousness.cognit import Cognit
from consciousness.language import LanguageFrame
from consciousness.relational import BoundSpatialRelation,ParticipantBelief,RelationalStructure
from simulation import ContinuousRuntime


def _prepared():
    settings=replace(Settings(),language_min_support=1,language_min_lift=0.,language_min_background_seconds=0.)
    runtime=ContinuousRuntime(756,settings);runtime.run_to_quiescence();core=runtime.simulation.core
    left=core.graph.add_cognit(Cognit(core.graph.next_id,kind="GENERAL",confidence=.91)).id
    right=core.graph.add_cognit(Cognit(core.graph.next_id,kind="GENERAL",confidence=.87)).id
    relation=core.graph.add_cognit(Cognit(core.graph.next_id,kind="RELATIONAL",confidence=.83)).id
    token=(1,0,1);core.relational_nodes[token]=relation
    for n,(word,target) in enumerate((("wug",left),("blicket",right),("dax",relation)),1):
        core.process_language_token(LanguageFrame(n,runtime.world_time,word),{target:1.})
    core.grounding_context.latest=None;core.grounding_context.historical.clear()
    return runtime,(left,right,relation),token


def _say(runtime,words):
    runtime.inject_utterance(words,runtime.world_time);runtime.run_to_quiescence()
    return runtime.last_utterance_result.relational_result


def test_first_ever_grounded_triple_builds_existing_relational_structure():
    runtime,(left,right,relation),token=_prepared();before=dict(runtime.simulation.core.language.sequence_support)
    result=_say(runtime,("dax","wug","blicket"));structure=result.relational_structure
    assert before=={} and isinstance(structure,RelationalStructure)
    assert structure.relations==(token,) and structure.role_edges==((0,1,token),)
    assert structure.source_cognits==(left,right,relation)
    assert result.confidence==min(runtime.simulation.core.graph.nodes[i].confidence for i in (left,right,relation))
    assert runtime.simulation.core.backend.full_graph_sync_calls==0


def test_participant_order_is_the_directed_role_binding():
    runtime,(left,right,_),token=_prepared();forward=_say(runtime,("dax","wug","blicket")).relational_structure
    reverse=_say(runtime,("dax","blicket","wug")).relational_structure
    assert forward.source_cognits[:2]==(left,right) and reverse.source_cognits[:2]==(right,left)
    assert forward.role_edges==reverse.role_edges==((0,1,token),) and forward.source_cognits!=reverse.source_cognits


def test_no_relational_anchor_stays_partial_and_unbound():
    runtime,_,_=_prepared();result=_say(runtime,("wug","blicket"))
    assert result.relational_structure is None and result.confidence==0. and result.unresolved_slots==()


def test_unknown_and_equal_strength_ambiguity_remain_unresolved():
    runtime,(left,_,_),_=_prepared();core=runtime.simulation.core
    alternative=core.graph.add_cognit(Cognit(core.graph.next_id,kind="GENERAL",confidence=.91)).id
    core.process_language_token(LanguageFrame(20,runtime.world_time,"amb"),{left:1.,alternative:1.})
    result=_say(runtime,("amb","unknown"))
    assert result.semantic_slots[0].resolved_cognit_id is None
    assert result.semantic_slots[0].retrieved_cognit_ids==tuple(sorted((left,alternative)))
    assert result.unresolved_slots==(0,1) and result.relational_structure is None


def test_composition_is_read_only_for_pass1_and_creates_no_goal_or_intent():
    runtime,_,_=_prepared();core=runtime.simulation.core
    token_results=tuple(core.process_language_token(LanguageFrame(30+n,runtime.world_time,w),{}) for n,w in enumerate(("dax","wug","blicket")))
    symbols=tuple(x.symbol_id for x in token_results);before=(core.language.to_dict(),core.graph.relation_count,core.state.goal,runtime.simulation.event_sequence.value)
    result=core.language.compose_relational(("dax","wug","blicket"),symbols,token_results)
    assert result.relational_structure is not None
    assert before==(core.language.to_dict(),core.graph.relation_count,core.state.goal,runtime.simulation.event_sequence.value)


def test_belief_scene_consumes_language_structure():
    runtime,(left,right,_),_=_prepared();core=runtime.simulation.core;structure=_say(runtime,("dax","wug","blicket")).relational_structure
    core.belief_scene.participants[left]=ParticipantBelief(left,(0.,0.),1,.9,1,True,0)
    core.belief_scene.participants[right]=ParticipantBelief(right,(1.,0.),1,.9,1,True,0)
    core.belief_scene.relations[(left,right,structure.relations[0])]=BoundSpatialRelation(999,left,right,structure.relations[0],.9,1)
    binding=core.belief_scene.best_binding(structure,(left,right),update_last=False)
    assert binding.role_to_participant==(left,right) and binding.unresolved_roles==0


def test_mid_utterance_save_load_derives_identical_result(tmp_path):
    runtime,_,_=_prepared();runtime.inject_utterance(("dax","wug","blicket"),runtime.world_time)
    for _ in range(3):runtime._process(runtime.scheduler.pop_ready(runtime.world_time)[0])
    path=tmp_path/"mid.seworld";runtime.save_world(path);loaded=ContinuousRuntime.load_world(path)
    runtime.run_to_quiescence();loaded.run_to_quiescence()
    assert runtime.last_utterance_result.relational_result==loaded.last_utterance_result.relational_result


def test_relational_composition_pythonhashseed_determinism():
    code='''from tests.test_v056_relational_language import _prepared,_say\nimport json\nr,_,_=_prepared();x=_say(r,("dax","wug","blicket"));print(json.dumps([x.ordered_symbol_ids,[s.retrieved_cognit_ids for s in x.semantic_slots],x.relational_structure.source_cognits,x.relational_structure.role_edges,x.provenance],separators=(",",":")))'''
    outputs=[]
    for seed in ("1","77"):
        env=os.environ.copy();env["PYTHONHASHSEED"]=seed;outputs.append(subprocess.check_output([sys.executable,"-c",code],env=env,text=True).strip())
    assert outputs[0]==outputs[1]
