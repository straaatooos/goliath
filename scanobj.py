import bpy
import bmesh
import mathutils

from . import quantities

def main(obj):
    correctmatrix(obj)
    obj.pka = obj.name
    if ( # exclude objects
        obj.type == "MESH" and
        obj.name != "0" and
        obj.name.find("_bbox") < 0
        ):
        bboxObject(obj)
        if 2 < len(obj.data.polygons) < 500: #make config
            bboxGeo(obj)
            putinstorey(obj)
            materialSlot(obj)
            fixopenings(obj)
        # if obj.isStorey is True:
        #     setstoreys()
    if obj.elementTypeOverride == '(auto)':
        autoCat(obj)
    pass

def correctmatrix(obj):
    M = mathutils.Matrix.Identity(4)
    if obj.matrix_parent_inverse != M:
        N = obj.matrix_parent_inverse - M
        obj.matrix_parent_inverse = M
        obj.matrix_basis += N

def bboxObject(baseObj):
    baseName = baseObj.name
    hasBbox = False

    # check if there already is a bbox object
    # !!! this needs to work with renamed objects of course, do this later
    for o in baseObj.children:
        if o.name.endswith("_bbox") is True:
            hasBbox = True

    if hasBbox is False:
        try:
            obj = bpy.data.objects[baseName + '_bbox']
        except:
            # add a new empty mesh
            mesh = bpy.data.meshes.new(baseName + "_bbox")
            # add a new object with the empty mesh
            obj = bpy.data.objects.new(baseName + "_bbox", mesh)
            # link to scene/view layer
            try:
                for c in baseObj.users_collection:
                    c.objects.link(obj)
            except:
                print("object probably already in some collection")
        # make child of baseObj
        obj.parent = baseObj
        obj.display_type = "WIRE"
        obj.hide_select = True
        obj.hide_render = True
        if baseObj.hide_get() == True:
            obj.hide_set(True)
        else:
            if baseObj.showbbox == False:
                obj.hide_set(True)
            else:
                obj.hide_set(False)

        obj.color = baseObj.color
        obj.matrix_world = baseObj.matrix_world*1

        #obj.elementTypeOverride = 'Utility'
        obj.elementType = 'Utility'

    else:
        # else clear existing bbox geometry
        obj = bpy.data.objects[baseName + '_bbox']
        me = bpy.data.objects[baseName + "_bbox"].data
        bm = bmesh.new()
        bm.from_mesh(me)
        bm.clear()
        bm.to_mesh(me)
        bm.free
        obj.color = baseObj.color
        obj.matrix_world = baseObj.matrix_world*1

        try:
            for c in baseObj.users_collection:
                c.objects.link(obj)
        except:
            print("object probably already in some collection")

        obj.display_type = "WIRE"
        obj.hide_select = True
        obj.hide_render = True
        if baseObj.hide_get() == True:
            obj.hide_set(True)
        else:
            if baseObj.showbbox == False:
                obj.hide_set(True)
            else:
                obj.hide_set(False)

        #obj.elementTypeOverride = 'Utility'
        obj.elementType = 'Utility'

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

    xvec = (1,0,0)
    yvec = (0,1,0)
    zvec = (0,0,1)

    # when object normal is NOT close to world Z aka the object is NOT flat (e.g. a slab)
    sortednormals = sorted(normals, key=lambda x:x.angle(zvec))
    oX = normal
    oZ = sortednormals[0]

    if oX.cross(oZ).magnitude == 0:   
        # when object normal IS close to world Z aka the object IS flat (e.g. a slab)
        sortednormals = sorted(normals, key=lambda x:x.angle(xvec))
        oX = sortednormals[0]

    if oX[0] < 0:
        oX *= -1

    oY = oX.cross(oZ)
    if oY.xy.angle_signed(oX.xy) < 0:
        oY *= -1

    objMat = mathutils.Matrix((oX, oY, oZ))

    print("bboxGeo:")
    print(objMat)
    print(objMat.to_euler())

    obj.euler = objMat.to_euler()

    myverts = []
    for f in faces[sortedIs[0]]:
        for v in f.verts:
            myverts.append(v)

    myverts = list(set(myverts))
    
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

def fixopenings(obj):
    i = 0
    for m in obj.modifiers:
        if m.type == "BOOLEAN":
            mobj = m.object
            i += 1
            if mobj is None:
                obj.modifiers.remove(m)
                i -= 1
            m.name = "Opening"+str(i)
            mobj.name = obj.name + "_opening"
            mobj.data.name = mobj.name
            mobj.children[0].name = mobj.name + "_bbox"

