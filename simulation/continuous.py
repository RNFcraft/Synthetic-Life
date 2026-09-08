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
        self.simulation=Simulation(seed,settings,backend="native");self.scheduler=EventScheduler();self.observation_ordinal=0;self.last_frame=None;self.actions_completed=0;self.cognition_wakes=0;self.scheduler.schedule(0.,RuntimeEventType.SENSORY_CHANGE)
    @property
    def world_time(self):return self.scheduler.now
    def _process(self,event):
        now,kind=event.time,event.type
        if kind==RuntimeEventType.SENSORY_CHANGE:
            self.last_frame=self.simulation.world.perceive(self.observation_ordinal);self.observation_ordinal+=1;self.simulation.core.step(self.last_frame,world_time=now);self.scheduler.schedule(now,RuntimeEventType.COGNITION_WAKE)
        elif kind==RuntimeEventType.COGNITION_WAKE:
            self.cognition_wakes+=1;action=self.simulation.core.deliberate(self.last_frame);self.scheduler.schedule(now+self.ACTION_DURATION,RuntimeEventType.WORLD_ACTION_COMPLETE,action.kind.value)
        elif kind==RuntimeEventType.WORLD_ACTION_COMPLETE:
            action=Action(ActionType(event.payload));intent=ActionIntent(action,WorldTime(now),event.id);self.simulation.world.apply_intent(intent);self.simulation.last_action=action;self.actions_completed+=1;self.scheduler.schedule(now,RuntimeEventType.SENSORY_CHANGE)
        elif kind==RuntimeEventType.MAINTENANCE:self.simulation.world.world_tick()
    def run_until(self,until,guard=100000):
        processed=0
        while self.scheduler.size:
            first=self.scheduler.snapshot()[0]
            if first.time>until:break
            for event in self.scheduler.pop_ready(first.time):
                self._process(event);processed+=1
                if processed>guard:raise RuntimeError("continuous runtime event guard exceeded")
        self.scheduler.pop_ready(float(until));self.simulation.world.advance_world_time(float(until));self.simulation.world_time=WorldTime(float(until));return processed
    def run_to_quiescence(self,guard=100000):
        processed=0;now=self.world_time
        while self.scheduler.size and self.scheduler.snapshot()[0].time<=now:
            for event in self.scheduler.pop_ready(now):self._process(event);processed+=1
            if processed>guard:raise RuntimeError("continuous runtime event guard exceeded")
        return processed
    def render_snapshot(self):
        w=self.simulation.world;w._refresh();return RenderSnapshot(self.world_time,tuple(RenderBody(b.id,b.x,b.y,b.orientation,b.held_object_id) for b in w.bodies.values()),tuple(RenderObject(o.id,o.x,o.y,o.state) for o in w.objects))
    def scheduler_state(self):return {"now":self.world_time,"next_id":self.scheduler.next_id,"events":[[e.time,e.id,e.type.name,e.payload] for e in self.scheduler.snapshot()]}
    def _frontier_state(self):
        f=self.last_frame;c=self.simulation.core;w=c.last_wave;events=c.patterns.last_events;s=c.state;names=("prediction_error","prediction_error_valid","representation_coverage","representation_error","continuity_error","overall_surprise","brier_score","ece","novelty","uncertainty","controllability","agency_estimate","pattern_selectivity","representation_quality","internal_tension","loop_score","tie_count","tie_resolution_method","goals_retired","goals_suspended")
        return {"frame":None if f is None else {"tick":f.tick,"radius":f.radius,"cells":[[x.relative_x,x.relative_y,x.occupied,x.state_channel,x.boundary,x.self_present,x.appearance_channel] for x in f.cells],"body":[f.body.touch_up,f.body.touch_down,f.body.touch_left,f.body.touch_right,f.body.holding,f.body.action_resistance]},"wave":[sorted(w.active_ids),w.energy,w.steps,w.transmitted_energy],"primitives":[[p.relative_x,p.relative_y,p.channel,p.value,p.previous_value,p.change.name] for p in events],"state":{name:getattr(s,name) for name in names},"tie_set":[x.name for x in s.tie_set],"action_scores":[[a.name,v] for a,v in s.action_scores.items()],"futures":[[a.name,asdict(v)] for a,v in s.futures.items()]}
    def save_world(self,path):
        native_time,native_sequence=self.simulation.world.native.time_state();self.simulation.world_time=WorldTime(native_time);self.simulation.event_sequence=EventSequence(native_sequence)
        fd,tmp=tempfile.mkstemp(suffix=".native");os.close(fd)
        try:self.simulation.core.backend.engine.save_graph(tmp);native=base64.b64encode(open(tmp,"rb").read()).decode("ascii")
        finally:os.unlink(tmp)
        engine=self.simulation.core.backend.engine;history=engine.transition_history();homeostasis=engine.homeostasis_runtime_state();elapsed=engine.continuous_time_state();elapsed_relations=engine.continuous_relation_time_state();dirty=engine.dirty_relation_state()
        save_container(path,"world",{"META":{"schema":"synthetic-entity-continuous-world","version":1},"STATE":self.simulation.snapshot_data(semantic_graph=True),"CONT":{"scheduler":self.scheduler_state(),"observation_ordinal":self.observation_ordinal,"actions_completed":self.actions_completed,"cognition_wakes":self.cognition_wakes,"transition_history":history,"homeostasis":homeostasis,"elapsed_cognits":elapsed,"elapsed_relations":elapsed_relations,"dirty_relations":dirty,"frontier":self._frontier_state()},"NBRN":{"encoding":"base64","data":native}},{"NBRN"})
    @classmethod
    def load_world(cls,path,settings=None):
        data=load_container(path,"world",{"META","STATE","CONT","NBRN"});fd,tmp=tempfile.mkstemp(suffix=".json");os.close(fd)
        try:save_snapshot(data["STATE"],tmp);sim=Simulation.load(tmp,settings,"native")
        finally:os.unlink(tmp)
        fd,tmp=tempfile.mkstemp(suffix=".native");os.close(fd)
        try:
            with open(tmp,"wb") as stream:stream.write(base64.b64decode(data["NBRN"]["data"]))
            engine=sim.core.backend.engine;engine.load_graph(tmp);engine.restore_transition_history(data["CONT"].get("transition_history",[]));engine.restore_homeostasis_runtime_state(*data["CONT"]["homeostasis"]);engine.restore_continuous_time_state(*data["CONT"].get("elapsed_cognits",[False,0.0,0.0,[-1.0]*engine.cognit_count,[-1.0]*engine.cognit_count,0]));engine.restore_continuous_relation_time_state(*data["CONT"].get("elapsed_relations",[[],0]));engine.restore_dirty_relation_state(data["CONT"]["dirty_relations"]);sim.core.backend.invalidate_state()
        finally:os.unlink(tmp)
        obj=cls.__new__(cls);obj.simulation=sim;obj.scheduler=EventScheduler();cont=data["CONT"];s=cont["scheduler"];events=[RuntimeEvent(t,i,getattr(RuntimeEventType,name),p) for t,i,name,p in s["events"]];obj.scheduler.restore(s["now"],s["next_id"],events);obj.observation_ordinal=cont["observation_ordinal"];obj.actions_completed=cont["actions_completed"];obj.cognition_wakes=cont["cognition_wakes"]
        frontier=cont["frontier"];raw=frontier["frame"]
        obj.last_frame=None if raw is None else SensoryFrame(raw["tick"],raw["radius"],tuple(SensoryCell(*x) for x in raw["cells"]),BodySense(*raw["body"]));ids,energy,steps,transmitted=frontier["wave"];sim.core.last_wave=WaveResult(frozenset(ids),energy,steps,transmitted);sim.core.patterns.last_events=tuple(SensoryPrimitive(x,y,ch,value,previous,SensoryEventKind[kind]) for x,y,ch,value,previous,kind in frontier["primitives"])
        for name,value in frontier["state"].items():setattr(sim.core.state,name,value)
        sim.core.state.tie_set=tuple(ActionType[name] for name in frontier["tie_set"]);sim.core.state.action_scores={ActionType[name]:value for name,value in frontier["action_scores"]};sim.core.state.futures={ActionType[name]:FutureEstimate(**{**value,"probabilities":{int(k):v for k,v in value["probabilities"].items()}}) for name,value in frontier["futures"]};return obj
