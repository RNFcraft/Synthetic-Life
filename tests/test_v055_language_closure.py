from dataclasses import replace

from consciousness.core import ContinuousCognitionFrontier
from consciousness.native_engine import RuntimeEvent,RuntimeEventType
from simulation import ContinuousRuntime


def _start_after_first_token(runtime,tokens=("dax","wug","blicket")):
    runtime.run_to_quiescence();runtime.inject_utterance(tokens);runtime._process(runtime.scheduler.pop_ready(runtime.world_time)[0]);runtime._process(runtime.scheduler.pop_ready(runtime.world_time)[0]);return runtime.language_frontier


def test_language_continue_defers_behind_unfinished_cognition_same_time_once():
    runtime=ContinuousRuntime(730);frontier=_start_after_first_token(runtime);core=runtime.simulation.core;pending=runtime.scheduler.pop_ready(runtime.world_time)[0];old_id=pending.id;before=(frontier.next_token_index,dict(core.language.exposures),dict(core.language.sequence_support),runtime.language_tokens_processed,core.cognitive_tick)
    cognition=core.continuous_frontier;cognition.committed=False;cognition.phase="OBSERVED";runtime._process(pending)
    deferred=next(e for e in runtime.scheduler.snapshot() if e.type==RuntimeEventType.LANGUAGE_CONTINUE);assert deferred.time==runtime.world_time and deferred.id>old_id and before==(frontier.next_token_index,core.language.exposures,core.language.sequence_support,runtime.language_tokens_processed,core.cognitive_tick)
    cognition.committed=True;cognition.phase="COMMITTED";runtime.run_to_quiescence();assert runtime.last_utterance_result.tokens==("dax","wug","blicket") and core.language.exposures=={"dax":1,"wug":1,"blicket":1}


def test_maintenance_defers_without_prune_until_language_done(monkeypatch):
    runtime=ContinuousRuntime(731);frontier=_start_after_first_token(runtime);core=runtime.simulation.core;calls=[];original=core.continuous_maintenance;monkeypatch.setattr(core,"continuous_maintenance",lambda *args:(calls.append(args),original(*args))[1]);before=(runtime.maintenance_ordinal,core.lifecycle_cursor,tuple(core.deletion_candidates),frontier.next_token_index)
    maintenance_id=runtime.scheduler.schedule(runtime.world_time,RuntimeEventType.MAINTENANCE);ready=runtime.scheduler.pop_ready(runtime.world_time);maintenance=next(e for e in ready if e.id==maintenance_id)
    for event in ready:
        if event.id!=maintenance_id:runtime.scheduler.schedule(event.time,event.type,event.payload)
    runtime._process(maintenance);deferred=next(e for e in runtime.scheduler.snapshot() if e.type==RuntimeEventType.MAINTENANCE and e.time==runtime.world_time)
    assert deferred.id>maintenance_id and not calls and before==(runtime.maintenance_ordinal,core.lifecycle_cursor,tuple(core.deletion_candidates),frontier.next_token_index)
    runtime.run_to_quiescence();assert runtime.language_frontier is None and len(calls)==1 and runtime.maintenance_ordinal==before[0]+1


def test_sequence_bookkeeping_follows_real_cognit_deletion_and_rebirth():
    runtime=ContinuousRuntime(732)
    for utterance in (("dax","wug"),("dax","wug"),("dax","blicket"),("dax","blicket"),("wug","dax"),("wug","dax")):runtime.inject_utterance(utterance);runtime.run_to_quiescence()
    core=runtime.simulation.core;dax,wug,blicket=(core.language.symbols[x] for x in ("dax","wug","blicket"));assert core.language.sequence_support[dax]=={wug:2,blicket:2} and wug in core.language.sequence_support
    core.settings=replace(core.settings,retention_threshold=2.,lifecycle_batch_size=1);core.deletion_candidates.appendleft(wug);core._prune(999)
    assert "wug" not in core.language.symbols and wug not in core.language.sequence_support and wug not in core.language.sequence_trials and wug not in core.language.sequence_materialized
    assert core.language.sequence_support[dax]=={blicket:2} and all(wug not in rows for rows in core.language.sequence_support.values()) and all(wug not in rows for rows in core.language.sequence_materialized.values())
    replacement=core.language.symbol("wug");assert replacement>wug and replacement not in core.language.sequence_support.get(dax,{})


def test_bounded_dialogue_channel_roles_and_observer_boundary():
    runtime=ContinuousRuntime(733);engine=runtime.simulation.core.backend.engine
    for n in range(70):engine.publish_dialogue_line(float(n),1 if n%2==0 else 2,f"line-{n}")
    revision,lines=engine.dialogue_snapshot();assert revision==70 and len(lines)==64 and lines[0][0]==7 and lines[-1]==(70,69.,2,"line-69")
    observer=runtime.simulation.world.native.create_brain_observer(engine);assert observer.latest_dialogue_snapshot()==(revision,lines)


def test_external_dialogue_publishes_once_after_deferral_and_once_per_utterance():
    runtime=ContinuousRuntime(734);runtime.run_to_quiescence();core=runtime.simulation.core;cognition=core.continuous_frontier;cognition.committed=False;cognition.phase="OBSERVED";runtime.inject_language("dax");event=runtime.scheduler.pop_ready(runtime.world_time)[0];runtime._process(event);assert core.backend.engine.dialogue_snapshot()==(0,[])
    cognition.committed=True;cognition.phase="COMMITTED";runtime.run_to_quiescence();revision,lines=core.backend.engine.dialogue_snapshot();assert revision==1 and [line[3] for line in lines]==["dax"]
    runtime.inject_utterance(("dax","wug"));runtime.run_to_quiescence();revision,lines=core.backend.engine.dialogue_snapshot();assert revision==2 and [line[3] for line in lines]==["dax","dax wug"] and all(line[2]==1 for line in lines)
