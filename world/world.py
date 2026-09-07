from random import Random
from typing import Any

from config import Settings
from .actions import Action, ActionResult, ActionType
from .entities import EntityBody
from .grid import Grid
from .objects import WorldObject
from .perception import BodySense, SensoryCell, SensoryFrame

DIRECTIONS = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}
ORIENTATIONS=("NORTH","EAST","SOUTH","WEST")
ACTION_ORIENTATION={"UP":"NORTH","RIGHT":"EAST","DOWN":"SOUTH","LEFT":"WEST"}
ORIENTATION_DELTA={"NORTH":(0,-1),"EAST":(1,0),"SOUTH":(0,1),"WEST":(-1,0)}


class World:
    """Deterministic physical laboratory. Only SensoryFrame crosses into Core."""
    def __init__(self, settings: Settings, rng: Random) -> None:
        self.settings, self.rng = settings, rng
        self.grid = Grid(settings.world_width, settings.world_height)
        entity_count=max(1,settings.entity_count)
        positions = rng.sample([(x, y) for y in range(self.grid.height) for x in range(self.grid.width)], min(settings.object_count, settings.max_objects) + entity_count)
        self.bodies={i:EntityBody(i,*positions[i],appearance=i+1) for i in range(entity_count)};self.body=self.bodies[0]
        self.objects = [WorldObject(i + 1, *p) for i, p in enumerate(positions[entity_count:])]
        self.held_object: WorldObject | None = None
        self.held_objects:dict[int,WorldObject]={};self.conflict_cursor=0;self.conflict_count=0
        self.body_resistance={i:0. for i in self.bodies};self.body_outcomes={i:"INITIAL" for i in self.bodies};self.fairness_wins={i:0 for i in self.bodies}
        self.world_tick_count = 0; self.next_object_id = len(self.objects) + 1
        self.next_spawn_tick = self._sample_next_spawn(0) if len(self.objects) < settings.max_objects else None
        self.last_resistance = 0.0; self.last_outcome = "INITIAL"
        self.state_change_count = 0
        self.spawn_records: list[dict[str, Any]] = [self._spawn_record(o, 0) for o in self.objects]
        self.action_counts = {"push_attempts":0,"successful_pushes":0,"grab_attempts":0,"successful_grabs":0,
                              "release_attempts":0,"successful_releases":0,"interaction_attempts":0,"successful_interactions":0,"blind_grabs":0,"blind_interactions":0}

    def _sample_next_spawn(self, tick: int) -> int:
        return tick + self.rng.randint(self.settings.spawn_interval_min, self.settings.spawn_interval_max)

    @staticmethod
    def _spawn_record(obj: WorldObject, tick: int) -> dict[str, Any]:
        return {"object_id":obj.id,"spawn_tick":tick,"spawn_position":obj.position,"first_observed_tick":None,
                "first_contact_tick":None,"first_displaced_tick":None,"first_interacted_tick":None}

    def initialize_controlled_objects(self,positions:list[tuple[int,int]],disable_spawning:bool=True)->None:
        """External experiment setup with valid identity and modification baseline."""
        if len(set(positions))!=len(positions) or any(not self.grid.contains(*p) for p in positions):raise ValueError("controlled object positions must be unique and in bounds")
        if any(p in {b.position for b in self.bodies.values()} for p in positions):raise ValueError("controlled object overlaps body")
        self.objects=[WorldObject(i+1,*p) for i,p in enumerate(positions)];self.held_objects={};self.held_object=None
        for body in self.bodies.values():body.held_object_id=None
        self.next_object_id=len(self.objects)+1;self.spawn_records=[self._spawn_record(o,self.world_tick_count) for o in self.objects];self.next_spawn_tick=None if disable_spawning else self._sample_next_spawn(self.world_tick_count)

    def object_at(self, position: tuple[int,int]) -> WorldObject | None:
        return next((o for o in self.objects if o.position == position), None)

    def _touch(self, dx: int, dy: int) -> bool:
        p=(self.body.x+dx,self.body.y+dy); return not self.grid.contains(*p) or self.object_at(p) is not None or any(b is not self.body and b.position==p for b in self.bodies.values())

    def perceive(self, tick: int, body_id:int=0) -> SensoryFrame:
        primary=self.body;self.body=self.bodies[body_id]
        occupied={o.position:o for o in self.objects};cells=[];r=self.settings.perception_radius;visible_ids=set()
        for dy in range(-r,r+1):
            for dx in range(-r,r+1):
                if not self._visible_offset(dx,dy,r):continue
                x,y=self.body.x+dx,self.body.y+dy;boundary=not self.grid.contains(x,y);obj=occupied.get((x,y)) if not boundary else None
                if obj:visible_ids.add(obj.id)
                other=next((b for b in self.bodies.values() if b is not self.body and b.position==(x,y)),None)
                cells.append(SensoryCell(dx,dy,obj is not None or other is not None,obj.state if obj else 0,boundary,dx==0 and dy==0,other.appearance if other else 0))
        for record in self.spawn_records:
            if record["object_id"] in visible_ids and record["first_observed_tick"] is None:record["first_observed_tick"]=tick
        body=BodySense(self._touch(0,-1),self._touch(0,1),self._touch(-1,0),self._touch(1,0),self.body.held_object_id is not None,self.body_resistance.get(body_id,0.))
        frame=SensoryFrame(tick,r,tuple(cells),body);self.body=primary;return frame

    def _visible_offset(self,dx:int,dy:int,radius:int)->bool:
        if dx==dy==0:return True
        fx,fy=ORIENTATION_DELTA[self.body.orientation];forward=dx*fx+dy*fy;lateral=abs(dx*fy-dy*fx)
        return 0<forward<=radius and max(abs(dx),abs(dy))<=radius and lateral<=1.75*forward

    def _mark(self, object_id: int, field: str) -> None:
        record=next((r for r in self.spawn_records if r["object_id"]==object_id),None)
        if record is not None and record[field] is None:record[field]=self.world_tick_count

    def apply_action(self,action:Action,body_id:int=0)->ActionResult:
        primary=self.body;self.body=self.bodies[body_id];self.held_object=self.held_objects.get(body_id)
        result=self._apply_current(action)
        self.body_resistance[body_id]=self.last_resistance;self.body_outcomes[body_id]=self.last_outcome
        if self.held_object is None:self.held_objects.pop(body_id,None)
        else:self.held_objects[body_id]=self.held_object
        self.body=primary;self.held_object=self.held_objects.get(0);return result

    def _apply_current(self, action: Action) -> ActionResult:
        self.last_resistance=0.0;kind=action.kind;name=kind.name
        if kind is ActionType.IDLE:self.last_outcome="IDLE";return ActionResult.SUCCESS
        if kind in (ActionType.TURN_LEFT,ActionType.TURN_RIGHT):
            index=ORIENTATIONS.index(self.body.orientation);step=-1 if kind is ActionType.TURN_LEFT else 1;self.body.orientation=ORIENTATIONS[(index+step)%4];self.last_outcome="TURN";return ActionResult.SUCCESS
        if name.startswith("MOVE_"):return self._move(name[5:])
        if name.startswith("GRAB_"):return self._grab(name[5:])
        if kind is ActionType.RELEASE:return self._release()
        if name.startswith("INTERACT_"):return self._interact(name[9:])
        if kind is ActionType.INTERACT:return self._interact({v:k for k,v in ACTION_ORIENTATION.items()}[self.body.orientation])
        return self._blocked("INVALID",ActionResult.INVALID)

    def _move(self, direction: str) -> ActionResult:
        dx,dy=DIRECTIONS[direction];target=(self.body.x+dx,self.body.y+dy);self.body.orientation=ACTION_ORIENTATION[direction]
        if not self.grid.contains(*target) or any(b is not self.body and b.position==target for b in self.bodies.values()):return self._blocked("BOUNDARY")
        obstacle=self.object_at(target)
        if obstacle is not None:
            self.action_counts["push_attempts"]+=1;self._mark(obstacle.id,"first_contact_tick");beyond=(target[0]+dx,target[1]+dy)
            if self.body.held_object_id is not None or not self.grid.contains(*beyond) or self.object_at(beyond) is not None or any(b is not self.body and b.position==beyond for b in self.bodies.values()):return self._blocked("CONTACT")
            obstacle.x,obstacle.y=beyond;self.action_counts["successful_pushes"]+=1;self._mark(obstacle.id,"first_displaced_tick")
        self.body.x,self.body.y=target;self.last_outcome="MOVE";return ActionResult.SUCCESS

    def _grab(self, direction: str) -> ActionResult:
        self.action_counts["grab_attempts"]+=1;self.body.orientation=ACTION_ORIENTATION[direction]
        if self.body.held_object_id is not None:return self._blocked("GRAB")
        dx,dy=DIRECTIONS[direction];obj=self.object_at((self.body.x+dx,self.body.y+dy))
        if obj is None:self.action_counts["blind_grabs"]+=1;return self._blocked("GRAB")
        self.body.held_object_id=obj.id;self.held_object=obj;self.objects.remove(obj);self.action_counts["successful_grabs"]+=1;self._mark(obj.id,"first_contact_tick");self.last_outcome="GRAB";return ActionResult.SUCCESS

    def _release(self) -> ActionResult:
        self.action_counts["release_attempts"]+=1
        if self.body.held_object_id is None:return self._blocked("RELEASE")
        dx,dy=ORIENTATION_DELTA[self.body.orientation];target=(self.body.x+dx,self.body.y+dy)
        if not self.grid.contains(*target) or self.object_at(target) is not None or any(b is not self.body and b.position==target for b in self.bodies.values()):return self._blocked("RELEASE")
        obj=self.held_object or WorldObject(self.body.held_object_id,*target);obj.x,obj.y=target;self.objects.append(obj);self.body.held_object_id=None;self.held_object=None
        self.action_counts["successful_releases"]+=1;self._mark(obj.id,"first_displaced_tick");self.last_outcome="RELEASE";return ActionResult.SUCCESS

    def _interact(self, direction: str) -> ActionResult:
        self.action_counts["interaction_attempts"]+=1;self.body.orientation=ACTION_ORIENTATION[direction];dx,dy=DIRECTIONS[direction]
        obj=self.object_at((self.body.x+dx,self.body.y+dy))
        if obj is None:self.action_counts["blind_interactions"]+=1;return self._blocked("INTERACT")
        obj.state=1-obj.state;self.state_change_count+=1;self.action_counts["successful_interactions"]+=1;self._mark(obj.id,"first_interacted_tick");self.last_outcome="INTERACT";return ActionResult.SUCCESS

    def _blocked(self, outcome: str, result: ActionResult=ActionResult.BLOCKED) -> ActionResult:
        self.last_resistance=1.0;self.last_outcome=outcome;return result

    def world_tick(self) -> str:
        self.world_tick_count+=1
        if self.next_spawn_tick is None or self.world_tick_count<self.next_spawn_tick:return "NOTHING"
        blocked={o.position for o in self.objects}|{b.position for b in self.bodies.values()};free=[(x,y) for y in range(self.grid.height) for x in range(self.grid.width) if (x,y) not in blocked]
        if not free:self.next_spawn_tick=self._sample_next_spawn(self.world_tick_count);return "SPAWN_BLOCKED"
        pos=self.rng.choice(free);obj=WorldObject(self.next_object_id,*pos);self.next_object_id+=1;self.objects.append(obj);self.spawn_records.append(self._spawn_record(obj,self.world_tick_count))
        count=len(self.objects)+(1 if self.body.held_object_id else 0);self.next_spawn_tick=self._sample_next_spawn(self.world_tick_count) if count<self.settings.max_objects else None
        return f"SPAWN_OBJECT:{obj.id}"

    def resolve_intents(self,intents:dict[int,Action])->dict[int,ActionResult]:
        # Classify all destinations/resources from immutable S_t before applying effects.
        destinations={};resources={};body_positions={i:b.position for i,b in self.bodies.items()}
        for i,action in intents.items():
            b=self.bodies[i];name=action.kind.name;target=None;resource=None
            if name.startswith(("MOVE_","GRAB_","INTERACT_")):
                prefix="MOVE_" if name.startswith("MOVE_") else "GRAB_" if name.startswith("GRAB_") else "INTERACT_";dx,dy=DIRECTIONS[name[len(prefix):]];target=(b.x+dx,b.y+dy)
            elif action.kind is ActionType.INTERACT:
                dx,dy=ORIENTATION_DELTA[b.orientation];target=(b.x+dx,b.y+dy)
            elif action.kind is ActionType.RELEASE:
                dx,dy=ORIENTATION_DELTA[b.orientation];target=(b.x+dx,b.y+dy)
            obj=self.object_at(target) if target is not None else None
            if name.startswith("MOVE_"):
                if target in body_positions.values():destinations[i]=target
                elif obj:
                    dx=target[0]-b.x;dy=target[1]-b.y;destinations[i]=(target[0]+dx,target[1]+dy);resource=obj.id
                else:destinations[i]=target
            elif name.startswith("GRAB_") or name.startswith("INTERACT_") or action.kind is ActionType.INTERACT:resource=obj.id if obj else None
            elif action.kind is ActionType.RELEASE:destinations[i]=target;resource=b.held_object_id
            if resource is not None:resources[i]=resource
        blocked=set()
        # Initial body occupancy is never assumed vacated; swaps/chains are neutral-blocked.
        for i,dest in destinations.items():
            if any(j!=i and pos==dest for j,pos in body_positions.items()):blocked.add(i)
        def arbitrate(groups):
            for contenders in groups.values():
                contenders=sorted(set(contenders)-blocked)
                if len(contenders)>1:
                    winner=contenders[self.conflict_cursor%len(contenders)];self.fairness_wins[winner]+=1;self.conflict_cursor=(self.conflict_cursor+1)%max(1,len(self.bodies));self.conflict_count+=1;blocked.update(set(contenders)-{winner})
        by_dest={};by_resource={}
        for i,x in destinations.items():by_dest.setdefault(x,[]).append(i)
        for i,x in resources.items():by_resource.setdefault(x,[]).append(i)
        arbitrate(by_dest);arbitrate(by_resource)
        results={}
        for body_id in sorted(intents):
            if body_id in blocked:self.body_resistance[body_id]=1.;self.body_outcomes[body_id]="CONFLICT";results[body_id]=ActionResult.BLOCKED
            else:results[body_id]=self.apply_action(intents[body_id],body_id)
        return results

    def to_dict(self) -> dict[str,Any]:
        return {"width":self.grid.width,"height":self.grid.height,"world_tick":self.world_tick_count,"next_spawn_tick":self.next_spawn_tick,"next_object_id":self.next_object_id,
                "last_resistance":self.last_resistance,"last_outcome":self.last_outcome,"state_change_count":self.state_change_count,"body":{"id":self.body.id,"x":self.body.x,"y":self.body.y,"orientation":self.body.orientation,"held_object_id":self.body.held_object_id,"appearance":self.body.appearance},
                "bodies":[{"id":b.id,"x":b.x,"y":b.y,"orientation":b.orientation,"held_object_id":b.held_object_id,"appearance":b.appearance} for b in self.bodies.values()],"conflict_cursor":self.conflict_cursor,"conflict_count":self.conflict_count,
                "body_resistance":self.body_resistance,"body_outcomes":self.body_outcomes,"fairness_wins":self.fairness_wins,
                "objects":[{"id":o.id,"x":o.x,"y":o.y,"type":o.type,"state":o.state,"passable":o.passable} for o in self.objects],
                "held_object":None if self.held_object is None else {"id":self.held_object.id,"x":self.held_object.x,"y":self.held_object.y,"type":self.held_object.type,"state":self.held_object.state,"passable":self.held_object.passable},
                "held_objects":{str(i):{"id":o.id,"x":o.x,"y":o.y,"type":o.type,"state":o.state,"passable":o.passable} for i,o in self.held_objects.items()},
                "spawn_records":self.spawn_records,"action_counts":self.action_counts}

    def configuration_hash(self) -> tuple[tuple[int,int,int],...]:
        values=[(o.x,o.y,o.state) for o in self.objects]
        if self.held_object is not None:values.append((-1,-1,self.held_object.state))
        return tuple(sorted(values))

    def world_modification(self) -> float:
        spawn={r["object_id"]:tuple(r["spawn_position"]) for r in self.spawn_records};total=float(self.state_change_count)
        for obj in self.objects:
            origin=spawn.get(obj.id,obj.position);total+=abs(obj.x-origin[0])+abs(obj.y-origin[1])
        if self.held_object is not None:
            origin=spawn.get(self.held_object.id,self.body.position);total+=abs(self.body.x-origin[0])+abs(self.body.y-origin[1])
        return total
