"""Maximum Pain - stance clips: the shoot-dodge (run-up, flight, landing, on the floor, getting up),
Last Stand (the fall, the stand, the wake-up), the vault, and cover (high and low, still and moving
along the wall, round an outside corner, aiming out of cover).

Heights: each clip is made on its own stance's floor (the game lowers the hips by the stance's
hipDrop, StanceRules), and the game's aim layer eases the body between heights when the stance
changes, so no clip has to. The shoot-dodge landing is the exception: the body really falls there,
so DodgeLand starts from the flight pose above the floor and lands on it.

Arms: the gun clips own the arms whenever a gun is held (hold, aim, blind fire, reload), and the aim
layer turns them onto the target from any of these poses, so the bodies here only have to fly, lie
and crouch the right way. The arms in these clips are for empty hands.
"""
import math

from mathutils import Matrix

import mp_lib as L
import mp_locomotion as M
from mp_lib import Clip, Keys, Pose, V, rot, smooth

TAU = 2 * math.pi
PRONE = L.FLOOR + 2.2  # DodgeGround and LastStand lower the hips 2.2
KNEEL = L.FLOOR + 1.2  # GettingUp lowers them 1.2
LOW = L.FLOOR + 1.8  # crouching and low cover
PREP = L.FLOOR + 0.6  # the dive's run-up
AIR_DROP = -0.55  # the body flies a little below the root part, so dives stay low
# Lying poses rest this far into the floor (studs). The boxes here are the default avatar's; slimmer
# avatars' parts are thinner and floated 0.18 above the floor when the boxes just touched it.
LYING = -0.06
SIDES = (("Left", -1.0), ("Right", 1.0))


def empty_arms(pose, shoulder, out, elbow, wrist=-6.0, yaw=0.0):
    for side, sign in SIDES:
        pose.set(side + "Shoulder", shoulder, sign * yaw, sign * out)
        pose.set(side + "Elbow", elbow, 0, 0)
        pose.set(side + "Wrist", wrist, 0, 0)
    return pose


def legs(pose, left, right, ankle=-30.0):
    """Leg angles (hip pitch, hip yaw, hip roll, knee) for poses whose feet aren't on the floor."""
    for side, (hip, yaw, roll, knee) in (("Left", left), ("Right", right)):
        pose.set(side + "Hip", hip, yaw, roll)
        pose.set(side + "Knee", knee, 0, 0)
        pose.set(side + "Ankle", ankle, 0, 0)
    return pose


def plant(pose, side, x, z, floor, yaw=0.0, toe=0.0, heel=0.0, knee=None):
    sole, r = L.foot_on_floor(x, z, floor, yaw, toe, heel)
    L.leg_ik(pose, side, sole, r, knee or V(x * 0.4, 0, -1))
    return pose


def palm(pose, side, x, z, floor, yaw=0.0, elbow=None):
    """A hand flat on the floor (arm IK), fingers turned by `yaw`."""
    hand = Matrix.Translation(V(x, floor + 0.16, z)) @ rot(0, yaw, 0).to_matrix().to_4x4()
    L.place_hand(pose, side, hand, elbow or V(0, 0.3, 1))
    return pose


# --- Shoot-dodge -------------------------------------------------------------------------------------
def dive_prep(direction):
    """The run-up (0.2 s, hips 0.6 lower): a dip and a drive toward the dive, the body already
    leaning the way it will fly."""
    lean = {"Forward": (-34.0, 0.0), "Back": (24.0, 0.0), "Left": (0.0, 26.0), "Right": (0.0, -26.0)}[direction]
    away = {"Forward": V(0, 0, 0.35), "Back": V(0, 0, -0.3), "Left": V(0.3, 0, 0), "Right": V(-0.3, 0, 0)}[direction]

    def pose(t):
        u = smooth(t / 0.2)
        p = Pose()
        p.set("Root", lean[0] * u - 6.0, 0, lean[1] * u, move=(0, 0.45 - 0.25 * u, 0))
        p.set("Waist", -8.0 + 4.0 * u, 0, 0)
        p.set("Neck", 10.0, 0, 0)
        empty_arms(p, 20.0 + 30.0 * u, 12.0, 50.0)
        # both feet down; the driving foot (away from the dive) ends behind, on its toes
        for side, sign in SIDES:
            x = sign * 0.6 + away.x * u * (1.0 if sign * away.x > 0 else 0.4)
            z = away.z * u * (1.0 if side == "Right" else 0.5)
            plant(p, side, x, z, PREP, 0, 0, 30.0 * u if side == "Right" else 10.0 * u)
        return p
    return pose


def dive_air(direction, t=0.0):
    """The flight (DodgeAir): flat out round the root part and a little below it, legs trailing
    together with a slow flutter (one a second)."""
    f = math.sin(TAU * t)
    p = Pose()
    if direction == "Forward":
        # head first, chest down, back arched to see ahead (Max Payne 3's forward dive)
        p.set("Root", -82.0, 0, 2.0 * f, move=(0, AIR_DROP, 0.4))
        p.set("Waist", 14.0, 0, 0)
        p.set("Neck", 42.0, 0, 0)
        legs(p, (-6.0, 0, -3.0, -14.0 + 5.0 * f), (-2.0, 0, 3.0, -26.0 - 5.0 * f))
        empty_arms(p, 165.0, 8.0, 20.0)
    elif direction == "Back":
        # on the back, feet first toward the target, curled up to see over them
        p.set("Root", 80.0, 0, 2.0 * f, move=(0, AIR_DROP, -0.4))
        p.set("Waist", -26.0, 0, 0)
        p.set("Neck", -32.0, 0, 0)
        legs(p, (22.0, 4.0, -4.0, -30.0 + 6.0 * f), (36.0, -4.0, 4.0, -50.0 - 6.0 * f))
        empty_arms(p, 60.0, 20.0, 30.0)
    else:
        # sideways, head leading, chest square to the target
        s = 1.0 if direction == "Left" else -1.0
        p.set("Root", 4.0, 0, s * 82.0, move=(0, AIR_DROP, 0))
        p.set("Waist", -6.0, s * 6.0, -s * 10.0)
        p.set("Neck", 0, 0, -s * 30.0)
        lead, trail = (14.0, 0, 0, -26.0 + 5.0 * f), (-10.0, 0, 0, -12.0 - 5.0 * f)
        legs(p, lead if s > 0 else trail, trail if s > 0 else lead)
        empty_arms(p, 80.0, 10.0, 25.0)
    return p


