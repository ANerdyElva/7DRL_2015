import pygame

import GameData

class GameState:
    def __init__( self, screen ):
        self.screen = screen
        self.screenTiles = ( int( screen.get_width() / GameData.TileSize[0] ), int( screen.get_height() / GameData.TileSize[1] ) )
        self.screenTileSize = ( int( 1280 / GameData.TileSize[0] ), int( 960 / GameData.TileSize[1] ) )
        
        self.clock = pygame.time.Clock()
        self.IsRunning = True
        self.RetVal = None

    def run( self ):
        while GameData.IsGameRunning and self.IsRunning:
            self.runFrame()

        return self.RetVal

    def quit( self, event ):
        GameData.IsGameRunning = False

    def handle( self, event ):
        if event.type == pygame.QUIT or ( event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE ):
            self.quit( event )
        else:
            return False

        return True
