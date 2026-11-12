"""Maximum Pain - arm actions: holds while hidden in cover, blind fire (still and on the cover runs, and with a
two-handed gun behind high cover), draws, picking up, painkillers, dropping a gun, and the reloads. They key
only the arms (blind fire also turns the waist and neck, pickup bends the waist, painkiller tilts the head), so
they ride on any body clip.

Guns are placed first (grip frames, as in mp_arms), then the hands put on them with arm IK. Reload
markers move the gun's parts in the game (AnimationController.MARKERS): the server's timer, not a
marker, decides when the ammo arrives, and the clip is stretched to that timer.
"""
import math

from mathutils import Matrix, Quaternion

import mp_arms as A
import mp_lib as L
import mp_locomotion as M
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
    """Keys from (time, pose) entries, or (time, pose, ease) for the span after that key (mp_lib.Keys)."""
    keys = Keys(loop_length)
    for entry in entries:
        keys.add(*entry)
    return keys.at


# --- Hidden in cover --------------------------------------------------------------------------------
# The cover bodies (mp_stances) are turned round inside the root part, back to the wall. The holds are
# made on them: each gun is placed in a body part's own frame and aimed in the body's facing frame
# (mp_arms.placed), so a clip is right on both sides' bodies (arm clips move with the chest). Max Payne 3
# holds the gun low or upright in front while hidden (Steam "Multiplayer" trailer, 1:35-1:43).
placed, pole = A.placed, A.pole


def high_body():
    return S.cover_high("Right")(0.0)


def low_body(side="Right"):
    return S.cover_low(side)(0.0)


def cover_hold_high(kind):
    """Behind high cover, back to the wall. One: the pistol low in front of the belly, muzzle down, as
    Max holds it. Two: the rifle upright across the chest, muzzle up and to the left (kept under the
    wall's top). Dual: both pistols up in front of the chest, muzzles up."""
    body = high_body()

    def pose(t):
        rise, tilt = A.breathing(t, 3.0, 0.6)
        if kind == "One":
            right = placed(body, "LowerTorso", (0.25, 0.15 + rise, -0.95), 18.0, -58.0 + tilt, 8.0)
            return arms(right=right, right_elbow=pole(body, 1, -0.6, 0.4), body=body)
        if kind == "Dual":
            right = placed(body, "UpperTorso", (0.42, -0.25 + rise, -0.85), -6.0, 72.0 + tilt, 12.0)
            left = placed(body, "UpperTorso", (-0.42, -0.25 + rise, -0.85), 6.0, 72.0 + tilt, -12.0)
            return arms(right=right, left=left, right_elbow=pole(body, 0.6, -1, 0.2), left_elbow=pole(body, -0.6, -1, 0.2), body=body)
        rifle = placed(body, "UpperTorso", (0.42, -0.55 + rise, -0.8), 28.0, 48.0 + tilt, -18.0)
        return arms(right=rifle, left=A.support_frame(rifle, "Rifle"), right_elbow=pole(body, 1, -0.6, 0.4), left_elbow=pole(body, -1, -0.8, 0.1), body=body)
    return pose


def cover_hold_low(kind, side=None):
    """Behind low cover, folded over the knees with the back to the wall, the gun up in front of the face
    ready to pop up (the "Multiplayer" trailer's rifle, 1:43). One: the pistol beside the face, muzzle up.
    Dual: one each side of the face. Two: the rifle upright in front of the chest, muzzle up past the
    face and leaning away from the edge the head looks to, so it doesn't cross the face (a clip per side)."""
    body = low_body(side or "Right")
    near = A.by_part

    def pose(t):
        rise, tilt = A.breathing(t, 3.0, 0.6)
        if kind == "Two":
            s = 1.0 if side == "Right" else -1.0
            rifle = near(body, "Head", -s * 0.2, -1.0 + rise, 0.55, -s * 12.0, 52.0 + tilt, -s * 8.0)
            return arms(right=rifle, left=A.support_frame(rifle, "Rifle"), right_elbow=pole(body, 0.7, -1, 0.1), left_elbow=pole(body, -0.7, -1, 0.1), body=body)
        right = near(body, "Head", 0.72, -0.35 + rise, 0.2, 4.0, 80.0 + tilt, 10.0)
        if kind == "One":
            return arms(right=right, right_elbow=pole(body, 0.4, -1, 0.2), body=body)
        left = near(body, "Head", -0.72, -0.35 + rise, 0.2, -4.0, 80.0 + tilt, -10.0)
        return arms(right=right, left=left, right_elbow=pole(body, 0.4, -1, 0.2), left_elbow=pole(body, -0.4, -1, 0.2), body=body)
    return pose


# --- Blind fire: the gun over or round the cover, the body kept behind it ----------------------------
LOW_TOP = 3.6 - (1 + L.HIP_HEIGHT - 1.8)  # the test arena's LowWall top, above the root part in low cover

# Blind fire over low cover from the squat (2026-11-11). The old clip twisted the chest 105 degrees on the folded
# body; on the squat the same twist left the gun 0.02 under the top and the torso 0.42 into the wall. Here the chest
# comes up out of the squat's forward lean (the waist about upright) and
# leans to the left, lifting the gun shoulder; the arm goes straight up past the head and over the top, the head
# ducked, looking down. Hand and forearm stay in front of the wall's face: the gun pokes over it. The gun can't be
# level up there - with the arm straight up the wrist can't bend back far enough, and a level gun was at most 0.22
# over the top - so it points over the wall tipped up about 25 degrees. Found by a scored search on the squat (the
# arm and gun out of the test arena's LowWall and the head, the torso off the wall, the head kept low) with the
# twist left unmirrored (the gun is always in the right hand); checked again by check_run_fire(still=True).
LOW_FIRE = {
    # waist (pitch, yaw, roll), where the head looks (x toward the edge, y, z), the grip (x from the right
    # shoulder, y over LOW_TOP, z), the gun's yaw and pitch, the right elbow's way
    "Right": ((2.26, 0.93, 29.99), (0.14, -1.269, 0.328), (0.046, 0.557, -0.785), (-8.857, 22.222), (1.11, -0.528, 0.489)),
    "Left": ((0.781, -0.385, 31.181), (0.091, -1.314, 0.453), (0.004, 0.571, -0.735), (-3.017, 25.0), (1.248, -1.026, 0.34)),
}


