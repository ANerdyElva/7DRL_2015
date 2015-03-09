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
import GameUtil
from GameState import GameState


class Game( GameState ):
    def __init__( self, screen, escapeFunc ):
        super().__init__( screen )

        self.escapeFunc = escapeFunc

        ###########################################################
        # Init the map
        ###########################################################
        GameData.Map = Map( GameData.TileCount[0], GameData.TileCount[1], GameData.MainAtlas, self.screen, self )
        GameData.Map.makeMap( initializeRandom, preIterInit, postInit )

        GameUtil.LoadEntities( self )

    def runFrame( self ):
        self.handleInput()

        if self.playerAction is not None:
            self.actionSystem.process( 500 )

        GameUtil.HandleExplosions( self, self.world.getEntityByComponent( ECS.Components.Position, GameComponents.Explosive ) )
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
        def getCamPos( x, y ):
            return ( min( max( int( x ) - int( self.screenTiles[0] / 2 ), 0 ), GameData.TileCount[0] - self.screenTiles[0] ),
                    min( max( int( y ) - int( self.screenTiles[1] / 2 ), 0 ), GameData.TileCount[1] - self.screenTiles[1] ) )
        if Cheats.Flying:
            self.camX, self.camY = getCamPos( GameData.CenterPos[0], GameData.CenterPos[1] )
        else:
            self.camX, self.camY = getCamPos( GameData.PlayerPosition.x, GameData.PlayerPosition.y )

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
                if event.key == pygame.K_F2 and Cheats.KeyboardCheats:
                    Cheats.ViewAll = not Cheats.ViewAll
                    GameData.Map.renderDirty = True
                elif event.key == pygame.K_F3 and Cheats.KeyboardCheats:
                    Cheats.Flying = not Cheats.Flying
                elif event.key == pygame.K_F4 and Cheats.KeyboardCheats:
                    inventory = GameData.Player.getComponent( GameComponents.Inventory )
                    print( inventory.addItem( GameData.TypeDefinitions['item']['item_stickygoo'], 10 ) )
                    print( inventory.addItem( GameData.TypeDefinitions['item']['item_explosive'], 10 ) )

                    for n in inventory.inventory:
                        print( n )
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
                    explosive.addComponent( GameComponents.TurnTaker( ai = lambda *_: GameComponents.Action( droppedEnt, 'explode', None ), timeTillNextTurn = 200 ) )
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
