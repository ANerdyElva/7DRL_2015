import Util

#Global definitions
TileSize = ( 32, 32 )
TileCount = ( 500, 500 )

CenterPos = [ TileCount[0] / 2, TileCount[1] / 2 ]
IsGameRunning = True

#Global variables
Map = None #Initialized in init.py
Fonts = {}

#Load the tiles and register which are being used
MainAtlas = Util.Atlas( 'data/tiles.png', TileSize )

MainAtlas.map_val_to_font( 0, 7, 0 )
MainAtlas.map_values_to_font( 8, 4, 0, 1 )
MainAtlas.map_values_to_font( 16, 7, 0, 0 )
MainAtlas.map_val_to_font( 'cursor', 5, 1 )
MainAtlas.map_val_to_font( 'cursor_green', 6, 1 )
MainAtlas.map_val_to_font( 'cursor_red', 6, 1 )

Entities = Util.Atlas( 'data/entity.png', TileSize )

Entities.map_val_to_font( 'tnt', 0, 0 )

#Build the TileTypes, no need to register them, that's handled in their constructor.
Util.TileType( Util.TILE_AIR, 'Air', hardness = 0.5 )

Util.MultiTileType( Util.TILE_WALL, 'Wall', MainAtlas, 16, 7, hardness = 4 )
Util.MultiTileType( Util.TILE_FIXED_WALL, 'Fixed wall', MainAtlas, 8, 4 )

