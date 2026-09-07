from simulation.clock import SpeedScheduler


def test_speed_scheduler_pause_step_and_rates()->None:
    s=SpeedScheduler(1);assert s.due_ticks(0)==0 and s.due_ticks(1)==1
    s.set_speed(.25);s.due_ticks(0);assert s.due_ticks(4)==1
    s.set_speed(0);s.due_ticks(5);assert s.due_ticks(10)==0;s.step_once();assert s.due_ticks(10)==1
    s.set_speed(-1);assert s.due_ticks(11,77)==77
