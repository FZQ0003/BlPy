#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: F_Qilin


import bpy
import json


def add_collection(name: str):
    """
    Add a new collection in Blender.

    :param name: Collection name.
    :return: New collection.
    """
    collection: bpy.types.Collection \
        = bpy.data.collections.new(name)
    bpy.context.scene.collection \
        .children.link(collection)
    return collection


def set_scene(
        name='Mine-imator Scene',
        width=1280, height=720, fps=24,
        use_active=True
):
    """
    Set up the scene.

    :param name: Scene name.
    :param width: Resolution X.
    :param height: Resolution Y.
    :param fps: Frame rate (Tempo).
    :param use_active:
        If True, use active collection;
        If False, add a new collection.
    :return: New collection.
    """
    # Set render settings
    scene = bpy.context.scene
    render = scene.render
    render.resolution_x = width
    render.resolution_y = height
    render.resolution_percentage = 100
    render.fps = fps
    render.fps_base = 1


def set_background(settings: dict):
    """
    Change the background.

    :param settings: Data from MI projects.
    :return: None.
    """
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
        use_active=False
    )
    group = add_collection(project['name'])
    # Todo: Read global timeline settings. (region)
    # Todo: Minecraft resources.
    # Todo: Items in MI use YXZ(Blender) euler.


if __name__ == '__main__':
    load('res/proj_01.json')