def dive_impact(direction, floor=PRONE):
    """Down on the floor the way the dive came in."""
    p = Pose()
    if direction == "Forward":
        p.set("Root", -90.0, 0, 0)
        p.set("Waist", 16.0, 0, 0)  # chest pushed up off the floor
        p.set("Neck", 34.0, 0, 0)
        legs(p, (-4.0, 0, -4.0, -12.0), (0.0, 0, 4.0, -20.0))
        empty_arms(p, 150.0, 16.0, 30.0)
    elif direction == "Back":
        p.set("Root", 86.0, 0, 0)
        p.set("Waist", -22.0, 0, 0)
        p.set("Neck", -34.0, 0, 0)
        legs(p, (26.0, 4.0, -6.0, -36.0), (40.0, -4.0, 6.0, -56.0))
        empty_arms(p, 40.0, 30.0, 40.0)
    else:
        s = 1.0 if direction == "Left" else -1.0
        p.set("Root", 6.0, 0, s * 90.0)
        p.set("Waist", -8.0, s * 6.0, -s * 14.0)  # the chest curls up off the floor
        p.set("Neck", 0, 0, -s * 36.0)
        lead, trail = (20.0, 0, 0, -40.0), (-6.0, 0, 0, -16.0)
        legs(p, lead if s > 0 else trail, trail if s > 0 else lead)
        empty_arms(p, 90.0, 30.0, 40.0)
    return L.ground(p, floor, LYING)


def on_floor(t, floor=PRONE, slump=0.0, period=2.4):
    """On the back, propped up to shoot between the feet (DodgeGround). `slump` sags it for a Last
    Stand: lower, rolled onto the left elbow, slower and heavier breathing."""
    breath = math.sin(TAU * t / period)
    p = Pose()
    # the torso about 30 degrees off the floor (26 slumped), head up to see over the feet
    p.set("Root", 72.0 + 4.0 * slump, 0, -8.0 * slump)
    p.set("Waist", -14.0 + 4.0 * slump - 1.5 * breath * (1 + slump), 4.0, 6.0 * slump)
    p.set("Neck", -26.0 + 4.0 * slump, 0, 4.0 * slump)
    # right knee up with the foot flat, the left leg out
    p.set("RightHip", 60.0 - 6.0 * slump, -8.0, 6.0)
    p.set("RightKnee", -92.0 + 10.0 * slump, 0, 0)
    p.set("RightAnkle", 22.0, 0, 0)
    p.set("LeftHip", 32.0, 10.0, -12.0 - 6.0 * slump)
    p.set("LeftKnee", -18.0 - 8.0 * slump, 0, 0)
    p.set("LeftAnkle", -12.0, 0, 0)
    # empty hands: propped on the elbows behind
    empty_arms(p, -38.0, 26.0, 70.0, -20.0)
    return L.ground(p, floor, LYING)


def dive_land(direction):
    """The landing (0.45 s): the body hits the floor the way it flew, slides, and rolls round onto its
    back with the feet toward the target (DodgeGround), the way Max Payne 3 keeps shooting from the
    floor. The root part falls about 2.4 studs in the first 0.17 s, so the first key is the flight
    pose and the impact is on the floor."""
    keys = Keys()
    keys.add(0.0, dive_air(direction))
    keys.add(0.15, dive_impact(direction))
    if direction == "Forward":
        keys.add(0.29, dive_impact("Left"))  # rolls onto the left side, legs swinging round
    keys.add(0.45, on_floor(0.0))
    return keys.at


def getting_up(floor=KNEEL):
    """Getting up off the floor (0.6 s, hips 1.2 lower): sit up, feet under, rock forward into a
    crouch, ready to stand."""
    start = on_floor(0.0, floor)
    sit = Pose()
    sit.set("Root", 18.0, 0, 0)
    sit.set("Waist", -18.0, 0, 0)
    sit.set("Neck", -6.0, 0, 0)
    legs(sit, (70.0, -10.0, 8.0, -110.0), (78.0, 10.0, -8.0, -118.0), 10.0)
    empty_arms(sit, -30.0, 22.0, 20.0, -30.0)
    L.ground(sit, floor)
    squat = Pose()
    squat.set("Root", -30.0, 0, 0, move=(0, 0.3, 0.25))
    squat.set("Waist", -22.0, 0, 0)
    squat.set("Neck", 34.0, 0, 0)
    empty_arms(squat, 30.0, 14.0, 40.0)
    for side, sign in SIDES:
        plant(squat, side, sign * 0.62, 0.15 if side == "Left" else -0.05, floor, sign * -10.0, 0, 30.0)
    crouch = Pose()
    crouch.set("Root", -14.0, 0, 0, move=(0, 0.75, 0.05))
    crouch.set("Waist", -18.0, 0, 0)
    crouch.set("Neck", 22.0, 0, 0)
    empty_arms(crouch, 18.0, 10.0, 40.0)
    for side, sign in SIDES:
        plant(crouch, side, sign * 0.62, -0.2 if side == "Left" else 0.3, floor, sign * -10.0, 0, 8.0 if side == "Right" else 0.0)
    keys = Keys()
    keys.add(0.0, start)
    keys.add(0.22, sit)
    keys.add(0.42, squat)
    keys.add(0.6, crouch)
    return keys.at, crouch


