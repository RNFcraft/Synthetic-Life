"""Offline physical metrics. Nothing in this module is an organism input."""
from math import exp
from statistics import median


def integrate_tension(samples, discount):
    total=0.
    for previous,current in zip(samples,samples[1:]):
        dt=current["time"]-previous["time"]
        if dt<0: raise ValueError("nonmonotonic metric samples")
        total+=exp(-discount*(previous["time"]+current["time"])/2)*(previous["tension"]+current["tension"])/2*dt
    return total


def trajectory_metrics(samples,consumptions,horizon,discount):
    if not samples or samples[0]["time"]!=0 or samples[-1]["time"]!=horizon:
        raise ValueError("metric trajectory must cover the declared horizon")
    first=consumptions[0] if consumptions else None
    return dict(success=first is not None,time_to_consume=first["time"] if first else None,
        censored_time=first["time"] if first else horizon,
        actions_to_consume=first["actions"] if first else None,
        censored_actions=first["actions"] if first else samples[-1]["actions"],
        consumption_count=len(consumptions),
        energy_spent=sum(max(0.,a["energy"]-b["energy"]) for a,b in zip(samples,samples[1:])),
        brownout=any(sample["energy"]<=0 for sample in samples),
        brownout_entries=sum(a["energy"]>0>=b["energy"] for a,b in zip(samples,samples[1:]))+int(samples[0]["energy"]<=0),
        J=integrate_tension(samples,discount))


def behavior_key(row):
    return (not row["success"], row["censored_time"], row["censored_actions"], row["J"])


def paired_win(full,fresh): return behavior_key(full)<behavior_key(fresh)


def aggregate(rows):
    if not rows: raise ValueError("empty trial group")
    return dict(n=len(rows),successes=sum(r["success"] for r in rows),brownouts=sum(r["brownout"] for r in rows),
                **{"median_"+field:median(r[field] for r in rows) for field in
                   ("censored_time","censored_actions","energy_spent","J")})


def reduced_advantage(fresh,full,ablated,reduction):
    advantage=fresh-full
    return advantage>1e-9 and fresh-ablated<=(1-reduction)*advantage+1e-9
