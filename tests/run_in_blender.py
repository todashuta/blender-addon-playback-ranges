"""Blender の内蔵 Python で pytest を実行する。

Blender は PYTHONPATH を無視するため、プロジェクトの .venv にある pytest を
sys.path に直接追加してから読み込む。
"""

import os
import sys
from pathlib import Path

site_packages = os.environ.get("PLAYBACK_RANGES_SITE_PACKAGES")
if not site_packages:
    raise SystemExit("PLAYBACK_RANGES_SITE_PACKAGES is not set")

sys.path.insert(0, site_packages)

import pytest

tests_dir = Path(__file__).resolve().parent
raise SystemExit(pytest.main([str(tests_dir), "-v"]))
