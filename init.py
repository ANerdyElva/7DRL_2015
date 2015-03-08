import pygame
import sys

import Cheats

for n in sys.argv:
    if hasattr( Cheats, n ):
        setattr( Cheats, n, True )

###########################################################
# Init pygame
###########################################################
pygame.init()

pygame.display.set_caption( "That's okay. You've got explosives." )
screen = pygame.display.set_mode( ( 1280, 960 ) )

#TODO Render a loading screen to the map?
import GameData
GameData.Screen = screen
GameData.update()

#TODO Start a main screen
import MainMenu
state = MainMenu.MainMenu( GameData.Screen )
state.run()
