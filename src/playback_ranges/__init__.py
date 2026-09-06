# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


import bpy
from bpy.types import (
    AddonPreferences,
    Context,
    Event,
    Operator,
    OperatorProperties,
    Panel,
    PropertyGroup,
    Scene,
    UILayout,
    WindowManager,
)
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    IntProperty,
    StringProperty,
)


def get_range() -> tuple[int, int]:
    scene: Scene = bpy.context.scene # type: ignore
    if scene.use_preview_range:
        return (scene.frame_preview_start, scene.frame_preview_end)
    return (scene.frame_start, scene.frame_end)


def set_range(start: int, end: int):
    scene: Scene = bpy.context.scene # type: ignore
    if scene.use_preview_range:
        scene.frame_preview_start = start
        scene.frame_preview_end = end
    else:
        scene.frame_start = start
        scene.frame_end = end


from pathlib import Path
LOCAL_HELP_PATH = Path(__file__).resolve().parent / "docs" / "index.html"


class PLAYBACK_RANGES_PT_panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    #bl_category = "Animation"
    bl_label = "Playback Ranges"

    @classmethod
    def poll(cls, context: Context) -> bool:
        return True

    def draw_header(self, context: Context):
        #preferences = context.preferences.addons[__name__].preferences
        layout = self.layout
        #if preferences.show_help_button:
        #layout.operator(PLAYBACK_RANGES_OT_open_offline_help.bl_idname, icon="HELP", text="")

    def draw(self, context: Context):
        scene: Scene = context.scene # type: ignore
        layout: UILayout = self.layout # type: ignore

        layout.operator(PLAYBACK_RANGES_OT_add.bl_idname, icon="ADD")

        current_range = get_range()
        for idx,x in enumerate(scene.playback_ranges_items): # type: ignore
            split = layout.split(align=True, factor=0.7)
            depress = (x.start, x.end) == current_range
            op = split.operator(PLAYBACK_RANGES_OT_set_range.bl_idname, text=x.get_button_text(), depress=depress)
            op.start = x.start
            op.end   = x.end
            op = split.operator(PLAYBACK_RANGES_OT_edit_item.bl_idname, text="", icon="GREASEPENCIL")
            op.index = idx
            op = split.operator(PLAYBACK_RANGES_OT_move_up.bl_idname, text="", icon="TRIA_UP")
            op.index = idx
            op = split.operator(PLAYBACK_RANGES_OT_move_down.bl_idname, text="", icon="TRIA_DOWN")
            op.index = idx
            op = split.operator(PLAYBACK_RANGES_OT_delete.bl_idname, text="", icon="TRASH")
            op.index = idx


class PLAYBACK_RANGES_OT_add(Operator):
    bl_idname = "playback_ranges.add"
    bl_label = "Add Playback Range"
    bl_description = "Add Playback Range"
    bl_options = {"UNDO"}

    name:  StringProperty(name="Name", default="Action")  # type: ignore
    start: IntProperty(name="Start", default=0, min=0)  # type: ignore
    end:   IntProperty(name="End", default=0, min=0)  # type: ignore

    @classmethod
    def poll(cls, context: Context) -> bool:
        return True

    def execute(self, context: Context):
        if self.start > self.end:
            self.report({"ERROR_INVALID_INPUT"}, "End must be grater than or equal to Start!")
            return {"CANCELLED"}

        scene: Scene = context.scene # type: ignore
        item = scene.playback_ranges_items.add() # type: ignore
        item.name  = self.name
        item.start = self.start
        item.end   = self.end

        if context.area:
            context.area.tag_redraw()

        return {"FINISHED"}

    def invoke(self, context: Context, event: Event):
        self.start, self.end = get_range()
        wm: WindowManager = context.window_manager # type: ignore
        return wm.invoke_props_dialog(self, width=200)

    def draw(self, context: Context):
        layout: UILayout = self.layout # type: ignore
        row = layout.row(align=True)
        row.alert = self.start > self.end
        row.prop(self, "start")
        row.prop(self, "end")
        #layout.label(text=f"Range: {self.start}-{self.end}")
        layout.prop(self, "name")


class PLAYBACK_RANGES_OT_delete(Operator):
    bl_idname = "playback_ranges.delete"
    bl_label = "Delete Playback Range"
    bl_description = "Delete Playback Range"
    bl_options = {"UNDO"}

    index: IntProperty(name="Index")  # type: ignore

    @classmethod
    def poll(cls, context: Context) -> bool:
        return True

    def execute(self, context: Context):
        scene: Scene = context.scene # type: ignore
        scene.playback_ranges_items.remove(self.index) # type: ignore

        return {"FINISHED"}

    def invoke(self, context: Context, event: Event):
        wm: WindowManager = context.window_manager # type: ignore
        return wm.invoke_confirm(self, event)


class PLAYBACK_RANGES_OT_move_up(Operator):
    bl_idname = "playback_ranges.move_up"
    bl_label = "Move Up"
    bl_description = ""
    bl_options = {"UNDO"}

    shift_key_down = False

    index: IntProperty(name="Index")  # type: ignore

    @classmethod
    def poll(cls, context: Context) -> bool:
        return True

    def execute(self, context: Context):
        scene: Scene = context.scene # type: ignore
        if self.shift_key_down:
            scene.playback_ranges_items.move(self.index, 0) # type: ignore
        else:
            scene.playback_ranges_items.move(self.index, self.index-1) # type: ignore

        return {"FINISHED"}

    def invoke(self, context: Context, event: Event):
        self.shift_key_down = event.shift
        return self.execute(context)


