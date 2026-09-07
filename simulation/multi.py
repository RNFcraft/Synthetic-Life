from dataclasses import replace
from random import Random
from config import Settings
from consciousness import SyntheticEntityCore
from world import Action,World
from .clock import SimulationClock
from .simulation import Simulation
from .snapshot import encode_random_state,save_snapshot
from persistence import load_container,save_container
from telemetry import SocialTelemetry


class MultiEntitySimulation:
    """Same-state observation, independent deliberation, simultaneous commit foundation."""
    def __init__(self,entity_count:int=2,seed:int=123,settings:Settings|None=None)->None:
        base=settings or Settings();self.settings=replace(base,entity_count=entity_count);self.seed=seed;self.rng=Random(seed);self.world=World(self.settings,self.rng);self.clock=SimulationClock()
        self.cores={i:SyntheticEntityCore(self.settings) for i in self.world.bodies};self.last_actions:dict[int,Action]={};self.last_results={};self.social=SocialTelemetry()

    def step(self)->dict[int,Action]:
        tick=self.clock.tick;frames={i:self.world.perceive(tick,i) for i in self.cores};intents={}
        for i,core in self.cores.items():core.step(frames[i]);self.social.observe(i,frames[i],core);intents[i]=core.deliberate(frames[i])
        self.social.observe_intents(tick,intents,self.world);self.last_results=self.world.resolve_intents(intents);self.last_actions=intents;self.world.world_tick();self.clock.advance();return intents

    def run(self,steps:int)->None:
        for _ in range(steps):self.step()

    def snapshot_data(self)->dict:
        cores={}
        for i,core in self.cores.items():
            holder=Simulation(self.seed,self.settings);holder.core=core;raw=holder.snapshot_data();cores[str(i)]={"cognitive_graph":raw["cognitive_graph"],"core":raw["core"]}
        return {"version":1,"seed":self.seed,"tick":self.clock.tick,"random_state":encode_random_state(self.rng.getstate()),"world":self.world.to_dict(),"cores":cores,"last_actions":{str(i):a.kind.name for i,a in self.last_actions.items()},"last_results":{str(i):r.name for i,r in self.last_results.items()}}

    def save_world(self,path:str)->None:
        save_container(path,"world",{"META":{"schema":"synthetic-entity-multiworld","version":1,"entities":len(self.cores)},"STATE":self.snapshot_data()})

    @classmethod
    def load_world(cls,path:str,settings:Settings|None=None)->"MultiEntitySimulation":
        import os,tempfile
        state=load_container(path,"world",{"META","STATE"})["STATE"];count=len(state["cores"]);multi=cls(count,state["seed"],settings)
        loaded=[]
        for key in sorted(state["cores"],key=int):
            base=Simulation(state["seed"],multi.settings).snapshot_data();base.update({"tick":state["tick"],"random_state":state["random_state"],"world":state["world"],**state["cores"][key]})
            fd,tmp=tempfile.mkstemp(suffix=".json");os.close(fd)
            try:save_snapshot(base,tmp);loaded.append(Simulation.load(tmp,multi.settings))
            finally:
                try:os.unlink(tmp)
                except OSError:pass
        multi.world=loaded[0].world;multi.rng=loaded[0].rng;multi.world.rng=multi.rng;multi.cores={i:s.core for i,s in enumerate(loaded)};multi.clock.tick=state["tick"]
        from world import ActionResult,ActionType
        multi.last_actions={int(i):Action(ActionType[name]) for i,name in state.get("last_actions",{}).items()};multi.last_results={int(i):ActionResult[name] for i,name in state.get("last_results",{}).items()};return multi
