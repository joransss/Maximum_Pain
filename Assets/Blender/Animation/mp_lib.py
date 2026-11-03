"""Maximum Pain - R15 animation toolkit for Blender.

Everything is authored in Roblox space: studs, Y up, the character facing -Z. A joint rotation here
is exactly the Transform Roblox applies to that joint (Motor6D or AnimationConstraint), so the
exported keyframes need no conversion. The armature sits under an empty that turns Roblox space into
Blender's Z-up view, so the viewport looks normal.

    build_rig()            the R15 rig (bones, part boxes, gun props, floor) from Roblox's default rig
    Pose / rot()           joint rotations in degrees about Roblox's axes
    leg_ik() / arm_ik()    two-bone IK: feet on the floor, hands on a gun
    Clip                   a clip: a function of time that returns a Pose, sampled and keyed
    bake() / export()      Blender actions, keyframe JSON for Studio, FBX for the Animation Editor
    render_sheet()         contact sheets for checking a clip frame by frame

Rotation convention (Roblox axes, in each joint's own frame, which is the parent part's frame):
    +X (pitch) swings a hanging limb forward; on the spine it leans back; on the knee it would bend
       forwards, so knee flexion is negative and elbow flexion positive.
    +Y (yaw) turns toward the character's left.
    +Z (roll) swings a hanging limb toward the character's right; on the spine it leans left.
"""
import json
import math
import os

import bpy
from mathutils import Matrix, Quaternion, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30


def V(x=0.0, y=0.0, z=0.0):
    return Vector((x, y, z))


# --- The rig: Roblox's default R15 (Players:CreateHumanoidModelFromDescription), studs, relative to the
# HumanoidRootPart. All joint frames are axis-aligned, so C0 and C1 are pure offsets.
PARTS = {
    "HumanoidRootPart": ((2.0, 2.0, 1.0), (0.0, 0.0, 0.0)),
    "LowerTorso": ((1.991, 0.401, 1.004), (0.0, -0.800, 0.0)),
    "UpperTorso": ((1.943, 1.698, 1.004), (0.0, 0.200, 0.0)),
    "Head": ((1.159, 1.182, 1.161), (0.0, 1.586, 0.0)),
    "RightUpperArm": ((1.001, 1.242, 1.002), (1.5, 0.369, 0.0)),
    "RightLowerArm": ((1.001, 1.118, 1.002), (1.5, -0.224, 0.0)),
    "RightHand": ((0.984, 0.316, 1.028), (1.5, -0.850, 0.0)),
    "LeftUpperArm": ((1.001, 1.242, 1.002), (-1.5, 0.369, 0.0)),
    "LeftLowerArm": ((1.001, 1.118, 1.002), (-1.5, -0.224, 0.0)),
    "LeftHand": ((0.984, 0.316, 1.028), (-1.5, -0.850, 0.0)),
    "RightUpperLeg": ((0.993, 1.363, 0.973), (0.5, -1.421, 0.0)),
    "RightLowerLeg": ((0.993, 1.301, 0.973), (0.5, -2.201, 0.0)),
    "RightFoot": ((1.009, 0.312, 1.001), (0.5, -2.850, 0.0)),
    "LeftUpperLeg": ((0.993, 1.363, 0.973), (-0.5, -1.421, 0.0)),
    "LeftLowerLeg": ((0.993, 1.301, 0.973), (-0.5, -2.201, 0.0)),
    "LeftFoot": ((1.009, 0.312, 1.001), (-0.5, -2.850, 0.0)),
}
# (joint, part0, part1, C0 offset in part0, C1 offset in part1), parents first. Roblox animations
# name each pose after part1.
JOINTS = [
    ("Root", "HumanoidRootPart", "LowerTorso", (0.0, -1.0, 0.0), (0.0, -0.19997, 0.0)),
    ("Waist", "LowerTorso", "UpperTorso", (0.0, 0.20002, 0.0), (0.0, -0.849, 0.0)),
    ("Neck", "UpperTorso", "Head", (0.0, 0.84903, 0.0), (0.0, -0.5758, 0.0)),
    ("RightShoulder", "UpperTorso", "RightUpperArm", (0.9716, 0.59751, 0.0), (-0.50053, 0.41892, 0.0)),
    ("RightElbow", "RightUpperArm", "RightLowerArm", (0.0, -0.35501, 0.0), (0.0, 0.27471, 0.0)),
    ("RightWrist", "RightLowerArm", "RightHand", (0.0, -0.53217, 0.0), (0.0, 0.13157, 0.0)),
    ("LeftShoulder", "UpperTorso", "LeftUpperArm", (-0.9716, 0.59751, 0.0), (0.50053, 0.41892, 0.0)),
    ("LeftElbow", "LeftUpperArm", "LeftLowerArm", (0.0, -0.35501, 0.0), (0.0, 0.27471, 0.0)),
    ("LeftWrist", "LeftLowerArm", "LeftHand", (0.0, -0.53217, 0.0), (0.0, 0.13157, 0.0)),
    ("RightHip", "LowerTorso", "RightUpperLeg", (0.5, -0.19997, 0.0), (0.0, 0.47139, 0.0)),
    ("RightKnee", "RightUpperLeg", "RightLowerLeg", (0.0, -0.44917, 0.0), (0.0, 0.41336, 0.0)),
    ("RightAnkle", "RightLowerLeg", "RightFoot", (0.0, -0.59649, 0.0), (0.0, 0.10602, 0.0)),
    ("LeftHip", "LowerTorso", "LeftUpperLeg", (-0.5, -0.19997, 0.0), (0.0, 0.47139, 0.0)),
    ("LeftKnee", "LeftUpperLeg", "LeftLowerLeg", (0.0, -0.44917, 0.0), (0.0, 0.41336, 0.0)),
    ("LeftAnkle", "LeftLowerLeg", "LeftFoot", (0.0, -0.59649, 0.0), (0.0, 0.10602, 0.0)),
]
JOINT = {j[0]: j for j in JOINTS}
POSE_NAME = {j[0]: j[2] for j in JOINTS}
PART_PARENT = {j[2]: j[1] for j in JOINTS}
JOINT_OF_PART = {j[2]: j[0] for j in JOINTS}
HIP_HEIGHT = 2.192
FOOT_HALF = 0.156  # foot part half height
SOLE_TO_ANKLE = FOOT_HALF + 0.10602  # sole up to the ankle pivot
# Standing soles relative to the HumanoidRootPart, from the joint chain (the stored part positions in
# PARTS are slightly off; the assembled rig is what counts). It equals -(1 + HIP_HEIGHT): Roblox's
# floor for this rig.
FLOOR = -1.0 + 0.19997 - 0.19997 - 0.47139 - 0.44917 - 0.41336 - 0.59649 - 0.10602 - FOOT_HALF
# A held gun: RightGripAttachment (hand) to the gun's Grip attachment, as LoadoutService hangs it.
GRIP = Matrix.Translation(V(0, -0.15778, 0)) @ Matrix.Rotation(math.radians(-90), 4, "X")

