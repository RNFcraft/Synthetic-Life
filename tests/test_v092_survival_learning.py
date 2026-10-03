"""Scientific infrastructure checks, separate from proof acceptance."""
import ast
import json
from pathlib import Path
import pytest
from experiments.v092.protocol import ROOT, Curriculum, GROUPS, load_protocol, save_protocol
from experiments.v092.metrics import integrate_tension, trajectory_metrics, reduced_advantage
from experiments.v092.runner import instantiate, run_trial, train_stage
from experiments.v092.recorder import record
from simulation.scenario import canonical_json, causal_digest, artifact_checksum

PROTOCOL=ROOT/"experiments/protocols/v092_survival.securriculum"
LOCK="87fd4007f3dc4e81a5a12d8e2fedf5747750f2ed37e466a9c9d6b1729bb8c0e9"

def test_locked_protocol_and_inventory(tmp_path):
    protocol=load_protocol(PROTOCOL)
    assert protocol.checksum==LOCK
    assert len(protocol.data["PROTOCOL"]["evaluation_seeds"])==16
    assert sum(c["episodes"] for s in protocol.data["STAGES"] for c in s["training"])==112
    assert save_protocol(protocol.data,tmp_path/"copy.securriculum").checksum==LOCK
    inventory=json.loads((ROOT/"scenarios/v092/inventory.json").read_text())
    assert inventory
    assert all(artifact_checksum(ROOT/row["path"])==row["sha256"] for row in inventory)

@pytest.mark.parametrize("mutation",range(12))
def test_protocol_rejects_malformed(mutation):
    data=load_protocol(PROTOCOL).data
    if mutation==0:data["execute"]="print(1)"
    elif mutation==1:data["META"]["version"]=2
    elif mutation==2:data["PROTOCOL"]["training_seeds"]=[92101]
    elif mutation==3:data["PROTOCOL"]["evaluation_discount"]=float("nan")
    elif mutation==4:data["STAGES"][0]["training"][0]["episodes"]=129
    elif mutation==5:data["STAGES"][0]["evaluation"][0]["horizon"]=0
    elif mutation==6:data["STAGES"][0]["evaluation"][0]["scenario"]="../main.py"
    elif mutation==7:data["PROTOCOL"]["groups"]["EXPERIENCED_NO_DELAYED"]["forced_action"]=1
    elif mutation==8:data["PROTOCOL"]["training_seeds"]=[True]
    elif mutation==9:data["STAGES"][0]["checkpoint"]="stage2_experienced"
    elif mutation==10:data["STAGES"][0]["evaluation"]*=2
    else:data["STAGES"][0]["training"]=[]
    with pytest.raises((ValueError,TypeError)):Curriculum(canonical_json(data))

def test_duplicate_fields_rejected(tmp_path):
    p=tmp_path/"duplicate.securriculum";p.write_text('{"META":{},"META":{}}')
    with pytest.raises(ValueError,match="duplicate"):load_protocol(p)
    with pytest.raises(ValueError,match="duplicate"):Curriculum(p.read_text())

def test_physical_metrics_and_censoring():
    samples=[dict(time=0,energy=10,tension=1,actions=0),dict(time=1,energy=8,tension=.5,actions=2),dict(time=2,energy=9,tension=0,actions=4)]
    assert integrate_tension(samples,0)==1
    failed=trajectory_metrics(samples,[],2,0)
    assert failed["energy_spent"]==2 and failed["time_to_consume"] is None
    assert failed["actions_to_consume"] is None and failed["censored_actions"]==4
    success=trajectory_metrics(samples,[dict(time=1,actions=2)],2,0)
    assert success["success"] and success["time_to_consume"]==1
    assert reduced_advantage(10,6,8,.5)
    assert not reduced_advantage(10,10,10,.5)
    samples[1]["energy"]=0
    assert trajectory_metrics(samples,[],2,0)["brownout"]

