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
import mp_stances as S
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


def facing(body):
    """The way a body's hips face (degrees of yaw in the root part's space), and that turn."""
    forward = L.solve(body)["LowerTorso"].to_3x3() @ V(0, 0, -1)
    yaw = math.degrees(math.atan2(-forward.x, -forward.z))
    return yaw, rot(0, yaw, 0)


def placed(body, part, offset, yaw=0.0, pitch=0.0, roll=0.0):
    """A grip frame at `offset` in `part`'s frame (on `body`), aimed in the body's facing frame: yaw turns
    the muzzle to the body's left, pitch lifts it, roll cants the top right. For bodies turned inside
    the root part (the cover bodies) or folded over (low cover)."""
    point = L.solve(body)[part] @ V(*offset)
    turn = facing(body)[1]
    return Matrix.Translation(point) @ (turn @ rot(pitch, yaw, -roll)).to_matrix().to_4x4()


def pole(body, x, y, z):
    """An elbow direction given in the body's facing frame, in the root part's space."""
    return facing(body)[1] @ V(x, y, z)


def by_part(body, part, right, up, forward, yaw=0.0, pitch=0.0, roll=0.0):
    """A grip frame `right`, `up` and `forward` studs from a part's centre, in the body's facing frame and
    aimed in it: on a body folded over its knees a part's own axes point every which way."""
    centre = L.solve(body)[part].translation
    turn = facing(body)[1]
    point = centre + turn @ V(right, up, -forward)
    return Matrix.Translation(point) @ (turn @ rot(pitch, yaw, -roll)).to_matrix().to_4x4()


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


# The two-handed gun carried in the left hand while a one-handed gun is out. Since 2026-11-11 it is held by its
# middle (LoadoutService; mp_lib.carry_grip): the fist round the middle of its length at the handguard's height,
# the gun's length front to back through it, like a bag's handle. Held by its pistol grip it hung from one end like
# a stick, and the carries pushed it into the body: crouched 0.66 into the legs and 0.56 into the torso (pointing
# out to the side), behind high cover 0.7 into the legs, and 0.47 into them running.
# Behind low cover the carry plays on the squat and on the run along the wall, folded nearly flat, so it is a
# compromise: on the squat the fist is by the left knee and the gun tipped up about 30 degrees, butt toward the
# floor, as if resting it; folded on the run the same arm brings it about level. Level on the squat, the gun went
# up to 0.86 into the floor on the run.
# Each carry puts the fist somewhere and points the gun, then puts the arm on it with IK. Found by a scored search
# with every long gun (each hangs from the fist at its own middle) on every body the carry plays over, the arm swing
# AimLayer adds on the run included; checked again by check_carry.
CARRIES = {
    # the fist (in the root part's space; behind cover in the body's facing frame), the gun's yaw (from the way the
    # body faces), pitch and cant, the elbow's way (like the fist)
    "Stand": ((-1.75, -0.88, 0.22), -4.1, -12.0, 19.0, (-0.7, 0.14, 0.23)),
    "Crouch": ((-1.77, 0.22, 0.26), -0.8, -7.3, 25.2, (-0.63, -0.61, 0.22)),
    "High": ((-0.93, -0.14, -1.52), 11.9, -12.0, 5.5, (-0.07, -0.47, 0.96)),
    "Low": ((-1.007, 0.58, -1.577), 4.17, 32.97, 27.49, (-0.732, -0.561, -1.163)),
}


def carried(body, kind, swing=0.0):
    """`body` with its left arm carrying the gun as CARRIES[kind] says, swinging lightly by `swing` (-1 to 1)."""
    (fx, fy, fz), yaw, pitch, roll, elbow = CARRIES[kind]
    turned = kind in ("High", "Low")
    face_yaw, turn = facing(body) if turned else (0.0, rot(0, 0, 0))
    fist = turn @ V(fx, fy + 0.01 * swing, fz + 0.02 * swing)
    gun = gun_frame(tuple(fist), yaw + face_yaw, pitch + 1.5 * swing, roll)
    L.place_hand(body, "Left", L.hand_for_grip(gun @ L.CARRY_TURN.inverted()), turn @ V(*elbow))
    return body


def carry_two_handed(t):
    """Upright bodies (standing, walking, running, sprinting): the arm hangs at the side, bent a little, the gun
    held by its middle beside the thigh, pointing ahead and a little down. The game's aim layer lifts it clear of
    the floor in any other pose (dives, rolls, lying down) and keeps it out of walls."""
    return carried(M.idle_pose(0.0), "Stand", math.sin(TAU * t / 2.6))


def carry_two_handed_low(t):
    """Crouched (crouching, the crouch walk, getting up): the gun beside the left knee, pointing ahead. Made on the
    crouched body."""
    return carried(M.crouch_idle_pose(0.0), "Crouch", math.sin(TAU * t / 2.6))


