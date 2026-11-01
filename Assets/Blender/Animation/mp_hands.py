"""Maximum Pain - arm actions: holds while hidden in cover, blind fire, draws, picking up, painkillers,
dropping a gun, and the reloads. They key only the arms (pickup and painkiller also bend the waist or
tilt the head), so they ride on any body clip.

Guns are placed first (grip frames, as in mp_arms), then the hands put on them with arm IK. Reload
markers move the gun's parts in the game (AnimationController.MARKERS): the server's timer, not a
marker, decides when the ammo arrives, and the clip is stretched to that timer.
"""
from mathutils import Matrix

import mp_arms as A
import mp_lib as L
import mp_stances as S
from mp_lib import Clip, Keys, Pose, V, rot

LOW_READY = ((1.14, -0.84, -0.55), 3.0, -52.0)  # mp_arms HoldPistol
HOLD_POLE = V(-1, -0.8, 0.1)  # the left elbow on a two-handed gun (AimLayer.HOLD_POLE)
RIGHT_LOW = V(0.6, -0.3, 1.0)


def gun(position, yaw=0.0, pitch=0.0, roll=0.0):
    return A.gun_frame(position, yaw, pitch, roll)


def on(gun_frame, offset, pitch=0.0, yaw=0.0, roll=0.0):
    """A frame on a gun (in its grip space): where a hand holds a magazine to it, racks its slide."""
    return gun_frame @ Matrix.Translation(V(*offset)) @ rot(pitch, yaw, roll).to_matrix().to_4x4()


def hand_at(position, pitch=0.0, yaw=0.0, roll=0.0):
    return Matrix.Translation(V(*position)) @ rot(pitch, yaw, roll).to_matrix().to_4x4()


def arms(right=None, left=None, left_hand=None, right_elbow=None, left_elbow=None, body=None):
    """Hands onto guns (grip frames) or a left hand at a frame of its own, with arm IK on `body`'s
    torso (the upright rest torso if none)."""
    p = body.copy() if body is not None else Pose()
    if right is not None:
        L.place_hand(p, "Right", L.hand_for_grip(right), right_elbow)
    if left is not None:
        L.place_hand(p, "Left", L.hand_for_grip(left), left_elbow)
    elif left_hand is not None:
        L.place_hand(p, "Left", left_hand, left_elbow)
    return p


def relaxed_left(p, shoulder=8.0, elbow=20.0):
    p.set("LeftShoulder", shoulder, 0, -6.0)
    p.set("LeftElbow", elbow, 0, 0)
    p.set("LeftWrist", -4.0, 0, 0)
    return p


def keyed(entries, loop_length=None):
    keys = Keys(loop_length)
    for t, pose in entries:
        keys.add(t, pose)
    return keys.at


# --- Hidden in cover --------------------------------------------------------------------------------
def cover_hold_high(kind):
    """Behind high cover: the gun up close to the chest, muzzle up (clear of the wall)."""
    def pose(t):
        rise, tilt = A.breathing(t, 3.0, 0.6)
        right = gun((0.62, 0.55 + rise, -0.72), 12.0, 62.0 + tilt, 0.0)
        if kind == "One":
            return relaxed_left(arms(right=right, right_elbow=V(0.5, -1, 0.3)), 30.0, 70.0)
        if kind == "Dual":
            left = gun((-0.62, 0.55 + rise, -0.72), -12.0, 62.0 + tilt, 0.0)
            return arms(right=right, left=left, right_elbow=V(0.5, -1, 0.3), left_elbow=V(-0.5, -1, 0.3))
        rifle = gun((0.5, 0.0 + rise, -0.62), 18.0, 58.0 + tilt, -20.0)  # port arms, muzzle up and left
        return arms(right=rifle, left=A.support_frame(rifle, "Rifle"), right_elbow=V(1, -0.6, 0.6), left_elbow=HOLD_POLE)
    return pose


def low_cover_body(side=None):
    """The low cover idle at rest; side-neutral (squared to the wall) without a side."""
    body = S.cover_low(side or "Right")(0.0)
    if side is None:
        body.set("Root", -32.0, 0, 0, move=(0, 0.7, 0.15))
        body.set("Waist", -46.0, 0, 0)
    return body


