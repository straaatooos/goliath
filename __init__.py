# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "Goliath",
    "author": "jhu",
    "description": "",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "",
    "warning": "",
    "category": "Generic",
}

from . import scanobj
from . import mainPanel
from . import conLines
from . import utils
from . import keymap

import os
import bpy

from bpy.app.handlers import persistent

# def elementTypeOverride_cb(*args):
#     for obj in bpy.data.objects:
#         if ( # exclude objects
#             obj.type == "MESH" and
#             obj.name != "0" and
#             obj.name.endswith("_bbox") is False
#             ):
#             scanobj.autoCat(obj)
#     for obj in bpy.context.selected_objects:
#         obj.elementTypeOverride = bpy.context.object.elementTypeOverride
#         # elementType gets changed by autoCat

def camera_cb(*args):
    # change render image size according to camera settings
    activecam = bpy.context.scene.camera.data
    bpy.context.scene.render.resolution_x = round(activecam.dim[0]*0.0393701*activecam.dpi)
    bpy.context.scene.render.resolution_y = round(activecam.dim[1]*0.0393701*activecam.dpi)
    activecam.ortho_scale = activecam.dim[0]*activecam.dimscale/1000

def rename_cb(*args):
    # rename all related objects (currently: bbox and note)
    print("rename_cb:")
    data = bpy.data

    for o in data.objects:
        newname = o.name
        if len(o.pka) == 0:
            oldname = newname
        else:
            oldname = o.pka
        
        if newname != oldname:
            try:
                o.data.name = newname
            except:
                pass


            try:
                for obj in data.objects:
                    
                    if obj.name.find(oldname + '_bbox') > -1 or obj.name.find(oldname + '_opening') > -1:
                        obj.name = obj.name.replace(oldname,newname)
                        obj.data.name = obj.name

                bpy.data.texts[oldname].name = newname
            except:
                pass

        o.pka = newname

def select_cb(obj, former):
    # notes
    notearea = bpy.data.window_managers[0].windows[0].workspace.screens[0].areas[3]
    notes = notearea.spaces[0]
    notes.show_line_numbers = False
    notes.show_syntax_highlight = False
    try:
        notes.text = bpy.data.texts[obj.name]
    except:
        bpy.data.texts.new(obj.name)
        notes.text = bpy.data.texts[obj.name]
    notearea.header_text_set("Object Notes: " + notes.text.name)

    try:
        bpy.data.objects[obj.name+"_bbox"] # when adding new object, scan it instantly
    except:
        scanobj.main(obj)

    for o in bpy.context.selected_objects:
        scanobj.main(o)

    obj.pka = obj.name

    if obj.type == "EMPTY":
        for c in obj.children:
            c.select_set(True)

    if obj.type == "CAMERA":
        
        if len(obj.data.background_images) > 0: 
            try:
                area = bpy.data.window_managers['WinMan'].windows[-1].workspace.screens[1].areas[0]
                imagespace = area.spaces[0]
                imagespace.image = obj.data.background_images[0].image
            except:
                # bpy.ops.wm.window_new()
                # area = bpy.data.window_managers['WinMan'].windows[-1].workspace.screens[1].areas[0]
                # area.ui_type = "IMAGE_EDITOR"
                # imagespace = bpy.data.window_managers['WinMan'].windows[-1].workspace.screens[1].areas[0].spaces[0]
                # imagespace.image = obj.data.background_images[0].image
                pass

    if obj.elementType != 'Opening':
        for c in obj.children:
            if c.elementType == 'Opening':
                c.hide_set(False)
        for c in former.children:
            if c.elementType == 'Opening':
                c.hide_set(True)

def scene_cb(*args):
    print("scene change")
    for o in bpy.context.scene.objects:
        try:
            for m in o.modifiers:
                if m.object is not None:
                    if m.object.name not in bpy.context.scene.objects:
                        m.show_viewport = False
                        m.show_render = False
                    if m.object.name in bpy.context.scene.objects:
                        m.show_viewport = True
                        m.show_render = True
                else:
                    o.modifiers.remove(m)
        except:
            pass

    for s in bpy.data.scenes:
        for n in s.demolish:
            if s != bpy.context.scene:
                bpy.data.objects[n.name].display_type = "TEXTURED"
            else:
                bpy.data.objects[n.name].display_type = "WIRE"


# def storey_cb(*args):
#     scanobj.setstoreys()
#     for o in bpy.data.objects:
#         try:
#             scanobj.putinstorey(o)
#         except:
#             pass

