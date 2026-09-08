"""C++ WorldRuntime authority with lightweight Python API views."""
from random import Random
from typing import Any
from config import Settings
from consciousness.native_engine import WorldRuntime
from .actions import Action,ActionResult,ActionType
from .entities import EntityBody
from .grid import Grid
from .objects import WorldObject
from .perception import BodySense,SensoryCell,SensoryFrame
from .time import ActionIntent

SHORT={"NORTH":"N","EAST":"E","SOUTH":"S","WEST":"W"};LONG={v:k for k,v in SHORT.items()};DELTA={"NORTH":(0,-1),"EAST":(1,0),"SOUTH":(0,1),"WEST":(-1,0)}
ACTION_DELTA={"UP":(0,-1),"DOWN":(0,1),"LEFT":(-1,0),"RIGHT":(1,0)}

class NativeWorld:
    """Normal native runtime: Python World physical methods are never called."""
    python_physical_calls=0
    def __init__(self,settings:Settings,rng:Random)->None:
        self.settings,self.rng=settings,rng;self.grid=Grid(settings.world_width,settings.world_height);n=max(1,settings.entity_count)
        positions=rng.sample([(x,y) for y in range(self.grid.height) for x in range(self.grid.width)],min(settings.object_count,settings.max_objects)+n)
        self.native=WorldRuntime(self.grid.width,self.grid.height,settings.perception_radius);self.native.initialize_multi([(i,*positions[i],"N",i+1) for i in range(n)],[(i+1,*p,0) for i,p in enumerate(positions[n:])])
        self.world_tick_count=0;self.next_object_id=min(settings.object_count,settings.max_objects)+1;self.next_spawn_tick=self._sample_next_spawn(0) if min(settings.object_count,settings.max_objects)<settings.max_objects else None;self.native.configure_spawning(settings.max_objects,self.next_spawn_tick,self.next_object_id)
        self.last_resistance=0.;self.last_outcome="INITIAL";self.state_change_count=0;self.body_resistance={i:0. for i in range(n)};self.body_outcomes={i:"INITIAL" for i in range(n)};self.fairness_wins={i:0 for i in range(n)};self.conflict_cursor=0;self.conflict_count=0
        self.action_counts={"push_attempts":0,"successful_pushes":0,"grab_attempts":0,"successful_grabs":0,"release_attempts":0,"successful_releases":0,"interaction_attempts":0,"successful_interactions":0,"blind_grabs":0,"blind_interactions":0}
        self._refresh();self.spawn_records=[self._spawn_record(o,0) for o in self.objects]
    def _sample_next_spawn(self,tick):return tick+self.rng.randint(self.settings.spawn_interval_min,self.settings.spawn_interval_max)
    @staticmethod
    def _spawn_record(o,tick):return {"object_id":o.id,"spawn_tick":tick,"spawn_position":o.position,"first_observed_tick":None,"first_contact_tick":None,"first_displaced_tick":None,"first_interacted_tick":None}
    def _mark(self,object_id,field):
        record=next((x for x in self.spawn_records if x["object_id"]==object_id),None)
        if record is not None and record[field] is None:record[field]=self.world_tick_count
    def _refresh(self):
        bodies,objects,held,tick,next_tick,next_id,cursor,conflicts,wins=self.native.full_state()
        self.bodies={i:EntityBody(i,x,y,LONG[o],held_id or None,appearance) for i,x,y,o,held_id,appearance in bodies};self.body=self.bodies[min(self.bodies)];self.objects=[WorldObject(i,x,y,state=state) for i,x,y,state in objects];self.held_objects={owner:WorldObject(i,x,y,state=state) for owner,i,x,y,state in held};self.held_object=self.held_objects.get(0)
        self.world_tick_count=tick;self.next_spawn_tick=next_tick;self.next_object_id=next_id;self.conflict_cursor=cursor;self.conflict_count=conflicts;self.fairness_wins={i:v for i,v in enumerate(wins)}
        self.body_resistance={i:value for i,value in enumerate(self.native.resistances())}
        self.last_resistance=self.body_resistance.get(0,0.)
    def initialize_controlled_objects(self,positions,disable_spawning=True):
        if len(set(positions))!=len(positions) or any(not self.grid.contains(*p) for p in positions):raise ValueError("controlled object positions must be unique and in bounds")
        if any(p in {b.position for b in self.bodies.values()} for p in positions):raise ValueError("controlled object overlaps body")
        self.native.initialize_multi([(i,b.x,b.y,SHORT[b.orientation],b.appearance) for i,b in self.bodies.items()],[(i+1,*p,0) for i,p in enumerate(positions)]);self.next_object_id=len(positions)+1;self.next_spawn_tick=None if disable_spawning else self._sample_next_spawn(self.world_tick_count);self.native.configure_spawning(self.settings.max_objects,self.next_spawn_tick,self.next_object_id);self._refresh();self.spawn_records=[self._spawn_record(o,self.world_tick_count) for o in self.objects]
    def object_at(self,position):return next((o for o in self.objects if o.position==position),None)
    def perceive(self,tick,body_id=0):
        cells,body=self.native.perceive(tick,body_id);frame=SensoryFrame(tick,self.settings.perception_radius,tuple(SensoryCell(*x) for x in cells),BodySense(*body));b=self.bodies[body_id];fx,fy=DELTA[b.orientation];r=self.settings.perception_radius;visible=set()
        for o in self.objects:
            dx,dy=o.x-b.x,o.y-b.y;forward=dx*fx+dy*fy;lateral=abs(dx*fy-dy*fx)
            if (dx==dy==0) or (0<forward<=r and max(abs(dx),abs(dy))<=r and lateral<=1.75*forward):visible.add(o.id)
        for record in self.spawn_records:
            if record["object_id"] in visible and record["first_observed_tick"] is None:record["first_observed_tick"]=tick
        return frame
    def _record(self,action,result,body_id,before,held,before_position):
        kind=action.kind;name=kind.name;success=result is ActionResult.SUCCESS;self.last_resistance=0. if success else 1.;self.body_resistance[body_id]=self.last_resistance
        if kind is ActionType.IDLE:outcome="IDLE"
        elif kind in (ActionType.TURN_LEFT,ActionType.TURN_RIGHT):outcome="TURN"
        elif name.startswith("MOVE_"):
            changed=[i for i,(x,y,s) in before.items() if any(o.id==i and o.position!=(x,y) for o in self.objects)]
            dx,dy=ACTION_DELTA[name[5:]];target=(before_position[0]+dx,before_position[1]+dy);obstacle=next((i for i,(x,y,_s) in before.items() if (x,y)==target),None)
            if obstacle is not None:self.action_counts["push_attempts"]+=1;self._mark(obstacle,"first_contact_tick")
            if changed:self.action_counts["successful_pushes"]+=1;self._mark(changed[0],"first_displaced_tick")
            outcome="MOVE" if success else "CONTACT" if obstacle is not None else "BOUNDARY"
        elif name.startswith("GRAB_"):
            self.action_counts["grab_attempts"]+=1
            if success:self.action_counts["successful_grabs"]+=1;self._mark(self.bodies[body_id].held_object_id,"first_contact_tick")
            else:self.action_counts["blind_grabs"]+=1
            outcome="GRAB"
        elif kind is ActionType.RELEASE:
            self.action_counts["release_attempts"]+=1
            if success:self.action_counts["successful_releases"]+=1;self._mark(held,"first_displaced_tick")
            outcome="RELEASE"
        else:
            self.action_counts["interaction_attempts"]+=1;changed=[i for i,(x,y,s) in before.items() if any(o.id==i and o.state!=s for o in self.objects)]
            if success:self.action_counts["successful_interactions"]+=1;self.state_change_count+=1;self._mark(changed[0],"first_interacted_tick")
            else:self.action_counts["blind_interactions"]+=1
            outcome="INTERACT"
        self.last_outcome=outcome;self.body_outcomes[body_id]=outcome
    def apply_action(self,action,body_id=0):
        before={o.id:(o.x,o.y,o.state) for o in self.objects};held=self.bodies[body_id].held_object_id;position=self.bodies[body_id].position;result=ActionResult(self.native.apply(action.kind.value,body_id));self._refresh();self._record(action,result,body_id,before,held,position);return result
    def apply_intent(self,intent,body_id=0):
        if body_id:return self.apply_action(intent.action,body_id)
        before={o.id:(o.x,o.y,o.state) for o in self.objects};held=self.body.held_object_id;position=self.body.position;result=ActionResult(self.native.apply_intent(intent.action.kind.value,intent.issued_at_world_time.seconds,intent.event_id));self._refresh();self._record(intent.action,result,0,before,held,position);return result
    def resolve_intents(self,intents):
        before={o.id:(o.x,o.y,o.state) for o in self.objects};held={i:b.held_object_id for i,b in self.bodies.items()};positions={i:b.position for i,b in self.bodies.items()};raw=self.native.resolve_intents(list(intents),[a.kind.value for a in intents.values()]);self._refresh();results={i:ActionResult(v) for i,v in zip(intents,raw)}
        for i,a in intents.items():self._record(a,results[i],i,before,held[i],positions[i])
        return results
    def world_tick(self):
        spawn=None;next_tick=self.next_spawn_tick
        if next_tick is not None and self.world_tick_count+1>=next_tick:
            occupied={o.position for o in self.objects}|{b.position for b in self.bodies.values()};free=[(x,y) for y in range(self.grid.height) for x in range(self.grid.width) if (x,y) not in occupied]
            if free:spawn=self.rng.choice(free)
            count=len(self.objects)+(1 if self.body.held_object_id else 0)+(1 if spawn else 0);next_tick=self._sample_next_spawn(self.world_tick_count+1) if count<self.settings.max_objects else None
        result=self.native.world_tick(spawn,next_tick);self._refresh()
        if result.startswith("SPAWN_OBJECT:"):self.spawn_records.append(self._spawn_record(next(o for o in self.objects if o.id==int(result.split(':')[1])),self.world_tick_count))
        return result
    def continuous_spawn_position(self):
        """Choose a continuous spawn position without touching native World state."""
        if not self.can_spawn_more():return None
        occupied={o.position for o in self.objects}|{b.position for b in self.bodies.values()}
        free=[(x,y) for y in range(self.grid.height) for x in range(self.grid.width) if (x,y) not in occupied]
        return self.rng.choice(free) if free else None
    def continuous_spawn(self,position,world_time,event_id):
        """Apply a selected continuous spawn as one physical event."""
        if position is None:raise ValueError("continuous spawn requires a free position")
        object_id=self.native.apply_spawn_event(position,float(world_time),int(event_id));self._refresh()
        if object_id is not None:
            self.spawn_records.append(self._spawn_record(next(o for o in self.objects if o.id==object_id),self.world_tick_count))
        return object_id
    def disable_legacy_spawning(self):
        self.native.configure_spawning(self.settings.max_objects,None,self.next_object_id);self._refresh()
    def can_spawn_more(self):
        return len(self.objects)+len(self.held_objects)<self.settings.max_objects
    def restore_native(self,world_time=0.,event_sequence=0):
        self.native.restore([(i,b.x,b.y,SHORT[b.orientation],b.appearance) for i,b in self.bodies.items()],[(o.id,o.x,o.y,o.state) for o in self.objects],[(i,o.id,o.x,o.y,o.state) for i,o in self.held_objects.items()],[self.body_resistance[i] for i in sorted(self.bodies)],self.world_tick_count,self.next_spawn_tick,self.next_object_id,self.conflict_cursor,self.conflict_count,[self.fairness_wins[i] for i in sorted(self.bodies)],world_time,event_sequence,self.settings.max_objects);self._refresh()
    def advance_world_time(self,seconds):self.native.advance_world_time(seconds)
    @staticmethod
    def _body_dict(b):return {"id":b.id,"x":b.x,"y":b.y,"orientation":b.orientation,"held_object_id":b.held_object_id,"appearance":b.appearance}
    @staticmethod
    def _object_dict(o):return {"id":o.id,"x":o.x,"y":o.y,"type":o.type,"state":o.state,"passable":o.passable}
    def to_dict(self)->dict[str,Any]:
        self._refresh();return {"width":self.grid.width,"height":self.grid.height,"world_tick":self.world_tick_count,"next_spawn_tick":self.next_spawn_tick,"next_object_id":self.next_object_id,"last_resistance":self.last_resistance,"last_outcome":self.last_outcome,"state_change_count":self.state_change_count,"body":self._body_dict(self.body),"bodies":[self._body_dict(b) for b in self.bodies.values()],"conflict_cursor":self.conflict_cursor,"conflict_count":self.conflict_count,"body_resistance":self.body_resistance,"body_outcomes":self.body_outcomes,"fairness_wins":self.fairness_wins,"objects":[self._object_dict(o) for o in self.objects],"held_object":None if self.held_object is None else self._object_dict(self.held_object),"held_objects":{str(i):self._object_dict(o) for i,o in self.held_objects.items()},"spawn_records":self.spawn_records,"action_counts":self.action_counts}
    def configuration_hash(self):return tuple(sorted([(o.x,o.y,o.state) for o in self.objects]+([(-1,-1,self.held_object.state)] if self.held_object else [])))
    def world_modification(self):
        origins={r["object_id"]:tuple(r["spawn_position"]) for r in self.spawn_records};total=float(self.state_change_count)
        for o in self.objects:origin=origins.get(o.id,o.position);total+=abs(o.x-origin[0])+abs(o.y-origin[1])
        if self.held_object:origin=origins.get(self.held_object.id,self.body.position);total+=abs(self.body.x-origin[0])+abs(self.body.y-origin[1])
        return total
