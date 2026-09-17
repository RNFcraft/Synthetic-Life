"""Pure signature transforms used by spatial-memory matching."""


def rotate_signature(signature: tuple, quarter_turns: int) -> tuple:
    rotated = []
    for x, y, channel, value in signature:
        for _ in range(quarter_turns % 4):
            x, y = -y, x
        rotated.append((x, y, channel, value))
    return tuple(sorted(rotated))


def weighted_similarity(a: tuple, b: tuple, weights=None) -> float:
    left, right = set(a), set(b)
    union = left | right
    if not union:
        return 1.0
    table = weights or {}
    return sum(table.get(item, 1.0) for item in left & right) / max(
        1e-9, sum(table.get(item, 1.0) for item in union)
    )


__all__ = ["rotate_signature", "weighted_similarity"]
