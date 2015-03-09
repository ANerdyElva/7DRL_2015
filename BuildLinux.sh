###############
# pygame
###############
# Grab source
hg clone https://bitbucket.org/pygame/pygame pygame_src

# Finally build and install
cd pygame_src
python3 setup.py build
cd ..

rm -rvf pygame
mkdir pygame
cp pygame_src/build/lib.linux-*/pygame . -rv
