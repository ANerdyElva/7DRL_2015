import GameData

__Base = {
        'baseHealth': 0,

        'randomRange': 0,

         'spawnFrequency': {},
        }

def __combine( first, second ):
    ret = dict( first )

    for n in second:
        ret[ n ] = second[ n ]

    return ret

SpawnList = {}

def __registerSpawnable( en ):
    spawnFrequency = en['spawnFrequency']
    for n in spawnFrequency:
        if n not in SpawnList:
            SpawnList[n] = []

        for i in range( spawnFrequency[n] ):
            SpawnList[n].append( en )
    return en

Player = __combine( __Base, {
        'baseHealth': 20,
        'movementSpeed': 10,
        'spriteAtlas': GameData.Entities,
        'spriteId': 'player',
        } )

Enemy = __registerSpawnable( __combine( __Base, {
        'baseHealth': 5,
        'movementSpeed': 5,

        'spriteAtlas': GameData.Entities,
        'spriteId': 'player',

        'randomRange': 10,

        'spawnFrequency': {
            'normal': 2,
            },
    } ) )
