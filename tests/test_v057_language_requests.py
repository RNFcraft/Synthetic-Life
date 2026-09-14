from dataclasses import replace
import os,subprocess,sys,unicodedata

from config import Settings
from consciousness.language import LanguageFrame,normalize_token
from consciousness.relational import RelationalStructure
from persistence import load_container
from simulation import ContinuousRuntime,Simulation
from tests.test_v056_relational_language import _prepared,_say,_embodied_curriculum


def _train_request(runtime,structure,cue="mip"):
    for _ in range(2):runtime.inject_utterance(("dax","wug","blicket"),runtime.world_time);runtime.run_to_quiescence()
    for _ in range(2):runtime.inject_utterance((cue,"dax","wug","blicket"),runtime.world_time,structure);runtime.run_to_quiescence()


def _ask(runtime,words):
    _say(runtime,words);return runtime.last_utterance_result.request_result


def test_learned_request_distinguishes_description_and_first_novel_request():
    runtime,_,_=_prepared();structure=_say(runtime,("dax","wug","blicket")).relational_structure;core=runtime.simulation.core
    _train_request(runtime,structure);core.state.goal=None;before=(runtime.actions_completed,runtime.simulation.event_sequence.value,runtime.simulation.world.to_dict())
    description=_say(runtime,("dax","wug","blicket"));assert description.relational_structure is not None and core.state.goal is None
    request=_ask(runtime,("mip","dax","wug","blicket"));goal=core.state.goal
    assert request.request_cue_symbol_ids==(core.language.symbols["mip"],) and request.desired_structure==request.relational_result.relational_structure
    assert goal is not None and goal.origin=="LANGUAGE_REQUEST" and core.target_structure==request.desired_structure and goal.id==request.goal_id
    assert core.target_structure.source_cognits==structure.source_cognits and core.target_structure.role_edges==structure.role_edges
    assert before==(runtime.actions_completed,runtime.simulation.event_sequence.value,runtime.simulation.world.to_dict())


def test_arbitrary_request_label_permutation_and_no_hardcoded_command():
    rows=[]
    for cue in ("mip","просьба"):
        runtime,_,_=_prepared();structure=_say(runtime,("dax","wug","blicket")).relational_structure;_train_request(runtime,structure,cue);runtime.simulation.core.state.goal=None;result=_ask(runtime,(cue,"dax","wug","blicket"));rows.append((result.desired_structure,runtime.simulation.core.state.goal.origin))
    assert rows[0]==rows[1]
    runtime,_,_=_prepared();result=_ask(runtime,("take","dax","wug","blicket"));assert result.request_cue_symbol_ids==() and runtime.simulation.core.state.goal is None


def test_ambiguous_or_incomplete_request_creates_no_goal():
    runtime,_,_=_prepared();structure=_say(runtime,("dax","wug","blicket")).relational_structure;_train_request(runtime,structure);runtime.simulation.core.state.goal=None
    assert _ask(runtime,("mip","unknown")).desired_structure is None and runtime.simulation.core.state.goal is None


def test_true_embodied_request_goal_uses_frozen_pass3_meanings():
    runtime,relational,*_=_embodied_curriculum({"relation":"dax","left":"wug","right":"blicket"});structure=relational.relational_structure
    _train_request(runtime,structure);runtime.simulation.core.state.goal=None;before=(runtime.actions_completed,runtime.simulation.event_sequence.value,runtime.simulation.world.to_dict());request=_ask(runtime,("mip","dax","wug","blicket"))
    assert request.desired_structure.source_cognits==structure.source_cognits and request.desired_structure.role_edges==structure.role_edges and runtime.simulation.core.state.goal.origin=="LANGUAGE_REQUEST"
    assert runtime.simulation.core.planner is not None and runtime.simulation.core.target_structure==request.desired_structure
    assert before==(runtime.actions_completed,runtime.simulation.event_sequence.value,runtime.simulation.world.to_dict()) and runtime.simulation.core.backend.full_graph_sync_calls==0


def test_unicode_nfc_exact_identity_and_grounding_sequence():
    runtime=ContinuousRuntime(770,replace(Settings(),language_min_support=1,language_min_lift=0.,language_min_background_seconds=0.));runtime.run_to_quiescence();core=runtime.simulation.core
    tokens=("просьба","слева","объект","猫","左","α","β","🔥","→","е","e","кот","Кот","🙂","🙃")
    for token in tokens:core.process_language_token(LanguageFrame(1,runtime.world_time,token),{})
    assert len({core.language.symbols[x] for x in tokens})==len(tokens) and core.language.symbols["е"]!=core.language.symbols["e"] and core.language.symbols["кот"]!=core.language.symbols["Кот"]
    composed="é";decomposed="e\u0301";a=core.process_language_token(LanguageFrame(2,runtime.world_time,composed),{}).symbol_id;b=core.process_language_token(LanguageFrame(3,runtime.world_time,decomposed),{}).symbol_id;assert normalize_token(composed)==normalize_token(decomposed) and a==b
    runtime.inject_utterance(("猫","左","α","🔥","→"));runtime.run_to_quiescence();assert tuple(core.language.symbols[x] for x in ("猫","左","α","🔥","→"))==runtime.last_utterance_result.ordered_symbol_ids


def test_utf8_request_evidence_brain_and_world_roundtrip(tmp_path):
    runtime,_,_=_prepared();structure=_say(runtime,("dax","wug","blicket")).relational_structure;_train_request(runtime,structure,"просьба")
    world=tmp_path/"unicode.seworld";brain=tmp_path/"unicode.sebrain";runtime.save_world(world);runtime.simulation.save_brain(brain)
    loaded=ContinuousRuntime.load_world(world);fresh=Simulation(771,backend="native");fresh.load_brain(brain)
    for core in (loaded.simulation.core,fresh.core):
        assert "просьба" in core.language.symbols and core.language.request_support["просьба"]==2 and core.language.request_concept_id in core.graph.nodes
    assert load_container(world,"world",{"META","STATE","CONT","NBRN"})["META"]["version"]==7 and load_container(brain,"brain",{"META","COGN","RELA","PATT","SPAT","BELS","LEAR","LANG","NBRN"})["META"]["version"]==6


def test_old_lexicon_migrates_without_request_cues():
    runtime,_,_=_prepared();data=runtime.simulation.core.language.to_dict()
    for key in ("request_concept_id","request_support","request_trials","request_materialized"):data.pop(key)
    from consciousness.language import LanguageLexicon
    restored=LanguageLexicon.from_dict(runtime.simulation.core,data);assert restored.request_concept_id is None and restored.request_support=={} and restored.request_materialized==set()


def test_request_pythonhashseed_determinism():
    code='''from tests.test_v057_language_requests import _prepared,_say,_train_request,_ask\nimport json\nr,_,_=_prepared();s=_say(r,("dax","wug","blicket")).relational_structure;_train_request(r,s,"просьба");r.simulation.core.state.goal=None;x=_ask(r,("просьба","dax","wug","blicket"));print(json.dumps((x.goal_id,x.request_cue_symbol_ids,x.desired_structure.source_cognits,x.desired_structure.role_edges,r.simulation.core.language.to_dict()),sort_keys=True))'''
    out=[]
    for seed in ("1","77"):
        env=os.environ.copy();env["PYTHONHASHSEED"]=seed;out.append(subprocess.check_output([sys.executable,"-c",code],env=env))
    assert out[0]==out[1]
