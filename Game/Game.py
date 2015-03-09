import pygame
import libtcodpy as tcod

from Util import *
from MapGen import *

from ActionSystem import ActionSystem
import Actions
import Characters
import Cheats
import ECS
import GameComponents
import GameData
from GameState import GameState


class Game( GameState ):
    def __init__( self, screen, escapeFunc ):
        super().__init__( screen )

        ###########################################################
        # Init the map
        ###########################################################
        GameData.Map = Map( GameData.TileCount[0], GameData.TileCount[1], GameData.MainAtlas, self.screen, self )
        GameData.Map.makeMap( initializeRandom, preIterInit, postInit )

        self.escapeFunc = escapeFunc
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

        for i in range( 5 ):
            choice = random.choice( Characters.SpawnList['normal'] )

            enemy = ECS.Entity()
            enemyChar = GameComponents.Character( choice )
            enemy.addComponent( ECS.Components.Position( int( random.random() * 10 - 5 + GameData.TileCount[0] / 2 ), int( random.random() * 10 - 5 + GameData.TileCount[1] / 2 ) ) )
            enemy.addComponent( enemyChar )
            enemy.addComponent( GameComponents.CharacterRenderer( enemyChar ) )
            enemy.addComponent( GameComponents.TurnTaker( ai = GameComponents.TurnTakerAi() ) )
            self.world.addEntity( enemy )

    def handleExplosions( self, explosionList ):
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


    def runFrame( self ):
        self.handleInput()

        if self.playerAction is not None:
            self.actionSystem.process( 500 )
        self.handleExplosions( self.world.getEntityByComponent( ECS.Components.Position, GameComponents.Explosive ) )
        self.world.process()

        self.updateCamPos()
        self.render()

    def render( self ):
        #Game drawing
        self.screen.fill( ( 0, 0, 0 ) )

        #Render map
        GameData.Map.render( self.camX * GameData.TileSize[0], self.camY * GameData.TileSize[1] )

        #Render entities
        for ent in self.world.getEntityByComponent( ECS.Components.Position, ECS.Components.Renderer ):
            pos = ent.getComponent( ECS.Components.Position )

            if GameData.Map.isVisible( pos.x, pos.y ):
                pos = ( ( pos.x - self.camX ) * GameData.TileSize[0], ( pos.y - self.camY ) * GameData.TileSize[1] )
                ent.getComponent( ECS.Components.Renderer ).render( self.screen, pos )

        #Render cursor
        GameData.MainAtlas.render( 'cursor', self.screen,
                ( self.mouseTilePos[0] - self.camX ) * GameData.TileSize[0],
                ( self.mouseTilePos[1] - self.camY ) * GameData.TileSize[1] )

        pygame.display.flip()

    def updateCamPos( self ):
        #Calculate camera position
        if Cheats.Flying:
            self.camX = min( max( GameData.CenterPos[0] - int( self.screenTiles[0] / 2 ), 0 ), GameData.TileCount[0] - self.screenTiles[0] )
            self.camY = min( max( GameData.CenterPos[1] - int( self.screenTiles[1] / 2 ), 0 ), GameData.TileCount[1] - self.screenTiles[1] )
        else:
            self.camX = min( max( GameData.PlayerPosition.x - int( self.screenTiles[0] / 2 ), 0 ), GameData.TileCount[0] - self.screenTiles[0] )
            self.camY = min( max( GameData.PlayerPosition.y - int( self.screenTiles[1] / 2 ), 0 ), GameData.TileCount[1] - self.screenTiles[1] )

    def handleInput( self ):
        self.updateCamPos()

        #Calculate mouse tile
        self.mousePos = pygame.mouse.get_pos()
        self.mouseTilePos = (
                int( ( self.camX * GameData.TileSize[0] + self.mousePos[0] ) / GameData.TileSize[0] ),
                int( ( self.camY * GameData.TileSize[1] + self.mousePos[1] ) / GameData.TileSize[1] ) )

        #Game logic
        for event in pygame.event.get():
            if self.handle( event ):
                pass
            elif event.type == pygame.MOUSEBUTTONUP:
                explosive = ECS.Entity()
                explosive.addComponent( ECS.Components.Position( *self.mouseTilePos ) )
                explosive.addComponent( GameComponents.Explosive( 32, 6.25 ) )
                explosive.addComponent( ECS.Components.Renderer( GameData.Entities, 'tnt' ) )
                self.world.addEntity( explosive )
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F2:
                    Cheats.ViewAll = not Cheats.ViewAll
                    GameData.Map.renderDirty = True
                elif event.key == pygame.K_F3:
                    Cheats.Flying = not Cheats.Flying
                elif event.key == pygame.K_w:
                    self.playerAction = GameComponents.Action( GameData.Player, 'move', ( 0, -1 ) )
                elif event.key == pygame.K_s:
                    self.playerAction = GameComponents.Action( GameData.Player, 'move', ( 0, 1 ) )
                elif event.key == pygame.K_a:
                    self.playerAction = GameComponents.Action( GameData.Player, 'move', ( -1, 0 ) )
                elif event.key == pygame.K_d:
                    self.playerAction = GameComponents.Action( GameData.Player, 'move', ( 1, 0 ) )
                elif event.key == pygame.K_1:
                    explosive = ECS.Entity()
                    explosive.addComponent( GameComponents.Explosive( 32, 6.25 ) )
                    explosive.addComponent( ECS.Components.Renderer( GameData.Entities, 'tnt' ) )
                    self.playerAction = GameComponents.Action( GameData.Player, 'dropEntity', explosive )

        if Cheats.Flying:
            curKeys = pygame.key.get_pressed()
            if curKeys[pygame.K_w]:
                GameData.CenterPos[1] -= 1
            if curKeys[pygame.K_s]:
                GameData.CenterPos[1] += 1
            if curKeys[pygame.K_a]:
                GameData.CenterPos[0] -= 1
            if curKeys[pygame.K_d]:
                GameData.CenterPos[0] += 1

    def quit( self, event ):
        if self.escapeFunc( event ):
            self.IsRunning = False


    def updateFov( self, tcodMap ):
        if GameData.Player is None:
            tcod.map_compute_fov( tcodMap, int( GameData.CenterPos[0] ), int( GameData.CenterPos[1] ), 50, True, algo = tcod.FOV_BASIC )
        else:
            pos = GameData.Player.getComponent( ECS.Components.Position )
            tcod.map_compute_fov( tcodMap, pos.x, pos.y, 50, True, tcod.FOV_BASIC )
