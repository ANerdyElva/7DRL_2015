tiles.png: tiles/tiles.txt
	montage -background none -geometry +0+0 -tile 8x `cat tiles/tiles.txt`  tiles.png
