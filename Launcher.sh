#!/bin/bash
PYTHONPATH="Game"

KERNEL_VERSION=`uname -m`

if [ "$KERNEL_VERSION" == "i686" ]; then
	PYTHONPATH="$PYTHONPATH:Linux32"
elif [ "$KERNEL_VERSION" == "x86_64" ]; then
	PYTHONPATH="$PYTHONPATH:Linux64"
else
	echo "Unknown kernel version! Hoping for the best with i686 (Sorry!)."
	PYTHONPATH="$PYTHONPATH:Linux32"
fi

echo Launching with Python Path \"$PYTHONPATH\"

export PYTHONPATH
python3.4 Game/init.py -OO