def cover_hold_low(kind, side=None):
    """Behind low cover the body is hunched right up to the wall, its chest folded onto its thighs, so
    the gun is held low (as in Max Payne 3): a pistol beside the right knee, muzzle down at the floor
    ahead; two pistols beside both knees; a rifle low across the front by the feet, muzzle along the
    wall. The rifle is long enough to reach the wall when the body turns toward the side worked, so
    it has a clip per side, made on that side's body."""
    def pose(t):
        rise, tilt = A.breathing(t, 3.0, 0.6)
        if kind == "Two":
            x, y, z, yaw = (0.8, -0.7, -1.0, 75.0) if side == "Right" else (0.4, -0.7, -0.8, 90.0)
            rifle = gun((x, y + rise, z), yaw, tilt, 0.0)
            return arms(right=rifle, left=A.support_frame(rifle, "Rifle"), right_elbow=V(0.6, 0.3, 0.6), left_elbow=V(-0.6, 0.3, 0.6), body=low_cover_body(side))
        right = gun((1.45, -0.45 + rise, -0.8), 15.0, -60.0 + tilt, 0.0)
        if kind == "One":
            return arms(right=right, right_elbow=V(0.3, -0.4, 0.5), body=low_cover_body())
        left = gun((-1.45, -0.45 + rise, -0.8), -15.0, -60.0 + tilt, 0.0)
        return arms(right=right, left=left, right_elbow=V(0.3, -0.4, 0.5), left_elbow=V(-0.3, -0.4, 0.5), body=low_cover_body())
    return pose


# --- Blind fire: the gun over or round the cover, the body kept behind it ----------------------------
def blind_fire(kind):
    """BlindFireLow{Right,Left}: the chest straightens and squares up to the wall (keyed at the waist)
    as far as keeps the head under a 3.6-stud top, and the gun arm reaches up to the top edge, the gun
    level over it. That is as high as an R15 arm reaches from the crouch, so on taller low cover the
    shots go into the wall. One clip per side: the crouched body turns toward the side worked.
    BlindFireHigh{Right,Left}: the gun arm out round the edge being worked, the gun pointing past the
    wall. Only the gun arm (and for low cover the waist) is keyed: the other hand stays with the body or
    a carried gun, and a two-handed gun gets its support hand from the game's aim layer."""
    s = 1.0 if kind.endswith("Right") else -1.0
    if kind.startswith("Low"):
        body = S.cover_low("Right" if s > 0 else "Left")(0.0)
        body.set("Waist", -28.0, s * 18.0, 0)
        x, y = (1.0, 2.25) if s > 0 else (0.4, 2.45)

        def pose(t):
            jolt = 0.04 * A.breathing(t, 0.5, 1.0)[0] / 0.018
            return arms(right=gun((x, y + jolt, -1.8), 0.0, -2.0, 0.0), right_elbow=V(1, 0, 0.5), body=body)
        return pose
    body = S.cover_high("Right" if s > 0 else "Left")(0.0)

    def pose(t):
        jolt = 0.04 * A.breathing(t, 0.5, 1.0)[0] / 0.018
        right = gun((s * 1.85 if s > 0 else -1.75, 0.55 + jolt, -0.75), -s * 8.0, 0.0, 0.0)
        return arms(right=right, right_elbow=V(s * 0.3, -1, 0.5), body=body)
    return pose


# --- Draws (stretched to the gun's DrawTime) ----------------------------------------------------------
def draw_one(t):
    """From the thigh holster (muzzle down) up and out, then down into the low ready."""
    holster = gun((1.06, -1.3, 0.08), 0.0, -88.0, 0.0)
    present = gun((1.0, -0.35, -0.8), 4.0, -12.0, 0.0)
    ready = gun(*LOW_READY)
    return keyed([
        (0.0, relaxed_left(arms(right=holster, right_elbow=V(0.8, 0, 1)))),
        (0.17, relaxed_left(arms(right=present, right_elbow=RIGHT_LOW))),
        (0.3, relaxed_left(arms(right=ready, right_elbow=RIGHT_LOW))),
    ])(t)