# --- Last Stand --------------------------------------------------------------------------------------
def last_stand_fall():
    """Taking the shot that would have killed (0.6 s): the knees go, the body sits down hard and falls
    back onto the floor, where it props up to fire back (LastStand). Made on the floor of the Last
    Stand stance; the aim layer brings the body down to it from standing."""
    stagger = Pose()
    stagger.set("Root", -16.0, 0, 6.0, move=(0, 2.2 - 0.45, 0.1))
    stagger.set("Waist", -24.0, 6.0, 4.0)
    stagger.set("Neck", 26.0, 0, -6.0)
    empty_arms(stagger, 26.0, 26.0, 50.0)
    for side, sign in SIDES:
        plant(stagger, side, sign * 0.55, 0.1 if side == "Right" else -0.15, PRONE, sign * -6.0)
    sitting = Pose()
    sitting.set("Root", 34.0, 0, -6.0)
    sitting.set("Waist", -20.0, 0, 0)
    sitting.set("Neck", -10.0, 0, 0)
    legs(sitting, (64.0, 10.0, -10.0, -70.0), (54.0, -10.0, 10.0, -54.0), 0.0)
    empty_arms(sitting, -20.0, 36.0, 30.0, -20.0)
    L.ground(sitting, PRONE, LYING)
    keys = Keys()
    keys.add(0.0, stagger)
    keys.add(0.24, sitting)
    keys.add(0.6, on_floor(0.0, PRONE, 1.0, 3.2))
    return keys.at


def last_stand_wakeup():
    """Surviving a Last Stand (3 s, hips 1.2 lower, defenseless): roll onto the side, push up onto a
    hand and a knee, kneel, then rise into a crouch, slowly and hurt."""
    lying = on_floor(0.0, KNEEL, 1.0, 3.2)
    side = Pose()
    side.set("Root", 10.0, 0, 84.0)
    side.set("Waist", -16.0, 8.0, -18.0)
    side.set("Neck", 10.0, 0, -30.0)
    legs(side, (60.0, 0, 0, -80.0), (40.0, 0, 0, -60.0), 0.0)
    empty_arms(side, 50.0, 20.0, 90.0)
    L.ground(side, KNEEL)
    palm(side, "Left", -1.6, -0.9, KNEEL, 30.0, V(-1, 0.5, 0.5))  # the bottom hand flat on the floor ahead
    fours = Pose()  # on the left hand and both knees, head hanging
    fours.set("Root", -72.0, 0, 6.0, move=(0, 0, 0.2))
    fours.set("Waist", -6.0, 0, 0)
    fours.set("Neck", -10.0, 0, 0)
    legs(fours, (82.0, 0, -6.0, -100.0), (86.0, 0, 6.0, -104.0), -20.0)
    fours.set("RightShoulder", 50.0, 0, 10.0)
    fours.set("RightElbow", 50.0, 0, 0)
    fours.set("LeftShoulder", 74.0, 0, -8.0)
    L.ground(fours, KNEEL)
    palm(fours, "Left", -0.8, -1.7, KNEEL, 10.0, V(-0.6, 0.2, 1))
    kneel = Pose()  # on the left knee, right foot planted, a hand on the knee
    kneel.set("Root", -10.0, 8.0, 0, move=(0, 0.25, 0.1))
    kneel.set("Waist", -26.0, -6.0, 0)
    kneel.set("Neck", 6.0, 0, 0)
    kneel.set("LeftHip", -6.0, 0, -4.0)
    kneel.set("LeftKnee", -96.0, 0, 0)
    kneel.set("LeftAnkle", -30.0, 0, 0)
    plant(kneel, "Right", 0.55, -0.9, KNEEL, -8.0)
    kneel.set("RightShoulder", 30.0, 0, 6.0)
    kneel.set("RightElbow", 40.0, 0, 0)
    kneel.set("LeftShoulder", 20.0, 0, -10.0)
    kneel.set("LeftElbow", 30.0, 0, 0)
    crouch = getting_up(KNEEL)[1]
    keys = Keys()
    keys.add(0.0, lying)
    keys.add(0.7, side)
    keys.add(1.45, fours)
    keys.add(2.15, kneel)
    keys.add(3.0, crouch)
    return keys.at


