import pygame

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

    def _getSurface( self ):
        return self.surface

    def _makeSurface( self, width, height ):
        if self.surface is None or width != self.surface.get_width() or height != self.surface.get_height():
            self.surface = pygame.Surface( ( width, height ) )

        self.width = width
        self.height = height

        return self.surface

    def renderAt( self, target, x, y ):
        target.blit( self.surface, ( x, y ) )
        self.x = x
        self.y = y

    def checkInteraction( self, event ):
        x = event.pos[0] - self.x
        y = event.pos[1] - self.y

        if x < self.width and y < self.height:
            return self.doInteraction( x, y )
        else:
            return False


class Window( GuiPart ):
    def __init__( self, width, height ):
        super().__init__()
        self.parts = WindowParts
        self.backgroundCol = ( 54, 47, 45 )

        self.setSize( width, height )

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

    def doInteraction( self, relX, relY ):
        pass

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

    def doInteraction( self, relX, relY ):
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
        self.renderAt( screen, ( screen.get_width() - self.width ) / 2, screen.get_height() - self.height )
