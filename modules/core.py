import bpy
import bmesh
import math
from mathutils import Vector
from . import utils
from .geometry import _find_best_slice
from .primitives import _create_cutting_plane
from .utils import _boolean_operation


def generate_mold(context):
    """
    Generate a mold shell by cutting the top and extruding the cross-section up to original height.
    Uses boolean operations with planes for clean cuts and direct face extrusion.
    """
    obj = context.active_object
    if not obj or obj.type != 'MESH':
        print("Error: Active object must be a mesh")
        return

    props = context.scene.mold_generator_props

    # Fetch addon preferences
    addon_key = __package__.split('.')[0]
    prefs = bpy.context.preferences.addons[addon_key].preferences
    keep = prefs.keep_intermediates

    # Work on a copy if requested - do it here ONCE
    if props.operate_on_copy:
        print("Creating copy of original object")
        # Store original name
        original_name = obj.name
        # Duplicate mesh and data
        new_obj = obj.copy()
        new_obj.data = obj.data.copy()
        new_obj.name = f"{original_name}_mold"
        context.collection.objects.link(new_obj)
        # Select the copy and make it active
        bpy.ops.object.select_all(action='DESELECT')
        new_obj.select_set(True)
        context.view_layer.objects.active = new_obj
        obj = new_obj  # Work on the copy from now on

    # Calculate Z limits for the active mesh (either original or copy)
    mesh = obj.data
    verts = [v.co.z for v in mesh.vertices]
    min_z = min(verts)
    max_z = max(verts)
    tol = 1e-6

    # Determine slice location
    if props.use_manual:
        best_z = props.manual_z
        best_length = props.manual_length
    else:
        best_z, best_length = _find_best_slice(mesh, max_z, depth=props.search_depth)
        props.found_z = best_z
        props.found_length = best_length

    print(f"Thickest cross-section at Z = {best_z:.3f} (approx.) with metric {best_length}")

    # STEP 1: Cut off the top part using boolean operation with a plane
    cutting_plane = _create_cutting_plane(
        context, 
        location=(0, 0, best_z), 
        normal=Vector((0, 0, -1)), 
        name="Z_Cutting_Plane",
        target_obj=obj  # Pass the object for size calculation
    )
    
    # Apply boolean difference to keep only the part below the plane
    _boolean_operation(context, obj, cutting_plane, operation='DIFFERENCE', self_intersection=False)

    if not keep:
        bpy.data.objects.remove(cutting_plane, do_unlink=True)
    else:
        cutting_plane.hide_viewport = True
    
    # STEP 2: Extrude the faces at the cut plane directly up
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    
    # Find all faces near the cut plane Z height with increased tolerance
    # Boolean operations can be imprecise, so we need a more forgiving tolerance
    cut_tolerance = 0.05  # Increased tolerance to 0.05 Blender units
    
    cut_faces = []
    for f in bm.faces:
        # Check if face normal is pointing upward (approximately Z+)
        if f.normal.z > 0.7:  # Allow for some angle in the normal
            # Get the average Z of the face vertices
            face_verts_z = [v.co.z for v in f.verts]
            avg_z = sum(face_verts_z) / len(face_verts_z)
            # Check if this face is near the cut plane
            if abs(avg_z - best_z) < cut_tolerance:
                cut_faces.append(f)
    
    print(f"Found {len(cut_faces)} faces near the cut plane Z={best_z} (tolerance={cut_tolerance})")
    
    if not cut_faces:
        print("Error: Could not find faces at the cut plane. Trying alternative approach...")
        
        # Alternative approach: Find the top-most faces with upward normals
        top_faces = []
        max_face_z = -float('inf')
        
        for f in bm.faces:
            if f.normal.z > 0.7:  # More tolerant normal check
                face_verts_z = [v.co.z for v in f.verts]
                avg_z = sum(face_verts_z) / len(face_verts_z)
                
                # Track the highest face Z value
                if avg_z > max_face_z:
                    max_face_z = avg_z
                    top_faces = [f]
                elif abs(avg_z - max_face_z) < 0.01:
                    top_faces.append(f)
        
        if top_faces:
            print(f"Using alternative approach: Found {len(top_faces)} top faces at Z={max_face_z}")
            cut_faces = top_faces
        else:
            print("Error: Could not find any suitable faces for extrusion")
            bm.free()
            return
    
    # Extrude the faces directly up
    ret = bmesh.ops.extrude_face_region(bm, geom=cut_faces)
    extruded_verts = [v for v in ret["geom"] if isinstance(v, bmesh.types.BMVert)]
    
    # Move the extruded vertices up to the original top
    bmesh.ops.translate(bm,
                       verts=extruded_verts,
                       vec=(0, 0, max_z - best_z))
    
    print(f"Extruded {len(extruded_verts)} vertices from Z={best_z} up to Z={max_z}")
    
    # Update the mesh
    bm.to_mesh(obj.data)
    obj.data.update()
    bm.free()
    
    # STEP 3: Optional - Cut the mold in half (this function creates the necessary copies)
    if props.cut_half:
        print(f"Cutting mold in half along {props.cut_axis} plane...")
        _split_shell(context, obj, props, keep)
    
    # Ensure the result is the active object
    context.view_layer.objects.active = obj
    return obj


def _split_shell(context, obj, props, keep):
    """
    Split the mold into two halves using boolean operations with a plane.
    """
    # Calculate the center of the object
    mesh = obj.data
    verts_co = [v.co for v in mesh.vertices]
    center = sum(verts_co, Vector()) / len(verts_co)
    
    # Determine cutting plane normal based on selected axis
    if props.cut_axis == 'YZ':
        normal = Vector((1, 0, 0))
    elif props.cut_axis == 'XZ':
        normal = Vector((0, 1, 0))
    else:  # 'XY'
        normal = Vector((0, 0, 1))
    
    # Create the cutting plane
    cutting_plane = _create_cutting_plane(
        context, 
        location=center, 
        normal=normal, 
        name=f"{props.cut_axis}_Split_Plane",
        target_obj=obj
    )
    
    # Create a duplicate of the original object for the second half
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    context.view_layer.objects.active = obj
    bpy.ops.object.duplicate()
    second_half = context.active_object
    second_half.name = f"{obj.name}_B"
    obj.name = f"{obj.name}_A"
    
    # Cut the first half using boolean difference
    print("Creating first half...")
    _boolean_operation(context, obj, cutting_plane, operation='DIFFERENCE', self_intersection=True)
    
    # Create a new cutting plane with inverted normal for the second half
    inverted_cutting_plane = _create_cutting_plane(
        context, 
        location=center, 
        normal=-normal,  # Use negative normal vector
        name=f"{props.cut_axis}_Split_Plane_Inverted",
        target_obj=second_half
    )
    
    # Cut the second half using boolean difference with the inverted plane
    print("Creating second half...")
    _boolean_operation(context, second_half, inverted_cutting_plane, operation='DIFFERENCE', self_intersection=True)
    
    # Clean up both cutting planes
    if not keep:
        bpy.data.objects.remove(cutting_plane, do_unlink=True)
        bpy.data.objects.remove(inverted_cutting_plane, do_unlink=True)
    else:
        cutting_plane.hide_viewport = True
        inverted_cutting_plane.hide_viewport = True
    
    # Select both halves
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    second_half.select_set(True)
    context.view_layer.objects.active = obj
    
    return obj, second_half