# --- Vault -------------------------------------------------------------------------------------------
def vault():
    """Over a low obstacle, a speed vault (made at 0.6 s): drive off the left foot, left hand onto the
    top, the body tipped over it while both legs swing out to the right, tucked, and down running. The
    game flies the root part over (VaultRules.position: up to 2.1 above the top by the near face, level
    across, down after the far face) and paces this clip by the way over, not the clock: the legs are
    up (tucked, 0.15 s, to clear, 0.43 s) from the near face to the far face, where the hips and tucked
    legs hang at most 1.85 below the root part. The gun arm keeps aiming; with a one-handed gun the free
    left hand takes the top."""
    run = M.gait(0.12, dict(M.RUN, direction=V(0, 0, -1)))
    drive = empty_arms(Pose(), 30.0, 16.0, 60.0)
    drive.set("Root", -20.0, 6.0, 10.0, move=(0, -0.1, 0))
    drive.set("Waist", -10.0, -6.0, 6.0)
    drive.set("Neck", 16.0, 0, -4.0)
    legs(drive, (-25.0, 0, -4.0, -30.0), (110.0, 0, 6.0, -130.0), -30.0)  # left pushing off, right knee driving up
    drive.set("LeftShoulder", 60.0, 0, -20.0)
    drive.set("LeftElbow", 30.0, 0, 0)
    tuck = empty_arms(Pose(), 40.0, 30.0, 50.0)  # left hand on the top, knees up, tipping over it
    tuck.set("Root", -12.0, -15.0, 45.5, move=(0.1, 0.05, 0))
    tuck.set("Waist", -12.0, 8.0, -18.2)
    tuck.set("Neck", 12.0, 14.0, -18.0)
    legs(tuck, (110.0, -10.0, 65.0, -135.0), (105.0, -12.0, 70.0, -130.0), -30.0)
    tuck.set("LeftShoulder", 40.0, 0, -36.0)
    tuck.set("LeftElbow", 6.0, 0, 0)
    tuck.set("LeftWrist", 60.0, 0, 0)  # palm flat on the top
    over = empty_arms(Pose(), 50.0, 40.0, 40.0)  # tipped right over the hand, the legs swung out to the right
    over.set("Root", -6.0, -20.0, 65.0, move=(0.2, 0.1, 0))
    over.set("Waist", -6.0, 10.0, -35.75)
    over.set("Neck", 6.0, 20.0, -24.0)
    legs(over, (85.0, -10.0, 75.0, -105.0), (80.0, -10.0, 80.0, -100.0), -25.0)
    over.set("LeftShoulder", 20.0, 0, -30.0)
    over.set("LeftElbow", 4.0, 0, 0)
    over.set("LeftWrist", 50.0, 0, 0)
    clear = over.copy()  # past the far face, the legs still up, coming round under the body
    clear.set("Root", -8.0, -15.0, 45.5, move=(0.1, 0.1, 0))
    clear.set("Waist", -6.0, 8.0, -22.75)
    legs(clear, (80.0, -10.0, 65.0, -105.0), (70.0, -10.0, 70.0, -95.0), -20.0)
    reach = Pose()  # coming down the far side, both feet forward under the body for the floor
    reach.set("Root", -8.0, -6.0, 6.0, move=(0, 0.05, 0))
    reach.set("Waist", -6.0, 4.0, 2.0)
    reach.set("Neck", 10.0, 2.0, -4.0)
    legs(reach, (60.0, 0, -6.0, -45.0), (50.0, 0, 6.0, -30.0), -16.0)
    empty_arms(reach, 40.0, 30.0, 40.0)
    land = Pose()  # down on the right foot first, knees taking it, running on
    land.set("Root", -16.0, 2.0, -2.0, move=(0, -0.28, 0))
    land.set("Waist", -10.0, 0, 0)
    land.set("Neck", 18.0, 0, 0)
    empty_arms(land, 30.0, 18.0, 50.0)
    plant(land, "Right", 0.55, -0.35, L.FLOOR, -6.0)
    plant(land, "Left", -0.6, 0.45, L.FLOOR, 6.0, 0, 30.0)
    keys = Keys()
    for t, pose in ((0.0, run), (0.06, drive), (0.15, tuck), (0.3, over), (0.43, clear), (0.52, reach), (0.6, land)):
        keys.add(t, pose)
    return keys.at


# --- Cover -------------------------------------------------------------------------------------------
# Max Payne 3's cover, side-on: the back and the inner shoulder against the wall, turned toward the edge
# being worked, the head looking along the wall to it, the gun low or upright in front (Steam trailers:
# "Design and Tech Video 2" 2:53-2:58, "Multiplayer" 1:35-1:43). Along the wall the body runs side-on,
# facing the way it goes. The game keeps the root part facing the wall (CoverController) and keeps the gap
# the body's reach toward the wall needs, so these clips turn the body round inside the root part and
# lean its back onto the wall: no gameplay code depends on which way the body faces.
HIGH_TURN = 150.0  # degrees the body is turned from facing the wall (180: flat against it)
LOW_TURN = 180.0  # folded over the knees, the body faces straight out so the head stays behind the wall's end
# How far the back reaches toward the wall from the root part. The game keeps the root part GAP (1.15)
# off the wall, or what the body's reach needs plus 0.05 (CoverController), so at 1.1 the back rests on
# the wall.
BACK_REACH = 1.1
# The root part stops 0.9 short of a wall's end (CoverRules.EDGE_MARGIN; 0.82 to 0.85 measured), and an
# R15's shoulders and the arm on the edge's side reach 1.3 to 1.8 along the wall. The idles sit back
# along the wall, away from the edge, so less of the body shows past the end: 0.5 past it there, centred
# on the root part (83tg's avatar, 2026-11-07). Any further, and the gun arm can't reach round the end to
# blind fire working right (it is the arm away from the edge, back to the wall).
HIGH_BACK = 0.35
LOW_BACK = 0.75
TORSO = ("Head", "UpperTorso", "LowerTorso")
UPPER_ARMS = ("LeftUpperArm", "RightUpperArm")  # CoverController counts them too (below the cover's top)


def facing(side, turn):
    """The body's yaw for a side: `turn` degrees round from the wall, toward the edge being worked."""
    return -(1.0 if side == "Right" else -1.0) * turn


def turned(yaw, x, z, shift=(0.0, 0.0)):
    """A point (x, z) in the turned body's own frame (facing -Z) in the root part's space, plus `shift`."""
    v = rot(0, yaw, 0) @ V(x, 0, z)
    return v.x + shift[0], v.z + shift[1]


def plant_turned(pose, side, yaw, x, z, floor, toe_out=0.0, toe=0.0, heel=0.0, shift=(0.0, 0.0)):
    """A foot planted at (x, z) in the turned body's frame, toes along the body plus `toe_out`."""
    px, pz = turned(yaw, x, z, shift)
    plant(pose, side, px, pz, floor, yaw + toe_out, toe, heel, rot(0, yaw, 0) @ V(x * 0.4, 0, -1))
    return pose


def look(pose, direction, joint="Neck"):
    """Turns a joint so its part faces `direction` (root part's space), kept upright. On a body folded
    over its knees a neck yaw rolls the head instead of turning it, so the head is aimed instead."""
    _, parent, part, _, _ = L.JOINT[joint]
    above = L.solve(pose)[parent].to_quaternion()
    forward = direction.normalized()
    right = forward.cross(V(0, 1, 0)).normalized()
    up = right.cross(forward)
    aim = Matrix((right, up, -forward)).transposed().to_quaternion()
    pose[joint] = (above.inverted() @ aim, pose.t(joint))
    return pose


def reach(pose, parts=TORSO):
    """How far the parts reach toward the wall (-Z) from the root part, as CoverController measures it."""
    world = L.solve(pose)
    return max(-(world[part] @ V(x * L.PARTS[part][0][0] / 2, y * L.PARTS[part][0][1] / 2, z * L.PARTS[part][0][2] / 2)).z
               for part in parts for x in (-1, 1) for y in (-1, 1) for z in (-1, 1))