def blind_fire(kind):
    """BlindFireLow{Right,Left}: on the squat, the chest up and leaning off the gun side (keyed at the waist),
    the gun arm straight up and the gun over the top, tipped up a little, without a look - the head ducks,
    looking down (keyed at the neck). LOW_FIRE says why. The head top stays about 3.05 over the floor (the
    test arena's 3.6-stud wall cleared by about 0.26, default R15) and the torso off the wall, so the gap holds.
    BlindFireHigh{Right,Left}: the gun arm out along the wall and the gun turned round the edge, the head
    looking along the wall, not round it. Working left the gun arm is the one by the edge; working right
    it reaches across the chest, the chest turned toward the edge (keyed at the waist).
    The other hand stays with the body clip or a carried gun; a two-handed gun gets its support hand
    from the game's aim layer. The shot itself leaves from the server's virtual muzzle (ShotRules)."""
    s = 1.0 if kind.endswith("Right") else -1.0
    side = "Right" if s > 0 else "Left"
    if kind.startswith("Low"):
        body = low_body(side)
        waist, (lx, ly, lz), (along, over, z), (yaw, pitch), (ex, ey, ez) = LOW_FIRE[side]
        body.set("Waist", *waist)
        S.look(body, V(s * lx, ly, lz))
        shoulder = L.pivot(L.solve(body), "RightShoulder")
        target = (shoulder.x + along, LOW_TOP + over, z)
        elbow = V(ex, ey, ez)
    else:
        body = high_body() if s > 0 else S.cover_high("Left")(0.0)
        if s > 0:
            # leaning forward off the wall and toward the edge, the chest turned a little to it, so the
            # arm reaches across to the corner without the other shoulder going into the wall
            body.set("Waist", -34.0, 15.0, 20.0)
        S.look(body, V(s, -0.1, 0.35))
        target = (0.95, 0.55, -0.25) if s > 0 else (-1.85, 0.55, -0.75)
        elbow = V(-0.3 if s > 0 else -0.6, -1, 0.6)
        yaw, pitch = s * 6.0, 0.0

    def pose(t):
        jolt = 0.04 * A.breathing(t, 0.5, 1.0)[0] / 0.018
        right = A.gun_frame((target[0], target[1] + jolt, target[2]), yaw, pitch, 0.0)
        return arms(right=right, right_elbow=elbow, body=body)
    return pose


# Blind fire while sliding along low cover (CoverLowMove{Left,Right}: side-on, the hips facing the way the
# body runs, folded nearly flat to keep the head under 3 studs). BlindFireLow's waist twist is made for the
# still body's hips, which face out from the wall: on the run it turned the chest a quarter turn the wrong
# way and the gun ended 2.7 out from the wall pointing back along it (2026-11-08, to-do 4.19). Folded that
# flat the shoulders are barely above the hips, so the chest comes partly out of the fold and leans the gun
# shoulder up; the arm goes straight up from it and the gun points over the top as high as BlindFireLow
# holds it. The head stays ducked under the raised arm, looking down ahead along the wall.
#   Left   the gun arm is on the wall side: the chest turns toward the wall, lifting the shoulder.
#   Right  it is on the open side: the chest rolls onto its left side, gun shoulder on top, facing out.
# Made on the run's body at the start of its cycle and checked on the whole cycle (register). The numbers
# were also chosen for the blends (Roblox blends each joint on its own, the short way round): raising the
# gun from the cover hold mid-slide comes up muzzle first, never down through the wall's face; and going
# left, starting or stopping a slide while firing keeps the gun over the top and pointing across while
# the hips turn under it. Going right the chest is turned about 150 degrees from BlindFireLow's, so its
# gun arm is too: the shoulder ended 170 degrees from the still clip's, the blend's way round flipped with
# the firing judder, and the gun swung back along the wall. The game doesn't cross-fade the two
# (AnimationController.DIP_ANY): the old clip goes down into the cover hold, then the new one comes up.
# Blind fire while sliding along high cover (CoverHighMove: a hunched jog, side-on): BlindFireHigh reaches
# round a wall's end from the still body, and on the run its chest twist turned the gun back along the
# wall (to-do 4.25). Mid-wall there's no end to reach round, so the gun arm points out ahead the way the
# body runs, about shoulder height, the barrel level and the head looking along it, the waist near the
# run's. Going right the gun arm is on the open side; going left it's on the wall side, the gun in front
# of the chest, the shoulder leading so the forearm passes beside the head (a first version crossed the
# face). Chosen like the low ones for the blends with BlindFireHigh and the cover holds. The two runs'
# gun arms are on opposite sides, so a reversal doesn't cross-fade either (AnimationController.dipFor).
RUN_FIRE = {
    # waist (pitch, yaw, roll), where the head looks, the grip (x from the shoulder, then y and z), the
    # gun's yaw and pitch, the elbow's way
    "LowLeft": ((-23.0, -73.0, 32.0), V(-0.55, -1.0, 0.0), (0.14, LOW_TOP + 0.7, -0.4), (0.0, -8.0), V(-0.88, -0.44, -0.18)),
    "LowRight": ((6.0, -54.0, 44.0), V(0.55, -1.0, 0.0), (0.25, LOW_TOP + 0.7, -0.09), (0.0, -8.0), V(-0.94, -0.08, 0.32)),
    "HighLeft": ((-8.2, 40.0, -3.3), V(-1.0, 0.23, -0.11), (-1.71, 0.33, 1.05), (84.1, -4.9), V(0.73, -0.14, 1.1)),
    "HighRight": ((-11.9, -7.5, -0.5), V(1.0, -0.34, 0.15), (1.71, 0.63, 2.52), (-97.3, 2.8), V(-0.53, -0.64, 0.74)),
}


