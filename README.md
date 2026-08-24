Hello OS Arch community, developer, interested individual

Here are some raw, more technical notes about the "Goliath" project.  

**For a project overview, see: https://community.osarch.org/discussion/3328/sketch-prototype-of-a-lightweight-h-bestands-bim-software-in-blender (outdated/incomplete)**

**User-oriented video introduction: https://youtu.be/9bOEjacAUMQ (outdated/incomplete)**

I also want to preface this by saying: I am an architecture student, not a developer by trade. I started this term with a bit of experience in programming mainly from small free time projects, but having close to no experience with Python or the Blender API. The code probably has a lot of room for improvement. Also, this is by no means intended to be a finished "product", but more of a demonstrator or prototype.

I will try to keep this up to date.

Thanks for your interest,

Julian "straaatooos" Hüther



### Changes to native Blender operations

**Object/Mesh logic**  
To avoid confusion, the general idea is to not have two different parameters that work on the same thing (geometry or other).
Object Scale and Rotation are automatically applied in Edit Mode and Object Origins are automatically moved to center of geometry when the Mesh is edited. This is to ensure that all edit mode lengths are real lengths, ~~that there is only one method of rotating geometry and to avoid confusion with offset object origins.~~

Notes:
- *Object-level rotation is necessary/useful for the Object logic explained in the next section, but it should be geometry based, at least in a soft way. Implementing this is already prepared through the Object.euler property. Will probably lead to issues/chaos at first.*
- *Having the object origin at the geometric center was easy to implement but is not ideal, because it changes at basically every modification. Find an alternative in the future.*

**Object/Mesh Separation**  
~~When done editing Meshes (on leaving Edit Mode), any unconnected geometry is separated into its own Object. This is done to force users into having a dedicated Object and thereby Properties for any separate piece of geometry.~~

Notes:
- *Turned out, of course, to be very impractical, especially when working on other things than BIM objects (which should still be possible). Vertex Groups could still be a way to go. Also see Additions - Object hierarchies.*

**Recursive Parent Object handling**
~~When working on Objects with Child Objects attached to it, using Duplicate duplicates the whole Parent/Child structure; using Remove removes the whole Parent/Child Structure~~ *(changed and moved to following section)*

**Edit Mode translation**  
When editing a Mesh in Face mode, using Grab automatically uses the normal axis of the face.

Notes:
- Think about whether default settings like this may be useful for Edge or Vertex mode as well


### Additions

**Object Properties**  
Generally, the geometric building model is assumed to consist of Mesh and Curve Objects. All of the following functions were worked on with Meshes in mind. It is not impossible for them to work for other Types of Objects, but unlikely.

**Element Types**  
Every Object has an Element Type. The integrated types were chosen based on IfcElement types, but several of the Ifc types were omitted to not overwhelm and slow down users, focusing on typically relevant types for smaller scale architecture.(Yes, this is almost exactly the IfcBuidlingElements selection, with a few exceptions.)

Notes:
- ~~Evaluate the choice of types~~ *'Opening' and 'Utility' Element Types were added. The intention above remains, try to prevent adding too many Types.*

**Primitive Type Detection**  
An Object's type is automatically determined based on its geometry, after editing said geometry. This automatic determination can be overridden.

Notes:
- The rules/heuristics of determining an object type can and probably should become more robust, while not increasing complexity to an unreasonable level. It does not need to be perfect, the override function exists for a reason, failure is expected.
- Said rules could become customizable

**Storeys**
Objects of Type Slab can be made to mark Storeys. Storey height is then set to the topmost (Global Z) Face of the Mesh. Every Object is put in one of the Storeys present in the Project based on the height. *The Storey Name (and possibly more properties in the future) can be specified in the Object.*

Notes:
- Non-Slab Storeys are not yet possible, maybe add Empty-based Storeys (as a secondary alternative!)
- Objects can only be in one Storey; should it be possible for them to be in multiple, in none?

**Custom "Goliath" Properties**
Similarly to native Blender, (Mesh) Objects and Materials can have custom properties, with respective property types. Additionally, each property has a certainty value attached to it, informing about the source and reliability of the property. These Properties represent what would be in Psets in traditional BIM software, which is why "Goliath" automatically suggests the Pset*Type*Common property names when adding a property.
The goal was to remove the "hurdle" of creating and managing Psets, again simplifying and accelarating the working process.

Notes:
- Having Psets can of course be useful and they should be integrated eventually. But handling them should remain as simple and quick as it is now. (Could this be handled with naming conventions?)
- Properties could have an Element Type setting that determines which Objects can/should have the property and which should not.
- When using a Pset*Type*Common property, the property type needs to be set accordingly.
- Previously added custom properties are not included in the name search pool

