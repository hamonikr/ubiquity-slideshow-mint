#!/bin/bash

TITLE="Slideshow tester"

SOURCE=.
BUILD=$SOURCE/build
SOURCESLIDES=$SOURCE/slideshows

slideshow=mint
mv "$BUILD" "$BUILD.backup" 2>/dev/null
trap "[ -e "$BUILD.backup" ] && rm -rf "$BUILD" ; mv "$BUILD.backup" "$BUILD"" 0 1 2 15
make build_$slideshow | tee | zenity --progress --pulsate --title="$TITLE" --text="Building temporary slideshow for testing.\n<i>(make build_$slideshow)</i>" --auto-close
./Slideshow.py --path="$BUILD/$slideshow" --controls
