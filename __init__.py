"""Mold Generator addon - Generate mold shells with customizable thickness and filling tunnel"""

bl_info = {
    "name": "Mold Generator",
    "author": "Your Name",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Mold Generator",
    "description": "Generate a mold shell cut at its thickest section and add a filling tunnel",
    "warning": "",
    "doc_url": "https://github.com/yourusername/blender-mold-generator",
    "category": "Object",
    "support": "COMMUNITY",
}

import bpy
from bpy.props import PointerProperty

from .modules import properties, operators, ui, core, utils

# Classes to register
classes = (
    properties.MoldGeneratorAddonPreferences,
    properties.MoldGeneratorProperties,
    operators.MoldFindSliceOperator,
    operators.MoldGenerateOperator,
    ui.MoldGeneratorPanel,
)

# Keymaps storage
addon_keymaps = []


def register():
    # Register classes
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    # Register scene properties
    bpy.types.Scene.mold_generator_props = PointerProperty(type=properties.MoldGeneratorProperties)
    # Add panel to object context menu
    bpy.types.VIEW3D_MT_object.append(ui.draw_mold_gen_menu)
    # Setup keymap (Ctrl+Alt+M)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new(
            operators.MoldGenerateOperator.bl_idname,
            'M', 'PRESS', ctrl=True, alt=True
        )
        addon_keymaps.append((km, kmi))


def unregister():
    # Remove keymaps
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    # Remove menu entry
    bpy.types.VIEW3D_MT_object.remove(ui.draw_mold_gen_menu)
    # Remove scene properties
    del bpy.types.Scene.mold_generator_props
    # Unregister classes
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == '__main__':
    register()
