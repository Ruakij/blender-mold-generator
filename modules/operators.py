import bpy
from .core import generate_mold, _find_best_slice
from .utils import report_error


class MoldFindSliceOperator(bpy.types.Operator):
    bl_idname = "mold.find"
    bl_label = "Find Slice"
    bl_description = "Compute the cut Z and perimeter for the active mesh"

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            report_error("Active object must be a mesh")
            return {'CANCELLED'}
        props = context.scene.mold_generator_props
        mesh = obj.data
        verts_z = [v.co.z for v in mesh.vertices]
        max_z = max(verts_z)
        z, length = _find_best_slice(mesh, max_z, depth=props.search_depth)
        props.found_z = z
        props.found_length = length
        self.report({'INFO'}, f"Slice at Z={z:.3f}, perimeter≈{length:.1f}")
        return {'FINISHED'}


class MoldGenerateOperator(bpy.types.Operator):
    bl_idname = "mold.generate"
    bl_label = "Generate Mold"
    bl_description = "Generate a mold shell from the active mesh"

    def execute(self, context):
        # No duplication here - moved to generate_mold function
        generate_mold(context)
        return {'FINISHED'}
