"""Utility functions for Mold Generator addon."""

import bpy


def validate_mesh(obj):
    """Ensure the object is a valid mesh for mold generation."""
    return obj and obj.type == 'MESH'


def report_error(message):
    """Utility to report errors in the UI."""
    print(f"Mold Generator Error: {message}")