IDENTITY = Quaternion()
ZERO = V()


# --- Rotations and poses -------------------------------------------------------------------------
def rot(x=0.0, y=0.0, z=0.0):
    """Degrees about Roblox's axes: roll (Z) first, then pitch (X), then yaw (Y) (fromEulerAnglesYXZ)."""
    return (
        Quaternion(V(0, 1, 0), math.radians(y))
        @ Quaternion(V(1, 0, 0), math.radians(x))
        @ Quaternion(V(0, 0, 1), math.radians(z))
    )


MIRROR = Matrix.Diagonal((-1.0, 1.0, 1.0))


def mirror_quaternion(q):
    m = MIRROR @ q.to_matrix() @ MIRROR
    return m.to_quaternion()


def swap_side(name):
    if name.startswith("Right"):
        return "Left" + name[5:]
    if name.startswith("Left"):
        return "Right" + name[4:]
    return name


class Pose(dict):
    """Joint name -> (rotation Quaternion, translation Vector), Roblox's Transform for that joint."""

    def q(self, joint):
        return self[joint][0] if joint in self else IDENTITY.copy()

    def t(self, joint):
        return self[joint][1] if joint in self else ZERO.copy()

    def set(self, joint, x=0.0, y=0.0, z=0.0, move=None):
        self[joint] = (rot(x, y, z), V(*move) if move else self.t(joint))
        return self

    def turn(self, joint, q):
        """Adds a rotation in the joint's frame on top of what is there (pre-multiplied)."""
        self[joint] = (q @ self.q(joint), self.t(joint))
        return self

    def move(self, joint, x=0.0, y=0.0, z=0.0):
        self[joint] = (self.q(joint), self.t(joint) + V(x, y, z))
        return self

    def copy(self):
        return Pose({k: (q.copy(), t.copy()) for k, (q, t) in self.items()})

    def mirrored(self):
        out = Pose()
        for k, (q, t) in self.items():
            out[swap_side(k)] = (mirror_quaternion(q), MIRROR @ t)
        return out

    def only(self, joints):
        return Pose({k: v for k, v in self.items() if k in joints})


def blend(a, b, alpha, joints=None):
    """Interpolates two poses (slerp for rotations)."""
    out = Pose()
    names = joints or set(a.keys()) | set(b.keys())
    for j in names:
        qa, qb = a.q(j), b.q(j)
        if qa.dot(qb) < 0:
            qb = -qb
        out[j] = (qa.slerp(qb, alpha), a.t(j).lerp(b.t(j), alpha))
    return out


def overlay(base, extra, weight=1.0):
    """Adds `extra`'s rotations and offsets on top of `base` (pre-multiplied), scaled by weight."""
    out = base.copy()
    for j, (q, t) in extra.items():
        qq = IDENTITY.slerp(q if q.w >= 0 else -q, weight)
        out[j] = (qq @ out.q(j), out.t(j) + t * weight)
    return out


# --- Forward kinematics ---------------------------------------------------------------------------
def solve(pose):
    """World matrix (relative to the HumanoidRootPart) of every part for a pose."""
    world = {"HumanoidRootPart": Matrix.Identity(4)}
    for name, p0, p1, c0, c1 in JOINTS:
        q, t = pose.get(name, (IDENTITY, ZERO))
        world[p1] = (
            world[p0]
            @ Matrix.Translation(V(*c0))
            @ Matrix.Translation(t)
            @ q.to_matrix().to_4x4()
            @ Matrix.Translation(-V(*c1))
        )
    return world


def pivot(world, joint):
    """A joint's pivot in the world."""
    _, p0, _, c0, _ = JOINT[joint]
    return (world[p0] @ Matrix.Translation(V(*c0))).translation


def grip(world, side="Right"):
    """The world frame of a gun held in a hand: its Grip attachment (barrel along -Z, top along +Y)."""
    return world[side + "Hand"] @ GRIP


def sole(world, side):
    """Middle of a foot's sole."""
    return world[side + "Foot"] @ V(0, -FOOT_HALF, 0)