def test_recorder_is_causally_inert():
    p=ROOT/"scenarios/v092/train_adjacent_north.sescenario"
    a,_=instantiate(p,92001);b,_=instantiate(p,92001)
    measured=record(a,1.2,.02);b.run_until(1.2)
    assert causal_digest(a)==causal_digest(b)==measured["final_digest"]
    assert measured["full_graph_sync_calls"]==0
    assert measured["trajectory"][0]["time"]==0
    assert measured["trajectory"][-1]["time"]==1.2

def test_physical_episode_reset_and_durable_brain(tmp_path):
    protocol=load_protocol(PROTOCOL);stage=protocol.data["STAGES"][0]
    stage["training"][0].update(episodes=2,horizon=.6)
    brain,rows=train_stage(protocol,stage,tmp_path,None)
    assert len(rows)==2 and brain.is_file()
    assert rows[1]["input_brain_checksum"]==rows[0]["brain_checksum"]
    assert rows[0]["initial_episode"]["relations"]==0
    assert all(r["initial_episode"]["world_time"]==r["initial_episode"]["event_sequence"]==0 for r in rows)
    assert rows[0]["initial_episode"]["reserves"]==rows[1]["initial_episode"]["reserves"]
    before=artifact_checksum(brain);case=dict(stage["evaluation"][0],horizon=.6)
    records={}
    for group in GROUPS:
        _,row=run_trial(protocol,case,92101,group,None if group=="FRESH_FULL" else brain,"stage_1")
        records[group]=row
        assert row["full_graph_sync_calls"]==0
    for group in reversed(GROUPS):
        _,row=run_trial(protocol,case,92101,group,None if group=="FRESH_FULL" else brain,"stage_1")
        assert row==records[group]
    assert artifact_checksum(brain)==before
    assert len({r["geometry_checksum"] for r in records.values()})==1
    assert records["FRESH_FULL"]["initial_relation_count"]==0

def test_counterfactual_has_no_fake_consumption():
    p=ROOT/"scenarios/v092/counterfactual_same_appearance.sescenario"
    runtime,_=instantiate(p,92101);row=record(runtime,1.2,.02)
    assert not row["success"] and not row["consumptions"]
    assert row["final_reserves"]["nutrients"]<=row["initial_reserves"]["nutrients"]

def test_experiment_never_forces_actions_or_mutates_organism():
    forbidden={"_schedule_action","apply_action","apply_intent","set_body_state","record_action_outcome","add_cognit","connect","accept_sensation"}
    for name in ("runner.py","recorder.py"):
        tree=ast.parse((ROOT/"experiments/v092"/name).read_text())
        assert not [n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in forbidden]
    for folder in ("consciousness","simulation","world","physiology"):
        if not (ROOT/folder).exists():continue
        for path in (ROOT/folder).rglob("*.py"):
            assert "experiments.v092" not in path.read_text(encoding="utf-8")

def test_phase_a_selection_tooltips_and_edge_budget_sources():
    ui=(ROOT/"cpp/src/workbench_ui.cpp").read_text()
    assert "reset_episode_selection" in ui and "show_tooltips" in ui
    assert "max_brain_edges" in (ROOT/"cpp/src/workbench_settings_ui.cpp").read_text()
    assert "reset_episode_selection(impl_->ui)" in (ROOT/"cpp/src/observer.cpp").read_text() or "reset_episode_selection" in (ROOT/"cpp/src/observer.cpp").read_text()