def blind_fire_move(kind):
    """BlindFire{Low,High}Move{Right,Left}: blind fire on the cover run that goes that way (see RUN_FIRE)."""
    height = "Low" if kind.startswith("Low") else "High"
    run, _ = S.cover_move(height, kind[len(height):])
    waist, look, (along, y, z), (yaw, pitch), elbow = RUN_FIRE[kind]
    body = run(0.0)
    body.set("Waist", *waist)
    S.look(body, look)
    x = L.pivot(L.solve(body), "RightShoulder").x + along

    def pose(t):
        jolt = 0.04 * A.breathing(t, 0.5, 1.0)[0] / 0.018
        right = A.gun_frame((x, y + jolt, z), yaw, pitch, 0.0)
        return arms(right=right, right_elbow=elbow, body=body)
    return pose


GUN_CLEAR = 0.3  # studs the gun's box stays over LOW_TOP (default R15; a slimmer avatar's arm is ~0.28 lower)
# Still, from the squat, the gun gets 0.26 over (LOW_FIRE): only its muzzle end pokes past the wall's face, so a
# slimmer avatar's touches the top edge at most.
STILL_CLEAR = 0.24
# The head box's highest corner over the floor: no higher than the old BlindFireLow's (3.31 on the default R15).
# Blind firing, the chest comes up and the head with it, past the run's 2.98 and the lowest cover's 3.
HEAD_TOP = 3.35
WALL_GAP = 1.15  # CoverRules.GAP: the least the game keeps the root part off the wall


def check_run_fire(clip, height, side, samples=16, still=False):
    """Self-check on the run's whole cycle (still: BlindFireLow over the low cover idle's 5.2 s): the gun arm and
    gun out of the wall and the forearm, hand and gun out of the head (sampled through each box), the torso no
    nearer the wall than the run's upper arms (so the game's gap holds). Low: the gun over the top, the head as
    low as the still blind fire's. High: the barrel within 14 degrees of straight ahead."""
    run, g = (S.cover_low(side), {"cycle": 5.2}) if still else S.cover_move(height, side)
    top = LOW_TOP if height == "Low" else 99.0  # the HighWall is over the head
    ahead = V(1 if side == "Right" else -1, 0, 0)
    gun_size, gun_centre = (V(*v) for v in L.GUNS["Pistol"][:2])
    for i in range(samples):
        t = g["cycle"] * i / samples
        p = run(t)
        p.update(clip.sample(t % clip.length))
        world = L.solve(p)
        boxes = [(world[part], V(), V(*L.PARTS[part][0])) for part in ("RightUpperArm", "RightLowerArm", "RightHand")]
        boxes.append((L.grip(world), gun_centre, gun_size))
        points = [[m @ (c + V(x * s.x, y * s.y, z * s.z) / 2) for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1)]
                  for m, c, s in boxes]
        where = "%s at %.2f s" % (clip.name, t)
        if height == "Low":
            over = min(q.y for q in points[-1]) - LOW_TOP
            size = V(*L.PARTS["Head"][0])
            head = max((world["Head"] @ (V(x * size.x, y * size.y, z * size.z) / 2)).y for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)) - S.LOW
            assert over > (STILL_CLEAR if still else GUN_CLEAR), "%s: the gun only %.2f over the top" % (where, over)
            assert head < HEAD_TOP, "%s: the head top %.2f over the floor" % (where, head)
        else:
            assert (L.grip(world).to_3x3() @ V(0, 0, -1)).dot(ahead) > 0.97, where + ": the gun not pointing ahead"
        assert not any(q.z < -WALL_GAP and q.y < top for box in points for q in box), where + ": in the wall"
        head, half = world["Head"].inverted(), V(*L.PARTS["Head"][0]) / 2
        assert not any(all(abs(c) < h for c, h in zip(head @ q, half)) for box in points[1:] for q in box), where + ": in the head"
        # still, the hips stay where the idle rests them, at BACK_REACH
        assert S.reach(p, S.TORSO) < S.BACK_REACH + (1e-3 if still else 0.0), where + ": the torso reaches the wall"


# Blind fire with a two-handed gun behind high cover (to-do 4.26, 2026-11-10). BlindFireHigh and its runs were
# made with a pistol in the right hand. A long gun there pointed into the wall: the arm guard (AimLayer)
# swung the arm up to 50 degrees round to keep it out, the support hand went 0.4 into a wall's end reaching
# round it (working right) or couldn't reach the gun at all (working left, and on both runs). These hold the
# gun in both hands, across the front of the body:
#   Still  the gun points toward the edge being worked, turned round it, so its muzzle pokes past a wall's
#          end and mid-wall stays in front of the wall. Working right the edge is on the body's left: the gun
#          runs across the chest, the waist as the idle's. Working left it is on the gun arm's side: the
#          chest turns to the corner (78 degrees), the support arm across.
#   Run    the gun ahead along the wall the way the body runs, held close.
# The support hand is the game's: AimLayer puts it on each gun's own Support point, the elbow toward its
# HOLD_POLE in the root part's space, so the clips key it the same way. The poses were found by a scored
# search, as RUN_FIRE's, with the place's long guns (LONG_GUNS) at a wall's end 0.5 to 0.9 past the root
# (where a slide stops) and mid-wall, then rounded and checked again (check_two_fire).
TWO_FIRE = {
    # waist (pitch, yaw, roll), where the head looks (y, z; x toward the edge), the grip (x toward the edge:
    # still, in the root part's space; run, from the right shoulder; then y and z), the gun turned round
    # toward the wall (degrees from along it), its pitch and cant, the right elbow's way
    "HighRight": ((-1.7, 8.5, -3.6), (0.1, 0.27), (0.49, 0.06, 0.95), 41.0, -5.9, 5.0, (0.29, -0.78, 0.65)),
    "HighLeft": ((0.8, -78.0, 4.8), (-0.03, -0.33), (0.2, 0.26, 1.02), 17.0, 3.1, 13.0, (0.35, -1.61, 0.08)),
    "HighMoveRight": ((-20.5, -42.8, 14.6), (0.22, 0.5), (1.32, -0.44, 1.75), 5.3, 1.1, -0.5, (0.55, -0.59, 0.69)),
    "HighMoveLeft": ((-5.6, -34.7, 9.5), (0.34, 0.16), (0.34, -0.24, 0.46), 5.0, -1.7, -4.3, (-1.1, -1.24, 0.15)),
}
LONG_GUNS = L.LONG_GUNS  # the place's long guns as they are (mp_lib)


