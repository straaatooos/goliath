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
            linkedobjs = []
            for o in objects:
                if o not in linkedobjs:
                    for l in o.linked:
                        lnkobj = bpy.data.objects[l.name]
                        if lnkobj not in objects:
                            objects.append(lnkobj)
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
            linkedobjs = []
            for o in objects:
                if o not in linkedobjs:
                    for l in o.linked:
                        lnkobj = bpy.data.objects[l.name]
                        if lnkobj not in objects:
                            objects.append(lnkobj)

            for o in objects:
                i = o.goliathProps.find(self.property_name)
                o.goliathProps.remove(i)
                
        elif self.subject_type == "mat":
            mat = bpy.context.object.material_slots[0].material
            i = mat.goliathProps.find(self.property_name)
            mat.goliathProps.remove(i)
        
        return {'FINISHED'}
    
class customPropGroup(bpy.types.PropertyGroup):

    def update(self, type):
        objects = bpy.context.selected_objects
        linkedobjs = []
        for o in objects:
            if o not in linkedobjs:
                for l in o.linked:
                    lnkobj = bpy.data.objects[l.name]
                    if lnkobj not in objects and self.name in lnkobj.goliathProps:
                        objects.append(lnkobj)

            if self.name not in o.goliathProps:
                objects.remove(o)

        match type:
            case 'string':        
                for o in objects:
                    if o.goliathProps[self.name].string != self.string:
                        o.goliathProps[self.name].string = self.string
            case 'int':        
                for o in objects:
                    if o.goliathProps[self.name].int != self.int:
                        o.goliathProps[self.name].int = self.int
            case 'float':        
                for o in objects:
                    if o.goliathProps[self.name].float != self.float:
                        o.goliathProps[self.name].float = self.float
            case 'bool':        
                for o in objects:
                    if o.goliathProps[self.name].bool != self.bool:
                        o.goliathProps[self.name].bool = self.bool
            case 'certainty':        
                for o in objects:
                    if o.goliathProps[self.name].certainty != self.certainty:
                        o.goliathProps[self.name].certainty = self.certainty

    def upstring(self, context):
        self.update('string')
    def upint(self, context):
        self.update('int')
    def upfloat(self, context):
        self.update('float')
    def upbool(self, context):
        self.update('bool')
    def upcert(self, context):
        self.update('certainty')

    # really? yes
    string: bpy.props.StringProperty(update=upstring)
    int: bpy.props.IntProperty(update=upint)
    float: bpy.props.FloatProperty(update=upfloat)
    bool: bpy.props.BoolProperty(update=upbool)
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
        default=4, update=upcert)#(default=5, min=1, max=5)

class customPropGroupMat(bpy.types.PropertyGroup):
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
        objs = context.selected_objects
        qlength = quantities.calc("length",objs)[0]
        qarea = quantities.calc("area",objs)[0]
        qvolume, warning = quantities.calc("volume",objs)
        qcount = quantities.calc("count",objs)[0]

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

        types = []
        typecounts = []
        for o in activeobj.children: # this should theoretically be recursive?
            if o.elementType != 'Utility' and o.elementType != 'Opening':
                if o.elementType not in types:
                    types.append(o.elementType)
                    typecounts.append(0)
                typecounts[types.index(o.elementType)] += 1
        string = ''
        for t in types:
            string += t + ' (' + str(typecounts[types.index(t)]) + "); "
        if len(types) != 0:
            box.row().label(text=("Consists of: "+string))

        try:
            row = box.row()
            row.label(text="In Storey: " + context.scene.storeys[activeobj.storey].name)
        except:
            pass

        row = box.row()
        row.prop(activeobj, "showbbox", text="Show Bounding Box")


        if activeobj.elementType == "Slab":
            row = box.row()
            row.prop(activeobj, "isStorey", text="Is Storey")
        
        if activeobj.isStorey == True: # first-and-a-half box - storey settings
            box = layout.box()
            box.label(text="Storey Settings")
            box.row().prop(context.scene.storeys[activeobj.storey], "name", text="Name")

        
        # second box - quantities
        box = layout.box()
        box.label(text="Quantities (Selection)")
        box.row().label(text="Length: " + str(qlength) + "m")
        box.row().label(text="Area: " + str(qarea) + "m²")
        box.row().label(text="Volume: " + str(qvolume) + "m³")
        box.row().label(text="Count: " + str(qcount))
        dimstr = [str(x) for x in quantities.dimensions(activeobj)]
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
        types = []
        typecounts = []
        for o in activeobj.children: # this should theoretically be recursive?
            if o.elementType not in types:
                types.append(o.elementType)
                typecounts.append(0)
            typecounts[types.index(o.elementType)] += 1
        string = ''
        for t in types:
            string += t + ' (' + str(typecounts[types.index(t)]) + "); "
        box.row().label(text=(string))
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
        string = ''
        for s in storeys:
            string += context.scene.storeys[s].name + ", "
        row.label(text="In Storeys: " + string) # storey detector

        # second box - quantities
        objs = context.object.children
        box = layout.box()
        box.label(text="Quantities (Group)")
        box.row().label(text="Length: " + str(quantities.calc("length",objs)[0]) + "m")
        box.row().label(text="Volume: " + str(quantities.calc("volume",objs)[0]) + "m³")
        box.row().label(text="Area: " + str(quantities.calc("area",objs)[0]) + "m²")
        box.row().label(text="Count: " + str(quantities.calc("count",objs)[0]))
        
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
        box.row().prop(activecam, "dimscale", text="Scale                           1 :")# this seems stupid
        box.row().prop(activecam, "dpi", text="DPI")

    def setTypeAuto(self):
        bpy.context.object.elementType = bpy.context.object.elementTypeOverride

    # def warningtype(self, obj):
        
    #     objvol = quantities.calc("volume")
    #     bboxvol = quantities.calc("volume")

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
        ("Opening", "Opening", "", 12),
        ("Other", "Other", "", 13),
        ("Utility", "Utility", "", 14)]
        
