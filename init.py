import pygame

###########################################################
# Init pygame
###########################################################
pygame.init()

pygame.display.set_caption( "That's okay. You've got explosives." )
screen = pygame.display.set_mode( ( 1280, 960 ) )


#TODO Render a loading screen to the map
import GameData

#TODO Start a main screen

#Start the game
import Game
state = Game.Game( screen )
state.run()
