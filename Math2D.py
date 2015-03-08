import math

class Point():
    def __init__( self, *args ):
        if len( args ) == 1:
            self.x = args[0].x
            self.y = args[0].y
        else:
            self.x = args[0]
            self.y = args[1]

    def __add__( p1, p2 ):
        return Point( p1.x + p2.x, p1.y + p2.y )

    def __sub__( p1, p2 ):
        return Point( p1.x - p2.x, p1.y - p2.y )

    def __truediv__( p1, p2 ):
        if type( p2 ) == Point:
            return Point( p1.x / p2.x, p1.y / p2.y )
        else:
            return Point( p1.x / p2, p1.y / p2 )
    def __mul__( p1, p2 ):
        if type( p2 ) == Point:
            return Point( p1.x * p2.x, p1.y * p2.y )
        else:
            return Point( p1.x * p2, p1.y * p2 )

    def inv( self ):
        x = 1 / self.x if self.x != 0 else 0
        y = 1 / self.y if self.y != 0 else 0

        return Point( x, y )

    def __str__( self ):
        return '[%s/%s]' % ( self.x, self.y )

    def afterComma( self ):
        return Point( self.x - int( self.x ), self.y - int( self.y ) )

    def int( self ):
        return Point( int( self.x ), int( self.y ) )
    def floor( self ):
        return Point( math.floor( self.x ), math.floor( self.y ) )

    def copysign( self, val ):
        return Point( math.copysign( val, self.x ), math.copysign( val, self.y ) )

    def normalized( self ):
        l = self.length
        if l != 0:
            l = 1.0 / l

        return Point( self.x * l, self.y * l )

    @property
    def squaredLength( self ):
        return self.x ** 2 + self.y ** 2
    @property
    def length( self ):
        return math.sqrt( self.squaredLength )

def traceGrid( x0, y0, x1, y1 ):
    x0 = int( x0 )
    y0 = int( y0 )
    x1 = int( x1 )
    y1 = int( y1 )

    dx = abs(x1 - x0);
    dy = abs(y1 - y0);
    x = x0;
    y = y0;
    n = 1 + dx + dy;
    x_inc = 1 if (x1 > x0) else -1
    y_inc = 1 if (y1 > y0) else -1
    error = dx - dy;
    dx *= 2;
    dy *= 2;

    while n > 0:
        if (error > 0):
            x += x_inc;
            error -= dy;
        else:
            y += y_inc;
            error += dx;

        n -= 1

        if n > 0:
            yield x, y, error > 0


class Rect():
    def __init__( self, *args ):
        if len( args ) == 2:
            _min = args[0]
            _max = args[1]
            self.p1 = Point( min( _min.x, _max.x ), min( _min.y, _max.y ) )
            self.p2 = Point( max( _min.x, _max.x ), max( _min.y, _max.y ) )
        elif len( args ) == 4:
            self.p1 = Point( min( args[0], args[2] ), min( args[1], args[3] ) )
            self.p2 = Point( max( args[0], args[2] ), max( args[1], args[3] ) )
        else:
            raise ValueError( 'Rect expects 2 or 4 arguments, received: ' + str( args ) )

    def __str__( self ):
        return '[Rect: %s; %s]' % ( self.p1, self.p2 )

    @property
    def width( self ):
        return self.p2.x - self.p1.x
    @property
    def height( self ):
        return self.p2.y - self.p1.y
    @property
    def dim( self ):
        return self.p2 - self.p1

    @property
    def center( self ):
        return ( self.p1 * 0.5 ) + ( self.p2 * 0.5 )

    def intersects( a, b ):
        return ( a.p1.x < b.p2.x and a.p2.x > b.p1.x and
                a.p1.y < b.p2.y and a.p2.y > b.p1.y )

    def findOverLap( self, other ):
        def _findOverLap( m1_min, m1_max, m2_min, m2_max ):
            if m1_max < m2_min or m2_max < m1_min:
                return None

            return max( m1_min, m2_min ), min( m1_max, m2_max )


        x = _findOverLap( self.p1.x, self.p2.x, other.p1.x, other.p2.x )
        if x is not None:
            #print( self, other )
            if self.p2.y < other.p1.y:
                return 'X', x, ( self.p2.y, other.p1.y )
            else:
                return 'X', x, ( other.p2.y, self.p1.y )

        y = _findOverLap( self.p1.y, self.p2.y, other.p1.y, other.p2.y )
        if y is not None:
            #print( self, other )
            if self.p2.x < other.p1.x:
                return 'Y', y, ( self.p2.x, other.p1.x )
            else:
                return 'Y', y, ( other.p2.x, self.p1.x )

    @property
    def size( self ):
        dim = self.dim
        return dim.x * dim.y

def IntPoint( *args ):
    if len( args ) == 1:
        return Point( int( args[0].x ), int( args[0].y ) )
    elif len( args ) == 2:
        return Point( int( args[0] ), int( args[1] ) )
    else:
        raise ValueError( 'IntPoint expects 1 or 2 arguments.' )

def IntRect( *args ):
    if len( args ) == 1:
        return Rect( IntPoint( args[0].p1 ), IntPoint( args[0].p2 ) )
    elif len( args ) == 2:
        return Rect( IntPoint( args[0] ), IntPoint( args[1] ) )
    elif len( args ) == 4:
        return Rect( int( args[ 0 ] ), int( args[ 1 ] ), int( args[ 2 ] ), int( args[ 3 ] ) )
    else:
        raise ValueError( 'IntRect expects 1, 2 or 4 arguments, received: ' + str( args ) )


def PointFromAngle( angle, dist ):
    return Point( math.sin( angle ) * dist, math.cos( angle ) * dist )
