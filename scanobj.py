import bpy
import bmesh
import mathutils

from . import quantities

def main(obj):
    if ( # exclude objects
        obj.type == "MESH" and
        obj.name != "0" and
        obj.name.endswith("_bbox") is False
        ):
        bboxObject(obj)
        bboxGeo(obj)
        materialSlot(obj)
        putinstorey(obj)
        autoCat(obj)
        if obj.isStorey is True:
            setstoreys()

def bboxObject(baseObj):
    baseName = baseObj.name
    hasBbox = False

    # check if there already is a bbox object
    # !!! this needs to work with renamed objects of course, do this later
    for obj in baseObj.children:
        if obj.name.endswith("_bbox") is True:
            hasBbox = True

    if hasBbox is False:
        # add a new empty mesh
        mesh = bpy.data.meshes.new(baseName + "_bbox")
        # add a new object with the empty mesh 
        obj = bpy.data.objects.new(baseName + "_bbox", mesh)
        # link to scene/view layer
        view_layer = bpy.context.view_layer
        view_layer.active_layer_collection.collection.objects.link(obj)
        # make child of baseObj
        obj.parent = baseObj
        obj.display_type = "WIRE"
        obj.hide_select = True
        obj.color = baseObj.color
        obj.location = baseObj.location
    else:
        # else clear existing bbox geometry
        me = bpy.data.objects[baseName + "_bbox"].data
        bm = bmesh.new()
        bm.from_mesh(me)
        bm.clear()
        bm.to_mesh(me)
        bm.free
        obj.color = baseObj.color
        obj.location = baseObj.location

def bboxGeo(obj):
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

    # calculate stuff

    faceareas = [[face.calc_area() for face in row] for row in faces]
    #facecenters = [[face.calc_center_bounds() for face in row] for row in faces]

    #areas = calculator(faceareas, False, False)
    #centers = calculator(facecenters, True, True)

    areas=[]

    for row in faceareas:
        totalarea = 0    
        for area in row:
            totalarea += area
        areas.append(totalarea)

    sortedIs = [i[0] for i in sorted(enumerate(areas), key=lambda x:x[1], reverse=True)]

    normal = normals[sortedIs[0]]
    myverts = []
    for f in faces[sortedIs[0]]:
        for v in f.verts:
            myverts.append(v)

    myverts = list(set(myverts))
    
    zvec = (0,0,1)
    angle = normal.angle(zvec)
    axis = normal.cross(zvec)
    rotMat = mathutils.Matrix.Rotation(angle, 4, axis)
    rotMatReverse = mathutils.Matrix.Rotation(-angle, 4, axis)
    
    cent = (0,0,0)
    
    # rotate to xy plane
    bmesh.ops.rotate(bm, cent=cent, matrix=rotMat, verts=myverts)
    
    offset = myverts[0].co.z

    # get vertex coordinates in 2d
    points2d = []
    for v in myverts:
        points2d.append((v.co.x,v.co.y))

    # get fit rotation (xy plane) angle and rotate
    fitAngle = mathutils.geometry.box_fit_2d(points2d)

    rotMatFit = mathutils.Matrix.Rotation(fitAngle, 4, 'Z')
    rotMatFitReverse = mathutils.Matrix.Rotation(-fitAngle, 4, 'Z')
    bmesh.ops.rotate(bm,cent=(0,0,0),matrix=rotMatFit,verts=myverts)

    # store new (=rotated) coordinates and make box base points
    co = []
    for v in myverts:
        co.append(v.co)
    
    x = [v.x for v in co]
    y = [v.y for v in co]
    
    x=sorted(x)
    y=sorted(y)
    
    p1 = (x[0],y[0],0)
    p2 = (x[0],y[-1],0)
    p3 = (x[-1],y[-1],0)
    p4 = (x[-1],y[0],0)
    
    points = [p1,p2,p3,p4]

    # reverse the rotation to avoid a 6 hour bug search
    bmesh.ops.rotate(bm,cent=(0,0,0),matrix=rotMatFitReverse,verts=myverts) 
    bmesh.ops.rotate(bm,cent=(0,0,0),matrix=rotMatReverse,verts=myverts)

    # make actual box
    me = bpy.data.objects[obj.name + "_bbox"].data
    bm1 = bmesh.new()
    bm1.from_mesh(me)
    
    myverts = []

    for p in points:
        verts = bm1.verts.new(p)
        myverts.append(verts)
    
    baseface = bm1.faces.new(myverts)
    baseface.normal = (0,0,1)
    
    bmesh.ops.translate(bm1, vec=(0,0,offset), verts=myverts)
    
    bmesh.ops.rotate(bm1,cent=(0,0,0),matrix=rotMatFitReverse,verts=myverts)
    
    bmesh.ops.rotate(bm1,cent=(0,0,0),matrix=rotMatReverse,verts=myverts)
    
    C = baseface.calc_center_bounds()
    B = baseface.normal

    # extrude ...
    
    mindot = 0
    maxdot = 0
    fac = 0

    for v in bm.verts:
        A = C-v.co
        r = A @ B
        if r > maxdot:
            maxdot = r
        if r < mindot:
            mindot = r

    if abs(mindot)>maxdot:
        fac = mindot
    else:
        fac = maxdot

    bm.free()

    extruded = bmesh.ops.extrude_discrete_faces(bm1, faces=[baseface])
    extruded = extruded["faces"][0].verts[:]
    bmesh.ops.translate(bm1, verts=extruded, vec=fac*(-B))
    newface = bm1.faces.new(myverts) # this face disappears sometimes for an unknown reason
    newface.normal_flip()

    bm1.to_mesh(me)
    bm1.free()

