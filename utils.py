import bpy
import bmesh
import mathutils

from . import scanobj

# def incollections(obj):
#     collections = []
#     for col in bpy.data.collections:
#         if obj.name in col.objects:
#             collections.append(col)
#     return collections

class modeToggle(bpy.types.Operator):
    bl_idname = "goliath.modetoggle"
    bl_label = "Toggle Object Mode"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):

        if context.object.mode == "EDIT": # when entering object mode, before toggle
            
            # separate, disabled for now
            # l = len(bpy.context.selected_objects)
            # bpy.ops.mesh.separate(type="LOOSE")
            # if len(bpy.context.selected_objects) > l:
            #     for o in bpy.context.selected_objects:
            #         scanobj.main(o)

            for obj in context.selected_objects:
                if obj.type == "MESH":
                    try:
                        bpy.data.objects[obj.name + "_bbox"].hide_set(not obj.showbbox)
                    except:
                        pass

        elif context.object.mode == "OBJECT": # when entering edit mode, before toggle
            for obj in context.selected_objects:
                # see if there is a bbox, if yes: hide it, if not: scan
                if obj.type == "MESH":
                    try: 
                        bpy.data.objects[obj.name + "_bbox"].hide_set(True)
                    except:
                        scanobj.main(obj)

            # not sure how useful this is
            #for obj in context.selected_objects:
            #    if obj == bpy.context.object:
            #        continue
            #    obj.parent = bpy.context.object

        bpy.ops.object.editmode_toggle()

        if context.object.mode == "OBJECT": # when entering object mode, after toggle
            for obj in context.selected_objects:
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
                scanobj.main(obj)

            for c in bpy.data.objects["0"].children:
                c.hide_select = True

        elif context.object.mode == "EDIT": # when entering edit mode, after toggle
            for c in bpy.data.objects["0"].children:
                c.hide_select = False
            
        return {'FINISHED'}

class delete(bpy.types.Operator):
    bl_idname = "goliath.delete"
    bl_label = "Delete Object And Children"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects is not None
    
    def recursive(self, obj):
        if obj.isStorey == True:
            obj.isStorey = False

        for c in obj.children:
            self.recursive(c)

        try:
            bpy.data.texts.remove(bpy.data.texts[obj.name])   
        except:
            pass

        try:
            bpy.data.meshes.remove(obj.data)
        except:
            pass

        try:
            bpy.data.objects.remove(obj)
        except:
            pass
            
    def execute(self, context):
        bpy.ops.goliath.unlink()
        
        for obj in bpy.context.selected_objects: # prevent a mess
            if obj.parent in bpy.context.selected_objects:
                obj.select_set(False)

        for obj in bpy.context.selected_objects:
            self.recursive(obj)
    
        return {'FINISHED'}

class duplicate(bpy.types.Operator):
    bl_idname = "goliath.duplicate"
    bl_label = "Duplicate Object And Children"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects is not None
    
    def recursive(self, obj, parent):
        if obj.name.endswith("_bbox") == False:
            obj.pka = ""
            view_layer = bpy.context.view_layer
            wasStorey = False
            if obj.isStorey == True:
                wasStorey = True
                obj.isStorey = False
            copy = obj.copy()
            worldmatrix = obj.matrix_world*1 # this is just a workaround, fix this
            try:
                copy.data = obj.data.copy()
            except:
                pass
            
            copy.parent = parent
            copy.matrix_world = worldmatrix
            for c in obj.users_collection:
                c.objects.link(copy)
            copy.select_set(True)
            # if parent is not None:
            #     copy.location -= parent.location

            if obj.name.endswith("_bbox") == True:
                copy.name = (parent.name + "_bbox")
                copy.data.name = (parent.name + "_bbox")

            if obj.name.find("_opening") > -1:
                copy.name = (parent.name + "_opening")
                copy.data.name = (parent.name + "_opening")

            copy.hide_set(obj.hide_get())
            
            for child in obj.children:
                self.recursive(child, copy)
            
            if wasStorey == True:
                obj.isStorey = True

            scanobj.main(copy)

    def execute(self, context):
        for obj in bpy.context.selected_objects: # prevent a mess
            if obj.parent in bpy.context.selected_objects:
                obj.select_set(False)

        for obj in bpy.context.selected_objects:
            self.recursive(obj, obj.parent)
            obj.select_set(False)
            bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
        
        bpy.ops.transform.translate('INVOKE_DEFAULT')

        return {'FINISHED'}

