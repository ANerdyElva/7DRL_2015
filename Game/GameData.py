import Util
import random
import pygame
import DataInit

#Global definitions
TileSize = ( 32, 32 )
TileCount = ( 500, 500 )

CenterPos = [ TileCount[0] / 2, TileCount[1] / 2 ]
IsGameRunning = True

#Global variables
Screen = None
Map = None #Initialized in init.py
Player = None
PlayerPosition = None
PlayerInventory = None
Fonts = {}

TypeDefinitions = {}

#Load the tiles and register which are being used
AtlasMap = {}

MainAtlas = Util.Atlas( 'data/tiles.png', TileSize )
AtlasMap['data/tiles.png'] = MainAtlas

MainAtlas.map_values_to_font( 0, 7, 0, 0 ) #Stone blocks
MainAtlas.map_values_to_font( 8, 4, 0, 1 ) #Bricks
MainAtlas.map_values_to_font( 16, 1, 7, 1 ) #Rubble
MainAtlas.map_values_to_font( 24, 1, 0, 2 ) #Rubble
MainAtlas.map_val_to_font( 'air', 7, 0 )
MainAtlas.map_val_to_font( 'cursor', 5, 1 )
MainAtlas.map_val_to_font( 'cursor_green', 6, 1 )
MainAtlas.map_val_to_font( 'cursor_red', 6, 1 )

Entities = Util.Atlas( 'data/entity.png', TileSize )
AtlasMap['data/entity.png'] = Entities

Entities.map_val_to_font( 'tnt', 0, 0 )
Entities.map_val_to_font( 'player', 1, 0 )

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

    global TypeDefinitions
    TypeDefinitions = DataInit.TypeDefinitions

    for n in TypeDefinitions['image']:
        definition = TypeDefinitions['image'][n]

        if definition.file not in AtlasMap:
            AtlasMap[definition.file] = Util.Atlas( definition.file, definition.size )

        atlas = AtlasMap[definition.file]
        atlas.map_val_to_font( definition.key, definition.atlasX, definition.atlasY )


#Build the TileTypes, no need to register them, that's handled in their constructor.
FloorAtlasIndex = 24

Util.TileType( Util.TILE_AIR, 'Air', hardness = 0.5, passable = True, viewThrough = True, transparent = True )

Util.BaseTileType( Util.TILE_RUBBLE, 'Rubble', MainAtlas, 16, hardness = 0.25, passable = True, viewThrough = True, transparent = True )
Util.MultiTileType( Util.TILE_FIXED_WALL, 'Fixed wall', MainAtlas, 8, 4 )
Util.MultiTileType( Util.TILE_WALL, 'Wall', MainAtlas, 0, 7,
        hardness = 20,
        onDestruction = lambda x, y: Util.TILE_RUBBLE if random.random() < 0.25 else Util.TILE_AIR )

