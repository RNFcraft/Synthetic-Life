"""Bounded behavioral validation for v0.5.1; reports failures without scripted solutions."""
from __future__ import annotations
import argparse,json,time
from dataclasses import replace
from pathlib import Path
from config import Settings
from curriculum import TARGET_PATTERNS,evaluate_pattern
from simulation import MultiEntitySimulation,Simulation
from world import Action,ActionType
from world.objects import WorldObject

def memory_trial(enabled:bool,budget:int,seed:int)->dict:
    sim=Simulation(seed,Settings(object_count=0,place_birth_visits=1,telemetry_history=1));w=sim.world;w.body.x=w.body.y=10;w.body.orientation="NORTH";w.objects=[WorldObject(1,10,8)]
    for tick in range(3):sim.core.step(w.perceive(tick));sim.core.deliberate(w.perceive(tick))
    created=len(sim.core.memory.structures);origin=w.body.position
    for action in (Action(ActionType.TURN_RIGHT),Action(ActionType.MOVE_RIGHT),Action(ActionType.MOVE_RIGHT),Action(ActionType.MOVE_RIGHT)):w.apply_action(action)
    if not enabled:sim.core.memory.structures.clear();sim.core.memory.enabled=False
    sim.core.receive_target(TARGET_PATTERNS["pair"]);react_before=sim.core.memory.reactivation_count;attempted=False;success=False;reacquire=None
    for _ in range(budget):
        sim.step();attempted|=abs(w.body.x-origin[0])+abs(w.body.y-origin[1])<3
        visible=any(c.occupied for c in w.perceive(sim.clock.tick).cells)
        if visible:success=True;reacquire=sim.clock.tick;break
    return {"memory_enabled":enabled,"memory_created":created,"memory_reactivated":sim.core.memory.reactivation_count-react_before,"memory_confirmed":sim.core.memory.confirmation_count,"memory_contradicted":sim.core.memory.contradiction_count,"return_attempted":attempted,"return_success":success,"reacquisition_tick":reacquire,"physical_actions":sim.clock.tick}

def curriculum_trial(target_name:str,budget:int,seed:int,sim=None)->tuple[dict,Simulation]:
    sim=sim or Simulation(seed,Settings(object_count=0,place_birth_visits=1,telemetry_history=1));sim.world.objects=[WorldObject(i+1,2+i*4,2+(i%2)*5) for i in range(5)]
    initial=evaluate_pattern(sim.world.objects,TARGET_PATTERNS[target_name]);sim.core.receive_target(TARGET_PATTERNS[target_name]);start_moves=sim.world.world_modification();success=False;completed=None
    before=(sim.core.state.subgoals_created,sim.core.memory.reactivation_count,sim.world.action_counts.copy())
    for _ in range(budget):
        sim.step()
        if evaluate_pattern(sim.world.objects,TARGET_PATTERNS[target_name]):success=True;completed=sim.clock.tick;break
    counts=sim.world.action_counts
    return {"target":target_name,"initially_satisfied":initial,"success":success and not initial,"completion_tick":completed,"object_movements":sim.world.world_modification()-start_moves,"blind_grabs":counts["blind_grabs"]-before[2].get("blind_grabs",0),"blind_interactions":counts["blind_interactions"]-before[2].get("blind_interactions",0),"plans":sim.core.planner.plans_created,"subgoals_created":sim.core.state.subgoals_created-before[0],"subgoals_completed":sim.core.state.subgoals_completed,"subgoals_failed":sim.core.state.subgoals_failed,"memory_retrievals":sim.core.memory.reactivation_count-before[1]},sim

def deliberation_trial(full:bool,budget:int,seed:int)->dict:
    settings=replace(Settings(telemetry_history=1),min_deliberation_cycles=1,max_deliberation_cycles=16 if full else 1);sim=Simulation(seed,settings);started=time.perf_counter();revisions=0;physical_places={};internal_regions={}
    for _ in range(budget):
        sim.step();revisions=sim.core.planner.plans_revised;position=sim.world.body.position;place=sim.core.memory.current_place_id
        if place is not None:physical_places.setdefault(position,set()).add(place);internal_regions.setdefault(place,set()).add(position)
    elapsed=time.perf_counter()-started;c=sim.world.action_counts
    return {"mode":"FULL_ADAPTIVE" if full else "MINIMAL","ticks":budget,"elapsed_seconds":elapsed,"physical_actions_per_sec":budget/max(elapsed,1e-9),"cognitive_cycles":sim.core.planner.total_cycles,"cognitive_cycles_per_sec":sim.core.planner.total_cycles/max(elapsed,1e-9),"plan_revisions":revisions,"blind_actions":c["blind_grabs"]+c["blind_interactions"],"world_modification":sim.world.world_modification(),"place_fragmentation_mean":sum(map(len,physical_places.values()))/max(1,len(physical_places)),"place_aliasing_mean":sum(map(len,internal_regions.values()))/max(1,len(internal_regions))}

def multi_trial(budget:int,seed:int)->dict:
    sim=MultiEntitySimulation(2,seed,Settings(object_count=5,telemetry_history=1,place_birth_visits=1));sim.world.bodies[0].x,sim.world.bodies[0].y,sim.world.bodies[0].orientation=10,10,"EAST";sim.world.bodies[1].x,sim.world.bodies[1].y,sim.world.bodies[1].orientation=12,10,"WEST";encounters=0;reactivations=[0,0]
    for _ in range(budget):
        frames=[sim.world.perceive(sim.clock.tick,i) for i in sim.cores];encounters+=sum(any(c.appearance_channel for c in f.cells) for f in frames);sim.step()
    for i,c in sim.cores.items():reactivations[i]=c.memory.reactivation_count
    return {"ticks":budget,"mutual_visibility_events":encounters,"other_structure_reactivations":reactivations,"conflicts":sim.world.conflict_count,"fairness_winners":sim.world.fairness_wins,"joint_object_interactions":sum(c["successful_interactions"] for c in [sim.world.action_counts])}

def main()->None:
    p=argparse.ArgumentParser();p.add_argument("--budget",type=int,default=120);p.add_argument("--output",default="v051-stabilization-results.json");a=p.parse_args();started=time.perf_counter()
    shared=Simulation(910,Settings(object_count=0,telemetry_history=1));pair,shared=curriculum_trial("pair",a.budget,910,shared);line,shared=curriculum_trial("line3",a.budget,911,shared);fresh,_=curriculum_trial("pair",a.budget,912)
    result={"memory":[memory_trial(True,a.budget,900),memory_trial(False,a.budget,900)],"curriculum":{"persistent_brain":[pair,line],"fresh_brain_control":fresh},"deliberation":[deliberation_trial(False,a.budget,920),deliberation_trial(True,a.budget,920)],"multi_entity":multi_trial(a.budget,930)};result["elapsed_seconds"]=time.perf_counter()-started
    Path(a.output).write_text(json.dumps(result,indent=2),encoding="utf-8");print(json.dumps(result,indent=2))

if __name__=="__main__":main()