class duplicatelinked(bpy.types.Operator):
    bl_idname = "goliath.duplicatelinked"
    bl_label = "Duplicate Object And Children as Linked Objects"
    bl_options = {'UNDO'}

    i = []

    @classmethod
    def poll(cls, context):
        return context.selected_objects is not None
    
    def recursive(self, obj, parent):
        if obj.name.endswith("_bbox") == False:
            obj.pka = ""
            self.i.append(0)
            view_layer = bpy.context.view_layer
            wasStorey = False
            if obj.isStorey == True:
                wasStorey = True
                obj.isStorey = False      
            copy = obj.copy()
            worldmatrix = obj.matrix_world*1
            try:
                copy.data = obj.data
            except:
                pass
            
            copy.parent = parent
            copy.matrix_world = worldmatrix
            for c in obj.users_collection:
                c.objects.link(copy)
            copy.select_set(True)

            if len(self.i) > 1:
                copy.linked.add().name = obj.name
                for l in obj.linked:
                    addlnk = bpy.data.objects[l.name].linked.add()
                    addlnk.name = copy.name
                obj.linked.add().name = copy.name

            if obj.name.endswith("_bbox") == True:
                copy.name = (parent.name + "_bbox")
                copy.data.name = (parent.name + "_bbox")
            
            copy.hide_set(obj.hide_get())
            
            for child in obj.children:
                self.recursive(child, copy)
            
            if wasStorey == True:
                obj.isStorey = True

            scanobj.main(copy)

    def execute(self, context):
        for obj in bpy.context.selected_objects: # prevent a mess
            if obj.parent in bpy.context.selected_objects:
                obj.select_set(False)

        for obj in bpy.context.selected_objects:
            self.recursive(obj, obj.parent)
            obj.select_set(False)
            bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]

        self.i.clear()
        
        bpy.ops.transform.translate('INVOKE_DEFAULT')

        return {'FINISHED'}

class replace(bpy.types.Operator):
    bl_idname = "goliath.replace"
    bl_label = "Replace Current Object With Family"
    bl_options = {'UNDO'}

    i = []

    @classmethod
    def poll(cls, context):
        return context.selected_objects is not None and context.scene.replacesource is not None
    
    def recursive(self, obj, parent):
        if obj.name.endswith("_bbox") == False:
        # copy.name = (parent.name + "_bbox")
        # copy.data.name = (parent.name + "_bbox")
            obj.pka = ""
            self.i.append(0)
            view_layer = bpy.context.view_layer
            wasStorey = False
            if obj.isStorey == True:
                wasStorey = True
                obj.isStorey = False      
            copy = obj.copy()
            worldmatrix = obj.matrix_world*1
            try:
                copy.data = obj.data
            except:
                pass
            
            copy.parent = parent
            copy.matrix_world = worldmatrix
            for c in obj.users_collection:
                c.objects.link(copy)

            if len(self.i) > 1:
                copy.linked.add().name = obj.name
                for l in obj.linked:
                    addlnk = bpy.data.objects[l.name].linked.add()
                    addlnk.name = copy.name
                obj.linked.add().name = copy.name
            elif len(self.i) == 1:
                bpy.context.view_layer.objects.active = copy
                copy.select_set(True)
            
            copy.hide_set(obj.hide_get())
            
            for child in obj.children:
                self.recursive(child, copy)
            
            if wasStorey == True:
                obj.isStorey = True

            scanobj.main(copy)


    def execute(self, context):
        source = context.scene.replacesource
        active = context.object
        matrix = active.matrix_basis*1
        bpy.ops.goliath.delete()
        # for obj in bpy.context.selected_objects: # prevent a mess
        #     if obj.parent in bpy.context.selected_objects:
        #         obj.select_set(False)

        self.recursive(source, source.parent)
        context.object.matrix_basis = matrix

        self.i.clear()

        return {'FINISHED'}

