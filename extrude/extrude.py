# -*- coding: UTF-8 -*-
# Code by F_Qilin.

# import os
import bpy
import bmesh
import math
import mathutils
import locale


def sgn(x, value=1.0):
    if type(x) is mathutils.Vector:
        tmp = mathutils.Vector((0.0, 0.0, 0.0))
        for _ in range(3):
            tmp[_] = sgn(x[_], value)
        return tmp
    else:
        if x > 0:
            return value
        elif x < 0:
            return -value
        else:
            return 0.0
        

def add_face(bm, faces, example):
    uv_layer = bm.loops.layers.uv.verify()
    face_new = bm.faces.new(faces, example)
    uvs = []
    for v in example.loops:
        uvs.append(v[uv_layer].uv)
    x = 0
    for v in face_new.loops:
        v[uv_layer].uv = uvs[x]
        x += 1
    return face_new


def judge_vec(vec, type=0):
    tmp = [abs(_) for _ in vec]
    tmp.sort()
    for i in range(len(tmp)):
        if math.isclose(tmp[i-1], tmp[i]):
            if type == 0:
                return False
            else:
                return None
    if type == 1:
        x = mathutils.Vector((0, 0, 0))
        y = [_ for _ in vec]
        for i in y:
            if math.isclose(tmp[-1], abs(i)):
                break
        x[y.index(i)] = sgn(i)
        return x
    else:
        return True


def judge_rec(verts):
    if len(verts) != 4:
        return False
    a = verts[0].co - verts[1].co
    b = verts[2].co - verts[3].co
    return math.isclose(a.cross(b).length, 0) and math.isclose(a.length, b.length)


def extrude_cus(value=1/64, del_face=True, del_others=False):
    me = bpy.context.object.data
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(me)
    
    v_lis = []
    v_special = {}
    for i in bm.verts:
        if i.select:
            v_lis.append(i)
        elif del_others:
            bm.verts.remove(i)
    v_lis_new = []
    for v in v_lis:
        tmp_vec = mathutils.Vector((0, 0, 0))
        for i in v.link_faces:
            if i.select:
                tmp_vec += i.normal
        v_lis_new.append(bm.verts.new(
            tuple(v.co + sgn(tmp_vec, value)), v
        ))
        x = judge_vec(tmp_vec, 1)
        if x is not None:
            v_special[v_lis_new[-1]] = bm.verts.new(
                tuple(v.co + x * value), v
            )
    tmp_lis = []
    f_lis_new = []
    f_lis_del = []
    for face in bm.faces:
        if face.select:
            for i in face.verts:
                tmp_lis.append(v_lis_new[v_lis.index(i)])
            if not judge_rec(tmp_lis):
                for x in range(len(tmp_lis)):
                    i = tmp_lis[x]
                    tmp_lis[x] = v_special.get(i, i)
            f_lis_new.append(add_face(bm, tmp_lis, face))
            for x in range(-1, len(tmp_lis)-1):
                tmp = (face.verts[x], face.verts[x+1], tmp_lis[x+1], tmp_lis[x])
                tmp_f = bm.faces.get(tmp)
                if tmp_f is None:
                    # f_lis_new.append(bm.faces.new(tmp))
                    add_face(bm, tmp, face)
                else:
                    f_lis_del.append(tmp_f)
            tmp_lis.clear()
            if del_face:
                f_lis_del.append(face)
    
    for i in f_lis_del:
        # f_lis_new.remove(i)
        bm.faces.remove(i)
    if del_others:
        for i in bm.edges:
            if len(i.link_faces) == 0:
                bm.edges.remove(i)
        for i in bm.verts:
            if len(i.link_edges) == 0:
                bm.verts.remove(i)
    
    bmesh.update_edit_mesh(me)
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent()
    bpy.ops.mesh.select_all(action='DESELECT')
    for i in f_lis_new:
        i.select_set(True)


