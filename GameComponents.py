import ECS
import GameData
import random

class Explosive( ECS.Component ):
    def __init__( self, rayPerSquare, strength ):
        self.rayPerSquare = rayPerSquare
        self.strength = strength

    def __str__( self ):
        return '{Explosive, strength: %d}' % ( self.strength )

class ExplosionRenderer( ECS.Components.Renderer ):
    def __init__( self ):
        super().__init__( None, None )
        self.start = GameData.CurTime - random.random() * 150
        self.rate = random.random() * 0.2 + 0.9

    def render( self, target, screenPos ):
        frame = int( ( GameData.CurTime - self.start ) * self.rate / 10 )

        if frame >= 74:
            self.entity.world.removeEntity( self.entity )
            return

        GameData.ExplosiveAtlas.render( frame, target, *screenPos )
