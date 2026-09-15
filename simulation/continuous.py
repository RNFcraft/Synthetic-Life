"""Deterministic event-driven v0.5.3 runtime foundation."""
from dataclasses import asdict,dataclass
import base64,os,tempfile
from config import Settings
from consciousness.native_engine import EventScheduler,RuntimeEvent,RuntimeEventType
from persistence import load_container,save_container
from world import Action,ActionIntent,ActionType,EventSequence,WorldTime
from world.perception import BodySense,SensoryCell,SensoryFrame
from consciousness.wave import WaveResult
from consciousness.patterns import SensoryEventKind,SensoryPrimitive
from consciousness.state import FutureEstimate
from consciousness.core import ContinuousCognitionFrontier
from consciousness.language import LanguageFrame,LanguageProcessingResult,LanguageUtteranceFrame,LanguageUtteranceFrontier,LanguageUtteranceResult
from .simulation import Simulation
from .snapshot import save_snapshot

@dataclass(frozen=True,slots=True)
class RenderBody:id:int;x:int;y:int;orientation:str;held_object_id:int|None
@dataclass(frozen=True,slots=True)
class RenderObject:id:int;x:int;y:int;state:int
@dataclass(frozen=True,slots=True)
class RenderSnapshot:world_time:float;bodies:tuple[RenderBody,...];objects:tuple[RenderObject,...]

