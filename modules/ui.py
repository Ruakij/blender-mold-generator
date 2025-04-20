import bpy


class MoldGeneratorPanel(bpy.types.Panel):
    bl_label = "Mold Generator"
    bl_idname = "MOLD_PT_mold_generator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mold Generator'

    def draw(self, context):
        layout = self.layout
        props = context.scene.mold_generator_props
        # Workflow options
        box = layout.box()
        box.label(text="Workflow", icon='TOOL_SETTINGS')
        box.prop(props, 'operate_on_copy')
        box.prop(props, 'cut_half')
        if props.cut_half:
            box.prop(props, 'cut_axis')

        # Advanced analytics
        adv = layout.box()
        adv.label(text="Slice", icon='MESH_CIRCLE')
        adv.prop(props, 'use_manual')
        if props.use_manual:
            adv.prop(props, 'manual_z')
            adv.prop(props, 'manual_length')
        # Search and analytics
        if not props.use_manual:
            adv.prop(props, 'search_depth')
            adv.operator('mold.find', text='Find Slice')
            row = adv.row()
            row.enabled = False
            row.prop(props, 'found_z')
            row.prop(props, 'found_length')

        # Execute
        layout.operator('mold.generate', text='Generate Mold')


def draw_mold_gen_menu(self, context):
    """Add Generate Mold to the object context menu"""
    self.layout.separator()
    from .operators import MoldGenerateOperator
    self.layout.operator(MoldGenerateOperator.bl_idname, text="Generate Mold")