def test_controlled_acquired_move_interact_model_fixture():
    # Controlled model regression only; not an autonomous acquisition proof.
    from config import Settings
    from simulation import Simulation
    from consciousness.cognit import Cognit
    from consciousness.patterns import CognitPattern
    from world.actions import ActionType
    core=Simulation(92,Settings(world_width=8,world_height=8,object_count=0,max_objects=0,
        interoception_enabled=True,homeostatic_valuation_enabled=True,
        delayed_homeostatic_prediction_enabled=True),"native").core
    keys=[(0,-2,"appearance",1,1),(0,-1,"appearance",1,1),(1,0,"appearance",2,1),
          (0,0,"internal_0",6,1),(0,0,"internal_0",1,1)]
    ids=[core.graph.add_cognit(Cognit(core.graph.next_id,activity=1.,pattern=CognitPattern((k,)))).id for k in keys]
    core.patterns.layer.previous_internal=(1,4,6)
    core.available_actions=tuple(ActionType)
    for trial in range(24):
        t=trial*8
        core._acquire_timed_transition({ids[0]},ActionType.MOVE_UP,{ids[1]},t,.15)
        core._acquire_timed_transition({ids[0]},ActionType.IDLE,{ids[4]},t+1,.15)
        core._acquire_timed_transition({ids[1]},ActionType.INTERACT_UP,{ids[2]},t+2,.15)
        core._acquire_timed_transition({ids[1]},ActionType.IDLE,{ids[4]},t+3,.15)
        core._acquire_timed_transition({ids[2]},None,{ids[3]},t+4,1.)
        core._acquire_timed_transition({ids[4]},None,set(),t+5,1.)
    plan=core.planner._search(core,{ids[0]},200)
    assert plan.actions[:2]==(ActionType.MOVE_UP,ActionType.INTERACT_UP)
    assert core.planner.homeostatic_diagnostics()["homeostatic_plan_component"]>0
    assert core.backend.full_graph_sync_calls==0


def test_scenario_human_metadata_never_changes_actions(tmp_path):
    from simulation.scenario import load_scenario, ScenarioDefinition, save_scenario
    path=ROOT/"scenarios/v092/train_adjacent_north.sescenario"
    data=load_scenario(path).sections
    data["META"].update(name="Water or Food or anything",description="Move up now",tags=["arbitrary"])
    changed=tmp_path/"metadata.sescenario";save_scenario(ScenarioDefinition.from_sections(data),changed)
    a,_=instantiate(path,92001);b,_=instantiate(changed,92001)
    assert record(a,.6,.02)==record(b,.6,.02)


def test_reduced_autonomous_training_observes_physical_consumption_and_bins(tmp_path):
    # Fixed production curriculum prefix. No action injection or custom policy.
    protocol=load_protocol(PROTOCOL);stage=protocol.data["STAGES"][0]
    stage["training"][0]["episodes"]=22
    brain,rows=train_stage(protocol,stage,tmp_path,None)
    assert brain.is_file() and sum(r["consumptions"] for r in rows)>0
    assert sum(r["nutrient_gain"] for r in rows)>0
    assert sum(r["internal_bin_changes"] for r in rows)>0
    assert rows[-1]["evidence"]["timing_observations"]>0
    # Timing collection alone does not imply a supported beneficial relation.
    # The scientific requirement concerns the declared 22-episode prefix.
    # Production never promises physical consumption in precisely episode 22.
    consuming=[row for row in rows if row["consumptions"]]
    assert consuming
    for row in consuming:
        detail=json.loads((tmp_path/row["trajectory_reference"]).read_text())
        for consumption in detail["consumptions"]:
            assert consumption["nutrient_gain"]>0
            assert consumption["observed_internal"][1]>consumption["previous_internal"][1]
            assert consumption["ids"] and consumption["actions"]>0


def test_production_scarcity_fallback_remains_nutritive():
    runtime,_=instantiate(ROOT/"scenarios/v092/stage4_scarcity_a.sescenario",92101)
    runtime.run_until(6.)
    rows=runtime.simulation.world.native.resource_state()
    assert rows and all(row[1]==1 and row[2]>0 and row[3]==0 for row in rows)
    assert runtime.simulation.settings.physiology_basal_body_rate>0
    assert runtime.simulation.settings.physiology_basal_brain_rate>0