**Oriented Bounding Boxes**  
Every Mesh Object is automatically put in an Object Oriented Bounding Box. This Bounding Box is used to determine type and dimensions/proportions. (The current algorithm for this is simple: it groups faces according to orientation, the largest area sum is used to draw the base of the box and it is extruded until it encloses the furthest vertex. See code for more.) This approach of course does not work with all geometries. When the difference between the Bounding Box and the Mesh is too great, calculating the quantities will generate a warning (see Object Panel).

Future:
- The Bounding Box algorithm can be improved and made more robust. Unlike with Auto Types, there is no override for this, so it is desirable to have a near perfectly robust algorithm. The only limiting factor is software performance.

**Quantities and Dimensions**
Using the Mesh and aforementioned Bounding Box geometry, four quantities can be calculated: Length; Area (of all Mesh faces); Volume; Object Count. As mentioned, dimensions are also determined from the Bounding Box.

Notes:
- Different configurations for quantities could be added, similar to Quantity Takeoff. (This is probably especially interesting when calculating areas - for this it would be nice to see which Faces are counted and which are not.) This should however never replace current Area calculation, since it is already very useful when it just counts all the face areas.
- Volume calculation only works if the Mesh is "perfect" (closed and all normals pointing in the right direction). Right now the solution is just a warning, but could the calculation algorithm be more robust?
- *Quantities work on the unmodified Mesh. This should be changed to consider the Mesh with its Modifiers applied (see Openings)*

**Object Panel**  
This Panel is - like other aspects of this project - inspired by existing architectural/CAD software.
It delivers all aforementioned information and properties to the user the moment an Object is selected. Quantities are updated live and summed up across the selection. Properties can be named, added and removed with one click respectively. The whole Panel is intended to be visible without scrolling. The aim is for users to be able to understand everything "at first glance". Descriptions are displayed when hovering, just as with Blender's native properties. The Panel changes with the type of Object selected (e.g. Group Objects, see Grouping).

Notes:
- For the object count, show how many of each type.
- Type override has no description yet.

**Object Notes**
On Object selection, a note Text is generated for the Object, if there is not yet one. It is automatically displayed in the bottom right corner of the window in the "Goliath" workspace. In it, users can write plain text about anything concerning the object.

Notes:
- *Notes should probably be linked to their objects by some property other than their name. This could also enable Notes being attached to multiple Objects.*
- Maybe it could be useful to have Notes that are not linked to Objects?
- It would be great if Notes could contain links (like a hyperlink, to other Objects, filepaths etc.). Notes currently use Blender's native Text Editor, which does not support links, potentially making this very complicated to implement. *Could be implemented by making an "interpreter" and an interface to go along with Notes*

Issues:
- The original idea was to include Notes in the Object Panel. This was not done, because showing editable multi line text in Panels is not really possible.

**Grouping**  
Objects can be grouped using a shortcut, generating a Group Object (Empty) that all grouped Objects are Parented to. A Group Object is useful because: it can be moved, controlling the whole Group's transformation; it can have its own Properties. Objects can be taken out of the Group or the Group can be completely disbanded.

Future:
- Think about how Group Editing works; should it be possible to select grouped Objects individually, or should the group serve as a barrier, getting its own "Edit Mode"? (The latter is, of course, how most software handles groups)
- Find a way to integrate Group properties into an Object's properties

**Recursive Parent Object handling, Object attachments**
*Objects come with attachments more or less automatically and forced. Right now, automatic attachments are Bounding Box Objects, Opening Ojbects and Notes (Texts). The underlying proposed and implemented logic is to have Objects consist of themselves and these attachments, meaning editing, copying and removing them affects the whole hierarchy instead of just the Object itself. Right now, this includes renaming, removing and duplicating objects. Object attachments work via the native Parent/Child system, Notes are attached via their name. This recursive nature is not limited to automatically attached Objects, but also affects all other Child objects*

Notes:
- *These Relationships should at some point be externalised instead of being stored in the .blend file*

**Construction Lines**  
When Editing a Mesh, existing Edges can be (by pressing a key) copied and elongated to serve as a snapping guide for transformation operations. Additionally, intersecting Construction Lines generate Intersection Points (Emptys) to snap to. Getting an Intersection Point is achieved in two key presses. Construction Lines and Intersection Points are saved into a history on generation. After a limited number of uses (currently 3) the oldest Line and its Points are cleared. After a Line is generated, transformation operations use the line as orientation.

Notes:
- This concept could and should be expanded to Faces and Vertices as well, generating Face/Edge intersections, or a closest point on an Edge to a Vertex, to mention two examples.
- Make the limit configurable.
- Evaluate auto orientation.

