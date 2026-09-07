from simulation import Simulation


def create(seed: int = 12345) -> Simulation:
    return Simulation(seed=seed)

