"""Maximum Pain - arm clips: how each gun is held low and raised, the carried two-handed gun, injured
arms. They key only the arm joints, so they ride on any body clip (idle, run, crouch, cover, dives).

Every pose places the gun first (its grip frame: barrel along -Z, top along +Y, in the root part's
space with the chest upright), then puts the hands on it with arm IK: the right hand on the grip and,
for two-handed guns, the left hand on the gun's own Support point. Rifle aims are made with the chest
bladed 30 degrees (left shoulder forward, as in a real shooting stance - the left hand can't reach the
handguard otherwise); the game's aim layer blades the chest the same way, relative to wherever the
player aims, so the arms land exactly as made here. The aim layer also turns the arms onto the target,
so these poses only have to be right with the gun level and straight ahead.
"""
import math

from mathutils import Matrix

import mp_lib as L
import mp_locomotion as M
from mp_lib import Clip, Pose, V, rot

TAU = 2 * math.pi
RIFLE_BLADE = -30.0  # Waist yaw while a rifle is shouldered (turned right, left shoulder forward)
PISTOL_BLADE = -10.0


def gun_frame(position, yaw=0.0, pitch=0.0, roll=0.0):
    """A gun's grip frame: yaw turns the muzzle left, pitch lifts it, roll cants the top right."""
    return Matrix.Translation(V(*position)) @ rot(pitch, yaw, -roll).to_matrix().to_4x4()


def support_frame(gun, kind, roll=75.0):
    """Where the left hand holds a two-handed gun: at its Support point, wrapped under and round the
    left side of the handguard (rolled about the barrel)."""
    point = gun @ L.gun_support(kind)
    turn = gun.to_quaternion() @ rot(0, 0, roll)
    return Matrix.Translation(point) @ turn.to_matrix().to_4x4()


def arms_pose(waist_yaw=0.0, right=None, left=None, right_elbow=None, left_elbow=None):
    """IK both hands onto gun frames with the chest turned by `waist_yaw` (only the arms are kept)."""
    pose = Pose()
    pose.set("Waist", 0, waist_yaw, 0)
    if right is not None:
        L.place_hand(pose, "Right", L.hand_for_grip(right), right_elbow)
    if left is not None:
        L.place_hand(pose, "Left", L.hand_for_grip(left), left_elbow)
    return pose


def breathing(t, period=3.2, amount=1.0):
    """A slow rise and fall for held poses: (height, pitch) offsets."""
    b = math.sin(TAU * t / period)
    return 0.018 * b * amount, 1.2 * b * amount


# --- Low holds ---------------------------------------------------------------------------------------
def one_handed_hold(position, yaw, pitch, elbow=None, period=3.2):
    def pose(t):
        rise, tilt = breathing(t, period)
        gun = gun_frame((position[0], position[1] + rise, position[2]), yaw, pitch + tilt)
        return arms_pose(0.0, right=gun, right_elbow=elbow)
    return pose


def two_handed_hold(kind, position, yaw, pitch, roll=-10.0, period=3.4):
    def pose(t):
        rise, tilt = breathing(t, period)
        gun = gun_frame((position[0], position[1] + rise, position[2]), yaw, pitch + tilt, roll)
        return arms_pose(0.0, right=gun, left=support_frame(gun, kind), right_elbow=V(1, -0.6, 0.6), left_elbow=V(-1, -0.8, 0.1))
    return pose


def dual_hold(t):
    """A pistol low beside each thigh (the one-handed low ready, mirrored)."""
    rise, tilt = breathing(t, 3.0)
    right = gun_frame((1.14, -0.84 + rise, -0.55), 3.0, -52.0 + tilt, 8.0)
    left = gun_frame((-1.14, -0.84 + rise, -0.55), -3.0, -52.0 + tilt, -8.0)
    return arms_pose(0.0, right=right, left=left, right_elbow=V(0.6, -0.3, 1.0), left_elbow=V(-0.6, -0.3, 1.0))


def carry_two_handed(t):
    """The two-handed gun riding in the left hand while a one-handed gun is out: held by its grip with
    the arm hanging beside the thigh, a little out from it so strafing legs don't cross it, muzzle
    forward and down 28 degrees (clear of the floor running and sprinting), swinging lightly. For
    upright bodies; crouched and hidden behind high cover have their own carries, and the game's aim
    layer lifts the gun clear of the floor in any other pose (dives, rolls, lying down)."""
    swing = math.sin(TAU * t / 2.6)
    gun = gun_frame((-1.55, -0.9 + 0.01 * swing, -0.05 + 0.02 * swing), 4.0, -28.0 + 2.0 * swing, -6.0)
    return arms_pose(0.0, left=gun, left_elbow=V(-0.4, 0.0, 1.0))


def carry_two_handed_low(t):
    """The carried gun while crouched (crouching, low cover, getting up). Made on the crouched body:
    the hunched chest would point the standing carry straight into the floor. Held at the left side,
    muzzle out to the left and a little forward, level, so it clears the floor and a low wall ahead."""
    swing = math.sin(TAU * t / 2.6)
    body = M.crouch_idle_pose(0.0)
    gun = gun_frame((-1.55, 0.05 + 0.01 * swing, 0.15), 70.0, -10.0 + 1.5 * swing, -30.0)
    L.place_hand(body, "Left", L.hand_for_grip(gun), V(-0.6, 0.0, 0.8))
    return body