def draw_dual(t):
    holster_r, holster_l = gun((1.06, -1.3, 0.08), 0.0, -88.0, 0.0), gun((-1.06, -1.3, 0.08), 0.0, -88.0, 0.0)
    present_r, present_l = gun((1.0, -0.35, -0.8), 4.0, -12.0, 8.0), gun((-1.0, -0.35, -0.8), -4.0, -12.0, -8.0)
    ready_r, ready_l = gun((1.14, -0.84, -0.55), 3.0, -52.0, 8.0), gun((-1.14, -0.84, -0.55), -3.0, -52.0, -8.0)
    left_elbow = V(-0.6, -0.3, 1.0)
    return keyed([
        (0.0, arms(right=holster_r, left=holster_l, right_elbow=V(0.8, 0, 1), left_elbow=V(-0.8, 0, 1))),
        (0.17, arms(right=present_r, left=present_l, right_elbow=RIGHT_LOW, left_elbow=left_elbow)),
        (0.3, arms(right=ready_r, left=ready_l, right_elbow=RIGHT_LOW, left_elbow=left_elbow)),
    ])(t)


def draw_two(t):
    """The two-handed gun comes over from the left side (where it was carried) into the right hand,
    swings up across the chest, the left hand catches the handguard, and down into the low ready."""
    carried = gun((-1.05, -0.95, -0.2), 4.0, -40.0, -6.0)
    port = gun((0.35, -0.05, -0.75), 30.0, 35.0, -20.0)
    ready = gun((0.45, -0.3, -0.2), 40.0, -15.0, -10.0)
    return keyed([
        (0.0, relaxed_left(arms(right=carried, right_elbow=V(0.6, -0.5, 1)), 10.0, 30.0)),
        (0.25, arms(right=port, left=A.support_frame(port, "Rifle"), right_elbow=V(1, -0.6, 0.6), left_elbow=HOLD_POLE)),
        (0.55, arms(right=ready, left=A.support_frame(ready, "Rifle"), right_elbow=V(1, -0.6, 0.6), left_elbow=HOLD_POLE)),
    ])(t)


# --- Pickup, painkiller, dropping a gun -------------------------------------------------------------
def pickup(t):
    """Picking a gun up (0.45 s): a quick bend at the waist, the free left hand scooping it off the
    floor in front, and back up."""
    def at(bend, reach):
        p = Pose()
        p.set("Waist", -bend, 6.0 * reach, 0)
        p.set("LeftShoulder", 20.0 + 55.0 * reach, 0, -10.0)
        p.set("LeftElbow", 30.0 - 22.0 * reach, 0, 0)
        p.set("LeftWrist", -10.0 - 20.0 * reach, 0, 0)
        return p
    return keyed([(0.0, at(0, 0)), (0.2, at(38.0, 1.0)), (0.45, at(0, 0))])(t)


def painkiller(t):
    """Painkillers (0.9 s): the left hand brings the bottle to the mouth, the head tips back to
    swallow, and the hand drops away."""
    rest = relaxed_left(Pose())
    rest.set("Neck", 0, 0, 0)
    mouth = Pose()
    L.place_hand(mouth, "Left", hand_at((-0.15, 1.35, -0.85), 70.0, -40.0, 0.0), V(-1, -1, 0.2))
    mouth.set("Neck", 6.0, 0, 0)
    swallow = mouth.copy()
    swallow.set("Neck", 26.0, 0, 0)
    L.place_hand(swallow, "Left", hand_at((-0.1, 1.55, -0.75), 100.0, -40.0, 0.0), V(-1, -1, 0.2))
    return keyed([(0.0, rest), (0.3, mouth), (0.5, swallow), (0.7, mouth), (0.9, rest)])(t)


def drop_gun(t):
    """Dropping the gun in the right hand (0.35 s): a flick out to the side and down, hand open."""
    ready = gun(*LOW_READY)
    flick = gun((1.45, -0.55, -0.45), -30.0, -20.0, 30.0)
    p0 = arms(right=ready, right_elbow=RIGHT_LOW)
    p1 = arms(right=flick, right_elbow=V(1, 0, 0.5))
    p2 = Pose()
    p2.set("RightShoulder", 6.0, 0, 8.0)
    p2.set("RightElbow", 18.0, 0, 0)
    p2.set("RightWrist", -20.0, 0, 0)
    return keyed([(0.0, p0), (0.14, p1), (0.35, p2)])(t)


