import bpy
from bpy.props import FloatProperty, PointerProperty


class MoldGeneratorProperties(bpy.types.PropertyGroup):
    # Search settings
    search_depth: FloatProperty(
        name="Search Depth",
        description="Distance down from the top to search for the thickest section",
        default=30.0,
        min=0.0,
        unit='LENGTH',
    )
    # Output of last generation
    found_z: FloatProperty(
        name="Cut Z",
        description="Z location of the thickest cross-section",
        default=0.0,
        unit='LENGTH',
    )
    found_length: FloatProperty(
        name="Perimeter",
        description="Approximate perimeter of the cross-section",
        default=0.0,
        unit='LENGTH',
    )
    # Options for workflow
    operate_on_copy: bpy.props.BoolProperty(
        name="Work on Copy",
        description="Duplicate object and work on the copy",
        default=False,
    )
    use_manual: bpy.props.BoolProperty(
        name="Use Manual Slice",
        description="Use manually entered Cut Z and Perimeter instead of recalculating",
        default=False,
    )
    manual_z: FloatProperty(
        name="Manual Cut Z",
        description="Manually specify the Z location for the cut",
        default=0.0,
        unit='LENGTH',
    )
    manual_length: FloatProperty(
        name="Manual Perimeter",
        description="Manually specify the perimeter value",
        default=0.0,
        unit='LENGTH',
    )
    # Cutting options
    cut_half: bpy.props.BoolProperty(
        name="Cut in Half",
        description="Cut the shell in half after extrusion",
        default=False,
    )
    cut_axis: bpy.props.EnumProperty(
        name="Cut Axis",
        description="Axis plane for cutting",
        items=[('YZ', 'YZ Plane', ''), ('XZ', 'XZ Plane', ''), ('XY', 'XY Plane', '')],
        default='YZ',
    )


class MoldGeneratorAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__.split('.')[0]

    def update_default_search_depth(self, context):
        for scene in bpy.data.scenes:
            if hasattr(scene, 'mold_generator_props'):
                scene.mold_generator_props.search_depth = self.default_search_depth

    default_search_depth: FloatProperty(
        name="Default Search Depth",
        default=30.0,
        unit='LENGTH',
        update=update_default_search_depth,
    )
    keep_intermediates: bpy.props.BoolProperty(
        name="Keep Intermediates",
        description="Do not apply or delete intermediate objects (planes, modifiers, duplicates) for debugging",
        default=False,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "default_search_depth")
        layout.prop(self, "keep_intermediates")
