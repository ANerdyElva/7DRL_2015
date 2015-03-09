import pygame
import GameData

import Cheats

from GameState import GameState
from Game import Game
import Util

class MainMenu( GameState ):
    def __init__( self, screen, isMain = True ):
        super().__init__( screen )
        self.background = GameData.MenuBackground
        self.isMain = isMain

        self.lines = []
        if isMain:
            self.lines.append( [ 'Start game', lambda event: self.startGame( event ) ] )
        else:
            self.lines.append( [ 'Back to game', lambda event: self.resumeGame( event ) ] )

        self.lines.append( tuple( ) )
        self.lines.append( tuple( ) )
        self.lines.append( tuple( ) )

        if not isMain:
            self.lines.append( [ 'Quit to main manu', lambda event: self.quitToMain( event ) ] )
        self.lines.append( [ 'Quit to desktop', lambda event: self.quit( event ) ] )

        self.fontLarge = Util.LoadFont( 'MenuLarge', 'data/segoesc.ttf', 28 )
        self.fontSmall = Util.LoadFont( 'MenuNormal', 'data/segoesc.ttf', 20 )

        self.activeMenu = None

        offset = 0
        for line in self.lines:
            if len( line ) > 0:
                font1 = Util.RenderFont( self.fontSmall, line[0], ( 50, 50, 50 ) )
                font2 = Util.RenderFont( self.fontSmall, line[0], ( 250, 80, 50 ) )

                line.append( font1 ) #2
                line.append( font2 ) #3
                line.append( pygame.Rect( 80, 354 + offset, font1.get_width(), font1.get_height() ) ) #4
            offset += 26


    def runFrame( self ):
        for event in pygame.event.get():
            if self.handle( event ):
                pass
            elif event.type == pygame.MOUSEMOTION:
                self.activeMenu = None
                for line in self.lines:
                    if len( line ) > 0 and line[4].collidepoint( pygame.mouse.get_pos() ):
                        self.activeMenu = line
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.activeMenu is not None:
                    self.activeMenu[1]( event )

        if Cheats.StartGame and self.isMain:
            self.startGame( None )

        self.render()

    def renderCentered( self, font, text, pos, col, alpha = 255 ):
        rendered = Util.RenderFont( font, text, col )

        _pos = ( pos[0] - int( rendered.get_width() / 2 ), pos[1] - int( rendered.get_height() / 2 ) )

        if alpha < 255:
            rect = pygame.Rect( _pos[0], _pos[1], rendered.get_width(), rendered.get_height() )
            back = self.background.subsurface( rect ).convert()
            back.blit( rendered, ( 0, 0 ) )

            back.set_alpha( alpha )
            self.screen.blit( back, _pos )
        else:
            self.screen.blit( rendered, _pos )

    def render( self ):
        self.screen.blit( self.background, ( 0, 0 ) )

        def timedRender( text, pos, time ):
            if pygame.time.get_ticks() > time:
                self.renderCentered( self.fontLarge, text, pos, ( 50, 50, 50 ),
                        min( 255, ( pygame.time.get_ticks() - time ) / 2000 * 255.0 ) )

        def h( large, small ):
            return 80 + large * 39 + small * 20
        self.renderCentered( self.fontLarge, 'You are in a maze of twisty passages,', ( self.screen.get_width() / 2, h( 0, 0 ) ), ( 50, 50, 50 ) )
        timedRender( "All alike.", ( self.screen.get_width() / 2, h( 1, 0 ) ), 1500 )
        timedRender( "You see no way out.", ( self.screen.get_width() / 2, h( 2, 1 ) ), 3000 )
        timedRender( "But that's okay.", ( self.screen.get_width() / 2, h( 3, 2 ) ), 4500 )
        timedRender( "You've got explosives.", ( self.screen.get_width() / 2, h( 4, 2 ) ), 6500 )
        
        offset = 0
        for line in self.lines:
            if len( line ) > 1:
                self.screen.blit( line[3] if self.activeMenu == line else line[2], line[4] )

            offset += 1

        pygame.display.flip()

    def startGame( self, event ):
        game = Game( self.screen, lambda event: MainMenu( self.screen, False ).run() )
        game.run()

    def resumeGame( self, event ):
        self.IsRunning = False

    def quit( self, event ):
        if self.isMain:
            self.IsRunning = False
        else:
            GameData.IsGameRunning = False

    def quitToMain( self, event ):
        self.IsRunning = False
        self.RetVal = True
