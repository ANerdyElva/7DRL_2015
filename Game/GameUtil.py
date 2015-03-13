import random
import math

from Util import *

import ECS
import Cheats
import GameComponents
import GameData
from ActionSystem import ActionSystem
import Actions
import Window

def LoadEntities( self ):
    self.world = ECS.World()
    self.actionSystem = ActionSystem( self.world, Actions.ActionMap )
    self.world.addSystem( self.actionSystem )

    self.playerAction = None
    def playerAction( __, _, wasBlocked, curTurn ):
        if self.playerAction is not None:
            char = GameData.Player.getComponent( GameComponents.Character )
            if random.random() < 0.125:
                char.attributes[ 'Health' ] = min( char.attributes[ 'Health' ] + 1, char.attributes[ 'baseHealth' ] )

        ret = self.playerAction
        self.playerAction = None
        return ret

    GameData.Player = ECS.Entity()
    GameData.Player.addComponent( ECS.Components.Position( int( GameData.CenterPos[ 0 ] ), int( GameData.CenterPos[1] ) ) )
    GameData.Player.addComponent( GameComponents.Character( GameData.TypeDefinitions['enemy']['player'] ) )
    GameData.Player.addComponent( GameComponents.CharacterRenderer( GameData.TypeDefinitions['enemy']['player'] ) )
    GameData.Player.addComponent( GameComponents.TurnTaker( playerAction ) )
    GameData.Player.isPlayer = True

    GameData.PlayerInventory = GameComponents.Inventory( 8 ) 
    GameData.Player.addComponent( GameData.PlayerInventory )

    GameData.PlayerInventory.addItem( GameData.TypeDefinitions['item']['item_explosive'], 1 )
    def updateInventoryCallback():
        GameData.PlayerInventory.inventory[0][1] = 99
    GameData.PlayerInventory.updateCallback = updateInventoryCallback
    GameData.PlayerInventory.addItem( GameData.TypeDefinitions['item']['item_explosive'], 1 )

    GameData.PlayerPosition = GameData.Player.getComponent( ECS.Components.Position )
    self.world.addEntity( GameData.Player )

    #Drop key in room
    key = CreateEntity( self, 'item_explosive_special' )
    key.addComponent( ECS.Components.Position( int( GameData.TileCount[0] / 2 ), int( GameData.TileCount[1] / 2 ) + 3 ) )
    self.world.addEntity( key )

    #Spawn some enemies
    spawnables = []
    for n in GameData.TypeDefinitions['enemy_base']:
        if n == 'enemy_base':
            continue

        for count in range( GameData.TypeDefinitions['enemy_base'][n].spawnChance ):
            spawnables.append( n )

    curSurface = ( GameData.MapGen_CenterRoom_Size[0] * 2 ) * ( GameData.MapGen_CenterRoom_Size[1] * 2 )

    curRadius = -1

    def setFixedWall( x, y ):
        _buffer[ I( int( x ), int( y ) ) ] = TILE_FIXED_WALL

    circleNum = 0
    while curRadius < GameData.MapGen_MaxCircleRadius:
        sectionCount = max( circleNum * GameData.MapGen_CircleSectionsPerLayer, 1 )
        nextSurface = curSurface + ( GameData.MapGen_BaseSurface * sectionCount )

        nextRadius = int( math.sqrt( nextSurface / math.pi ) )

        sectionAngle = math.pi * 2 / sectionCount

        def getPointInsection( curSection ):
            r = random.randrange( curRadius, nextRadius )
            angle = ( curSection + random.random() ) * sectionAngle

            return ( int( math.sin( angle ) * r + GameData.CenterPos[0] ), int( math.cos( angle ) * r + GameData.CenterPos[1] ) )

        for curSection in range( sectionCount ):
            spawnsRemaining = circleNum * GameData.MapGen_MobsPerLevelIncrease

            while True:
                point = getPointInsection( curSection )

                if GameData.Map.get( *point ) == TILE_AIR:
                    key = CreateEntity( self, 'item_explosive_special' )
                    key.addComponent( ECS.Components.Position( *point ) )
                    self.world.addEntity( key )
                    break

            for attempt in range( int( spawnsRemaining * 2.5 ) ):
                point = getPointInsection( curSection )

                if GameData.Map.get( *point ) == TILE_AIR:
                    spawnsRemaining -= 1
                    ent = CreateEntity( self, spawnables[ circleNum % len( spawnables ) ] )
                    ent.addComponent( ECS.Components.Position( *point ) )
                    ent.active = False
                    self.world.addEntity( ent )


                if spawnsRemaining <= 0:
                    break



        curRadius = nextRadius
        curSurface = int( curRadius ** 2 * math.pi )
        circleNum += 1

    i = -4
    #for n in [ 'enemy_ranged_mook_1', 'enemy_ranged_mook_2', 'enemy_ranged_mook_3' ]:
    for n in [ 'enemy_ranged_mook_1' ]:
        ent = CreateEntity( self, n )
        ent.addComponent( ECS.Components.Position( int( GameData.TileCount[0] / 2 ) + i, int( GameData.TileCount[1] / 2 ) - 3 ) )
        self.world.addEntity( ent )
        i += 1


