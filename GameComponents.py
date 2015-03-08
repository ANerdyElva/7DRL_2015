import ECS

class Explosive( ECS.Component ):
    def __init__( self, strength ):
        self.strength = strength

    def __str__( self ):
        return '{Explosive, strength: %d}' % ( self.strength )
