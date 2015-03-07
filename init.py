from TileTypes import *

from Map import Map
from MapGen import *
from Atlas import Atlas

_map = Map( 500, 500 )

tiles = Atlas( 'tiles.png', ( 32, 32 ) )

_map.makeMap( initializeRandom, preIterInit, postInit )
_map.render( tiles )

pos = [ 250, 250 ]
running = True

import pygame
pygame.init()

screen = pygame.display.set_mode( ( 1280, 960 ) )
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
    screen.fill( ( 255, 255, 255 ) )

    screen.blit( _map.surface.subsurface( pygame.Rect( pos[0] * 32, pos[1] * 32, screen.get_width(), screen.get_height()  ) ), ( 0, 0 ) )

    pygame.display.flip()
    clock.tick(60)

#def handleKey( key ):
#    if key.vk == tcod.KEY_ESCAPE:
#        global running
#        running = False
#    elif key.c == ord('w'):
#        pos[1] -= 1
#    elif key.c == ord('s'):
#        pos[1] += 1
#    elif key.c == ord('a'):
#        pos[0] -= 1
#    elif key.c == ord('d'):
#        pos[0] += 1
#
#
#while not tcod.console_is_window_closed() and running:
#    offsetX = pos[0] - int( SCREEN_WIDTH / 2 )
#    offsetY = pos[1] - int( SCREEN_HEIGHT / 2 )
#
#    tcod.console_blit( _map.console, offsetX, offsetY, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0, 1.0, 1.0 )
#
#    tcod.console_flush()
#    handleKey( tcod.console_wait_for_keypress( False ) )
