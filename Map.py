import libtcodpy as tcod
import random
import math

from TileTypes import *

class Map:
    def __init__( self, width, height ):
        self.width = width
        self.height = height

    def I( self, x, y ):
        return x + y * self.width

    def get( self, x, y ):
        return self._buffer[ self.I( x, y ) ]

    def makeMap( self, getVal, preIterInit, postInit ):
        I = lambda x, y: x + y * self.width

        #_buffer = bytearray( [ ( 1 if random.random() > 0.5 else 0 ) for _ in range( self.width * self.height ) ] )
        halfHeight = int( self.height / 2 )
        halfWidth = int( self.width / 2 )
        _buffer = bytearray( [ getVal( x, y ) for y in range( -halfHeight, halfHeight ) for x in range( -halfWidth, halfWidth ) ])
        _backBuffer = bytearray( self.width * self.height )

        preIterInit( self, I, _buffer )

        for iterI in range( 2 ):
            offsets = (
                    I(-1,-1), I(-1,0), I(-1,1),
                    I(0,1),
                    I(1,1), I(1,0), I(1,-1),
                    I(0,-1) )

            for x in range( 1, self.width - 1 ):
                for y in range( 1, self.height - 1 ):
                    i = I( x, y )

                    count = (
                        _buffer[ i + offsets[0] ] +
                        _buffer[ i + offsets[1] ] +
                        _buffer[ i + offsets[2] ] +
                        _buffer[ i + offsets[3] ] +
                        _buffer[ i + offsets[4] ] +
                        _buffer[ i + offsets[5] ] +
                        _buffer[ i + offsets[6] ] +
                        _buffer[ i + offsets[7] ] )

                    ### Maze gen
                    #if count == 3:
                    #    _backBuffer[ i ] = 1
                    #elif count == 0 or count > 5:
                    #    _backBuffer[ i ] = 0
                    #else:
                    #    _backBuffer[ i ] = _buffer[ i ]

                    if count in ( 6, 7, 8 ):
                        _backBuffer[ i ] = 1
                    elif count in ( 1, 2, 3 ):
                        _backBuffer[ i ] = 0
                    else:
                        _backBuffer[ i ] = _buffer[ i ]


            preIterInit( self, I, _backBuffer )

            temp = _buffer
            _buffer = _backBuffer
            _backBuffer = temp

        postInit( self, I, _buffer )
        self._buffer = _buffer

    def render( self ):
        self.console = tcod.console_new( self.width, self.height )
        #tcod.console_set_background_color( self.console, tcod.transparent )

        tcod.console_set_custom_font(b'tiles.png', tcod.FONT_LAYOUT_ASCII_INROW, 16, 16 )
        tcod.console_map_ascii_codes_to_font( 0, 7, 0, 0 )
        tcod.console_map_ascii_codes_to_font( 8, 4, 0, 1 )
        tcod.console_map_ascii_codes_to_font( 16, 4, 7, 0 )

        for y in range( self.height ):
            for x in range( self.width ):
                i = self.I( x, y )
                val = self._buffer[ i ]
                
                if val == TILE_FIXED_WALL:
                    tcod.console_put_char( self.console, x, y, 8, tcod.BKGND_NONE )
                elif val == TILE_WALL:
                    tcod.console_put_char( self.console, x, y, 0, tcod.BKGND_NONE )
                else:
                    tcod.console_put_char( self.console, x, y, 16, tcod.BKGND_NONE )

        #tcod.console_set_custom_font(b'data/fonts/arial10x10.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)