def searchProps(self, context, edit_text): 
    type = context.object.elementType

    items = Psets.items(type) # un-hard-code this!!!
    
    return items

class storey(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Storey Name", default="Unnamed Storey")
    height: bpy.props.FloatProperty(name="Storey Height", default=0)

class propobject(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name (ID) of Object")

def elementTypeOverride_cb(self, context):
    for obj in context.selected_objects:
        if obj.elementTypeOverride != self.elementTypeOverride:
            obj.elementTypeOverride = self.elementTypeOverride

        if self.elementTypeOverride == '(auto)':
            scanobj.autoCat(obj)
        else:
            obj.elementType = obj.elementTypeOverride

from . import scanobj
def storey_cb(self, context):
    storeys = context.scene.storeys
    if self.isStorey == True:
        self.storey = 0
        height = scanobj.highpoint(self)
        newstorey = storeys.add()
        newstorey.name = str(height)
        newstorey.height = height

        for i,s in enumerate(storeys): # sort by height
            heights = [s.height for s in storeys]
            indices = [i[0] for i in sorted(enumerate(heights), key=lambda x:x[1])]
            storeys.move(indices[i], i)

    else:
        storeys.remove(self.storey)

    # scanobj.setstoreys()
    for o in bpy.data.objects:
        try:
            scanobj.putinstorey(o)
        except:
            pass

def bbox_cb(self, context):
    for obj in context.selected_objects:
        scanobj.main(obj)

class replacepanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_test_1"
    bl_label = "Replace"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Replace"

    @classmethod
    def poll(cls, context):
        return (context.object is not None)
    
    def draw(self, context):
        row = self.layout.row()
        row.label(text="Replace Source Object/Family")
        # row = self.layout.row()
        # row.operator("goliath.addprop", icon='ADD', text="")
        row = self.layout.row()
        row.prop(context.scene, "replacesource", text="")

classes = [addPropOperator, removePropOperator, customPropGroup, customPropGroupMat,
           storeyPropGroup, goliathMainPanel, storey, propobject, replacepanel]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.goliathProps = bpy.props.CollectionProperty(type=customPropGroup,name="Custom Props")
    bpy.types.Material.goliathProps = bpy.props.CollectionProperty(type=customPropGroupMat,name="Custom Props")
    bpy.types.Object.elementType = bpy.props.EnumProperty(items=elementtypes_enum)
    bpy.types.Object.elementTypeOverride = bpy.props.EnumProperty(items=elementtypes_enum, update=elementTypeOverride_cb)
    bpy.types.Object.storey = bpy.props.IntProperty()
    bpy.types.Object.isStorey = bpy.props.BoolProperty(
            name="is Storey",
            description="Whether the slab marks a Building Storey",
            default=False,
            update=storey_cb)
    #bpy.types.Object.storeyProps = bpy.props.PointerProperty(type=storeyPropGroup,name="Storey Props")
    bpy.types.Object.euler = bpy.props.FloatVectorProperty(name='Main Normal Axis', default=(0.0,0.0,1.0))
    bpy.types.Object.location_relative = bpy.props.FloatVectorProperty(name='Location Relative to Parent', default=(0,0,0))
    bpy.types.Object.pka = bpy.props.StringProperty(name='Previous Name')
    bpy.types.Object.linked = bpy.props.CollectionProperty(type=propobject,name="Linked Objects")
    bpy.types.Object.showbbox = bpy.props.BoolProperty(name="Show Bounding Box",default=False,update=bbox_cb)
    
    bpy.types.Scene.storeys = bpy.props.CollectionProperty(type=storey)
    bpy.types.Scene.replacesource = bpy.props.PointerProperty(type=bpy.types.Object)
    bpy.types.Scene.demolish = bpy.props.CollectionProperty(type=propobject)

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
    #del bpy.types.Object.storeyProps
    del bpy.types.Object.euler
    del bpy.types.Object.location_relative
    del bpy.types.Object.pka
    del bpy.types.Object.linked
    del bpy.types.Object.showbbox

    del bpy.types.Scene.storeys
    del bpy.types.Scene.replacesource
    del bpy.types.Scene.demolish

    del bpy.types.WindowManager.myprop
    del bpy.types.WindowManager.myproptype