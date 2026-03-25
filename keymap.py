import bpy

# Store (keymap, keymap_item) for cleanup on unregister.
addon_keymaps = []


def register_keymaps():
    wm = bpy.context.window_manager
    kc_addon = wm.keyconfigs.addon
    if kc_addon is None:
        return  # Can be None in background mode.
    
    kc_active = wm.keyconfigs.active

    km_objmode = kc_addon.keymaps.new(name="Object Mode")
    km_mesh = kc_addon.keymaps.new(name="Mesh")
    km_objnonmodal = kc_addon.keymaps.new(name="Object Non-modal")
    km_3dview = kc_addon.keymaps.new(name="3D View", space_type='VIEW_3D')

    activetype = kc_active.keymaps["Object Mode"].keymap_items["transform.rotate"].type
    objrotate = km_objmode.keymap_items.new(
        idname="goliath.objrotate",
        type='R',
        value='PRESS',
    )
    addon_keymaps.append((km_objmode, objrotate))

    objscale = km_objmode.keymap_items.new(
        idname="goliath.objscale",
        type='S',
        value='PRESS',
    )
    addon_keymaps.append((km_objmode, objscale))

    group = km_objmode.keymap_items.new(
        idname="goliath.group",
        type='G',
        value='PRESS',
        ctrl=True,
    )
    addon_keymaps.append((km_objmode, group))

    ungroup = km_objmode.keymap_items.new(
        idname="goliath.ungroup",
        type='G',
        value='PRESS',
        alt=True,
    )
    addon_keymaps.append((km_objmode, ungroup))

    duplicate = km_objmode.keymap_items.new(
        idname="goliath.duplicate",
        type='D',
        value='PRESS',
        shift=True
    )
    addon_keymaps.append((km_objmode, duplicate))

    delete = km_objmode.keymap_items.new(
        idname="goliath.delete",
        type='X',
        value='PRESS',
    )
    addon_keymaps.append((km_objmode, delete))

    modetoggle = km_objnonmodal.keymap_items.new(
        idname="goliath.modetoggle",
        type='TAB',
        value='PRESS',
    )
    addon_keymaps.append((km_objnonmodal, modetoggle))

    conlines = km_mesh.keymap_items.new(
        idname="goliath.conlines",
        type='C',
        value='PRESS',
    )
    addon_keymaps.append((km_mesh, conlines))

    conlinesclear = km_3dview.keymap_items.new(
        idname="goliath.conlinesclear",
        type='C',
        value='PRESS',
        alt=True,
    )
    addon_keymaps.append((km_3dview, conlinesclear))

def unregister_keymaps():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()