class insert(bpy.types.Operator):
    bl_idname = "goliath.insert"
    bl_label = "Insert Object in Hierarchy"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects is not None and context.scene.replacesource is not None
    
    def recursive(self, obj, parent):
        pass # for the future
        # if obj.name.endswith("_bbox") == False:
        # # copy.name = (parent.name + "_bbox")
        # # copy.data.name = (parent.name + "_bbox")
        #     obj.pka = ""
        #     self.i.append(0)
        #     view_layer = bpy.context.view_layer
        #     wasStorey = False
        #     if obj.isStorey == True:
        #         wasStorey = True
        #         obj.isStorey = False      
        #     copy = obj.copy()
        #     worldmatrix = obj.matrix_world*1
        #     try:
        #         copy.data = obj.data
        #     except:
        #         pass
            
        #     copy.parent = parent
        #     copy.matrix_world = worldmatrix
        #     for c in obj.users_collection:
        #         c.objects.link(copy)

        #     if len(self.i) > 1:
        #         copy.linked.add().name = obj.name
        #         for l in obj.linked:
        #             addlnk = bpy.data.objects[l.name].linked.add()
        #             addlnk.name = copy.name
        #         obj.linked.add().name = copy.name
        #     elif len(self.i) == 1:
        #         bpy.context.view_layer.objects.active = copy
        #         copy.select_set(True)
            
        #     copy.hide_set(obj.hide_get())
            
        #     for child in obj.children:
        #         self.recursive(child, copy)
            
        #     if wasStorey == True:
        #         obj.isStorey = True

        #     scanobj.main(copy)


    def execute(self, context):
        print("WIP!")
        # source = context.scene.replacesource
        # active = context.object
        # matrix = active.matrix_basis*1
        # bpy.ops.goliath.delete()
        # # for obj in bpy.context.selected_objects: # prevent a mess
        # #     if obj.parent in bpy.context.selected_objects:
        # #         obj.select_set(False)

        # self.recursive(source, source.parent)
        # context.object.matrix_basis = matrix

        # self.i.clear()

        return {'FINISHED'}

class eject(bpy.types.Operator):
    bl_idname = "goliath.eject"
    bl_label = "Eject Selected Hierarchy Level"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects is not None and context.scene.replacesource is not None

    def execute(self, context):
        children = []
        for obj in context.selected_objects:
            for c in obj.children:
                matrix = c.matrix_world
                c.parent = obj.parent
                c.matrix_world = matrix
                children.append(c)
                        
        bpy.ops.goliath.delete()

        for c in children:
            c.hide_set(False)
            c.select_set(True)

        return {'FINISHED'}
    
class unlink(bpy.types.Operator):
        bl_idname = "goliath.unlink"
        bl_label = "Make Selected Objects/Hierarchies independant"
        bl_options = {'UNDO'}#

        @classmethod
        def poll(cls, context):
            return context.selected_objects is not None
        
        def recursive(self, obj):
            for l in obj.linked:
                print(obj.name+" linked to "+l.name)
                if l.name != obj.name:
                    i = bpy.data.objects[l.name].linked.find(obj.name)
                    bpy.data.objects[l.name].linked.remove(i)
            obj.linked.clear()
            copy = obj.data.copy()
            copy.name = obj.name
            obj.data = copy
            for c in obj.children:
                self.recursive(c)
    
        def execute(self, context):
            for obj in context.selected_objects:
                self.recursive(obj)
    
            return {'FINISHED'}
    
class join(bpy.types.Operator):
    bl_idname = "goliath.join"
    bl_label = "Join Objects And Clean Up Remnants"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        poll = True
        try:
            for obj in context.selected_objects:
                if obj.type != "MESH":
                    poll = False
        except:
            poll = False
        return poll
            
    def execute(self, context):
        names = []

        for obj in bpy.context.selected_objects:
            if obj != bpy.context.object:
                names.append(obj.name)

        bpy.ops.object.join()

        for name in names:
            bpy.data.texts.remove(bpy.data.texts[name])
            bpy.data.objects.remove(bpy.data.objects[name + "_bbox"])
            bpy.data.meshes.remove(bpy.data.meshes[name + "_bbox"])
            bpy.data.meshes.remove(bpy.data.meshes[name])
    
        return {'FINISHED'}
    
