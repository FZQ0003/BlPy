#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: F_Qilin


import bpy


def old_01(name='OLD Type', pixel=True, use_active=True):
    """
    Set up the scene (old type).

    :param name: Scene name.
    :param pixel: If True, use MI unit system (1m = 16u).
    :param use_active:
        If True, use active collection;
        If False, add a new collection.
    :return: None.
    """
    # Add a parent & change unit system
    op_obj = bpy.ops.object
    op_obj.empty_add(
        type='PLAIN_AXES',
        radius=16,
        align='WORLD',
        location=(0, 0, 0),
        rotation=(0, 0, 0)
    )
    obj = bpy.context.object
    obj.name = name
    if pixel:
        obj.scale = (0.0625, 0.0625, 0.0625)
        bpy.context.scene.unit_settings.system = 'NONE'

    if not use_active:
        op_obj.move_to_collection(
            collection_index=0,
            is_new=True,
            new_collection_name=name
        )