def HandleExplosions( self, explosionList ):
    hitTiles = {}
    positionMapping = None

    for explosionEnt in explosionList:
        explosive = explosionEnt.getComponent( GameComponents.Explosive )
        if not explosive.isFiring:
            continue

        if positionMapping is None:
            positionMapping = {}

            for ent in self.world.getEntityByComponent( ECS.Components.Position, GameComponents.Character ):
                pos = ent.getComponent( ECS.Components.Position )
                pos = ( pos.x, pos.y )

                if pos not in positionMapping:
                    positionMapping[ pos ] = [ 0 ]

                positionMapping[ pos ].append( ent )

        explosionPosition = explosionEnt.getComponent( ECS.Components.Position )
        explosionPosition = ( explosionPosition.x, explosionPosition.y )

        def handleRay( targetX, targetY ):
            curExplosionStrength = explosive.strength

            lastPos = ( explosionPosition[0], explosionPosition[1] )
            def handleBlock( x, y ): #Return value is whether or not to continue
                nonlocal curExplosionStrength
                if curExplosionStrength <= 0:
                    return False

                curToughness = TileTypes[ GameData.Map.get( x, y ) ].hardness
                if curToughness is None: #Unbreakable block
                    return False

                nonlocal lastPos
                if abs( lastPos[0] - x ) + abs( lastPos[1] - y ) == 2:
                    curExplosionStrength -= 7.07106781187 # sqrt(2)*5
                else:
                    curExplosionStrength -= 5
                lastPos = ( x, y )

                if ( x, y ) in positionMapping:
                    entList = positionMapping[ ( x, y ) ]
                    entList[0] += 1

                if ( x, y ) in hitTiles:
                    curToughness = hitTiles[ ( x, y ) ]
                else:
                    hitTiles[ ( x, y ) ] = curToughness

                if curExplosionStrength > curToughness:
                    hitTiles[ ( x, y ) ] = 0
                    curExplosionStrength -= curToughness
                    return True
                else: # curToughness >= curExplosionStrength
                    hitTiles[ ( x, y ) ] = curToughness - curExplosionStrength
                    curExplosionStrength = 0
                    return False

            for n in LineIter( explosionPosition[0], explosionPosition[1], int( explosionPosition[0] + targetX ), int( explosionPosition[1] + targetY ) ):
                yield handleBlock( *n )
            yield False

        rays = []
        for i in range( explosive.rayPerSquare ):
            s = math.sin( i * math.pi / 2 / explosive.rayPerSquare )
            c = math.cos( i * math.pi / 2 / explosive.rayPerSquare )

            rays.append( handleRay( s * 200 + 20 * random.random() - 10, c * 200 + 20 * random.random() - 10 ) )
            rays.append( handleRay( -s * 200 + 20 * random.random() - 10, c * 200 + 20 * random.random() - 10 ) )
            rays.append( handleRay( s * 200 + 20 * random.random() - 10, -c * 200 + 20 * random.random() - 10 ) )
            rays.append( handleRay( -s * 200 + 20 * random.random() - 10, -c * 200 + 20 * random.random() - 10 ) )

        newRays = []
        while len( rays ) > 0:
            for n in rays:
                if next( n ):
                    newRays.append( n )

            rays = newRays
            newRays = []

        explosive.onFire()


    if positionMapping is not None:
        hitEntities = [ n for n in positionMapping.values() if n[0] > 0 ]

        for n in hitEntities:
            damage = math.sqrt( n[0] )
            for hitEnt in n[1:]:
                hitEnt.getComponent( GameComponents.Character ).takeDamage( damage )

    if len( hitTiles ) > 0:
        for tilePos in hitTiles:
            if hitTiles[ tilePos ] == 0:
                tileType = TileTypes[ GameData.Map.get( tilePos[0], tilePos[1] ) ]
                targetType = TILE_AIR

                if hasattr( tileType, 'onDestruction' ):
                    targetType = tileType.onDestruction( *tilePos )

                GameData.Map.set( tilePos[0], tilePos[1], targetType )

                effect = ECS.Entity()
                effect.addComponent( ECS.Components.Position( *tilePos ) )
                effect.addComponent( GameComponents.ExplosionRenderer() )
                self.world.addEntity( effect )