class hide(bpy.types.Operator):
    bl_idname = "goliath.hide"
    bl_label = "Recursive/Group Hide"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects is not None
            
    def recursive(self, obj):
        for c in obj.children:
            if c.name in bpy.context.scene.objects:
                self.recursive(c)
                c.hide_set(True)
            
    def execute(self, context):
        # for obj in bpy.context.selected_objects: # prevent a mess
        #     if obj.parent in bpy.context.selected_objects:
        #         obj.select_set(False)

        for obj in bpy.context.selected_objects:
            self.recursive(obj)
            if obj.type != "EMPTY":
                obj.hide_set(True)
    
        return {'FINISHED'}
    
class unhide(bpy.types.Operator):
    bl_idname = "goliath.unhide"
    bl_label = "Unhide Group/Most Recent/All"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects is not None
    
    def recursive(self, obj):
        for c in obj.children:
            self.recursive(c)
            c.hide_set(False)
            
    def execute(self, context):
        if len(context.selected_objects) > 0:
            for obj in context.selected_objects:
                if obj.parent is not None:
                    for s in obj.parent.children:
                        #self.recursive(s)
                        s.hide_set(False)
                else:
                    for c in obj.children:
                        #self.recursive(c) # what about openings?
                        c.hide_set(False)

                
        else:
            bpy.ops.object.hide_view_clear()
    
        return {'FINISHED'}

class objTranslate(bpy.types.Operator):
    # not sure if to keep this one
    bl_idname = "goliath.objtranslate"
    bl_label = "Move Object Geometry"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        if bpy.context.object.type == "MESH":
            bpy.ops.goliath.modetoggle()
            bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.transform.translate('INVOKE_DEFAULT')

        return {'FINISHED'}
    
class objScale(bpy.types.Operator):
    # not sure if to keep this one
    bl_idname = "goliath.objscale"
    bl_label = "Scale Object Geometry"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        if bpy.context.object.type == "MESH":
            bpy.ops.goliath.modetoggle()
            bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.transform.resize('INVOKE_DEFAULT')

        return {'FINISHED'}
    
class objRotate(bpy.types.Operator):
    # not sure if to keep this one
    bl_idname = "goliath.objrotate"
    bl_label = "Rotate Object Geometry"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        if bpy.context.object.type == "MESH":
            bpy.ops.goliath.modetoggle()
            bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.transform.rotate('INVOKE_DEFAULT')

        return {'FINISHED'}
    
class editTranslate(bpy.types.Operator):
    # not sure if to keep this one
    bl_idname = "goliath.edittranslate"
    bl_label = "Move Mesh Geometry"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        oldpivotsetting = context.scene.tool_settings.transform_pivot_point
        if bpy.context.tool_settings.mesh_select_mode[2] is True:
            context.scene.tool_settings.transform_pivot_point = "ACTIVE_ELEMENT"
            bpy.ops.transform.translate('INVOKE_DEFAULT', orient_type="NORMAL", constraint_axis=(False, False, True))
        else:
            try:
                bpy.ops.transform.translate('INVOKE_DEFAULT', orient_type="Construction Line", constraint_axis=(False, True, False))
            except:
                pass
                bpy.ops.transform.translate('INVOKE_DEFAULT')
        
        context.scene.tool_settings.transform_pivot_point = oldpivotsetting

        return {'FINISHED'}

class group(bpy.types.Operator):
    # not sure if to keep this one
    bl_idname = "goliath.group"
    bl_label = "Group Selected Objects"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        empty = bpy.data.objects.new("Group", None)
        view_layer = bpy.context.view_layer
        view_layer.active_layer_collection.collection.objects.link(empty)
        empty.empty_display_size = 1
        empty.show_in_front = True
        empty.show_name = True
        loc = mathutils.Vector((0,0,0))
        tick = 0
        for o in bpy.context.selected_objects:
            loc += o.location
            tick += 1
        empty.location = loc/tick

        for i,o in enumerate(bpy.context.selected_objects):
            o.location -= loc/tick # annoying. why is this necessary in the first place
            o.parent = empty

        return {'FINISHED'}
    
class ungroup(bpy.types.Operator):
    # not sure if to keep this one
    bl_idname = "goliath.ungroup"
    bl_label = "Dissolve Group"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        for obj in bpy.context.selected_objects: # prevent a mess
            if obj.parent in bpy.context.selected_objects:
                obj.select_set(False)

        for obj in bpy.context.selected_objects:
            if obj.type == "EMPTY":
                for c in obj.children:
                    worldmatrix = 1*c.matrix_world
                    c.parent = None
                    c.matrix_world = worldmatrix
                bpy.data.texts.remove(bpy.data.texts[obj.name])
                bpy.data.objects.remove(obj)
            else:
                worldmatrix = 1*obj.matrix_world
                obj.parent = None
                obj.matrix_world = worldmatrix

        return {'FINISHED'}
    
