import bpy
import pytest

import playback_ranges


def test_通常の再生範囲を返す(scene):
    assert playback_ranges.get_range(bpy.context) == (1, 10)


def test_プレビュー範囲が有効ならプレビュー範囲を返す(scene):
    scene.use_preview_range = True
    scene.frame_preview_start = 20
    scene.frame_preview_end = 30

    assert playback_ranges.get_range(bpy.context) == (20, 30)


def test_通常の再生範囲を更新する(scene):
    playback_ranges.set_range(bpy.context, 3, 7)

    assert (scene.frame_start, scene.frame_end) == (3, 7)


def test_プレビュー範囲が有効ならプレビュー範囲を更新する(scene):
    scene.use_preview_range = True

    playback_ranges.set_range(bpy.context, 3, 7)

    assert (scene.frame_preview_start, scene.frame_preview_end) == (3, 7)


def test_負のプレビューフレームを受け付ける(scene):
    scene.use_preview_range = True

    playback_ranges.set_range(bpy.context, -20, -5)

    assert (scene.frame_preview_start, scene.frame_preview_end) == (-20, -5)


def test_負の通常フレームはゼロにクランプする(scene):
    playback_ranges.set_range(bpy.context, -10, 5)

    assert (scene.frame_start, scene.frame_end) == (0, 5)


def test_ボタン文言に名前と範囲を含める(scene):
    item = scene.playback_ranges_items.add()
    item.name = "Action"
    item.start = 1
    item.end = 10

    assert item.get_button_text() == "Action: 1-10"


def test_名前がなければ範囲だけを表示する(scene):
    item = scene.playback_ranges_items.add()
    item.name = ""
    item.start = 1
    item.end = 10

    assert item.get_button_text() == "1-10"


def test_開始と終了が同じなら単一フレームを表示する(scene):
    item = scene.playback_ranges_items.add()
    item.name = ""
    item.start = 5
    item.end = 5

    assert item.get_button_text() == "5"


def test_追加は指定した範囲を保存する(scene):
    result = bpy.ops.playback_ranges.add("EXEC_DEFAULT", name="Test", start=1, end=10)

    assert result == {"FINISHED"}
    item = scene.playback_ranges_items[0]
    assert (item.name, item.start, item.end) == ("Test", 1, 10)


def test_追加は負のフレームを受け付ける(scene):
    result = bpy.ops.playback_ranges.add("EXEC_DEFAULT", name="Neg", start=-20, end=-5)

    assert result == {"FINISHED"}
    item = scene.playback_ranges_items[0]
    assert (item.start, item.end) == (-20, -5)


def test_追加は開始が終了より大きければ拒否する(scene):
    with pytest.raises(
        RuntimeError, match="End must be greater than or equal to Start!"
    ):
        bpy.ops.playback_ranges.add("EXEC_DEFAULT", name="Bad", start=10, end=1)

    assert len(scene.playback_ranges_items) == 0


def test_削除は項目を取り除く(scene):
    bpy.ops.playback_ranges.add("EXEC_DEFAULT", name="A", start=1, end=10)

    result = bpy.ops.playback_ranges.delete("EXEC_DEFAULT", index=0)

    assert result == {"FINISHED"}
    assert len(scene.playback_ranges_items) == 0


def test_削除は範囲外のインデックスを拒否する(scene):
    bpy.ops.playback_ranges.add("EXEC_DEFAULT", name="A", start=1, end=10)

    result = bpy.ops.playback_ranges.delete("EXEC_DEFAULT", index=5)

    assert result == {"CANCELLED"}
    assert len(scene.playback_ranges_items) == 1


def test_上移動は項目を上に動かす(scene):
    bpy.ops.playback_ranges.add("EXEC_DEFAULT", name="A", start=1, end=10)
    bpy.ops.playback_ranges.add("EXEC_DEFAULT", name="B", start=2, end=20)

    result = bpy.ops.playback_ranges.move_up("EXEC_DEFAULT", index=1)

    assert result == {"FINISHED"}
    assert [x.name for x in scene.playback_ranges_items] == ["B", "A"]


def test_上移動は先頭でキャンセルする(scene):
    bpy.ops.playback_ranges.add("EXEC_DEFAULT", name="A", start=1, end=10)

    result = bpy.ops.playback_ranges.move_up("EXEC_DEFAULT", index=0)

    assert result == {"CANCELLED"}


def test_下移動は項目を下に動かす(scene):
    bpy.ops.playback_ranges.add("EXEC_DEFAULT", name="A", start=1, end=10)
    bpy.ops.playback_ranges.add("EXEC_DEFAULT", name="B", start=2, end=20)

    result = bpy.ops.playback_ranges.move_down("EXEC_DEFAULT", index=0)

    assert result == {"FINISHED"}
    assert [x.name for x in scene.playback_ranges_items] == ["B", "A"]


def test_下移動は末尾でキャンセルする(scene):
    bpy.ops.playback_ranges.add("EXEC_DEFAULT", name="A", start=1, end=10)

    result = bpy.ops.playback_ranges.move_down("EXEC_DEFAULT", index=0)

    assert result == {"CANCELLED"}


def test_編集は項目を更新する(scene):
    bpy.ops.playback_ranges.add("EXEC_DEFAULT", name="A", start=1, end=10)

    result = bpy.ops.playback_ranges.edit_item(
        "EXEC_DEFAULT", index=0, name="B", start=2, end=20
    )

    assert result == {"FINISHED"}
    item = scene.playback_ranges_items[0]
    assert (item.name, item.start, item.end) == ("B", 2, 20)


def test_編集は範囲外のインデックスを拒否する(scene):
    bpy.ops.playback_ranges.add("EXEC_DEFAULT", name="A", start=1, end=10)

    result = bpy.ops.playback_ranges.edit_item(
        "EXEC_DEFAULT", index=5, name="B", start=2, end=20
    )

    assert result == {"CANCELLED"}


def test_編集は開始が終了より大きければ拒否する(scene):
    bpy.ops.playback_ranges.add("EXEC_DEFAULT", name="A", start=1, end=10)

    with pytest.raises(
        RuntimeError, match="End must be greater than or equal to Start!"
    ):
        bpy.ops.playback_ranges.edit_item(
            "EXEC_DEFAULT", index=0, name="B", start=20, end=2
        )

    item = scene.playback_ranges_items[0]
    assert (item.name, item.start, item.end) == ("A", 1, 10)


def test_範囲設定は負のプレビュー範囲を設定する(scene):
    scene.use_preview_range = True

    result = bpy.ops.playback_ranges.set_range("EXEC_DEFAULT", start=-40, end=-15)

    assert result == {"FINISHED"}
    assert (scene.frame_preview_start, scene.frame_preview_end) == (-40, -15)


def test_範囲設定は明示的な値がなければキャンセルする(scene):
    result = bpy.ops.playback_ranges.set_range("EXEC_DEFAULT")

    assert result == {"CANCELLED"}
