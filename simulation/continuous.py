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
        self.simulation=Simulation(seed,settings,backend="native");self.scheduler=EventScheduler();self.observation_ordinal=0;self.last_frame=None;self.actions_completed=0;self.cognition_wakes=0;self.cognition_continuations=0;self.cognition_generation=0;self.maintenance_ordinal=0;self._sensory_dirty=False;self._legacy_monolithic_frontier=False
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
        elif kind==RuntimeEventType.WORLD_ACTION_COMPLETE:
            action=Action(ActionType(event.payload));intent=ActionIntent(action,WorldTime(now),event.id);self.simulation.world.apply_intent(intent);self.simulation.last_action=action;self.actions_completed+=1;self.scheduler.schedule(now,RuntimeEventType.SENSORY_CHANGE)
        elif kind==RuntimeEventType.WORLD_SPAWN:
            before=self._sensory_signature();self.simulation.world.continuous_spawn(now,event.id);after=self._sensory_signature()
            if self.simulation.world.can_spawn_more():self.scheduler.schedule(now+self.simulation.world._sample_next_spawn(0),RuntimeEventType.WORLD_SPAWN)
            if before!=after:
                if self._action_in_flight():self._sensory_dirty=True
                else:self.scheduler.schedule(now,RuntimeEventType.SENSORY_CHANGE)
        elif kind==RuntimeEventType.MAINTENANCE:
            frontier=self.simulation.core.continuous_frontier
            if frontier is not None and frontier.phase in {"OBSERVED","DELIBERATING","QUIESCENT"}:self.scheduler.schedule(now,RuntimeEventType.MAINTENANCE);return
            self.maintenance_ordinal+=1;self.simulation.core.continuous_maintenance(self.maintenance_ordinal)
            self.scheduler.schedule(now+self.simulation.settings.continuous_maintenance_interval_seconds,RuntimeEventType.MAINTENANCE)
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
                self._process(event);processed+=1
                if processed>guard:raise self._runaway_error()
        self.scheduler.pop_ready(float(until));self.simulation.world.advance_world_time(float(until));self.simulation.world_time=WorldTime(float(until));return processed
    def run_to_quiescence(self,guard=100000):
        processed=0;now=self.world_time
        while self.scheduler.size and self.scheduler.snapshot()[0].time<=now:
            for event in self.scheduler.pop_ready(now):self._process(event);processed+=1
            if processed>guard:raise self._runaway_error()
        return processed
    def _runaway_error(self):
        frontier=self.simulation.core.continuous_frontier;session=frontier.session if frontier else None;goal=self.simulation.core.state.goal
        pending=[] if session is None else [work.kind.value for work in session.pending_work];history=[] if session is None else session.work_history[-12:]
        return RuntimeError(f"continuous runtime event guard exceeded: generation={self.cognition_generation} world_time={self.world_time} pending={pending} recent={history} goal_id={None if goal is None else goal.id}")
    def render_snapshot(self):
        w=self.simulation.world;w._refresh();return RenderSnapshot(self.world_time,tuple(RenderBody(b.id,b.x,b.y,b.orientation,b.held_object_id) for b in w.bodies.values()),tuple(RenderObject(o.id,o.x,o.y,o.state) for o in w.objects))
    def scheduler_state(self):return {"now":self.world_time,"next_id":self.scheduler.next_id,"events":[[e.time,e.id,e.type.name,e.payload] for e in self.scheduler.snapshot()]}
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
        save_container(path,"world",{"META":{"schema":"synthetic-entity-continuous-world","version":4},"STATE":state,"CONT":{"scheduler":self.scheduler_state(),"observation_ordinal":self.observation_ordinal,"actions_completed":self.actions_completed,"cognition_wakes":self.cognition_wakes,"cognition_continuations":self.cognition_continuations,"cognition_generation":self.cognition_generation,"maintenance_ordinal":self.maintenance_ordinal,"sensory_dirty":self._sensory_dirty,"legacy_monolithic_frontier":self._legacy_monolithic_frontier,"transition_history":history,"homeostasis":homeostasis,"elapsed_cognits":elapsed,"elapsed_relations":elapsed_relations,"dirty_relations":dirty,"frontier":self._frontier_state()},"NBRN":{"encoding":"base64","data":native}},{"NBRN"})
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
        obj=cls.__new__(cls);obj.simulation=sim;obj.scheduler=EventScheduler();cont=data["CONT"];s=cont["scheduler"];events=[RuntimeEvent(t,i,getattr(RuntimeEventType,name),p) for t,i,name,p in s["events"]];obj.scheduler.restore(s["now"],s["next_id"],events);obj.observation_ordinal=cont["observation_ordinal"];obj.actions_completed=cont["actions_completed"];obj.cognition_wakes=cont["cognition_wakes"];obj.cognition_continuations=cont.get("cognition_continuations",0);obj.cognition_generation=cont.get("cognition_generation",0);obj.maintenance_ordinal=cont.get("maintenance_ordinal",0);obj._sensory_dirty=cont.get("sensory_dirty",False);obj._legacy_monolithic_frontier=cont.get("legacy_monolithic_frontier",data["META"].get("version",1)<2 and any(e.type==RuntimeEventType.COGNITION_WAKE for e in events))
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