def materialSlot(obj):
    if len(obj.material_slots) < 1:
        obj.data.materials.append(bpy.data.materials[-1])
        obj.material_slots[0].material = None

def setstoreys():
    storeyheights = []
    storeynames = []

    for obj in bpy.data.objects:
        baseName = obj.name
        if obj.isStorey is True:
            me = bpy.data.objects[baseName + "_bbox"].data
            bm = bmesh.new()
            bm.from_mesh(me)

            vertZs = [v.co.z+obj.location.z for v in bm.verts[:]]
            vertZs = sorted(vertZs)
            height = vertZs[-1]

            storeyheights.append(height)
            obj.storeyProps.name = str(round(height,2))
            storeynames.append(obj.storeyProps.name)
            bm.free()

    if len(storeyheights) == 0:
        bpy.types.Scene.storeyheights = [0]
        bpy.types.Scene.storeynames = ["0"]
    else:
        bpy.types.Scene.storeyheights = storeyheights
        bpy.types.Scene.storeynames = storeynames

    for o in bpy.data.objects:
        try:
            putinstorey(o)
        except:
            pass

def putinstorey(obj):
    if obj.type == "MESH":
        if obj.isStorey == True:
            obj.storey = obj.storeyProps.name
        else:
            inStoreys = [] # todo: integrating mulit-storey objects
            storeyheights = bpy.types.Scene.storeyheights
            storeynames = bpy.types.Scene.storeynames

            me = bpy.data.objects[obj.name + "_bbox"].data
            bm = bmesh.new()
            bm.from_mesh(me)

            vertZs = [v.co.z for v in bm.verts[:]]
            vertZs = sorted(vertZs)

            bm.free()

            lowpoint,highpoint = 0,0

            for i,h in enumerate(storeyheights):
                if vertZs[0] > h:
                    lowpoint = i
                if vertZs[-1] > h:
                    highpoint = i
            
            if lowpoint == highpoint:
                inStoreys = [lowpoint]
            else:
                inStoreys = [lowpoint, highpoint]

            obj.storey = storeynames[lowpoint]

def autoCat(obj):
    obj = bpy.context.object

    if obj.elementTypeOverride == "(auto)":
        if quantities.calc("length")[0] > 3:
            obj.elementType = "Beam"
        else:
            obj.elementType = "Wall"
    else:
        bpy.context.object.elementType = bpy.context.object.elementTypeOverride