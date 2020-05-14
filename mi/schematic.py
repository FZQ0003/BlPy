#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: F_Qilin


import nbtlib


def load(filename):
    file = nbtlib.load(filename)
    for i in file['Schematic']['Blocks']:
        print(i, end=' ')


if __name__ == '__main__':
    load('res/sce01.nbt')
