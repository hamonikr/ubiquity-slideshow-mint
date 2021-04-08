# Makefile for ubiquity-slideshow-mint

SOURCE=.
BUILD=$(SOURCE)/build
SOURCESLIDES=$(SOURCE)/slideshows

all: clean build_mint translations

build_init:
	mkdir -p $(BUILD)

build_mint: build_init
	cp -rL $(SOURCESLIDES)/mint $(BUILD)

translations:
	# python generate-local-slides.py mint
	python3 generate-local-slides.py mint

.PHONY : clean

clean:
	-rm -rf $(BUILD)