def carry_two_handed_cover(t):
    """The carried gun hidden behind high cover: nearly straight down beside the left leg and turned
    out a little, clear of the wall the character faces (the standing carry pointed into it)."""
    swing = math.sin(TAU * t / 2.6)
    gun = gun_frame((-1.3, -0.6 + 0.01 * swing, 0.4), 60.0, -80.0 + 1.5 * swing, -6.0)
    return arms_pose(0.0, left=gun, left_elbow=V(-0.5, 0.0, 1.0))


def injured_arm(side):
    """An arm in the red hangs, shoulder dropped, swinging slack."""
    sign = 1 if side == "Right" else -1

    def pose(t):
        sway = math.sin(TAU * t / 2.2)
        p = Pose()
        p.set(side + "Shoulder", -6.0 + 4.0 * sway, 0, sign * -3.0)
        p.set(side + "Elbow", 12.0 + 3.0 * sway, 0, 0)
        p.set(side + "Wrist", -10.0, sign * 6.0, 0)
        return p
    return pose


# --- Aims --------------------------------------------------------------------------------------------
def aim_pistol(t):
    """One-handed, arm out at the target, Max Payne 3 style; the other hand stays free (or on the
    carried rifle)."""
    rise, tilt = breathing(t, 3.0, 0.4)
    gun = gun_frame((0.42, 0.98 + rise, -1.86), 0.0, tilt)
    return arms_pose(PISTOL_BLADE, right=gun, right_elbow=V(0.7, -1.0, 0.2))


def aim_rifle(t):
    """Shouldered: stock in the right shoulder, cheek down to the sights, left hand on the support."""
    rise, tilt = breathing(t, 3.4, 0.4)
    gun = gun_frame((0.4, 0.98 + rise, -0.86), 0.0, tilt, 0.0)
    return arms_pose(RIFLE_BLADE, right=gun, left=support_frame(gun, "Rifle", 80.0), right_elbow=V(1, -0.5, 0.4), left_elbow=V(-0.4, -1, 0.1))


def aim_dual(t):
    """Both arms out, each gun on the target, canted slightly outward."""
    rise, tilt = breathing(t, 3.0, 0.4)
    right = gun_frame((0.62, 0.98 + rise, -1.9), 2.0, tilt, 14.0)
    left = gun_frame((-0.62, 0.98 + rise, -1.9), -2.0, tilt, -14.0)
    return arms_pose(0.0, right=right, left=left, right_elbow=V(0.8, -1, 0.1), left_elbow=V(-0.8, -1, 0.1))


def register():
    R, Lt, B = L.RIGHT_ARM, L.LEFT_ARM, L.ARMS
    # Low ready beside the thigh (not across the belly), elbow relaxed, muzzle forward and down.
    LOW_ELBOW = V(0.6, -0.3, 1.0)
    Clip("HoldPistol", 3.2, one_handed_hold((1.14, -0.84, -0.55), 3.0, -52.0, LOW_ELBOW), loop=True, priority="Action", joints=R, gun=("Pistol", None))
    Clip("HoldRevolver", 3.2, one_handed_hold((1.12, -0.8, -0.58), 4.0, -48.0, LOW_ELBOW), loop=True, priority="Action", joints=R, gun=("Revolver", None))
    # Short guns ride at the hip, pointing ahead and down, the hand out over the right hip.
    Clip("HoldSMG", 3.2, one_handed_hold((1.06, -0.42, -0.8), 6.0, -24.0, LOW_ELBOW), loop=True, priority="Action", joints=R, gun=("SMG", None))
    Clip("HoldSawnOff", 3.2, one_handed_hold((1.08, -0.5, -0.76), 4.0, -30.0, LOW_ELBOW), loop=True, priority="Action", joints=R, gun=("SawnOff", None))
    # Low ready, found by search so both hands reach with the left elbow relaxed (about 50 degrees).
    # Searched so both hands reach with natural elbows (right about 100 degrees, left about 45).
    Clip("HoldRifle", 3.4, two_handed_hold("Rifle", (0.45, -0.3, -0.2), 40.0, -15.0), loop=True, priority="Action", joints=B, gun=("Rifle", None))
    Clip("HoldShotgun", 3.4, two_handed_hold("Shotgun", (0.3, -0.3, -0.1), 55.0, -10.0), loop=True, priority="Action", joints=B, gun=("Shotgun", None))
    Clip("HoldSniper", 3.6, two_handed_hold("Sniper", (0.45, -0.45, -0.2), 40.0, -15.0), loop=True, priority="Action", joints=B, gun=("Sniper", None))
    Clip("HoldDual", 3.0, dual_hold, loop=True, priority="Action", joints=B, gun=("Pistol", "Pistol"))
    Clip("CarryTwoHanded", 2.6, carry_two_handed, loop=True, priority="Action", joints=Lt, gun=(None, "Rifle"))
    Clip("CarryTwoHandedLow", 2.6, carry_two_handed_low, loop=True, priority="Action", joints=Lt, drop=1.8, gun=(None, "Rifle"))
    Clip("CarryTwoHandedCover", 2.6, carry_two_handed_cover, loop=True, priority="Action", joints=Lt, gun=(None, "Rifle"))
    Clip("InjuredArmLeft", 2.2, injured_arm("Left"), loop=True, priority="Action", joints=Lt)
    Clip("InjuredArmRight", 2.2, injured_arm("Right"), loop=True, priority="Action", joints=R)
    Clip("AimPistol", 3.0, aim_pistol, loop=True, priority="Action2", joints=R, gun=("Pistol", None))
    Clip("AimRifle", 3.4, aim_rifle, loop=True, priority="Action2", joints=B, gun=("Rifle", None))
    Clip("AimDual", 3.0, aim_dual, loop=True, priority="Action2", joints=B, gun=("Pistol", "Pistol"))
