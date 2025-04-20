import bpy
import bmesh
import math
from mathutils import Vector

def _find_best_slice(mesh, max_z, depth=30.0, samples=30):
    """
    Helper function to find the best slice based on cross-sectional perimeter.
    """
    min_z = max_z - depth
    best_z = min_z
    best_length = 0.0
    for i in range(samples + 1):
        z = min_z + (max_z - min_z) * i / samples
        length = 0.0
        for edge in mesh.edges:
            v1 = mesh.vertices[edge.vertices[0]].co
            v2 = mesh.vertices[edge.vertices[1]].co
            if (v1.z - z) * (v2.z - z) < 0:
                length += 1.0
        if length > best_length:
            best_length = length
            best_z = z
    return best_z, best_length