def blind_fire_two(kind):
    """BlindFireHighTwo{Right,Left} on the still idle, BlindFireHighMoveTwo{Right,Left} on the run that goes
    that way (see TWO_FIRE). Keys both arms, the waist and the neck."""
    move = "Move" in kind
    side = "Right" if kind.endswith("Right") else "Left"
    s = 1.0 if side == "Right" else -1.0
    waist, (look_y, look_z), (gx, gy, gz), turn, pitch, roll, elbow = TWO_FIRE[kind]
    body = S.cover_move("High", side)[0](0.0) if move else S.cover_high(side)(0.0)
    body.set("Waist", *waist)
    S.look(body, V(s, look_y, look_z))
    x = (L.pivot(L.solve(body), "RightShoulder").x if move else 0.0) + s * gx
    yaw = -s * (90.0 - turn)

    def pose(t):
        jolt = 0.04 * A.breathing(t, 0.5, 1.0)[0] / 0.018
        right = A.gun_frame((x, gy + jolt, gz), yaw, pitch, s * roll)
        return arms(right=right, left=A.support_frame(right, "Rifle"), right_elbow=V(s * elbow[0], elbow[1], elbow[2]),
                    left_elbow=HOLD_POLE, body=body)
    return pose


def _depth(a, b):
    return L.box_depth(a[0], a[1], b[0], b[1])


def _part(world, name):
    return (world[name], L.PARTS[name][0])


def _wall(end=None, side="Right"):
    """The high wall in the root part's space: mid-wall, or ending `end` past the root on the side worked."""
    near, far = -WALL_GAP, -WALL_GAP - 2.0
    lo, hi = -50.0, 50.0
    if end is not None:
        lo, hi = (-50.0, end) if side == "Right" else (-end, 50.0)
    return (Matrix.Translation(V((lo + hi) / 2, L.FLOOR + 4.0, (near + far) / 2)), (hi - lo, 8.0, near - far))


def _with_support(p, gun):
    """The pose with the left hand where AimLayer puts it on this gun, and how far the hand is from it."""
    q = p.copy()
    miss = L.place_support(q, gun)
    return q, L.solve(q), miss


def _gun(world, gun):
    return L.long_gun_box(world, gun)


def _two_fire_parts(world, gun):
    """The arm boxes and the gun's: upper arms first, then forearms and hands, then the gun."""
    upper = [_part(world, n) for n in ("RightUpperArm", "LeftUpperArm")]
    rest = [_part(world, n) for n in ("RightLowerArm", "RightHand", "LeftLowerArm", "LeftHand")]
    return upper, rest, _gun(world, gun)


def _guard_turn(p, gun):
    """Mid-wall, the smallest turn of the right arm about the vertical through its shoulder (the arm guard's
    yaw or swing, in 2 degree steps up to 60) that clears it and the gun, and the left arm's depth in the wall
    once the support hand follows the gun. None if no turn does."""
    wall = _wall()
    for step in range(31):
        for sign in ((1.0,) if step == 0 else (1.0, -1.0)):
            q = p.copy()
            if step:
                world = L.solve(q)
                parent = world["UpperTorso"].to_quaternion()
                turn = Quaternion(V(0, 1, 0), math.radians(sign * 2.0 * step))
                q["RightShoulder"] = ((parent.inverted() @ turn @ parent) @ q.q("RightShoulder"), q.t("RightShoulder"))
            world = L.solve(q)
            boxes = [_part(world, n) for n in ("RightUpperArm", "RightLowerArm", "RightHand")] + [_gun(world, gun)]
            if max(_depth(b, wall) for b in boxes) <= 0.05:
                _, world, _ = _with_support(q, gun)
                left = max(_depth(_part(world, n), wall) for n in ("LeftUpperArm", "LeftLowerArm", "LeftHand"))
                return 2.0 * step, left
    return None


def _head_reach(world, s):
    half = V(*L.PARTS["Head"][0]) / 2
    return max(s * (world["Head"] @ V(x * half.x, y * half.y, z * half.z)).x for x in (-1, 1) for y in (-1, 1) for z in (-1, 1))


