import math
import random

from TileTypes import *

def initializeRandom( x, y ):
    dist = math.sqrt( x ** 2 + y ** 2 )
    angle = math.atan2( x, y ) / math.pi * 5
    rand = ( random.random() * 7 ) - 3.5

    val = ( ( dist + angle + rand ) % 10 )
    if val > 5:
        return 1
    else:
        return 0

def preIterInit( self, I, _buffer ):
    for x in range( self.width ):
        _buffer[ I( x, 0 ) ] = 1
        _buffer[ I( x, self.height - 1 ) ] = 1
    for y in range( self.height ):
        _buffer[ I( 0, y ) ] = 1
        _buffer[ I( self.width - 1, y ) ] = 1

    for x in range( 1, self.width- 1  ):
        _buffer[ I( x, 1 ) ] = 0
        _buffer[ I( x, self.height - 2 ) ] = 0
    for y in range( 1, self.height - 1 ):
        _buffer[ I( 1, y ) ] = 0
        _buffer[ I( self.width - 2, y ) ] = 0

def postInit( self, I, _buffer ):
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

    #Clear center room
    centerX = int( self.width / 2 )
    centerY = int( self.height / 2 )

    centerRoomSize = ( 5, 5 )
    for x in range( centerX - centerRoomSize[0] - 1, centerX + centerRoomSize[0] + 1 ):
        for y in range( centerY - centerRoomSize[1] - 1, centerY + centerRoomSize[1] + 1 ):
            _buffer[ I( x, y ) ] = TILE_AIR

    #Build center room walls
    for x in range( centerX - centerRoomSize[0] - 1, centerX + centerRoomSize[0] + 1 ):
        _buffer[ I( x, centerY - centerRoomSize[1] - 1 ) ] = TILE_FIXED_WALL
        _buffer[ I( x, centerY + centerRoomSize[1] ) ] = TILE_FIXED_WALL
    for y in range( centerY - centerRoomSize[1] - 1, centerY + centerRoomSize[1] + 1 ):
        _buffer[ I( centerX - centerRoomSize[0] - 1, y ) ] = TILE_FIXED_WALL
        _buffer[ I( centerX + centerRoomSize[0], y ) ] = TILE_FIXED_WALL
