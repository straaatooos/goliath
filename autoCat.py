import bpy
import bmesh
import mathutils

from . import quantities

class autoCatOperator(bpy.types.Operator):
    bl_idname = "goliath.autocat"
    bl_label = "Auto-Categorize Object"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        for o in context.selected_objects:
            if o.type == "MESH":
                self.autoCat()

        return {'FINISHED'}
    
    def autoCat(self):
        activeobj = bpy.context.object

        if activeobj.elementTypeOverride == "(auto)":
            if quantities.calc("length") > 3:
                activeobj.elementType = "Beam"
            else:
                activeobj.elementType = "Wall"
        else:
            bpy.context.object.elementType = bpy.context.object.elementTypeOverride

    def drawCurve(A, B):
        A4d = A.to_4d()
        B4d = B.to_4d()

        curveData = bpy.data.curves.new('myCurve', type='CURVE')
        curveData.dimensions = '3D'
        curveData.resolution_u = 2

        polyline = curveData.splines.new('POLY')
        polyline.points.add(1)
        polyline.points[0].co = (A4d)
        polyline.points[1].co = (B4d)

        curveObj = bpy.data.objects.new('myCurve', curveData)

        view_layer = bpy.context.view_layer
        view_layer.active_layer_collection.collection.objects.link(curveObj)