def check_two_fire(clip, side, move, samples=16):
    """Self-check with every long gun (the support hand placed as AimLayer places it): the arms and gun out of
    the wall, the forearms, hands and gun out of the head, the support hand on the gun, the torso's reach
    under BACK_REACH, and nothing pressed deeper into the torso's box than the holds already are (the boxes
    are crude: the cover hold's forearms are 0.74 to 0.83 in, the low rifle hold's gun 0.73).
    Still: at a wall's end 0.5, 0.7 and 0.9 past the root nothing touches it, the muzzle pokes 0.4 past the
    widest, the head no nearer the edge than the idle's + 0.15; mid-wall the arm guard needs at most 30
    degrees (the M107, five studs long, 45) and the support arm stays out after it.
    Run: on the run's whole cycle, out of the wall, the gun clear of the legs and within 22 degrees of ahead."""
    s = 1.0 if side == "Right" else -1.0
    keyed = clip.joints
    if move:
        run, g = S.cover_move("High", side)
        times = [g["cycle"] * i / samples for i in range(samples)]
        idle_head = None
    else:
        run = S.cover_high(side)
        times = [0.0, 0.125, 0.375]  # the firing judder: middle, up, down
        idle_head = _head_reach(L.solve(run(0.0)), s)
    for t in times:
        p = run(t)
        arm = clip.sample(t % clip.length)
        for j in keyed:
            p[j] = arm[j]
        where = "%s at %.2f s" % (clip.name, t)
        assert S.reach(p, S.TORSO) < S.BACK_REACH, where + ": the torso reaches the wall"
        if move:
            barrel = L.grip(L.solve(p)).to_3x3() @ V(0, 0, -1)
            assert barrel.normalized().dot(V(s, 0, 0)) > math.cos(math.radians(22)), where + ": the gun not ahead"
        else:
            assert _head_reach(L.solve(p), s) < idle_head + 0.15, where + ": the head nearer the edge than the idle's"
            muzzle = L.grip(L.solve(p)) @ V(*LONG_GUNS["AK47"][3])
            assert s * muzzle.x > 0.9 + 0.4, where + ": the muzzle short of a wall's end"
        for gun in LONG_GUNS:
            q, world, miss = _with_support(p, gun)
            label = "%s, %s" % (where, gun)
            # 0.05: the M500's pump is the furthest support point (1.43 ahead of the grip), 0.03 out of reach
            # at one point of the run going right
            assert miss < 0.05, "%s: the support hand %.2f off the gun" % (label, miss)
            upper, rest, gunbox = _two_fire_parts(world, gun)
            head = _part(world, "Head")
            assert max(_depth(b, head) for b in rest + [gunbox]) < 0.03, label + ": in the head"
            torso = [_part(world, "UpperTorso"), _part(world, "LowerTorso")]
            assert max(_depth(b, tb) for b in rest for tb in torso) < 1.0, label + ": an arm deep in the torso"
            assert max(_depth(gunbox, tb) for tb in torso) < 0.75, label + ": the gun deep in the torso"
            boxes = upper + rest + [gunbox]
            if move:
                deepest = max(_depth(b, _wall()) for b in boxes)
                assert deepest < 0.03, "%s: %.2f in the wall" % (label, deepest)
                legs = max(_depth(gunbox, _part(world, n)) for n in ("RightUpperLeg", "LeftUpperLeg", "RightLowerLeg", "LeftLowerLeg"))
                assert legs < 0.13, "%s: the gun %.2f in a leg" % (label, legs)
                continue
            for end in (0.5, 0.7, 0.9):
                deepest = max(_depth(b, _wall(end, side)) for b in boxes)
                assert deepest < (0.06 if gun == "M107" else 0.03), "%s: %.2f in a wall's end %.1f past" % (label, deepest, end)
            if t == 0.0:
                guard = _guard_turn(p, gun)
                assert guard is not None, label + ": the arm guard can't clear it mid-wall"
                angle, left = guard
                assert angle <= (45.0 if gun == "M107" else 30.0), "%s: the arm guard turns it %d degrees mid-wall" % (label, angle)
                assert left < 0.05, "%s: the support arm %.2f in the wall mid-wall" % (label, left)


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


# Switching between the carried two-handed gun and a one-handed gun (2026-11-12). Carried, the gun hangs from the left
# hand by its middle (mp_arms.CARRIES); in hand, from the right by its grip. The game moves it to the other hand
# partway through the switch (LoadoutRules.HANDOVER: these shares of the switch's time), when both hands are on it
# in HANDOVER: the right on the grip, the left round the middle, the gun across the front of the body pointing left.
# Before, it was re-hung as the switch began: drawing it, the rifle jumped 2.4 studs and turned 50 degrees in one
# frame; putting it back, it snapped round 90 to 112 degrees. Found by a scored search on the idle (both hands on
# it, nothing in the body, the elbows down, the gun clear of the legs on the left arm's way there from the carry).
HANDOVER = ((0.675, -0.083, -1.262), 75.5, -9.3, -84.8, V(0.253, 0.006, 0.497), V(-0.414, 0.76, -0.602))
DRAW_HANDOVER = 0.4  # drawing the carried gun: the right hand takes it
SWAP_HANDOVER, SWAP_DRAW = 0.33, 0.53  # putting it back for a one-handed gun: the left takes it, then the right draws
SWITCH_GUN = "AK47"  # the clips are shared by the long guns; each hangs from the left hand at its own middle
SWITCH_REPORT = None  # a dict to collect check_switch's numbers (tuning)


def joints_of(pose, joints):
    p = Pose()
    for j in joints:
        p[j] = pose[j]
    return p


def handover_pose():
    """Both hands on the gun in HANDOVER, on the standing idle (only the arms are kept)."""
    position, yaw, pitch, roll, right_elbow, left_elbow = HANDOVER
    g = gun(position, yaw, pitch, roll)
    p = M.idle_pose(0.0)
    L.place_hand(p, "Right", L.hand_for_grip(g), right_elbow)
    L.place_hand(p, "Left", L.hand_for_carry(g, SWITCH_GUN), left_elbow)
    return joints_of(p, L.ARMS)


# The left arm's waypoint between the carry and the handover: the gun level beside the left hip at belly height, so
# its stock doesn't sweep through the left thigh as it turns (going straight there it went 0.5 into it, the M107 0.76).
# The left arm goes carry - VIA - handover in straight joint blends, as the search checked them: on a spline through
# the three, the stock swung 0.35 into the hip.
VIA = ((-1.514, 0.179, -0.539), 13.9, 0.0, 0.0, V(-1.801, -1.193, -0.09))


def via_pose():
    position, yaw, pitch, roll, elbow = VIA
    p = M.idle_pose(0.0)
    L.place_hand(p, "Left", L.hand_for_carry(gun(position, yaw, pitch, roll), SWITCH_GUN), elbow)
    return joints_of(p, L.LEFT_ARM)


