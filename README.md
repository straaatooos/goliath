Hello OS Arch community, developer, interested individual

Here are some raw, more technical notes about the "Goliath" project.  

**For a project overview, see: https://community.osarch.org/discussion/3328/sketch-prototype-of-a-lightweight-h-bestands-bim-software-in-blender**

**User-oriented video introduction: https://youtu.be/9bOEjacAUMQ**

I also want to preface this by saying: I am an architecture student, not a developer by trade. I started this term with a bit of experience in programming mainly from small free time projects, but having close to no experience with Python or the Blender API. The code probably has a lot of room for improvement. Also, this is by no means intended to be a finished "product", but more of a demonstrator or prototype.

I will try to keep this up to date.

Thanks for your interest,

Julian "straaatooos" Hüther



### Changes to native Blender operations

**Object/Mesh logic**  
To avoid confusion, the general idea is to not have two different parameters that work on the same thing (geometry or other).
Object Scale and Rotation are automatically applied in Edit Mode and Object Origins are automatically moved to center of geometry when the Mesh is edited. This is to ensure that all edit mode lengths are real lengths, that there is only one method of rotating geometry and to avoid confusion with offset object origins.

Alternatives:
- All object parameters are always 0/0/0 etc. and all geometry changes are always applied only in Edit Mode, that is on the Mesh level instead of the Object level. This might be nice for Meshes and Curves, but would obviously not work with other Object Types.

Future:
- Rotation could be made to set automatically according to geometry in a similar way Location does. Scale might be problematic, since changes to it always clash with the dimensions of the actual mesh.

Issues:
- Groups/Parenting

**Object/Mesh Separation**  
When done editing Meshes (on leaving Edit Mode), any unconnected geometry is separated into its own Object. This is done to force users into having a dedicated Object and thereby Properties for any separate piece of geometry.

Future:
- The new, separated Objects are supposed to be grouped automatically on separation, however this is not yet implemented.

Issues:
- The necessity of this concept should be questioned. There are probably other ways of achieving a similar effect, automatic Vertex Groups maybe?

**Recursive Parent Object handling**  
When working on Objects with Child Objects attached to it, using Duplicate duplicates the whole Parent/Child structure; using Remove removes the whole Parent/Child Structure

**Edit Mode translation**  
When editing a Mesh in Face mode, using Grab automatically uses the normal axis of the face.

Future:
- Think about whether default settings like this may be useful for Edge or Vertex mode as well


### Additions

**Object Properties**  
Generally, the geometric building model is assumed to consist of Mesh and Curve Objects. All of the following functions were worked on with Meshes in mind. It is not impossible for them to work for other Types of Objects, but unlikely.

**Element Types**  
Every Object has an Element Type. The integrated types were chosen based on IfcElement types, but several of the Ifc types were omitted to not overwhelm and slow down users, focusing on typically relevant types for smaller scale architecture.(Yes, this is almost exactly the IfcBuidlingElements selection, with a few exceptions.)

Future:
- Evaluate the choice of types

**Primitive Type Detection**  
An Object's type is automatically determined based on its geometry, after editing said geometry. This automatic determination can be overridden.

Future:
- The rules/heuristics of determining an object type can and probably should become more robust, while not increasing complexity to an unreasonable level. It does not need to be perfect, the override function exists for a reason, failure is expected.
- Said rules could become customizable

Issues:
- The rules still need to be implemented into the autoCat.py.

**Storeys**  
Objects of Type Slab can be made to mark Storeys. Storey height is then set to the topmost (Global Z) Face of the Mesh. Every Object is put in one of the Storeys present in the Project based on the height. The goal is to avoid having extra Storey Objects unless absolutely necessary.

Future:
- Storeys still need properties like Name, Offset etc.
- Non-Slab Storeys are not yet possible (that is similarly set Storeys for Objects that are not Slabs *and* completely Object independant Storeys)
- Objects can only be in one Storey; should it be possible for them to be in multiple, in none? 

**Custom "Goliath" Properties**    
Similarly to native Blender, (Mesh) Objects and Materials can have custom properties, with respective property types. Additionally, each property has a certainty value attached to it, informing about the source and reliability of the property. These Properties represent what would be in Psets in traditional BIM software, which is why "Goliath" automatically suggests the Pset*Type*Common property names when adding a property.
The goal was to remove the "hurdle" of creating and managing Psets, again simplifying and accelarating the working process.

Future:
- Having Psets can of course be useful and they should be integrated eventually. But handling them should remain as simple and quick as it is now. (Could this be handled with naming conventions?)
- Properties could have an Element Type setting that determines which Objects can/should have the property and which should not.
- When using a Pset*Type*Common property, the property type needs to be set accordingly.

Issues:
- Previously added custom properties are not included in the name search pool

