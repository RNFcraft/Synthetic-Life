"""Bounded non-semantic SensoryFrame to native receptor transduction."""
from dataclasses import dataclass
from world.perception import SensoryFrame


@dataclass(slots=True)
class SensoryNeuralTelemetry:
    sensory_frames_transduced:int=0
    sensory_receptor_events:int=0
    active_receptors:int=0


class NeuralSensoryTransducer:
    BOOLEAN_CHANNELS=3
    BODY_CHANNELS=6
    def __init__(self,settings,substrate):
        self.settings=settings;self.substrate=substrate;self.radius=settings.perception_radius;self.bins=settings.sensory_neural_channel_bins
        if self.radius<0 or self.bins<2:raise ValueError("invalid sensory receptor physiology")
        self.cell_stride=self.BOOLEAN_CHANNELS+2*self.bins;self.cell_count=(2*self.radius+1)**2
        self.receptor_count=self.cell_count*self.cell_stride+self.BODY_CHANNELS
        if self.receptor_count>settings.sensory_neural_max_receptors:raise ValueError("sensory receptor bank exceeds configured bound")
        if substrate.micro_kappa_count:
            if substrate.micro_kappa_count!=self.receptor_count:raise ValueError("neural substrate does not match sensory receptor topology")
        else:
            for _ in range(self.receptor_count):substrate.add_micro_kappa()
        self.telemetry=SensoryNeuralTelemetry()
    def _cell_base(self,x,y):
        r=self.radius
        if x < -r or x > r or y < -r or y > r:raise ValueError("sensory cell outside receptor field")
        return ((y+r)*(2*r+1)+(x+r))*self.cell_stride
    def receptor_ids(self,frame:SensoryFrame):
        if frame.radius!=self.radius:raise ValueError("sensory radius does not match receptor physiology")
        active=[];seen=set()
        for cell in sorted(frame.cells,key=lambda c:(c.relative_y,c.relative_x)):
            key=(cell.relative_x,cell.relative_y)
            if key in seen:raise ValueError("duplicate sensory cell")
            seen.add(key);base=self._cell_base(*key)
            for offset,on in enumerate((cell.occupied,cell.boundary,cell.self_present)):
                if on:active.append((base+offset,1.))
            for bank,value in ((self.BOOLEAN_CHANNELS,cell.state_channel),(self.BOOLEAN_CHANNELS+self.bins,cell.appearance_channel)):
                if not isinstance(value,int) or value<0 or value>=self.bins:raise ValueError("sensory channel outside receptor bins")
                if cell.occupied or value:active.append((base+bank+value,1.))
        body=frame.body;base=self.cell_count*self.cell_stride
        values=(body.touch_up,body.touch_down,body.touch_left,body.touch_right,body.holding,body.action_resistance)
        for offset,value in enumerate(values):
            magnitude=float(value)
            if magnitude<0. or magnitude>1.:raise ValueError("body sensory value outside physiological range")
            if magnitude:active.append((base+offset,magnitude))
        if len(active)>self.settings.sensory_neural_max_injections_per_frame:raise ValueError("sensory frame exceeds injection bound")
        return tuple(active)
    def transduce(self,frame:SensoryFrame,time:float):
        active=self.receptor_ids(frame);amplitude=self.settings.sensory_neural_input_amplitude;delay=self.settings.sensory_neural_receptor_delay
        if amplitude<=0. or delay<=0.:raise ValueError("invalid sensory stimulation physiology")
        ids=[row[0] for row in active];energies=[amplitude*row[1] for row in active];times=[float(time)+index*delay for index in range(len(active))]
        if ids:self.substrate.inject_batch(ids,energies,times)
        self.telemetry.sensory_frames_transduced+=1;self.telemetry.sensory_receptor_events+=len(ids);self.telemetry.active_receptors=len(ids)
        return tuple(ids), (float(time) if not times else times[-1])
