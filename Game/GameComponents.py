import ECS
import GameData
import random
from Util.TileTypes import *
import pygame
import Math2D
import math
import GameUtil

class Explosive( ECS.Component ):
    def __init__( self, rayPerSquare, strength ):
        self.rayPerSquare = rayPerSquare
        self.strength = strength
        self.isFiring = False

    def onFire( self ):
        self.entity.world.removeEntity( self.entity )

    def hitEntity( self, otherEnt ):
        pass

    def __str__( self ):
        return '{Explosive, strength: %d}' % ( self.strength )

    def doFire( self ):
        self.isFiring = True
        return 1000

class BombRenderer( ECS.Components.Renderer ):
    def __init__( self, definition ):
        img = GameData.TypeDefinitions[ 'image' ][ definition.image ]
        super().__init__( GameData.AtlasMap[ img.file ], img.key )

    def _setEntity( self, ent ):
        super()._setEntity( ent )

        self.ai = ent.getComponent( TurnTaker ).ai
        ent.bombAge = 0


    def render( self, target, screenPos ):
        fillPart = self.entity.bombAge / self.ai.explodeDelay

        target.fill( ( 255, 255, 0 ), pygame.Rect( screenPos[0], screenPos[1] - 2, GameData.TileSize[0], 5 ) )
        target.fill( ( 248, 202, 0 ), pygame.Rect( screenPos[0], screenPos[1] - 2, ( GameData.TileSize[0] * fillPart ), 5 ) )
        super().render( target, screenPos )

class SpecialExplosive( Explosive ):
    def __init__( self ):
        super().__init__( 64, 30 )

    def onFire( self ):
        self.entity.world.removeEntity( self.entity )

        _map = GameData.Map
        self.pos = self.entity.getComponent( ECS.Components.Position )

        for x in range( -4, 5 ):
            for y in range( -4, 5 ):
                if ( x ** 2 + y ** 2 ) < 4 ** 2:
                    _map.set( self.pos.x + x, self.pos.y + y, TILE_AIR )

    def doFire( self ):
        _map = GameData.Map
        self.pos = self.entity.getComponent( ECS.Components.Position )

        # Check cardinal directions to fire
        if (_map.get( self.pos.x - 1, self.pos.y ) == TILE_FIXED_WALL or
            _map.get( self.pos.x + 1, self.pos.y ) == TILE_FIXED_WALL or
            _map.get( self.pos.x, self.pos.y - 1 ) == TILE_FIXED_WALL or
            _map.get( self.pos.x, self.pos.y + 1 ) == TILE_FIXED_WALL ):
                self.isFiring = True
        return 1000




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
    def __init__( self, definition ):
        self.definition = definition
        self.attributes = {}
        self.onRemove = None

        data = self.definition.getData()
        for key in data:
            if key.startswith('base'):
                self.attributes[ key[4:] ] = data[key]
            self.attributes[ key ] = data[ key ]

    def _setEntity( self, ent ):
        super()._setEntity( ent )
        ent.passable = False
        ent.isPlayer = False

        if self.definition.has( 'damageRange' ):
            ent.attackDistance = self.definition.damageRange ** 2

    def takeDamage( self, count ):
        self.attributes[ 'Health' ] -= count
        if self.attributes[ 'Health' ] < 0:
            self.entity.world.removeEntity( self.entity )

            if self.onRemove is not None:
                self.onRemove( self )

            if self.definition.has( 'drops' ):
                for n in self.definition.drops:
                    dropped = GameUtil.CreateEntity( n )
                    pos = self.entity.getComponent( ECS.Components.Position )
                    dropped.addComponent( ECS.Components.Position( pos.x, pos.y ) )
                    self.entity.world.addEntity( dropped )


class Item( ECS.Component ):
    def __init__( self, definition ):
        if isinstance( definition, str ):
            self.definition = GameData.TypeDefinitions[''][ definition ]
        else:
            self.definition = definition
        self.count = 1

class Inventory( ECS.Component ):
    def __init__( self, inventorySize ):
        self.inventorySize = inventorySize
        self.inventory = {}
        self.isDirty = True
        self.updateCallback = lambda: None

    def addItem( self, item, count ):
        self.isDirty = True
        for n in self.inventory:
            itemStack = self.inventory[n]
            if itemStack[0] == item:
                if itemStack[1] + count <= item.maxStackSize:
                    itemStack[1] += count
                    count = 0
                else:
                    count -= item.maxStackSize - itemStack[1]
                    itemStack[1] = item.maxStackSize

        def firstEmpty():
            for i in range( self.inventorySize ):
                if i not in self.inventory:
                    return i
            else:
                return -1

        while count > 0:
            slot = firstEmpty()
            if slot == -1:
                self.updateCallback()
                return count

            if count <= item.maxStackSize:
                self.inventory[slot] = [ item, count ]
                count = 0
            else:
                count -= item.maxStackSize
                self.inventory[slot] = [ item, item.maxStackSize ]

        self.updateCallback()
        return 0

    def dropItem( self, slot, count ):
        self.isDirty = True

        if slot in self.inventory:
            if self.inventory[slot][1] > count:
                self.inventory[slot][1] -= count
                self.updateCallback()
                return count
            else:
                ret = self.inventory[slot][1]
                del self.inventory[slot]
                self.updateCallback()
                return ret
        else:
            self.updateCallback()
            return 0

