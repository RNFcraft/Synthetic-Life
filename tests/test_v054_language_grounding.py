from dataclasses import asdict
from pathlib import Path
import os,subprocess,sys

import pytest

from consciousness.cognit import Cognit
from consciousness.language import GroundingContextEntry,GroundingContextSnapshot,LanguageFrame,normalize_token
from consciousness.relation import RelationType
from consciousness.wave import WaveResult
from simulation import ContinuousRuntime,Simulation


def _concept(runtime,kind="GENERAL"):
    core=runtime.simulation.core
    return core.graph.add_cognit(Cognit(core.graph.next_id,kind=kind,confidence=.8)).id


def _expose(runtime,token,context):
    core=runtime.simulation.core;tracker=core.grounding_context;base=tracker.accounted_until if tracker.accounted_until is not None else runtime.world_time
    observed=base+1.1;spoken=observed+.1;tracker.observe(GroundingContextSnapshot(observed,int(observed*1000),tuple(GroundingContextEntry(i,1.) for i in sorted(context))))
    core.process_language(LanguageFrame(core.language.total_exposures+1,spoken,token))


def _relation(runtime,token,target):
    core=runtime.simulation.core;source=core.language.symbols[token]
    return next((r for r in core.graph.outgoing(source) if r.target_id==target and r.relation_type is RelationType.ASSOCIATIVE),None)


def _train(swapped=False):
    runtime=ContinuousRuntime(540);runtime.run_to_quiescence();x,y=_concept(runtime),_concept(runtime)
    for i in range(6):
        dx,bl=(y,x) if swapped else (x,y)
        _expose(runtime,"dax",{dx,_concept(runtime)})
        _expose(runtime,"blicket",{bl,_concept(runtime)})
    return runtime,x,y


def test_language_frame_is_identity_and_time_only():
    frame=LanguageFrame(7,1.25,"  dax  ")
    assert asdict(frame)=={"message_id":7,"issued_at_world_time":1.25,"surface":"dax"}
    assert normalize_token("Dax")!=normalize_token("dax")
    with pytest.raises(ValueError):LanguageFrame(1,0.,"two tokens")


def test_symbol_identity_and_novel_symbol_neutrality():
    runtime=ContinuousRuntime(541);runtime.run_to_quiescence();sequence=runtime.simulation.event_sequence.value;world=runtime.simulation.world.to_dict();actions=runtime.actions_completed
    _expose(runtime,"wug",set());first=runtime.simulation.core.language.symbols["wug"]
    _expose(runtime,"wug",set())
    assert runtime.simulation.core.language.symbols["wug"]==first
    assert list(runtime.simulation.core.graph.outgoing(first))==[]
    assert runtime.simulation.event_sequence.value==sequence and runtime.simulation.world.to_dict()==world and runtime.actions_completed==actions


def test_nonce_grounding_permutation_and_distractors():
    normal,x,y=_train(False);swapped,sx,sy=_train(True)
    cross=_relation(normal,"dax",y)
    assert cross is None or _relation(normal,"dax",x).strength>cross.strength
    assert _relation(normal,"blicket",y) is not None and _relation(normal,"dax",x) is not None
    assert _relation(swapped,"dax",sy) is not None and _relation(swapped,"blicket",sx) is not None
    assert _relation(normal,"dax",x).support==6


def test_contradiction_and_functional_cue_retrieval():
    runtime,x,y=_train(False);relation=_relation(runtime,"dax",x);before=relation.strength
    engine=runtime.simulation.core.backend.engine;engine.set_activity(x-1,0.);engine.set_activity(y-1,0.);engine.set_refractory(x-1,0);engine.set_refractory(y-1,0)
    tracker=runtime.simulation.core.grounding_context;tracker.latest=None;tracker.historical.clear()
    evidence=dict(runtime.simulation.core.language.evidence["dax"]);trials=runtime.simulation.core.language.grounded_trials["dax"]
    _expose(runtime,"dax",set())
    assert evidence==runtime.simulation.core.language.evidence["dax"] and trials==runtime.simulation.core.language.grounded_trials["dax"]
    assert runtime.simulation.core.graph.nodes[x].activity>runtime.simulation.core.graph.nodes[y].activity
    assert x in runtime.simulation.core.language.last_language_wave_active_ids
    after_cue=_relation(runtime,"dax",x).strength
    for _ in range(8):_expose(runtime,"dax",{y})
    assert _relation(runtime,"dax",x).strength<after_cue and before>0


def test_same_time_order_and_pending_seworld_continuation(tmp_path):
    runtime=ContinuousRuntime(542);runtime.run_to_quiescence();x=_concept(runtime);runtime.simulation.core.last_wave=WaveResult(frozenset({x}),1.,1)
    first=runtime.inject_language("dax",runtime.world_time);second=runtime.inject_language("blicket",runtime.world_time)
    path=tmp_path/"pending.seworld";runtime.save_world(path);loaded=ContinuousRuntime.load_world(path)
    assert list(loaded.language_inbox)==[first,second]
    runtime.run_to_quiescence();loaded.run_to_quiescence()
    assert loaded.simulation.core.language.to_dict()==runtime.simulation.core.language.to_dict()
    assert loaded.scheduler_state()==runtime.scheduler_state() and not loaded.language_inbox
    ids=list(range(runtime.simulation.core.backend.engine.cognit_count))
    assert loaded.simulation.core.backend.engine.cognit_state_full(ids)==runtime.simulation.core.backend.engine.cognit_state_full(ids)


def test_sebrain_transfer_and_dangling_symbol_policy(tmp_path):
    runtime,x,_=_train(False);path=tmp_path/"grounded.sebrain";runtime.simulation.save_brain(path)
    fresh=Simulation(999,backend="native");fresh.load_brain(path)
    assert fresh.core.language.symbols==runtime.simulation.core.language.symbols
    assert any(r.target_id==x for r in fresh.core.graph.outgoing(fresh.core.language.symbols["dax"]))
    symbol=fresh.core.language.symbols["dax"];fresh.core.graph.remove_cognit(symbol);replacement=fresh.core.language.symbol("dax")
    assert replacement!=symbol and fresh.core.graph.nodes[replacement].kind=="LANGUAGE_SYMBOL"


def test_no_language_runtime_baseline_and_full_sync():
    a,b=ContinuousRuntime(543),ContinuousRuntime(543);a.run_until(2.);b.run_until(2.)
    assert a.scheduler_state()==b.scheduler_state() and a.simulation.snapshot_data()==b.simulation.snapshot_data()
    assert a.simulation.core.backend.full_graph_sync_calls==0


def test_language_source_has_no_semantic_mapping():
    # The compatibility facade and extracted language data/state modules share
    # the same frozen anti-semantic boundary.
    source="\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(Path("consciousness").glob("language*.py"))
    )
    forbidden=("ActionType","relative_x","relative_y","SensoryPrimitive","commands[","meanings[","dictionary[")
    assert not any(token in source for token in forbidden)


def test_language_curriculum_is_pythonhashseed_deterministic():
    code='''import json
from tests.test_v054_embodied_grounding import _embodied
r,a,b=_embodied({"A":"dax","B":"blicket"})
print(json.dumps([a,b,r.simulation.core.language.to_dict()],sort_keys=True,separators=(",",":")))'''
    outputs=[]
    for seed in ("1","77"):
        env=os.environ.copy();env["PYTHONHASHSEED"]=seed
        outputs.append(subprocess.check_output([sys.executable,"-c",code],env=env,text=True).strip())
    assert outputs[0]==outputs[1]