def lowest(pose):
    """The lowest corner of any body part's box for a pose (relative to the HumanoidRootPart)."""
    world = solve(pose)
    low = math.inf
    for part, (size, _) in PARTS.items():
        if part == "HumanoidRootPart":
            continue
        m = world[part]
        for sx in (-0.5, 0.5):
            for sy in (-0.5, 0.5):
                for sz in (-0.5, 0.5):
                    low = min(low, (m @ V(sx * size[0], sy * size[1], sz * size[2])).y)
    return low


def ground(pose, floor, clearance=0.02):
    """Moves the whole body (the Root joint) so its lowest point rests on the floor: lying poses."""
    return pose.move("Root", 0, floor + clearance - lowest(pose), 0)


# --- Inverse kinematics ---------------------------------------------------------------------------
def _frame(a, b):
    """Orthonormal basis from a primary direction and a secondary one (Gram-Schmidt)."""
    x = a.normalized()
    y = b - x * b.dot(x)
    if y.length < 1e-8:
        y = V(0, 0, 1) if abs(x.z) < 0.9 else V(1, 0, 0)
        y = y - x * y.dot(x)
    y.normalize()
    z = x.cross(y)
    return Matrix((x, y, z)).transposed()


def two_bone(pose, upper, middle, end, target, pole, pole_local, end_rotation=None):
    """Bends a three-joint limb so the end joint's pivot reaches `target` (world), the middle joint
    pointing toward `pole` (world direction). `pole_local` is the way the middle joint points in the
    upper part's own frame at rest (knees forward, elbows back). Optionally turns the end part to a
    world rotation. Writes the three joints into `pose` (rotations only)."""
    _, p0_u, p1_u, c0_u, c1_u = JOINT[upper]
    _, _, p1_m, c0_m, c1_m = JOINT[middle]
    _, _, _, c0_e, _ = JOINT[end]
    world = solve(pose)
    start = pivot(world, upper)
    bone1 = V(*c0_m) - V(*c1_u)
    bone2 = V(*c0_e) - V(*c1_m)
    length1, length2 = bone1.length, bone2.length
    reach = target - start
    # R15's shoulder pivot sits at the upper arm's inner corner, so a straight arm (parts in line)
    # is not pivot-in-line: its reach is |bone1 + bone2|, short of the bones' sum. Reaching further
    # would bend the elbow backward, so the reach stops at straight.
    straight = min((bone1 + bone2).length, length1 + length2 - 1e-4)
    distance = min(max(reach.length, abs(length1 - length2) + 1e-4), straight)
    direction = reach.normalized()
    side = pole - direction * pole.dot(direction)
    if side.length < 1e-6:
        side = V(0, 0, -1) - direction * direction.z
    side.normalize()
    along = (length1 * length1 - length2 * length2 + distance * distance) / (2 * distance)
    height = math.sqrt(max(length1 * length1 - along * along, 0.0))
    knee = start + direction * along + side * height
    stop = start + direction * distance

    parent_rotation = world[p0_u].to_quaternion()
    upper_world = _frame(knee - start, side) @ _frame(bone1, V(*pole_local)).transposed()
    lower_world = _frame(stop - knee, side) @ _frame(bone2, V(*pole_local)).transposed()
    upper_q = upper_world.to_quaternion()
    lower_q = lower_world.to_quaternion()
    pose[upper] = (parent_rotation.inverted() @ upper_q, ZERO.copy())
    pose[middle] = (upper_q.inverted() @ lower_q, ZERO.copy())
    if end_rotation is not None:
        pose[end] = (lower_q.inverted() @ end_rotation, ZERO.copy())
    return pose


def foot_rotation(yaw=0.0, pitch=0.0, roll=0.0):
    """A foot's world rotation: yaw turns the toes left, pitch lifts them, roll tips onto the outside."""
    return rot(pitch, yaw, roll)


def leg_ik(pose, side, sole_point, rotation=None, knee=None):
    """Plants a foot: its sole's middle at `sole_point` (world), turned by `rotation` (world), the knee
    toward `knee` (world direction, default forward)."""
    rotation = rotation or IDENTITY
    ankle = sole_point + rotation @ V(0, SOLE_TO_ANKLE, 0)
    return two_bone(pose, side + "Hip", side + "Knee", side + "Ankle", ankle, knee or V(0, 0, -1), (0, 0, -1), rotation)


def foot_on_floor(x, z, floor, yaw=0.0, toe=0.0, heel=0.0):
    """Sole position and rotation for a foot on the floor. `toe` lifts the toes about the heel (heel
    strike); `heel` lifts the heel about the toes (push-off). Degrees."""
    rotation = foot_rotation(yaw, toe - heel)
    middle = V(x, floor, z)
    turn = rot(0, yaw, 0)
    if toe > 0:  # pivot on the heel
        heel_point = middle + turn @ V(0, 0, 0.5)
        middle = heel_point + rotation @ V(0, 0, -0.5)
    elif heel > 0:  # pivot on the toes
        toe_point = middle + turn @ V(0, 0, -0.5)
        middle = toe_point + rotation @ V(0, 0, 0.5)
    return middle, rotation


def arm_ik(pose, side, wrist_target, hand_rotation=None, elbow=None):
    """Puts a wrist pivot at `wrist_target` (world), the elbow toward `elbow` (world direction)."""
    default_elbow = V(0.5 if side == "Right" else -0.5, -0.3, 1.0)
    return two_bone(
        pose,
        side + "Shoulder",
        side + "Elbow",
        side + "Wrist",
        wrist_target,
        elbow or default_elbow,
        (0, 0, 1),
        hand_rotation,
    )


def hand_for_grip(grip_frame):
    """The hand's world matrix whose grip frame (RightGripAttachment) sits at `grip_frame`."""
    return grip_frame @ GRIP.inverted()


