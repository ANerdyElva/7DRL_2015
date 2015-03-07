TILE_AIR = 0

TILE_FIXED_WALL = 10
TILE_WALL = 11
TILE_RUBBLE = 12

TILE_DOOR_CLOSED = 20
TILE_DOOR_OPEN = 21

TileTypes = {}

class TileType:
    def __init__( self, typeId, name ):
        self.typeId = typeId
        self.name = name

        if self.typeId in TileTypes.keys():
            raise Exception( 'Double typeid: %d, %s' % ( self.typeId, self.name ) )

        TileTypes[ self.typeId ] = self

    def render( self, target, x, y ):
        pass

class BaseTileType( TileType ):
    def __init__( self, typeId, name, atlas, atlasIndex ):
        super().__init__( typeId, name )
        self.atlas = atlas
        self.atlasIndex = atlasIndex

    def render( self, target, x, y ):
        self.atlas.render( self.atlasIndex, target, x, y )
