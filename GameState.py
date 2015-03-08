import pygame

import GameData

class GameState:
    def __init__( self, screen ):
        self.screen = screen
        self.screenTiles = ( int( screen.get_width() / GameData.TileSize[0] ), int( screen.get_height() / GameData.TileSize[1] ) )
        self.screenTileSize = ( int( 1280 / GameData.TileSize[0] ), int( 960 / GameData.TileSize[1] ) )
        
        self.clock = pygame.time.Clock()

    def run( self ):
        while GameData.IsGameRunning:
            self.runFrame()



