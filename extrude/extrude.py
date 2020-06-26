# -*- coding: UTF-8 -*-
# Code by F_Qilin.

bl_info = {
    "name": "Extrude for Voxels",
    "category": "Mesh",
    "version": (1, 3, 1),
    "blender": (2, 80, 0),
    "location": "",
    "description": "An addon of better extrusion for Minecraft voxels",
    "warning": "",
    "wiki_url": "https://www.bilibili.com/video/av85835353?p=3",
    "author": "F_Qilin",
    "tracker_url": "https://www.popiask.cn/1abMMg"
}

try:
    import bpy
    import bmesh
    import math
    import mathutils
    import locale

    bool_exit = bpy.context is None
except ImportError:
    bool_exit = True
except AttributeError:
    bool_exit = True

if bool_exit:
    print('WARNING - Blender script does not run directly!')
    input('Press Enter to exit...')
    exit()


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


def judge_vec(vec, judge_type=0):
    tmp = [abs(_) for _ in vec]
    tmp.sort()
    for i in range(len(tmp)):
        if math.isclose(tmp[i - 1], tmp[i]):
            if type == 0:
                return False
            else:
                return None
    if judge_type == 1:
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


def del_useless(seq):
    del_lis = []
    for i in seq:
        if len(i.link_faces) < 1:
            del_lis.append(i)
    for i in del_lis:
        seq.remove(i)


def extrude_cus(value=1 / 64, del_face=True, del_others=False, remd=True):
    me = bpy.context.object.data
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(me)

    if del_others:
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.delete(type='FACE')
        bpy.ops.mesh.select_all(action='SELECT')
    if remd:
        bpy.ops.mesh.remove_doubles()

    v_lis = []
    v_special = {}
    for i in bm.verts:
        if i.select:
            v_lis.append(i)
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
            for x in range(-1, len(tmp_lis) - 1):
                tmp = (face.verts[x], face.verts[x + 1], tmp_lis[x + 1], tmp_lis[x])
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
    # NEW: Delete useless verts & edges.
    del_useless(bm.verts)
    del_useless(bm.edges)

    bmesh.update_edit_mesh(me)
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent()
    bpy.ops.mesh.select_all(action='DESELECT')
    for i in f_lis_new:
        try:
            i.select_set(True)
        except ReferenceError:
            pass


class ExtrudeCustom(bpy.types.Operator):
    """Extrude selected faces"""

    GLOBAL_LANG = ['en_US', 'zh_CN']

    # NEW: Blender 2.83 LTS.
    if hasattr(bpy.context, 'preferences'):
        # Blender 2.8x
        obj_sys = bpy.context.preferences.view
        if hasattr(obj_sys, 'use_international_fonts'):
            # Blender 2.80-2.82
            bool_usefonts = obj_sys.use_international_fonts
        else:
            # Blender 2.83+
            bool_usefonts = True
    elif hasattr(bpy.context, 'user_preferences'):
        # Blender 2.7x
        obj_sys = bpy.context.user_preferences.system
        bool_usefonts = obj_sys.use_international_fonts
    else:
        bool_usefonts = False

    if bool_usefonts:
        if obj_sys.language == 'DEFAULT':
            name_lang = locale.getdefaultlocale()[0]
        else:
            name_lang = obj_sys.language
        if name_lang in GLOBAL_LANG:
            lang_i = GLOBAL_LANG.index(name_lang)
        else:
            lang_i = 0
    else:
        lang_i = 0

    NAME_LABEL = ['Extrude for Voxels', '挤压 (体素)'][lang_i]
    NAME_VALUE = ['Offset', 'Offset'][lang_i]
    NAME_DEL_FACE = ['Delete Original Selected Faces', '删除原选中面'][lang_i]
    NAME_DEL_OTHERS = ['Delete Other Faces', '删除其他面'][lang_i]
    NAME_UNIT = ['Unit of Measure', '单位'][lang_i]
    NAME_VOX = ['Minecraft Voxel (6.25cm)', 'MC体素 (6.25cm)'][lang_i]
    NAME_CM = ['Centimetre (cm)', '厘米 (cm)'][lang_i]
    NAME_M = ['Metre (m)', '米 (m)'][lang_i]
    NAME_REMD = ['Merge Vertices by Distance', '按距离合并顶点'][lang_i]

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
        name=NAME_VALUE,
        # unit = 'LENGTH',
        # min = -6.25,
        # max = 6.25,
        default=1 / 64,
        step=1,
        precision=6
    )

    value_o = bpy.props.FloatProperty(
        options={'HIDDEN'},
        # min = -6.25,
        # max = 6.25,
        default=1 / 64,
        update=unit_conv
    )

    unit = bpy.props.EnumProperty(
        name=NAME_UNIT,
        items=[
            ('m', NAME_M, NAME_M),
            ('cm', NAME_CM, NAME_CM),
            ('vox', NAME_VOX, NAME_VOX)
        ],
        default='m',
        update=unit_conv
    )

    del_face = bpy.props.BoolProperty(
        name=NAME_DEL_FACE,
        default=True
    )

    del_others = bpy.props.BoolProperty(
        name=NAME_DEL_OTHERS,
        default=False
    )

    remd = bpy.props.BoolProperty(
        name=NAME_REMD,
        default=True
    )

    def execute(self, context):
        if self.unit == 'cm':
            self.value_o = self.value / 100
        elif self.unit == 'vox':
            self.value_o = self.value / 16
        else:
            self.value_o = self.value
        # if self.value_o > 1/16:
        #     self.value_o = 1/16
        # elif self.value_o < -1/16:
        #     self.value_o = -1/16
        extrude_cus(self.value_o, self.del_face, self.del_others, self.remd)
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
    register()