# --- Reloads -----------------------------------------------------------------------------------------
def reload_pistol():
    """Magazine pistols and the Uzi (1.6 s): tip the gun in, the magazine drops, the left hand fetches
    one from the belt, slaps it home and racks the slide."""
    ready = gun(*LOW_READY)
    work = gun((0.3, 0.1, -1.0), 28.0, 20.0, 38.0)  # in front of the chest, mag well turned to the left hand
    well = on(work, (0.0, -0.5, 0.05), 0.0, 0.0, 0.0)
    slide = on(work, (0.0, 0.2, 0.15), -90.0, 0.0, 0.0)
    racked = on(work, (0.0, 0.2, 0.45), -90.0, 0.0, 0.0)  # slide pulled back
    belt = hand_at((-0.85, -0.75, -0.2), 0.0)
    keys = [
        (0.0, relaxed_left(arms(right=ready, right_elbow=RIGHT_LOW))),
        (0.18, relaxed_left(arms(right=work, right_elbow=V(1, -1, 0.3)), 14.0, 40.0)),
        (0.48, arms(right=work, left_hand=belt, right_elbow=V(1, -1, 0.3), left_elbow=V(-1, 0, 0.6))),
        (0.76, arms(right=work, left=well, right_elbow=V(1, -1, 0.3), left_elbow=V(-1, -1, 0.2))),
        (0.92, arms(right=work, left_hand=slide, right_elbow=V(1, -1, 0.3), left_elbow=V(-1, -0.5, 0.2))),
        (1.04, arms(right=work, left_hand=racked, right_elbow=V(1, -1, 0.3), left_elbow=V(-1, -0.5, 0.2))),
        (1.3, relaxed_left(arms(right=gun((0.9, -0.5, -0.8), 10.0, -25.0, 10.0), right_elbow=RIGHT_LOW), 14.0, 40.0)),
        (1.6, relaxed_left(arms(right=ready, right_elbow=RIGHT_LOW))),
    ]
    markers = [(0.2, "MagOut", ""), (0.5, "MagGrab", ""), (0.78, "MagIn", ""), (0.95, "BoltBack", ""), (1.05, "BoltForward", "")]
    return keyed(keys), markers


def reload_revolver():
    """The revolver (3 s): swing the cylinder out, muzzle up to dump the empties, a speedloader from
    the pocket, cylinder in with a flick of the wrist."""
    ready = gun(*LOW_READY)
    side = gun((0.3, 0.15, -1.0), 30.0, 10.0, 80.0)  # rolled onto its side, cylinder toward the left hand
    dump = gun((0.25, 0.35, -0.9), 20.0, 70.0, 80.0)  # muzzle up, empties fall out
    load = gun((0.25, 0.0, -0.95), 20.0, -45.0, 80.0)  # muzzle down to take the speedloader
    cylinder = lambda g: on(g, (0.0, 0.0, -0.25), 0.0, 0.0, 0.0)
    pocket = hand_at((-0.8, -0.8, 0.0), 0.0)
    keys = [
        (0.0, relaxed_left(arms(right=ready, right_elbow=RIGHT_LOW))),
        (0.3, arms(right=side, left=cylinder(side), right_elbow=V(1, -1, 0.3), left_elbow=V(-1, -1, 0.2))),
        (0.7, arms(right=dump, left=cylinder(dump), right_elbow=V(1, -1, 0.3), left_elbow=V(-1, -1, 0.2))),
        (1.0, arms(right=load, left_hand=hand_at((-0.4, -0.2, -0.6)), right_elbow=V(1, -1, 0.3), left_elbow=V(-1, 0, 0.6))),
        (1.4, arms(right=load, left_hand=pocket, right_elbow=V(1, -1, 0.3), left_elbow=V(-1, 0, 0.6))),
        (1.95, arms(right=load, left=on(load, (0.0, 0.1, -0.2), 180.0, 0.0, 0.0), right_elbow=V(1, -1, 0.3), left_elbow=V(-1, -1, 0.2))),
        (2.35, relaxed_left(arms(right=side, right_elbow=V(1, -1, 0.3)), 14.0, 40.0)),
        (3.0, relaxed_left(arms(right=ready, right_elbow=RIGHT_LOW))),
    ]
    markers = [(0.3, "CylinderOut", ""), (1.4, "MagGrab", ""), (2.35, "CylinderIn", "")]
    return keyed(keys), markers