def onto_wall(pose, parts=TORSO + UPPER_ARMS):
    """Moves the body along the root part's Z until the parts reach BACK_REACH toward the wall (-Z), and
    returns the move (studs) so the feet can be planted with it."""
    move = reach(pose, parts) - BACK_REACH
    pose.move("Root", 0, 0, move)
    return move


def cover_high(side):
    """High cover: back and inner shoulder on the wall, turned toward the edge, knees soft, the feet out
    from the wall so the weight rests back on it, the inner arm forward off the wall, the head turned
    along the wall to the edge. A slow breath and a shift of weight."""
    s = 1.0 if side == "Right" else -1.0
    yaw = facing(side, HIGH_TURN)
    lead, trail = ("Left", "Right") if s > 0 else ("Right", "Left")  # the foot on the edge's side leads

    def pose(t):
        breath = math.sin(TAU * t / 3.2)
        shift = math.sin(TAU * t / 6.4)
        p = Pose()
        hips = turned(yaw, s * 0.03 * shift, 0.0)
        x = hips[0] - s * HIGH_BACK
        p.set("Root", 5.0, yaw, s * 1.5 * shift, move=(x, -0.16 + 0.01 * breath, hips[1]))
        p.set("Waist", -4.0 - breath, s * 8.0, -s * 1.5)
        p.set("Neck", 2.0, s * (38.0 + 3.0 * shift), -s * 3.0)
        empty_arms(p, 10.0, 6.0, 24.0)
        p.set(lead + "Shoulder", 16.0, 0, -s * 4.0)  # the inner arm a little forward, off the wall
        p.set(lead + "Elbow", 30.0, 0, 0)
        z = onto_wall(p)
        plant_turned(p, lead, yaw, -s * 0.52, -0.45, L.FLOOR, s * 12.0, shift=(x, z))
        plant_turned(p, trail, yaw, s * 0.62, -0.28, L.FLOOR, -s * 8.0, shift=(x, z))
        return p
    return pose


def cover_low(side):
    """Low cover (hips 1.8 lower): down on the balls of the feet with the back against the wall, folded
    over the knees to keep the head top under 3 studs (the lowest cover), the head turned along the wall
    to the edge. An R15's head and torso are long for its legs, so only a deep fold gets the head that
    low; folded straight out from the wall, the head stays behind the wall's end."""
    s = 1.0 if side == "Right" else -1.0
    yaw = facing(side, LOW_TURN)
    lead, trail = ("Left", "Right") if s > 0 else ("Right", "Left")

    def pose(t):
        breath = math.sin(TAU * t / 2.6)
        shift = math.sin(TAU * t / 5.2)
        p = Pose()
        x = -s * LOW_BACK + s * 0.02 * shift  # back along the wall, away from the edge
        p.set("Root", -30.0, yaw, s * 1.5 * shift, move=(x, 0.4 + 0.01 * breath, 0))
        p.set("Waist", -46.0 - breath, s * 8.0, 0)
        look(p, V(s * 0.93, -0.12, 0.34))  # along the wall to the edge
        z = onto_wall(p, TORSO)  # the legs and arms aren't placed yet

        def feet():
            plant_turned(p, lead, yaw, -s * 0.58, -0.55, LOW, s * 12.0, 0, 20.0, (x, z))
            plant_turned(p, trail, yaw, s * 0.6, -0.4, LOW, -s * 8.0, 0, 14.0, (x, z))
        feet()
        # squatting, the backs of the thighs come out behind the hips: off the wall too
        extra = reach(p, TORSO + ("LeftUpperLeg", "RightUpperLeg")) - BACK_REACH
        if extra > 0:
            p.move("Root", 0, 0, extra)
            z += extra
            feet()
        # empty hands resting on the knees
        world = L.solve(p)
        for hand in ("Left", "Right"):
            knee = world[hand + "LowerLeg"] @ V(0, 0.55, -0.35)
            palm(p, hand, knee.x, knee.z, knee.y - 0.16, yaw, V(0.25 if hand == "Left" else -0.25, -1, 0.3))
        return p
    return pose


def cover_move(height, side):
    """Moving along the wall side-on, facing the way it goes, the inner shoulder by the wall: a hunched
    jog behind high cover (9.6 studs/s), a crouched run behind low cover (8 studs/s) folded far enough
    to keep the head under the top. The chest opens a little to the open side and the head looks
    ahead along the wall."""
    s = 1.0 if side == "Right" else -1.0
    if height == "High":
        g = dict(M.JOG)
        g.update({"speed": 9.6, "cycle": 0.56, "duty": 0.4, "pelvis": -0.42, "bob": 0.06, "lean": 12.0,
                  "hip_lean": 6.0, "hip_turn": 90.0, "counter": 0.0, "side_lean": 0.0, "arm_swing": 14.0,
                  "arm_carry": 14.0, "elbow": 60.0, "lift": 0.34, "width": 0.95, "toe_out": 4.0})
    else:
        # the waist takes most of the fold: folded at the hips, the trailing shin went through the floor
        g = dict(M.CROUCH_WALK)
        g.update({"speed": 8.0, "cycle": 0.56, "duty": 0.55, "hip_lean": 28.0, "lean": 58.0, "hip_turn": 90.0,
                  "counter": 0.0, "side_lean": 0.0, "pelvis": 0.74, "width": 1.1, "lift": 0.2, "toe_out": 4.0,
                  "arm_swing": 8.0, "arm_carry": 50.0, "elbow": 80.0})
    g["direction"] = V(s, 0, 0)
    open_ = -s * 10.0  # the chest turned a little out from the wall

    def run(t):
        p = M.gait(t, g)
        p.turn("Waist", rot(0, open_, 0))
        # the gait turns the head back to the root part's front (the wall): it looks ahead instead
        p.set("Neck", 10.0 if height == "High" else 54.0, -open_ * 0.6, 0)
        return p

    # One shift for the whole cycle (a changing one would slide the feet): the inner shoulder and arm
    # come no nearer the wall than the idle's back, so the game holds the gap the idle needed, and the
    # body sits back along the way it goes, so the head leads the root part by no more than 0.8 (high) or
    # 1 (low). The root stops 0.9 short of a wall's end, and the head leading further poked past it while
    # the run blended into the idle (0.64 past, leading by 1.5).
    cycle = [run(g["cycle"] * i / 8) for i in range(8)]
    out = max(reach(p, TORSO + UPPER_ARMS) for p in cycle) - BACK_REACH
    half = V(*L.PARTS["Head"][0]) / 2
    lead = max(s * (L.solve(p)["Head"] @ V(x * half.x, y * half.y, z * half.z)).x
               for p in cycle for x in (-1, 1) for y in (-1, 1) for z in (-1, 1))
    back = -s * max(lead - (0.8 if height == "High" else 1.0), 0.0)

    def pose(t):
        return run(t).move("Root", back, 0, out)
    return pose, g