CreateEntityComponentMapping = {
        'item': ( lambda  definition, args: GameComponents.Item( *args ) ),
        'specialbomb': ( lambda  definition, args: GameComponents.SpecialExplosive( *args ) ),
        'character': ( lambda  definition, _: ( GameComponents.Character( definition ), GameComponents.CharacterRenderer( definition ) ) ),
        'baseAI': ( lambda  definition, _: GameComponents.TurnTaker( ai = GameComponents.TurnTakerAi() ) ),
        'proximity': ( lambda definition, radius: GameComponents.ProximityBomb( radius ) ),
        'sticky': ( lambda definition, distance: GameComponents.StickyBomb( distance ) ),
        'explosiveRenderer': ( lambda definition, _: GameComponents.BombRenderer( definition ) ),
        }

def CreateEntity( self, definition ):
    if isinstance( definition, str ):
        definition = GameData.TypeDefinitions[''][ definition ]

    if Cheats.Verbose:
        print( 'CreateEntity %s' % str( definition ) )

    ent = ECS.Entity()

    if definition.has( 'explosion_rayStrength' ) and definition.has( 'explosion_rayCount' ):
        exp = GameComponents.Explosive( int( definition.explosion_rayCount / 4 ), definition.explosion_rayStrength )
        ent.addComponent( exp )

    if definition.has( 'explosion_delay' ):
        ent.addComponent( GameComponents.TurnTaker( ai = GameComponents.BombAi( definition.explosion_delay ) ) )

    if 'item' in definition.baseType:
        ent.addComponent( GameComponents.Item( definition ) )

    if definition.has( 'components' ):
        try:
            for comp in definition.components:
                factory = CreateEntityComponentMapping[ comp ]
                createComps = factory( definition, definition.components[ comp ] )
                try:
                    for createComp in createComps:
                        ent.addComponent( createComp )
                except TypeError:
                    ent.addComponent( createComps )
        except KeyError as e:
            print( 'Exception: ' + repr( e ) )

    #TODO Make a nice factory set up out of this
    if definition.has( 'image' ) and not ent.hasComponent( ECS.Components.Renderer ):
        img = GameData.TypeDefinitions['image'][ definition.image ]
        ent.addComponent( ECS.Components.Renderer( GameData.AtlasMap[ img.file ], img.key ) )

    return ent

def ShowCombineCount( game, recipe, maxCraftable ):
    game.actionWindow.guiParts = []
    count = 1

    def addButton( text, cb ):
        nonlocal count
        button = Window.Button( LoadFont( 'ButtonFont', '', '' ), text, ( 20, 30 * count ), ( 260, 25 ) )
        button.pressCallback = cb
        game.actionWindow.guiParts.append( button )

        count += 1

    def cancel( *_ ):
        GameData.PlayerInventory.isDirty = True 

    addButton( 'Cancel', cancel )
    
    def craft( finalCount ):
        inv = GameData.PlayerInventory.inventory

        for i in range( finalCount ):
            if GameData.PlayerInventory.addItem( GameData.TypeDefinitions['item'][recipe.result], 1 ) == 0:
                notDropped = dict( [ (n,1) for n in recipe.items ] )

                while len( notDropped ) > 0:
                    try:
                        for n in inv:
                            if inv[n][0].name in notDropped:
                                del notDropped[inv[n][0].name]
                                GameData.PlayerInventory.dropItem( n, 1 )
                    except:
                        pass


    addButton( 'Craft 1', lambda *_: craft( 1 ) )
    addButton( 'Craft %d' % int( maxCraftable / 2 ), lambda *_: craft( int( maxCraftable / 2 )) )
    addButton( 'Craft %d' % maxCraftable, lambda *_: craft( maxCraftable ) )


