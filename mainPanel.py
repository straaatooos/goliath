import bpy
from . import quantities
from . import Psets
    
class addPropOperator(bpy.types.Operator):
    bl_idname = "goliath.addprop"
    bl_label = "Add Property"
    bl_options = {'REGISTER', 'UNDO'}
    
    property_name: bpy.props.StringProperty()
    property_type: bpy.props.StringProperty()
    subject_type: bpy.props.StringProperty()
    
    def execute(self, context):
        if self.subject_type == "obj":
            objects = context.selected_objects
            for o in objects:
                o.goliathProps.add().name = self.property_name
                o.goliathProps[self.property_name].type = self.property_type
                
        elif self.subject_type == "mat":
            mat = bpy.context.object.material_slots[0].material
            mat.goliathProps.add().name = self.property_name
            mat.goliathProps[self.property_name].type = self.property_type
        
        return {'FINISHED'}
    
class removePropOperator(bpy.types.Operator):
    bl_label = "Remove Property"
    bl_idname = "goliath.removeprop"
    bl_options = {'REGISTER', 'UNDO'}
    
    property_name: bpy.props.StringProperty()
    subject_type: bpy.props.StringProperty()
    
    def execute(self, context):
        if self.subject_type == "obj":
            objects = context.selected_objects
            for o in objects:
                i = o.goliathProps.find(self.property_name)
                o.goliathProps.remove(i)
                
        elif self.subject_type == "mat":
            mat = bpy.context.object.material_slots[0].material
            i = mat.goliathProps.find(self.property_name)
            mat.goliathProps.remove(i)
        
        return {'FINISHED'}
    
class customPropGroup(bpy.types.PropertyGroup):
    # really? yes
    string: bpy.props.StringProperty()
    int: bpy.props.IntProperty()
    float: bpy.props.FloatProperty()
    bool: bpy.props.BoolProperty()
    #enum: bpy.props.EnumProperty()
    
    #type: bpy.props.EnumProperty()
    type: bpy.props.StringProperty()

    # make certainty categories configurable/individualized (maybe?)
    certainty_enum = [
        ("1", "1", "", 1),
        ("2", "2", "", 2),
        ("3", "3", "", 3),
        ("4", "4", "", 4)]

    certainty: bpy.props.EnumProperty(
        items=certainty_enum,
        description="Information certainty\n1 = guess\n2 = assumption\n3 = from document(s)\n4 = from field\nValue",
        default=4)#(default=5, min=1, max=5)
    
class storeyPropGroup(bpy.types.PropertyGroup):
    isFinished: bpy.props.BoolProperty()
    offset: bpy.props.FloatProperty()
    offsetObj: bpy.props.PointerProperty(type=bpy.types.Object)
    name: bpy.props.StringProperty()