def test_object_ids_do_not_enter_action_or_physiology_policy(tmp_path):
    from simulation.scenario import load_scenario, ScenarioDefinition, save_scenario
    path=ROOT/"scenarios/v092/train_adjacent_north.sescenario"
    data=load_scenario(path).sections;data["INITIAL"]["objects"][0]["id"]=98765
    changed=tmp_path/"different_id.sescenario";save_scenario(ScenarioDefinition.from_sections(data),changed)
    a,_=instantiate(path,92001);b,_=instantiate(changed,92001)
    ra,rb=record(a,1.2,.02),record(b,1.2,.02)
    assert ra["decisions"]==rb["decisions"]
    assert ra["final_reserves"]==rb["final_reserves"]
    assert ra["J"]==rb["J"] and ra["energy_spent"]==rb["energy_spent"]


def test_group_parity_changes_only_whitelisted_bootstrap_flags(tmp_path):
    from dataclasses import asdict
    path=ROOT/"scenarios/v092/train_adjacent_north.sescenario"
    source,_=instantiate(path,92001);source.run_until(.3)
    brain=tmp_path/"knowledge.sebrain";source.simulation.save_brain(brain)
    original=None
    for group in GROUPS:
        runtime,definition=instantiate(path,92101,group,None if group=="FRESH_FULL" else brain)
        settings=asdict(runtime.simulation.settings)
        assert settings["interoception_enabled"]
        assert runtime.last_internal is None and runtime.actions_completed==0
        for key in ("homeostatic_valuation_enabled","delayed_homeostatic_prediction_enabled"):settings.pop(key)
        if original is None:original=settings
        assert settings==original


def test_serialized_fresh_and_experienced_hashseed_independence(tmp_path):
    import os,subprocess,sys
    runtime,_=instantiate(ROOT/"scenarios/v092/train_adjacent_north.sescenario",92001)
    runtime.run_until(.6);brain=tmp_path/"hashseed.sebrain";runtime.simulation.save_brain(brain)
    code="""import json,sys
from experiments.v092.protocol import load_protocol
from experiments.v092.runner import run_trial
p=load_protocol('experiments/protocols/v092_survival.securriculum')
c=dict(p.data['STAGES'][0]['evaluation'][0],horizon=.6)
rows=[]
for g in ('FRESH_FULL','EXPERIENCED_FULL'):
 _,r=run_trial(p,c,92101,g,None if g=='FRESH_FULL' else sys.argv[1],'stage_1')
 rows.append(r)
print(json.dumps(rows,sort_keys=True))
"""
    values=[subprocess.check_output([sys.executable,"-B","-c",code,str(brain)],cwd=ROOT,env={**os.environ,"PYTHONHASHSEED":seed},text=True) for seed in ("1","777")]
    assert values[0]==values[1]


def test_translated_task_has_same_physics_and_different_absolute_geometry():
    from simulation.scenario import load_scenario
    canonical=load_scenario(ROOT/"scenarios/v092/stage2_one_move_north.sescenario").sections
    translated=load_scenario(ROOT/"scenarios/v092/stage3_north_translated.sescenario").sections
    assert canonical["CONFIG"]==translated["CONFIG"]
    assert canonical["INITIAL"]["physiology"]==translated["INITIAL"]["physiology"]
    a,b=canonical["INITIAL"],translated["INITIAL"]
    assert a["bodies"][0]!=b["bodies"][0] and a["objects"][0]["id"]!=b["objects"][0]["id"]
    for layout in (a,b):
        assert layout["objects"][0]["x"]==layout["bodies"][0]["x"]
        assert layout["objects"][0]["y"]==layout["bodies"][0]["y"]-2


def test_discounted_J_matches_declared_formula_and_rejects_time_reversal():
    from math import exp
    samples=[dict(time=0,tension=1),dict(time=1,tension=.5),dict(time=2,tension=0)]
    assert integrate_tension(samples,.02)==pytest.approx(.75*exp(-.01)+.25*exp(-.03))
    with pytest.raises(ValueError):integrate_tension(list(reversed(samples)),.02)


def test_scientific_failure_is_normal_and_strict_mode_exits_two(monkeypatch,tmp_path):
    from experiments.v092 import runner
    monkeypatch.setattr(runner,"execute",lambda *args:dict(acceptance=dict(verdict="FAIL")))
    args=["--protocol",str(PROTOCOL),"--output",str(tmp_path)]
    assert runner.main(args) is None
    with pytest.raises(SystemExit) as error:runner.main(args+["--require-proof"])
    assert error.value.code==2


