import GameData
import pygame

import functools

def LoadFont( name, fileName = '', size = '' ):
    if name in GameData.Fonts:
        return GameData.Fonts[name]

    font = pygame.font.Font( fileName, size )
    GameData.Fonts[ name ] = font

    return font

@functools.lru_cache( maxsize = 128 )
def RenderFont( font, text, col ):
    return font.render( text, True, col )
