from dataclasses import asdict
from collections import Counter,deque
from random import Random
from typing import Any
from config import Settings
from consciousness import SyntheticEntityCore
from consciousness.cognit import Cognit
from consciousness.patterns import CognitPattern
from consciousness.relation import Relation,RelationStatus,RelationType
from consciousness.state import Goal,TraceEntry
from telemetry import EventLogger,Telemetry,TickMetrics
from world import Action,ActionResult,ActionType,NativeWorld,World
from world.entities import EntityBody
from world.grid import Grid
from world.objects import WorldObject
from world.time import ActionIntent,EventSequence,WorldTime
from .clock import SimulationClock
from .snapshot import decode_random_state,encode_random_state,load_snapshot,save_snapshot
from persistence import load_container,save_container


class Simulation:
    def __init__(self,seed:int=12345,settings:Settings|None=None,backend:str="python")->None:
        self.seed=seed;self.settings=settings or Settings();self.rng=Random(seed);self.world=(NativeWorld if backend=="native" else World)(self.settings,self.rng)
        self.core=SyntheticEntityCore(self.settings,backend);self.clock=SimulationClock();self.world_time=WorldTime();self.event_sequence=EventSequence();self.telemetry=Telemetry(self.settings.telemetry_history)
        self.event_log=EventLogger();self.last_action:Action|None=None;self.last_action_result:ActionResult|None=None

    def step(self)->TickMetrics:
        tick=self.clock.tick;frame=self.world.perceive(tick);self.core.step(frame);action=self.core.deliberate(frame);intent=ActionIntent(action,self.world_time,self.event_sequence.next());result=self.world.apply_intent(intent) if isinstance(self.world,NativeWorld) else self.world.apply_action(intent.action)
        self.event_log.emit(tick,f"ACTION {action.kind.name} {result.name}");world_event=None
        if (tick+1)%self.settings.world_tick_interval==0:
            world_event=self.world.world_tick();self.event_log.emit(tick,f"WORLD_EVENT {world_event}")
        for event in self.core.events:self.event_log.emit(tick,event)
        names=("COGNIT_CREATED","COGNIT_DELETED","RELATION_CREATED","RELATION_DELETED")
        counts={name:sum(e.startswith(name) for e in self.core.events) for name in names};nodes=list(self.core.graph.nodes.values());n=len(nodes);r=self.core.graph.relation_count
        goal=self.core.state.goal;self.telemetry.object_configurations.add(self.world.configuration_hash())
        relations=[] if self.core.backend else [relation for edges in self.core.graph.adjacency.values() for relation in edges.values()]
        provisional_relations=self.core.backend.engine.provisional_count if self.core.backend else sum(x.status is RelationStatus.PROVISIONAL for x in relations)
        consolidated_relations=self.core.backend.engine.consolidated_count if self.core.backend else sum(x.status is RelationStatus.CONSOLIDATED for x in relations)
        body=frame.body;action_counts=self.world.action_counts;body_primitives=sum(e.channel.startswith("body_") for e in self.core.patterns.last_events)
        metrics=TickMetrics(tick,self.world.world_tick_count,self.world.body.position,frame.summary(),action.kind.name,result.name,n,r,
          len(self.core.last_wave.active_ids),len(self.core.last_wave.active_ids)/max(1,n),self.core.last_wave.steps,self.core.last_wave.energy,
          sum(x.effective_threshold for x in nodes)/max(1,n),sum(x.activity for x in nodes)/max(1,n),max((x.activity for x in nodes),default=0.0),
          self.core.state.prediction_error,self.core.state.novelty,self.core.state.uncertainty,self.core.state.controllability,
          self.core.state.internal_tension,self.core.state.loop_score,goal.id if goal else None,goal.target_cognit_ids if goal else (),
          goal.intensity if goal else 0.0,goal.age if goal else 0,goal.persistence if goal else 0.0,
          {a.name:v for a,v in self.core.state.action_scores.items()},r/max(1,n*(n-1)),counts[names[0]],counts[names[1]],counts[names[2]],counts[names[3]],world_event,len(self.telemetry.positions|{self.world.body.position}),
          self.core.state.tie_count,len(self.core.state.tie_set),self.core.state.tie_resolution_method,self.core.state.representation_coverage,self.core.state.representation_error,
          self.core.state.prediction_error_valid,self.core.state.prediction_error,self.core.state.continuity_error,self.core.state.overall_surprise,self.core.state.brier_score,self.core.state.ece,
          len(self.core.patterns.last_events),len(self.core.perception.last_local),sum(not t.closed for t in self.core.perception.tracks.values()),self.core.perception.last_created,self.core.perception.last_closed,
          {a.name:s.support for a,s in self.core.perception.transforms.stats.items()},{a.name:self.core.perception.transforms.estimate(a)[3] for a in ActionType},
          sum(bool(x.pattern and not x.pattern.nodes) for x in nodes),sum(bool(x.pattern and x.pattern.nodes) for x in nodes),len(self.core.composites.candidates),
          sum((x.pattern.abstraction_depth if x.pattern else 0) for x in nodes)/max(1,n),max((x.pattern.abstraction_depth if x.pattern else 0 for x in nodes),default=0),
          sum(e.startswith("COMPOSITE_CREATED") for e in self.core.events),sum(e.startswith("COMPOSITE_DELETED") for e in self.core.events),self.core.state.goals_retired,self.core.state.goals_suspended,
          len(self.world.spawn_records),action_counts["push_attempts"],action_counts["successful_pushes"],action_counts["grab_attempts"],action_counts["successful_grabs"],
          action_counts["release_attempts"],action_counts["successful_releases"],action_counts["interaction_attempts"],action_counts["successful_interactions"],
          len(self.telemetry.object_configurations),self.world.world_modification(),provisional_relations,
          consolidated_relations,sum(x.relation_type is RelationType.SELF_ACTION for x in relations),
          self.core.relation_candidates,self.core.relations_materialized/max(1,self.core.relation_candidates),self.core.state.pattern_selectivity,
          self.core.state.representation_quality,self.core.state.agency_estimate,sum((body.touch_up,body.touch_down,body.touch_left,body.touch_right)),
          body.holding,body.action_resistance,len(self.core.patterns.last_events)-body_primitives,body_primitives)
        self.telemetry.record(metrics);self.last_action=action;self.last_action_result=result;self.clock.advance();self.world_time=WorldTime(float(self.clock.tick))
        if isinstance(self.world,NativeWorld):self.world.advance_world_time(self.world_time.seconds)
        return metrics

    def run(self,ticks:int)->None:
        for _ in range(ticks):self.step()

    def snapshot_data(self,semantic_graph:bool=False)->dict[str,Any]:
        core=self.core;goal=asdict(core.state.goal) if core.state.goal else None
        return {"version":4,"seed":self.seed,"tick":self.clock.tick,"world_time_seconds":self.world_time.seconds,"event_sequence":self.event_sequence.value,"random_state":encode_random_state(self.rng.getstate()),"world":self.world.to_dict(),
          "cognitive_graph":core.graph.semantic_to_dict() if semantic_graph and core.backend else core.graph.to_dict(),"entity_state":{"last_action":self.last_action.kind.name if self.last_action else None,
          "last_action_result":self.last_action_result.name if self.last_action_result else None},"core":{"transitions":core.transitions.to_dict(),
          "previous_active":sorted(core.previous_active),"previous_action":core.previous_action.name if core.previous_action else None,
          "predictions":core.state.predictions,"goal":goal,"next_goal_id":core.next_goal_id,"goals_generated":core.state.goals_generated,
          "goal_stack":[asdict(x) for x in core.goal_stack],"target_cognit_ids":sorted(core.target_cognit_ids),"goal_metrics":{"subgoals_created":core.state.subgoals_created,"subgoals_completed":core.state.subgoals_completed,"subgoals_failed":core.state.subgoals_failed,"max_goal_depth":core.state.max_goal_depth,"parent_resumptions":core.state.parent_resumptions},
          "cognitive_tick":core.cognitive_tick,
          "relational":{"nodes":[[list(k),v] for k,v in core.relational_nodes.items()],"belief_scene":core.belief_scene.to_dict(),"current":{"participant_count":core.current_structure.participant_count,"relations":core.current_structure.relations,"confidence":core.current_structure.confidence,"source_cognits":core.current_structure.source_cognits,"role_edges":core.current_structure.role_edges},"target":None if core.target_structure is None else {"participant_count":core.target_structure.participant_count,"relations":core.target_structure.relations,"confidence":core.target_structure.confidence,"source_cognits":core.target_structure.source_cognits,"role_edges":core.target_structure.role_edges},"target_mismatch":core.target_mismatch,"previous_target_mismatch":core.previous_target_mismatch,"previous_context":sorted(core.previous_context),"previous_body_signature":core.previous_body_signature},"affordances":core.affordances.to_dict(),
          "completed_goal_lifetimes":core.state.completed_goal_lifetimes,"sensory_previous":[[x,y,*values] for (x,y),values in core.patterns.layer.previous.items()],
          "sensory_previous_body":core.patterns.layer.previous_body,"relation_prediction_enabled":core.relation_prediction_enabled,
          "available_actions":[a.name for a in core.available_actions],
          "memory":core.memory.to_dict(),"planner":core.planner.to_dict(),
          "previous_observation":sorted(getattr(core,"previous_observation",frozenset())),"predictions_without_composites":core.predictions_without_composites,
          "relation_diagnostics":{"candidates":core.relation_candidates,"materialized":core.relations_materialized,"supports":list(core.candidate_supports)[-512:],"lifts":list(core.candidate_lifts)[-512:]},
          "prototypes":[{"participants":p.participants,"occurrences":p.occurrences,"stable_observations":p.stable_observations,
          "predicted_hits":p.predicted_hits,"prediction_trials":p.prediction_trials,"explained_sum":p.explained_sum,"last_tick":p.last_tick,"translation_tolerant":p.translation_tolerant}
          for p in core.patterns.prototypes.values()],
          "perception":{"tracks":[{"id":t.id,"participants":t.participants,"centroid":t.centroid,"primitive_signature":sorted(t.primitive_signature),
          "state_signature":t.state_signature,"confidence":t.confidence,"age":t.age,"missing_ticks":t.missing_ticks,"last_seen_tick":t.last_seen_tick,"closed":t.closed}
          for t in core.perception.tracks.values()],"next_track_id":core.perception.next_track_id,
          "created_total":core.perception.created_total,"closed_total":core.perception.closed_total,"completed_lifetimes":core.perception.completed_lifetimes,
          "transforms":core.perception.transforms.to_dict()},
          "composites":{"recent":list(core.composites.recent),"candidates":[asdict(c) for c in core.composites.candidates.values()],
          "composites":[[list(k),v] for k,v in core.composites.composites.items()],"dependencies":dict(core.composites.dependencies),
          "created_total":core.composites.created_total,"deleted_total":core.composites.deleted_total},
          "tie_resolver":core.tie_resolver.to_dict(),"calibration":core.calibration.to_dict(),
          "lifecycle":{"cursor":core.lifecycle_cursor,"deletion_candidates":list(core.deletion_candidates),"dirty_cognits":sorted(core.dirty_cognits)},
          "trace":[{"tick":e.tick,"active":e.active,"action":e.action.name,"prediction":e.prediction,"prediction_error":e.prediction_error,
          "goal_id":e.goal_id,"internal_tension":e.internal_tension,"percept_ids":e.percept_ids,"representation_error":e.representation_error} for e in core.trace.entries]}}

    def save(self,path:str)->None:save_snapshot(self.snapshot_data(),path)

    def save_world(self,path:str)->None:
        import base64,tempfile,os
        sections={"META":{"schema":"synthetic-entity-world","version":2 if self.core.backend else 1,"numeric_backend":self.core.backend_name},"STATE":self.snapshot_data(semantic_graph=bool(self.core.backend))}
        if self.core.backend:
            fd,tmp=tempfile.mkstemp(suffix='.native');os.close(fd)
            try:self.core.backend.engine.save_graph(tmp);sections["NBRN"]={"encoding":"base64","data":base64.b64encode(open(tmp,'rb').read()).decode('ascii')}
            finally:
                try:os.unlink(tmp)
                except OSError:pass
        save_container(path,"world",sections,{"NBRN"})

    @classmethod
    def load_world(cls,path:str,settings:Settings|None=None,backend:str="python")->"Simulation":
        import base64,tempfile,os
        data=load_container(path,"world",{"META","STATE","NBRN"})
        fd,tmp=tempfile.mkstemp(suffix=".json");os.close(fd)
        try:
            save_snapshot(data["STATE"],tmp);sim=cls.load(tmp,settings,backend)
            if sim.core.backend and "NBRN" in data:
                fd,native_tmp=tempfile.mkstemp(suffix='.native');os.close(fd)
                try:
                    with open(native_tmp,'wb') as stream:stream.write(base64.b64decode(data["NBRN"]["data"]))
                    sim.core.backend.engine.load_graph(native_tmp);sim.core.backend.invalidate_state()
                finally:
                    try:os.unlink(native_tmp)
                    except OSError:pass
            return sim
        finally:
            try:os.unlink(tmp)
            except OSError:pass

    def save_brain(self,path:str)->None:
        import base64,tempfile,os
        snapshot=self.snapshot_data(semantic_graph=bool(self.core.backend));graph=snapshot["cognitive_graph"];core=snapshot["core"]
        patterns={"prototypes":core["prototypes"],"composites":{"composites":core["composites"]["composites"],"dependencies":core["composites"]["dependencies"],"created_total":core["composites"]["created_total"],"deleted_total":core["composites"]["deleted_total"]}}
        learned={"transforms":core["perception"]["transforms"],"relation_diagnostics":core["relation_diagnostics"],"calibration":core["calibration"],"affordances":core["affordances"],"relational_nodes":core["relational"]["nodes"]}
        sections={"META":{"schema":"synthetic-entity-brain","version":3 if self.core.backend else 2,"episode_boundary":True,"numeric_backend":self.core.backend_name},"COGN":{"next_id":graph["next_id"],"nodes":graph["nodes"]},"RELA":{"relations":graph["relations"]},"PATT":patterns,"SPAT":core["memory"],"BELS":core["relational"]["belief_scene"],"LEAR":learned,"LANG":{}}
        if self.core.backend:
            fd,tmp=tempfile.mkstemp(suffix='.native');os.close(fd)
            try:self.core.backend.engine.save_graph(tmp);sections["NBRN"]={"encoding":"base64","data":base64.b64encode(open(tmp,'rb').read()).decode('ascii')}
            finally:
                try:os.unlink(tmp)
                except OSError:pass
        save_container(path,"brain",sections,{"LANG","NBRN"})

    def load_brain(self,path:str)->None:
        import tempfile,os
        import base64
        data=load_container(path,"brain",{"META","COGN","RELA","PATT","SPAT","BELS","LEAR","LANG","NBRN"});blank=self.snapshot_data(semantic_graph=bool(self.core.backend));blank["cognitive_graph"]={**data["COGN"],**data["RELA"]};core=blank["core"]
        core["memory"]=data["SPAT"];core["prototypes"]=data["PATT"]["prototypes"];saved=data["PATT"]["composites"];core["composites"].update(saved);core["composites"]["recent"]=[];core["composites"]["candidates"]=[]
        core["perception"]["transforms"]=data["LEAR"]["transforms"];core["relation_diagnostics"]=data["LEAR"]["relation_diagnostics"];core["calibration"]=data["LEAR"]["calibration"];core["affordances"]=data["LEAR"].get("affordances",[]);core["memory"]["current_place_id"]=None;core["relational"]["nodes"]=data["LEAR"].get("relational_nodes",[]);core["relational"]["belief_scene"]=data.get("BELS",{})
        # A transferred brain begins a new episode: no track, goal, trace, plan cursor or active state survives.
        core.update({"previous_active":[],"previous_action":None,"predictions":{},"goal":None,"goal_stack":[],"target_cognit_ids":[],"sensory_previous":[],"sensory_previous_body":{},"previous_observation":[],"trace":[]});core["perception"].update({"tracks":[],"next_track_id":1,"created_total":0,"closed_total":0,"completed_lifetimes":[]});core["planner"]={}
        fd,tmp=tempfile.mkstemp(suffix=".json");os.close(fd)
        try:
            save_snapshot(blank,tmp);loaded=type(self).load(tmp,self.settings,self.core.backend_name);self.core=loaded.core
            if self.core.backend and "NBRN" in data:
                fd,native_tmp=tempfile.mkstemp(suffix='.native');os.close(fd)
                try:
                    with open(native_tmp,'wb') as stream:stream.write(base64.b64decode(data["NBRN"]["data"]))
                    self.core.backend.engine.load_graph(native_tmp);self.core.backend.invalidate_state()
                finally:
                    try:os.unlink(native_tmp)
                    except OSError:pass
            for node in self.core.graph.nodes.values():node.activity=0.;node.refractory_ticks=0
            self.core.belief_scene.new_episode()
        finally:
            try:os.unlink(tmp)
            except OSError:pass

    @classmethod
    def load(cls,path:str,settings:Settings|None=None,backend:str="python")->"Simulation":
        data=load_snapshot(path)
        if data.get("version")!=4:raise ValueError(f"Unsupported snapshot schema v{data.get('version')}; expected v4")
        sim=cls(data["seed"],settings,backend);sim.clock.tick=data["tick"];sim.world_time=WorldTime(data.get("world_time_seconds",float(sim.clock.tick)));sim.event_sequence=EventSequence(data.get("event_sequence",sim.clock.tick));sim.rng.setstate(decode_random_state(data["random_state"]));world=data["world"]
        sim.world.grid=Grid(world["width"],world["height"]);sim.world.world_tick_count=world["world_tick"]
        bodies=world.get("bodies",[world["body"]]);sim.world.bodies={x["id"]:EntityBody(**x) for x in bodies};sim.world.body=sim.world.bodies[min(sim.world.bodies)];sim.world.objects=[WorldObject(**x) for x in world["objects"]]
        sim.world.next_spawn_tick=world["next_spawn_tick"];sim.world.next_object_id=world["next_object_id"];sim.world.last_resistance=world["last_resistance"];sim.world.last_outcome=world["last_outcome"]
        sim.world.state_change_count=world.get("state_change_count",0)
        sim.world.held_objects={int(k):WorldObject(**v) for k,v in world.get("held_objects",{}).items()};sim.world.held_object=sim.world.held_objects.get(0) or (WorldObject(**world["held_object"]) if world.get("held_object") else None)
        sim.world.conflict_cursor=world.get("conflict_cursor",0);sim.world.conflict_count=world.get("conflict_count",0)
        sim.world.body_resistance={int(k):v for k,v in world.get("body_resistance",{i:0. for i in sim.world.bodies}).items()};sim.world.body_outcomes={int(k):v for k,v in world.get("body_outcomes",{i:"INITIAL" for i in sim.world.bodies}).items()};sim.world.fairness_wins={int(k):v for k,v in world.get("fairness_wins",{i:0 for i in sim.world.bodies}).items()}
        sim.world.spawn_records=[{**x,"spawn_position":tuple(x["spawn_position"])} for x in world["spawn_records"]];sim.world.action_counts=world["action_counts"]
        for key in ("blind_grabs","blind_interactions"):sim.world.action_counts.setdefault(key,0)
        if isinstance(sim.world,NativeWorld):sim.world.restore_native(sim.world_time.seconds,sim.event_sequence.value)
        graph=data["cognitive_graph"];sim.core.graph.nodes.clear()
        if not sim.core.backend:sim.core.graph.adjacency.clear();sim.core.graph.next_id=graph["next_id"]
        for raw in graph["nodes"]:
            item=dict(raw);p=item.pop("pattern");item["last_activated_cognitive_tick"]=item.pop("last_activated_tick",item.get("last_activated_cognitive_tick",None));pattern=None
            if p:
                from consciousness.patterns import PatternNode,PatternParticipantType,PatternRelation,PatternRelationType
                nodes=tuple(PatternNode(PatternParticipantType[x["participant_type"]],x["reference"],x["role"]) for x in p.get("nodes",[]))
                relations=tuple(PatternRelation(x["source"],x["target"],PatternRelationType[x["relation_type"]],x["expected_delta_t"],x["time_tolerance"],tuple(x["spatial_mean"]),x["spatial_variance"]) for x in p.get("relations",[]))
                pattern=CognitPattern(tuple(tuple(x) for x in p["participants"]),tuple(tuple(x) for x in p["relative_relationships"]),tuple(p["temporal_order"]),p["tolerance"],p["occurrence_count"],p["stability"],p["predictive_value"],nodes,relations,p.get("compression_gain",0.),p.get("redundancy",0.),p.get("abstraction_depth",0),p.get("is_translation_tolerant",False),p.get("positive_match_mean",0.),p.get("background_match_mean",0.),p.get("selectivity_trials",0))
            node=Cognit(pattern=pattern,**item);sim.core.graph.add_cognit(node)
            if pattern:
                sim.core.pattern_nodes[pattern.signature]=node.id
                for primitive in pattern.participants:sim.core.primitive_index[primitive].add(node.id)
                if pattern.selectivity_trials:sim.core._selectivity_sum+=pattern.match_selectivity;sim.core._selectivity_count+=1
        for raw in graph["relations"]:
            item=dict(raw);item["last_used_cognitive_tick"]=item.pop("last_used_tick",item.get("last_used_cognitive_tick",None));item["last_evidence_world_tick"]=item.pop("last_update_tick",item.get("last_evidence_world_tick",0));item["relation_type"]=RelationType[item["relation_type"]];item["status"]=RelationStatus[item.get("status","PROVISIONAL")];relation=Relation(**item)
            if sim.core.backend:
                native,_=sim.core.graph.connect(relation.source_id,relation.target_id,relation.relation_type,relation.context_id)
                for field in ("strength","confidence","prediction_probability","support","lift","last_evidence_world_tick","status","contradiction_evidence","usefulness","confirmations","last_used_cognitive_tick"):setattr(native,field,getattr(relation,field))
            else:sim.core.graph.adjacency[relation.source_id][(relation.target_id,relation.relation_type,relation.context_id)]=relation
        core=data["core"];sim.core.transitions.restore(core["transitions"]);sim.core.previous_active=set(core["previous_active"])
        sim.core.previous_action=ActionType[core["previous_action"]] if core["previous_action"] else None;sim.core.state.predictions={int(k):v for k,v in core["predictions"].items()}
        if core["goal"]:sim.core.state.goal=Goal(**{**core["goal"],"target_cognit_ids":tuple(core["goal"]["target_cognit_ids"]),"target_signature":tuple(tuple(x) for x in core["goal"].get("target_signature",()))})
        sim.core.goal_stack=[Goal(**{**x,"target_cognit_ids":tuple(x["target_cognit_ids"]),"target_signature":tuple(tuple(v) for v in x.get("target_signature",()))}) for x in core.get("goal_stack",[])];sim.core.target_cognit_ids=set(core.get("target_cognit_ids",[]))
        for key,value in core.get("goal_metrics",{}).items():setattr(sim.core.state,key,value)
        sim.core.cognitive_tick=core.get("cognitive_tick",sim.clock.tick)
        from consciousness.relational import RelationalStructure
        relational=core.get("relational",{});sim.core.relational_nodes={tuple(k):v for k,v in relational.get("nodes",[])}
        def restore_structure(raw):return RelationalStructure(raw["participant_count"],tuple(tuple(x) for x in raw["relations"]),raw["confidence"],tuple(raw.get("source_cognits",())),tuple((x[0],x[1],tuple(x[2])) for x in raw.get("role_edges",()))) if raw else None
        sim.core.current_structure=restore_structure(relational.get("current")) or RelationalStructure(0,());sim.core.target_structure=restore_structure(relational.get("target"));sim.core.target_mismatch=relational.get("target_mismatch",1.);sim.core.previous_target_mismatch=relational.get("previous_target_mismatch",1.);sim.core.previous_context=frozenset(relational.get("previous_context",()));sim.core.previous_body_signature=tuple(relational.get("previous_body_signature",()));sim.core.belief_scene.restore(relational.get("belief_scene",{}));sim.core.affordances.restore(core.get("affordances",[]))
        sim.core.next_goal_id=core["next_goal_id"];sim.core.state.goals_generated=core["goals_generated"];sim.core.state.completed_goal_lifetimes=core["completed_goal_lifetimes"]
        sim.core.patterns.layer.previous={(x[0],x[1]):tuple(x[2:]) for x in core["sensory_previous"]}
        sim.core.patterns.layer.previous_body=core.get("sensory_previous_body",{})
        sim.core.previous_observation=frozenset(tuple(x) for x in core.get("previous_observation",[]));sim.core.predictions_without_composites={int(k):v for k,v in core.get("predictions_without_composites",{}).items()}
        sim.core.relation_prediction_enabled=core.get("relation_prediction_enabled",True);diagnostics=core.get("relation_diagnostics",{})
        sim.core.available_actions=tuple(ActionType[x] for x in core.get("available_actions",[a.name for a in ActionType]))
        sim.core.memory.restore(core.get("memory",{}));sim.core.planner.restore(core.get("planner",{}))
        sim.core.relation_candidates=diagnostics.get("candidates",0);sim.core.relations_materialized=diagnostics.get("materialized",0)
        sim.core.candidate_supports=deque(diagnostics.get("supports",[]),maxlen=4096);sim.core.candidate_lifts=deque(diagnostics.get("lifts",[]),maxlen=4096)
        from consciousness.patterns import ProtoPattern
        for raw in core.get("prototypes",[]):
            item=dict(raw);item["participants"]=tuple(tuple(x) for x in item["participants"]);proto=ProtoPattern(**item);sim.core.patterns.prototypes[(proto.participants,proto.translation_tolerant)]=proto
        for e in core["trace"]:sim.core.trace.append(TraceEntry(e["tick"],tuple(tuple(x) for x in e["active"]),ActionType[e["action"]],tuple(tuple(x) for x in e["prediction"]),e["prediction_error"],e["goal_id"],e["internal_tension"],tuple(e.get("percept_ids",())),e.get("representation_error",0.)))
        from consciousness.percepts import PersistentPercept
        percept=core["perception"];sim.core.perception.tracks={x["id"]:PersistentPercept(**{**x,"participants":tuple(tuple(v) for v in x["participants"]),"centroid":tuple(x["centroid"]),"primitive_signature":frozenset(tuple(v) for v in x["primitive_signature"]),"state_signature":tuple(x["state_signature"])}) for x in percept["tracks"]}
        sim.core.perception.next_track_id=percept["next_track_id"];sim.core.perception.created_total=percept["created_total"];sim.core.perception.closed_total=percept["closed_total"];sim.core.perception.completed_lifetimes=percept["completed_lifetimes"];sim.core.perception.transforms.restore(percept["transforms"])
        from consciousness.composites import CompositeCandidate
        composite=core["composites"];sim.core.composites.recent=deque((tuple(x) for x in composite["recent"]),maxlen=sim.settings.composite_window_max)
        sim.core.composites.candidates={tuple(x["sequence"]):CompositeCandidate(**{**x,"sequence":tuple(x["sequence"])}) for x in composite["candidates"]};sim.core.composites.composites={tuple(k):v for k,v in composite["composites"]};sim.core.composites.dependencies=Counter({int(k):v for k,v in composite["dependencies"].items()});sim.core.composites.created_total=composite["created_total"];sim.core.composites.deleted_total=composite["deleted_total"]
        sim.core.tie_resolver.cursor=core["tie_resolver"]["cursor"];sim.core.calibration.restore(core["calibration"])
        lifecycle=core.get("lifecycle",{});sim.core.lifecycle_cursor=lifecycle.get("cursor",0);sim.core.deletion_candidates=deque(lifecycle.get("deletion_candidates",[]));sim.core.dirty_cognits=set(lifecycle.get("dirty_cognits",[]))
        entity=data["entity_state"];sim.last_action=Action(ActionType[entity["last_action"]]) if entity["last_action"] else None;sim.last_action_result=ActionResult[entity["last_action_result"]] if entity["last_action_result"] else None
        return sim
