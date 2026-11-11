"""Detección de colisiones (círculo de golpe contra rectángulo de cuerpo)."""


def circle_rect(cx, cy, r, rect):
    nx = max(rect.left, min(cx, rect.right))
    ny = max(rect.top, min(cy, rect.bottom))
    dx, dy = cx - nx, cy - ny
    return dx * dx + dy * dy <= r * r


def hit_point(cx, cy, rect):
    """Punto de contacto aproximado para dibujar la chispa del impacto."""
    nx = max(rect.left, min(cx, rect.right))
    ny = max(rect.top, min(cy, rect.bottom))
    return (cx + nx) / 2, (cy + ny) / 2
