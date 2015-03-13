def StarCallback( fun ):
    def cb( x, y ):
        fun( x, y )
        fun( x - 1, y )
        fun( x + 1, y )
        fun( x, y - 1 )
        fun( x, y + 1 )

    return cb

def Line(x0, y0, x1, y1, cb):
    "Bresenham's line algorithm"
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    sx = -1 if x0 > x1 else 1
    sy = -1 if y0 > y1 else 1

    if dx > dy:
        err = dx / 2.0
        while x != x1:
            if cb(x, y) == True:
                return
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != y1:
            if cb(x, y) == True:
                return

            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
    if cb(x, y) == True:
        return


def LineIter( x0, y0, x1, y1 ):
    pixels = []
    Line( x0, y0, x1, y1, lambda x, y: pixels.append( ( x, y ) ) )

    for p in pixels:
        yield p
