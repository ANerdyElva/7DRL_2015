import random
import math
import pygame

from Util import TileTypes

class Map:
    def __init__( self, width, height, tiles, screen ):
        self.width = width
        self.height = height
        self.surface = None

        self.renderDirty = True
        self.atlas = tiles
        self.target = screen

    def I( self, x, y ):
        return x + y * self.width

    def get( self, x, y ):
        return self._buffer[ self.I( x, y ) ]
    def set( self, x, y, val ):
        self._buffer[ self.I( x, y ) ] = val
        self.renderDirty = True

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

    def preRender( self, camX, camY ):
        tileCount = (
                ( int( self.target.get_width() / self.atlas.tileSize[0] ) + 2 ),
                ( int( self.target.get_height() / self.atlas.tileSize[1] ) + 2 ) )

        if self.surface is None:
            self.surface = pygame.Surface( (
                 tileCount[0] * self.atlas.tileSize[0],
                 tileCount[1] * self.atlas.tileSize[1]
                 ) )

        self.surface.fill( ( 0, 0, 0 ) )

        for y in range( tileCount[1] ):
            _y = y * self.atlas.tileSize[1]

            if y + camY >= self.height:
                continue

            for x in range( tileCount[0] ):
                if x + camX >= self.width:
                    continue

                i = self.I( x + camX, y + camY )
                val = self._buffer[ i ]
                _x = x * self.atlas.tileSize[1]

                TileTypes[ val ].render( self.surface, _x, _y, x + camX, y + camY )

    def render( self, x, y ):
        renderX = int( x / self.atlas.tileSize[0] )
        renderY = int( y / self.atlas.tileSize[1] )
        if ( self.renderDirty or renderX != self.lastRenderX or renderY != self.lastRenderY ):
            print( 'Rendering.' )
            self.renderDirty = False
            self.lastRenderX = renderX
            self.lastRenderY = renderY

            self.preRender( renderX, renderY )

        rect = pygame.Rect( x % self.atlas.tileSize[0], y % self.atlas.tileSize[1], self.target.get_width(), self.target.get_height() )
        self.target.blit( self.surface.subsurface( rect ), ( 0, 0 ) )
