BLENDER_EXE = "/Applications/Blender/Blender 4.2 LTS.app/Contents/MacOS/Blender"
file ?=

.PHONY: help build validate

help:
	@echo "Usage:"
	@echo "  make build"
	@echo "  make validate"
	@echo "  make validate file=add-on-package.zip"

build:
	$(BLENDER_EXE) --command extension build

validate:
	$(BLENDER_EXE) --command extension validate $(file)
