import ECS

class Entity():
    def __init__( self, tag = None ):
        self.componentList = []
        self.componentMap = {}
        self.componentBaseMap = {}

        self.onRemove = []

        self.id = Entity.nextId
        self.passable = True

        Entity.nextId += 1

    def setWorld( self, world ):
        self.world = world
        self.world.markDirty()

        for comp in self.componentList:
            comp.finalize()

    def addComponent( self, comp ):
        compType = type( comp )
        self.componentList.append( comp )
        self.componentMap[ compType ] = comp
        comp._setEntity( self )

        base = compType.__bases__[0]
        while base != ECS.Component:
            if base in self.componentBaseMap:
                self.componentBaseMap[base].append( comp )
            else:
                self.componentBaseMap[base] = [ comp ]

            if base not in self.componentMap:
                self.componentMap[ base ] = comp

            base = base.__bases__[0]
        
    def getComponentByBase( self, base ):
        if base in self.componentBaseMap:
            return list( self.componentBaseMap[ base ] )

    def getComponent( self, comp ):
        if comp in self.componentMap:
            return self.componentMap[ comp ]
        else:
            return None

    def hasComponent( self, comp ):
        return comp in self.componentMap

    def __str__( self ):
        return '[Entity %d %s]' % ( self.id, '/'.join( [ str( self.componentMap[ n ] ) for n in self.componentMap ] ) )

    nextId = 1

