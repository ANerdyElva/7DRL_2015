import pygame

import GameData
import Cheats

class GameState:
    def __init__( self, screen ):
        self.screen = screen
        self.screenTiles = ( int( screen.get_width() / GameData.TileSize[0] ), int( screen.get_height() / GameData.TileSize[1] ) )
        self.screenTileSize = ( int( 1280 / GameData.TileSize[0] ), int( 960 / GameData.TileSize[1] ) )
        
        self.clock = pygame.time.Clock()
        self.IsRunning = True
        self.RetVal = None

        self.guiParts = []

    def run( self ):
        average = 0
        frameNum = 0

        while GameData.IsGameRunning and self.IsRunning:
            start = pygame.time.get_ticks()
            GameData.CurTime = start
            self.runFrame()
            end = pygame.time.get_ticks()

            average = ( average * 4  + ( end - start ) ) / 5

            frameNum += 1
            if frameNum % 10 == 0:
                pygame.display.set_caption( "That's okay. You've got explosions. [%s] [%d]" % ( self.__class__.__name__, 1000.0 / average ) )

            if Cheats.QuitGame and frameNum > 50:
                GameData.IsGameRunning = False

        return self.RetVal

    def handle( self, event ):
        if event.type == pygame.QUIT or ( event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE ):
            self.quit( event )
        elif event.type in ( pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION ):
            for n in self.guiParts:
                if n.checkInteraction( event ):
                    return True
            return False
        else:
            return False

        return True
