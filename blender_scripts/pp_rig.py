# Penis Rig v. 1.1.1

# HOW TO USE:
# Select the chain of bones for the penis, then run (play button in text editor).


# TIPS:
# You can parent 'penis_trg_ctrl' to the hole.
# You can scale the penis rotation bone to control the falloff.


cs_segment = "cs_pen_segment"  # custom shape name (if any)
cs_target = "cs_pen_target"
cs_rotation_ctrl = "cs_pen_rot"

import bpy
from mathutils import Vector
from rna_prop_ui import rna_idprop_ui_create
import math


def spawn_bone(arm, name, c_head, c_tail, roll, parent=None, use_deform=False):
    ebone = arm.data.edit_bones.new(name)
    ebone.tail = c_tail
    ebone.head = c_head
    ebone.roll = roll
    ebone.use_deform = use_deform
    if parent:
        ebone.parent = parent
    return ebone.name


def bones_to_names(arm, ebones):
    names = []
    for eb in ebones:
        names.append(eb.name)
    return names


def get_ebone(arm, name):
    return arm.data.edit_bones[name]


def get_pbone(arm, name):
    return arm.pose.bones[name]


def vec_distance(v1, v2):
    return math.sqrt(((v1[0] - v2[0]) ** 2) + ((v1[1] - v2[1]) ** 2) + ((v1[2] - v2[2]) ** 2))


def custom_property(pb, name, dft, min=0.0, max=1000.0, overrideable=False):
    rna_idprop_ui_create(pb, name, default=dft, min=min, max=max, description='', overridable=overrideable)


def rebuild_hierarchy(arm, bones):
    ordered_bones = []
    origin = None
    # find the origin bone
    for b in bones:
        if b.parent not in bones:
            origin = b
            ordered_bones.append(origin)
            break

    while_break = False
    b = origin
    while not while_break:
        while_break = True
        for bc in b.children:
            if bc in bones:
                b = bc
                ordered_bones.append(bc)
                while_break = False
                break

    return ordered_bones


def get_master(arm, bone):
    while True:
        if bone.parent:
            bone = bone.parent
        else:
            return bone.name


def GE_driver_simple(arm, b, c):
    d = c.driver_add('influence').driver
    v = d.variables.new()
    v.name = 'GE'
    v.type = 'SINGLE_PROP'
    v.targets[0].id_type = 'OBJECT'
    v.targets[0].id = arm
    v.targets[0].data_path = 'pose.bones["' + b + '"]["GAME_EXPORT_PENIS"]'

    d.expression = '1 - GE'


def move_to_layer(bone, layername, visible=False):
    arm = bone.id_data

    bone_coll = arm.collections.get(layername)
    if not bone_coll:
        bone_coll = arm.collections.new(layername)

    bone_coll.is_visible = visible

    bone_coll.assign(bone)
    for iter_bone_coll in arm.collections:
        if iter_bone_coll.name != layername:
            iter_bone_coll.unassign(bone)


scene = bpy.context.scene

bpy.ops.object.mode_set(mode='EDIT')
arm = bpy.context.selected_editable_objects[0]
bones_def = rebuild_hierarchy(arm, bpy.context.selected_bones.copy())
scale_ref = vec_distance(bones_def[0].head, bones_def[0].tail)
bones_def = bones_to_names(arm, bones_def)
bones_trg_rot = []
bones_trg_loc = []
bones_ctrl = []

# get cs from names
if cs_segment:
    cs_segment = bpy.data.objects.get(cs_segment)
if cs_target:
    cs_target = bpy.data.objects.get(cs_target)
if cs_rotation_ctrl:
    cs_rotation_ctrl = bpy.data.objects.get(cs_rotation_ctrl)

# penis root bone
if get_ebone(arm, bones_def[0]).parent:
    bone_root = get_ebone(arm, bones_def[0]).parent.name