class PLAYBACK_RANGES_OT_move_down(Operator):
    bl_idname = "playback_ranges.move_down"
    bl_label = "Move Down"
    bl_description = ""
    bl_options = {"UNDO"}

    shift_key_down = False

    index: IntProperty(name="Index")  # type: ignore

    @classmethod
    def poll(cls, context: Context) -> bool:
        return True

    def execute(self, context: Context):
        scene: Scene = context.scene # type: ignore
        if self.shift_key_down:
            scene.playback_ranges_items.move(self.index, len(scene.playback_ranges_items)-1) # type: ignore
        else:
            scene.playback_ranges_items.move(self.index, self.index+1) # type: ignore

        return {"FINISHED"}

    def invoke(self, context: Context, event: Event):
        self.shift_key_down = event.shift
        return self.execute(context)


class PLAYBACK_RANGES_OT_edit_item(Operator):
    bl_idname = "playback_ranges.edit_item"
    bl_label = "Edit"
    bl_description = ""
    bl_options = {"UNDO"}

    shift_key_down = False

    index: IntProperty(name="Index", options={"HIDDEN"})  # type: ignore

    name:  StringProperty(name="Name")  # type: ignore
    start: IntProperty(name="Start", min=0)  # type: ignore
    end:   IntProperty(name="End", min=0)  # type: ignore

    @classmethod
    def poll(cls, context: Context) -> bool:
        return True

    def execute(self, context: Context):
        if self.start > self.end:
            self.report({"ERROR_INVALID_INPUT"}, "End must be grater than or equal to Start!")
            return {"CANCELLED"}

        scene: Scene = context.scene # type: ignore
        item = scene.playback_ranges_items[self.index] # type: ignore
        item.name = self.name
        item.start = self.start
        item.end = self.end

        if context.area:
            context.area.tag_redraw()

        return {"FINISHED"}

    def invoke(self, context: Context, event: Event):
        self.shift_key_down = event.shift

        scene: Scene = context.scene # type: ignore
        item = scene.playback_ranges_items[self.index] # type: ignore
        self.name  = item.name
        self.start = item.start
        self.end   = item.end
        wm: WindowManager = context.window_manager # type: ignore
        return wm.invoke_props_dialog(self, width=200)

    def draw(self, context: Context):
        layout: UILayout = self.layout # type: ignore
        row = layout.row(align=True)
        row.alert = self.start > self.end
        row.prop(self, "start")
        row.prop(self, "end")
        layout.prop(self, "name")


class PLAYBACK_RANGES_OT_set_range(Operator):
    bl_idname = "playback_ranges.set_range"
    bl_label = "Set Playback Range"
    bl_description = "Set Playback Range"
    bl_options = {"UNDO"}

    shift_key_down = False

    start: IntProperty(name="Start", default=-1)  # type: ignore
    end:   IntProperty(name="End", default=-1)  # type: ignore

    @classmethod
    def poll(cls, context: Context) -> bool:
        return True

    def execute(self, context: Context):
        if self.start < 0 or self.end < 0:
            return {"CANCELLED"}

        scene: Scene = context.scene # type: ignore
        set_range(self.start, self.end)

        if self.shift_key_down:
            scene.frame_current = self.start

        return {"FINISHED"}

    def invoke(self, context: Context, event: Event):
        self.shift_key_down = event.shift
        return self.execute(context)


class PLAYBACK_RANGES_OT_open_offline_help(Operator):
    bl_idname = "playback_ranges.open_offline_help"
    bl_label = "Open Offline Help"
    bl_description = "Playback Ranges: Open Offline Help"
    bl_options = {"INTERNAL"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        return True

    @classmethod
    def description(cls, context: Context, properties: OperatorProperties):
        return f"Open Offline Help.\n{LOCAL_HELP_PATH}"

    def execute(self, context: Context):
        return bpy.ops.wm.url_open(url=LOCAL_HELP_PATH.as_uri())

    def invoke(self, context: Context, event: Event):
        wm: WindowManager = context.window_manager # type: ignore
        return wm.invoke_confirm(self, event)


class PlaybackRangeItem(PropertyGroup):
    name:  StringProperty(name="Name", default="")  # type: ignore
    start: IntProperty(name="Start", default=0, min=0)  # type: ignore
    end:   IntProperty(name="End", default=0, min=0)  # type: ignore

    def get_button_text(self) -> str:
        s = ""
        if self.name != "":
            s = f"{self.name}: "
        if self.start == self.end:
            s += str(self.start)
        else:
            s += f"{self.start}-{self.end}"
        return s


class PLAYBACK_RANGES_Preferences(AddonPreferences):
    bl_idname = __name__

    #show_help_button: BoolProperty(name="Show Help Button on Panel Header", default=True)  # type: ignore

    def draw(self, context: Context):
        layout = self.layout
        #layout.prop(self, "show_help_button")
        layout.label(text="Location: 3D View > Side Bar > Misc > Playback Ranges")


classes = (
        PLAYBACK_RANGES_PT_panel,
        PLAYBACK_RANGES_OT_set_range,
        PLAYBACK_RANGES_OT_add,
        PLAYBACK_RANGES_OT_delete,
        PLAYBACK_RANGES_OT_move_up,
        PLAYBACK_RANGES_OT_move_down,
        PLAYBACK_RANGES_OT_edit_item,

        PLAYBACK_RANGES_OT_open_offline_help,

        PlaybackRangeItem,

        PLAYBACK_RANGES_Preferences,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    Scene.playback_ranges_items = CollectionProperty(type=PlaybackRangeItem) # type: ignore


def unregister():
    if hasattr(Scene, "playback_ranges_items"):
        del Scene.playback_ranges_items

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
