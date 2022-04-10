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


bl_info = {
    "name": "Playback Ranges",
    "author": "todashuta",
    "version": (1, 0, 1),
    "blender": (2, 83, 0),
    "location": "3D View > Side Bar > Misc > Playback Ranges",
    "description": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Animation"
}


import bpy


class PLAYBACK_RANGES_PT_panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    #bl_category = "Animation"
    bl_label = "Playback Ranges"

    @classmethod
    def poll(cls, context) -> bool:
        return True

    def draw(self, context):
        scene = context.scene
        layout = self.layout

        layout.operator(PLAYBACK_RANGES_OT_add.bl_idname, icon="ADD")

        for idx,x in enumerate(scene.playback_ranges_items):
            split = layout.split(align=True, factor=0.7)
            icon = "BLANK1"
            if scene.use_preview_range:
                if x.start == scene.frame_preview_start and x.end == scene.frame_preview_end:
                    #split.alert = True
                    icon = "CHECKMARK"
            else:
                if x.start == scene.frame_start and x.end == scene.frame_end:
                    #split.alert = True
                    icon = "CHECKMARK"
            name = "" if x.name == "" else f"{x.name}: "
            text = name + (str(x.start) if x.start == x.end else f"{x.start}-{x.end}")
            op = split.operator(PLAYBACK_RANGES_OT_set_range.bl_idname, text=text, icon=icon)
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


class PLAYBACK_RANGES_OT_add(bpy.types.Operator):
    bl_idname = "playback_ranges.add"
    bl_label = "Add Playback Range"
    bl_description = "Add Playback Range"

    name:  bpy.props.StringProperty(name="Name", default="Action")  # type: ignore
    start: bpy.props.IntProperty(name="Start", default=0, options={"HIDDEN"})  # type: ignore
    end:   bpy.props.IntProperty(name="End", default=0, options={"HIDDEN"})  # type: ignore

    @classmethod
    def poll(cls, context) -> bool:
        return True

    def execute(self, context):
        scene = context.scene
        item = scene.playback_ranges_items.add()
        item.name  = self.name
        item.start = self.start
        item.end   = self.end

        if context.area:
            context.area.tag_redraw()

        return {"FINISHED"}

    def invoke(self, context, event):
        scene = context.scene
        if scene.use_preview_range:
            self.start = scene.frame_preview_start
            self.end   = scene.frame_preview_end
        else:
            self.start = scene.frame_start
            self.end   = scene.frame_end
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        #row = layout.row()
        #row.prop(self, "start")
        #row.prop(self, "end")
        #row.enabled = False
        layout.label(text=f"Range: {self.start}-{self.end}")
        layout.prop(self, "name")


class PLAYBACK_RANGES_OT_delete(bpy.types.Operator):
    bl_idname = "playback_ranges.delete"
    bl_label = "Delete Playback Range"
    bl_description = "Delete Playback Range"

    index: bpy.props.IntProperty(name="Index")  # type: ignore

    @classmethod
    def poll(cls, context) -> bool:
        return True

    def execute(self, context):
        scene = context.scene
        scene.playback_ranges_items.remove(self.index)

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)


class PLAYBACK_RANGES_OT_move_up(bpy.types.Operator):
    bl_idname = "playback_ranges.move_up"
    bl_label = "Move Up"
    bl_description = ""

    shift_key_down = False

    index: bpy.props.IntProperty(name="Index")  # type: ignore

    @classmethod
    def poll(cls, context) -> bool:
        return True

    def execute(self, context):
        scene = context.scene
        if self.shift_key_down:
            scene.playback_ranges_items.move(self.index, 0)
        else:
            scene.playback_ranges_items.move(self.index, self.index-1)

        return {"FINISHED"}

    def invoke(self, context, event):
        self.shift_key_down = event.shift
        return self.execute(context)


class PLAYBACK_RANGES_OT_move_down(bpy.types.Operator):
    bl_idname = "playback_ranges.move_down"
    bl_label = "Move Down"
    bl_description = ""

    shift_key_down = False

    index: bpy.props.IntProperty(name="Index")  # type: ignore

    @classmethod
    def poll(cls, context) -> bool:
        return True

    def execute(self, context):
        scene = context.scene
        if self.shift_key_down:
            scene.playback_ranges_items.move(self.index, len(scene.playback_ranges_items)-1)
        else:
            scene.playback_ranges_items.move(self.index, self.index+1)

        return {"FINISHED"}

    def invoke(self, context, event):
        self.shift_key_down = event.shift
        return self.execute(context)


class PLAYBACK_RANGES_OT_edit_item(bpy.types.Operator):
    bl_idname = "playback_ranges.edit_item"
    bl_label = "Edit"
    bl_description = ""

    shift_key_down = False

    index: bpy.props.IntProperty(name="Index", options={"HIDDEN"})  # type: ignore

    name:  bpy.props.StringProperty(name="Name")  # type: ignore
    start: bpy.props.IntProperty(name="Start", min=0)  # type: ignore
    end:   bpy.props.IntProperty(name="End", min=0)  # type: ignore

    @classmethod
    def poll(cls, context) -> bool:
        return True

    def execute(self, context):
        scene = context.scene
        item = scene.playback_ranges_items[self.index]
        item.name = self.name
        item.start = self.start
        item.end = self.end

        if context.area:
            context.area.tag_redraw()

        return {"FINISHED"}

    def invoke(self, context, event):
        self.shift_key_down = event.shift

        scene = context.scene
        item = scene.playback_ranges_items[self.index]
        self.name  = item.name
        self.start = item.start
        self.end   = item.end
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "name")
        if self.shift_key_down:
            row = layout.row()
            row.prop(self, "start")
            row.prop(self, "end")


class PLAYBACK_RANGES_OT_set_range(bpy.types.Operator):
    bl_idname = "playback_ranges.set_range"
    bl_label = "Set Playback Range"
    bl_description = "Set Playback Range"

    shift_key_down = False

    start: bpy.props.IntProperty(name="Start", default=-1)  # type: ignore
    end:   bpy.props.IntProperty(name="End", default=-1)  # type: ignore

    @classmethod
    def poll(cls, context) -> bool:
        return True

    def execute(self, context):
        if self.start < 0 or self.end < 0:
            return {"CANCELLED"}

        scene = context.scene
        if scene.use_preview_range:
            scene.frame_preview_start = self.start
            scene.frame_preview_end   = self.end
        else:
            scene.frame_start = self.start
            scene.frame_end   = self.end

        if self.shift_key_down:
            scene.frame_current = self.start

        return {"FINISHED"}

    def invoke(self, context, event):
        self.shift_key_down = event.shift
        return self.execute(context)


class PlaybackRangeItem(bpy.types.PropertyGroup):
    name:  bpy.props.StringProperty(name="Name", default="")  # type: ignore
    start: bpy.props.IntProperty(name="Start", default=0, min=0)  # type: ignore
    end:   bpy.props.IntProperty(name="End", default=0, min=0)  # type: ignore


classes = (
        PLAYBACK_RANGES_PT_panel,
        PLAYBACK_RANGES_OT_set_range,
        PLAYBACK_RANGES_OT_add,
        PLAYBACK_RANGES_OT_delete,
        PLAYBACK_RANGES_OT_move_up,
        PLAYBACK_RANGES_OT_move_down,
        PLAYBACK_RANGES_OT_edit_item,

        PlaybackRangeItem,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.playback_ranges_items = bpy.props.CollectionProperty(type=PlaybackRangeItem)


def unregister():
    if hasattr(bpy.types.Scene, "playback_ranges_items"):
        del bpy.types.Scene.playback_ranges_items

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