def two_arms(right_keys, left_keys):
    """Each arm on its own keys."""
    right, left = keyed(right_keys), keyed(left_keys)

    def pose(t):
        p = joints_of(right(t), L.RIGHT_ARM)
        p.update(joints_of(left(t), L.LEFT_ARM))
        return p
    return pose


def rifle_ready():
    return joints_of(A.two_handed_hold("Rifle", (0.45, -0.3, -0.2), 40.0, -15.0)(0.0), L.ARMS)


def pistol_ready():
    return joints_of(A.one_handed_hold(*LOW_READY, RIGHT_LOW)(0.0), L.RIGHT_ARM)


def draw_two():
    """Drawing the carried two-handed gun (0.55 s, stretched to its DrawTime): the left hand lifts it by its middle
    over the thigh (VIA) and brings it across the front of the body, the right takes the grip (DRAW_HANDOVER), it
    swings up across the chest, the left hand slides to the handguard, and down into the low ready. Starts on the
    carry and the pistol's low ready, ends on HoldRifle."""
    length = 0.55
    at = round(DRAW_HANDOVER * length, 4)
    port = gun((0.35, -0.1, -0.85), 30.0, 25.0, -20.0)  # up 35 degrees, the M107 went 0.12 into the head
    ported = arms(right=port, left=A.support_frame(port, "Rifle"), right_elbow=V(1, -0.6, 0.6), left_elbow=HOLD_POLE, body=M.idle_pose(0.0))
    over, ready = handover_pose(), rifle_ready()
    return two_arms(
        [(0.0, pistol_ready()), (at, over), (0.38, ported), (length, ready)],
        [(0.0, joints_of(A.carry_two_handed(0.0), L.LEFT_ARM), "linear"), (round(at / 2, 4), via_pose(), "linear"), (at, over), (0.38, ported), (length, ready)])


def swap_to_one():
    """Putting the two-handed gun back to the carry for a one-handed gun (0.3 s, stretched to that gun's DrawTime):
    the left hand takes the rifle by its middle across the front of the body (SWAP_HANDOVER) and carries it over the
    thigh (VIA) down to the left side, while the right hand goes to the thigh holster (SWAP_DRAW) and brings the
    pistol up into the low ready. Starts on HoldRifle, ends on the carry and HoldPistol."""
    length = 0.3
    at, draw = round(SWAP_HANDOVER * length, 4), round(SWAP_DRAW * length, 4)
    holster = arms(right=gun((1.06, -1.3, 0.08), 0.0, -88.0, 0.0), right_elbow=V(0.8, 0, 1), body=M.idle_pose(0.0))
    over, ready = handover_pose(), rifle_ready()
    return two_arms(
        [(0.0, ready), (at, over), (draw, holster), (length, pistol_ready())],
        [(0.0, ready), (at, over, "linear"), (round((at + length) / 2, 4), via_pose(), "linear"), (length, joints_of(A.carry_two_handed(0.0), L.LEFT_ARM))])


def check_switch(clip, handover, to_right, samples=60):
    """Self-check of a switch clip on the standing idle with every long gun, hung as the game hangs it: from the left
    hand by its middle before the handover and from the right by its grip after (or the other way round). Carried in
    the left hand it stays out of the body; in the right, no deeper in it than HoldRifle's own pose (on these boxes
    the rifle held at the low ready reads up to 0.35 into the legs and 0.85 into the torso, by gun); out of the head and the floor
    throughout. At the handover the AK-47 is in the same place from either hand."""
    body = M.idle_pose(0.0)
    legs = ("LeftUpperLeg", "RightUpperLeg", "LeftLowerLeg", "RightLowerLeg")
    trunk = ("UpperTorso", "LowerTorso")

    def depths(arm, left_hand):
        p = body.copy()
        for j in L.ARMS:
            p[j] = arm[j]
        w = L.solve(p)
        out = {}
        for g in L.LONG_GUNS:
            box = L.long_gun_box(w, g, carried=True) if left_hand else L.long_gun_box(w, g)
            out[g] = (L.deepest([box], [L.part_box(w, n) for n in legs]), L.deepest([box], [L.part_box(w, n) for n in trunk]),
                      L.deepest([box], [L.part_box(w, "Head")]), L.box_lowest(box) - L.FLOOR)
        return out

    held = depths(rifle_ready(), False)
    held_legs, held_trunk = max(v[0] for v in held.values()), max(v[1] for v in held.values())
    worst = {}
    for i in range(samples + 1):
        t = clip.length * i / samples
        left_hand = (t < handover * clip.length) == to_right
        for g, (in_legs, in_trunk, in_head, over_floor) in depths(clip.sample(t), left_hand).items():
            where = "%s at %.3f s, %s %s" % (clip.name, t, g, "in the left hand" if left_hand else "in the right")
            # the M107's middle is half a stud further along it than the AK-47's the handover was made with
            carried = 0.1 if g == "M107" else 0.05
            allow_legs, allow_trunk = (carried, carried) if left_hand else (held_legs + 0.1, held_trunk + 0.1)
            assert in_legs < allow_legs, "%s: %.2f in a leg" % (where, in_legs)
            assert in_trunk < allow_trunk, "%s: %.2f in the torso" % (where, in_trunk)
            assert in_head == 0.0, where + ": in the head"
            assert over_floor > 0.3, "%s: %.2f over the floor" % (where, over_floor)
            for key, value in (("legs", in_legs), ("trunk", in_trunk), ("floor", -over_floor)):
                k = (key + (" left" if left_hand else " right"), g == "M107")
                worst[k] = max(worst.get(k, -9.0), value)
    p = body.copy()
    arm = clip.sample(handover * clip.length)
    for j in L.ARMS:
        p[j] = arm[j]
    w = L.solve(p)
    a, b = L.carry_grip(w, SWITCH_GUN), L.grip(w)
    gap = (a.translation - b.translation).length
    turn = math.degrees(a.to_quaternion().rotation_difference(b.to_quaternion()).angle)
    assert gap < 0.03 and min(turn, 360 - turn) < 3.0, "%s: at the handover the gun is %.2f and %.0f degrees apart" % (clip.name, gap, turn)
    worst["handover gap", False], worst["handover turn", False] = gap, min(turn, 360 - turn)
    return worst


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


