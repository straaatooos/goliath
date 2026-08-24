import bpy
import bmesh
import mathutils

from . import quantities
from . import scanobj

def autoCat(obj):
    # bmesh from baseObj
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)

    normals = []
    faces = []

    # prepare list for every direction of faces in mesh
    for face in bm.faces:
        if face.normal not in normals:
            normals.append(face.normal)

    # make a list of lists with one for each direction
    # add each face to one of the normal lists
    rows = len(normals)

    for x in range(rows):
        row = []
        faces.append(row)
        
    for face in bm.faces:
        row = normals.index(face.normal)
        faces[row].append(face)

    faceareas = [[face.calc_area() for face in row] for row in faces]

    areas=[]

    for row in faceareas:
        totalarea = 0    
        for area in row:
            totalarea += area
        areas.append(totalarea)

    sortedIs = [i[0] for i in sorted(enumerate(areas), key=lambda x:x[1], reverse=True)]

    normal = normals[sortedIs[0]]
    
    print("autoCat:")
    print(areas[sortedIs[0]])

# class autoCatOperator(bpy.types.Operator):
#     bl_idname = "goliath.autocat"
#     bl_label = "Auto-Categorize Object"

#     @classmethod
#     def poll(cls, context):
#         return context.active_object is not None
    
#     def execute(self, context):
#         for o in context.selected_objects:
#             if o.type == "MESH":
#                 self.autoCat()

#         return {'FINISHED'}
    
#     def autoCat(self):
#         activeobj = bpy.context.object

#         if activeobj.elementTypeOverride == "(auto)":
#             if quantities.calc("length") > 3:
#                 activeobj.elementType = "Beam"
#             else:
#                 activeobj.elementType = "Wall"
#         else:
#             bpy.context.object.elementType = bpy.context.object.elementTypeOverride

#     def drawCurve(A, B):
#         A4d = A.to_4d()
#         B4d = B.to_4d()

#         curveData = bpy.data.curves.new('myCurve', type='CURVE')
#         curveData.dimensions = '3D'
#         curveData.resolution_u = 2

#         polyline = curveData.splines.new('POLY')
#         polyline.points.add(1)
#         polyline.points[0].co = (A4d)
#         polyline.points[1].co = (B4d)

#         curveObj = bpy.data.objects.new('myCurve', curveData)

#         view_layer = bpy.context.view_layer
#         view_layer.active_layer_collection.collection.objects.link(curveObj)