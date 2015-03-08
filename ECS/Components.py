import random

from Math2D import *

class Component():
    def _setEntity( self, ent ):
        self.entity = ent

    def __str__( self ):
        return '{%s 0x%X}' % ( type( self ).__name__, hash( self ) )

    def finalize( self ):
        pass

class Position( Component ):
    def __init__( self, x, y ):
        self.x = x
        self.y = y

    def moveTo( self, other ):
        self.x = other.x
        self.y = other.y

    def __str__( self ):
        return '{Position %d/%d}' % ( self.x, self.y )

class Renderer( Component ):
    def __init__( self, atlas, renderType ):
        self.atlas = atlas
        self.renderType = renderType

    def render( self, target, screenPos ):
        self.atlas.render( self.renderType, target, *screenPos )

    def __str__( self ):
        return '{%s %s:%s}' % ( type( self ).__name__, self.atlas, self.renderType )
