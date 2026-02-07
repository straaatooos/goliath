import bpy
import bmesh
import mathutils

def conObject():
    # check if there already is a 0 object
    if "0" not in bpy.context.scene.objects:
        # add a new empty mesh
        mesh = bpy.data.meshes.new("0")
        # add a new object with the empty mesh 
        obj = bpy.data.objects.new("0", mesh)
        # link to scene/view layer
        view_layer = bpy.context.view_layer
        view_layer.active_layer_collection.collection.objects.link(obj)
        obj.hide_select = True
        obj.color = [1,0.25,0.1,0.3]

class conLinesClearOperator(bpy.types.Operator):
    bl_idname = "goliath.conlinesclear"
    bl_label = "Clear Construction Lines"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        # clear existing geometry
        try:
            bpy.data.objects["0"]
            obj0 = bpy.data.objects["0"]
            me = obj0.data
            bm = bmesh.new()
            bm.from_mesh(me)
            bm.clear()
            bm.to_mesh(me)
            bm.free()
                
            for obj in obj0.children:
                bpy.data.objects.remove(obj)
        except:
            pass

        bpy.types.Scene.conlinesequence = [] # the "history" is saved here

        try:
            bpy.context.scene.transform_orientation_slots[0].type = "Con Line"  # make configurable (maybe)
            bpy.ops.transform.delete_orientation()
        except:
            pass

        return {'FINISHED'}


class conLinesOperator(bpy.types.Operator):
    bl_idname = "goliath.conlines"
    bl_label = "Add Construction Lines"

    @classmethod
    def poll(cls, context):
        return context.object.mode == "EDIT"

    def execute(self, context):
        vertcount = len(bpy.data.objects["0"].data.vertices)

        self.duplicator()

        vertcount = len(bpy.data.objects["0"].data.vertices)-vertcount
        sequence = bpy.types.Scene.conlinesequence
        sequence.append(vertcount) # add to history

        if len(sequence) > 3: # when used more than X times, remove everything from the first usage
                              # make X configurable

            # clear existing geometry
            obj0 = bpy.data.objects["0"]
            me = obj0.data
            bm = bmesh.new()
            bm.from_mesh(me)
            verts = []
            bm.verts.ensure_lookup_table()
            print(sequence[0])
            for i in range(sequence[0]):
                verts.append(bm.verts[i])
            bmesh.ops.delete(bm, geom=verts)
            bm.to_mesh(me)
            bm.free()

            for i in range(sequence[0]-2):
                bpy.data.objects.remove(obj0.children[0])
            for o in obj0.children:
                o.name = "intersection" # make configurable

            del sequence[0]

        return {'FINISHED'}

    def editImaginaryMesh(self, newedges):
        obj0 = bpy.data.objects["0"]
        me = obj0.data
        bm1 = bmesh.new()
        bm1.from_mesh(me)
        
        self.intersector(bm1, newedges)
            
        newedgeco = [newedges.verts[0].co, newedges.verts[1].co]
        newedgeverts = [bm1.verts.new(newedgeco[0]), bm1.verts.new(newedgeco[1])]
        bm1.edges.new(newedgeverts)
        
        bm1.to_mesh(me) 
        bm1.free()
        
    def intersector(self, bm, newedge): # this finds intersections between newedge and bm, bm in this case is "0" mesh
        obj0 = bpy.data.objects["0"]
        edges = [e for e in bm.edges]
        verts = []

        [u1, u2] = [vertex.co for vertex in newedge.verts]
        
        for edge in edges:
            [v1, v2] = [vertex.co for vertex in edge.verts]

            iv = mathutils.geometry.intersect_line_line(u1, u2, v1, v2)
            if iv != None:
                iv = (iv[0] + iv[1]) / 2
                
                a = iv - u1
                b = iv - u2
                c = u1 - u2
                d = iv - v1
                e = iv - v2
                f = v1 - v2
                
                threshold = 0.0001 # tolerance because all this is sometimes not 100% precise, make configurable
                if a.length + b.length - c.length < threshold and d.length + e.length - f.length < threshold:
                # this if: and a,b,c,d,e,f were supposed to prevent faulty intersection points, not sure if it is obsolete
                # maybe test disabling this (there had to have been a reason though)

                    verts.append(bm.verts.new(iv))

                    # add empty object to mark the point
                    empty = bpy.data.objects.new("intersection", None) # make name configurable (used a couple lines up as well)
                    view_layer = bpy.context.view_layer
                    view_layer.active_layer_collection.collection.objects.link(empty)
                    empty.location = iv
                    empty.parent = obj0
                    empty.empty_display_size = 0.1 # make configurable
                    empty.show_in_front = True
                        
        return verts
                        
    def duplicator(self):
        me = bpy.context.object.data

        bm = bmesh.from_edit_mesh(me)

        # save the previous state to return to after usage
        prevmode = bpy.context.tool_settings.mesh_select_mode[:]
        prevselect = [v for v in bm.verts if v.select == True]
        prevselect.extend([e for e in bm.edges if e.select == True])
        prevselect.extend([f for f in bm.faces if f.select == True])

        bpy.context.tool_settings.mesh_select_mode = (False, True, False)
        bpy.ops.mesh.select_all(action='DESELECT')

        bpy.ops.view3d.select('INVOKE_DEFAULT')

        try:
            bpy.ops.transform.delete_orientation() # if there is a custom orientation, delete it
        except:
            pass
        bpy.ops.transform.create_orientation(name="Con Line", use=False, overwrite=True)

        bm = bmesh.from_edit_mesh(me)
        for v in bm.verts:
            v.co += bpy.context.object.location # move from 0,0,0 to object position

        selected = [v for v in bm.verts if v.select == True]
        
        if len(selected)>1: # this is not necessary, originally this was meant to be used with either verts(1)/edges(2)/faces(>2)
                            # maybe this can be implemented later

            selectedverts = [vert.co for vert in selected]

            midpoint = mathutils.Vector((0,0,0))

            for vert in selected:
                midpoint += vert.co

            midpoint = midpoint/len(selectedverts)

            mat_loc = mathutils.Matrix.Translation(-midpoint)

            selected0 = bmesh.ops.duplicate(bm, geom=selected)

            geomdupe = selected0["geom"]
            mygeom = [ele for ele in geomdupe # this is old code, probably can be improved
                            if isinstance(ele, bmesh.types.BMVert)]
                            
            scalevec = mathutils.Vector((1,1,1))
            scalevec *= 200 # scale factor, make configurable
                        
            bmesh.ops.scale(bm,vec=scalevec,space=mat_loc,verts=mygeom)

            if len(mygeom) == 2:
                newedges = bm.edges.new(mygeom)
            if len(mygeom) > 2: # same as the other if: this was only necessary if usage with faces had been implemented
                bm.faces.new(mygeom)
                
            for vertex in selected:
                vertex.select = False

            self.editImaginaryMesh(newedges) # send geometry to "0" mesh
            
            bmesh.ops.delete(bm, geom=newedges.verts)
        
        for ele in prevselect:
            ele.select = True

        for v in bm.verts:
            v.co -= bpy.context.object.location # move back to original position
        bmesh.update_edit_mesh(me)
        bm.free()

        bpy.context.tool_settings.mesh_select_mode = prevmode

classes = [conLinesClearOperator, conLinesOperator]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.conlinesequence = []

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.conlinesequence