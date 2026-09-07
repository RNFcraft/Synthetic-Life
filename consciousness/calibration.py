from collections import deque


class CalibrationTracker:
    def __init__(self,capacity:int)->None:self.samples:deque[tuple[float,float]]=deque(maxlen=capacity)
    def observe(self,predicted:dict[int,float],observed:set[int])->None:
        for node_id in set(predicted)|observed:self.samples.append((predicted.get(node_id,0.0),1.0 if node_id in observed else 0.0))
    @property
    def brier_score(self)->float:return sum((p-y)**2 for p,y in self.samples)/max(1,len(self.samples))
    @property
    def ece(self)->float:
        total=len(self.samples)
        if not total:return 0.0
        error=0.0
        for lower in (i/10 for i in range(10)):
            bucket=[(p,y) for p,y in self.samples if lower<=p<(lower+.1) or (lower==.9 and p==1)]
            if bucket:error+=len(bucket)/total*abs(sum(p for p,_ in bucket)/len(bucket)-sum(y for _,y in bucket)/len(bucket))
        return error
    def to_dict(self)->dict:return {"capacity":self.samples.maxlen,"samples":list(self.samples)}
    def restore(self,data:dict)->None:self.samples=deque((tuple(x) for x in data.get("samples",[])),maxlen=data.get("capacity",512))