def wrist_for_hand(hand_matrix, side):
    """The wrist pivot for a hand placed at `hand_matrix`."""
    _, _, _, _, c1 = JOINT[side + "Wrist"]
    return hand_matrix @ V(*c1)


def place_hand(pose, side, hand_matrix, elbow=None):
    """Puts a hand exactly at a world matrix (position and rotation) with arm IK."""
    return arm_ik(pose, side, wrist_for_hand(hand_matrix, side), hand_matrix.to_quaternion(), elbow)


def floor_guard(pose, floor):
    """Keeps hands and feet out of the floor: one that dips below it is lifted onto it with limb IK,
    keeping its rotation and the knee's or elbow's direction. Applied after keys are blended, where
    a limb can pass through the floor between two good poses."""
    for side in ("Left", "Right"):
        for end, upper, middle in (("Foot", "Hip", "Knee"), ("Hand", "Shoulder", "Elbow")):
            world = solve(pose)
            m = world[side + end]
            size = PARTS[side + end][0]
            low = min((m @ V(x * size[0], y * size[1], z * size[2])).y for x in (-0.5, 0.5) for y in (-0.5, 0.5) for z in (-0.5, 0.5))
            if low >= floor:
                continue
            lift = Matrix.Translation(V(0, floor - low, 0))
            bend = pivot(world, side + middle) - pivot(world, side + upper)
            if end == "Foot":
                leg_ik(pose, side, (lift @ m) @ V(0, -FOOT_HALF, 0), m.to_quaternion(), bend)
            else:
                place_hand(pose, side, lift @ m, bend)
    return pose


