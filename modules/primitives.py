import bpy
from mathutils import Vector, Matrix, Quaternion

def _calculate_plane_size(obj, normal):
    """Calculate appropriate plane size based on object dimensions and cutting normal"""
    dimensions = obj.dimensions
    
    # Calculate the diagonal of the bounding box
    diagonal = (dimensions.x**2 + dimensions.y**2 + dimensions.z**2)**0.5
    
    # For safety, make the plane twice the diagonal length
    # This ensures the plane extends well beyond the object in all directions
    return diagonal * 2.0

def _create_cutting_plane(context, location, normal, size=None, name="Cutting_Plane", target_obj=None):
    """Create a plane object at the specified location with the given normal"""
    # Calculate appropriate size if not specified and target object is provided
    if size is None and target_obj is not None:
        size = _calculate_plane_size(target_obj, normal)
    elif size is None:
        # Default size if no target object provided
        size = 100.0
        
    # Create a plane mesh
    bpy.ops.mesh.primitive_plane_add(size=size, location=location)
    plane = context.active_object
    plane.name = name
    
    # Align plane to the normal direction
    # Normalize the normal vector (just to be safe)
    normal = normal.normalized()
    
    # Default plane normal is Z-up (0, 0, 1)
    z_axis = Vector((0, 0, 1))
    
    # Special case: if the normal is pointing exactly down (-Z)
    if (normal - Vector((0, 0, -1))).length < 0.001:
        # Simply rotate 180 degrees around X axis
        plane.rotation_euler = (3.14159, 0, 0)
    elif normal != z_axis:  # Only rotate if not already aligned to Z
        # Calculate the rotation that aligns z_axis with normal
        # Using quaternion rotation which handles any direction correctly
        rotation = z_axis.rotation_difference(normal)
        plane.rotation_euler = rotation.to_euler()
    
    return plane
