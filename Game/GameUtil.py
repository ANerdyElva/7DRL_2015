import random
import math

from Util import *

import ECS
import GameComponents
import GameData
from ActionSystem import ActionSystem
import Actions
import Characters
import GameUtil

def LoadEntities( self ):
    self.world = ECS.World()
    self.actionSystem = ActionSystem( self.world, Actions.ActionMap )
    self.world.addSystem( self.actionSystem )

    self.playerAction = None
    def playerAction( __, _, wasBlocked ):
        ret = self.playerAction
        self.playerAction = None
        return ret

    GameData.Player = ECS.Entity()
    GameData.Player.addComponent( ECS.Components.Position( int( GameData.CenterPos[ 0 ] ), int( GameData.CenterPos[1] ) ) )
    GameData.Player.addComponent( GameComponents.Character( Characters.Player ) )
    GameData.Player.addComponent( GameComponents.CharacterRenderer( GameData.Player.getComponent( GameComponents.Character ) ) )
    GameData.Player.addComponent( GameComponents.TurnTaker( playerAction ) )


    GameData.PlayerPosition = GameData.Player.getComponent( ECS.Components.Position )
    self.world.addEntity( GameData.Player )

def HandleExplosions( self, explosionList ):
    hitTiles = {}

    for ent in explosionList:
        explosive = ent.getComponent( GameComponents.Explosive )
        if not explosive.isFiring:
            continue

        pos = ent.getComponent( ECS.Components.Position )
        pos = ( pos.x, pos.y )

        def handleRay( targetX, targetY ):
            curStrength = explosive.strength

            def handleBlock( x, y ):
                nonlocal curStrength
                if curStrength <= 0:
                    return True

                curStrength -= 1

                curToughness = TileTypes[ GameData.Map.get( x, y ) ].hardness
                if curToughness is None: #Unbreakable block
                    return True

                if ( x, y ) in hitTiles:
                    curToughness = hitTiles[ ( x, y ) ]
                else:
                    hitTiles[ ( x, y ) ] = curToughness

                if curStrength > curToughness:
                    hitTiles[ ( x, y ) ] = 0
                    curStrength -= curToughness
                else:
                    hitTiles[ ( x, y ) ] = curToughness - curStrength

            Line( pos[0], pos[1], int( pos[0] + targetX ), int( pos[1] + targetY ), handleBlock )

        for i in range( explosive.rayPerSquare ):
            s = math.sin( i * math.pi / 2 / explosive.rayPerSquare )
            c = math.cos( i * math.pi / 2 / explosive.rayPerSquare )

            handleRay( s * 200 + 20 * random.random() - 10, c * 200 + 20 * random.random() - 10 )
            handleRay( -s * 200 + 20 * random.random() - 10, c * 200 + 20 * random.random() - 10 )
            handleRay( s * 200 + 20 * random.random() - 10, -c * 200 + 20 * random.random() - 10 )
            handleRay( -s * 200 + 20 * random.random() - 10, -c * 200 + 20 * random.random() - 10 )

        self.world.removeEntity( ent )

    if len( hitTiles ) > 0:
        for tilePos in hitTiles:
            if hitTiles[ tilePos ] == 0:
                tileType = TileTypes[ GameData.Map.get( tilePos[0], tilePos[1] ) ]
                targetType = TILE_AIR

                if hasattr( tileType, 'onDestruction' ):
                    targetType = tileType.onDestruction( *tilePos )

                GameData.Map.set( tilePos[0], tilePos[1], targetType )

                effect = ECS.Entity()
                effect.addComponent( ECS.Components.Position( *tilePos ) )
                effect.addComponent( GameComponents.ExplosionRenderer() )
                self.world.addEntity( effect )