# One-handed reloads (2026-11-11). With a two-handed gun carried in the left hand, the reloads made for a free left
# hand brought that hand - and the carried gun with it - over to the gun being reloaded: the carried rifle went
# through the pistol. These key only the right arm, so the carried gun stays in its carry, and the gun is reloaded
# against the belt the way ReloadDual's hands do it. Each has its two-handed clip's markers at the same times
# (AnimationController moves the gun's parts on them); the game plays them while a two-handed gun is carried.
ONE_HAND_REPORT = None  # a dict to collect check_one_hand_reload's numbers instead of asserting (tuning)
BELT = (1.25, -0.4, -0.5)  # the right hip, where the gun meets the belt's pouches
BELT_ELBOW = V(1, 0, 0.6)
WORK_ELBOW = V(1, -1, 0.3)


def at_belt(pitch, roll=0.0, down=0.0, position=BELT):
    """The gun at the belt, pushed `down` onto a pouch."""
    x, y, z = position
    return gun((x, y - down, z), 0.0, pitch, roll)


def one_hand(entries):
    """Right-arm keys from (time, grip frame, elbow) entries."""
    return keyed([(t, arms(right=g, right_elbow=e)) for t, g, e in entries])


def reload_pistol_one():
    """Magazine pistols and the Uzi, one-handed (1.6 s): tip the gun in and the magazine drops, down to the belt
    where it is pushed onto a fresh one, then a flick racks the slide."""
    ready = gun(*LOW_READY)
    keys = one_hand([
        (0.0, ready, RIGHT_LOW),
        (0.2, gun((0.55, 0.05, -0.95), 20.0, 15.0, 35.0), WORK_ELBOW),  # tipped in, the magazine drops
        (0.5, at_belt(5.0), BELT_ELBOW),
        (0.78, at_belt(5.0, down=0.12), BELT_ELBOW),  # pushed onto the fresh magazine
        (1.0, gun((0.8, 0.0, -0.9), 6.0, 25.0, 8.0), WORK_ELBOW),  # the flick racks it
        (1.3, gun((0.9, -0.5, -0.8), 10.0, -25.0, 10.0), RIGHT_LOW),
        (1.6, ready, RIGHT_LOW),
    ])
    markers = [(0.2, "MagOut", ""), (0.5, "MagGrab", ""), (0.78, "MagIn", ""), (0.95, "BoltBack", ""), (1.05, "BoltForward", "")]
    return keys, markers


def reload_revolver_one():
    """The revolver, one-handed (3 s): a flick of the wrist swings the cylinder out, muzzle up and a shake to dump
    the empties, down to the belt where the cylinder is pushed onto a speedloader, and a flick back shuts it."""
    ready = gun((1.12, -0.8, -0.58), 4.0, -48.0)  # HoldRevolver
    dump = gun((0.45, 0.4, -0.85), 15.0, 75.0, 80.0)  # muzzle up, the empties fall out
    shake = Matrix.Translation(V(0, -0.08, 0)) @ dump
    keys = one_hand([
        (0.0, ready, RIGHT_LOW),
        (0.3, gun((0.45, 0.1, -0.95), 25.0, 10.0, 80.0), WORK_ELBOW),  # rolled onto its side, the cylinder out
        (0.7, dump, WORK_ELBOW),
        (0.85, shake, WORK_ELBOW),
        (1.0, dump, WORK_ELBOW),
        (1.4, at_belt(-60.0, 30.0), BELT_ELBOW),
        (1.8, at_belt(-60.0, 30.0, down=0.1), BELT_ELBOW),  # onto the speedloader
        (2.0, at_belt(-60.0, 30.0), BELT_ELBOW),
        (2.35, gun((0.8, 0.05, -0.95), 8.0, 20.0, -20.0), WORK_ELBOW),  # the flick back shuts it
        (2.65, gun((0.9, -0.5, -0.8), 10.0, -25.0, 10.0), RIGHT_LOW),
        (3.0, ready, RIGHT_LOW),
    ])
    markers = [(0.3, "CylinderOut", ""), (1.4, "MagGrab", ""), (2.35, "CylinderIn", "")]
    return keys, markers


def reload_sawn_off_one():
    """The sawn-off, one-handed (2.4 s): a snap down breaks it open, tipped up to drop the empties, down to the
    belt's shell loops where the open breech is dipped onto two shells, and a snap up shuts it."""
    ready = gun((1.08, -0.5, -0.76), 4.0, -30.0)  # HoldSawnOff
    keys = one_hand([
        (0.0, ready, RIGHT_LOW),
        (0.25, gun((0.75, -0.35, -0.95), 8.0, -25.0), WORK_ELBOW),  # the snap down breaks it open
        (0.6, gun((0.6, 0.2, -0.85), 15.0, 60.0), WORK_ELBOW),  # tipped up, the empties fall out
        (1.05, at_belt(-40.0), BELT_ELBOW),
        (1.35, at_belt(-40.0, down=0.1), BELT_ELBOW),
        (1.47, at_belt(-40.0), BELT_ELBOW),
        (1.6, at_belt(-40.0, down=0.1), BELT_ELBOW),
        (1.9, gun((0.75, 0.1, -1.0), 8.0, 25.0), WORK_ELBOW),  # the snap up shuts it
        (2.4, ready, RIGHT_LOW),
    ])
    markers = [(0.25, "BreakOpen", ""), (1.05, "MagGrab", ""), (1.35, "ShellIn", "1"), (1.6, "ShellIn", "2"), (1.9, "BreakClose", "")]
    return keys, markers