class ExtrudeCustom(bpy.types.Operator):
    """Extrude selected faces"""
    
    GLOBAL_LANG = ['en_US', 'zh_CN']
    
    if (
        bpy.context.preferences.view.use_international_fonts
        and locale.getdefaultlocale()[0] in GLOBAL_LANG
    ):
        lang_i = GLOBAL_LANG.index(locale.getdefaultlocale()[0])
    else:
        lang_i = 0
    
    NAME_LABEL = ['Extrude for Cubes', '挤压 (方块)'][lang_i]
    NAME_VALUE = ['Offset', 'Offset'][lang_i]
    NAME_DEL_FACE = ['Delete Selected Faces', '删除选中面'][lang_i]
    NAME_DEL_OTHERS = ['Delete Other Faces', '删除其他面'][lang_i]
    NAME_UNIT = ['Unit of Measure', '单位'][lang_i]
    NAME_VOX = ['Minecraft Voxel (6.25cm)', 'MC体素 (6.25cm)'][lang_i]
    NAME_CM = ['Centimetre (cm)', '厘米 (cm)'][lang_i]
    NAME_M = ['Metre (m)', '米 (m)'][lang_i]
    
    def unit_conv(self, context):
        if self.unit == 'cm':
            self.value = self.value_o * 100
        elif self.unit == 'vox':
            self.value = self.value_o * 16
        else:
            self.value = self.value_o
    
    bl_idname = 'mesh.extrude_custom'
    bl_label = NAME_LABEL
    bl_options = {'REGISTER', 'UNDO'}
    
    value = bpy.props.FloatProperty(
        name = NAME_VALUE,
        # unit = 'LENGTH',
        min = -6.25,
        max = 6.25,
        default = 1/64,
        step = 1,
        precision = 6
    )
    
    value_o = bpy.props.FloatProperty(
        options = {'HIDDEN'},
        min = -6.25,
        max = 6.25,
        default = 1/64,
        update = unit_conv
    )
    
    unit = bpy.props.EnumProperty(
        name = NAME_UNIT,
        items = [
            ('m', NAME_M, NAME_M),
            ('cm', NAME_CM, NAME_CM),
            ('vox', NAME_VOX, NAME_VOX)
        ],
        default = 'm',
        update = unit_conv
    )
    
    del_face = bpy.props.BoolProperty(
        name = NAME_DEL_FACE,
        default = True
    )
    
    del_others = bpy.props.BoolProperty(
        name = NAME_DEL_OTHERS,
        default = False
    )
    
    def execute(self, context):
        if self.unit == 'cm':
            self.value_o = self.value / 100
        elif self.unit == 'vox':
            self.value_o = self.value / 16
        else:
            self.value_o = self.value
        if self.value_o > 1/16:
            self.value_o = 1/16
        elif self.value_o < -1/16:
            self.value_o = -1/16
        extrude_cus(self.value_o, self.del_face, self.del_others)
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(ExtrudeCustom.bl_idname, icon='MESH_CUBE')

    
def register():
    bpy.utils.register_class(ExtrudeCustom)
    bpy.types.VIEW3D_MT_edit_mesh_faces.append(menu_func)

     
def unregister():
    bpy.types.VIEW3D_MT_edit_mesh_faces.remove(menu_func)
    bpy.utils.unregister_class(ExtrudeCustom)        


if __name__ == '__main__':
    # os.system('cls')
    # print('== START ==\n')
    register()
    # test2(-0.2)
    # print('\n== END ==')


"""
def test(value):
    me = bpy.context.object.data
    bpy.ops.object.mode_set(mode="EDIT")
    
    if me.is_editmode is True:
        print('[Info] Edit mode is on.')
        flag = 0
    else:
        print('[Info] Edit mode is off.')
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action='SELECT')
        flag = 1

    bm = bmesh.from_edit_mesh(me)
    for v in bm.verts:
        tmp = mathutils.Vector((0.0, 0.0, 0.0))
        for _ in range(3):
            tmp[_] = sgn(v.normal[_], value)
        v.co += tmp
    bmesh.update_edit_mesh(me)
    
    if flag:
        bpy.ops.object.mode_set(mode="OBJECT")


def judge_overlap(*faces):
    x = 0
    for v in faces[0].verts:
        if v in face[1].verts:
            x += 1
    return x > 2


def test3():
    me = bpy.context.object.data
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(me)
    
    f_lis = []
    for face in bm.faces:
        if face.select:
            f_lis.append(face)
    face1, face2 = f_lis
    
    vs1 = {_ for _ in face1.verts}
    vs2 = {_ for _ in face2.verts}
    if len(vs1 & vs2) == 3:
        bm.faces.remove(face1)
        bm.faces.remove(face2)
        v_dif = [_ for _ in vs1 ^ vs2]
        for i in (vs1 & vs2):
            if len(i.link_edges) > 2 and not math.isclose(
                (i.co - v_dif[0].co).cross(i.co - v_dif[1].co).length, 0
            ):
                v_dif.append(i)
                return bm.faces.new(v_dif)
                # break
    # bmesh.update_edit_mesh(me)
"""
