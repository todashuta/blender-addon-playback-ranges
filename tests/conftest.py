import bpy
import pytest

import playback_ranges


@pytest.fixture(autouse=True)
def registered_addon():
    playback_ranges.register()
    yield
    playback_ranges.unregister()


@pytest.fixture
def scene():
    scene = bpy.context.scene
    scene.playback_ranges_items.clear()
    scene.use_preview_range = False
    scene.frame_start = 1
    scene.frame_end = 10
    yield scene