def check_one_hand_reload(clip, kind, two, samples=24, report=None):
    """Self-check over the clip on the bodies the carries play over (standing, crouched, behind high and low cover),
    with every long gun carried as its carry holds it: the reloaded gun and the right forearm and hand stay out of the
    carried gun and the head, and no deeper in the legs and torso than the two-handed reload's (`two`, sampled the
    same way). Made on an upright chest like every reload, both go into the thighs on the folded bodies (crouched,
    low cover), and on the boxes a forearm at rest already reads 0.7 into the torso."""
    bodies = [(M.idle_pose(0.0), A.carry_two_handed(0.0)), (M.crouch_idle_pose(0.0), A.carry_two_handed_low(0.0)),
              (S.cover_high("Right")(0.0), A.carry_two_handed_cover(0.0)), (S.cover_low("Right")(0.0), A.carry_two_handed_cover_low(0.0))]
    size, centre = L.GUNS[kind][:2]
    for n, (body, carry) in enumerate(bodies):
        worst = {}
        for label, sample in (("one", clip.sample), ("two", two)):
            for i in range(samples):
                p = body.copy()
                for j in L.LEFT_ARM:
                    p[j] = carry[j]
                arm = sample(clip.length * i / samples)
                for j in L.RIGHT_ARM:
                    p[j] = arm[j]
                world = L.solve(p)
                held = (L.grip(world) @ Matrix.Translation(V(*centre)), size)
                fore = [L.part_box(world, q) for q in ("RightLowerArm", "RightHand")]
                legs = [L.part_box(world, q) for q in A.LEGS]
                trunk = [L.part_box(world, q) for q in A.TRUNK]
                carried = [L.long_gun_box(world, g, carried=True) for g in L.LONG_GUNS]
                for key, value in (("carried", L.deepest([held] + fore, carried)), ("head", L.deepest([held] + fore, [L.part_box(world, "Head")])),
                                   ("legs", L.deepest([held] + fore, legs)), ("torso", L.deepest([held] + fore, trunk))):
                    worst[label, key] = max(worst.get((label, key), 0.0), value)
        if report is not None:
            report["%s body %d" % (clip.name, n)] = {"%s %s" % k: round(v, 3) for k, v in worst.items()}
            continue
        where = "%s, body %d" % (clip.name, n)
        assert worst["one", "carried"] < 0.02, "%s: %.2f into the carried gun" % (where, worst["one", "carried"])
        assert worst["one", "head"] < 0.02, where + ": in the head"
        for key in ("legs", "torso"):
            assert worst["one", key] < worst["two", key] + 0.1, "%s: %.2f in the %s (the two-handed reload %.2f)" % (where, worst["one", key], key, worst["two", key])


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
        still = Clip("BlindFireLow" + side, 0.5, blind_fire("Low" + side), loop=True, priority="Action2", joints=R | {"Waist", "Neck"}, drop=1.8,
                     gun=("Pistol", None), note="over CoverLow" + side)
        check_run_fire(still, "Low", side, samples=26, still=True)
        Clip("BlindFireHigh" + side, 0.5, blind_fire("High" + side), loop=True, priority="Action2", joints=R | {"Waist", "Neck"}, gun=("Pistol", None))
        for height, drop in (("Low", 1.8), ("High", 0.0)):
            move = Clip("BlindFire%sMove%s" % (height, side), 0.5, blind_fire_move(height + side), loop=True, priority="Action2",
                        joints=R | {"Waist", "Neck"}, drop=drop, gun=("Pistol", None), note="over Cover%sMove%s" % (height, side))
            check_run_fire(move, height, side)
        # a two-handed gun behind high cover: both hands on it (TWO_FIRE)
        still = Clip("BlindFireHighTwo" + side, 0.5, blind_fire_two("High" + side), loop=True, priority="Action2",
                     joints=B | {"Waist", "Neck"}, gun=("Rifle", None), note="over CoverHigh" + side)
        check_two_fire(still, side, False)
        move = Clip("BlindFireHighMoveTwo" + side, 0.5, blind_fire_two("HighMove" + side), loop=True, priority="Action2",
                    joints=B | {"Waist", "Neck"}, gun=("Rifle", None), note="over CoverHighMove" + side)
        check_two_fire(move, side, True)
    Clip("DrawOneHanded", 0.3, draw_one, priority="Action3", joints=R, gun=("Pistol", None))
    Clip("DrawDual", 0.3, draw_dual, priority="Action3", joints=B, gun=("Pistol", "Pistol"))
    draw = Clip("DrawTwoHanded", 0.55, draw_two(), priority="Action3", joints=B, gun=("Rifle", None))
    swap = Clip("SwapToOneHanded", 0.3, swap_to_one(), priority="Action3", joints=B, gun=("Pistol", None), note="the rifle back to the carry")
    for clip, handover, to_right in ((draw, DRAW_HANDOVER, True), (swap, SWAP_HANDOVER, False)):
        worst = check_switch(clip, handover, to_right)
        if SWITCH_REPORT is not None:
            SWITCH_REPORT[clip.name] = {"%s%s" % (k, " M107" if big else ""): round(v, 3) for (k, big), v in worst.items()}
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
    # a two-handed gun carried in the left hand: the right hand alone (AnimationController picks these then)
    for name, length, made, gun_id, two in (("ReloadPistolOneHand", 1.6, reload_pistol_one(), "Pistol", reload_pistol()),
                                            ("ReloadRevolverOneHand", 3.0, reload_revolver_one(), "Revolver", reload_revolver()),
                                            ("ReloadSawnOffOneHand", 2.4, reload_sawn_off_one(), "SawnOff", reload_sawn_off())):
        pose, markers = made
        one = Clip(name, length, pose, priority="Action3", joints=R, markers=markers, gun=(gun_id, None))
        check_one_hand_reload(one, gun_id, two[0], report=ONE_HAND_REPORT)
