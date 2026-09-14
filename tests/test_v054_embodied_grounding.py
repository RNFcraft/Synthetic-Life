from dataclasses import replace

import pytest

from config import Settings
from consciousness.cognit import Cognit
from consciousness.language import GroundingContextEntry,GroundingContextSnapshot,GroundingContextTracker,LanguageFrame
from consciousness.native_engine import RuntimeEventType
from consciousness.wave import WaveResult
from simulation import ContinuousRuntime
from persistence import load_container,save_container


def _observe(runtime,label,t,generation):
    x,y,o=(1,1,"N") if label=="A" else (28,28,"S")
    world=runtime.simulation.world;world.native.set_body_state(0,x,y,o);world._refresh()
    runtime.simulation.core.begin_continuous_observation(world.perceive(generation),t,generation)
    return {e.cognit_id for e in runtime.simulation.core.grounding_context.latest.entries}


def _embodied(mapping,only_first=False):
    settings=replace(Settings(),object_count=0,max_objects=0,language_min_background_seconds=.3)
    runtime=ContinuousRuntime(650,settings);core=runtime.simulation.core;t=0.;generation=0
    for label in "ABABAB":generation+=1;t+=1.2;_observe(runtime,label,t,generation)
    pairs=[("A",mapping["A"])] if only_first else [("A",mapping["A"]),("B",mapping["B"])]
    for _ in range(5):
        for label,token in pairs:generation+=1;t+=1.2;_observe(runtime,label,t,generation);core.process_language(LanguageFrame(generation,t+.1,token))
    generation+=1;t+=1.2;rep_a=_observe(runtime,"A",t,generation)
    generation+=1;t+=1.2;rep_b=_observe(runtime,"B",t,generation)
    result=core.process_language(LanguageFrame(999,t+.1,"dax"));wave=set(result.wave.active_ids)
    return runtime,len(wave&rep_a),len(wave&rep_b)


def test_real_world_perception_embodied_grounding_and_permutation():
    first,a,b=_embodied({"A":"dax","B":"blicket"});second,sa,sb=_embodied({"A":"blicket","B":"dax"})
    assert a>b and sb>sa
    assert first.simulation.core.language.outgoing_scans==second.simulation.core.language.outgoing_scans==0
    assert first.simulation.core.language.native_relation_batch_calls>0


def test_first_word_learns_from_unlabelled_embodied_background():
    runtime,a,b=_embodied({"A":"dax","B":"unused"},only_first=True)
    assert a>b and set(runtime.simulation.core.language.symbols)=={"dax"}


def test_worldtime_temporal_credit_and_expiration():
    settings=replace(Settings(),language_grounding_horizon_seconds=1.,language_grounding_tau_seconds=.5)
    tracker=GroundingContextTracker(settings);tracker.observe(GroundingContextSnapshot(2.,1,(GroundingContextEntry(7,1.),)))
    assert tracker.eligible(2.25)[7]==pytest.approx(.6065306597126334)
    assert tracker.eligible(3.01)=={}


def test_delayed_trial_is_grounded_but_expired_exposure_is_not():
    settings=replace(Settings(),language_min_background_seconds=.1,language_min_support=1)
    near=ContinuousRuntime(656,settings);node=near.simulation.core.graph.add_cognit(Cognit(near.simulation.core.graph.next_id)).id
    near.simulation.core.grounding_context.observe(GroundingContextSnapshot(0.,1,(GroundingContextEntry(node,1.),)));near.simulation.core.grounding_context.accrue(.2);near.simulation.core.process_language(LanguageFrame(1,.4,"dax"))
    assert near.simulation.core.language.grounded_trials["dax"]==1
    far=ContinuousRuntime(657,settings);other=far.simulation.core.graph.add_cognit(Cognit(far.simulation.core.graph.next_id)).id
    far.simulation.core.grounding_context.observe(GroundingContextSnapshot(0.,1,(GroundingContextEntry(other,1.),)));far.simulation.core.grounding_context.accrue(2.);far.simulation.core.process_language(LanguageFrame(1,2.,"dax"))
    assert far.simulation.core.language.grounded_trials.get("dax",0)==0 and far.simulation.core.language.evidence["dax"]=={}


def test_grounding_ignores_last_wave_and_language_wave_is_separate():
    runtime=ContinuousRuntime(651,replace(Settings(),object_count=0,max_objects=0,language_min_background_seconds=0.01));core=runtime.simulation.core
    context=_observe(runtime,"A",1.,1);decoy=core.graph.add_cognit(Cognit(core.graph.next_id)).id;ordinary=WaveResult(frozenset({decoy}),.4,1);core.last_wave=ordinary
    core.process_language(LanguageFrame(1,1.1,"dax"));assert core.last_wave is ordinary
    assert decoy not in core.language.evidence["dax"] and set(core.language.evidence["dax"]).issubset(context)


