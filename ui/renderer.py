import time
from simulation import Simulation
from simulation.clock import SpeedScheduler
from .camera import fit_grid
from .panels import draw_lines


class Renderer:
    SPEEDS=list(SpeedScheduler.SPEEDS);LABELS=["PAUSE","0.1x","0.25x","0.5x","1x","2x","5x","10x","100x","1000x","MAX"]
    TABS=["GENERAL","COGNITION","PERCEPTION","GOAL","RELATIONS","ACTION","AGENCY"]
    def __init__(self,simulation:Simulation,size:tuple[int,int]=(1200,800))->None:
        import pygame
        self.pg=pygame;pygame.init();self.screen=pygame.display.set_mode(size,pygame.RESIZABLE)
        pygame.display.set_caption("Synthetic Entity v0.4 - agency research environment")
        self.font=pygame.font.SysFont("consolas",17);self.small=pygame.font.SysFont("consolas",13)
        self.simulation=simulation;self.speed_index=4;self.scheduler=SpeedScheduler(1.0);self.tab=0;self.debug=False;self.running=True;self.fps=0.;self.tps=0.
    def run(self)->None:
        clock=self.pg.time.Clock()
        while self.running:
            started=time.perf_counter();self._events();ticks=self.scheduler.due_ticks(started,500)
            for _ in range(ticks):self.simulation.step()
            self.tps=ticks/max(time.perf_counter()-started,1e-9);self._draw();self.pg.display.flip();self.fps=clock.tick(60)
        self.pg.quit()
    def _events(self)->None:
        for event in self.pg.event.get():
            if event.type==self.pg.QUIT:self.running=False
            elif event.type==self.pg.KEYDOWN:
                if event.key in (self.pg.K_ESCAPE,self.pg.K_q):self.running=False
                elif event.key==self.pg.K_SPACE:self.speed_index=0 if self.speed_index else 4;self.scheduler.set_speed(self.SPEEDS[self.speed_index])
                elif event.key==self.pg.K_PERIOD:self.speed_index=0;self.scheduler.set_speed(0.0);self.scheduler.step_once()
                elif event.key==self.pg.K_RIGHT:self.speed_index=min(len(self.SPEEDS)-1,self.speed_index+1);self.scheduler.set_speed(self.SPEEDS[self.speed_index])
                elif event.key==self.pg.K_LEFT:self.speed_index=max(0,self.speed_index-1);self.scheduler.set_speed(self.SPEEDS[self.speed_index])
                elif event.key==self.pg.K_F1:self.debug=not self.debug
                elif self.pg.K_1<=event.key<=self.pg.K_7:self.tab=event.key-self.pg.K_1
    def _draw(self)->None:
        pg,screen=self.pg,self.screen;width,height=screen.get_size();panel_width=max(390,width//3);world_width=width-panel_width
        screen.fill((16,20,26));layout=fit_grid((0,0,world_width,height-58),self.simulation.world.grid.width,self.simulation.world.grid.height)
        for y in range(self.simulation.world.grid.height):
            for x in range(self.simulation.world.grid.width):pg.draw.rect(screen,(37,44,54),(layout.left+x*layout.cell,layout.top+y*layout.cell,layout.cell,layout.cell),1)
        for obj in self.simulation.world.objects:
            pg.draw.rect(screen,(231,166,min(230,73+obj.state*20)),(layout.left+obj.x*layout.cell+2,layout.top+obj.y*layout.cell+2,max(2,layout.cell-4),max(2,layout.cell-4)),border_radius=2)
        body=self.simulation.world.body;pg.draw.circle(screen,(82,200,160),(layout.left+body.x*layout.cell+layout.cell//2,layout.top+body.y*layout.cell+layout.cell//2),max(3,layout.cell//3))
        if body.held_object_id is not None:pg.draw.circle(screen,(231,166,73),(layout.left+body.x*layout.cell+layout.cell//2,layout.top+body.y*layout.cell+layout.cell//2),max(4,layout.cell//2),2)
        pg.draw.rect(screen,(22,28,36),(world_width,0,panel_width,height));m=self.simulation.telemetry.latest
        title=["SYNTHETIC ENTITY v0.4",f"[1] GENERAL [2] COGNITION [3] PERCEPTION",f"[4] GOAL [5] RELATIONS [6] ACTION [7] AGENCY","",self.TABS[self.tab],""]
        draw_lines(screen,self.font,title,world_width+20,18,(218,225,232),22)
        lines=self._tab_lines(m);draw_lines(screen,self.small,lines,world_width+20,150,(166,188,207),18)
        controls=f"[Space] pause [.] step [arrows] {self.LABELS[self.speed_index]} [F1] debug [Q] quit"
        draw_lines(screen,self.small,[controls],18,height-34,(165,181,197),18)
        if self.debug:
            overlay=pg.Surface((270,140),pg.SRCALPHA);overlay.fill((0,0,0,205));screen.blit(overlay,(18,18))
            draw_lines(screen,self.small,[f"FPS {self.fps:.0f}",f"ticks/sec {self.tps:,.0f}",f"active wave {len(self.simulation.core.last_wave.active_ids)}",
                f"cognits {len(self.simulation.core.graph.nodes)}",f"relations {self.simulation.core.graph.relation_count}",f"speed {self.LABELS[self.speed_index]}"],30,28,(116,224,190),19)
    def _tab_lines(self,m)->list[str]:
        core=self.simulation.core
        if m is None:return ["Waiting for first tick"]
        if self.tab==0:
            return [f"Tick / world      {m.tick} / {m.world_tick}",f"Position          {m.entity_position}",f"Chosen action     {m.action}",f"Action result     {m.action_result}","",
              f"Objects/configs   {m.objects_spawned}/{m.unique_object_configurations}",f"World modification {m.world_modification:.1f}",f"Cognits           {m.cognit_count}",f"Relations         {m.relation_count}",f"Relation density  {m.relation_density:.4f}",f"Created/deleted κ {m.created_cognits}/{m.deleted_cognits}",f"Created/deleted ρ {m.created_relations}/{m.deleted_relations}"]
        if self.tab==1:
            lines=[f"Active κ          {m.active_cognit_count} ({m.active_ratio:.1%})",f"Wave steps/energy {m.wave_size} / {m.wave_energy:.3f}",f"Mean threshold    {m.mean_threshold:.3f}",f"Mean/max activity {m.mean_activity:.3f} / {m.max_activity:.3f}","",
              f"Prediction error  {m.prediction_error:.3f}",f"Novelty           {m.novelty:.3f}",f"Uncertainty       {m.uncertainty:.3f}",f"Controllability   {m.controllability:.3f}",f"Internal tension  {m.internal_tension:.3f}",f"Loop score        {m.loop_score:.3f}","","TOP ACTIVE COGNITS"]
            lines[6:6]=[f"Primitive/composite {m.primitive_cognit_count}/{m.composite_cognit_count}",f"Composite candidates {m.composite_candidate_count}",f"Tie eps/set/method {core.settings.action_tie_epsilon:g}/{m.tie_set_size}/{m.tie_resolution_method}"]
            lines += [f"k{n.id} a={n.activity:.2f} th={n.effective_threshold:.2f} n={n.novelty:.2f} age={n.age}" for n in sorted(core.graph.nodes.values(),key=lambda n:n.activity,reverse=True)[:5]];return lines
        if self.tab==2:
            lines=[f"Visual/body σ      {m.visual_primitive_count}/{m.body_primitive_count}",f"Local percepts     {m.local_percept_count}",f"Persistent tracks {m.persistent_percept_count}",f"Coverage / error   {m.representation_coverage:.3f} / {m.representation_error:.3f}",f"Selectivity/quality {m.pattern_selectivity:.3f}/{m.representation_quality:.3f}",f"Touch/hold/resist  {m.body_touch_count}/{int(m.holding)}/{m.action_resistance:.1f}",f"Continuity error   {m.continuity_error:.3f}","","PERCEPT TRACKS"]
            lines += [f"pi{t.id} age={t.age} conf={t.confidence:.2f} missing={t.missing_ticks}" for t in list(self.simulation.core.perception.tracks.values()) if not t.closed][:8]
            lines += ["","SENSORIMOTOR"]
            lines += [f"{a.name:<11} n={s.support} conf={self.simulation.core.perception.transforms.estimate(a)[3]:.2f}" for a,s in self.simulation.core.perception.transforms.stats.items()]
            return lines
        if self.tab==3:
            goal=core.state.goal;lines=["CURRENT GOAL"]
            lines += ["none"] if goal is None else [f"G{goal.id} targets {goal.target_cognit_ids}",f"intensity         {goal.intensity:.3f}",f"confidence        {goal.confidence:.3f}",f"age/persistence   {goal.age} / {goal.persistence:.3f}"]
            lines += ["","PREDICTED FUTURES"]
            for action,future in core.state.futures.items():lines.append(f"{action.name:<11} c={future.confidence:.2f} n={future.expected_novelty:.2f} g={future.goal_alignment:.2f}") ;lines.append(f"  loop={future.loop_risk:.2f} score={future.score:.3f}")
            return lines
        if self.tab==5:
            lines=["ACTION FUTURES"]
            for action,f in sorted(core.state.futures.items(),key=lambda x:x[1].score,reverse=True)[:12]:lines.append(f"{action.name:<15} p={len(f.probabilities):<3} c={f.confidence:.2f} V={f.score:.3f}")
            lines += ["",f"tie {tuple(a.name for a in core.state.tie_set)}",f"resolver {core.state.tie_resolution_method}"];return lines
        if self.tab==6:
            return [f"AgencyEstimate    {m.agency_estimate:.3f}",f"Controllability   {m.controllability:.3f}",f"SELF_ACTION rho   {m.self_action_relations}",f"Holding           {int(m.holding)}",f"Resistance        {m.action_resistance:.1f}","",* [f"{a.name:<15} n={core.transitions.action_counts[a]}" for a in list(core.transitions.action_counts)[:10]]]
        relations=sorted((r for edges in core.graph.adjacency.values() for r in edges.values()),key=lambda r:r.strength*r.confidence,reverse=True)[:10]
        lines=[f"Total P/C/SELF {m.relation_count}/{m.provisional_relations}/{m.consolidated_relations}/{m.self_action_relations}",f"Candidates/rate {m.relation_candidates}/{m.materialization_rate:.4f}","","STRONGEST RELATIONS"]
        for relation in relations:
            action=f" a={relation.context_id}" if relation.context_id is not None else ""
            lines.extend([f"k{relation.source_id}->k{relation.target_id} {relation.relation_type.name[:4]} {relation.status.name[:4]}{action}",f"  s={relation.strength:.2f} c={relation.confidence:.2f} n={relation.support} lift={relation.lift:.2f}",f"  u={relation.usefulness:.2f} contra={relation.contradiction_evidence:.2f}"])
        return lines