# --- Timing helpers -------------------------------------------------------------------------------
def smooth(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def smoother(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * u * (u * (u * 6 - 15) + 10)


def ease_out(u, power=2.0):
    u = min(max(u, 0.0), 1.0)
    return 1 - (1 - u) ** power


def ease_in(u, power=2.0):
    u = min(max(u, 0.0), 1.0)
    return u**power


def wave(t, period, phase=0.0):
    return math.sin(2 * math.pi * (t / period + phase))


class Keys:
    """Key poses on a timeline, interpolated with smooth (Catmull-Rom, clamped) curves per joint,
    like Blender's auto-clamped Bezier keys. `ease` per key: "smooth" (default), "linear", "hold"."""

    def __init__(self, loop_length=None):
        self.keys = []  # (time, Pose, ease)
        self.loop_length = loop_length

    def add(self, time, pose, ease="smooth"):
        self.keys.append((time, pose, ease))
        self.keys.sort(key=lambda k: k[0])
        return self

    def joints(self):
        names = set()
        for _, pose, _ in self.keys:
            names |= set(pose.keys())
        return names

    def at(self, t):
        keys = self.keys
        if self.loop_length:
            t = t % self.loop_length
        if t <= keys[0][0] and not self.loop_length:
            return keys[0][1].copy()
        if t >= keys[-1][0] and not self.loop_length:
            return keys[-1][1].copy()
        index = 0
        for i in range(len(keys)):
            if keys[i][0] <= t:
                index = i
        if self.loop_length:
            a = keys[index]
            b = keys[(index + 1) % len(keys)]
            span = (b[0] - a[0]) % self.loop_length or self.loop_length
            u = ((t - a[0]) % self.loop_length) / span
            before = keys[(index - 1) % len(keys)][1]
            after = keys[(index + 2) % len(keys)][1]
        else:
            a, b = keys[index], keys[min(index + 1, len(keys) - 1)]
            span = max(b[0] - a[0], 1e-6)
            u = (t - a[0]) / span
            before = keys[max(index - 1, 0)][1]
            after = keys[min(index + 2, len(keys) - 1)][1]
        if a[2] == "hold":
            return a[1].copy()
        if a[2] == "linear":
            return blend(a[1], b[1], u)
        out = Pose()
        for j in self.joints():
            out[j] = _catmull(before, a[1], b[1], after, j, u)
        return out


def _catmull(p0, p1, p2, p3, joint, u):
    """Clamped Catmull-Rom on quaternion components and translations (no overshoot past neighbours)."""
    qs = [p.q(joint) for p in (p0, p1, p2, p3)]
    for i in (0, 2, 3):
        ref = qs[1] if i == 0 else qs[i - 1]
        if qs[i].dot(ref) < 0:
            qs[i] = -qs[i]
    ts = [p.t(joint) for p in (p0, p1, p2, p3)]

    def curve(a, b, c, d):
        m1 = (c - a) * 0.5
        m2 = (d - b) * 0.5
        # clamp: a flat tangent where the curve turns, like Blender's auto-clamped handles
        if (b - a) * (c - b) <= 0:
            m1 = 0.0
        if (c - b) * (d - c) <= 0:
            m2 = 0.0
        u2, u3 = u * u, u * u * u
        return (2 * u3 - 3 * u2 + 1) * b + (u3 - 2 * u2 + u) * m1 + (-2 * u3 + 3 * u2) * c + (u3 - u2) * m2

    q = Quaternion([curve(qs[0][i], qs[1][i], qs[2][i], qs[3][i]) for i in range(4)])
    q.normalize()
    t = V(*[curve(ts[0][i], ts[1][i], ts[2][i], ts[3][i]) for i in range(3)])
    return (q, t)


# --- Clips ----------------------------------------------------------------------------------------
CLIPS = {}
BODY = [j[0] for j in JOINTS]
ARMS = {"RightShoulder", "RightElbow", "RightWrist", "LeftShoulder", "LeftElbow", "LeftWrist"}
RIGHT_ARM = {"RightShoulder", "RightElbow", "RightWrist"}
LEFT_ARM = {"LeftShoulder", "LeftElbow", "LeftWrist"}
LEGS = {"RightHip", "RightKnee", "RightAnkle", "LeftHip", "LeftKnee", "LeftAnkle"}


class Clip:
    """A clip: `pose(t)` gives the pose at time t. `joints` are the joints it keys (others are left to
    lower layers in Roblox). `drop` is the stance's hip drop (studs the game lowers the body), so the
    preview floor sits where the game's does. `props` lists scenery for the preview."""

    def __init__(self, name, length, pose, loop=False, priority="Movement", joints=None, drop=0.0,
                 markers=None, props=None, gun=None, fps=FPS, note=""):
        self.name = name
        self.length = length
        self.pose = pose
        self.loop = loop
        self.priority = priority
        self.joints = list(joints) if joints else list(BODY)
        self.drop = drop
        self.markers = markers or []  # (time, name, value)
        self.props = props or []
        self.gun = gun  # gun prop for previews: (right gun id, left gun id or None)
        self.fps = fps
        self.note = note
        CLIPS[name] = self

    def floor(self):
        return FLOOR + self.drop

    def sample(self, t):
        pose = self.pose(t)
        return Pose({j: pose[j] for j in self.joints if j in pose})


def mirror_clip(clip, name, swap_gun=False):
    """A left-right mirror of a clip (for side variants)."""
    joints = [swap_side(j) for j in clip.joints]
    return Clip(name, clip.length, lambda t: clip.pose(t).mirrored(), clip.loop, clip.priority, joints,
                clip.drop, list(clip.markers), [mirror_prop(p) for p in clip.props],
                clip.gun, clip.fps, clip.note + " (mirrored)")


def mirror_prop(prop):
    kind, size, position = prop
    return (kind, size, (-position[0], position[1], position[2]))


# --- Sampling and reduction -----------------------------------------------------------------------
def samples(clip):
    count = max(1, int(round(clip.length * clip.fps)))
    return [i / clip.fps for i in range(count)] + [clip.length]


def _q_angle(a, b):
    d = abs(a.dot(b))
    return 2 * math.acos(min(1.0, d))


def reduce_track(times, values, tolerance_angle=math.radians(0.35), tolerance_move=0.004):
    """Drops samples that the neighbours' linear interpolation reproduces within tolerance."""
    keep = [0]
    i = 0
    n = len(times)
    while i < n - 1:
        j = i + 2
        while j < n:
            ok = True
            for k in range(i + 1, j):
                u = (times[k] - times[i]) / (times[j] - times[i])
                qa, qb = values[i][0], values[j][0]
                if qa.dot(qb) < 0:
                    qb = -qb
                q = qa.slerp(qb, u)
                t = values[i][1].lerp(values[j][1], u)
                if _q_angle(q, values[k][0]) > tolerance_angle or (t - values[k][1]).length > tolerance_move:
                    ok = False
                    break
            if not ok:
                break
            j += 1
        keep.append(j - 1)
        i = j - 1
    return sorted(set(keep))


def clip_data(clip):
    """The clip as Roblox keyframe data: per-pose tracks of [time, x, y, z, qw, qx, qy, qz]."""
    times = samples(clip)
    poses = [clip.sample(t) for t in times]
    tracks = {}
    # By pose name, so every export writes the same file (a set's order changes between runs).
    for joint in sorted(clip.joints, key=lambda j: POSE_NAME[j]):
        values = [(p.q(joint), p.t(joint)) for p in poses]
        # keep quaternions on one hemisphere so interpolation never takes the long way
        for k in range(1, len(values)):
            if values[k][0].dot(values[k - 1][0]) < 0:
                values[k] = (-values[k][0], values[k][1])
        keep = reduce_track(times, values)
        rows = []
        for k in keep:
            q, t = values[k]
            rows.append([round(times[k], 4), round(t.x, 4), round(t.y, 4), round(t.z, 4),
                         round(q.w, 5), round(q.x, 5), round(q.y, 5), round(q.z, 5)])
        tracks[POSE_NAME[joint]] = rows
    return {
        "name": clip.name,
        "length": round(clip.length, 4),
        "loop": clip.loop,
        "priority": clip.priority,
        "markers": [[round(t, 4), n, v] for t, n, v in clip.markers],
        "tracks": tracks,
    }


# --- Checks ---------------------------------------------------------------------------------------
def hinge_angle(q):
    """Signed bend of a hinge joint about X, degrees (knees bend negative, elbows positive)."""
    angle = 2 * math.degrees(math.acos(min(1.0, abs(q.w))))
    axis_x = q.x if q.w >= 0 else -q.x
    return angle if axis_x >= 0 else -angle


def validate(clip, speed=0.0, direction=None, contact=0.02):
    """Numbers that say whether a clip is physically sound:
    sink    - deepest any sole goes below the floor (studs)
    slide   - worst drift of a planted foot over the ground while the body moves at `speed`
    knees   - range of knee bend (degrees, negative = flexion; positive would hyperextend)
    elbows  - range of elbow bend (positive = flexion)
    head    - lowest and highest head top above the game's floor (the floor HipHeight gives)"""
    direction = direction or V(0, 0, -1)
    floor = clip.floor()
    game_floor = -(1 + HIP_HEIGHT) + clip.drop
    step = 1.0 / clip.fps
    times = samples(clip)
    sink = 0.0
    slide = 0.0
    knees = [999.0, -999.0]
    elbows = [999.0, -999.0]
    heads = [999.0, -999.0]
    previous = {}
    for t in times:
        pose = clip.pose(t)
        world = solve(pose)
        for side in ("Left", "Right"):
            corners = [world[side + "Foot"] @ V(x * 0.5, -FOOT_HALF, z * 0.5) for x in (-1, 1) for z in (-1, 1)]
            sink = max(sink, floor - min(c.y for c in corners))
            # Each corner of the sole that stays on the floor from one frame to the next must not move
            # over the ground (the body moves at `speed`, so the ground moves the other way under it).
            for index, corner in enumerate(corners):
                key = (side, index)
                ground = corner + direction * speed * t
                touching = corner.y <= floor + contact
                if touching and key in previous and previous[key][1]:
                    drift = (V(ground.x, 0, ground.z) - V(previous[key][0].x, 0, previous[key][0].z)).length
                    slide = max(slide, drift / step)  # studs per second
                previous[key] = (ground, touching)
            k = hinge_angle(pose.q(side + "Knee"))
            e = hinge_angle(pose.q(side + "Elbow"))
            knees = [min(knees[0], k), max(knees[1], k)]
            elbows = [min(elbows[0], e), max(elbows[1], e)]
        head_top = (world["Head"] @ V(0, PARTS["Head"][0][1] / 2, 0)).y - game_floor
        heads = [min(heads[0], head_top), max(heads[1], head_top)]
    return {
        "sink": round(sink, 3),
        "slide": round(slide, 3),
        "knees": [round(knees[0]), round(knees[1])],
        "elbows": [round(elbows[0]), round(elbows[1])],
        "head": [round(heads[0], 2), round(heads[1], 2)],
    }


# --- Blender scene ---------------------------------------------------------------------------------
ROBLOX_TO_BLENDER = Matrix(((-1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
COLLECTION = "MP_R15"
COLORS = {
    "Head": (0.86, 0.78, 0.68, 1),
    "UpperTorso": (0.22, 0.24, 0.28, 1),
    "LowerTorso": (0.18, 0.19, 0.22, 1),
    "Arm": (0.30, 0.32, 0.36, 1),
    "Hand": (0.86, 0.78, 0.68, 1),
    "Leg": (0.25, 0.22, 0.20, 1),
    "Foot": (0.10, 0.10, 0.10, 1),
    "Gun": (0.05, 0.05, 0.05, 1),
    "Floor": (0.62, 0.62, 0.60, 1),
    "Prop": (0.50, 0.53, 0.58, 1),
}


def _color_for(part):
    if part == "Head":
        return COLORS["Head"]
    if part.endswith("Hand"):
        return COLORS["Hand"]
    if part.endswith("Foot"):
        return COLORS["Foot"]
    if "Arm" in part:
        return COLORS["Arm"]
    if "Leg" in part:
        return COLORS["Leg"]
    return COLORS.get(part, (0.5, 0.5, 0.5, 1))


def _box_mesh(name, size, center=(0, 0, 0)):
    sx, sy, sz = size[0] / 2, size[1] / 2, size[2] / 2
    cx, cy, cz = center
    verts = [(cx + x * sx, cy + y * sy, cz + z * sz) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return mesh


def _collection():
    col = bpy.data.collections.get(COLLECTION)
    if not col:
        col = bpy.data.collections.new(COLLECTION)
        bpy.context.scene.collection.children.link(col)
    return col


def rig():
    return bpy.data.objects.get("RIG_R15")


def build_rig():
    """Builds (or rebuilds) the rig: armature RIG_R15 with a bone per part, a box per part, gun props
    and a floor, under MP_RobloxSpace."""
    col = _collection()
    for obj in list(col.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for data in list(bpy.data.armatures):
        if data.users == 0:
            bpy.data.armatures.remove(data)
    space = bpy.data.objects.new("MP_RobloxSpace", None)
    space.matrix_world = ROBLOX_TO_BLENDER
    col.objects.link(space)
    armature = bpy.data.armatures.new("RIG_R15")
    obj = bpy.data.objects.new("RIG_R15", armature)
    col.objects.link(obj)
    obj.parent = space
    bpy.context.view_layer.objects.active = obj
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bones = armature.edit_bones
    root = bones.new("HumanoidRootPart")
    root.head, root.tail = V(0, 0, 0), V(0, 0.4, 0)
    rest = solve(Pose())
    for name, p0, p1, c0, c1 in JOINTS:
        bone = bones.new(p1)
        head = pivot(rest, name)
        bone.head, bone.tail = head, head + V(0, 0.25, 0)
        bone.roll = 0
        bone.parent = bones[p0]
        bone.use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")
    for pb in obj.pose.bones:
        pb.rotation_mode = "QUATERNION"
    obj.show_in_front = False
    armature.display_type = "STICK"
    bpy.context.view_layer.update()
    for part, (size, _) in PARTS.items():
        if part == "HumanoidRootPart":
            continue
        mesh = _box_mesh("GEO_" + part, size)
        geo = bpy.data.objects.new("GEO_" + part, mesh)
        col.objects.link(geo)
        geo.parent = obj
        geo.parent_type = "BONE"
        geo.parent_bone = part
        geo.color = _color_for(part)
        bpy.context.view_layer.update()
        geo.matrix_world = ROBLOX_TO_BLENDER @ rest[part]  # placed by the joints, like the assembled rig
    floor = bpy.data.objects.new("GEO_Floor", _box_mesh("GEO_Floor", (14, 0.02, 14), (0, -0.01, 0)))
    col.objects.link(floor)
    floor.parent = space
    floor.color = COLORS["Floor"]
    set_floor(FLOOR)
    bpy.context.view_layer.update()
    return obj


def set_floor(y):
    floor = bpy.data.objects.get("GEO_Floor")
    if floor:
        floor.matrix_parent_inverse = Matrix.Identity(4)
        floor.location = (0, y, 0)


def apply_pose(pose):
    """Poses the armature (no keyframes)."""
    obj = rig()
    for name, _, p1, _, _ in JOINTS:
        pb = obj.pose.bones[p1]
        q, t = pose.get(name, (IDENTITY, ZERO))
        pb.rotation_quaternion = q
        pb.location = t
    bpy.context.view_layer.update()


def _fcurves(action):
    """An action's F-curves. Blender 4.4 moved them into layers and slots, and 5.0 removed
    action.fcurves; older versions keep them on the action itself."""
    if hasattr(action, "fcurves"):
        return list(action.fcurves)
    curves = []
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                curves.extend(bag.fcurves)
    return curves


def bake(clip):
    """Keys the clip into a Blender action (one key per sampled frame) so the .blend holds it."""
    obj = rig()
    if obj.animation_data is None:
        obj.animation_data_create()
    old = bpy.data.actions.get(clip.name)
    if old:
        bpy.data.actions.remove(old)  # rebaking starts from an empty action
    action = bpy.data.actions.new(clip.name)
    action.use_fake_user = True
    obj.animation_data.action = action
    for t in samples(clip):
        frame = t * FPS
        pose = clip.sample(t)
        for joint in clip.joints:
            pb = obj.pose.bones[POSE_NAME[joint]]
            q, loc = pose.get(joint, (IDENTITY, ZERO))
            pb.rotation_quaternion = q
            pb.location = loc
            pb.keyframe_insert("rotation_quaternion", frame=frame)
            pb.keyframe_insert("location", frame=frame)
    for fc in _fcurves(action):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
    for t, name, _ in clip.markers:
        marker = action.pose_markers.new(name)
        marker.frame = int(round(t * FPS))
    action["length"] = clip.length
    action["loop"] = clip.loop
    action["priority"] = clip.priority
    return action


# --- Props for previews ---------------------------------------------------------------------------
GUNS = {
    # id: (handle box size, handle centre, magazine size, magazine centre, support point) in grip space
    "Pistol": ((0.11, 0.43, 0.80), (0, 0, -0.25), (0.09, 0.37, 0.24), (0, -0.06, 0.04), (-0.05, -0.10, -0.02)),
    "Revolver": ((0.17, 0.71, 1.30), (0, 0.07, -0.50), (0.18, 0.18, 0.21), (0, 0.25, -0.19), (-0.06, -0.14, -0.03)),
    "SMG": ((0.18, 0.73, 1.70), (0, 0.13, -0.12), (0.09, 0.77, 0.17), (0, -0.15, 0.02), (0, 0.19, -0.44)),
    "SawnOff": ((0.17, 0.57, 1.80), (0, 0.18, -0.70), (0.16, 0.07, 0.22), (0, 0.31, -0.57), (0, 0.19, -0.84)),
    "Rifle": ((0.14, 0.65, 3.20), (0, 0.06, -0.43), (0.11, 0.87, 0.38), (0, -0.21, -0.47), (0, 0.16, -0.92)),
    "Shotgun": ((0.14, 0.65, 3.60), (0, -0.11, -0.62), (0.17, 0.16, 0.85), (0, 0.0, -1.31), (0, -0.08, -1.43)),
    "Sniper": ((0.21, 1.09, 5.00), (0, 0.33, -0.95), (0.14, 0.44, 0.53), (0, 0.07, -0.60), (0, 0.31, -1.02)),
}


def gun_support(kind):
    return V(*GUNS[kind][4])


def show_gun(side, kind):
    """Shows a gun prop in a hand (None hides it)."""
    col = _collection()
    name = "GEO_Gun_" + side
    for old_name in (name, name + "_Mag"):
        old = bpy.data.objects.get(old_name)
        if old:
            bpy.data.objects.remove(old, do_unlink=True)
    if not kind:
        return None
    handle_size, handle_center, mag_size, mag_center, _ = GUNS[kind]
    mesh = _box_mesh(name, handle_size, handle_center)
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    mag = bpy.data.objects.new(name + "_Mag", _box_mesh(name + "_Mag", mag_size, mag_center))
    col.objects.link(mag)
    for o in (obj, mag):
        o.parent = rig()
        o.parent_type = "BONE"
        o.parent_bone = side + "Hand"
        o.color = COLORS["Gun"]
    bpy.context.view_layer.update()
    rest = solve(Pose())
    frame = grip(rest, side)
    obj.matrix_world = ROBLOX_TO_BLENDER @ frame
    mag.matrix_world = ROBLOX_TO_BLENDER @ frame
    return obj


def set_props(props):
    """Scenery for a preview: ("box", size, centre) in Roblox space relative to the root part."""
    col = _collection()
    for obj in list(col.objects):
        if obj.name.startswith("GEO_Prop"):
            bpy.data.objects.remove(obj, do_unlink=True)
    space = bpy.data.objects.get("MP_RobloxSpace")
    for i, (kind, size, center) in enumerate(props):
        obj = bpy.data.objects.new("GEO_Prop%d" % i, _box_mesh("GEO_Prop%d" % i, size, center))
        col.objects.link(obj)
        obj.parent = space
        obj.color = COLORS["Prop"]


# --- Previews --------------------------------------------------------------------------------------
VIEWS = {
    # name: (camera position, look-at point) in Roblox space
    "front": ((5.5, 1.0, -9.5), (0, -0.6, 0)),
    "side": ((11.0, 0.2, 0.0), (0, -0.6, 0)),
    "back": ((-4.5, 1.6, 9.5), (0, -0.6, 0)),
    "top": ((0.0, 12.0, 0.01), (0, -0.6, 0)),
    "chest": ((3.4, 1.4, -4.6), (0, 0.35, -0.7)),  # close on the arms and gun
    "chest_side": ((5.8, 0.9, -0.8), (0, 0.35, -0.8)),
}


def _camera():
    cam = bpy.data.objects.get("MP_Camera")
    if not cam:
        data = bpy.data.cameras.new("MP_Camera")
        cam = bpy.data.objects.new("MP_Camera", data)
        bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    return cam


def _look(position, target):
    p = ROBLOX_TO_BLENDER @ V(*position)
    q = ROBLOX_TO_BLENDER @ V(*target)
    direction = q - p
    return Matrix.Translation(p) @ direction.to_track_quat("-Z", "Y").to_matrix().to_4x4()


def render_sheet(clip, path, frames=8, views=("front", "side"), size=300, times=None):
    """Renders `frames` evenly spaced poses of a clip for each view and tiles them into one PNG."""
    import numpy as np

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "OBJECT"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.render.resolution_x = size
    scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    cam = _camera()
    cam.data.lens = 50
    set_floor(clip.floor())
    set_props(clip.props)
    guns = clip.gun or (None, None)
    show_gun("Right", guns[0])
    show_gun("Left", guns[1] if len(guns) > 1 else None)
    times = times or [clip.length * i / max(frames - 1, 1) for i in range(frames)]
    tiles = []
    tmp = os.path.join(os.path.dirname(path), "_frame.png")
    for view in views:
        row = []
        position, target = VIEWS[view]
        cam.matrix_world = _look(position, target)
        for t in times:
            apply_pose(clip.pose(t))
            scene.render.filepath = tmp
            bpy.ops.render.render(write_still=True)
            image = bpy.data.images.load(tmp, check_existing=False)
            pixels = np.array(image.pixels[:], dtype=np.float32).reshape(size, size, 4)
            bpy.data.images.remove(image)
            row.append(pixels)
        tiles.append(np.concatenate(row, axis=1))
    sheet = np.concatenate(tiles[::-1], axis=0)
    height, width = sheet.shape[0], sheet.shape[1]
    out = bpy.data.images.new("MP_Sheet", width=width, height=height, alpha=True)
    out.pixels = sheet.ravel()
    out.filepath_raw = path
    out.file_format = "PNG"
    out.save()
    bpy.data.images.remove(out)
    if os.path.exists(tmp):
        os.remove(tmp)
    apply_pose(Pose())
    return path


def render_grid(entries, path, views=("front", "side"), size=230):
    """One contact sheet for several clips: `entries` is a list of (clip name, time); each becomes a
    column, each view a row."""
    import numpy as np

    columns = []
    tmp = os.path.join(os.path.dirname(path), "_cell.png")
    for name, t in entries:
        render_sheet(CLIPS[name], tmp, frames=1, views=views, size=size, times=[t])
        image = bpy.data.images.load(tmp, check_existing=False)
        width, height = image.size
        columns.append(np.array(image.pixels[:], dtype=np.float32).reshape(height, width, 4))
        bpy.data.images.remove(image)
    if os.path.exists(tmp):
        os.remove(tmp)
    sheet = np.concatenate(columns, axis=1)
    out = bpy.data.images.new("MP_Grid", width=sheet.shape[1], height=sheet.shape[0], alpha=True)
    out.pixels = sheet.ravel()
    out.filepath_raw = path
    out.file_format = "PNG"
    out.save()
    bpy.data.images.remove(out)
    return path


# --- Export ----------------------------------------------------------------------------------------
def export(names=None, folder=None, fbx=False):
    """Writes keyframes.json (every clip, exact Transforms for Studio) and optionally one FBX per clip."""
    folder = folder or os.path.join(HERE, "Exports")
    os.makedirs(folder, exist_ok=True)
    chosen = [CLIPS[n] for n in (names or sorted(CLIPS))]
    data = [clip_data(c) for c in chosen]
    path = os.path.join(folder, "keyframes.json")
    existing = {}
    if names and os.path.exists(path):
        with open(path) as fh:
            existing = {c["name"]: c for c in json.load(fh)}
    for c in data:
        existing[c["name"]] = c
    with open(path, "w") as fh:
        json.dump([existing[k] for k in sorted(existing)], fh, separators=(",", ":"))
    if fbx:
        fbx_folder = os.path.join(folder, "FBX")
        os.makedirs(fbx_folder, exist_ok=True)
        for clip in chosen:
            export_fbx(clip, fbx_folder)
    return path


def export_fbx(clip, folder):
    """One FBX per clip for Studio's Animation Editor (Import > From File). Bones are named after the
    R15 parts; the armature is baked in Blender's Y-up FBX space, in studs, without leaf bones."""
    obj = rig()
    action = bake(clip)
    obj.animation_data.action = action
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start, scene.frame_end = 0, int(round(clip.length * FPS))
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.fbx(
        filepath=os.path.join(folder, clip.name + ".fbx"),
        use_selection=True,
        object_types={"ARMATURE"},
        add_leaf_bones=False,
        primary_bone_axis="Y",
        secondary_bone_axis="X",
        axis_forward="-Z",
        axis_up="Y",
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_ALL",
        bake_anim=True,
        bake_anim_use_all_actions=False,
        bake_anim_use_nla_strips=False,
        bake_anim_force_startend_keying=True,
        bake_anim_simplify_factor=0.0,
        use_armature_deform_only=False,
    )
