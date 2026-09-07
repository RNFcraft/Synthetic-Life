from collections import deque
from dataclasses import asdict,dataclass
from typing import Any


@dataclass(frozen=True,slots=True)
class TickMetrics:
    tick:int;world_tick:int;entity_position:tuple[int,int];sensory_summary:dict[str,int];action:str;action_result:str
    cognit_count:int;relation_count:int;active_cognit_count:int;active_ratio:float;wave_size:int;wave_energy:float
    mean_threshold:float;mean_activity:float;max_activity:float;prediction_error:float;novelty:float;uncertainty:float
    controllability:float;internal_tension:float;loop_score:float;goal_id:int|None;goal_targets:tuple[int,...]
    goal_intensity:float;goal_age:int;goal_persistence:float;action_scores:dict[str,float];relation_density:float
    created_cognits:int;deleted_cognits:int;created_relations:int;deleted_relations:int;random_world_event:str|None
    unique_positions_visited:int=0
    action_tie_count:int=0;tie_set_size:int=0;tie_resolution_method:str="NONE"
    representation_coverage:float=0.0;representation_error:float=0.0;prediction_error_valid:bool=False
    known_prediction_error:float=0.0;continuity_error:float=0.0;overall_surprise:float=0.0;brier_score:float=0.0;ece:float=0.0
    primitive_event_count:int=0;local_percept_count:int=0;persistent_percept_count:int=0;tracks_created:int=0;tracks_closed:int=0
    sensorimotor_support:dict[str,int]|None=None;sensorimotor_confidence:dict[str,float]|None=None
    primitive_cognit_count:int=0;composite_cognit_count:int=0;composite_candidate_count:int=0;mean_abstraction_depth:float=0.0;max_abstraction_depth:int=0
    composites_created:int=0;composites_deleted:int=0;goals_retired:int=0;goals_suspended:int=0
    objects_spawned:int=0;push_attempts:int=0;successful_pushes:int=0;grab_attempts:int=0;successful_grabs:int=0
    release_attempts:int=0;successful_releases:int=0;interaction_attempts:int=0;successful_interactions:int=0
    unique_object_configurations:int=0;world_modification:float=0.0;provisional_relations:int=0;consolidated_relations:int=0
    self_action_relations:int=0;relation_candidates:int=0;materialization_rate:float=0.0;pattern_selectivity:float=0.0
    representation_quality:float=0.0;agency_estimate:float=0.0;body_touch_count:int=0;holding:bool=False;action_resistance:float=0.0
    visual_primitive_count:int=0;body_primitive_count:int=0
    def to_dict(self)->dict[str,Any]:return asdict(self)


class Telemetry:
    def __init__(self,capacity:int)->None:
        self.history:deque[TickMetrics]=deque(maxlen=capacity);self.peak_active_cognits=0;self.positions:set[tuple[int,int]]=set();self.object_configurations:set[tuple]=set()
    def record(self,metrics:TickMetrics)->None:
        self.history.append(metrics);self.peak_active_cognits=max(self.peak_active_cognits,metrics.active_cognit_count);self.positions.add(metrics.entity_position)
    @property
    def latest(self)->TickMetrics|None:return self.history[-1] if self.history else None