def ShowCombineButton( game ):
    game.actionWindow.guiParts = []
    count = 1

    def addButton( text, cb ):
        nonlocal count
        button = Window.Button( LoadFont( 'ButtonFont', '', '' ), text, ( 20, 30 * count ), ( 260, 25 ) )
        button.pressCallback = cb
        game.actionWindow.guiParts.append( button )

        count += 1

    def cancel( *_ ):
        GameData.PlayerInventory.isDirty = True 

    addButton( 'Cancel', cancel )

    selected = game.inventorySlot
    definition = GameData.PlayerInventory.inventory[selected][0]
    defName = definition.name

    for recipeName in GameData.TypeDefinitions['recipe']:
        recipe = GameData.TypeDefinitions['recipe'][recipeName]
        recipeResult = GameData.TypeDefinitions['item'][recipe.result]

        maxCount = recipeResult.maxStackSize
        typedCount = {}

        for name in recipe.items:
            typedCount[name] = 0

            for i in GameData.PlayerInventory.inventory:
                item = GameData.PlayerInventory.inventory[i][0]
                if item.name == name:
                    typedCount[name] += GameData.PlayerInventory.inventory[i][1]

        maxCraftable = min( [ typedCount[n] for n in typedCount ] )
        if maxCraftable > maxCount:
            maxCraftable = maxCount
        if maxCraftable > 0:
            addButton( '%s (max %d)' % ( recipeResult.displayname, maxCraftable ), lambda *_: ShowCombineCount( game, recipe, maxCraftable ) )

fontInventoryCount = LoadFont( 'InventoryCount', 'data/framd.ttf', 8 )
def UpdateInventory( game ):
    inventory = GameData.PlayerInventory
    selected = game.inventorySlot

    for i in range( min( inventory.inventorySize, game.hotbar.slotCount ) ):
        if i in inventory.inventory:
            def renderSlot( screen, pos ):
                item = inventory.inventory[i]
                if item[0].has( 'image' ):
                    img = GameData.TypeDefinitions['image'][item[0].image]
                    GameData.AtlasMap[ img.file ].render( img.key, screen, pos[0] + 2, pos[1] + 6 )

                render = RenderFont( fontInventoryCount, str( item[1] ), ( 255, 255, 255 ) )
                screen.blit( render, ( pos[0] + 6, pos[1] + 44 - render.get_height() ) )

            game.hotbar.updateSlot( i, renderSlot, 2 if i == selected else 1 )
        else:
            game.hotbar.updateSlot( i, None, 0 )

    #Update action window
    if selected == -1 or selected not in inventory.inventory:
        game.actionWindow.guiParts = []
    else:
        definition = inventory.inventory[selected][0]
        defName = definition.name

        game.actionWindow.guiParts = []
        count = 1

        def addButton( text, cb ):
            nonlocal count
            button = Window.Button( LoadFont( 'ButtonFont', '', '' ), text, ( 20, 30 * count ), ( 260, 25 ) )
            button.pressCallback = cb
            game.actionWindow.guiParts.append( button )

            count += 1


        # Combine button
        for recipeName in GameData.TypeDefinitions['recipe']:
            recipe = GameData.TypeDefinitions['recipe'][recipeName]
            if defName in recipe.items:

                addButton( 'Combine', lambda *_: ShowCombineButton( game ) )
                break

        # Action buttons
        if definition.has( 'use' ):
            uses = definition.use

            if isinstance( uses, str ):
                uses = ( uses,  )

            if 'throw' in uses:
                addButton( 'Throw (Click on target)', None )

            if 'drop' in uses:
                addButton( 'Drop explosive (E)', lambda *_: game.dropItem() )

        curCount = inventory.inventory[selected][1]
        if curCount < 99 and not ( inventory.inventory[selected][0].has( 'indestructible' ) and inventory.inventory[selected][0].indestructible ):
            addButton( 'Destroy item (1)', lambda *_: inventory.dropItem( selected, 1 ) )

            if curCount > 10:
                addButton( 'Destroy item (%d)' % int( curCount / 2 ), lambda *_: inventory.dropItem( selected, int( curCount / 2 ) ) )
            if curCount > 5:
                addButton( 'Destroy item (%d)' % curCount, lambda *_: inventory.dropItem( selected, curCount ) )