else:
    b = get_ebone(arm, bones_def[0])
    bone_root = spawn_bone(arm,
                           'penis_root',
                           b.head,
                           (b.head + Vector((0, scale_ref * 1.5, 0))),
                           b.roll,
                           None,
                           True
                           )
    b.parent = get_ebone(arm, bone_root)

# spawn bone_trg
b = get_ebone(arm, bones_def[0])
parent = get_ebone(arm, bone_root)

bone_trg = spawn_bone(arm,
                      'penis_trg',
                      b.head,
                      b.tail,
                      b.roll,
                      parent,
                      True)

bone_trg_ctrl = spawn_bone(arm,
                           'penis_trg_ctrl',
                           b.head,
                           b.tail,
                           b.roll,
                           None)

bone_rot_ctrl = spawn_bone(arm,
                           'penis_rot_ctrl',
                           b.head + Vector((scale_ref * 1.5, 0, 0)),
                           b.tail + Vector((scale_ref * 1.5, 0, 0)),
                           b.roll,
                           parent,
                           True)

# spawn bone for variables
bone_var = spawn_bone(arm,
                      'penis_variables',
                      parent.head + Vector((scale_ref, 0, 0)),
                      parent.tail + Vector((scale_ref, 0, 0)),
                      parent.roll,
                      parent)

# setup the
for i in range(0, len(bones_def)):
    b = get_ebone(arm, bones_def[i])

    # spawn the driver bones
    # parent the chair origin to target bone
    if i == 0:
        parent = get_ebone(arm, bone_trg)
    else:
        parent = get_ebone(arm, bones_trg_rot[i - 1])

    bones_trg_rot.append(spawn_bone(arm,
                                    'penis_trg_rot_' + str(i + 1),
                                    b.head,
                                    b.tail,
                                    b.roll,
                                    parent))
    bones_trg_loc.append(spawn_bone(arm,
                                    'penis_trg_loc_' + str(i + 1),
                                    b.tail,
                                    (b.tail + Vector((0, scale_ref, 0))),
                                    b.roll,
                                    get_ebone(arm, bones_trg_rot[i])))

    # spawn the ctrl bones

    if i == 0:
        parent = get_ebone(arm, bone_root)
    else:
        parent = get_ebone(arm, bones_ctrl[i - 1])

    bones_ctrl.append(spawn_bone(arm,
                                 'penis_ctrl_' + str(i + 1),
                                 b.head,
                                 b.tail,
                                 b.roll,
                                 parent,
                                 True))

# spawn in the ctrl bone on the top (unreal compatibility hack)
b = get_ebone(arm, bones_ctrl[len(bones_ctrl) - 1])
bones_ctrl.append(spawn_bone(arm,
                             'penis_ctrl_' + str(i + 2),
                             b.tail,
                             (b.tail + Vector((0, 0, scale_ref))),
                             b.roll,
                             b,
                             True))

bone_base = bones_ctrl[0]

# spawn bone_trg_aim
parent = get_ebone(arm, bone_trg)
b = get_ebone(arm, bones_ctrl[0])
bone_trg_aim = spawn_bone(arm,
                          'penis_trg_ctrl_aim',
                          b.tail,
                          b.tail + (b.tail - b.head),
                          parent.roll,
                          parent)

# create constraints
bpy.ops.object.mode_set(mode='POSE')

# Create Game Exporting property
# bone_character_master = get_master(arm, get_pbone(arm, bone_root))
bone_character_master = bone_root
custom_property(get_pbone(arm, bone_character_master), "GAME_EXPORT_PENIS", 0, min=0, max=1, overrideable=True)

# Copy local transform to the trg bone
b = get_pbone(arm, bone_trg)
c = b.constraints.new('COPY_TRANSFORMS')
c.target = arm
c.subtarget = bone_trg_ctrl

# Damped Track for the ctrl base bone

# fix for Y rotation of ctrl bones
b = get_pbone(arm, bones_ctrl[0])
c = b.constraints.new('COPY_ROTATION')
c.target = arm
c.subtarget = bone_trg_aim
c.name = 'dick_tilt'
c.influence = 0.0
# GE_driver_simple(arm, bone_character_master, c)

