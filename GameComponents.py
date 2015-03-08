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
        self.frame = int( random.random() * 15 )

    def render( self, target, screenPos ):
        GameData.ExplosiveAtlas.render( self.frame, target, *screenPos )

        self.frame += 1
        if self.frame >= 74:
            self.entity.world.removeEntity( self.entity )