Issues:
- Construction Lines currently do not account for Object Rotation (this goes back to Object Logic; should they need to?).

**Cameras**
Cameras contain a dimensions property, which is automatically used when the camera is active. This enables using cameras with specific image sizes. This is nothing new, but was "low hanging fruit" and therefore quickly integrated into the Addon. *Other Properties, like dpi and scale for orthographic cameras (effectively "drawings")*

**Point Clouds**  
Point Clouds can be processed after import. In addition to coloring the points, the Point Cloud is filtered as follows: since loading the complete Point Cloud can lead to performance issues, points are removed by distance, reducing the number of points in exchange for less accuracy. The full resolution Point Cloud is only loaded inside of a "Magnifier" sphere that can be moved and resized by the user. This way full accuracy is present where it is needed while increasing performance. Point Clouds are non-selectable and can be moved with a Parent Object, similar to groups.

Notes:
- This currently depends on objects in the startup file. It should eventually work independantly.
- Currently only works for Point Clouds that have color information stored in vertex attributes (is there even a different way of storing color info?)
- Currently only a single Point Cloud per Project is supported
- Usage/configuration requires basic knowledge of Geometry Nodes, there could be a simpler interface for it.
- It should eventually be possible to use multiple Magnifiers.
- It should eventually be possible to use Magnifiers that are not Spheres. At least other primitives.

**Workspace/Startup File**  
The Workspace was made to be similar to the default Blender Startup File in order to offer some familiarity for Blender users. In the workspace the Timeline Area at the bottom is removed and a Text Editor Area is added for Notes. The default display mode is Material Preview; Wireframes are displayed with Object Color; Edge Length display is enabled. Also included in the Startup File, as mentioned, are the Objects necessary for Point Cloud Processing (Magnifier, Parent Empty, empty Geometry Node Objects, Materials). Finally, there is a Section Plane Object and a corresponding default Material for shader 
driven sectioning.

Notes:
- Since the Section Plane works via shader, it only works if an Object's Material is prepared correctly. For this, there is a Node Group in the Startup File that should be inserted just in front of the Shader Output Node. Optimally, this Node Group is integrated into new Materials by default. *Right now, it is not.*

**Photos (new)**
Reference photos can be added into the scene. They are added as a Camera containing the chosen reference photo as a Background Image. The Camera is configured to match the focal length of the photo (that is written into the photos metadata). The proposed usage is to add the photo and manually position it into the scene. Opening a new Image Editor Window then enables browsing through photos by clicking on the Camera/Photo Object.

Notes:
- The positioning step would of course be nice to have automated. Maybe through feature matching like in photogrammetry software or through camera sensor metadata in the photo file.
- This could be used to map which surfaces/Objects have been photographed and which might be missing. Related, it could be used to detect which Objects are shown in which photo, enabling yet another way of browsing through the photos.

**Decompositions (new)**
When using Parent/Child hierarchies to document decompositions, these hierarchies can be navigated through level by level. For example: Parent Object is selected -> go down a level -> Parent is hidden and Children are displayed -> go up a level -> children are hidden and parent is displayed. The object panel always shows which objects the selected object consists of. This hierarchy system can be used in an arbitrary way. This is strongly related to the M3 design project.

**Linked Hierarchies/Replace (new)**
Hierarchies can be linked in a way similar to linking Objects in native Blender. A linked Hierarchy contains Objects whose Mesh Data is linked with their twins from the original Hierarchy, along with their relative position to their Parent Object. The Replace Operator can be used to replace a selected Object with a specified Object/Hierarchy (its Children, their children and so on) at it the position of the replaced Object. The Object to Replace with is specified in the N-Panel ("Replace" tab). Alternatively, linked Hierarchies can be duplicated similar to duplicating linked Objects. Objects and Hierarchies can be unlinked via another Operator.

**Openings (new)**
Openings can be added to selected Objects. Opening Objects are assigned the Element Type 'Opening' and parented to the selected Object. On operation, a Cube is added aligned to the selected object, along with an automatically configured Boolean Modifier. This is similar to how non-destructive, Boolean-based Add-Ons work (for example ND). Openings are shown only when their Opening Object is present in the active Scene.

Notes:
- Removing Openings still leads to some problems that need to be fixed.
- Openings are not yet considered in quantity calculation.
- There should be a way to set the opening size (and maybe position) in the interface.

**Demolish (new)**
Whole Objects can be marked as "demolished" which results in them being displayed as a yellow Wireframe. The demolish status is stored in the Scene, meaning an Object can be marked as demolished in one scene but remain in its original status in another.