c = b.constraints.new('DAMPED_TRACK')
c.target = arm
c.subtarget = bone_trg_aim
GE_driver_simple(arm, bone_character_master, c)

# Move Aim Target down when Target_ctrl goes up (better rotational controls)
b = get_pbone(arm, bone_trg_aim)
c = b.constraints.new('TRANSFORM')
c.target = arm
c.subtarget = bone_trg
c.target_space = 'LOCAL'
c.owner_space = 'LOCAL'
c.use_motion_extrapolate = True
c.from_max_y = 1.0
c.to_max_y = -0.5
GE_driver_simple(arm, bone_character_master, c)

# measure the distances
measure_list = []
measure_list.append(bone_trg)
measure_list = measure_list + bones_trg_loc

parent = get_pbone(arm, bone_base)
parent_location = arm.matrix_world @ parent.matrix @ parent.location
dis_avg = 0.0
dis_last = 0.0
b_var = get_pbone(arm, bone_var)
for i in range(0, len(measure_list)):
    b = get_pbone(arm, measure_list[i])
    b_location = arm.matrix_world @ b.matrix @ b.location
    dis = vec_distance(parent_location, b_location)
    custom_property(b_var, "dis_default_" + str(i), dis)
    custom_property(b_var, "dis_" + str(i), dis)
    #    bpy.context.view_layer.update()

    # scale support driver
    d = b_var.driver_add('["dis_' + str(i) + '"]').driver
    d.type = 'SCRIPTED'

    v = d.variables.new()
    v.name = 'default'
    v.type = 'SINGLE_PROP'
    v.targets[0].id_type = 'OBJECT'
    v.targets[0].id = arm
    v.targets[0].data_path = 'pose.bones["' + bone_var + '"]["dis_default_' + str(i) + '"]'

    v = d.variables.new()
    v.name = 'parent_scale'
    v.type = 'TRANSFORMS'
    v.targets[0].id = arm
    v.targets[0].bone_target = bone_root
    v.targets[0].transform_type = 'SCALE_Y'
    v.targets[0].transform_space = 'WORLD_SPACE'

    d.expression = 'default'

    for k in range(i, -1, -1):
        v = d.variables.new()
        v.name = 'scale' + str(k)
        v.type = 'TRANSFORMS'
        v.targets[0].id = arm
        v.targets[0].bone_target = bones_ctrl[k]
        v.targets[0].transform_type = 'SCALE_Y'
        v.targets[0].transform_space = 'WORLD_SPACE'
        if k == i:
            d.expression += '* ((scale' + str(k)
        else:
            d.expression += '+' + 'scale' + str(k)
    d.expression += ') / (' + str(i + 1) + '* parent_scale))'

    # average distance
    if i != 0:
        dis_avg += dis - dis_last
    dis_last = dis

dis_avg = dis_avg / (len(measure_list) - 1)
custom_property(get_pbone(arm, bone_var), "dis_avg_default", dis_avg)
custom_property(get_pbone(arm, bone_var), "dis_avg", dis_avg)

# driver to control the average scale during animation
d = b_var.driver_add('["dis_avg"]').driver
d.type = 'SCRIPTED'

v = d.variables.new()
v.name = 'control'
v.type = 'TRANSFORMS'
v.targets[0].id = arm
v.targets[0].bone_target = bone_rot_ctrl
v.targets[0].transform_type = 'SCALE_Y'
v.targets[0].transform_space = 'LOCAL_SPACE'

v = d.variables.new()
v.name = 'dis_avg'
v.type = 'SINGLE_PROP'
v.targets[0].id_type = 'OBJECT'
v.targets[0].id = arm
v.targets[0].data_path = 'pose.bones["' + bone_var + '"]["dis_avg_default"]'

d.expression = 'dis_avg * control'

