Playback Ranges Addon
=====================

https://todashuta.github.io/blender-addon-playback-ranges/

Generate Docs
-------------

```
cd docs_src
uv run .\make.bat html
```

Test
----

`uv sync` で依存を入れてから、Blender の実行ファイルを指定して実行します。

```
cd src/playback_ranges
make test BLENDER_EXE=/path/to/blender
```

Windows では `make.cmd test` を使います。
