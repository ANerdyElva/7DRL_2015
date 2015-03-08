import pygame
import libtcodpy as tcod

from Util import *
from MapGen import *

import GameData
import Cheats
import GameComponents
from GameState import GameState

import ECS

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

    def runFrame( self ):
        self.handleInput()

        self.world.process()

        hitTiles = {}
        for ent in self.world.getEntityByComponent( ECS.Components.Position, GameComponents.Explosive ):
            pos = ent.getComponent( ECS.Components.Position )
            pos = ( pos.x, pos.y )

            explosive = ent.getComponent( GameComponents.Explosive )

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

        self.render()

    def render( self ):
        #Game drawing
        self.screen.fill( ( 255, 255, 255 ) )

        #Render map
        GameData.Map.render( self.camX * GameData.TileSize[0], self.camY * GameData.TileSize[1] )

        #Render entities
        for ent in self.world.getEntityByComponent( ECS.Components.Position, ECS.Components.Renderer ):
            pos = ent.getComponent( ECS.Components.Position )
            pos = ( ( pos.x - self.camX ) * GameData.TileSize[0], ( pos.y - self.camY ) * GameData.TileSize[1] )
            ent.getComponent( ECS.Components.Renderer ).render( self.screen, pos )

        #Render cursor
        GameData.MainAtlas.render( 'cursor', self.screen,
                ( self.mouseTilePos[0] - self.camX ) * GameData.TileSize[0],
                ( self.mouseTilePos[1] - self.camY ) * GameData.TileSize[1] )

        pygame.display.flip()


    def handleInput( self ):
        #Calculate camera position
        self.camX = min( max( GameData.CenterPos[0] - int( self.screenTiles[0] / 2 ), 0 ), GameData.TileCount[0] - self.screenTiles[0] )
        self.camY = min( max( GameData.CenterPos[1] - int( self.screenTiles[1] / 2 ), 0 ), GameData.TileCount[1] - self.screenTiles[1] )

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
