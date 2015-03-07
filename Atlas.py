import pygame

class Atlas:
    def __init__( self, fileName, tileSize ):
        self.image = pygame.image.load( fileName )
        self.fileName = fileName
        self.tileSize = tileSize

        self.tileCount = (
                self.image.get_width() / self.tileSize[0], 
                self.image.get_height() / self.tileSize[1] )

        self.mapping = {}

    def map_values_to_font( self, val, count, tileX, tileY ):
        for i in range( count ):
            self.map_val_to_font( val, tileX, tileY )

            val += 1
            tileX += 1
            if tileX == self.tileCount[0]:
                tileX = 0
                tileY += 1

    def map_val_to_font( self, val, tileX, tileY ):
        n = ( tileX * self.tileSize[0], tileY * self.tileSize[1] )
        self.mapping[ val ] = self.image.subsurface( pygame.Rect( n[0], n[1], self.tileSize[0], self.tileSize[1] ) )

    def render( self, val, target, dstX, dstY ):
        target.blit( self.mapping[ val ], ( dstX, dstY ) )