def test_active_frontier_defers_same_time_exactly_once():
    runtime=ContinuousRuntime(652);event=runtime.scheduler.pop_ready(0.)[0];runtime._process(event);assert runtime.simulation.core.continuous_frontier.phase=="OBSERVED"
    message=runtime.inject_language("dax");ready=runtime.scheduler.pop_ready(0.);language_event=next(e for e in ready if e.type==RuntimeEventType.LANGUAGE_INPUT);old_id=language_event.id
    for queued in ready:runtime._process(queued)
    deferred=next(e for e in runtime.scheduler.snapshot() if e.type==RuntimeEventType.LANGUAGE_INPUT);assert deferred.time==0. and deferred.id>old_id and message in runtime.language_inbox
    runtime.run_to_quiescence();assert message not in runtime.language_inbox and runtime.simulation.core.language.exposures["dax"]==1 and runtime.simulation.event_sequence.value==0


def test_fractional_language_time_enters_native_before_mutation():
    runtime=ContinuousRuntime(653);core=runtime.simulation.core;core.grounding_context.observe(GroundingContextSnapshot(.4,1,()))
    core.process_language(LanguageFrame(1,.437,"dax"));assert core.world_time_seconds==.437 and core.backend.engine.continuous_time_state()[2]==.437


def test_language_resource_bounds_and_candidate_cap():
    vocab=ContinuousRuntime(654,replace(Settings(),max_cognits=3));core=vocab.simulation.core
    for n in range(10):core.process_language(LanguageFrame(n,float(n),f"w{n}"))
    assert len(core.graph.nodes)<=3
    settings=replace(Settings(),max_new_relations_per_tick=2,language_min_support=1,language_min_lift=0.,language_min_background_seconds=0.,language_max_provisional_candidates_per_symbol=4)
    runtime=ContinuousRuntime(655,settings);core=runtime.simulation.core;targets=[core.graph.add_cognit(Cognit(core.graph.next_id)).id for _ in range(12)];entries=tuple(GroundingContextEntry(i,1.) for i in targets);core.grounding_context.observe(GroundingContextSnapshot(0.,1,entries));core.grounding_context.accrue(1.)
    result=core.process_language(LanguageFrame(1,1.,"dax"));assert result.grounding_relations_materialized<=2 and len(core.language.evidence["dax"])<=4 and core.graph.relation_count<=settings.max_relations


def test_evidence_and_relation_state_are_order_invariant():
    def run(order):
        runtime=ContinuousRuntime(660,replace(Settings(),language_min_support=1,language_min_background_seconds=0.,language_min_lift=0.));core=runtime.simulation.core;a=core.graph.add_cognit(Cognit(core.graph.next_id)).id;b=core.graph.add_cognit(Cognit(core.graph.next_id)).id;tracker=core.grounding_context;tracker.background_mass={a:1.,b:1.};tracker.total_experience_time=2.
        for n,label in enumerate(order,1):
            target=a if label=="A" else b;t=float(n*2);tracker.latest=None;tracker.accounted_until=t;tracker.observe(GroundingContextSnapshot(t,n,(GroundingContextEntry(target,1.),)));core.process_language(LanguageFrame(n,t,"dax"))
        source=core.language.symbols["dax"];relations=sorted((r.target_id,r.strength,r.confidence,r.support,r.lift) for r in core.graph.outgoing(source));return core.language.to_dict(),relations
    assert run("AABAB")==run("BAABA")


def test_real_old_language_schema_migration(tmp_path):
    runtime=ContinuousRuntime(658);world=tmp_path/"new.seworld";runtime.save_world(world);data=load_container(world,"world",{"META","STATE","CONT","NBRN"});data["META"]["version"]=4;data["CONT"].pop("language",None);legacy=tmp_path/"v4.seworld";save_container(legacy,"world",data,{"NBRN"});loaded=ContinuousRuntime.load_world(legacy)
    assert loaded.simulation.core.language.symbols=={} and loaded.simulation.core.grounding_context.recent==loaded.simulation.core.grounding_context.recent.__class__(maxlen=loaded.simulation.settings.language_recent_contexts)
    brain=tmp_path/"new.sebrain";runtime.simulation.save_brain(brain);sections=load_container(brain,"brain",{"META","COGN","RELA","PATT","SPAT","BELS","LEAR","LANG","NBRN"});sections["META"]["version"]=4;sections["LANG"]={};old_brain=tmp_path/"v4.sebrain";save_container(old_brain,"brain",sections,{"LANG","NBRN"});fresh=runtime.simulation.__class__(659,backend="native");fresh.load_brain(old_brain);assert fresh.core.language.symbols=={} and not fresh.core.grounding_context.recent
