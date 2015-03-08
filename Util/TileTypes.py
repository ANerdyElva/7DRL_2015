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

    def render( self, target, x, y, worldX, worldY ):
        pass

class BaseTileType( TileType ):
    def __init__( self, typeId, name, atlas, atlasIndex ):
        super().__init__( typeId, name )
        self.atlas = atlas
        self.atlasIndex = atlasIndex

    def render( self, target, x, y, worldX, worldY ):
        self.atlas.render( self.atlasIndex, target, x, y )

def bsd_rand(seed):
    seed = (1103515245 * seed + 12345) & 0x7fffffff
    seed = (1103515245 * seed + 12345) & 0x7fffffff
    seed = (1103515245 * seed + 12345) & 0x7fffffff
    return seed

class MultiTileType( BaseTileType ):
    def __init__( self, typeId, name, atlas, atlasIndex, atlasEnd ):
        super().__init__( typeId, name, atlas, atlasIndex )
        self.atlasEnd = atlasEnd

    def render( self, target, x, y, worldX, worldY ):
        _hash = ( bsd_rand( worldX ) ^ bsd_rand( worldY ) ) & 127

        if _hash < 64:
            self.atlas.render( self.atlasIndex, target, x, y )
        else:
            offset = ( ( _hash - 64 ) / 64.0 )
            self.atlas.render( self.atlasIndex + int( offset * self.atlasEnd ), target, x, y )
