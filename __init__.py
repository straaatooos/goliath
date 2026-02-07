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

import os
import bpy

from bpy.app.handlers import persistent

#testing

def elementTypeOverride_cb(*args):
    for obj in bpy.data.objects:
        if ( # exclude objects
            obj.type == "MESH" and
            obj.name != "0" and
            obj.name.endswith("_bbox") is False
            ):
            scanobj.autoCat(obj)

def camera_cb(*args):
    # change render image size according to camera settings
    activecam = bpy.context.scene.camera.data
    bpy.context.scene.render.resolution_x = activecam.dim[0]
    bpy.context.scene.render.resolution_y = activecam.dim[1]

def rename_cb(*args):
    # rename all related objects (currently: bbox and note)
    for o in bpy.data.objects:
        if o.data is not None:
            o.data.name = o.name
            for c in o.children:
                if c.name.endswith("_bbox") == True:
                    oldname = c.name.removesuffix("_bbox")
                    c.name = o.name + "_bbox"
                    c.data.name = o.name + "_bbox"
                    bpy.data.texts[oldname].name = o.name

def select_cb(obj):
    # notes
    notearea = bpy.data.window_managers[0].windows[0].workspace.screens[0].areas[3]
    notearea.header_text_set("Object Notes")
    notes = notearea.spaces[0]
    notes.show_line_numbers = False
    notes.show_syntax_highlight = False
    try:
        notes.text = bpy.data.texts[obj.name]
    except:
        bpy.data.texts.new(obj.name)
        notes.text = bpy.data.texts[obj.name]

    if [obj.name + "_bbox"] not in obj.children: # when adding new object, scan it instantly
        scanobj.main(obj)

def storey_cb(*args):
    scanobj.setstoreys()
    for o in bpy.data.objects:
        try:
            scanobj.putinstorey(o)
        except:
            pass

@persistent
def goliathOnLoad(arg1, arg2):
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
    bpy.types.Scene.storeyheights = []
    bpy.types.Scene.storeynames = []
    scanobj.setstoreys()

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

    bpy.msgbus.subscribe_rna(
    key=(bpy.types.Object, "elementTypeOverride"),
    owner=object(),
    args=(1, 2, 3),
    notify=elementTypeOverride_cb,
    )

    bpy.msgbus.subscribe_rna(
    key=(bpy.types.Camera, "dim"),
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
    key=(bpy.types.Object, "isStorey"),
    owner=object(),
    args=(1, 2, 3),
    notify=storey_cb,
    )

    bpy.msgbus.subscribe_rna(
    key=(bpy.types.Object, "storeyProps"),
    owner=object(),
    args=(1, 2, 3),
    notify=storey_cb,
    )

@persistent
def selectHandler(scene):
    # when active object changes: select_cb(obj)
    # maybe there is a better way to do this?
    activeobj = bpy.context.object
    if bpy.types.Scene.activeobj != activeobj:
        select_cb(activeobj)
    bpy.types.Scene.activeobj = activeobj

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
    bpy.app.handlers.depsgraph_update_post.append(selectHandler)

def unregister():
    conLines.unregister()
    mainPanel.unregister()
    utils.unregister()

    bpy.app.handlers.load_post.remove(goliathOnLoad)
    bpy.app.handlers.depsgraph_update_post.remove(selectHandler)

if __name__ == "__main__":
    register()