def cover_corner(height, side):
    """Round an outside corner (0.35 s): the game swings the root part round the end of the wall and
    turns its facing with it. The clip starts and ends on the cover idle at rest, so it blends in and
    out without a jump; between, the body takes a side-on stride round the corner, as it would moving
    along the wall."""
    high = height == "High"
    rest = (cover_high if high else cover_low)(side)(0.0)
    move, g = cover_move(height, side)
    mid = move(g["cycle"] * 0.3)  # mid-stride, the leading foot reaching round
    keys = Keys()
    keys.add(0.0, rest)
    keys.add(0.175, mid)
    keys.add(0.35, rest.copy())
    return keys.at


AIM_YAW, AIM_PITCH = 14.0, -4.0  # cover_aim's Root
# x, z, yaw, heel. The back heel is up: flatter, the shin leant over the foot and its box went 0.12 into
# the floor (2026-11-08).
AIM_FEET = {"Left": (-0.7, -0.45, 14.0, 0.0), "Right": (0.7, 0.45, -18.0, 22.0)}


def cover_aim(t):
    """Aiming out of cover (popped round high cover, or up over low cover): a braced stance, feet
    wide, knees soft, weight forward. The aim clip and the aim layer do the arms and the chest."""
    breath = math.sin(TAU * t / 2.8)
    p = Pose()
    p.set("Root", AIM_PITCH, AIM_YAW, 0, move=(0, -0.22 + 0.01 * breath, 0.05))
    p.set("Waist", -6.0 - breath, -10.0, 0)
    p.set("Neck", 6.0, -4.0, 0)
    empty_arms(p, 20.0, 12.0, 40.0)
    for side, (x, z, yaw, heel) in AIM_FEET.items():
        plant(p, side, x, z, L.FLOOR, yaw, 0, heel)
    return p


# --- Popping up out of low cover and ducking back ----------------------------------------------------
# The low idle faces out from the wall and the aim faces over it, so a blend between them turned the body
# about 166° in a fifth of a second, the feet swinging round with the hips through the wall's base (0.43
# deep, 2026-11-07). These clips take the turn: the body rises (or sinks) turning toward the edge the head
# was looking at, the feet stepping round outside the wall. The game changes the hip height at once and
# AimLayer holds the body where it was, easing it to the new height at HEIGHT_EASE; the feet are planted
# where that hold leaves the floor, so they stay on it. The game plays them in real time, as the hold eases.
POP_TIME = 0.25  # the CoverPeek stance (PEEK_TIME), bound to it
DUCK_TIME = 0.3
HEIGHT_EASE = 10.0  # AimLayer's rate, per second
LOW_DROP = 1.8  # low cover's hip drop (StanceRules)
LOW_PITCH = -30.0  # cover_low's Root
LOW_FEET_HEEL = (20.0, 14.0)  # cover_low's heels: lead, trail
TURN_SWAY = 0.6  # studs the hips sway out from the wall at the middle of the turn
KNEE_FOLLOWS_FOOT = 0.75  # how much of its turn a knee takes with its foot's step; the rest with the hips
DUCK_DROP = (0.2, 1.0)  # the share of the duck the hips go down over: the feet start round first
DUCK_FOLD = (0.0, 0.7)  # and the body folds over
STEP_LIFT = (0.3, 0.12)  # studs a stepping foot comes up: popping up, ducking
# The legs are kept off the wall: it is 1.15 from the root part (CoverController's least gap). The aim's
# knees reach 1.03 to 1.06 (the default R15's boxes), so where the pop-up ends, still 0.15 low, they
# touch it; turning them out any further twisted the legs 58 degrees from the aim they hand over to.
LEG_REACH = 1.15


def sole_spot(pose, side):
    """A planted foot's sole middle (x, z) and which way its toes point (yaw, degrees), from a pose."""
    world = L.solve(pose)
    point = L.sole(world, side)
    toes = world[side + "Foot"].to_3x3() @ V(0, 0, -1)
    return point.x, point.z, math.degrees(math.atan2(-toes.x, -toes.z))


def knee_spot(pose, side):
    """Which way a leg's knee bends in a pose: its pivot's direction off the hip-ankle line (root part's
    space), and that direction's yaw (degrees)."""
    world = L.solve(pose)
    hip, knee, ankle = (L.pivot(world, side + joint) for joint in ("Hip", "Knee", "Ankle"))
    line = (ankle - hip).normalized()
    off = ((knee - hip) - line * (knee - hip).dot(line)).normalized()
    return off, math.degrees(math.atan2(-off.x, -off.z))


def wrap(angle):
    """An angle in degrees, wrapped to -180..180."""
    return (angle + 180.0) % 360.0 - 180.0


# A one-handed gun holstered on the left thigh (LoadoutRules), as a box in the LeftUpperLeg's frame: the
# Uzi's, measured in the game (2026-11-08). It hangs past the knee, so a thigh raised toward the wall
# puts it in the wall.
HOLSTER = (V(-0.504, -0.117, 0.022), V(0.177, 1.70, 1.026))


