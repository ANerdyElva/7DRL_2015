import ECS
import GameData
import random

class Explosive( ECS.Component ):
    def __init__( self, rayPerSquare, strength ):
        self.rayPerSquare = rayPerSquare
        self.strength = strength
        self.isFiring = False

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

class Character( ECS.Component ):
    def __init__( self, baseType ):
        self.baseType = baseType
        self.attributes = {}

        for key in self.baseType:
            if key.startswith('base'):
                self.attributes[ key[6:] ] = self.baseType[key]
            self.attributes[ key ] = self.baseType[ key ]

        def _setEntity( self, ent ):
            super()._setEntity( ent )
            ent.passable = False

class CharacterRenderer( ECS.Components.Renderer ):
    def __init__( self, char ):
        super().__init__( char.baseType['spriteAtlas'], char.baseType['spriteId'] )

class Action():
    def __init__( self, entity, name, params ):
        self.entity = entity
        self.name = name
        self.params = params

    def __str__( self ):
        return '[%s@Ent.%d %s (%s)]' % ( type(self).__name__, self.entity.id, self.name, self.params )

class TurnTaker( ECS.Components.Component ):
    def __init__( self, ai = None, timeTillNextTurn = 0 ):
        self.ai = ai
        self.timeTillNextTurn = timeTillNextTurn
        self.wasBlocked = 0
        self.target = None

    def getNextTurn( self ):
        if self.ai is not None:
            ret = self.ai( self, self.entity, self.wasBlocked )
            return ret

    def finalize( self ):
        if self.entity.hasComponent( Character ):
            self.randomRange = self.entity.getComponent( Character ).baseType['randomRange']
        else:
            self.randomRange = 0

_directions = ( ( 1, 0 ), ( 0, 1 ), ( -1, 0 ), ( 0, -1 ) )
class TurnTakerAi():
    def __call__( self, turnComponent, ent, wasBlocked ):
        if turnComponent.target is None:
            return Action( ent, 'move', random.choice( _directions ) )

        pos = Point( ent.getComponent( Position ) )
        targetPos = Point( turnComponent.target.getComponent( Position ) )

        if ( targetPos - pos ).squaredLength < 8:
            return Action( ent, 'attack', turnComponent.target )
        elif ( targetPos - pos ).squaredLength < 120 ** 2:
            if wasBlocked > 2:
                return Action( ent, 'sleep', random.randrange( 50, 200 ) )
            elif wasBlocked > 0:
                return Action( ent, 'move', random.choice( _directions ) )
            else:
                path = ent.world._map.findPath( pos, targetPos )

                if path is not None and len( path ) > 1:
                    nextPoint = path[ -2 ]

                    _x = int(math.floor(pos.x))
                    _y = int(math.floor(pos.y)) 

                    move = ( nextPoint[0] - _x, nextPoint[1] - _y )
                    return Action( ent, 'move', move )

        return Action( ent, 'sleep', 400 )