def carry_two_handed_cover(t):
    """Hidden behind high cover, back to the wall: the gun in front of the left hip, pointing ahead of the body, the
    elbow down by the side, clear of the wall either side and on the run along it."""
    return carried(S.cover_high("Right")(0.0), "High", math.sin(TAU * t / 2.6))


LEGS = ("LeftUpperLeg", "RightUpperLeg", "LeftLowerLeg", "RightLowerLeg", "LeftFoot", "RightFoot")
TRUNK = ("UpperTorso", "LowerTorso")


def _gait_bodies(base, samples=8):
    out = []
    for direction in M.DIRECTIONS.values():
        g = dict(base)
        g["direction"] = direction
        out += [(M.gait(g["cycle"] * i / samples, g), i / samples) for i in range(samples)]
    return out


def carry_bodies(kind):
    """(pose, run phase or None) pairs a carry plays over, and the floor (root part's space)."""
    if kind == "Stand":
        sprint = dict(M.SPRINT)
        bodies = [(M.idle_pose(0.0), None), (M.idle_pose(2.0), None)] + _gait_bodies(M.JOG) + _gait_bodies(M.RUN)
        bodies += [(M.gait(sprint["cycle"] * i / 8, sprint), i / 8) for i in range(8)]
        return bodies, L.FLOOR
    if kind == "Crouch":  # AimLayer swings the carrying arm with the crouch walk's stride too
        return [(M.crouch_idle_pose(0.0), None)] + _gait_bodies(M.CROUCH_WALK), L.FLOOR + 1.8
    height = "Low" if kind == "Low" else "High"
    idle = S.cover_low if kind == "Low" else S.cover_high
    bodies = []
    for side in ("Right", "Left"):
        run, g = S.cover_move(height, side)
        bodies += [(idle(side)(0.0), None)] + [(run(g["cycle"] * i / 8), None) for i in range(8)]
    return bodies, (S.LOW if kind == "Low" else L.FLOOR)


# Carry limits: no deeper into the legs' boxes than this anywhere the carry plays (the default R15's legs are a stud
# thick; the M107 is five studs long), out of the torso, head and floor, behind high cover out of the wall.
CARRY_LEGS = {"Stand": (0.16, 0.18), "Crouch": (0.17, 0.15), "High": (0.07, 0.03), "Low": (0.11, 0.23)}


def check_carry(clip, kind):
    """Self-check with every long gun carried by its middle, on every body the carry plays over (the run's arm swing
    from AimLayer, -12 degrees, included)."""
    bodies, floor = carry_bodies(kind)
    # CoverRules.GAP off the root; behind low cover the test arena's LowWall (3.6 high), the gun may go over it
    height = 3.6 if kind == "Low" else 8.0
    wall = (Matrix.Translation(V(0, floor + height / 2, -1.15 - 1.0)), (100.0, height, 2.0))
    for n, (body, phase) in enumerate(bodies):
        arm = clip.sample((n * 0.37) % clip.length)
        for j in clip.joints:
            body[j] = arm[j]
        if phase is not None:
            body.turn("LeftShoulder", rot(-12.0 * math.cos(TAU * (phase - 0.04)), 0, 0))
        world = L.solve(body)
        legs = [L.part_box(world, p) for p in LEGS]
        trunk = [L.part_box(world, p) for p in TRUNK]
        arms = [L.part_box(world, p) for p in ("LeftUpperArm", "LeftLowerArm", "LeftHand")]
        for gun in L.LONG_GUNS:
            box = L.long_gun_box(world, gun, carried=True)
            where = "%s, body %d, %s" % (clip.name, n, gun)
            limit = CARRY_LEGS[kind][1 if gun == "M107" else 0]
            assert L.deepest([box], legs) < limit, "%s: %.2f in a leg" % (where, L.deepest([box], legs))
            assert L.deepest([box], trunk) < 0.07, "%s: %.2f in the torso" % (where, L.deepest([box], trunk))
            assert L.deepest([box], [L.part_box(world, "Head")]) == 0.0, where + ": in the head"
            assert L.box_lowest(box) > floor + 0.04, "%s: %.2f over the floor" % (where, L.box_lowest(box) - floor)
            if kind in ("High", "Low"):
                assert L.deepest([box] + arms, [wall]) < 0.03, where + ": in the wall"


# Two-handed guns held while crouched (crouching, the crouch walk). The standing low ready made on an upright chest
# pointed into the floor and through the thighs on the crouched one (2026-11-11: the gun up to 0.78 into the legs and
# 1.3 into the floor, the forearms 0.9 into the thighs, the right arm folded into the chest). Made on the crouch idle:
# the gun across the front of the body, muzzle to the front-left and down, both hands on it, the elbows down. Found by
# a search with every gun of the set on the crouch idle and the whole crouch walk, the support hand placed as
# AimLayer places it; checked again by check_low_hold.
LOW_HOLDS = {
    # the grip (root part's space, on the crouch idle), the gun's yaw, pitch and cant, the right elbow's way
    "Rifle": ((0.3, 0.26, -2.03), 68.1, -24.6, 8.4, (1.24, -1.3, -0.43)),
    "Shotgun": ((0.68, 0.43, -1.8), 69.1, -24.3, 11.3, (1.21, -2.16, -1.07)),
    "Sniper": ((0.5, 0.26, -1.84), 63.4, -21.4, 14.2, (1.68, -1.56, -0.17)),
}


