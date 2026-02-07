import bpy
import mathutils

from . import scanobj

class modeToggle(bpy.types.Operator):
    bl_idname = "goliath.modetoggle"
    bl_label = "Toggle Object Mode"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):

        if context.object.mode == "EDIT": # when entering object mode, before toggle
            
            # separate
            l = len(bpy.context.selected_objects)
            bpy.ops.mesh.separate(type="LOOSE")
            if len(bpy.context.selected_objects) > l:
                for o in bpy.context.selected_objects:
                    scanobj.main(o)

            for obj in context.selected_objects:
                if obj.type == "MESH":  
                    bpy.data.objects[obj.name + "_bbox"].hide_viewport = False

        elif context.object.mode == "OBJECT": # when entering edit mode, before toggle
            for obj in context.selected_objects:
                # see if there is a bbox, if yes: hide it, if not: scan
                if obj.type == "MESH":
                    try: 
                        bpy.data.objects[obj.name + "_bbox"]
                        bpy.data.objects[obj.name + "_bbox"].hide_viewport = True
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
        for c in obj.children:
            self.recursive(c)
            try:
                bpy.data.texts.remove(bpy.data.texts[c.name])   
            except:
                pass

            try:
                bpy.data.objects.remove(c)
            except:
                pass
            
    def execute(self, context):
        for obj in bpy.context.selected_objects: # prevent a mess
            if obj.parent in bpy.context.selected_objects:
                obj.select_set(False)

        for obj in bpy.context.selected_objects:
            self.recursive(obj)
            bpy.data.texts.remove(bpy.data.texts[obj.name])
            bpy.data.objects.remove(obj)
    
        return {'FINISHED'}

class duplicate(bpy.types.Operator):
    bl_idname = "goliath.duplicate"
    bl_label = "Duplicate Object And Children"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects is not None
    
    def recursive(self, obj, parent):
        view_layer = bpy.context.view_layer        
        copy = obj.copy()
        worldmatrix = obj.matrix_world*1
        try:
            copy.data = obj.data.copy()
        except:
            pass
        new = copy.matrix_world
        
        copy.parent = parent
        copy.matrix_world = worldmatrix
        view_layer.active_layer_collection.collection.objects.link(copy)
        # copy.select_set(True)
        # if parent is not None:
        #     copy.location -= parent.location

        if obj.name.endswith("_bbox") == True:
            copy.name = (parent.name + "_bbox")
            copy.data.name = (parent.name + "_bbox")
        
        for child in obj.children:
            self.recursive(child, copy)

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
        if bpy.context.tool_settings.mesh_select_mode[2] is True:
            bpy.ops.transform.translate('INVOKE_DEFAULT', orient_type="NORMAL", constraint_axis=(False, False, True))
        else:
            try:
                bpy.ops.transform.translate('INVOKE_DEFAULT', orient_type="Con Line", constraint_axis=(False, True, False))
            except:
                pass
                bpy.ops.transform.translate('INVOKE_DEFAULT')
            

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

classes = [modeToggle, duplicate, delete, objScale, objRotate, editTranslate, group, ungroup, pointcloudProcess] #objTranslate
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Camera.dim = bpy.props.IntVectorProperty(name="Dimensions",default=(1920,1080),min=0,size=2)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Camera.dim