class goliathMainPanel(bpy.types.Panel):
    bl_label = "Element Properties"
    bl_idname = "OBJECT_PT_goliath_mainpanel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_options = set({'HIDE_HEADER'})

 
    def draw(self, context):
        layout = self.layout
        activeobj = context.object
        type = activeobj.type

        match type:
            case "MESH":
                self.mesh(context, activeobj, layout)
            case "CAMERA":
                self.camera(activeobj, layout)
            case "EMPTY":
                self.group(context, activeobj, layout)

    def mesh(self, context, activeobj, layout):
        qlength = quantities.calc("length")[0]
        qarea = quantities.calc("area")[0]
        qvolume, warning = quantities.calc("volume")
        qcount = quantities.calc("count")[0]

        if "open" in warning:
            row = layout.row()
            row.label(icon="WARNING_LARGE")
            row.label(text="Mesh is not closed, quantities are not reliable")
        if "volumediscrepancy" in warning:
            row = layout.row()
            row.label(icon="WARNING_LARGE")
            row.label(text="Bounding Box is inaccurate, quantities are not reliable")

        # first box - type
        box = layout.box()
        if activeobj.elementTypeOverride == "(auto)":
            row = box.row()
            row.label(text=("Type: " + activeobj.elementType))
            row.prop(activeobj, "elementTypeOverride", text="")
        else:
            row = box.row()
            row.prop(activeobj, "elementTypeOverride", text="Type")
        
        try:
            parentname = activeobj.parent.name
            row = box.row()
            row.label(text="Part of: " + parentname)
        except:
            pass
        row = box.row()
        row.label(text="In Storey: " + activeobj.storey)

        if activeobj.elementType == "Slab":
            row = box.row()
            row.prop(activeobj, "isStorey", text="Is Storey")
        
        # if activeobj.isStorey == True: # first-and-a-half box - storey settings
        #     box = layout.box()
        #     box.label(text="Storey Settings")
        #     box.row().prop(activeobj.storeyProps, "name", text="Name")
        #     row=box.row()
        #     row.prop(activeobj.storeyProps, "isFinished", text="Is Finished")
        #     row.prop(activeobj.storeyProps, "offset", text="Offset")
        #     box.row().prop(activeobj.storeyProps, "offsetObj")

        
        # second box - quantities
        box = layout.box()
        box.label(text="Quantities (Selection)")
        box.row().label(text="Length: " + str(qlength) + "m")
        box.row().label(text="Area: " + str(qarea) + "m²")
        box.row().label(text="Volume: " + str(qvolume) + "m³")
        box.row().label(text="Count: " + str(qcount))
        dimstr = [str(x) for x in quantities.dimensions()]
        box.row().label(text="Dimensions (w/l/h): " + "m, ".join(dimstr) + "m")
        
        # third box - properties
        box = layout.box()    
        box.label(text="Object Properties")
        try:    
            self.propertyUI(activeobj, "obj", box)
        except AttributeError:
            pass
        
        # fourth box - material
        if len(activeobj.material_slots) > 0: 
            box = layout.box()
            box.label(text="Material")
            row = box.row()
            row.prop(context.object.material_slots[0], "material", text="")
            row.operator("material.new", icon="ADD", text="")
            try:
                self.propertyUI(context.object.material_slots[0].material, "mat", box)
            except AttributeError:
                pass

    def group(self, context, activeobj, layout):
        box = layout.box()
        # row = box.row()
        # types = []
        for o in activeobj.children:
            # if o.elementType not in types:
            #     types.append(o.elementType)
            box.row().label(text=(str(o.elementType)))
        # row.label(text=("Types: " + str(types)))
        
        try:
            parentname = activeobj.parent.name
            row = box.row()
            row.label(text="Part of: " + parentname)
        except:
            pass
        row = box.row()
        storeys = []
        for o in activeobj.children:
            if o.storey not in storeys:
                storeys.append(o.storey) # this is for multi-storey objects
        row.label(text="In Storeys: " + str(storeys)) # storey detector

        # second box - quantities
        box = layout.box()
        box.label(text="Quantities (Group)")
        box.row().label(text="Length: " + str(quantities.calc("length")) + "m")
        box.row().label(text="Volume: " + str(quantities.calc("volume")) + "m³")
        box.row().label(text="Area: " + str(quantities.calc("area")) + "m²")
        box.row().label(text="Count: " + str(quantities.calc("count")))
        
        # third box - properties
        box = layout.box()    
        box.label(text="Group Properties")
        self.propertyUI(activeobj, "obj", box)
    
    def propertyUI(self, obj, type, box):
        wm = bpy.context.window_manager        
        for i,p in enumerate(obj.goliathProps[:]):
            row = box.row()
            row.prop(p, p.type, text=p.name)
            row.prop(p, "certainty", text="")
            remove = row.operator("goliath.removeprop", icon="REMOVE", text="")
            remove.property_name = p.name
            remove.subject_type = type
            
        row = box.row()
        row.prop(wm, "myprop", text="")
        row.prop(wm, "myproptype", text="")
        add = row.operator("goliath.addprop", icon="ADD", text="")
        add.property_name = wm.myprop
        add.property_type = wm.myproptype
        add.subject_type = type

    def camera(self, activeobj, layout):
        activecam = activeobj.data
        # first box - type
        box = layout.box()
        box.row().label(text="Camera Dimensions")
        box.row().prop(activecam, "dim", index=0, text="Width")
        box.row().prop(activecam, "dim", index=1, text="Height")

    def setTypeAuto(self):
        bpy.context.object.elementType = bpy.context.object.elementTypeOverride

    def warningtype(self, obj):
        
        objvol = quantities.calc("volume")
        bboxvol = quantities.calc("volume")

proptypes_enum = [ # add "translations"
        ("int", "int", "", 1),
        ("float", "float", "", 2),
        ("string", "string", "", 3),
        ("bool", "bool", "", 4),]
        
elementtypes_enum = [ # make configurable
        ("(auto)", "(auto)", "", 0),
        ("Beam", "Beam", "", 1),
        ("Column", "Column", "", 2),
        ("Covering", "Covering", "", 3),
        ("Door", "Door", "", 4),
        ("Member", "Member", "", 5),
        ("Railing", "Railing", "", 6),
        ("Roof", "Roof", "", 7),
        ("Slab", "Slab", "", 8),
        ("Stair", "Stair", "", 9),
        ("Wall", "Wall", "", 10),
        ("Window", "Window", "", 11),
        ("Other", "Other", "", 12)]
        
def searchProps(self, context, edit_text): 
    type = context.object.elementType

    items = Psets.items(type) # un-hard-code this!!!
    
    return items

classes = [addPropOperator, removePropOperator, customPropGroup, storeyPropGroup, goliathMainPanel]
 
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.goliathProps = bpy.props.CollectionProperty(type=customPropGroup,name="Custom Props")
    bpy.types.Material.goliathProps = bpy.props.CollectionProperty(type=customPropGroup,name="Custom Props")
    bpy.types.Object.elementType = bpy.props.EnumProperty(items=elementtypes_enum)
    bpy.types.Object.elementTypeOverride = bpy.props.EnumProperty(items=elementtypes_enum)
    bpy.types.Object.storey = bpy.props.StringProperty()
    bpy.types.Object.isStorey = bpy.props.BoolProperty(
            name="is Storey",
            description="Whether the slab marks a Building Storey",
            default=False)
    bpy.types.Object.storeyProps = bpy.props.PointerProperty(type=storeyPropGroup,name="Storey Props")
    bpy.types.WindowManager.myprop = bpy.props.StringProperty(
            name="Prop Name",
            description="Name of the new Property",
            default="Name...",
            search = searchProps,
            )
    bpy.types.WindowManager.myproptype = bpy.props.EnumProperty(
            items=proptypes_enum, 
            name="Type", 
            description="Datatype of the new Property")
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.goliathProps
    del bpy.types.Material.goliathProps
    del bpy.types.Object.elementType
    del bpy.types.Object.elementTypeOverride
    del bpy.types.Object.storey
    del bpy.types.Object.isStorey
    del bpy.types.Object.storeyProps
    del bpy.types.WindowManager.myprop
    del bpy.types.WindowManager.myproptype