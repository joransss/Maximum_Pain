"""Builds the Maximum Pain R15 animation rig in the open Blender scene.
Run in Blender:  exec(open(r"<this folder>\\mp_rig.py").read(), {"__file__": r"<this folder>\\mp_rig.py"})

- Armature "R15": one bone per Roblox part (bone name = part name), bone heads at the Motor6D joints.
- Box proxies for every part and the 9mm pistol (from the Studio tool), parented to their bones.
- IK controls (not exported): IK_Foot.L/R (+ knee poles) and IK_Hand.L/R (+ elbow poles, children of UpperTorso).
"""
import bpy, bmesh, math
from mathutils import Matrix, Vector

exec(open(__import__("os").path.join(__import__("os").path.dirname(__file__), "mp_common.py")).read(), globals())

COLORS = {"skin": (0.62, 0.45, 0.35, 1), "jacket": (0.09, 0.09, 0.1, 1), "shirt": (0.75, 0.73, 0.68, 1),
          "pants": (0.14, 0.15, 0.17, 1), "shoes": (0.04, 0.03, 0.03, 1), "gun": (0.05, 0.05, 0.055, 1)}
PART_COLOR = {"Head": "skin", "UpperTorso": "jacket", "LowerTorso": "pants", "RightHand": "skin", "LeftHand": "skin",
              "RightFoot": "shoes", "LeftFoot": "shoes"}


def bp(v):
    return C @ Vector(v)


def material(key):
    m = bpy.data.materials.get("MP_" + key) or bpy.data.materials.new("MP_" + key)
    m.diffuse_color = COLORS[key]
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = COLORS[key]
    return m


def box(name, size, key):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    bm.to_mesh(me)
    bm.free()
    me.materials.append(material(key))
    obj = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def attach(obj, arm, bone, world):
    """Parent obj to a bone and place it at `world` (Blender space, rest pose)."""
    obj.parent, obj.parent_type, obj.parent_bone = arm, "BONE", bone
    b = arm.data.bones[bone]
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.matrix_basis = (b.matrix_local @ Matrix.Translation((0, b.length, 0))).inverted() @ world


def build():
    for o in list(bpy.data.objects):
        if o.name in ("Cube", "R15") or o.name.startswith("MP_") or o.get("mp_rig"):
            bpy.data.objects.remove(o, do_unlink=True)
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.unit_settings.system = "NONE"

    data = bpy.data.armatures.new("R15")
    arm = bpy.data.objects.new("R15", data)
    scene.collection.objects.link(arm)
    arm.show_in_front = True
    data.display_type = "STICK"
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    eb = data.edit_bones

    tails = {
        "HumanoidRootPart": JOINT_POS["HumanoidRootPart"] + Vector((0, 0, -1)),
        "LowerTorso": JOINT_POS["UpperTorso"], "UpperTorso": JOINT_POS["Head"],
        "Head": JOINT_POS["Head"] + Vector((0, 1.15, 0)),
    }
    for s in ("Right", "Left"):
        tails[s + "UpperArm"] = JOINT_POS[s + "LowerArm"]
        tails[s + "LowerArm"] = JOINT_POS[s + "Hand"]
        tails[s + "Hand"] = CENTER[s + "Hand"] + Vector((0, -0.16, 0))
        tails[s + "UpperLeg"] = JOINT_POS[s + "LowerLeg"]
        tails[s + "LowerLeg"] = JOINT_POS[s + "Foot"]
        tails[s + "Foot"] = JOINT_POS[s + "Foot"] + Vector((0, -0.1, -0.6))
    right = bp((1, 0, 0)) - bp((0, 0, 0))  # Roblox +X in Blender space

    def new_bone(name, head, tail, parent=None, deform=True):
        b = eb.new(name)
        b.head, b.tail = bp(head), bp(tail)
        z = right.cross((b.tail - b.head).normalized())
        if z.length > 1e-3:
            b.align_roll(z)
        b.parent = eb[parent] if parent else None
        b.use_deform = deform
        return b

    new_bone("HumanoidRootPart", JOINT_POS["HumanoidRootPart"], tails["HumanoidRootPart"])
    for name in BONES:
        new_bone(name, JOINT_POS[name], tails[name], PARENT[name])
    for s in ("Right", "Left"):
        sign = 1 if s == "Right" else -1
        new_bone("IK_Foot." + s[0], JOINT_POS[s + "Foot"], tails[s + "Foot"], "HumanoidRootPart", False)
        knee = JOINT_POS[s + "LowerLeg"]
        new_bone("Pole_Knee." + s[0], knee + Vector((0, 0, -3)), knee + Vector((0, 0.4, -3)), "HumanoidRootPart", False)
        new_bone("IK_Hand." + s[0], JOINT_POS[s + "Hand"], tails[s + "Hand"], "UpperTorso", False)
        elbow = JOINT_POS[s + "LowerArm"]
        new_bone("Pole_Elbow." + s[0], elbow + Vector((sign * 0.8, -0.6, 2.5)), elbow + Vector((sign * 0.8, -0.2, 2.5)), "UpperTorso", False)
    bpy.ops.object.mode_set(mode="OBJECT")

    for name in BONES:
        data.bones[name]["rbx_joint"] = list(JOINT_POS[name])
    arm["rbx_bones"] = BONES

    # IK: lower limb chains of 2 reach the control; hands and feet copy the control's rotation.
    # Pole angles were searched so the solved chain equals the rest pose exactly (error < 2e-4 studs).
    pole_angles = {"RightLowerLeg": 90, "LeftLowerLeg": 90, "RightLowerArm": -71.1, "LeftLowerArm": -108.9}
    for s in ("Right", "Left"):
        k = s[0]
        for limb, ctrl, pole, end in (("LowerLeg", "IK_Foot.", "Pole_Knee.", "Foot"), ("LowerArm", "IK_Hand.", "Pole_Elbow.", "Hand")):
            pb = arm.pose.bones[s + limb]
            ik = pb.constraints.new("IK")
            ik.name = "IK"
            ik.target, ik.subtarget = arm, ctrl + k
            ik.pole_target, ik.pole_subtarget = arm, pole + k
            ik.pole_angle = math.radians(pole_angles[s + limb])
            ik.chain_count = 2
            ik.use_tail = True
            ik.use_stretch = False
            cr = arm.pose.bones[s + end].constraints.new("COPY_ROTATION")
            cr.name = "IK_Rot"
            cr.target, cr.subtarget = arm, ctrl + k

    # Proxies
    for name in ["HumanoidRootPart"] + BONES:
        if name == "HumanoidRootPart":
            continue
        key = PART_COLOR.get(name) or ("jacket" if "Arm" in name else "pants")
        obj = box("MP_" + name, SIZES[name], key)
        obj["mp_rig"] = True
        attach(obj, arm, name, C @ Matrix.Translation(CENTER[name]))
    hand = Matrix.Translation(CENTER["RightHand"])
    handle = hand @ HANDLE_IN_HAND
    for part, (size, pos) in GUN_PARTS.items():
        obj = box("MP_Gun_" + part, size, "gun")
        obj["mp_rig"] = True
        attach(obj, arm, "RightHand", C @ handle @ Matrix.Translation(pos))
    muzzle = bpy.data.objects.new("MP_Muzzle", None)
    muzzle.empty_display_size = 0.15
    scene.collection.objects.link(muzzle)
    muzzle["mp_rig"] = True
    attach(muzzle, arm, "RightHand", C @ handle @ Matrix.Translation(MUZZLE))
    return arm


arm = build()
