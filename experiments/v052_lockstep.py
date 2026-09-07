"""Stop at the first differing field using identical sensory input.

Diagnostic only: exports selected state; never called from runtime.
"""
import argparse
import json
from dataclasses import asdict
from pathlib import Path
from config import Settings
from simulation import Simulation

FIELDS=('activity','threshold','homeostatic_threshold','activity_trace','confidence','utility','refractory_ticks','age','last_activated_cognitive_tick','predictive_contribution','low_retention_ticks','novelty')

def compare(p,n,tick,phase,tolerance=5e-6):
    def mismatch(field,a,b):return dict(tick=tick,phase=phase,field=field,python=a,native=b)
    if set(p.graph.nodes)!=set(n.graph.nodes):return mismatch('cognit_ids',sorted(p.graph.nodes),sorted(n.graph.nodes))
    for i in sorted(p.graph.nodes):
        for field in FIELDS:
            a,b=getattr(p.graph.nodes[i],field),getattr(n.graph.nodes[i],field)
            if a==b:continue
            if isinstance(a,float) and isinstance(b,(int,float)) and abs(a-b)<=tolerance:continue
            return mismatch(f'cognit[{i}].{field}',a,b)
    for field in ('previous_active','cognitive_tick'):
        a,b=getattr(p,field),getattr(n,field)
        if a!=b:return mismatch(field,sorted(a) if isinstance(a,set) else a,sorted(b) if isinstance(b,set) else b)
    if p.graph.relation_count!=n.graph.relation_count:return mismatch('relation_count',p.graph.relation_count,n.graph.relation_count)
    for i in sorted(p.graph.nodes):
        def rows(g):return {(r.target_id,r.relation_type.value,r.context_id):r for r in g.outgoing(i)}
        a,b=rows(p.graph),rows(n.graph)
        if a.keys()!=b.keys():return mismatch(f'outgoing[{i}]',list(a),list(b))
        for key in a:
            for f in ('strength','confidence','support','lift','last_evidence_world_tick','confirmations','contradiction_evidence','usefulness'):
                x,y=getattr(a[key],f),getattr(b[key],f)
                if abs(x-y)>tolerance:return mismatch(f'relation[{i},{key}].{f}',x,y)
    return None

def run(seed=77,steps=100,objects=0):
    settings=Settings(object_count=objects,telemetry_history=1)
    p=Simulation(seed,settings);n=Simulation(seed,settings,backend='native')
    for tick in range(steps):
        frame=p.world.perceive(tick)
        p.core.step(frame);n.core.step(frame)
        result=compare(p.core,n.core,tick,'perception')
        if result:return result
        a=p.core.deliberate(frame);b=n.core.deliberate(frame)
        result=compare(p.core,n.core,tick,'deliberation')
        if result:return result
        if a.kind!=b.kind:return dict(tick=tick,phase='action',field='action',python=a.kind.name,native=b.kind.name)
        p.world.apply_action(a);n.world.apply_action(b)
        if (tick+1)%settings.world_tick_interval==0:p.world.world_tick();n.world.world_tick()
    return dict(passed=True,seed=seed,steps=steps,objects=objects)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--seed',type=int,default=77);parser.add_argument('--steps',type=int,default=100);parser.add_argument('--objects',type=int,default=0)
    args=parser.parse_args();result=run(args.seed,args.steps,args.objects)
    Path('runs/v052-first-divergence.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(result,indent=2))