**Oriented Bounding Boxes**  
Every Mesh Object is automatically put in an Object Oriented Bounding Box. This Bounding Box is used to determine type and dimensions/proportions. (The current algorithm for this is simple: it groups faces according to orientation, the largest area sum is used to draw the base of the box and it is extruded until it encloses the furthest vertex. See code for more.) This approach of course does not work with all geometries. When the difference between the Bounding Box and the Mesh is too great, calculating the quantities will generate a warning (see Object Panel).

Future:
- The Bounding Box algorithm can be improved and made more robust. Unlike with Auto Types, there is no override for this, so it is desirable to have a near perfectly robust algorithm. The only limiting factor is software performance.

**Quantities and Dimensions**  
Using the Mesh and aforementioned Bounding Box geometry, four quantities can be calculated: Length; Area (of all Mesh faces); Volume; Object Count. As mentioned, dimensions are also determined from the Bounding Box.

Future:
- Different configurations for quantities could be added, similar to Quantity Takeoff. (This is probably especially interesting when calculating areas - for this it would be nice to see which Faces are counted and which are not.) This should however never replace current Area calculation, since it is already very useful when it just counts all the face areas.

Issues:
- Volume calculation only works if the Mesh is "perfect" (closed and all normals pointing in the right direction). Right now the solution is just a warning, but could the calculation algorithm be more robust?

**Object Panel**  
This Panel is - like other aspects of this project - inspired by existing architectural/CAD software.
It delivers all aforementioned information and properties to the user the moment an Object is selected. Quantities are updated live and summed up across the selection. Properties can be named, added and removed with one click respectively. The whole Panel is intended to be visible without scrolling. The aim is for users to be able to understand everything "at first glance". Descriptions are displayed when hovering, just as with Blender's native properties. The Panel changes with the type of Object selected (e.g. Group Objects, see Grouping).

Future:
- For the object count, show how many of each type.

Issues:
- Type override has no description yet.

**Object Notes**  
On Object selection, a note Text is generated for the Object, if there is not yet one. It is automatically displayed in the bottom right corner of the window in the "Goliath" workspace. In it, users can write plain text about anything concerning the object.

Future:
- Currently Notes are linked to their Objects only by name. This seems like a bad way to do it, eventhough renaming works
- Maybe it could be useful to have Notes that are not linked to Objects?
- It would be great if Notes could contain links (like a hyperlink, to other Objects, filepaths etc.). Notes currently use Blender's native Text Editor, which does not support links, potentially making this very complicated to implement.

Issues:
- The original idea was to include Notes in the Object Panel. This was not done, because showing editable multi line text in Panels is not really possible.

**Grouping**  
Objects can be grouped using a shortcut, generating a Group Object (Empty) that all grouped Objects are Parented to. A Group Object is useful because: it can be moved, controlling the whole Group's transformation; it can have its own Properties. Objects can be taken out of the Group or the Group can be completely disbanded.

Future:
- Think about how Group Editing works; should it be possible to select grouped Objects individually, or should the group serve as a barrier, getting its own "Edit Mode"? (The latter is, of course, how most software handles groups)
- Find a way to integrate Group properties into an Object's properties

**Construction Lines**  
When Editing a Mesh, existing Edges can be (by pressing a key) copied and elongated to serve as a snapping guide for transformation operations. Additionally, intersecting Construction Lines generate Intersection Points (Emptys) to snap to. Getting an Intersection Point is achieved in two key presses. Construction Lines and Intersection Points are saved into a history on generation. After a limited number of uses (currently 3) the oldest Line and its Points are cleared. After a Line is generated, transformation operations use the line as orientation.

Future:
- This concept could and should be expanded to Faces and Vertices as well, generating Face/Edge intersections, or a closest point on an Edge to a Vertex, to mention two examples.
- Make the limit configurable.
- Evaluate auto orientation.

Issues:
- Construction Lines currently do not account for Object Rotation (this goes back to Object Logic; should they need to?).

**Point Clouds**  
Point Clouds can be processed after import. In addition to coloring the points, the Point Cloud is filtered as follows: since loading the complete Point Cloud can lead to performance issues, points are removed by distance, reducing the number of points in exchange for less accuracy. The full resolution Point Cloud is only loaded inside of a "Magnifier" sphere that can be moved and resized by the user. This way full accuracy is present where it is needed while increasing performance. Point Clouds are non-selectable and can be moved with a Parent Object, similar to groups.

Future:
- It should eventually be possible to use multiple Magnifiers.
- It should eventually be possible to use Magnifiers that are not Spheres. At least other primitives.

Issues:
- This currently depends on objects in the startup file. It should eventually work independantly.
- Currently only works for Point Clouds that have color information stored in vertex attributes (is there even a different way of storing color info?)
- Currently only a single Point Cloud per Project is supported
- Usage/configuration requires basic knowledge of Geometry Nodes, there could be a simpler interface for it.

