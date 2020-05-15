#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: F_Qilin


import nbtlib


def load(filepath: str):
    """
    Load a Minecraft schematic file.

    :param filepath: Path of the schematic.
    :return: None.
    """
    file = nbtlib.load(filepath)
    for i in file['Schematic']['Blocks']:
        print(i, end=' ')


if __name__ == '__main__':
    load('res/sce01.nbt')