# create constraints on segment bones
for i in range(0, len(bones_def)):
    b = get_pbone(arm, bones_def[i])
    btl = get_pbone(arm, bones_trg_loc[i])
    btr = get_pbone(arm, bones_trg_rot[i])
    btc = get_pbone(arm, bones_ctrl[i])

    c = b.constraints.new('COPY_SCALE')
    c.target = arm
    c.subtarget = bones_ctrl[i]
    c.target_space = 'LOCAL'
    c.owner_space = 'LOCAL'
    GE_driver_simple(arm, bone_character_master, c)

    # twist controls
    c = b.constraints.new('COPY_ROTATION')
    c.target = arm
    c.subtarget = bones_ctrl[i]
    c.target_space = 'WORLD'
    c.owner_space = 'WORLD'
    GE_driver_simple(arm, bone_character_master, c)

    c = b.constraints.new('DAMPED_TRACK')
    c.target = arm
    c.subtarget = btl.name
    GE_driver_simple(arm, bone_character_master, c)

    # loc targets constraints
    c = btl.constraints.new('COPY_LOCATION')
    c.target = arm
    c.subtarget = bone_trg

    custom_property(btl, "inf_1", 0.0, min=0.0, max=1.0)

    # driver
    d = btl.driver_add('["inf_1"]').driver
    d.type = 'SCRIPTED'

    # distance to target
    v = d.variables.new()
    v.name = 'dis_b_t'
    v.type = 'LOC_DIFF'
    v.targets[0].id = arm
    v.targets[0].bone_target = bone_base
    v.targets[1].id = arm
    v.targets[1].bone_target = bone_trg

    # distance last
    v = d.variables.new()
    v.name = 'dis_last'
    v.type = 'SINGLE_PROP'
    v.targets[0].id_type = 'OBJECT'
    v.targets[0].id = arm
    v.targets[0].data_path = 'pose.bones["' + bone_var + '"]["dis_' + str(i) + '"]'

    # distance
    v = d.variables.new()
    v.name = 'dis'
    v.type = 'SINGLE_PROP'
    v.targets[0].id_type = 'OBJECT'
    v.targets[0].id = arm
    v.targets[0].data_path = 'pose.bones["' + bone_var + '"]["dis_' + str(i + 1) + '"]'

    # distance average
    v = d.variables.new()
    v.name = 'dis_avg'
    v.type = 'SINGLE_PROP'
    v.targets[0].id_type = 'OBJECT'
    v.targets[0].id = arm
    v.targets[0].data_path = 'pose.bones["' + bone_var + '"]["dis_avg"]'

    d.expression = '(dis_b_t-dis_last+dis_avg) / (dis-dis_last+(dis_avg))'  # d.expression = '(dis_b_t-dis_last+dis_avg) / (dis-dis_last+(dis_avg/2))' for half bone path

    # ease in out
    d = c.driver_add('influence').driver
    v = d.variables.new()
    v.name = 'inf'
    v.type = 'SINGLE_PROP'
    v.targets[0].id_type = 'OBJECT'
    v.targets[0].id = arm
    v.targets[0].data_path = 'pose.bones["' + btl.name + '"]["inf_1"]'

    v = d.variables.new()
    v.name = 'GE'
    v.type = 'SINGLE_PROP'
    v.targets[0].id_type = 'OBJECT'
    v.targets[0].id = arm
    v.targets[0].data_path = 'pose.bones["' + bone_character_master + '"]["GAME_EXPORT_PENIS"]'

    # bezier blend
    d.expression = '(inf * inf * (3.0 - 2.0 * inf)) * (1 - GE)'

    c = btl.constraints.new('COPY_LOCATION')
    c.target = arm
    c.subtarget = bones_ctrl[i + 1]

    custom_property(btl, "inf_2", 0.0, min=0.0, max=1.0)

    # driver
    d = btl.driver_add('["inf_2"]').driver
    d.type = 'SCRIPTED'

    # distance to target
    v = d.variables.new()
    v.name = 'dis_b_t'
    v.type = 'LOC_DIFF'
    v.targets[0].id = arm
    v.targets[0].bone_target = bone_base
    v.targets[1].id = arm
    v.targets[1].bone_target = bone_trg

    # distance last
    v = d.variables.new()
    v.name = 'dis_last'
    v.type = 'SINGLE_PROP'
    v.targets[0].id_type = 'OBJECT'
    v.targets[0].id = arm
    v.targets[0].data_path = 'pose.bones["' + bone_var + '"]["dis_' + str(i) + '"]'

    # distance average
    v = d.variables.new()
    v.name = 'dis_avg'
    v.type = 'SINGLE_PROP'
    v.targets[0].id_type = 'OBJECT'
    v.targets[0].id = arm
    v.targets[0].data_path = 'pose.bones["' + bone_var + '"]["dis_avg"]'

    d.expression = '(dis_b_t-dis_last-dis_avg*2*.6)/(dis_avg*2)'

    # ease in out
    d = c.driver_add('influence').driver
    v = d.variables.new()
    v.name = 'inf'
    v.type = 'SINGLE_PROP'
    v.targets[0].id_type = 'OBJECT'
    v.targets[0].id = arm
    v.targets[0].data_path = 'pose.bones["' + btl.name + '"]["inf_2"]'

    v = d.variables.new()
    v.name = 'GE'
    v.type = 'SINGLE_PROP'
    v.targets[0].id_type = 'OBJECT'
    v.targets[0].id = arm
    v.targets[0].data_path = 'pose.bones["' + bone_character_master + '"]["GAME_EXPORT_PENIS"]'
    # bezier blend
    d.expression = '(inf * inf * (3.0 - 2.0 * inf)) * (1 - GE)'

    c = btr.constraints.new('COPY_LOCATION')
    c.target = arm
    c.subtarget = bones_ctrl[i]
    c.target_space = 'LOCAL'
    c.owner_space = 'LOCAL'
    GE_driver_simple(arm, bone_character_master, c)
    if i != 0:
        c = btr.constraints.new('COPY_ROTATION')
        c.target = arm
        c.subtarget = bones_ctrl[i]
        c.target_space = 'LOCAL'
        c.owner_space = 'LOCAL'
        GE_driver_simple(arm, bone_character_master, c)
    c = btr.constraints.new('COPY_SCALE')
    c.target = arm
    c.subtarget = bones_ctrl[i]
    c.target_space = 'LOCAL'
    c.owner_space = 'LOCAL'
    GE_driver_simple(arm, bone_character_master, c)

    # rotation controls
    if i != 0:
        c = btc.constraints.new('COPY_ROTATION')
        c.target = arm
        c.subtarget = bone_rot_ctrl
        c.target_space = 'LOCAL'
        c.owner_space = 'LOCAL'
        c.mix_mode = 'BEFORE'

    # custom shapes
    if cs_segment:
        btc.custom_shape = cs_segment
        btc.custom_shape_transform = b

    # move bones to layers
    move_to_layer(btc.bone, 'Penis_IK_Control', visible=True)
    move_to_layer(b.bone, 'PenisIK_deform')
    move_to_layer(btl.bone, 'PenisIK_Mech1')
    move_to_layer(btr.bone, 'PenisIK_Mech1')

# custom shape for target, rot_ctrl bone
if cs_target:
    b = get_pbone(arm, bone_trg_ctrl)
    b.custom_shape = cs_target

if cs_rotation_ctrl:
    b = get_pbone(arm, bone_rot_ctrl)
    b.custom_shape = cs_rotation_ctrl

b = get_pbone(arm, bone_trg_aim)
move_to_layer(b.bone, 'PenisIK_Mech2')

b = get_pbone(arm, bone_trg)
move_to_layer(b.bone, 'PenisIK_Mech2')

b = get_pbone(arm, bones_ctrl[len(bones_ctrl) - 1])
move_to_layer(b.bone, 'PenisIK_Mech2')