**Scene Logic (new)**
This is not really a feature but more of a technical proposition that is partly implemented through the points above. A way to show different states of the structure that is being worked on in the Project is to have them stored in different scenes. This could (already) work as follows: a "main" scene contains the structure in its current, as is state. Another scene contains the structure with the modifications (Openings and demolished or added Objects) contained in a new design proposal/variant. Past states could also be documented in other scenes. The choice "main" scene is the user's; it could be the original state from the far past or the current state.

Notes:
- Right now, the "main" scene is required to be named "Bestand". This was a quick and dirty solution and should obviously be changed.
- It may be useful to have this stored in another way than Scenes and accordingly enable having different states present in the same scene (for example for design variants that concern only part of a structure).

**Scale tool (new)**
A basic scale tool to scale and align Objects in a source to target way was implemented, however its usage/way of working is complicated and will likely be changed soon. To have this documentation be comprehensive, it is still mentioned in this way. It was used in the M3 project.


### Future Work/Other Ideas

**Translate Operation**  
When translating ("Grab") Objects, inputting a distance should not automatically lock the translation to an axis. Instead, the total distance of the translation should be limited. This was tried by running a Modal Operator on top of the Translate Operator, but resulted in glitchy handling because the two Operators were working against eachother. Optimally, this is changed in the Translate Operator itself. This was not done, since it would require either changing Blender's source code or completely rebuilding the Operator in Python.

**Modifiers**  
Especially useful for modeling architecture are Blender's Modifiers (like Boolean, Array etc.), which exist in other forms in most existing architectural software. Optimally, using Modifiers should be made to feel like using operators, meaning quicker and less complicated than the current process of adding a Modifier, setting parameters etc.. ~~This was not done in this project, because many Blender Addons have already approached this problem. In the future, it would be great to integrate some of those solutions in "Goliath".~~
*This was done for Booleans, see Additions - Openings.*

**Property Changes**  
(In my opinion) Changing properties should automatically apply to all selected Objects (this would not only be helpful when working with this Addon, but also in general). In Blender, this can be done by holding down the Alt key while changing a property, which is, as I understand, quite an obscure function. The question, whether this should be the default behavior is apparently old: there is a 8 year old Blender Dev issue about it https://projects.blender.org/blender/blender/issues/54862. ~~Because of this, changing this was not approached in this project.~~ *Partly implemented by prop update functions*

**Drawing Output**  
The very elementary topic of drawing output was explicity not a part of this project, mainly because 1. another group of students initially worked on this and 2. the domain of this topic is large enough to fill an entire term by itself. However, of course it would not only be great but necessary to integrate this functionality into an Addon like "Goliath". *Partly, very superficially approached by adding previously mentioned Camera properties*

**Texture/UV Based Damage Marking**  
Another important topic when dealing with Bestand is mapping damage. Like the Drawing Output, this is nothing new, but it would be helpful for a way to deal with this to be implemented in this project. One idea for how this could be done is using UV Maps and interactive texturing (like Texture Paint in Blender or similar functions in other CG software). In contrast to Object or Vertex based methods, this would allow for an appropriate mapping level of detail. Groups or types of damage could be distinguished using separate texture maps or color coding. Since UV Maps are supported in the Ifc format, this information could even be exported.

**Ifc Export**  
The way "Goliath" is intended to work is partly inspired by the Ifc standard and Bonsai specifically. Unlike Bonsai, the idea is not to use the .ifc file as a Project file. However, Projects are still intended to be exchanged as .ifc files (or at least the possibility of doing this is). For this, "Goliath" needs an .ifc exporter/translator. Bonsai could serve as this itself, or it could be the main reference for making one.

**Documenting Time/Building History**  
This is yet another old but important topic working with Bestand, especially for historic or "heritage" architecture. Documentation and clear, readable display of building history should be approached for "Goliath". *The current Scene system mentioned previously could be (and was) used for this.*

**References**  
Objects in a building model should be able to refer to other data with a type/category/reason of reference. Closely related to this is the previously explained ability to have (hyper)links in Notes. This other data should not only encompass other objects in the project file but also external objects, like photos, old drawings, old texts etc..

**Linking Data**  
In the Extension and in the propsed ideas, as well as in construction projects in general, we are dealing with many different types of data. Currently, in this prototype stage, the connecting "fulcrum" for all of this data is the Blender/"Goliath" Project file. This should be questioned, because it is inevitable that there are going to be multiple project files and file types from different sources, be it software or other, throughout a projects working process. Alternatively, there could be a meta-level structure (database, manifest, graph) coordinating project data and managing the links in between.