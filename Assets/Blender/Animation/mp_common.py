"""Shared data for the Maximum Pain R15 animation pipeline (rig, clips, export). Run inside Blender.

Conventions: 1 Blender unit = 1 stud. Ground at z = 0. The character faces -Y.
Roblox -> Blender is the proper rotation x -> -x, y -> z, z -> y (so Roblox forward -Z becomes Blender -Y),
plus the HumanoidRootPart height. Poses are authored in Roblox terms (CFrames in HumanoidRootPart space)
and converted here, so exported numbers drop straight into KeyframeSequence Poses.
"""
import math
from mathutils import Matrix, Vector

HERE = __import__("os").path.dirname(__file__)
FPS = 30
HRP_HEIGHT = 3.1924  # default R15 body: HipHeight 2.1924 + half the 2-stud root
C = Matrix(((-1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, HRP_HEIGHT), (0, 0, 0, 1)))

# (part1, part0, C0 position, C1 position) from Players:CreateHumanoidModelFromDescription (R15, default
# description). Every R15 rig attachment has identity rotation, so a joint frame is just a position.
JOINTS = [
    ("LowerTorso", "HumanoidRootPart", (0, -1, 0), (0, -0.2, 0)),
    ("UpperTorso", "LowerTorso", (0, 0.2, 0), (0, -0.849, 0)),
    ("Head", "UpperTorso", (0, 0.849, 0), (0, -0.5758, 0)),
    ("RightUpperArm", "UpperTorso", (0.9716, 0.5975, 0), (-0.5005, 0.4189, 0)),
    ("RightLowerArm", "RightUpperArm", (0, -0.355, 0), (0, 0.2747, 0)),
    ("RightHand", "RightLowerArm", (0, -0.5322, 0), (0, 0.1316, 0)),
    ("LeftUpperArm", "UpperTorso", (-0.9716, 0.5975, 0), (0.5005, 0.4189, 0)),
    ("LeftLowerArm", "LeftUpperArm", (0.0005, -0.3549, 0), (0.0005, 0.2748, 0)),
    ("LeftHand", "LeftLowerArm", (0.0005, -0.5322, 0), (0.0005, 0.1316, 0)),
    ("RightUpperLeg", "LowerTorso", (0.5, -0.2, 0), (0, 0.4714, 0)),
    ("RightLowerLeg", "RightUpperLeg", (0, -0.4492, 0), (0, 0.4134, 0)),
    ("RightFoot", "RightLowerLeg", (0, -0.5965, 0), (0, 0.106, 0)),
    ("LeftUpperLeg", "LowerTorso", (-0.5, -0.2, 0), (0, 0.4714, 0)),
    ("LeftLowerLeg", "LeftUpperLeg", (0, -0.4493, 0), (0, 0.4132, 0)),
    ("LeftFoot", "LeftLowerLeg", (0, -0.5965, 0), (0, 0.106, 0)),
]
SIZES = {
    "HumanoidRootPart": (2, 2, 1), "LowerTorso": (1.9914, 0.4007, 1.004), "UpperTorso": (1.9432, 1.698, 1.004),
    "Head": (1.159, 1.182, 1.1606), "RightUpperArm": (1.0011, 1.2416, 1.0019), "RightLowerArm": (1.0011, 1.1175, 1.0019),
    "RightHand": (0.9843, 0.3158, 1.0283), "LeftUpperArm": (1.0011, 1.2416, 1.0019), "LeftLowerArm": (1.0011, 1.1175, 1.0019),
    "LeftHand": (0.9843, 0.3158, 1.0283), "RightUpperLeg": (0.9928, 1.3629, 0.9727), "RightLowerLeg": (0.9928, 1.3007, 0.9728),
    "RightFoot": (1.0089, 0.312, 1.0011), "LeftUpperLeg": (0.9928, 1.3629, 0.9727), "LeftLowerLeg": (0.9928, 1.3007, 0.9728),
    "LeftFoot": (1.0089, 0.312, 1.0011),
}
PARENT = {p1: p0 for p1, p0, _, _ in JOINTS}
BONES = [p1 for p1, _, _, _ in JOINTS]  # exported joints, parents first
JOINT_POS = {"HumanoidRootPart": Vector((0, 0, 0))}  # joint (C0) position at rest, HRP space
CENTER = {"HumanoidRootPart": Vector((0, 0, 0))}  # part centre at rest, HRP space
C1 = {}
for _p1, _p0, _c0, _c1 in JOINTS:
    JOINT_POS[_p1] = CENTER[_p0] + Vector(_c0)
    CENTER[_p1] = JOINT_POS[_p1] - Vector(_c1)
    C1[_p1] = Vector(_c1)

# 9mm Pistol tool (ReplicatedStorage.Assets.Weapons): R15 holds tools at RightHand.RightGripAttachment, Grip = (0,-0.11,-0.2).
GRIP_ATT = Matrix.Translation((0, -0.1578, 0)) @ Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, 0), (0, 0, 0, 1)))
HANDLE_IN_HAND = GRIP_ATT @ Matrix.Translation((0, -0.11, -0.2)).inverted()  # Handle frame in RightHand space
GUN_PARTS = {  # name: (size, position in Handle space); all axis-aligned. Barrel points along Handle -Z.
    "Frame": ((0.2, 0.7523, 1.3507), (0, 0.0289, -0.4446)), "Slide": ((0.23, 0.2685, 1.366), (0, 0.5283, -0.493)),
    "Barrel": ((0.1, 0.1, 0.93), (0, 0.51, -0.735)), "GripPanels": ((0.245, 0.5276, 0.3699), (0, -0.0165, 0.0151)),
    "Magazine": ((0.22, 0.1346, 0.3266), (0, -0.3268, 0.0937)), "Hammer": ((0.07, 0.1881, 0.1302), (0, 0.5386, 0.2265)),
    "Trigger": ((0.04, 0.1747, 0.088), (0, 0.2247, -0.3863)),
}
MUZZLE = Vector((0, 0.51, -1.231))


def cf(pos=(0, 0, 0), rx=0.0, ry=0.0, rz=0.0):
    """Roblox CFrame.new(pos) * CFrame.Angles(rx, ry, rz), angles in degrees."""
    r = Matrix.Rotation(math.radians(rx), 4, "X") @ Matrix.Rotation(math.radians(ry), 4, "Y") @ Matrix.Rotation(math.radians(rz), 4, "Z")
    return Matrix.Translation(pos) @ r


def look(pos, forward, up=(0, 1, 0)):
    """Frame at pos whose -Z points along forward (Roblox CFrame.lookAt convention)."""
    f = Vector(forward).normalized()
    r = f.cross(Vector(up)).normalized()
    u = r.cross(f)
    m = Matrix.Identity(4)
    for i in range(3):
        m[i][0], m[i][1], m[i][2], m[i][3] = r[i], u[i], -f[i], pos[i]
    return m


def joint_frame(name):
    return Matrix.Translation(JOINT_POS[name])


def wrist_from_gun(gun):
    """Right wrist joint frame (HRP space) that puts the pistol's Handle at `gun`."""
    return gun @ HANDLE_IN_HAND.inverted() @ Matrix.Translation(C1["RightHand"])


def hand_to_wrist(hand_part, side):
    return hand_part @ Matrix.Translation(C1[side + "Hand"])


def bone_q(arm, name):
    """Rest bone frame relative to its Roblox joint frame (rotation only): T = Q P Q^-1."""
    return (C @ joint_frame(name)).inverted() @ arm.data.bones[name].matrix_local
