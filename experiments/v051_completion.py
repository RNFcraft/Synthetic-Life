"""Final bounded, non-scripted v0.5.1 behavioral completion experiment."""
import json,time
from pathlib import Path
from config import Settings
from curriculum import TARGET_PATTERNS,evaluate_pattern
from simulation import Simulation

def run_target(sim,name,budget):
    target=TARGET_PATTERNS[name];sim.core.receive_target(target);initial=sim.core.target_mismatch;minimum=initial;trajectory=[];before=sim.world.action_counts.copy();start_mod=sim.world.world_modification();success=False
    for i in range(1,budget+1):
        sim.step();minimum=min(minimum,sim.core.target_mismatch)
        if i in (1,25,100,250,500):trajectory.append({"tick":i,"mismatch":sim.core.target_mismatch})
        if evaluate_pattern(sim.world.objects,target):success=True;break
    counts={k:sim.world.action_counts[k]-before.get(k,0) for k in sim.world.action_counts}
    return {"target":name,"success":success,"actions":i,"initial_mismatch":initial,"minimum_mismatch":minimum,"final_mismatch":sim.core.target_mismatch,"mismatch_samples":trajectory,"world_modification":sim.world.world_modification()-start_mod,"action_counts":counts,"plans":sim.core.planner.plans_created,"subgoals_created":sim.core.state.subgoals_created,"subgoals_completed":sim.core.state.subgoals_completed,"memory_retrievals":sim.core.memory.reactivation_count,"unique_action_context_trials":sim.core.affordances.unique_trials,"mean_epistemic":sum(sim.core.affordances.last_epistemic.values())/max(1,len(sim.core.affordances.last_epistemic))}

def main():
    sim=Simulation(1051,Settings(object_count=0,place_birth_visits=1,telemetry_history=1));sim.world.body.x=sim.world.body.y=15;sim.world.initialize_controlled_objects([(3+i*5,4+(i%2)*7) for i in range(5)])
    started=time.perf_counter();pair=run_target(sim,"pair",500);line=run_target(sim,"line3",500);elapsed=time.perf_counter()-started
    result={"seed":1051,"pair":pair,"line3":line,"elapsed_seconds":elapsed,"physical_actions_per_second":(pair["actions"]+line["actions"])/elapsed,"cognitive_cycles_per_second":sim.core.planner.total_cycles/elapsed}
    Path("v051-completion-results.json").write_text(json.dumps(result,indent=2),encoding="utf-8");print(json.dumps(result,indent=2))

if __name__=="__main__":main()
