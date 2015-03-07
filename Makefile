tiles.png: tiles/tiles.txt
	montage -background '#FF00FF' -geometry +0+0 -tile 8x `cat tiles/tiles.txt`  tiles.png