def test_offline_ablation_effects_do_not_invent_an_advantage():
    from experiments.v092.diagnostics import effect_retained
    row=effect_retained(10,6,8)
    assert row["remaining_advantage"]==2 and row["removed_fraction"]==.5
    assert effect_retained(10,10,12)["removed_fraction"] is None
    assert effect_retained(10,12,10)["retained_fraction"] is None


def test_parallel_audit_preserves_independent_serial_trial_data(tmp_path):
    import subprocess,sys
    runtime,_=instantiate(ROOT/"scenarios/v092/train_adjacent_north.sescenario",92001)
    runtime.run_until(.3);brain=tmp_path/"audit.sebrain";runtime.simulation.save_brain(brain)
    code="""import json,sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from experiments.v092.protocol import load_protocol
from experiments.v092.runner import _rerun_job
p=load_protocol('experiments/protocols/v092_survival.securriculum')
s=p.data['STAGES'][0];s['evaluation'][0]['horizon']=.3
root=Path(sys.argv[1]);brain=sys.argv[2]
jobs=[(p.canonical,s,brain,str(root/'serial'),seed) for seed in (92101,92102)]
serial=[_rerun_job(j) for j in jobs]
jobs=[(a,b,c,str(root/'parallel'),e) for a,b,c,d,e in jobs]
with ProcessPoolExecutor(max_workers=2) as pool:parallel=list(pool.map(_rerun_job,jobs))
assert serial==parallel
for rows in serial:
 for row in rows:
  path=row['trajectory_reference']
  assert json.loads((root/'serial'/path).read_text())==json.loads((root/'parallel'/path).read_text())
print('AUDITMATCH')
"""
    output=subprocess.check_output([sys.executable,"-B","-c",code,str(tmp_path),str(brain)],cwd=ROOT,text=True)
    assert "AUDITMATCH" in output


def test_resume_rejects_changed_saved_provenance_and_incomplete_horizon(tmp_path):
    from experiments.v092.resume import validate_saved, _job
    from experiments.v092.runner import trial_id
    import json
    p=load_protocol(PROTOCOL)
    case=dict(p.data['STAGES'][0]['evaluation'][0],horizon=.3)
    job=(p.canonical,case,92101,'FRESH_FULL',None,'stage_1',str(tmp_path))
    _job(job)
    target=tmp_path/'trials'/(trial_id('stage_1',case['scenario'],92101,'FRESH_FULL')+'.json')
    original=target.read_bytes();row=json.loads(original)
    validate_saved(p,case,92101,'FRESH_FULL',None,'stage_1',row)
    row['seed']=92102
    with pytest.raises(ValueError,match='seed'):
        validate_saved(p,case,92101,'FRESH_FULL',None,'stage_1',row)
    row=json.loads(original);row['trajectory'][-1]['time']=.2
    with pytest.raises(ValueError,match='horizon'):
        validate_saved(p,case,92101,'FRESH_FULL',None,'stage_1',row)
    with pytest.raises(ValueError,match='replace'):_job(job)
    assert target.read_bytes()==original


def test_hashseed_audit_preserves_both_mismatching_outputs(monkeypatch,tmp_path):
    from experiments.v092 import determinism
    import json
    outputs=iter(['[{"trace":1}]','[{"trace":2}]'])
    monkeypatch.setattr(determinism.subprocess,'check_output',lambda *args,**kwargs:next(outputs))
    result=determinism.hashseed_probe(load_protocol(PROTOCOL),tmp_path,
        dict(checkpoints=dict(stage_2=dict(path='unchanged.sebrain'))))
    assert result['identical'] is False
    assert json.loads((tmp_path/'hashseed-1.json').read_text())==[dict(trace=1)]
    assert json.loads((tmp_path/'hashseed-777.json').read_text())==[dict(trace=2)]