def leg_reach(pose, side):
    """How far a leg's boxes (and on the left the holstered gun) reach toward the wall (-Z) from the
    root part."""
    world = L.solve(pose)
    boxes = [(world[side + part], V(), V(*L.PARTS[side + part][0])) for part in ("UpperLeg", "LowerLeg")]
    if side == "Left":
        boxes.append((world["LeftUpperLeg"],) + HOLSTER)
    return max(-(m @ (centre + V(x * size.x / 2, y * size.y / 2, z * size.z / 2))).z
               for m, centre, size in boxes for x in (-1, 1) for y in (-1, 1) for z in (-1, 1))


def cover_turn(side, up):
    """Popping up out of low cover to aim (`up`, CoverPopUp), or ducking back into it (CoverDuck). The
    body turns toward the edge being worked: working right from facing out (yaw -180) up through facing
    the edge (-90) to the aim (14); working left from 180 down through 90.
    Turned side-on, the torso is as wide toward the wall as it is across, so popping up the body leaves
    the wall before it turns (it went 0.47 into it turning in place), and ducking it turns before it
    settles back against the wall, folding over as it turns and going down once the feet are round
    (folded while still facing the wall, the knees went into it). The foot on the turn's outside steps
    round first. The knees turn with the feet, and out from the wall where they (or a holstered gun)
    would reach it."""
    s = 1.0 if side == "Right" else -1.0
    lead, trail = ("Left", "Right") if s > 0 else ("Right", "Left")
    low, aim = cover_low(side)(0.0), cover_aim(0.0)
    first, last = (low, aim) if up else (aim, low)
    length = POP_TIME if up else DUCK_TIME
    yaw_low = facing(side, LOW_TURN)
    yaws = (yaw_low, AIM_YAW) if up else (AIM_YAW, yaw_low)
    pitches = (LOW_PITCH, AIM_PITCH) if up else (AIM_PITCH, LOW_PITCH)
    heels_low = {lead: LOW_FEET_HEEL[0], trail: LOW_FEET_HEEL[1]}
    # (start, end) shares of the clip for each part of the move
    spans = {
        "turn": (0.0, 1.0) if up else (0.0, 0.55),
        "off_wall": (0.0, 0.55) if up else (0.45, 1.0),  # the hips along and away from the wall
        "chest": (0.0, 1.0) if up else DUCK_FOLD,  # the waist, neck, arms and the body's lean
        trail: (0.05, 0.5) if up else (0.15, 0.45),
        lead: (0.4, 0.9) if up else (0.0, 0.3),
        "drop": DUCK_DROP,  # ducking, the hips down to the floor
    }
    lift = STEP_LIFT[0] if up else STEP_LIFT[1]
    feet = {}
    for foot in ("Left", "Right"):
        a, b = sole_spot(first, foot), sole_spot(last, foot)
        turn = yaws[1] - yaws[0]
        toe_b = a[2] + turn + wrap(b[2] - (a[2] + turn))  # the toes turn with the body
        # The knee turns with the toes too, from the bend it has in the pose the clip starts on to the
        # one it ends on. Bent the way the body faced (away from the wall), it bent backward over the
        # feet once they had stepped round, and the legs ended 100 to 146 degrees twisted from the aim.
        bend_a, yaw_a = knee_spot(first, foot)
        bend_b, yaw_b = knee_spot(last, foot)
        knee_turn = (toe_b - a[2]) + wrap(yaw_b - (yaw_a + toe_b - a[2]))
        bend_b = rot(0, -knee_turn, 0) @ bend_b  # turned back to the start, to blend with it
        heels = (heels_low[foot], AIM_FEET[foot][3]) if up else (AIM_FEET[foot][3], heels_low[foot])
        feet[foot] = (a, b, toe_b, heels, bend_a, bend_b, knee_turn)

    def share(u, part):
        start, end = spans[part]
        return L.smoother((u - start) / (end - start))

    def floor(t):
        # where the floor is in the clip while AimLayer holds the body: below it popping up, above ducking
        held = LOW_DROP * math.exp(-HEIGHT_EASE * t)
        return L.FLOOR + held if up else LOW - held

    def pose(t):
        u = min(max(t / length, 0.0), 1.0)
        p = L.blend(first, last, share(u, "chest"), {"Waist", "Neck"} | L.ARMS)
        e = share(u, "turn")
        yaw = yaws[0] + (yaws[1] - yaws[0]) * e
        a, b = first.t("Root"), last.t("Root")
        off = share(u, "off_wall")
        if up:
            y = a.y + (b.y - a.y) * L.smoother(u)
        else:
            # Ducking, the hips' height over the floor follows DUCK_DROP whatever AimLayer's hold does (the
            # root takes back what the hold has eased so far). Left to the hold, they dropped half way in
            # 0.06 s, with the feet still stepping: the knees folded forward over them, the shins nearly
            # flat (0.3 into the floor), and the front knee into the wall.
            eased, total = floor(t) - floor(0.0), floor(length) - floor(0.0)
            y = a.y + (b.y - a.y - total) * share(u, "drop") + eased
        # half-turned the chest's width faces the wall: the hips sway out from it through the turn
        sway = TURN_SWAY * math.sin(math.pi * e)
        move = (a.x + (b.x - a.x) * off, y, a.z + (b.z - a.z) * off + sway)
        p.set("Root", pitches[0] + (pitches[1] - pitches[0]) * share(u, "chest"), yaw, 0, move=move)
        for foot, (fa, fb, toe_b, heels, bend_a, bend_b, knee_turn) in feet.items():
            v = share(u, foot)
            x, z = fa[0] + (fb[0] - fa[0]) * v, fa[1] + (fb[1] - fa[1]) * v
            height = floor(t) + lift * math.sin(math.pi * v)
            sole, r = L.foot_on_floor(x, z, height, fa[2] + (toe_b - fa[2]) * v, 0.0, heels[0] + (heels[1] - heels[0]) * v)
            # mostly with the foot (a shin hardly twists on it), a little with the hips
            k = KNEE_FOLLOWS_FOOT * v + (1.0 - KNEE_FOLLOWS_FOOT) * e
            knee = rot(0, knee_turn * k, 0) @ bend_a.lerp(bend_b, k)
            L.leg_ik(p, foot, sole, r, knee)
            # Over the toes, the knee of a foot near the wall reached 0.17 past its face (the front foot of
            # the aim is 0.2 from it): turn it out from the wall, no more than it needs.
            if leg_reach(p, foot) > LEG_REACH:
                lo, hi = 0.0, 4.0
                for _ in range(10):
                    mid = (lo + hi) / 2
                    L.leg_ik(p, foot, sole, r, knee + V(0, 0, mid))
                    lo, hi = (mid, hi) if leg_reach(p, foot) > LEG_REACH else (lo, mid)
                L.leg_ik(p, foot, sole, r, knee + V(0, 0, hi))
        return p
    return pose


