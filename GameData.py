import Util
import random
import pygame

#Global definitions
TileSize = ( 32, 32 )
TileCount = ( 500, 500 )

CenterPos = [ TileCount[0] / 2, TileCount[1] / 2 ]
IsGameRunning = True

#Global variables
Screen = None
Map = None #Initialized in init.py
Player = None
Fonts = {}

#Load the tiles and register which are being used
MainAtlas = Util.Atlas( 'data/tiles.png', TileSize )

MainAtlas.map_values_to_font( 0, 7, 0, 0 ) #Stone blocks
MainAtlas.map_values_to_font( 8, 4, 0, 1 ) #Bricks
MainAtlas.map_values_to_font( 16, 1, 7, 1 ) #Rubble
MainAtlas.map_values_to_font( 24, 1, 0, 2 ) #Rubble
MainAtlas.map_val_to_font( 'air', 7, 0 )
MainAtlas.map_val_to_font( 'cursor', 5, 1 )
MainAtlas.map_val_to_font( 'cursor_green', 6, 1 )
MainAtlas.map_val_to_font( 'cursor_red', 6, 1 )

Entities = Util.Atlas( 'data/entity.png', TileSize )

Entities.map_val_to_font( 'tnt', 0, 0 )

ExplosiveAtlas = Util.Atlas( 'data/explosion.png', TileSize )
ExplosiveAtlas.map_values_to_font( 0, 74, 0, 0 )

#Load the large images
MenuBackground = None
Fog = None

def update():
    global Screen
    global MenuBackground
    global Fog

    MenuBackground = pygame.transform.smoothscale( pygame.image.load( 'data/parchment_1.png' ), ( Screen.get_width(), Screen.get_height() ) )
    Fog = pygame.transform.smoothscale( pygame.image.load( 'data/fog.png' ), ( Screen.get_width(), Screen.get_height() ) )
    Fog.set_alpha( 60 )

#Build the TileTypes, no need to register them, that's handled in their constructor.
FloorAtlasIndex = 24

Util.TileType( Util.TILE_AIR, 'Air', hardness = 0.5, passable = True, viewThrough = True, transparent = True )

Util.BaseTileType( Util.TILE_RUBBLE, 'Rubble', MainAtlas, 16, hardness = 0.25, passable = True, viewThrough = True, transparent = True )
Util.MultiTileType( Util.TILE_FIXED_WALL, 'Fixed wall', MainAtlas, 8, 4 )
Util.MultiTileType( Util.TILE_WALL, 'Wall', MainAtlas, 0, 7,
        hardness = 20,
        onDestruction = lambda x, y: Util.TILE_RUBBLE if random.random() < 0.25 else Util.TILE_AIR )

