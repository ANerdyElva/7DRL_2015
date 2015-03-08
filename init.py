import pygame

from Util import *
from MapGen import *

tileSize = ( 32, 32 )
tileCount = ( 500, 500 )
tiles = Atlas( 'tiles.png', tileSize )

tiles.map_val_to_font( 0, 7, 0 )
tiles.map_values_to_font( 8, 4, 0, 1 )
tiles.map_values_to_font( 16, 7, 0, 0 )
tiles.map_val_to_font( 'cursor', 5, 1 )
tiles.map_val_to_font( 'cursor_green', 6, 1 )
tiles.map_val_to_font( 'cursor_red', 6, 1 )

TileType( TILE_AIR, 'Air' )

MultiTileType( TILE_WALL, 'Wall', tiles, 16, 7 )
MultiTileType( TILE_FIXED_WALL, 'Fixed wall', tiles, 8, 4 )

pygame.init()

pygame.display.set_caption( "That's okay. You've got explosives." )
screen = pygame.display.set_mode( ( 1280, 960 ) )
screenTiles = ( int( screen.get_width() / tileSize[0] ), int( screen.get_height() / tileSize[1] ) )

_map = Map( tileCount[0], tileCount[1], tiles, screen )
_map.makeMap( initializeRandom, preIterInit, postInit )

pos = [ tileCount[0] / 2, tileCount[1] / 2 ]
running = True

screenTileSize = ( int( 1280 / tileSize[0] ), int( 960 / tileSize[1] ) )

done = False

clock = pygame.time.Clock()


while not done:
    #Calculate mouse tile
    camX = min( max( pos[0] - int( screenTiles[0] / 2 ), 0 ), tileCount[0] - screenTiles[0] )
    camY = min( max( pos[1] - int( screenTiles[1] / 2 ), 0 ), tileCount[1] - screenTiles[1] )

    mousePos = pygame.mouse.get_pos()
    mouseTilePos = ( int( ( camX * tileSize[0] + mousePos[0] ) / tileSize[0] ), int( ( camY * tileSize[1] + mousePos[1] ) / tileSize[1] ) )

    #Game logic
    for event in pygame.event.get():
        if event.type == pygame.QUIT or ( event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE ):
            done = True
        #elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:


    curKeys = pygame.key.get_pressed()
    if curKeys[pygame.K_w]:
        pos[1] -= 1
    if curKeys[pygame.K_s]:
        pos[1] += 1
    if curKeys[pygame.K_a]:
        pos[0] -= 1
    if curKeys[pygame.K_d]:
        pos[0] += 1


    #Game drawing
    screen.fill( ( 255, 255, 255 ) )

    _map.render( camX * tileSize[0], camY * tileSize[1] )
    tiles.render( 'cursor', screen, ( mouseTilePos[0] - camX ) * tileSize[0], ( mouseTilePos[1] - camY ) * tileSize[1] )

    pygame.display.flip()
    clock.tick(60)
