import pygame
import Util

WindowParts = (
        pygame.image.load( 'gui/window_tl.png' ),
        pygame.image.load( 'gui/window_t.png' ),
        pygame.image.load( 'gui/window_tr.png' ),
        pygame.image.load( 'gui/window_l.png' ),
        pygame.image.load( 'gui/window_r.png' ),
        pygame.image.load( 'gui/window_bl.png' ),
        pygame.image.load( 'gui/window_b.png' ),
        pygame.image.load( 'gui/window_br.png' )
        )

class GuiPart:
    def __init__( self ):
        self.surface = None
        self.x = -1
        self.y = -1
        self.width = -1
        self.height = -1
        self.parent = None

    def move( self, x, y ):
        self.x = x
        self.y = y

    def _getSurface( self ):
        return self.surface

    def _makeSurface( self, width, height, flags = 0 ):
        if self.surface is None or width != self.surface.get_width() or height != self.surface.get_height():
            self.surface = pygame.Surface( ( width, height ), flags = flags )

        self.width = width
        self.height = height

        return self.surface

    def render( self, target ):
        if self.surface is None:
            self._render()

        self._x = self.x
        self._y = self.y

        if self.parent is not None:
            self._x += self.parent._x
            self._y += self.parent._y

        target.blit( self.surface, ( self._x, self._y ) )

    def _checkInteraction( self, x, y, buttonPressed ):
        if x < self.width and y < self.height:
            return self.doInteraction( x, y, buttonPressed )
        else:
            return False
    def checkInteraction( self, event ):
        x = event.pos[0] - self.x
        y = event.pos[1] - self.y

        return self._checkInteraction( x, y, event.type == pygame.MOUSEBUTTONUP )


class Window( GuiPart ):
    def __init__( self, width, height, x, y ):
        super().__init__()
        self.parts = WindowParts
        self.backgroundCol = ( 54, 47, 45 )

        self.setSize( width, height )
        self.move( x, y )

        self.guiParts = []

    def setSize( self, width, height ):
        width = max( width, 200 )
        height = max( height, 200 )

        surface = self._makeSurface( width, height )
        surface.fill( self.backgroundCol )

        # Top bar
        surface.blit( pygame.transform.scale( self.parts[1], ( width - 24 - 24, 24 ) ), ( 24, 0 ) )
        # Bottom bar
        surface.blit( pygame.transform.scale( self.parts[6], ( width - 24 - 24, 24 ) ), ( 24, height - 24 ) )
        # Left bar
        surface.blit( pygame.transform.scale( self.parts[3], ( 24, height - 24 - 24 ) ), ( 0, 24 ) )
        # Right bar
        surface.blit( pygame.transform.scale( self.parts[4], ( 24, height - 24 - 24 ) ), ( width - 24, 24 ) )

        # Top left
        surface.blit( self.parts[0], ( 0, 0 ) )
        # Top right
        surface.blit( self.parts[2], ( width - 24, 0 ) )
        # Bottom left
        surface.blit( self.parts[5], ( 0, height - 24 ) )
        # Bottom right
        surface.blit( self.parts[7], ( width - 24, height - 24 ) )

    def doInteraction( self, relX, relY, buttonPressed ):
        for n in self.guiParts:
            if n._checkInteraction( relX - n.x, relY - n.y, buttonPressed ):
                return True

        return True

    def render( self, target ):
        super().render( target )

        for n in self.guiParts:
            n.parent = self
            n.render( target )



barParts = (
    pygame.image.load( 'gui/hotbar_back.png' ),
    pygame.image.load( 'gui/hotbar_glass.png' ),
    pygame.image.load( 'gui/hotbar_yellow_glass.png' ),
    )

class Hotbar( GuiPart ):
    def __init__( self, slotCount ):
        super().__init__()
        self.slotCount = slotCount

        self._makeSurface( 36 * slotCount, 44 )
        self.slotCallback = None

        for i in range( slotCount ):
            self.updateSlot( i, None, 0 )

    def updateSlot( self, which, callback, overlay = 0 ):
        pos = ( which * 36, 0 )

        surface = self._getSurface()
        surface.blit( barParts[0], pos )

        if callback is not None:
            callback( surface, pos )
        if overlay > 0:
            surface.blit( barParts[ overlay ], pos )

    def doInteraction( self, relX, relY, buttonPressed ):
        if not buttonPressed:
            return False

        if relY < 6 or relY > 38:
            return False

        slotI = int( relX / 36 )
        slotRelX = relX - ( slotI * 36 )
        if slotRelX < 2 or slotRelX > 34:
            return False

        if self.slotCallback is not None:
            self.slotCallback( slotI )

        return True

    def render( self, screen ):
        self.move( ( screen.get_width() - self.width ) / 2, screen.get_height() - self.height )
        super().render( screen )

class Button( GuiPart ):
    def __init__( self, font, text, pos, size ):
        super().__init__()
        self.font = font
        self.text = text

        self.pressCallback = None

        self.move( *pos )
        self._makeSurface( *size )

        self.surface.fill( (  24, 17, 15 ) )
        renderedFont = Util.RenderFont( self.font, self.text, ( 255, 255, 255 ) )
        self.surface.blit( renderedFont,
                ( ( self.surface.get_width() - renderedFont.get_width() ) / 2, ( self.surface.get_height() - renderedFont.get_height() ) / 2 ) )

    def doInteraction( self, x, y, pressed ):
        if x < 0 or x > self.width or y < 0 or y > self.height:
            return False

        if pressed and self.pressCallback is not None:
            self.pressCallback( self )

        return True

    def render( self, target ):
        super().render( target )

class Text( GuiPart ):
    def __init__( self, font, text, pos, size ):
        super().__init__()
        self.font = font
        self.text = text

        self.pressCallback = None

        self.move( *pos )
        self._makeSurface( *size, flags = pygame.SRCALPHA )

        self.surface.fill( ( 0, 0, 0, 0 ) )
        renderedFont = Util.RenderFont( self.font, self.text, ( 255, 255, 255 ) )
        self.surface.blit( renderedFont,
                ( ( self.surface.get_width() - renderedFont.get_width() ) / 2, ( self.surface.get_height() - renderedFont.get_height() ) / 2 ) )

    def doInteraction( self, x, y, pressed ):
        if x < 0 or x > self.width or y < 0 or y > self.height:
            return False

        if pressed and self.pressCallback is not None:
            self.pressCallback( self )

        return True

    def render( self, target ):
        super().render( target )