**Scan**  
All Information that is currently in the Object Panel is and should remain visible on selection, without needing to open another window or pressing anything. All Objects present in the Project should be processed ("scanned") to contain the necessary information for this when Projects are loaded or Objects added respectively.

**Cameras**  
Cameras contain a dimensions property, which is automatically used when the camera is active. This enables using cameras with specific image sizes. This is nothing new, but was "low hanging fruit" and therefore quickly integrated into the Addon.

Future:
- Add properties for scale and paper dimensions

**Workspace/Startup File**  
The Workspace was made to be similar to the default Blender Startup File in order to offer some familiarity for Blender users. In the workspace the Timeline Area at the bottom is removed and a Text Editor Area is added for Notes. The default display mode is Material Preview; Wireframes are displayed with Object Color; Edge Length display is enabled. Also included in the Startup File, as mentioned, are the Objects necessary for Point Cloud Processing (Magnifier, Parent Empty, empty Geometry Node Objects, Materials). Finally, there is a Section Plane Object and a corresponding default Material for shader 
driven sectioning.

Issues:
- Since the Section Plane works via shader, it only works if an Object's Material is prepared correctly. For this, there is a Node Group in the Startup File that should be inserted just in front of the Shader Output Node. Optimally, this Node Group is integrated into new Materials by default.


### Future Work/Other Ideas

**Translate Operation**  
When translating ("Grab") Objects, inputting a distance should not automatically lock the translation to an axis. Instead, the total distance of the translation should be limited. This was tried by running a Modal Operator on top of the Translate Operator, but resulted in glitchy handling because the two Operators were working against eachother. Optimally, this is changed in the Translate Operator itself. This was not done, since it would require either changing Blender's source code or completely rebuilding the Operator in Python.

**Modifiers**  
Especially useful for modeling architecture are Blender's Modifiers (like Boolean, Array etc.), which exist in other forms in most existing architectural software. Optimally, using Modifiers should be made to feel like using operators, meaning quicker and less complicated than the current process of adding a Modifier, setting parameters etc.. This was not done in this project, because many Blender Addons have already approached this problem. In the future, it would be great to integrate some of those solutions in "Goliath".

**Property Changes**  
(In my opinion) Changing properties should automatically apply to all selected Objects (this would not only be helpful when working with this Addon, but also in general). In Blender, this can be done by holding down the Alt key while changing a property, which is, as I understand, quite an obscure function. The question, whether this should be the default behavior is apparently old: there is a 8 year old Blender Dev issue about it https://projects.blender.org/blender/blender/issues/54862. Because of this, changing this was not approached in this project.

**Drawing Output**  
The very elementary topic of drawing output was explicity not a part of this project, mainly because 1. another group of students initially worked on this and 2. the domain of this topic is large enough to fill an entire term by itself. However, of course it would not only be great but necessary to integrate this functionality into an Addon like "Goliath".

**Texture/UV Based Damage Marking**  
Another important topic when dealing with Bestand is mapping damage. Like the Drawing Output, this is nothing new, but it would be helpful for a way to deal with this to be implemented in this project. One idea for how this could be done is using UV Maps and interactive texturing (like Texture Paint in Blender or similar functions in other CG software). In contrast to Object or Vertex based methods, this would allow for an appropriate mapping level of detail. Groups or types of damage could be distinguished using separate texture maps or color coding. Since UV Maps are supported in the Ifc format, this information could even be exported.

**Ifc Export**  
The way "Goliath" is intended to work is partly inspired by the Ifc standard and Bonsai specifically. Unlike Bonsai, the idea is not to use the .ifc file as a Project file. However, Projects are still intended to be exchanged as .ifc files (or at least the possibility of doing this is). For this, "Goliath" needs an .ifc exporter/translator. Bonsai could serve as this itself, or it could be the main reference for making one.

**Documenting Time/Building History**  
This is yet another old but important topic working with Bestand, especially for historic or "heritage" architecture. Documentation and clear, readable display of building history should be approached for "Goliath".

**References**  
Objects in a building model should be able to refer to other data with a type/category/reason of reference. Closely related to this is the previously explained ability to have (hyper)links in Notes. This other data should not only encompass other objects in the project file but also external objects, like photos, old drawings, old texts etc..

**Linking Data**  
In the Extension and in the propsed ideas, as well as in construction projects in general, we are dealing with many different types of data. Currently, in this prototype stage, the connecting "fulcrum" for all of this data is the Blender/"Goliath" Project file. This should be questioned, because it is inevitable that there are going to be multiple project files and file types from different sources, be it software or other, throughout a projects working process. Alternatively, there could be a meta-level structure (database, manifest, graph) coordinating project data and managing the links in between.