# --- Landing roll (replaces mp_locomotion's) ---------------------------------------------------------
def land_roll(t):
    """A hard landing while moving (0.8 s): drop into a forward shoulder roll and come up running.
    The root part doesn't turn (Roblox moves it), so the body rolls round it; during the roll its
    lowest point rides exactly on the floor, so nothing sinks."""
    length = 0.8
    u = t / length
    p = Pose()
    roll = smooth((u - 0.12) / 0.62)  # one full turn forward
    tuck = math.sin(math.pi * min(max((u - 0.05) / 0.85, 0.0), 1.0))
    p.set("Root", -360.0 * roll, 6.0 * tuck, 0)
    p.set("Waist", -45.0 * tuck, 0, 8.0 * tuck)
    p.set("Neck", -40.0 * tuck, 0, 0)
    for side, sign in SIDES:
        p.set(side + "Shoulder", 60.0 * tuck + 10.0, 0, sign * (14.0 + 10.0 * tuck))
        p.set(side + "Elbow", 70.0 * tuck + 20.0, 0, 0)
        p.set(side + "Hip", 95.0 * tuck, 0, sign * 6.0)
        p.set(side + "Knee", -125.0 * tuck, 0, 0)
        p.set(side + "Ankle", 20.0 * tuck, 0, 0)
    L.ground(p, L.FLOOR)
    if u < 0.12 or u > 0.86:  # before and after the roll the feet are on the floor
        w = 1 - smooth(u / 0.12) if u < 0.12 else smooth((u - 0.86) / 0.14)
        planted = p.copy()
        planted.set("Root", -10.0 * (1 - w), 0, 0, move=(0, -0.3 * (1 - w), 0))
        for side, x in (("Left", -0.6), ("Right", 0.6)):
            plant(planted, side, x, 0.0, L.FLOOR)
        p = L.blend(p, planted, w)
    return p


def guarded(fn, floor, after=0.0):
    """A clip whose hands and feet are kept out of the floor (from `after` seconds on)."""
    return lambda t: fn(t) if t < after else L.floor_guard(fn(t), floor)


def register():
    for d in ("Forward", "Back", "Left", "Right"):
        Clip("DodgePrep" + d, 0.2, guarded(dive_prep(d), PREP), drop=0.6)
        Clip("DodgeAir" + d, 1.0, (lambda dd: lambda t: dive_air(dd, t))(d), loop=True, note="flight")
        # the first 0.15 s is still above the floor: the root part is falling onto it
        Clip("DodgeLand" + d, 0.45, guarded(dive_land(d), PRONE + LYING, 0.15), drop=2.2, note="lands from the flight pose")
    Clip("DodgeGround", 2.4, guarded(on_floor, PRONE + LYING), loop=True, drop=2.2)
    Clip("GettingUp", 0.6, guarded(getting_up()[0], KNEEL + LYING), drop=1.2)
    Clip("LastStandFall", 0.6, guarded(last_stand_fall(), PRONE + LYING), drop=2.2)
    Clip("LastStand", 3.2, guarded(lambda t: on_floor(t, PRONE, 1.0, 3.2), PRONE + LYING), loop=True, drop=2.2)
    Clip("LastStandWakeup", 3.0, guarded(last_stand_wakeup(), KNEEL + LYING), drop=1.2)
    Clip("Vault", 0.6, vault(), note="stretched to the vault's length")
    for side in ("Left", "Right"):
        Clip("CoverHigh" + side, 6.4, cover_high(side), loop=True)
        Clip("CoverLow" + side, 5.2, guarded(cover_low(side), LOW), loop=True, drop=1.8)
        high, g = cover_move("High", side)
        Clip("CoverHighMove" + side, g["cycle"], high, loop=True, note="9.6 studs/s")
        low, g = cover_move("Low", side)
        Clip("CoverLowMove" + side, g["cycle"], guarded(low, LOW), loop=True, drop=1.8, note="8 studs/s")
        Clip("CoverCornerHigh" + side, 0.35, guarded(cover_corner("High", side), L.FLOOR))
        Clip("CoverCornerLow" + side, 0.35, guarded(cover_corner("Low", side), LOW), drop=1.8)
        # made for AimLayer's height hold (see cover_turn): no floor guard, the floor moves. A half turn in
        # a quarter second: sampled at the game's frame rate, not interpolated from 30.
        pop = Clip("CoverPopUp" + side, POP_TIME, cover_turn(side, True), fps=60, note="real time; plays bound to CoverPeek")
        duck = Clip("CoverDuck" + side, DUCK_TIME, cover_turn(side, False), drop=1.8, fps=60, note="real time")
        # Self-check: each turn starts on the legs of the pose it leaves (a twisted start shows as a spin).
        for clip, start in ((pop, cover_low(side)(0.0)), (duck, cover_aim(0.0))):
            begin = clip.pose(0.0)
            for joint in L.LEGS:
                angle = math.degrees(begin.q(joint).rotation_difference(start.q(joint)).angle)
                angle = min(angle, 360.0 - angle)
                assert angle < 5.0, "%s starts %.0f degrees off at %s" % (clip.name, angle, joint)
    Clip("CoverAim", 2.8, cover_aim, loop=True)
    Clip("LandRoll", 0.8, guarded(land_roll, L.FLOOR))
