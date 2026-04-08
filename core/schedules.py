"""Agendas 1D com interpolação linear (empuxo vs tempo, arfagem vs tempo)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LinearSchedule1D:
    """Pontos (x, y) ordenados por x; avaliação com interpolação linear e extrapolação pelo último valor."""

    points: tuple[tuple[float, float], ...]

    def __post_init__(self) -> None:
        if len(self.points) < 2:
            raise ValueError("São necessários pelo menos dois pontos.")
        xs = [p[0] for p in self.points]
        if any(xs[i] >= xs[i + 1] for i in range(len(xs) - 1)):
            raise ValueError("Os pontos devem estar ordenados por x crescente.")

    def eval_at(self, x: float) -> float:
        x = float(x)
        pts = self.points
        if x <= pts[0][0]:
            return float(pts[0][1])
        if x >= pts[-1][0]:
            return float(pts[-1][1])
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]
            x1, y1 = pts[i + 1]
            if x0 <= x <= x1:
                if x1 == x0:
                    return float(y0)
                t = (x - x0) / (x1 - x0)
                return float(y0 + t * (y1 - y0))
        return float(pts[-1][1])


def thrust_flat() -> LinearSchedule1D:
    """Empuxo nominal constante (fração 1.0)."""
    return LinearSchedule1D(((0.0, 1.0), (1.0e9, 1.0)))


def pitch_vertical_only() -> LinearSchedule1D:
    """Arfagem nula: eixo do empuxo alinhado à vertical (+y)."""
    return LinearSchedule1D(((0.0, 0.0), (1.0e9, 0.0)))