def rifle_like(length, kind, bolt=True):
    """Magazine rifles, the semi-auto shotgun, the MP5 and the sniper rifle: the gun canted at the low
    ready, the left hand strips the magazine and drops it, fetches a fresh one from the vest, rocks it
    in, then reaches over and works the charging handle."""
    ready = gun((0.45, -0.3, -0.2), 40.0, -15.0, -10.0)
    work = gun((0.4, -0.2, -0.45), 32.0, 5.0, -35.0)  # canted, mag well toward the left hand
    well = (0.0, -0.45, -0.5) if kind != "Sniper" else (0.0, -0.3, -0.6)
    mag = lambda g, drop=0.0: on(g, (well[0], well[1] - drop, well[2]), 0.0, 0.0, 0.0)
    handle = on(work, (0.14, 0.12, -0.75), 0.0, 0.0, 90.0)
    vest = hand_at((-0.5, -0.35, -0.75), 20.0)
    support = A.support_frame(ready, "Rifle")
    t = lambda share: round(share * length, 4)
    keys = [
        (0.0, arms(right=ready, left=support, right_elbow=V(1, -0.6, 0.6), left_elbow=HOLD_POLE)),
        (t(0.1), arms(right=work, left=mag(work), right_elbow=V(1, -0.6, 0.6), left_elbow=V(-1, -1, 0.1))),
        (t(0.18), arms(right=work, left=mag(work, 0.35), right_elbow=V(1, -0.6, 0.6), left_elbow=V(-1, -1, 0.1))),
        (t(0.38), arms(right=work, left_hand=vest, right_elbow=V(1, -0.6, 0.6), left_elbow=V(-1, -0.4, 0.4))),
        (t(0.56), arms(right=work, left=mag(work, 0.25), right_elbow=V(1, -0.6, 0.6), left_elbow=V(-1, -1, 0.1))),
        (t(0.62), arms(right=work, left=mag(work), right_elbow=V(1, -0.6, 0.6), left_elbow=V(-1, -1, 0.1))),
    ]
    markers = [(t(0.16), "MagOut", ""), (t(0.38), "MagGrab", ""), (t(0.62), "MagIn", "")]
    if bolt:
        keys += [
            (t(0.74), arms(right=work, left_hand=handle, right_elbow=V(1, -0.6, 0.6), left_elbow=V(-0.6, 0.2, 0.6))),
            (t(0.79), arms(right=work, left_hand=handle @ Matrix.Translation(V(0, 0, 0.3)), right_elbow=V(1, -0.6, 0.6), left_elbow=V(-0.6, 0.2, 0.6))),
        ]
        markers += [(t(0.77), "BoltBack", ""), (t(0.8), "BoltForward", "")]
    keys += [(length, arms(right=ready, left=support, right_elbow=V(1, -0.6, 0.6), left_elbow=HOLD_POLE))]
    return keyed(keys), markers


def reload_pump():
    """The pump shotgun (3 s): rolled onto its side, the left hand feeds five shells from the belt into
    the loading port one by one, then back to the pump and racks it."""
    ready = gun((0.3, -0.3, -0.1), 55.0, -10.0, -10.0)
    work = gun((0.35, -0.25, -0.4), 35.0, 0.0, -70.0)  # rolled, the loading port toward the left hand
    port = on(work, (0.0, -0.3, -0.55), 0.0, 0.0, 0.0)
    belt = hand_at((-0.6, -0.55, -0.45), 10.0)
    support = A.support_frame(ready, "Shotgun")
    keys = [(0.0, arms(right=ready, left=support, right_elbow=V(1, -0.6, 0.6), left_elbow=HOLD_POLE))]
    markers = []
    start = 0.3
    for i in range(5):
        a = start + i * 0.4
        keys.append((round(a, 3), arms(right=work, left_hand=belt, right_elbow=V(1, -0.6, 0.6), left_elbow=V(-1, -0.3, 0.4))))
        keys.append((round(a + 0.22, 3), arms(right=work, left=port, right_elbow=V(1, -0.6, 0.6), left_elbow=V(-1, -1, 0.1))))
        markers.append((round(a + 0.24, 3), "ShellIn", str(i + 1)))
    pumped = A.support_frame(ready, "Shotgun") @ Matrix.Translation(V(0, 0, 0.3))
    keys += [
        (2.5, arms(right=ready, left=support, right_elbow=V(1, -0.6, 0.6), left_elbow=HOLD_POLE)),
        (2.62, arms(right=ready, left=pumped, right_elbow=V(1, -0.6, 0.6), left_elbow=HOLD_POLE)),
        (3.0, arms(right=ready, left=support, right_elbow=V(1, -0.6, 0.6), left_elbow=HOLD_POLE)),
    ]
    markers.append((2.62, "Pump", ""))
    return keyed(keys), markers


