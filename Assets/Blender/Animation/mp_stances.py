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
def cover_high(side):
    """High cover (facing the wall, 1.15 studs off it): tall and tight, turned toward the edge being
    worked, inside shoulder to the wall, head on the edge."""
    s = 1.0 if side == "Right" else -1.0

    def pose(t):
        breath = math.sin(TAU * t / 3.2)
        shift = math.sin(TAU * t / 6.4)
        p = Pose()
        p.set("Root", -2.0, -s * 34.0, s * 2.0 * shift, move=(s * 0.05 * shift, -0.12 + 0.01 * breath, 0.15))
        p.set("Waist", -4.0 - breath, -s * 6.0, -s * 4.0)  # leaning the inside shoulder in
        p.set("Neck", 2.0, -s * 26.0 + s * 3.0 * shift, 0)
        empty_arms(p, 30.0, 10.0, 70.0)
        plant(p, "Right" if s > 0 else "Left", s * 0.75, -0.45, L.FLOOR, -s * 40.0)  # outside foot toward the edge
        plant(p, "Left" if s > 0 else "Right", -s * 0.45, 0.35, L.FLOOR, -s * 20.0)
        return p
    return pose


def cover_low(side):
    """Low cover (hips 1.8 lower): down on the balls of the feet behind it, head under the top (the
    lowest cover is 3 studs), turned a little toward the edge being worked. An R15 has to hunch far
    over to keep its head that low, so the head reaches about 2.8 studs ahead of the root part, to
    the wall (side-on, it would stick out past the wall's ends instead)."""
    s = 1.0 if side == "Right" else -1.0

    def pose(t):
        breath = math.sin(TAU * t / 2.6)
        shift = math.sin(TAU * t / 5.2)
        p = Pose()
        # head top about 2.8 studs off the floor: under the lowest cover (3 studs)
        p.set("Root", -32.0, -s * 18.0, s * 2.0 * shift, move=(s * 0.03 * shift, 0.7 + 0.01 * breath, 0.15))
        p.set("Waist", -46.0 - breath, -s * 6.0, 0)
        p.set("Neck", 56.0, -s * 18.0, 0)
        empty_arms(p, 50.0, 12.0, 90.0)
        plant(p, "Right" if s > 0 else "Left", s * 0.7, -0.35, LOW, -s * 24.0, 0, 18.0)
        plant(p, "Left" if s > 0 else "Right", -s * 0.55, 0.45, LOW, -s * 10.0, 0, 10.0)
        return p
    return pose


def cover_move(height, side):
    """Shuffling along the wall, still facing it: high cover 9.6 studs/s upright, low cover 8 studs/s
    crouched with the head kept under the top. Short side steps that never cross."""
    s = 1.0 if side == "Right" else -1.0
    if height == "High":
        g = {
            "speed": 9.6, "cycle": 0.56, "duty": 0.5, "pelvis": -0.2, "bob": 0.05, "walk": True, "twist": 3.0,
            "roll": 3.0, "lean": 4.0, "hip_lean": 2.0, "hip_turn": 0.0, "side_lean": 2.0, "counter": 0.9,
            "arm_swing": 6.0, "arm_carry": 26.0, "elbow": 60.0, "arm_out": 10.0, "width": 1.0, "lift": 0.24,
            "strike": 4.0, "push": 10.0, "trail": 10.0, "sway": 0.04, "bob_nod": 0.5, "toe_out": 0.0,
        }
    else:
        g = dict(M.CROUCH_WALK)
        g.update({"speed": 8.0, "cycle": 0.56, "duty": 0.55, "hip_lean": 30.0, "hip_turn": 0.0, "pelvis": 0.76,
                  "width": 1.15, "lift": 0.18, "toe_out": 0.0, "arm_swing": 4.0, "arm_carry": 46.0, "elbow": 90.0})
    g["direction"] = V(s, 0, 0)

    def pose(t):
        p = M.gait(t, g)
        if height == "High":
            p.set("Waist", -4.0, -s * 8.0, 0)
            p.set("Neck", 2.0, -s * 30.0, 0)
        else:
            p.set("Waist", -46.0, -s * 6.0, 0)
            p.set("Neck", 56.0, -s * 22.0, 0)
        return p
    return pose, g


def cover_corner(height, side):
    """Round an outside corner (0.35 s): the game swings the root part round the end of the wall
    and turns its facing with it. The clip starts and ends on the cover idle at rest, so it blends in
    and out without a jump. Between, the body squares up to the turn and the trailing foot comes
    across (high: crossing in front of the leading one; crouched: only closing up)."""
    s = 1.0 if side == "Right" else -1.0
    high = height == "High"
    rest = (cover_high if high else cover_low)(side)(0.0)
    lead, trail = ("Right", "Left") if s > 0 else ("Left", "Right")
    mid = rest.copy()
    if high:
        mid.set("Root", -4.0, -s * 10.0, -s * 6.0, move=(0, -0.15, 0.1))
        mid.set("Waist", -6.0, -s * 10.0, 0)
        mid.set("Neck", 6.0, -s * 20.0, 0)
        plant(mid, lead, s * 0.54, -0.1, L.FLOOR, -s * 20.0)
        sole, r = L.foot_on_floor(s * 0.54, -0.28, L.FLOOR + 0.24, -s * 25.0)
        L.leg_ik(mid, trail, sole, r, V(s * 0.3, 0, -1))
    else:
        mid.set("Root", -32.0, -s * 8.0, -s * 4.0, move=(0, 0.7, 0.15))
        plant(mid, lead, s * 0.54, -0.1, LOW, -s * 20.0, 0, 18.0)
        sole, r = L.foot_on_floor(s * 0.1, 0.0, LOW + 0.16, -s * 25.0)
        L.leg_ik(mid, trail, sole, r, V(s * 0.3, 0, -1))
    keys = Keys()
    keys.add(0.0, rest)
    keys.add(0.175, mid)
    keys.add(0.35, rest.copy())
    return keys.at


def cover_aim(t):
    """Aiming out of cover (popped round high cover, or up over low cover): a braced stance, feet
    wide, knees soft, weight forward. The aim clip and the aim layer do the arms and the chest."""
    breath = math.sin(TAU * t / 2.8)
    p = Pose()
    p.set("Root", -4.0, 14.0, 0, move=(0, -0.22 + 0.01 * breath, 0.05))
    p.set("Waist", -6.0 - breath, -10.0, 0)
    p.set("Neck", 6.0, -4.0, 0)
    empty_arms(p, 20.0, 12.0, 40.0)
    plant(p, "Left", -0.7, -0.45, L.FLOOR, 14.0)
    plant(p, "Right", 0.7, 0.45, L.FLOOR, -18.0, 0, 6.0)
    return p


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
    Clip("CoverAim", 2.8, cover_aim, loop=True)
    Clip("LandRoll", 0.8, guarded(land_roll, L.FLOOR))
