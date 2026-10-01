"""Structural, bounded valuation of learned internal sensory consequences.

No body, physical resource, or action identity is an input to this helper.
Unpredicted probability mass means unchanged internal state, not improvement.
"""
from dataclasses import dataclass
from .patterns import is_internal_primitive


@dataclass(frozen=True)
class InternalEstimate:
    levels: tuple[float, ...]
    progress: float
    confidence: float
    predictions: int


def internal_estimate(graph, probabilities, levels, targets, bins):
    distributions = [{} for _ in levels]
    for node_id, probability in sorted(probabilities.items()):
        node = graph.nodes.get(node_id)
        pattern = node.pattern if node else None
        # Singleton sensor states avoid counting composites as independent evidence.
        if not pattern or len(pattern.participants) != 1:
            continue
        primitive = pattern.participants[0]
        if not is_internal_primitive(primitive):
            continue
        channel = primitive[2].removeprefix("internal_")
        if not channel.isdecimal():
            continue
        index, level = int(channel), primitive[3]
        if index >= len(levels) or not 0 <= level < bins:
            continue
        distribution = distributions[index]
        distribution[level] = max(distribution.get(level, 0.), max(0., min(1., probability)))
    predicted = list(levels)
    progress = confidence = 0.
    count = 0
    for index, distribution in enumerate(distributions):
        mass = sum(distribution.values())
        if not mass:
            continue
        count += len(distribution)
        scale = max(1., mass)
        known_mass = mass / scale
        current_distance = abs(levels[index] - targets[index])
        future_distance = (1. - known_mass) * current_distance
        future_distance += sum(p / scale * abs(level - targets[index]) for level, p in sorted(distribution.items()))
        progress += (current_distance - future_distance) / ((bins - 1) * len(levels))
        predicted[index] = (1. - known_mass) * levels[index] + sum(p / scale * level for level, p in sorted(distribution.items()))
        confidence += known_mass / len(levels)
    return InternalEstimate(tuple(predicted), max(-1., min(1., progress)), confidence, count)
