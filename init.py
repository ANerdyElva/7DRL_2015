from TileTypes import *

from Map import Map
from MapGen import *
from Atlas import Atlas

_map = Map( 500, 500 )

tileSize = ( 32, 32 )
tiles = Atlas( 'tiles.png', tileSize )

_map.makeMap( initializeRandom, preIterInit, postInit )
_map.preRender( tiles )

pos = [ 250, 250 ]
running = True

import pygame
pygame.init()

screen = pygame.display.set_mode( ( 1280, 960 ) )
screenTileSize = ( int( 1280 / tileSize[0] ), int( 960 / tileSize[1] ) )
pygame.display.set_caption( "That's okay. You've got explosives." )

done = False

clock = pygame.time.Clock()

while not done:
    #Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT or ( event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE ):
            done = True

    curKeys = pygame.key.get_pressed()
    if curKeys[pygame.K_w]:
        pos[1] -= 1
    if curKeys[pygame.K_s]:
        pos[1] += 1
    if curKeys[pygame.K_a]:
        pos[0] -= 1
    if curKeys[pygame.K_d]:
        pos[0] += 1

    #Game logic

    #Game drawing
    camX = min( max( ( pos[0] * tileSize[0] ) - screen.get_width() / 2, 0 ), _map.surface.get_width() - screen.get_width() )
    camY = min( max( ( pos[1] * tileSize[1] ) - screen.get_height() / 2, 0 ), _map.surface.get_height() - screen.get_height() )

    screen.fill( ( 255, 255, 255 ) )

    _map.render( screen, camX, camY )

    pygame.display.flip()
    clock.tick(60)