class CharacterRenderer( ECS.Components.Renderer ):
    def __init__( self, definition ):
        img = GameData.TypeDefinitions[ 'image' ][ definition.image ]
        super().__init__( GameData.AtlasMap[ img.file ], img.key )

    def _setEntity( self, ent ):
        super()._setEntity( ent )
        self.character = ent.getComponent( Character )

    def render( self, target, screenPos ):
        fillPart = self.character.attributes[ 'Health' ] / self.character.attributes[ 'baseHealth' ]

        target.fill( ( 137, 22, 35 ), pygame.Rect( screenPos[0], screenPos[1] - 2, GameData.TileSize[0], 5 ) )
        target.fill( ( 250, 42, 0 ), pygame.Rect( screenPos[0], screenPos[1] - 2, ( GameData.TileSize[0] * fillPart ), 5 ) )

        super().render( target, screenPos )

class Action():
    def __init__( self, entity, name, params ):
        self.entity = entity
        self.name = name
        self.params = params

    def __str__( self ):
        return '[%s@Ent.%d %s (%s)]' % ( type(self).__name__, self.entity.id, self.name, self.params )

class StickyBomb( ECS.Components.Component ):
    def __init__( self, distance ):
        self.maxDistanceSquared = distance ** 2

    def bombThink( self, ent, curTurn, age ):
        myPos = ent.getComponent( ECS.Components.Position )

        closest = None
        closestDist = self.maxDistanceSquared

        for otherEnt in ent.world.getEntityByComponent( Character, ECS.Components.Position ):
            if otherEnt.isPlayer:
                continue

            pos = otherEnt.getComponent( ECS.Components.Position )

            distanceSquared = ( pos.x - myPos.x ) ** 2 + ( pos.y - myPos.y ) ** 2
            if distanceSquared < closestDist:
                closest = pos
                closestDist = distanceSquared

        if closest is not None:
            myPos.x = closest.x
            myPos.y = closest.y

            return None


class ProximityBomb( ECS.Components.Component ):
    def __init__( self, radius ):
        self.radius = radius
        self.radiusSquared = radius ** 2

    def bombThink( self, ent, curTurn, age ):
        if age < 50:
            return None

        myPos = ent.getComponent( ECS.Components.Position )

        for otherEnt in ent.world.getEntityByComponent( Character, ECS.Components.Position ):
            if otherEnt.isPlayer:
                continue

            pos = otherEnt.getComponent( ECS.Components.Position )

            distanceSquared = ( pos.x - myPos.x ) ** 2 + ( pos.y - myPos.y ) ** 2
            if distanceSquared < self.radiusSquared:
                return Action( ent, 'explode', None )

class TurnTaker( ECS.Components.Component ):
    def __init__( self, ai = None, timeTillNextTurn = 0 ):
        self.ai = ai
        self.timeTillNextTurn = timeTillNextTurn
        self.wasBlocked = 0
        self.target = None

    def getNextTurn( self, curTurn ):
        if self.ai is not None:
            ret = self.ai( self, self.entity, self.wasBlocked, curTurn )
            return ret

    def finalize( self ):
        if self.entity.hasComponent( Character ):
            self.randomRange = self.entity.getComponent( Character ).definition.randomRange
        else:
            self.randomRange = 0


class BombAi():
    def __init__( self, explodeDelay ):
        self.explodeDelay = explodeDelay

    def __call__( self, turnComponent, ent, wasBlocked, curTurn ):
        bombAge = curTurn - ent.firstTurn
        ent.bombAge = bombAge

        if bombAge > self.explodeDelay:
            return Action( ent, 'explode', None )
        else:
            for comp in ent.componentList:
                if hasattr( comp, 'bombThink' ):
                    ret = comp.bombThink( ent, curTurn, bombAge )
                    if ret is not None:
                        return ret
        return Action( ent, 'sleep', 20 )


_directions = ( ( 1, 0 ), ( 0, 1 ), ( -1, 0 ), ( 0, -1 ) )
class TurnTakerAi():
    def __call__( self, turnComponent, ent, wasBlocked, curTurn ):
        if turnComponent.target is None:
            if random.random() < 0.2:
                return Action( ent, 'findEnemy', turnComponent )
            return Action( ent, 'move', random.choice( _directions ) )

        pos = Math2D.Point( ent.getComponent( ECS.Components.Position ) )
        targetPos = Math2D.Point( turnComponent.target.getComponent( ECS.Components.Position ) )

        if ( targetPos - pos ).squaredLength < ent.attackDistance:
            return Action( ent, 'attack', turnComponent.target )
        elif ( targetPos - pos ).squaredLength < 20 ** 2:
            if wasBlocked > 2:
                return Action( ent, 'sleep', random.randrange( 50, 200 ) )
            elif wasBlocked > 0:
                return Action( ent, 'move', random.choice( _directions ) )
            else:
                path = GameData.Map.findPath( pos, targetPos )

                if path is not None and len( path ) > 1:
                    nextPoint = path[ -2 ]

                    _x = int(math.floor(pos.x))
                    _y = int(math.floor(pos.y))

                    move = ( nextPoint[0] - _x, nextPoint[1] - _y )
                    return Action( ent, 'move', move )
                else:
                    turnComponent.target = None

        return Action( ent, 'sleep', random.randrange( 400, 600 ) )
