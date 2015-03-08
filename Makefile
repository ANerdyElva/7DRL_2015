TILE_SOURCES=$(wildcard tiles/*.txt)
TILE_DEST=$(patsubst tiles/%.txt,data/%.png,$(TILE_SOURCES))

all: $(TILE_DEST)
	echo $(TILE_SOURCES)

data/%.png: tiles/%.txt
	montage -background none -geometry +0+0 -tile 8x `cat $<` $@
