"""Utility functions for Mold Generator addon."""

import bpy


def validate_mesh(obj):
    """Ensure the object is a valid mesh for mold generation."""
    return obj and obj.type == 'MESH'


def report_error(message):
    """Utility to report errors in the UI."""
    print(f"Mold Generator Error: {message}")

def _boolean_operation(context, target, cutter, operation='DIFFERENCE', solver='EXACT', self_intersection=True):
    """Apply a boolean operation to the target object using the cutter object"""
    # Select the target object
    bpy.ops.object.select_all(action='DESELECT')
    target.select_set(True)
    context.view_layer.objects.active = target
    
    # Add a boolean modifier
    bool_mod = target.modifiers.new(name="Boolean", type='BOOLEAN')
    bool_mod.operation = operation
    bool_mod.object = cutter
    bool_mod.solver = solver
    bool_mod.use_self = self_intersection
    
    # Always apply the modifier to ensure the mesh data is updated
    bpy.ops.object.modifier_apply(modifier=bool_mod.name)
    
    return target