@persistent
def goliathOnLoad(arg1, arg2):
    print("loading file")
    # set up workspace
    path = os.path.dirname(__file__) + "\\goliathstartup.blend"
    if "Goliath" in bpy.data.workspaces:
        bpy.data.window_managers[0].windows[0].workspace = bpy.data.workspaces["Goliath"]
    else:
        # if bpy.path.abspath("//") == "":
        #     sethomefile() # this sets the home file,
        #     return        # but doesn't reset it when the addon is disabled
        #                   # which is at least very impolite
        #                   # also does not work right now. fix later
        # else:
        bpy.ops.workspace.append_activate(idname="Goliath", filepath=path)

    conLines.conObject() # make "0" object

    # reset everything
    bpy.types.Scene.activeobj = bpy.context.object
    # bpy.types.Scene.storeyheights = []
    # bpy.types.Scene.storeynames = []
    # scanobj.setstoreys()

    # for scene in bpy.data.scenes:
    #     resetstoreys(scene)

    for o in bpy.data.objects:
        try:
            if o.name.find("_bbox.") > -1:
                bpy.data.objects.remove(o)
            if o.name.find("_bbox") > -1:
                if o.parent is None:
                    bpy.data.objects.remove(o)
        except:
            print("exception in load_post")

    for o in bpy.data.objects:
        try:
            if o.name.find("_bbox") > -1:
                if o.name != o.parent.name + "_bbox":
                    o.name = o.parent.name + "_bbox"
        except:
            print("exception in load_post")

    for o in bpy.data.objects:
        for l in o.linked:
            if l.name not in bpy.data.objects or l.name == o.name:
                i = o.linked.find(l.name)
                o.linked.remove(i)

    bpy.ops.goliath.conlinesclear()

    # scan everything
    for o in bpy.data.objects:
        try:
            scanobj.main(o)
        except:
            pass

    bpy.data.window_managers[0].windows[0].workspace.screens[0].areas[3].header_text_set("Object Notes")
    # for some reason this acts on an outdated state, not working as intended.
    # to fix this, the header is added in select_cb for now....

    # bpy.msgbus.subscribe_rna(
    # key=(bpy.types.Object, "elementTypeOverride"),
    # owner=object(),
    # args=(1, 2, 3),
    # notify=elementTypeOverride_cb,
    # )

    bpy.msgbus.subscribe_rna(
    key=(bpy.types.Camera, "dim"),
    owner=object(),
    args=(1, 2, 3),
    notify=camera_cb,
    )

    bpy.msgbus.subscribe_rna(
    key=(bpy.types.Camera, "dimscale"),
    owner=object(),
    args=(1, 2, 3),
    notify=camera_cb,
    )

    bpy.msgbus.subscribe_rna(
    key=(bpy.types.Camera, "dpi"),
    owner=object(),
    args=(1, 2, 3),
    notify=camera_cb,
    )

    bpy.msgbus.subscribe_rna(
    key=(bpy.types.Scene, "camera"),
    owner=object(),
    args=(1, 2, 3),
    notify=camera_cb,
    )

    bpy.msgbus.subscribe_rna(
    key=(bpy.types.Object, "name"),
    owner=object(),
    args=(1, 2, 3),
    notify=rename_cb,
    )

    bpy.msgbus.subscribe_rna(
    key=(bpy.types.Window, "scene"),
    owner=object(),
    args=(1, 2, 3),
    notify=scene_cb,
    )

    # bpy.msgbus.subscribe_rna(
    # key=(bpy.types.Object, "isStorey"),
    # owner=object(),
    # args=(1, 2, 3),
    # notify=storey_cb,
    # )

    # bpy.msgbus.subscribe_rna(
    # key=(bpy.types.Object, "storeyProps"),
    # owner=object(),
    # args=(1, 2, 3),
    # notify=storey_cb,
    # )

@persistent
def depsgraphHandler(scene):
    # when active object changes: select_cb(obj)
    # maybe there is a better way to do this?
    selected = bpy.context.selected_objects
    active = bpy.context.object
    formeractive = bpy.types.Scene.activeobj
    if formeractive != active:
        try:
            select_cb(active, formeractive)
        except:
            print("exception in select_cb")
    bpy.types.Scene.activeobj = active # proper way to do this would be to use view_layer.objects.active
    for obj in active.linked:
        bpy.data.objects[obj.name].location = active.location

def sethomefile():
    # how should the startup file thing work?
    # set homefile or generate everything by code?
    path = os.path.dirname(__file__) + "\\goliathstartup.blend"
    print(path)
    bpy.ops.wm.open_mainfile(filepath=path)
    bpy.ops.wm.save_homefile()
    bpy.ops.wm.read_homefile(app_template="")

def resethomefile():
    bpy.ops.wm.read_factory_settings()
    bpy.ops.wm.read_userpref()

def register():
    conLines.register()
    mainPanel.register()
    utils.register()

    bpy.app.handlers.load_post.append(goliathOnLoad)
    bpy.app.handlers.depsgraph_update_post.append(depsgraphHandler)

    keymap.register_keymaps()

def unregister():
    conLines.unregister()
    mainPanel.unregister()
    utils.unregister()

    bpy.app.handlers.load_post.remove(goliathOnLoad)
    bpy.app.handlers.depsgraph_update_post.remove(depsgraphHandler)

    keymap.unregister_keymaps()

if __name__ == "__main__":
    register()