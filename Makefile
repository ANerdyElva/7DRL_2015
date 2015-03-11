TILE_SOURCES=$(wildcard tiles/*.txt)
TILE_DEST=$(patsubst tiles/%.txt,data/%.png,$(TILE_SOURCES))

all: $(TILE_DEST)

data/%.png: tiles/%.txt
	montage -background none -geometry +0+0 -tile 8x `cat $<` $@

release: Release

Release: all
	rm -rf Release
	mkdir Release

	cp -r Game Release
	cp -v README.md LICENSE Release

	cp -r data Release
	cp -r gui Release

	cp Launcher.sh Launcher.bat Release

ifeq ($(OS),Windows_NT)
	$(MAKE) Release/Windows
else

ifeq ($(shell uname -m),x86_64)
	$(MAKE) Release/Linux64
else
	$(MAKE) Release/Linux32
endif

endif


TestRelease: Release
ifeq ($(OS),Windows_NT)
	cd Release && ./Launcher.bat
else
	cd Release && ./Launcher.sh
endif

Linux64: BuildLinux.sh
	rm -rfv Linux64/pygame*
	cd Linux64 && ../BuildLinux.sh

Linux32: BuildLinux.sh
	rm -rfv Linux32/pygame*
	cd Linux32 && ../BuildLinux.sh

Release/Windows: dist
	mkdir Release/Windows
	cp Windows/*dll Release/Windows
	cp dist/* Release/Windows

Release/Linux64: Linux64
	mkdir Release/Linux64
	cp Linux64/pygame Release/Linux64 -r
	cp Linux64/libtcod/* Release/Linux64 -r

Release/Linux32: Linux32
	mkdir Release/Linux32
	cp Linux32/pygame Release/Linux32 -r
	cp Linux32/libtcod/* Release/Linux32 -r

dist_src:
	rm -rf dist_src
	mkdir dist_src
	cp Windows/* dist_src/ -vr
	cp Game/* dist_src/ -vr

dist: all dist_src
	rm -rf dist/*

	( cd dist_src && python -m py2exe init.py -d ../dist -c -O  )


