import libtcodpy as libtcod
import random

from GameComponents import *

class ActionSystem():
    def __init__( self, world, actions ):
        self.toProcessList = []
        self.world = world
        self.actions = actions
        self.curTurn = 0

    def clean( self ):
        self.toProcessList = []

    def updateProcessList( self ):
        entities = self.world.getEntityByComponent( TurnTaker )
        self.toProcessList = []

        for ent in entities:
            turnTaker = ent.getComponent( TurnTaker )

            if not hasattr( ent, '_nextTurn' ):
                ent._nextTurn = turnTaker.timeTillNextTurn + self.curTurn
            if not hasattr( turnTaker, 'firstTurn' ):
                ent.firstTurn = self.curTurn

            self._insertEnt( ent )

    def _insertEnt( self, ent ):
        tp = self.toProcessList
        if ent in self.toProcessList:
            tp.pop( tp.index( ent ) )
        
        begin = 0
        end = len( tp ) - 1
        listEnd = len( tp )

        key = ent._nextTurn

        if listEnd == 0:
            tp.append( ent )
            return

        while end >= begin:
            mid = begin + ( ( end - begin ) // 2 )

            comp = tp[ mid ]._nextTurn

            if comp > key:
                begin = mid + 1
            elif comp < key:
                end = mid - 1
            else:
                break

        #Key not found, check if to insert before or after the current index
        if comp > key:
            tp.insert( mid + 1, ent )
        else:
            tp.insert( mid, ent )


    def process( self, maxTime ):
        if len( self.toProcessList ) == 0:
            self.updateProcessList()
            if len( self.toProcessList ) == 0:
                print( 'No entities to take actions' )
                return False

        firstEnt = self.toProcessList.pop()
        turnTaker = firstEnt.getComponent( TurnTaker )

        #if self.curTurn + maxTime < firstEnt._nextTurn:
        #    self.curTurn += maxTime
        #    self._insertEnt( firstEnt )
        #    return True

        action = turnTaker.getNextTurn( self.curTurn )
        if action is None:
            self._insertEnt( firstEnt )
            return False

        restTime = self.actions[ action.name ]( action.name, self, action.entity, action.params )
        if restTime is None:
            self._insertEnt( firstEnt )
            return False

        if restTime == 1:
            turnTaker.wasBlocked += 1
        else:
            turnTaker.wasBlocked = 0

        assert( restTime > 0 )
        randExtra = random.randrange( -turnTaker.randomRange, turnTaker.randomRange+1 )

        self.curTurn = firstEnt._nextTurn
        firstEnt._nextTurn = self.curTurn + restTime + randExtra
        self._insertEnt( firstEnt )

        return True
