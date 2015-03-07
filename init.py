import libtcodpy as tcod
from TileTypes import *

print( [ ( n, getattr( tcod, n ) ) for n in dir( tcod ) if n[:4] == 'FONT' ] )

from Map import Map
from MapGen import *

SCREEN_WIDTH = 180
SCREEN_HEIGHT = 100

#tcod.console_set_custom_font(b'data/fonts/arial10x10.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)
tcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, b'python/tcod tutorial', False)

_map = Map( 500, 500 )

_map.makeMap( initializeRandom, preIterInit, postInit )
_map.render()

pos = [ 250, 250 ]
running = True

def handleKey( key ):
    if key.vk == tcod.KEY_ESCAPE:
        global running
        running = False
    elif key.c == ord('w'):
        pos[1] -= 1
    elif key.c == ord('s'):
        pos[1] += 1
    elif key.c == ord('a'):
        pos[0] -= 1
    elif key.c == ord('d'):
        pos[0] += 1


while not tcod.console_is_window_closed() and running:
    offsetX = pos[0] - int( SCREEN_WIDTH / 2 )
    offsetY = pos[1] - int( SCREEN_HEIGHT / 2 )

    tcod.console_blit( _map.console, offsetX, offsetY, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0, 1.0, 1.0 )

    tcod.console_flush()
    handleKey( tcod.console_wait_for_keypress( False ) )