def two_handed_hold_low(kind, period=3.4):
    (x, y, z), yaw, pitch, roll, elbow = LOW_HOLDS[kind]

    def pose(t):
        rise, tilt = breathing(t, period)
        body = M.crouch_idle_pose(0.0)
        gun = gun_frame((x, y + rise, z), yaw, pitch + tilt, roll)
        L.place_hand(body, "Right", L.hand_for_grip(gun), V(*elbow))
        L.place_hand(body, "Left", L.hand_for_grip(support_frame(gun, kind)), L.HOLD_POLE)
        return body
    return pose


def check_low_hold(clip, kind):
    """Self-check on the crouch idle and the crouch walk (every direction, 8 points of its cycle) with every gun of
    the set, the support hand placed as AimLayer places it: the gun over the floor and out of the legs and head, the
    forearms and hands out of the head and no deeper in the legs than resting on them, the support hand on the gun."""
    bodies, floor = carry_bodies("Crouch")
    for n, (body, _) in enumerate(bodies):
        arm = clip.sample((n * 0.37) % clip.length)
        for j in clip.joints:
            body[j] = arm[j]
        for gun in L.LONG_SETS[kind]:
            p = body.copy()
            miss = L.place_support(p, gun)
            world = L.solve(p)
            where = "%s, body %d, %s" % (clip.name, n, gun)
            box = L.long_gun_box(world, gun)
            legs = [L.part_box(world, q) for q in LEGS]
            head = [L.part_box(world, "Head")]
            fore = [L.part_box(world, q) for q in ("RightLowerArm", "RightHand", "LeftLowerArm", "LeftHand")]
            # 0.06: the M500's pump is the furthest support point, 1.43 ahead of its grip; at the bottom of a breath on
            # one stride it is 0.05 out of reach
            assert miss < 0.06, "%s: the support hand %.2f off the gun" % (where, miss)
            assert L.box_lowest(box) > floor + 0.05, "%s: %.2f over the floor" % (where, L.box_lowest(box) - floor)
            assert L.deepest([box], legs) < 0.1, "%s: %.2f in a leg" % (where, L.deepest([box], legs))
            assert L.deepest([box] + fore, head) < 0.02, where + ": in the head"
            assert L.deepest(fore, legs) < 0.35, "%s: an arm %.2f in a leg" % (where, L.deepest(fore, legs))


def carry_two_handed_cover_low(t):
    """Behind low cover, squatting with the back to the wall: the fist by the left knee, the gun held by its middle,
    tipped up and pointing out from the wall, its butt toward the floor (CARRIES). Made on the squat."""
    return carried(S.cover_low("Right")(0.0), "Low", 0.4 * math.sin(TAU * t / 2.6))  # squatting, it barely sways


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
    # crouched: the two-handed guns across the front of the body (LOW_HOLDS)
    for kind in ("Rifle", "Shotgun", "Sniper"):
        low = Clip("Hold%sLow" % kind, 3.4, two_handed_hold_low(kind), loop=True, priority="Action", joints=B, drop=1.8, gun=(kind, None))
        check_low_hold(low, kind)
    # the carried gun, held by its middle (CARRIES)
    for name, made, kind, drop in (("CarryTwoHanded", carry_two_handed, "Stand", 0.0), ("CarryTwoHandedLow", carry_two_handed_low, "Crouch", 1.8),
                                   ("CarryTwoHandedCover", carry_two_handed_cover, "High", 0.0),
                                   ("CarryTwoHandedCoverLow", carry_two_handed_cover_low, "Low", 1.8)):
        check_carry(Clip(name, 2.6, made, loop=True, priority="Action", joints=Lt, drop=drop, gun=(None, "Rifle")), kind)
    Clip("InjuredArmLeft", 2.2, injured_arm("Left"), loop=True, priority="Action", joints=Lt)
    Clip("InjuredArmRight", 2.2, injured_arm("Right"), loop=True, priority="Action", joints=R)
    Clip("AimPistol", 3.0, aim_pistol, loop=True, priority="Action2", joints=R, gun=("Pistol", None))
    Clip("AimRifle", 3.4, aim_rifle, loop=True, priority="Action2", joints=B, gun=("Rifle", None))
    Clip("AimDual", 3.0, aim_dual, loop=True, priority="Action2", joints=B, gun=("Pistol", "Pistol"))
