class SocialTelemetry:
    """External diagnostics; physical identity never returns to a cognitive Core."""
    def __init__(self,window:int=4):
        self.window=window;self.appearance_memory={};self.last_visible={};self.other_reidentifications=0;self.encounters=0;self.resource_attempts={};self.joint_object_interactions=0
    def observe(self,observer_id,frame,core):
        appearances={c.appearance_channel for c in frame.cells if c.appearance_channel}
        for appearance in appearances:
            self.encounters+=1;matches=[m for m in core.memory.structures.values() if ("appearance",appearance) in m.feature_signature]
            if not matches:continue
            memory=max(matches,key=lambda m:m.last_confirmed_tick);key=(observer_id,appearance);previous=self.appearance_memory.get(key)
            if previous==memory.cognit_id and frame.tick-self.last_visible.get(key,frame.tick)>1:self.other_reidentifications+=1
            self.appearance_memory[key]=memory.cognit_id;self.last_visible[key]=frame.tick
    def observe_intents(self,tick,intents,world):
        directions={"UP":(0,-1),"DOWN":(0,1),"LEFT":(-1,0),"RIGHT":(1,0)}
        for entity,action in intents.items():
            name=action.kind.name
            if not (name.startswith("GRAB_") or name.startswith("INTERACT_") or name.startswith("MOVE_")):continue
            dx,dy=directions[name.split("_",1)[1]];body=world.bodies[entity];obj=world.object_at((body.x+dx,body.y+dy))
            if not obj:continue
            prior=self.resource_attempts.get(obj.id)
            if prior and prior[0]!=entity and tick-prior[1]<=self.window:self.joint_object_interactions+=1
            self.resource_attempts[obj.id]=(entity,tick)
    def to_dict(self):return {"encounters":self.encounters,"other_reidentifications":self.other_reidentifications,"joint_object_interactions":self.joint_object_interactions}