class ContinuousRuntime:
    ACTION_DURATION=.15
    def __init__(self,seed=12345,settings:Settings|None=None):
        self.simulation=Simulation(seed,settings,backend="native");self.scheduler=EventScheduler();self.observation_ordinal=0;self.last_frame=None;self.actions_completed=0;self.cognition_wakes=0;self.cognition_continuations=0;self.cognition_generation=0;self.maintenance_ordinal=0;self._legacy_monolithic_frontier=False;self.language_inbox={};self.next_language_message_id=1;self.language_frontier=None;self.last_utterance_result=None;self.language_utterances_processed=0;self.language_tokens_processed=0;self.neural_bridge_deliveries=[]
        world=self.simulation.world;first=world.next_spawn_tick;world.disable_legacy_spawning()
        if first is not None:self.scheduler.schedule(float(first),RuntimeEventType.WORLD_SPAWN)
        interval=self.simulation.settings.continuous_maintenance_interval_seconds
        if interval<=0:raise ValueError("continuous maintenance interval must be positive")
        self.scheduler.schedule(float(interval),RuntimeEventType.MAINTENANCE);self.scheduler.schedule(0.,RuntimeEventType.SENSORY_CHANGE)
    @property
    def world_time(self):return self.scheduler.now
    def _process(self,event):
        now,kind=event.time,event.type
        if kind==RuntimeEventType.SENSORY_CHANGE:
            self._legacy_monolithic_frontier=False;self.cognition_generation+=1;generation=self.cognition_generation;self.last_frame=self.simulation.world.perceive(self.observation_ordinal);self.observation_ordinal+=1;self.simulation.core.begin_continuous_observation(self.last_frame,now,generation);self.scheduler.schedule(now,RuntimeEventType.COGNITION_WAKE,generation)
        elif kind==RuntimeEventType.COGNITION_WAKE:
            if self._legacy_monolithic_frontier:
                self._legacy_monolithic_frontier=False;self.cognition_wakes+=1;action=self.simulation.core.deliberate(self.last_frame);self.scheduler.schedule(now+self.ACTION_DURATION,RuntimeEventType.WORLD_ACTION_COMPLETE,action.kind.value);return
            if event.payload!=self.cognition_generation:return
            self.cognition_wakes+=1
            if self.simulation.core.begin_continuous_cognition(event.payload):self.scheduler.schedule(now,RuntimeEventType.COGNITION_CONTINUE,event.payload)
        elif kind==RuntimeEventType.COGNITION_CONTINUE:
            if event.payload!=self.cognition_generation:return
            quiet=self.simulation.core.continue_continuous_cognition(event.payload);self.cognition_continuations+=1
            if quiet:
                action=self.simulation.core.commit_continuous_action(event.payload)
                if action is not None:self.scheduler.schedule(now+self.ACTION_DURATION,RuntimeEventType.WORLD_ACTION_COMPLETE,action.kind.value)
            elif quiet is False:self.scheduler.schedule(now,RuntimeEventType.COGNITION_CONTINUE,event.payload)
        elif kind==RuntimeEventType.NEURAL_BRIDGE:
            rows=self.simulation.core.process_continuous_assembly_bridge(now);self.neural_bridge_deliveries.extend(rows)
        elif kind==RuntimeEventType.WORLD_ACTION_COMPLETE:
            action=Action(ActionType(event.payload));physical_sequence=self.simulation.event_sequence.next();intent=ActionIntent(action,WorldTime(now),physical_sequence);self.simulation.world.apply_intent(intent);self.simulation.last_action=action;self.actions_completed+=1;self.scheduler.schedule(now,RuntimeEventType.SENSORY_CHANGE)
        elif kind==RuntimeEventType.WORLD_SPAWN:
            before=self._sensory_signature();position=self.simulation.world.continuous_spawn_position()
            if position is not None:
                physical_sequence=self.simulation.event_sequence.next();self.simulation.world.continuous_spawn(position,now,physical_sequence)
            after=self._sensory_signature()
            if self.simulation.world.can_spawn_more():self.scheduler.schedule(now+self.simulation.world._sample_next_spawn(0),RuntimeEventType.WORLD_SPAWN)
            if before!=after:
                if not self._action_in_flight():self.scheduler.schedule(now,RuntimeEventType.SENSORY_CHANGE)
        elif kind==RuntimeEventType.MAINTENANCE:
            frontier=self.simulation.core.continuous_frontier
            if self.language_frontier is not None or (frontier is not None and frontier.phase in {"OBSERVED","DELIBERATING","QUIESCENT"}):self.scheduler.schedule(now,RuntimeEventType.MAINTENANCE);return
            self.maintenance_ordinal+=1;self.simulation.core.continuous_maintenance(now,self.maintenance_ordinal)
            self.scheduler.schedule(now+self.simulation.settings.continuous_maintenance_interval_seconds,RuntimeEventType.MAINTENANCE)
        elif kind==RuntimeEventType.LANGUAGE_INPUT:
            frame=self.language_inbox[event.payload];frontier=self.simulation.core.continuous_frontier
            if (frontier is not None and not frontier.committed and frontier.phase in {"OBSERVED","DELIBERATING","QUIESCENT"}) or self.language_frontier is not None:
                self.scheduler.schedule(now,RuntimeEventType.LANGUAGE_INPUT,event.payload);return
            if isinstance(frame,LanguageFrame):self._publish_external_dialogue(frame.issued_at_world_time,frame.surface);self.simulation.core.process_language(frame);del self.language_inbox[event.payload]
            else:
                self._publish_external_dialogue(frame.issued_at_world_time," ".join(frame.tokens));context=dict(self.simulation.core.grounding_context.eligible(now));self.language_frontier=LanguageUtteranceFrontier(frame,context);self.scheduler.schedule(now,RuntimeEventType.LANGUAGE_CONTINUE,event.payload)
        elif kind==RuntimeEventType.LANGUAGE_CONTINUE:
            frontier=self.language_frontier
            if frontier is None or frontier.frame.message_id!=event.payload:return
            cognition=self.simulation.core.continuous_frontier
            if cognition is not None and not cognition.committed and cognition.phase in {"OBSERVED","DELIBERATING","QUIESCENT"}:
                self.scheduler.schedule(now,RuntimeEventType.LANGUAGE_CONTINUE,event.payload);return
            if frontier.phase=="TOKEN":
                index=frontier.next_token_index;token=frontier.frame.tokens[index];result=self.simulation.core.process_language_token(LanguageFrame(frontier.frame.message_id,frontier.frame.issued_at_world_time,token),frontier.grounding_context);frontier.processed_symbol_ids.append(result.symbol_id);frontier.token_results.append(result);frontier.next_token_index+=1;self.language_tokens_processed+=1
                if frontier.next_token_index==len(frontier.frame.tokens):frontier.phase="COMPOSE"
                self.scheduler.schedule(now,RuntimeEventType.LANGUAGE_CONTINUE,event.payload)
            elif frontier.phase=="COMPOSE":
                core=self.simulation.core;core.world_time_seconds=now;core.memory.set_world_time(now);core.backend.begin_continuous_time(now);core.cognitive_tick+=1;edges,_=core.language.learn_sequence(frontier.processed_symbol_ids);active=frozenset(i for result in frontier.token_results for i in result.wave.active_ids if i in core.graph.nodes and core.graph.nodes[i].kind!="LANGUAGE_SYMBOL");relational=core.language.compose_relational(frontier.frame.tokens,frontier.processed_symbol_ids,frontier.token_results);core.language.learn_request(frontier.frame.tokens,frontier.frame.request_target is not None);request=core.language.compose_request(relational,frontier.token_results);self.last_utterance_result=LanguageUtteranceResult(frontier.frame.message_id,now,frontier.frame.tokens,tuple(frontier.processed_symbol_ids),tuple(frontier.token_results),edges,active,len(frontier.frame.tokens),relational,request);frontier.phase="DONE";self.language_utterances_processed+=1;del self.language_inbox[event.payload];self.language_frontier=None
    def inject_language(self,surface,at_time=None):
        when=self.world_time if at_time is None else float(at_time)
        if when<self.world_time:raise ValueError("language input cannot precede current WorldTime")
        message_id=self.next_language_message_id;frame=LanguageFrame(message_id,when,surface)
        self.next_language_message_id+=1;self.language_inbox[message_id]=frame;self.scheduler.schedule(when,RuntimeEventType.LANGUAGE_INPUT,message_id);return message_id
    def advance_neural_to(self,time):
        """Advance neural time with bounded coarse Assembly handoffs."""
        when=float(time)
        if when<self.world_time:raise ValueError("neural time cannot precede continuous runtime time")
        substrate=self.simulation.core.backend.engine.neurodynamic_substrate()
        while True:
            while True:
                pending=self.simulation.core.process_continuous_assembly_bridge(substrate.current_time);self.neural_bridge_deliveries.extend(pending)
                if len(pending)<64:break
            reached=substrate.advance_to_bridge_boundary(when,64)
            if reached:
                while True:
                    pending=self.simulation.core.process_continuous_assembly_bridge(substrate.current_time);self.neural_bridge_deliveries.extend(pending)
                    if len(pending)<64:break
                break
        return when
    def inject_utterance(self,tokens,at_time=None,request_target=None):
        if isinstance(tokens,str):raise TypeError("utterance token boundaries must be supplied explicitly")
        tokens=tuple(tokens)
        if len(tokens)==1 and request_target is None:return self.inject_language(tokens[0],at_time)
        if len(tokens)>self.simulation.settings.language_max_tokens_per_utterance:raise ValueError("utterance exceeds language_max_tokens_per_utterance")
        when=self.world_time if at_time is None else float(at_time)
        if when<self.world_time:raise ValueError("language input cannot precede current WorldTime")
        message_id=self.next_language_message_id;frame=LanguageUtteranceFrame(message_id,when,tokens,request_target)
        self.next_language_message_id+=1;self.language_inbox[message_id]=frame;self.scheduler.schedule(when,RuntimeEventType.LANGUAGE_INPUT,message_id);return message_id
    def _publish_external_dialogue(self,world_time,text):self.simulation.core.backend.engine.publish_dialogue_line(float(world_time),1,text)
    def _sensory_signature(self):
        cells,body=self.simulation.world.native.perceive(self.observation_ordinal,0)
        return tuple(cells),tuple(body)
    def _action_in_flight(self):
        return any(e.type==RuntimeEventType.WORLD_ACTION_COMPLETE for e in self.scheduler.snapshot())
    def run_until(self,until,guard=100000):
        processed=0
        while self.scheduler.size:
            first=self.scheduler.snapshot()[0]
            if first.time>until:break
            for event in self.scheduler.pop_ready(first.time):
                self._process(event)
                if event.type in (RuntimeEventType.SENSORY_CHANGE,RuntimeEventType.COGNITION_WAKE,RuntimeEventType.COGNITION_CONTINUE,RuntimeEventType.MAINTENANCE,RuntimeEventType.LANGUAGE_INPUT,RuntimeEventType.LANGUAGE_CONTINUE,RuntimeEventType.NEURAL_BRIDGE):self.publish_brain_snapshot(self.simulation.core.last_language_result.wave.active_ids if event.type in (RuntimeEventType.LANGUAGE_INPUT,RuntimeEventType.LANGUAGE_CONTINUE) and self.simulation.core.last_language_result else None)
                processed+=1
                if processed>guard:raise self._runaway_error()
        self.scheduler.pop_ready(float(until));self.simulation.world.advance_world_time(float(until));self.simulation.world_time=WorldTime(float(until));return processed
    def run_to_quiescence(self,guard=100000):
        processed=0;now=self.world_time
        while self.scheduler.size and self.scheduler.snapshot()[0].time<=now:
            for event in self.scheduler.pop_ready(now):
                self._process(event)
                if event.type in (RuntimeEventType.SENSORY_CHANGE,RuntimeEventType.COGNITION_WAKE,RuntimeEventType.COGNITION_CONTINUE,RuntimeEventType.MAINTENANCE,RuntimeEventType.LANGUAGE_INPUT,RuntimeEventType.LANGUAGE_CONTINUE,RuntimeEventType.NEURAL_BRIDGE):self.publish_brain_snapshot(self.simulation.core.last_language_result.wave.active_ids if event.type in (RuntimeEventType.LANGUAGE_INPUT,RuntimeEventType.LANGUAGE_CONTINUE) and self.simulation.core.last_language_result else None)
                processed+=1
            if processed>guard:raise self._runaway_error()
        return processed
    def publish_brain_snapshot(self,active_ids=None):
        """One coarse observer-only publication at causal event boundaries."""
        core=self.simulation.core;active=sorted(i-1 for i in (core.last_wave.active_ids if active_ids is None else active_ids))
        core.backend.engine.publish_brain_snapshot(float(self.world_time),core.cognitive_tick,self.cognition_generation,active)
    def _runaway_error(self):
        frontier=self.simulation.core.continuous_frontier;session=frontier.session if frontier else None;goal=self.simulation.core.state.goal
        pending=[] if session is None else [work.kind.value for work in session.pending_work];history=[] if session is None else session.work_history[-12:]
        return RuntimeError(f"continuous runtime event guard exceeded: generation={self.cognition_generation} world_time={self.world_time} pending={pending} recent={history} goal_id={None if goal is None else goal.id}")
    def render_snapshot(self):
        w=self.simulation.world;w._refresh();return RenderSnapshot(self.world_time,tuple(RenderBody(b.id,b.x,b.y,b.orientation,b.held_object_id) for b in w.bodies.values()),tuple(RenderObject(o.id,o.x,o.y,o.state) for o in w.objects))
    def scheduler_state(self):return {"now":self.world_time,"next_id":self.scheduler.next_id,"events":[[e.time,e.id,e.type.name,e.payload] for e in self.scheduler.snapshot()]}
    @staticmethod
    def _language_result_dict(result):return {"symbol_id":result.symbol_id,"wave":[sorted(result.wave.active_ids),result.wave.energy,result.wave.steps,result.wave.transmitted_energy],"candidates":result.grounding_candidates_updated,"created":result.grounding_relations_materialized}
    @staticmethod
    def _language_result_load(raw):
        ids,energy,steps,transmitted=raw["wave"];return LanguageProcessingResult(raw["symbol_id"],WaveResult(frozenset(ids),energy,steps,transmitted),raw["candidates"],raw["created"])
    @staticmethod
    def _structure_dict(value):return None if value is None else {"participant_count":value.participant_count,"relations":value.relations,"confidence":value.confidence,"source_cognits":value.source_cognits,"role_edges":value.role_edges}
    @staticmethod
    def _structure_load(raw):
        if raw is None:return None
        from consciousness.relational import RelationalStructure
        return RelationalStructure(int(raw["participant_count"]),tuple(tuple(x) for x in raw["relations"]),float(raw["confidence"]),tuple(raw.get("source_cognits",())),tuple((x[0],x[1],tuple(x[2])) for x in raw.get("role_edges",())))
    def _inbox_load(self,rows):
        out={}
        for row in rows:
            i,t,value=row[:3];target=self._structure_load(row[3]) if len(row)>3 else None
            out[int(i)]=LanguageFrame(int(i),float(t),value) if isinstance(value,str) else LanguageUtteranceFrame(int(i),float(t),tuple(value),target)
        return out
    def _language_frontier_state(self):
        f=self.language_frontier
        return None if f is None else {"frame":[f.frame.message_id,f.frame.issued_at_world_time,list(f.frame.tokens),self._structure_dict(f.frame.request_target)],"grounding_context":[[i,q] for i,q in sorted(f.grounding_context.items())],"next_token_index":f.next_token_index,"processed_symbol_ids":f.processed_symbol_ids,"token_results":[self._language_result_dict(x) for x in f.token_results],"phase":f.phase}
    def _utterance_result_state(self):
        r=self.last_utterance_result
        return None if r is None else {"message_id":r.message_id,"world_time":r.world_time,"tokens":list(r.tokens),"ordered_symbol_ids":list(r.ordered_symbol_ids),"token_results":[self._language_result_dict(x) for x in r.token_results],"sequence_edges":[list(x) for x in r.sequence_edges],"composed_active_ids":sorted(r.composed_active_ids),"token_count":r.token_count}
    def _frontier_state(self):
        f=self.last_frame;c=self.simulation.core;w=c.last_wave;events=c.patterns.last_events;s=c.state;names=("prediction_error","prediction_error_valid","representation_coverage","representation_error","continuity_error","overall_surprise","brier_score","ece","novelty","uncertainty","controllability","agency_estimate","pattern_selectivity","representation_quality","internal_tension","loop_score","tie_count","tie_resolution_method","goals_retired","goals_suspended")
        cognition=c.continuous_frontier
        cognition_data=None if cognition is None else {"generation":cognition.generation,"world_time":cognition.world_time,"current":sorted(cognition.current),"track_ids":list(cognition.track_ids),"phase":cognition.phase,"action":None if cognition.action is None else cognition.action.name,"committed":cognition.committed,"session":None if cognition.session is None else c.planner.session_to_dict(cognition.session)}
        return {"frame":None if f is None else {"tick":f.tick,"radius":f.radius,"cells":[[x.relative_x,x.relative_y,x.occupied,x.state_channel,x.boundary,x.self_present,x.appearance_channel] for x in f.cells],"body":[f.body.touch_up,f.body.touch_down,f.body.touch_left,f.body.touch_right,f.body.holding,f.body.action_resistance]},"wave":[sorted(w.active_ids),w.energy,w.steps,w.transmitted_energy],"primitives":[[p.relative_x,p.relative_y,p.channel,p.value,p.previous_value,p.change.name] for p in events],"state":{name:getattr(s,name) for name in names},"tie_set":[x.name for x in s.tie_set],"action_scores":[[a.name,v] for a,v in s.action_scores.items()],"futures":[[a.name,asdict(v)] for a,v in s.futures.items()],"cognition":cognition_data}
    def save_world(self,path):
        native_time,native_sequence=self.simulation.world.native.time_state();self.simulation.world_time=WorldTime(native_time);self.simulation.event_sequence=EventSequence(native_sequence)
        state=self.simulation.snapshot_data(semantic_graph=True)
        fd,tmp=tempfile.mkstemp(suffix=".native");os.close(fd)
        try:self.simulation.core.backend.engine.save_graph(tmp);native=base64.b64encode(open(tmp,"rb").read()).decode("ascii")
        finally:os.unlink(tmp)
        engine=self.simulation.core.backend.engine;history=engine.transition_history();homeostasis=engine.homeostasis_runtime_state();elapsed=engine.continuous_time_state();elapsed_relations=engine.continuous_relation_time_state();dirty=engine.dirty_relation_state()
        inbox=[[i,f.issued_at_world_time,f.surface if isinstance(f,LanguageFrame) else list(f.tokens),None if isinstance(f,LanguageFrame) else self._structure_dict(f.request_target)] for i,f in sorted(self.language_inbox.items())]
        save_container(path,"world",{"META":{"schema":"synthetic-entity-continuous-world","version":7},"STATE":state,"CONT":{"scheduler":self.scheduler_state(),"observation_ordinal":self.observation_ordinal,"actions_completed":self.actions_completed,"cognition_wakes":self.cognition_wakes,"cognition_continuations":self.cognition_continuations,"cognition_generation":self.cognition_generation,"maintenance_ordinal":self.maintenance_ordinal,"legacy_monolithic_frontier":self._legacy_monolithic_frontier,"transition_history":history,"homeostasis":homeostasis,"elapsed_cognits":elapsed,"elapsed_relations":elapsed_relations,"dirty_relations":dirty,"frontier":self._frontier_state(),"language":{"lexicon":self.simulation.core.language.to_dict(),"grounding":self.simulation.core.grounding_context.durable_dict(),"context":self.simulation.core.grounding_context.episode_dict(),"next_message_id":self.next_language_message_id,"inbox":inbox,"active_frontier":self._language_frontier_state(),"last_utterance_result":self._utterance_result_state(),"utterances_processed":self.language_utterances_processed,"tokens_processed":self.language_tokens_processed}},"NBRN":{"encoding":"base64","data":native}},{"NBRN"})
    @classmethod
    def load_world(cls,path,settings=None):
        data=load_container(path,"world",{"META","STATE","CONT","NBRN"});fd,tmp=tempfile.mkstemp(suffix=".json");os.close(fd)
        try:save_snapshot(data["STATE"],tmp);sim=Simulation.load(tmp,settings,"native")
        finally:os.unlink(tmp)
        fd,tmp=tempfile.mkstemp(suffix=".native");os.close(fd)
        try:
            with open(tmp,"wb") as stream:stream.write(base64.b64decode(data["NBRN"]["data"]))
            engine=sim.core.backend.engine;engine.load_graph(tmp);engine.restore_transition_history(data["CONT"].get("transition_history",[]));engine.restore_homeostasis_runtime_state(*data["CONT"]["homeostasis"]);engine.restore_continuous_time_state(*data["CONT"].get("elapsed_cognits",[False,0.0,0.0,[-1.0]*engine.cognit_count,[-1.0]*engine.cognit_count,[.25]*engine.cognit_count,0]));engine.restore_continuous_relation_time_state(*data["CONT"].get("elapsed_relations",[[],0]));engine.restore_dirty_relation_state(data["CONT"]["dirty_relations"]);sim.core.backend.invalidate_state()
        finally:os.unlink(tmp)
        obj=cls.__new__(cls);obj.simulation=sim;obj.scheduler=EventScheduler();cont=data["CONT"];s=cont["scheduler"];events=[RuntimeEvent(t,i,getattr(RuntimeEventType,name),p) for t,i,name,p in s["events"]];obj.scheduler.restore(s["now"],s["next_id"],events);obj.observation_ordinal=cont["observation_ordinal"];obj.actions_completed=cont["actions_completed"];obj.cognition_wakes=cont["cognition_wakes"];obj.cognition_continuations=cont.get("cognition_continuations",0);obj.cognition_generation=cont.get("cognition_generation",0);obj.maintenance_ordinal=cont.get("maintenance_ordinal",0);obj._legacy_monolithic_frontier=cont.get("legacy_monolithic_frontier",data["META"].get("version",1)<2 and any(e.type==RuntimeEventType.COGNITION_WAKE for e in events));language=cont.get("language",{});from consciousness.language import LanguageLexicon;sim.core.language=LanguageLexicon.from_dict(sim.core,language.get("lexicon",{}));sim.core.grounding_context.restore_durable(language.get("grounding",{}));sim.core.language.restore_legacy_grounding(sim.core.grounding_context);sim.core.grounding_context.restore_episode(language.get("context",{}));obj.next_language_message_id=int(language.get("next_message_id",1));obj.language_inbox=obj._inbox_load(language.get("inbox",[]));obj.language_utterances_processed=int(language.get("utterances_processed",0));obj.language_tokens_processed=int(language.get("tokens_processed",0));obj.language_frontier=None;obj.last_utterance_result=None;obj.neural_bridge_deliveries=[]
        active=language.get("active_frontier")
        if active is not None:
            frame=active["frame"];i,t,tokens=frame[:3];target=obj._structure_load(frame[3]) if len(frame)>3 else None;obj.language_frontier=LanguageUtteranceFrontier(LanguageUtteranceFrame(int(i),float(t),tuple(tokens),target),{int(k):float(v) for k,v in active["grounding_context"]},int(active["next_token_index"]),list(active["processed_symbol_ids"]),[obj._language_result_load(x) for x in active["token_results"]],active["phase"])
        last=language.get("last_utterance_result")
        if last is not None:obj.last_utterance_result=LanguageUtteranceResult(int(last["message_id"]),float(last["world_time"]),tuple(last["tokens"]),tuple(last["ordered_symbol_ids"]),tuple(obj._language_result_load(x) for x in last["token_results"]),tuple(tuple(x) for x in last["sequence_edges"]),frozenset(last["composed_active_ids"]),int(last["token_count"]))
        if data["META"].get("version",3)<4:
            first=sim.world.next_spawn_tick;sim.world.disable_legacy_spawning()
            if first is not None and not any(e.type==RuntimeEventType.WORLD_SPAWN for e in events):obj.scheduler.schedule(max(obj.scheduler.now,float(first)),RuntimeEventType.WORLD_SPAWN)
            if not any(e.type==RuntimeEventType.MAINTENANCE for e in events):obj.scheduler.schedule(obj.scheduler.now+sim.settings.continuous_maintenance_interval_seconds,RuntimeEventType.MAINTENANCE)
        frontier=cont["frontier"];raw=frontier["frame"]
        obj.last_frame=None if raw is None else SensoryFrame(raw["tick"],raw["radius"],tuple(SensoryCell(*x) for x in raw["cells"]),BodySense(*raw["body"]));ids,energy,steps,transmitted=frontier["wave"];sim.core.last_wave=WaveResult(frozenset(ids),energy,steps,transmitted);sim.core.patterns.last_events=tuple(SensoryPrimitive(x,y,ch,value,previous,SensoryEventKind[kind]) for x,y,ch,value,previous,kind in frontier["primitives"])
        for name,value in frontier["state"].items():setattr(sim.core.state,name,value)
        sim.core.state.tie_set=tuple(ActionType[name] for name in frontier["tie_set"]);sim.core.state.action_scores={ActionType[name]:value for name,value in frontier["action_scores"]};sim.core.state.futures={ActionType[name]:FutureEstimate(**{**value,"probabilities":{int(k):v for k,v in value["probabilities"].items()}}) for name,value in frontier["futures"]}
        cognition=frontier.get("cognition")
        if cognition is not None:
            session=None if cognition["session"] is None else sim.core.planner.session_from_dict(cognition["session"]);sim.core.continuous_frontier=ContinuousCognitionFrontier(cognition["generation"],cognition["world_time"],obj.last_frame,set(cognition["current"]),tuple(cognition["track_ids"]),session,cognition["phase"],None if cognition["action"] is None else ActionType[cognition["action"]],cognition["committed"])
        return obj