def reload_sawn_off():
    """The sawn-off (2.4 s): break it open, tip the empties out, two shells from the pocket, snap it
    shut with a flick."""
    ready = gun((1.08, -0.5, -0.76), 4.0, -30.0, 0.0)
    open_ = gun((0.4, -0.05, -0.95), 25.0, 15.0, 0.0)
    tipped = gun((0.4, 0.2, -0.85), 25.0, 60.0, 0.0)
    breech = on(open_, (0.0, 0.15, -0.2), 0.0, 0.0, 0.0)
    pocket = hand_at((-0.8, -0.8, 0.0))
    keys = [
        (0.0, relaxed_left(arms(right=ready, right_elbow=RIGHT_LOW))),
        (0.25, relaxed_left(arms(right=open_, right_elbow=V(1, -1, 0.3)), 14.0, 40.0)),
        (0.6, relaxed_left(arms(right=tipped, right_elbow=V(1, -1, 0.3)), 14.0, 40.0)),
        (1.05, arms(right=open_, left_hand=pocket, right_elbow=V(1, -1, 0.3), left_elbow=V(-1, 0, 0.6))),
        (1.35, arms(right=open_, left=breech, right_elbow=V(1, -1, 0.3), left_elbow=V(-1, -1, 0.2))),
        (1.6, arms(right=open_, left=breech @ Matrix.Translation(V(0.05, 0, 0)), right_elbow=V(1, -1, 0.3), left_elbow=V(-1, -1, 0.2))),
        (1.9, relaxed_left(arms(right=gun((0.6, 0.1, -1.0), 10.0, 10.0, 0.0), right_elbow=V(1, -1, 0.3)), 14.0, 40.0)),
        (2.4, relaxed_left(arms(right=ready, right_elbow=RIGHT_LOW))),
    ]
    markers = [(0.25, "BreakOpen", ""), (1.05, "MagGrab", ""), (1.35, "ShellIn", "1"), (1.6, "ShellIn", "2"), (1.9, "BreakClose", "")]
    return keyed(keys), markers


def reload_dual():
    """Two pistols (2.4 s): both tip in and the magazines drop, the guns come down to the hips where
    fresh magazines are slapped in against the belt, then both slides are racked with a flick."""
    ready_r, ready_l = gun((1.14, -0.84, -0.55), 3.0, -52.0, 8.0), gun((-1.14, -0.84, -0.55), -3.0, -52.0, -8.0)
    tip_r, tip_l = gun((0.55, 0.05, -0.95), 20.0, 15.0, 35.0), gun((-0.55, 0.05, -0.95), -20.0, 15.0, -35.0)
    hip_r, hip_l = gun((0.95, -0.6, -0.35), 0.0, -80.0, 0.0), gun((-0.95, -0.6, -0.35), 0.0, -80.0, 0.0)
    flick_r, flick_l = gun((0.8, 0.0, -0.9), 6.0, 25.0, 8.0), gun((-0.8, 0.0, -0.9), -6.0, 25.0, -8.0)
    re, le = V(1, -1, 0.3), V(-1, -1, 0.3)
    keys = [
        (0.0, arms(right=ready_r, left=ready_l, right_elbow=RIGHT_LOW, left_elbow=V(-0.6, -0.3, 1.0))),
        (0.25, arms(right=tip_r, left=tip_l, right_elbow=re, left_elbow=le)),
        (0.9, arms(right=hip_r, left=hip_l, right_elbow=V(1, 0, 0.6), left_elbow=V(-1, 0, 0.6))),
        (1.35, arms(right=hip_r @ Matrix.Translation(V(0, 0.1, 0)), left=hip_l @ Matrix.Translation(V(0, 0.1, 0)), right_elbow=V(1, 0, 0.6), left_elbow=V(-1, 0, 0.6))),
        (1.75, arms(right=flick_r, left=flick_l, right_elbow=re, left_elbow=le)),
        (2.4, arms(right=ready_r, left=ready_l, right_elbow=RIGHT_LOW, left_elbow=V(-0.6, -0.3, 1.0))),
    ]
    markers = [(0.25, "MagOut", ""), (0.9, "MagGrab", ""), (1.35, "MagIn", ""), (1.7, "BoltBack", ""), (1.8, "BoltForward", "")]
    return keyed(keys), markers


