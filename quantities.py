import bpy
import bmesh
import mathutils

def calc(type):
    quantity = 0
    warning = []
    
    if bpy.context.object.type == "EMPTY":
        selected = bpy.context.object.children
    else:
        selected = bpy.context.selected_objects
    
    for o in selected:
        baseName = o.name
        warningthresh = 1.2

        try:
            bpy.data.objects[baseName + "_bbox"]
            match type:
                case "length": # find a way to not have this doubled
                    me = bpy.data.objects[baseName + "_bbox"].data
                    bm = bmesh.new()
                    bm.from_mesh(me)

                    edges = [e for e in bm.edges[:]]
                    edges = sorted(edges, key=bmesh.types.BMEdge.calc_length)
                    edgelengths = [edges[0].calc_length(), edges[4].calc_length(), edges[8].calc_length()]
                    quantity += edgelengths[-1]
                    bm.free()

                case "area":
                    me = o.data
                    bm = bmesh.new()
                    bm.from_mesh(me)

                    faces = [f for f in bm.faces[:]]
                    faces = sorted(faces, key=bmesh.types.BMFace.calc_area)
                    totalarea = sum([f.calc_area() for f in faces])
                    quantity += totalarea
                    bm.free()

                case "volume":
                    me = o.data
                    bm = bmesh.new()
                    bm.from_mesh(me)
                    bmesh.ops.triangulate(bm, faces=bm.faces)

                    volume = 0
                    for f in bm.faces:
                        v1 = f.verts[0].co
                        v2 = f.verts[1].co
                        v3 = f.verts[2].co
                        volume += v1.dot(v2.cross(v3)) / 6
                    quantity += volume

                    for e in bm.edges:
                        if e.is_manifold == False:
                            warning.append("open")
                    bm.free()

                    me = bpy.data.objects[o.name + "_bbox"].data
                    bm = bmesh.new()
                    bm.from_mesh(me)
                    bmesh.ops.triangulate(bm, faces=bm.faces)

                    bboxvolume = 0
                    for f in bm.faces:
                        v1 = f.verts[0].co
                        v2 = f.verts[1].co
                        v3 = f.verts[2].co
                        bboxvolume += v1.dot(v2.cross(v3)) / 6
                    bm.free()

                    bboxvolume = abs(bboxvolume)
                    if warningthresh*bboxvolume < volume or bboxvolume/warningthresh > volume: # > warningthresh*bboxvolume
                        warning.append("volumediscrepancy")
                        # pass

                case "count":
                    quantity += 1
        except:
            quantity += 0

        quantity = round(quantity, 2)
    return quantity, warning

def dotZ(edge):
    z = mathutils.Vector((0,0,1))
    
    co1 = edge.verts[0].co
    co2 = edge.verts[1].co
    vector = (co1-co2)
    norm = vector.normalized()
    
    return abs(norm @ z)        
            
def dimensions():
    obj = bpy.context.object

    dim = [0,0,0] # width, length, height
    
    baseName = obj.name
    
    try:
        bpy.data.objects[baseName + "_bbox"]
        
        me = bpy.data.objects[baseName + "_bbox"].data
        bm = bmesh.new()
        bm.from_mesh(me)

        edges = [e for e in bm.edges[:]]
        edges = sorted(edges, key=bmesh.types.BMEdge.calc_length)
        edges = [edges[0], edges[4], edges[8]]

        if obj.elementType == 'Beam':
            dim[1] = edges[2].calc_length()
            edges.pop(2)
            edges = sorted(edges, key=dotZ)
            dim[0], dim[2] =  edges[0].calc_length(), edges[1].calc_length()
        else:
            edges = sorted(edges, key=dotZ)
            dim[2] = edges[2].calc_length()
            edges.pop(2)
            edges = sorted(edges, key=bmesh.types.BMEdge.calc_length)
            dim[0], dim[1] =  edges[0].calc_length(), edges[1].calc_length()

        bm.free()
        dim = [round(d, 2) for d in dim]

    except:
        pass

    return dim