def materialSlot(obj):
    if len(obj.material_slots) < 1:
        obj.data.materials.append(bpy.data.materials[-1])
        obj.material_slots[0].material = None

def highpoint(obj):
    # storeyheights = []
    # storeynames = []

    # for obj in bpy.data.objects:
    bpy.context.view_layer.update()
    objloc = obj.matrix_world.to_translation()
    baseName = obj.name
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)

    vertZs = [v.co.z+objloc[2] for v in bm.verts[:]]
    vertZs = sorted(vertZs)
    height = vertZs[-1]

    return height

    #         storeyheights.append(height)
    #         obj.storeyProps.name = str(round(height,2))
    #         storeynames.append(obj.storeyProps.name)
    #         bm.free()

    # if len(storeyheights) == 0:
    #     bpy.types.Scene.storeyheights = [0]
    #     bpy.types.Scene.storeynames = ["0"]
    # else:
    #     bpy.types.Scene.storeyheights = storeyheights
    #     bpy.types.Scene.storeynames = storeynames

    # for o in bpy.data.objects:
    #     try:
    #         putinstorey(o)
    #     except:
    #         pass

def putinstorey(obj):
    #bpy.context.view_layer.update()
    tol = 0.001
    objloc = obj.matrix_world.to_translation()

    if obj.type == "MESH":
        inStoreys = [] # todo: integrating mulit-storey objects
        storeyheights = [storey.height for storey in bpy.context.scene.storeys]
        storeynames = [storey.name for storey in bpy.context.scene.storeys]

        me = obj.data
        bm = bmesh.new()
        bm.from_mesh(me)

        vertZs = [v.co.z+objloc[2] for v in bm.verts[:]]
        vertZs = sorted(vertZs)

        bm.free()

        lowpoint,highpoint = 0,0

        for i,h in enumerate(storeyheights):
            if vertZs[0] > h-tol:
                lowpoint = i
            if vertZs[-1] > h-tol:
                highpoint = i
        
        if lowpoint == highpoint:
            inStoreys = [lowpoint]
        else:
            inStoreys = [lowpoint, highpoint]

        if obj.elementType == "Slab":
            obj.storey = highpoint
        else:
            obj.storey = lowpoint #storeynames[lowpoint]

def autoCat(obj):
    if obj.type == 'MESH':
        if obj.name.find("_opening") > 0 and obj.name.find("_bbox") < 0:
            obj.elementType = 'Opening'

        else:

            # bmesh from baseObj
            me = obj.data
            bm = bmesh.new()
            bm.from_mesh(me)

            volume = quantities.calc('volume',obj)[0]

            if volume > 20:
                obj.elementType = 'Other'
            else:
                normals = []
                faces = []
                edges = []

                

                # prepare list for every direction of faces in mesh
                for face in bm.faces:
                    if face.normal not in normals:
                        normals.append(face.normal)

                for edge in bm.edges:
                    edges.append(edge)

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

                sortededges = sorted(edges, key=lambda x:x.calc_length())
                

                principalarea = areas[sortedIs[0]]
                totalarea = sum(areas)
                principalnormal = normals[sortedIs[0]]

                print("autoCat:")
                print(principalarea)
                print(totalarea)
                print(principalnormal)

                z = mathutils.Vector((0,0,1))
                dim = quantities.dimensions(obj)
                print(dim)

                if sum(dim) == 0:
                    obj.elementType = 'Utility'

                elif totalarea/principalarea < 2.7:
                    
                    fac = abs(principalnormal@z)
                    if fac > 0.95:
                        if dim[2] < 0.04:
                            obj.elementType = 'Covering' # should this be 'Floor'?
                        else:
                            obj.elementType = 'Slab'

                    elif fac < 0.05:
                        if dim[0] < 0.1:
                            obj.elementType = 'Covering'
                        else:
                            obj.elementType = 'Wall'
                    else:
                        obj.elementType = 'Roof'

                elif totalarea/principalarea > 2.7:
                    dotZ = quantities.dotZ(sortededges[-1])
                    
                    if dotZ > 0.95:
                        obj.elementType = 'Column'
                    elif dotZ < 0.05:
                        obj.elementType = 'Beam'
                    else:
                        obj.elementType = 'Member'

                else:
                    obj.elementType = 'Other'

    else:
        obj.elementType = 'Utility'