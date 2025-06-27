def check_collision(x1, y1, x2, y2):
    return (
        x1 < x2 + 8 and
        x1 + 8 > x2 and
        y1 < y2 + 8 and
        y1 + 8 > y2
    )