class pointcloudProcess(bpy.types.Operator):
    # not sure if to keep this one
    bl_idname = "goliath.pointcloudprocess"
    bl_label = "Process Point Cloud"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        activeobj = bpy.context.object

        bpy.data.node_groups["PointCloudReduced"].nodes["Object Info"].inputs[0].default_value = activeobj
        bpy.data.node_groups["PointCloudRawFiltered"].nodes["Object Info.001"].inputs[0].default_value = activeobj

        activeobj.hide_viewport = True
        activeobj.hide_select = True

        return {'FINISHED'}
    
class align(bpy.types.Operator):
    # not sure if to keep this one
    bl_idname = "goliath.align"
    bl_label = "Align Geometry"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        source = bpy.data.objects['alignSource']
        target = bpy.data.objects['alignTarget']

        a1 = source.data.vertices[0].co
        b1 = source.data.vertices[1].co
        v1 = a1-b1
        m1 = ((a1+b1)/2)#source.location + 
        l1 = v1.length

        a2 = target.data.vertices[0].co
        b2 = target.data.vertices[1].co
        v2 = a2-b2
        m2 = ((a2+b2)/2)
        l2 = v2.length

        axis = v1.cross(v2)
        angle = v1.angle(v2)
        scale = (l2/l1)*mathutils.Vector((1,1,1))
        offset = (target.location-source.location + m2-m1)
        

        for o in bpy.context.selected_objects:
            me = o.data
            bm = bmesh.new()
            bm.from_mesh(me)
            verts = bm.verts

            matrix = mathutils.Matrix.Rotation(angle, 4, axis)
            space = mathutils.Matrix.Translation(-(source.location-o.location))

            bmesh.ops.rotate(bm, cent=m1, matrix=matrix, verts=verts, space=space)

            bm.to_mesh(me)
            bm.free()

        c1 = source.data.vertices[2].co
        d1 = mathutils.geometry.intersect_point_line(c1, a1, b1)[0]
        u1 = c1-d1

        c2 = target.data.vertices[2].co
        d2 = mathutils.geometry.intersect_point_line(c2, a2, b2)[0]
        u2 = c2-d2

        for o in bpy.context.selected_objects:
            me = o.data 
            bm = bmesh.new()
            bm.from_mesh(me)
            verts = bm.verts

            angle = u1.angle(u2)
            matrix = mathutils.Matrix.Rotation(-angle, 4, v2)
            space = mathutils.Matrix.Translation(-(source.location+m1-o.location))
            bmesh.ops.rotate(bm, cent=m1, matrix=matrix, verts=verts, space=space)
            bmesh.ops.scale(bm, vec=scale, verts=verts, space=space)
            bmesh.ops.translate(bm, vec=offset, verts=verts, space=space)
            

            bm.to_mesh(me)
            bm.free()
        
        return {'FINISHED'}

from bpy_extras.io_utils import ImportHelper
from PIL import Image

