import math
import random

from Util.TileTypes import *
from Util import Line, StarCallback

centerRoomSize = ( 5, 5 )

def initializeRandom( x, y ):
    dist = math.sqrt( x ** 2 + y ** 2 )
    angle = math.atan2( x, y ) / math.pi * 5
    rand = ( random.random() * 7 ) - 3.5

    val = ( ( dist + angle + rand ) % 10 )
    if val > 5:
        return 1
    else:
        return 0

def circle(x0, y0, radius, endRadius, cb):
    stepSize = 1.0 / endRadius

    angle = math.pi / 2
    while angle >= 0:
        c = math.cos( angle )
        s = math.sin( angle )

        r = radius
        while r < endRadius:
            cb( int( c * r ) + x0, int( s * r ) + y0 )
            cb( int( s * r ) + x0, int( c * r ) + y0 )
            cb(-int( c * r ) + x0, int( s * r ) + y0 )
            cb(-int( s * r ) + x0, int( c * r ) + y0 )
            cb( int( c * r ) + x0,-int( s * r ) + y0 )
            cb( int( s * r ) + x0,-int( c * r ) + y0 )
            cb(-int( c * r ) + x0,-int( s * r ) + y0 )
            cb(-int( s * r ) + x0,-int( c * r ) + y0 )

            r += 0.5

        angle -= stepSize


def buildFixedWalls( self, I, _buffer, val ):
    #Clear center room
    centerX = int( self.width / 2 )
    centerY = int( self.height / 2 )

    for x in range( centerX - centerRoomSize[0] - 1, centerX + centerRoomSize[0] + 1 ):
        for y in range( centerY - centerRoomSize[1] - 1, centerY + centerRoomSize[1] + 1 ):
            _buffer[ I( x, y ) ] = 0

    #Build center room walls
    for x in range( centerX - centerRoomSize[0] - 1, centerX + centerRoomSize[0] + 1 ):
        _buffer[ I( x, centerY - centerRoomSize[1] - 1 ) ] = val
        _buffer[ I( x, centerY + centerRoomSize[1] ) ] = val
    for y in range( centerY - centerRoomSize[1] - 1, centerY + centerRoomSize[1] + 1 ):
        _buffer[ I( centerX - centerRoomSize[0] - 1, y ) ] = val
        _buffer[ I( centerX + centerRoomSize[0], y ) ] = val

def preIterInit( self, I, _buffer ):
    #Outer wall
    for x in range( self.width ):
        _buffer[ I( x, 0 ) ] = 1
        _buffer[ I( x, self.height - 1 ) ] = 1
    for y in range( self.height ):
        _buffer[ I( 0, y ) ] = 1
        _buffer[ I( self.width - 1, y ) ] = 1

    #Area around outer wall
    for x in range( 1, self.width- 1  ):
        _buffer[ I( x, 1 ) ] = 0
        _buffer[ I( x, self.height - 2 ) ] = 0
    for y in range( 1, self.height - 1 ):
        _buffer[ I( 1, y ) ] = 0
        _buffer[ I( self.width - 2, y ) ] = 0

    buildFixedWalls( self, I, _buffer, 1 )


def postInit( self, I, _buffer ):
    centerX = int( self.width / 2 )
    centerY = int( self.height / 2 )

    for x in range( self.width ):
        for y in range( self.height ):
            i = I( x, y )
            val = _buffer[ i ]

            if val == 0:
                _buffer[ i ] = TILE_AIR #NOOP, but for clarity
            elif val == 1:
                _buffer[ i ] = TILE_WALL
            else:
                raise Exception( "Incorrect tile type in postInit!" )

    for x in range( self.width ):
        _buffer[ I( x, 0 ) ] = TILE_FIXED_WALL
        _buffer[ I( x, self.height - 1 ) ] = TILE_FIXED_WALL
    for y in range( self.height ):
        _buffer[ I( 0, y ) ] = TILE_FIXED_WALL
        _buffer[ I( self.width - 1, y ) ] = TILE_FIXED_WALL

    buildFixedWalls( self, I, _buffer, TILE_FIXED_WALL )

    curSurface = ( centerRoomSize[0] * 2 ) * ( centerRoomSize[1] * 2 )

    sectionSurface = 50 * 50
    curRadius = -1

    def setFixedWall( x, y ):
        _buffer[ I( int( x ), int( y ) ) ] = TILE_FIXED_WALL

    circleNum = 0
    while curRadius < 200:
        sectionCount = max( circleNum * 4, 1 )
        nextSurface = curSurface + ( sectionSurface * sectionCount )

        nextRadius = int( math.sqrt( nextSurface / math.pi ) )
        circle( centerX, centerY, nextRadius, nextRadius + 2, setFixedWall )

        #Seperate sections in circle
        if sectionCount > 1:
            for i in range( sectionCount ):
                angle = i * math.pi * 2 / sectionCount
                s = math.sin( angle )
                c = math.cos( angle )

                Line( int( s * ( curRadius + 1 ) ) + centerX, int( c * ( curRadius + 1 ) ) + centerY, int( s * nextRadius ) + centerX, int( c * nextRadius ) + centerY, StarCallback( setFixedWall ) )


        curRadius = nextRadius
        curSurface = int( curRadius ** 2 * math.pi )
        circleNum += 1