def register():
    R, Lt, B = L.RIGHT_ARM, L.LEFT_ARM, L.ARMS
    # the free left hand stays with the body clip, or with a carried two-handed gun (CarryTwoHanded)
    Clip("CoverHoldHighOne", 3.0, cover_hold_high("One"), loop=True, priority="Action", joints=R, gun=("Pistol", None))
    Clip("CoverHoldHighTwo", 3.0, cover_hold_high("Two"), loop=True, priority="Action", joints=B, gun=("Rifle", None))
    Clip("CoverHoldHighDual", 3.0, cover_hold_high("Dual"), loop=True, priority="Action", joints=B, gun=("Pistol", "Pistol"))
    Clip("CoverHoldLowOne", 3.0, cover_hold_low("One"), loop=True, priority="Action", joints=R, drop=1.8, gun=("Pistol", None))
    Clip("CoverHoldLowDual", 3.0, cover_hold_low("Dual"), loop=True, priority="Action", joints=B, drop=1.8, gun=("Pistol", "Pistol"))
    for side in ("Right", "Left"):
        Clip("CoverHoldLowTwo" + side, 3.0, cover_hold_low("Two", side), loop=True, priority="Action", joints=B, drop=1.8, gun=("Rifle", None))
        Clip("BlindFireLow" + side, 0.5, blind_fire("Low" + side), loop=True, priority="Action2", joints=R | {"Waist"}, drop=1.8, gun=("Pistol", None))
        Clip("BlindFireHigh" + side, 0.5, blind_fire("High" + side), loop=True, priority="Action2", joints=R, gun=("Pistol", None))
    Clip("DrawOneHanded", 0.3, draw_one, priority="Action3", joints=R, gun=("Pistol", None))
    Clip("DrawDual", 0.3, draw_dual, priority="Action3", joints=B, gun=("Pistol", "Pistol"))
    Clip("DrawTwoHanded", 0.55, draw_two, priority="Action3", joints=B, gun=("Rifle", None))
    Clip("Pickup", 0.45, pickup, priority="Action3", joints=Lt | {"Waist"})
    Clip("Painkiller", 0.9, painkiller, priority="Action3", joints=Lt | {"Neck"})
    Clip("DropGun", 0.35, drop_gun, priority="Action3", joints=R)
    for name, length, made, joints, gun_id in (
        ("ReloadPistol", 1.6, reload_pistol(), B, "Pistol"),
        ("ReloadRevolver", 3.0, reload_revolver(), B, "Revolver"),
        ("ReloadRifle", 2.5, rifle_like(2.5, "Rifle"), B, "Rifle"),
        ("ReloadSniper", 3.5, rifle_like(3.5, "Sniper"), B, "Sniper"),
        ("ReloadPump", 3.0, reload_pump(), B, "Shotgun"),
        ("ReloadSawnOff", 2.4, reload_sawn_off(), B, "SawnOff"),
        ("ReloadDual", 2.4, reload_dual(), B, "Pistol"),
    ):
        pose, markers = made
        Clip(name, length, pose, priority="Action3", joints=joints, markers=markers, gun=(gun_id, "Pistol" if name == "ReloadDual" else None))
