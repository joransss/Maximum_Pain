"""Authoring helpers: key poses in Roblox terms onto the R15 rig built by mp_rig.py.

    clip = Clip("Name", length, loop=False, priority="Action", joints=None)
    clip.fk(t, "UpperTorso", cf(...))      # Motor6D.Transform of that joint
    clip.foot(t, "Right", frame)            # ankle joint frame, HumanoidRootPart space (IK)
    clip.hand(t, "Left", frame)             # wrist joint frame, HRP space with the chest at rest (IK, rides the chest)
    clip.gun(t, frame)                      # pistol Handle frame (HRP space, chest at rest) -> right wrist target
    clip.done()
Times are seconds. Keys use Blender's auto-clamped Bezier easing; loops get a Cycles modifier so the
easing wraps seamlessly. Unkeyed joints stay at rest.
"""
import bpy, math
from mathutils import Matrix, Vector

exec(open(__import__("os").path.join(__import__("os").path.dirname(__file__), "mp_common.py")).read(), globals())

ARM = bpy.data.objects["R15"]
Q = {b.name: bone_q(ARM, b.name) for b in ARM.data.bones if "rbx_joint" in b}
for _s in ("Right", "Left"):
    Q["IK_Foot." + _s[0]] = Q[_s + "Foot"]
    Q["IK_Hand." + _s[0]] = Q[_s + "Hand"]
ARMS = ["UpperTorso", "Head", "RightUpperArm", "RightLowerArm", "RightHand", "LeftUpperArm", "LeftLowerArm", "LeftHand"]
RIGHT_ARM = ["RightUpperArm", "RightLowerArm", "RightHand"]


def fcurves(act):
    if hasattr(act, "fcurves"):
        return act.fcurves
    from bpy_extras import anim_utils
    curves = []
    for slot in act.slots:
        cb = anim_utils.action_get_channelbag_for_slot(act, slot)
        if cb:
            curves.extend(cb.fcurves)
    return curves


def reset_pose():
    for pb in ARM.pose.bones:
        # A straight leg is a dead spot for Blender's IK; a small knee pre-bend picks the forward-knee solution.
        # IK fully overrides it, so it never reaches the exported pose.
        pb.matrix_basis = Matrix.Rotation(math.radians(-3), 4, "X") if pb.name.endswith("LowerLeg") else Matrix.Identity(4)
        for c in pb.constraints:
            c.influence = 1.0


def use_action(act):
    ad = ARM.animation_data or ARM.animation_data_create()
    ad.action = act
    if hasattr(ad, "action_slot") and len(act.slots):
        ad.action_slot = act.slots[0]


def rest_foot(side):
    return joint_frame(side + "Foot")


def rest_wrist(side):
    return joint_frame(side + "Hand")


class Clip:
    def __init__(self, name, length, loop=False, priority="Action", joints=None):
        old = bpy.data.actions.get(name)
        if old:
            bpy.data.actions.remove(old)
        self.act = bpy.data.actions.new(name)
        self.act.use_fake_user = True
        self.act["length"], self.act["loop"], self.act["priority"] = float(length), bool(loop), priority
        self.act["joints"] = list(joints or BONES)
        self.length, self.loop = length, loop
        reset_pose()
        ARM.animation_data_create()
        ARM.animation_data.action = self.act
        self.last = {}

    def _key(self, bone, basis, t):
        pb = ARM.pose.bones[bone]
        loc, rot, _ = basis.decompose()
        prev = self.last.get(bone)
        if prev is not None and prev.dot(rot) < 0:
            rot.negate()  # keep quaternion keys in one hemisphere so interpolation never flips
        self.last[bone] = rot
        pb.location, pb.rotation_quaternion = loc, rot
        f = t * FPS
        pb.keyframe_insert("location", frame=f, group=bone)
        pb.keyframe_insert("rotation_quaternion", frame=f, group=bone)

    def fk(self, t, bone, transform):
        self._key(bone, Q[bone].inverted() @ transform @ Q[bone], t)

    def _target(self, t, ctrl, frame):
        self._key(ctrl, ARM.data.bones[ctrl].matrix_local.inverted() @ C @ frame @ Q[ctrl], t)

    def foot(self, t, side, frame):
        self._target(t, "IK_Foot." + side[0], frame)

    def hand(self, t, side, frame):
        self._target(t, "IK_Hand." + side[0], frame)

    def gun(self, t, handle):
        self.hand(t, "Right", wrist_from_gun(handle))

    def done(self):
        for fc in fcurves(self.act):
            if self.loop and not fc.modifiers:
                fc.modifiers.new("CYCLES")
            for k in fc.keyframe_points:
                k.handle_left_type = k.handle_right_type = "AUTO_CLAMPED"
            fc.update()
        reset_pose()
        return self.act
