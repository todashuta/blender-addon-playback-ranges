BLENDER_EXE ?= "/Applications/Blender/Blender 4.5 LTS.app/Contents/MacOS/Blender"
SITE_PACKAGES = $(shell uv run python -c "import site; print(site.getsitepackages()[0])")
file ?=

.PHONY: help build validate test

help:
	@echo "Usage:"
	@echo "  make build"
	@echo "  make validate"
	@echo "  make validate file=add-on-package.zip"
	@echo "  make test"

build:
	$(BLENDER_EXE) --command extension build

validate:
	$(BLENDER_EXE) --command extension validate $(file)

test:
	PLAYBACK_RANGES_SITE_PACKAGES="$(SITE_PACKAGES)" $(BLENDER_EXE) --background --factory-startup --python ../../tests/run_in_blender.py
