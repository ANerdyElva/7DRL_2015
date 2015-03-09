TILE_SOURCES=$(wildcard tiles/*.txt)
TILE_DEST=$(patsubst tiles/%.txt,data/%.png,$(TILE_SOURCES))

all: $(TILE_DEST)

data/%.png: tiles/%.txt
	montage -background none -geometry +0+0 -tile 8x `cat $<` $@

release: Release

Release: all
	rm -rvf Release
	mkdir Release

	cp -rv Game Windows Release
	cp -v README.md LICENSE Release

	cp -rv data Release

	cp -v Launcher.sh Release

	$(MAKE) Release/Linux32

TestRelease: Release
	cd Release && ./Launcher.sh

Linux32: BuildLinux.sh
	rm -rfv Linux32/pygame*
	cd Linux32 && ../BuildLinux.sh

Release/Linux32: Linux32
	mkdir Release/Linux32
	cp Linux32/pygame Release/Linux32 -rv
	cp Linux32/libtcod/* Release/Linux32 -rv
