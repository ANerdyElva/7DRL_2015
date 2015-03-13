from ECS import Components

import GameComponents
import ECS

import math
import Math2D

import GameData

MOVE_LENGTH = 100
MIN_TURN_LENGTH = 1

defaultCharacter = None

def _sqrt( i ):
    if i == 2:
        return 1.41421356237
    elif i == 1:
        return 1
    else:
        return math.sqrt( i )

def _getChar( ent ):
    ret = ent.getComponent( GameComponents.Character )

    if ret is not None:
        return ret
    else:
        if defaultCharacter is None:
            defaultCharacter = GameComponents.Character( GameData.TypeDefinitions['']['enemy_base'] )

        return defaultCharacter

def Move( actionName, actionSystem, ent, params ):
    diff = _sqrt( params[ 0 ] ** 2 + params[ 1 ] ** 2 )

    pos = ent.getComponent( Components.Position )
    newPos = ( pos.x + params[ 0 ], pos.y + params[ 1 ] )

    if not GameData.Map.isPassable( *newPos ):
        return MIN_TURN_LENGTH

    entsAtPos = actionSystem.world.getEntitiesAtPos( Math2D.Point( newPos[0], newPos[1] ) )
    entsAtPos = list( [ n for n in entsAtPos if n != ent and n.passable == False ] )
    if len( entsAtPos ) > 0:
        return MIN_TURN_LENGTH

    pos.x += params[ 0 ]
    pos.y += params[ 1 ]

    char = _getChar( ent )
    return diff * char.attributes[ 'movementSpeed' ] * 10

def Sleep( actionName, actionSystem, ent, params ):
    return params

def Attack( actionName, actionSystem, ent, target ):
    selfChar = ent.getComponent( GameComponents.Character )
    targetChar = target.getComponent( GameComponents.Character )

    targetChar.takeDamage( selfChar.definition.damage )
    if targetChar.attributes[ 'Health' ] <= 0:
        ent.getComponent( GameComponents.TurnTaker ).target = None

    return selfChar.definition.damageRest

def ThrowEntity( actionName, actionSystem, ent, params ):
    droppedEnt = params[0]
    dropPos = params[1]

    droppedEnt.addComponent( ECS.Components.Position( *dropPos ) )

    actionSystem.world.addEntity( droppedEnt )

    return 20

def DropEntity( actionName, actionSystem, ent, droppedEnt ):
    pos = ent.getComponent( ECS.Components.Position )
    droppedEnt.addComponent( ECS.Components.Position( pos.x, pos.y ) )

    actionSystem.world.addEntity( droppedEnt )

    return 20

def Explode( actionName, actionSystem, ent, params ):
    return ent.getComponent( GameComponents.Explosive ).doFire()

def FindEnemy( actionName, actionSystem, ent, turnTaker ):
    #TODO Make this smarter? Maybe, who knows
    turnTaker.target = GameData.Player


ActionMap = {}
ActionMap[ 'move' ] = Move
ActionMap[ 'sleep' ] = Sleep
ActionMap[ 'attack' ] = Attack
ActionMap[ 'findEnemy' ] = FindEnemy

ActionMap[ 'dropEntity' ] = DropEntity
ActionMap[ 'throwEntity' ] = ThrowEntity

ActionMap[ 'explode' ] = Explode