class photo(bpy.types.Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "goliath.photo"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Add Photo with Camera"
    bl_options = {'UNDO'}

    # ImportHelper mix-in class uses this.
    filename_ext = ".txt"

    filter_glob: bpy.props.StringProperty(
        default="*.png",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # # List of operator properties, the attributes will be assigned
    # # to the class instance from the operator settings before calling.
    # focallength: bpy.props.IntProperty(
    #     name="Focal Length",
    #     description="Example Tooltip",
    #     default=26,
    # )

    # type: bpy.props.EnumProperty(
    #     name="Example Enum",
    #     description="Choose between two items",
    #     items=(
    #         ('OPT_A', "First Option", "Description one"),
    #         ('OPT_B', "Second Option", "Description two"),
    #     ),
    #     default='OPT_A',
    # )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        # select image from browser
        filepath = self.filepath

        img = Image.open(filepath)
        xmp = str(img.info['xmp'])
        i = xmp.find("35mm")
        focallength = int(xmp[i+10:i+12])

        img = bpy.data.images.load(filepath)
        #focallength = self.focallength

        
        cam = bpy.data.cameras.new(name=img.name)
        camobj = bpy.data.objects.new(name=img.name, object_data=cam)
        bg = cam.background_images.new()
        bg.image = img
        bg.display_depth = "FRONT"
        bg.alpha = 0.4

        cam.show_background_images = True
        cam.lens = focallength
        [cam.dim[0], cam.dim[1]] = [round(img.size[0]/0.0393701), round(img.size[1]/0.0393701)]
        cam.dpi = 1 # fix this later
        context.scene.render.resolution_x = img.size[0]
        context.scene.render.resolution_y = img.size[1]

        #(read image metadata for camera data?)

        camobj.show_name = True

        view_layer = bpy.context.view_layer
        view_layer.active_layer_collection.collection.objects.link(camobj)

        bpy.context.scene.camera = camobj

        bpy.ops.view3d.view_camera()

        bpy.data.screens["Default"].areas[2].spaces[0].lock_camera = True

        return {'FINISHED'}
    
class opening(bpy.types.Operator):
    # not sure if to keep this one
    bl_idname = "goliath.addopening"
    bl_label = "Add Opening"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        baseObj = bpy.context.object
        # baseLoc = baseObj.matrix_world.to_translation()

        bpy.ops.mesh.primitive_cube_add(size=1.0, scale=(1,0.885,2.135))#location=baseLoc)
        newObj = bpy.context.object
        bpy.data.texts[newObj.name].name = "temp"
        newObj.name = baseObj.name + "_opening"
        newObj.data.name = newObj.name
        newObj.children[0].name = newObj.name + "_bbox"
        bpy.data.texts["temp"].name = newObj.name
        newObj.display_type = 'WIRE'
        newObj.parent = baseObj

        if context.scene.name == "Bestand":
            for c in baseObj.users_collection:
                c.objects.link(newObj)
            # collections = incollections(baseObj)
            # for col in collections:
            #     col.objects.link(newObj)
        
        newObj.elementTypeOverride = 'Opening'
        newObj.elementType = 'Opening'

        newObj.matrix_world = baseObj.matrix_world

        baserotmat = mathutils.Euler(baseObj.euler).to_matrix()
        baserotmat = baserotmat.inverted()
        newObj.rotation_euler = baserotmat.to_euler()
        
        bool = baseObj.modifiers.new(name=newObj.name, type='BOOLEAN')
        bool.object = newObj
        bool.operation = 'DIFFERENCE'
        #bpy.ops.object.modifier_apply()


        return {'FINISHED'}

class decompup(bpy.types.Operator):
    # not sure if to keep this one
    bl_idname = "goliath.decompup"
    bl_label = "Up a Level in Decomposition"
    bl_options = {'UNDO'}

    levels = []
    levels.clear()

    @classmethod
    def poll(cls, context):
        return True
    
    def findlvl(self, obj, i):
        if obj.parent is not None:
            self.levels[i] += 1
            self.findlvl(obj.parent, i)

    def select(self, obj, lvl):
        #select(obj, lvl)
        pass

    def hide(self, obj):
        for c in obj.children:
            self.hide(c)
            #c.hide_viewport = True
            c.hide_render = True
            c.hide_set(True)
           
    def execute(self, context):
        objects = []
        levels = self.levels
        i = 0

        for obj in context.selected_objects:
            objects.append(obj)
            levels.append(0)
            self.findlvl(obj, i)
            i += 1

        sortedIs = [i[0] for i in sorted(enumerate(levels), key=lambda x:x[1], reverse=True)]
        maxlvl = levels[sortedIs[0]]

        blacklist = []

        for i in sortedIs:
            lvl = levels[i]
            obj = objects[i]
            if lvl == maxlvl and lvl > 0:
                lvl -= 1
                # obj.hide_viewport = True
                # obj.hide_render = True
                # obj.hide_set(True)
                if obj.parent not in blacklist:                
                    #obj.parent.hide_viewport = False
                    obj.parent.hide_set(False)
                    obj.parent.hide_render = False
                    obj.parent.select_set(True)
                    self.hide(obj.parent)
                    blacklist.append(obj.parent)

        context.view_layer.objects.active = context.selected_objects[0]

        levels.clear()
        blacklist.clear()

        return {'FINISHED'}

class decompdown(bpy.types.Operator):
    # not sure if to keep this one
    bl_idname = "goliath.decompdown"
    bl_label = "Down a Level in Decomposition"
    bl_options = {'UNDO'}

    levels = []

    @classmethod
    def poll(cls, context):
        return True

    def findlvl(self, obj, i):
        if obj.parent is not None:
            self.levels[i] += 1
            self.findlvl(obj.parent, i)

    def select(self, obj, lvl):
        #select(obj, lvl)
        pass
           
    def execute(self, context):
        objects = []
        levels = self.levels
        i = 0

        for obj in context.selected_objects:
            objects.append(obj)
            levels.append(0)
            self.findlvl(obj, i)
            i += 1

        sortedIs = [i[0] for i in sorted(enumerate(levels), key=lambda x:x[1], reverse=True)]
        maxlvl = levels[sortedIs[0]]

        for i in sortedIs:
            obj = objects[i]
            lvl = levels[i]
            if  lvl == maxlvl:
                proceed = False
                for c in obj.children:
                    if c.name.find('_bbox') < 0 and c.name.find('_opening') < 0:
                        lvl += 1
                        proceed = True
                        #c.hide_viewport = False
                        c.hide_render = False
                        c.hide_set(False)
                        c.select_set(True)
                if proceed == True:                       
                    #obj.hide_viewport = True
                    obj.hide_render = True
                    obj.hide_set(True)

        context.view_layer.objects.active = context.selected_objects[0]

        levels.clear()

        return {'FINISHED'}

class resetstoreys(bpy.types.Operator):
    # not sure if to keep this one
    bl_idname = "goliath.resetstoreys"
    bl_label = "Reset Storeys of Current Scene"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True
    
    def resetstoreys(self, scene):
        for s in enumerate(scene.storeys): # remove all storeys
            #print("removing " + s.name + "(" +str(i))
            scene.storeys.remove(0)
        for obj in scene.objects: # this is identical to a passage in mainPanel.storey_cb
            if obj.isStorey == True:
                height = scanobj.highpoint(obj)
                newstorey = scene.storeys.add()
                newstorey.name = str(height)
                newstorey.height = height

            for i,s in enumerate(scene.storeys): # sort by height
                heights = [s.height for s in bpy.context.scene.storeys]
                indices = [i[0] for i in sorted(enumerate(heights), key=lambda x:x[1])]
                scene.storeys.move(indices[i], i)

    def execute(self, context):
        self.resetstoreys(context.scene)
        return {'FINISHED'}

class demolish(bpy.types.Operator):
    # not sure if to keep this one
    bl_idname = "goliath.demolish"
    bl_label = "Demolish"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        obj = context.object
        if obj.name not in context.scene.demolish:
            context.scene.demolish.add().name = obj.name
        obj.display_type = 'WIRE'
        return {'FINISHED'}

class reconstruct(bpy.types.Operator):
    # not sure if to keep this one
    bl_idname = "goliath.reconstruct"
    bl_label = "Reconstruct"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        obj = context.object
        context.scene.demolish.remove(obj.name)
        obj.display_type = 'TEXTURED'
        return {'FINISHED'}


classes = [modeToggle, duplicate, duplicatelinked, replace, insert, eject, unlink,
           delete, join, hide, unhide, objScale, objRotate, editTranslate,
           group, ungroup, pointcloudProcess, align, photo, opening, 
           decompup, decompdown, resetstoreys, demolish, reconstruct] #objTranslate
    
def menu_func(self, context):
    self.layout.operator(photo.bl_idname, text=photo.bl_label)
    self.layout.operator(opening.bl_idname, text=opening.bl_label)
    self.layout.operator(demolish.bl_idname, text=demolish.bl_label)
    self.layout.operator(reconstruct.bl_idname, text=reconstruct.bl_label)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Camera.dim = bpy.props.IntVectorProperty(name="Dimensions",default=(420,297),min=0,size=2)
    bpy.types.Camera.dimscale = bpy.props.FloatProperty(name="Scale",default=(100))
    bpy.types.Camera.dpi = bpy.props.IntProperty(name="DPI", default=(300))

    bpy.types.VIEW3D_MT_add.append(menu_func)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Camera.dim
    del bpy.types.Camera.dimscale
    del bpy.types.Camera.dpi

    bpy.types.VIEW3D_MT_add.remove(menu_func)