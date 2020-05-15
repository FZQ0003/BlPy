#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: F_Qilin


import bpy
import json


def set_scene(
        name='Mine-imator Scene',
        width=1280, height=720, fps=24,
        pixel=True, use_active=True
):
    """
    Set up the scene.

    :param name: Scene name.
    :param width: Resolution X.
    :param height: Resolution Y.
    :param fps: Frame rate (Tempo).
    :param pixel: If True, use MI unit system (1m = 16u).
    :param use_active:
        If True, use active collection;
        If False, add a new collection.
    :return: None.
    """
    # Set render settings
    render = bpy.context.scene.render
    render.resolution_x = width
    render.resolution_y = height
    render.resolution_percentage = 100
    render.fps = fps
    render.fps_base = 1

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

    # Todo: Add a new collection.
    if not use_active:
        op_obj.move_to_collection(
            collection_index=0,
            is_new=True,
            new_collection_name=name
        )


def set_camera(settings: dict):
    """
    Set up the camera or add a new one.

    :param settings: Data from MI projects.
    :return: None.
    """
    # Todo: Work & active camera.
    pass


def load(filepath: str):
    """
    Load a Mine-imator project.
    
    :param filepath: Path of the project.
    :return: None.
    """
    with open(filepath, 'r') as f:
        data = json.loads(f.read())
    project = data['project']
    set_scene(
        name=project['name'],
        width=project['video_width'],
        height=project['video_height'],
        fps=project['tempo'],
        pixel=True, use_active=False
    )
    # Todo: Read global timeline settings.
    # Todo: Minecraft resources.
    # Todo: Items in MI use YXZ(Blender) euler.


if __name__ == '__main__':
    load('res/proj_01.json')
