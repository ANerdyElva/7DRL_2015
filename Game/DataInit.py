import json
import GameData

_incomplete = []
_definitions = {}

def Load( fileName ):
    global _incomplete
    global _definitions

    jsonFile = open( fileName, 'r' )
    jsonDump = json.load( jsonFile )
    jsonFile.close()

    for definition in jsonDump:
        if 'type' not in definition or 'name' not in definition:
            print( 'Incomplete JSON definition:' )
            print( definition )
            continue

        if definition['type'] is None:
            _definitions[definition['name']] = definition
        else:
            _incomplete.append( definition )

def merge( base, new ):
    ret = dict( base )

    for key in new:
        if key.endswith( '_clear' ):
            del ret[ key[:-6] ]

    for key in new:
        val = new[ key ]

        if key not in ret:
            ret[key] = val
        else:
            oldVal = ret[ key ]

            if oldVal is None:
                ret[key] = val
            elif isinstance( val, dict ):
                ret[key] = merge( oldVal, val )
            elif isinstance( val, list ):
                ret[key] = oldVal + val
            else:
                ret[key] = val

    return ret

class Data:
    def __init__( self, val ):
        self.__data = val

    def __getattr__( self, key ):
        keys = key.split('.')
        ret = self.__data

        for n in keys:
            ret = ret[n]

        return ret

    def __str__( self ):
        return str( self.__data )

    def __repr__( self ):
        return repr( self.__data )

def Finalize():
    global _definitions
    global _incomplete

    _newIncomplete = []

    while len( _incomplete ) > 0:
        for definition in _incomplete:
            if definition['type'] in _definitions:
                finalized = merge( _definitions[ definition['type'] ], definition )

                if 'baseType' not in finalized:
                    finalized['baseType'] = [ definition['type'] ]
                else:
                    finalized['baseType'] += ( definition['type'], )

                _definitions[ finalized[ 'name' ] ] = finalized
            else:
                _newIncomplete.append( definition )

        if len( _newIncomplete ) == len( _incomplete ):
            raise Exception( 'Incomplete JSON data. Can\'t find type for:\n' + repr( _newIncomplete ) )

        _incomplete = _newIncomplete

    for n in _definitions:
        definition = _definitions[ n ]

        if 'baseType' not in definition:
            continue

        for base in definition['baseType']:
            if base not in GameData.TypeDefinitions:
                GameData.TypeDefinitions[base] = {}

            GameData.TypeDefinitions[base][definition['name']] = Data( definition )
