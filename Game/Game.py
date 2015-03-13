import pygame
import libtcodpy as tcod

from Util import *
from MapGen import *

from ActionSystem import ActionSystem
import Actions
import Cheats
import ECS
import GameComponents
import GameData
import GameUtil
import Window
from GameState import GameState


class Game( GameState ):
    def __init__( self, screen, escapeFunc ):
        super().__init__( screen )

        self.escapeFunc = escapeFunc
        self.hotbar = Window.Hotbar( 8 )
        def updateInventory( slot ):
            self.inventorySlot = slot
            GameUtil.UpdateInventory( self )

        self.hotbar.slotCallback = updateInventory
        self.guiParts.append( self.hotbar )
        self.inventorySlot = 0

        self.actionWindow = Window.Window( 300, 200, 0, self.screen.get_height() - 200 )
        self.guiParts.append( self.actionWindow )
        self.actionWindow.guiParts.append( Window.Button(
            LoadFont( 'ButtonFont', 'data/framd.ttf', 10 ),
            'Combine', ( 20 , 30 ), ( 260, 25 ) ) )

        self.pickupWindow = Window.Window( 300, 200, self.screen.get_width() - 300, self.screen.get_height() - 200 )

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

        itemsAtCurPos = [ n for n in [ n.getComponent( GameComponents.Item ) for n in self.world.getEntitiesAtPos( GameData.PlayerPosition ) ] if n is not None ]
        if len( itemsAtCurPos ) > 0:
            if self.pickupWindow not in self.guiParts:
                self.guiParts.append( self.pickupWindow )

            count = 1

            def addButton( text, cb ):
                nonlocal count
                button = Window.Button( LoadFont( 'ButtonFont', '', '' ), text, ( 20, 30 * count ), ( 260, 25 ) )
                button.pressCallback = cb
                self.pickupWindow.guiParts.append( button )

                count += 1

            def pickup( item ):
                remaining = GameData.PlayerInventory.addItem( item.definition, item.count )
                if remaining > 0:
                    item.count -= remaining
                else:
                    self.world.removeEntity( item.entity )
                self.pickupWindow.guiParts = []

            self.pickupWindow.guiParts.clear()
            if len( self.pickupWindow.guiParts ) == 0:
                for item in itemsAtCurPos:
                    addButton( '%s (%d)' % ( item.definition.displayname, item.count ), lambda *_: pickup( item ) )

        elif self.pickupWindow in self.guiParts:
            self.guiParts.remove( self.pickupWindow )

        GameUtil.HandleExplosions( self, self.world.getEntityByComponent( ECS.Components.Position, GameComponents.Explosive ) )
        self.world.process()

        self.updateCamPos()
        self.render()

    def render( self ):
        #Game drawing
        self.screen.fill( ( 0, 0, 0 ) )

        if GameData.PlayerInventory.isDirty:
            GameUtil.UpdateInventory( self )
            GameData.PlayerInventory.isDirty = False


        #Render map
        GameData.Map.render( self.camX * GameData.TileSize[0], self.camY * GameData.TileSize[1] )

        #Render entities
        for ent in self.world.getEntityByComponent( ECS.Components.Position, ECS.Components.Renderer ):
            pos = ent.getComponent( ECS.Components.Position )

            if GameData.Map.isVisible( pos.x, pos.y ):
                pos = ( ( pos.x - self.camX ) * GameData.TileSize[0], ( pos.y - self.camY ) * GameData.TileSize[1] )
                ent.getComponent( ECS.Components.Renderer ).render( self.screen, pos )

        #Render tile cursor
        GameData.MainAtlas.render( 'cursor', self.screen,
                ( self.mouseTilePos[0] - self.camX ) * GameData.TileSize[0],
                ( self.mouseTilePos[1] - self.camY ) * GameData.TileSize[1] )

        #Render GUI
        for n in self.guiParts:
            n.render( self.screen )

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
                definition = self.getSelectedItemIfUseableAs( 'throw' )
                if definition is not None:
                    if definition.has( 'dropsAs' ):
                        explosive = GameUtil.CreateEntity( self, definition.dropsAs )
                    else:
                        explosive = GameUtil.CreateEntity( self, definition )
                    self.playerAction = GameComponents.Action( GameData.Player, 'throwEntity', ( explosive, self.mouseTilePos ) )
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F2 and Cheats.KeyboardCheats:
                    Cheats.ViewAll = not Cheats.ViewAll
                    GameData.Map.renderDirty = True
                elif event.key == pygame.K_F3 and Cheats.KeyboardCheats:
                    Cheats.Flying = not Cheats.Flying
                elif event.key == pygame.K_F4 and Cheats.KeyboardCheats:
                    GameData.PlayerInventory.addItem( GameData.TypeDefinitions['item']['item_stickygoo'], 10 )
                elif event.key == pygame.K_w:
                    self.playerAction = GameComponents.Action( GameData.Player, 'move', ( 0, -1 ) )
                elif event.key == pygame.K_s:
                    self.playerAction = GameComponents.Action( GameData.Player, 'move', ( 0, 1 ) )
                elif event.key == pygame.K_a:
                    self.playerAction = GameComponents.Action( GameData.Player, 'move', ( -1, 0 ) )
                elif event.key == pygame.K_d:
                    self.playerAction = GameComponents.Action( GameData.Player, 'move', ( 1, 0 ) )
                elif event.key in ( pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8 ):
                    slot = ( event.key - pygame.K_0 ) - 1
                    self.inventorySlot = slot

                    GameUtil.UpdateInventory( self )
                elif event.key == pygame.K_e:
                    self.dropItem()

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

    def getSelectedItemIfUseableAs( self, action ):
        slot = self.inventorySlot

        if slot in GameData.PlayerInventory.inventory and GameData.PlayerInventory.inventory[slot][1] > 0:
            definition = GameData.PlayerInventory.inventory[slot][0]

            if definition.has( 'use' ) and ( definition.use == action or action in definition.use ):
                if GameData.PlayerInventory.dropItem( slot, 1 ):
                    return definition

        return None

    def dropItem( self ):
        definition = self.getSelectedItemIfUseableAs( 'drop' )
        if definition is not None:
            if definition.has( 'dropsAs' ):
                explosive = GameUtil.CreateEntity( self, definition.dropsAs )
            else:
                explosive = GameUtil.CreateEntity( self, definition )
            self.playerAction = GameComponents.Action( GameData.Player, 'dropEntity', explosive )
