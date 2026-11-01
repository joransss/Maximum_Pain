"""Maximum Pain - locomotion clips: idle, run, jog, sprint, crouch, limp, hobble, jump, fall, land.

Movement in Roblox is fast for an R15 leg (16 studs/s running with a leg under 2 studs long), so the
cycles use a quick cadence, short ground contact and a lowered, slightly hunched body: the feet stay
planted for the whole contact (no sliding) and the body reads heavy and grounded, like Max Payne 3's.
Every directional set shares one cycle so the game can blend directions in step (left foot strikes at
phase 0, right foot at 0.5). The game plays each clip at speed / authored speed.
"""
import math

from mathutils import Vector

import mp_lib as L
from mp_lib import Clip, Pose, V, rot, smooth, wave

TAU = 2 * math.pi
DIRECTIONS = {
    "Forward": V(0, 0, -1),
    "Back": V(0, 0, 1),
    "Left": V(-1, 0, 0),
    "Right": V(1, 0, 0),
}


def gait(t, g):
    """One frame of a gait. `g` holds the gait's numbers (see the sets below)."""
    cycle, duty = g["cycle"], g["duty"]
    direction = g["direction"]
    backward = direction.z > 0.5
    strafe = abs(direction.x) > 0.5
    hip_turn = g.get("hip_turn", 0.0) * (-direction.x if strafe else 0.0)  # toward the travel side
    phase_left = (t / cycle) % 1.0
    pose = Pose()

    # Pelvis: two bobs per cycle (lowest at mid-stance for a run), sway toward the planted foot,
    # yaw following the legs, roll dropping the swing-side hip.
    mid = duty / 2
    beat = math.cos(TAU * 2 * (phase_left - mid))
    bob = g["bob"] * (beat if g.get("walk") else -beat)
    sway = g.get("sway", 0.0) * math.cos(TAU * (phase_left - mid))
    twist = g["twist"] * math.cos(TAU * phase_left)
    pelvis_yaw = hip_turn - twist if not backward else hip_turn + twist
    roll = g.get("roll", 0.0) * math.cos(TAU * (phase_left - mid))
    pose.set("Root", -g.get("hip_lean", 0.0), pelvis_yaw, roll, move=(-sway, g["pelvis"] + bob, g.get("pelvis_z", 0.0)))

    # Spine: lean into the run, chest turned back to face the aim, a little counter-swing.
    lean = g["lean"] * (g.get("back_lean", -0.4) if backward else 1.0)
    side_lean = g.get("side_lean", 0.0) * (direction.x if strafe else 0.0)
    pose.set("Waist", -lean, -pelvis_yaw * g.get("counter", 0.85) + twist * 0.35, side_lean - roll * 0.6)
    # Head stays level and on the aim: it undoes what the spine and pelvis left.
    neck_pitch = lean * 0.55 + g.get("hip_lean", 0.0) * 0.6 - g.get("bob_nod", 0.0) * beat
    neck_yaw = -(pelvis_yaw + pose.q("Waist").to_euler("YXZ").y * 180 / math.pi) * 0.9
    pose.set("Neck", neck_pitch, neck_yaw, -side_lean * 0.5)

    # Arms: opposite to the legs, elbows bent, a touch of follow-through (phase lag).
    lag = g.get("arm_lag", 0.04)
    swing = math.cos(TAU * (phase_left - lag))
    for side, sign in (("Left", -1.0), ("Right", 1.0)):
        forward = sign * swing
        if backward:
            forward = -forward
        shoulder = g["arm_swing"] * forward + g.get("arm_carry", 10.0)
        out = (4 + g.get("arm_out", 6.0) * (0.5 + 0.5 * abs(forward))) * (1 if side == "Right" else -1)
        across = g.get("arm_across", 0.0) * max(forward, 0.0) * (1 if side == "Right" else -1)
        pose.set(side + "Shoulder", shoulder, -across, out)
        elbow = g["elbow"] + g.get("elbow_swing", 0.0) * max(forward, 0.0)
        pose.set(side + "Elbow", elbow, 0, 0)
        pose.set(side + "Wrist", -6, 0, 0)

    for side, sole, rotation, knee in feet(t, g):
        L.leg_ik(pose, side, sole, rotation, knee)
    return pose


def swing_path(v, duty, matching=0.65):
    """Where a swinging foot is along its stride (-0.5 behind to 0.5 ahead) at swing progress v. It
    leaves and lands moving back under the body (part of the way to ground speed, `matching`), as real
    feet do, so touchdown is seamless; a smoothstep alone would land the foot still moving forward."""
    eased = -0.5 + smooth(v)
    tangent = -(1 - duty) / duty
    v2, v3 = v * v, v * v * v
    hermite = (2 * v3 - 3 * v2 + 1) * -0.5 + (v3 - 2 * v2 + v) * tangent + (-2 * v3 + 3 * v2) * 0.5 + (v3 - v2) * tangent
    return eased + (hermite - eased) * matching


def feet(t, g):
    """Where each foot is at time t: (side, sole point, rotation, knee direction). A foot is planted
    for its duty of the cycle, rolling heel to toe, moving back at exactly the ground speed; then it
    swings through on an arc. Feet sit under the hips, turned with them (strafes run "hips first").
    `duty_Left`/`duty_Right`, `lift_*`, `push_*` and `trail_*` override one leg (limps)."""
    cycle, speed, direction = g["cycle"], g["speed"], g["direction"]
    floor = L.FLOOR + g.get("drop", 0.0)
    backward = direction.z > 0.5
    strafe = abs(direction.x) > 0.5
    hip_turn = g.get("hip_turn", 0.0) * (-direction.x if strafe else 0.0)
    hips = rot(0, hip_turn, 0)
    phase_left = (t / cycle) % 1.0
    out = []
    for side, offset in (("Left", 0.0), ("Right", 0.5)):
        duty = g.get("duty_" + side, g["duty"])
        travel = speed * duty * cycle
        phase = (phase_left + offset) % 1.0
        width = g["width"] / 2 * (1 if side == "Right" else -1)
        lateral = hips @ V(width, 0, 0)
        toe_out = g.get("toe_out", 6.0) * (-1 if side == "Right" else 1)
        strike_angle = g.get("strike_" + side, g.get("strike", 12.0))
        if phase < duty:
            u = phase / duty
            along = 0.5 - u
            lift = 0.0
            strike = strike_angle * (1 - smooth(u / 0.22))
            push = g.get("push_" + side, g.get("push", 25.0)) * smooth((u - 0.55) / 0.45)
            toe, heel = (push, strike) if backward else (strike, push)
        else:
            v = (phase - duty) / (1 - duty)
            along = swing_path(v, duty)
            # Airborne the whole swing. The foot is highest early, behind the body (the heel kicks up),
            # passes under the hips lower, then reaches forward close to the ground.
            lift = g.get("lift_" + side, g["lift"]) * math.sin(math.pi * v**0.6) ** 1.3
            # The toes trail down after push-off (pivoting on the toe tip, so it never digs into the
            # floor), then come up ready to strike. Backwards it is the other way round.
            trail = g.get("trail_" + side, g.get("trail", 30.0)) * (1 - smooth(v / 0.45))
            ready = strike_angle * smooth((v - 0.55) / 0.45)
            toe, heel = (trail, ready) if backward else (ready, trail)
            if toe >= heel:
                heel = 0.0
            else:
                toe = 0.0
        position = lateral + direction * (along * travel) + V(0, 0, g.get("feet_z", 0.0))
        sole, rotation = L.foot_on_floor(position.x, position.z, floor + lift, hip_turn + toe_out, max(toe, 0.0), max(heel, 0.0))
        out.append((side, sole, rotation, hips @ V(width * 0.25, 0, -1)))
    return out


def gait_set(prefix, base, joints=None, priority="Movement"):
    """Four directional clips of one gait, all on the same cycle."""
    for name, direction in DIRECTIONS.items():
        g = dict(base)
        g["direction"] = direction
        Clip(
            prefix + name,
            g["cycle"],
            (lambda gg: lambda t: gait(t, gg))(g),
            loop=True,
            priority=priority,
            joints=joints,
            drop=g.get("drop", 0.0),
            note="speed %.1f studs/s" % g["speed"],
        )


# --- The sets ---------------------------------------------------------------------------------------
RUN = {  # 16 studs/s: standing movement. 4 steps a second keeps the flights short.
    "speed": 16.0, "cycle": 0.50, "duty": 0.28, "pelvis": -0.37, "bob": 0.10, "twist": 9.0, "roll": 3.0,
    "lean": 9.0, "hip_lean": 3.0, "hip_turn": 50.0, "side_lean": 4.0, "counter": 0.9,
    "arm_swing": 32.0, "arm_carry": 8.0, "elbow": 72.0, "elbow_swing": 22.0, "arm_out": 8.0, "arm_across": 10.0,
    "width": 0.95, "lift": 0.5, "strike": 10.0, "push": 30.0, "trail": 38.0, "sway": 0.03, "bob_nod": 1.5,
}
JOG = {  # 11.2 studs/s: aiming while moving, limping
    "speed": 11.2, "cycle": 0.54, "duty": 0.36, "pelvis": -0.31, "bob": 0.07, "twist": 7.0, "roll": 2.5,
    "lean": 6.0, "hip_lean": 2.0, "hip_turn": 45.0, "side_lean": 3.0, "counter": 0.9,
    "arm_swing": 22.0, "arm_carry": 8.0, "elbow": 55.0, "elbow_swing": 18.0, "arm_out": 7.0, "arm_across": 6.0,
    "width": 1.0, "lift": 0.38, "strike": 12.0, "push": 24.0, "trail": 30.0, "sway": 0.04, "bob_nod": 1.0,
}
CROUCH_WALK = {  # 8.8 studs/s, hips dropped 1.8 by the game: low, quick, sneaking steps
    "speed": 8.8, "cycle": 0.55, "duty": 0.55, "drop": 1.8, "pelvis": 0.72, "back_lean": 0.85, "bob": 0.05, "walk": True,
    "twist": 6.0, "roll": 2.0, "lean": 30.0, "hip_lean": 16.0, "hip_turn": 40.0, "side_lean": 3.0, "counter": 0.9,
    "arm_swing": 12.0, "arm_carry": 22.0, "elbow": 50.0, "elbow_swing": 10.0, "arm_out": 10.0,
    "width": 1.15, "lift": 0.2, "strike": 8.0, "push": 18.0, "trail": 22.0, "sway": 0.05, "bob_nod": 0.5,
    "feet_z": 0.05,
}
SPRINT = {  # 24 studs/s, forward only
    "speed": 24.0, "cycle": 0.44, "duty": 0.20, "pelvis": -0.40, "bob": 0.11, "twist": 11.0, "roll": 3.5,
    "lean": 17.0, "hip_lean": 6.0, "hip_turn": 0.0, "counter": 0.9, "direction": V(0, 0, -1),
    "arm_swing": 46.0, "arm_carry": 6.0, "elbow": 82.0, "elbow_swing": 18.0, "arm_out": 6.0, "arm_across": 16.0,
    "width": 0.9, "lift": 0.62, "strike": 6.0, "push": 36.0, "trail": 50.0, "sway": 0.02, "bob_nod": 2.0,
}


def idle_pose(t):
    """Standing, weight on both feet with a slow shift, breathing, knees soft, ready."""
    pose = Pose()
    shift = math.sin(TAU * t / 4.0)
    breath = math.sin(TAU * t / 2.0)
    pose.set("Root", -1.0, 2.0 + shift * 1.0, shift * 1.2, move=(-shift * 0.045, -0.07 + breath * 0.008, 0))
    pose.set("Waist", -3.5 - breath * 1.0, -2.0 - shift * 1.2, -shift * 1.4)
    pose.set("Neck", 4.0 + breath * 0.6, shift * 2.0 + math.sin(TAU * t / 4.0 + 1.1) * 1.5, shift * 0.5)
    for side, sign in (("Left", -1.0), ("Right", 1.0)):
        pose.set(side + "Shoulder", 5.0 + breath * 1.2, 0, sign * (7.0 + breath * 0.8))
        pose.set(side + "Elbow", 14.0 + breath * 1.0, 0, 0)
        pose.set(side + "Wrist", -4.0, 0, 0)
    floor = L.FLOOR
    for side, x, z, yaw in (("Left", -0.6, -0.12, 8.0), ("Right", 0.62, 0.18, -12.0)):
        sole, r = L.foot_on_floor(x, z, floor, yaw)
        L.leg_ik(pose, side, sole, r, V(x * 0.3, 0, -1))
    return pose


def crouch_idle_pose(t):
    """Crouched (hips dropped 1.8 by the game): balanced on the balls of the feet, torso forward,
    head up and on the aim; head top about 3.4 studs above the floor, under low cover."""
    pose = Pose()
    breath = math.sin(TAU * t / 2.4)
    shift = math.sin(TAU * t / 3.6)
    pose.set("Root", -16.0, 4.0 + shift, shift * 1.5, move=(-shift * 0.03, 0.62 + breath * 0.01, 0.05))
    pose.set("Waist", -30.0 - breath * 1.2, -4.0, -shift)
    pose.set("Neck", 34.0 + breath * 0.5, shift * 2.0, 0)
    for side, sign in (("Left", -1.0), ("Right", 1.0)):
        pose.set(side + "Shoulder", 24.0 + breath, 0, sign * 10.0)
        pose.set(side + "Elbow", 48.0, 0, 0)
        pose.set(side + "Wrist", -6.0, 0, 0)
    floor = L.FLOOR + 1.8
    for side, x, z, yaw, heel in (("Left", -0.62, -0.25, 10.0, 0.0), ("Right", 0.6, 0.45, -16.0, 14.0)):
        sole, r = L.foot_on_floor(x, z, floor, yaw, 0.0, heel)
        L.leg_ik(pose, side, sole, r, V(x * 0.5, 0, -1))
    return pose


def limp_pose(t, bad="Right"):
    """Limping at 11 studs/s: the hurt leg gets a short, stiff, low step with no push-off; while it
    holds the weight the body dips and leans away from it, and the other arm flares for balance."""
    good = "Left" if bad == "Right" else "Right"
    g = dict(JOG)
    g["direction"] = V(0, 0, -1)
    g["duty_" + bad], g["duty_" + good] = 0.2, 0.46
    g["lift_" + bad], g["push_" + bad], g["trail_" + bad], g["strike_" + bad] = 0.22, 4.0, 8.0, 4.0
    g["arm_swing"] = 14.0
    pose = gait(t, g)
    phase = (t / g["cycle"] + (0.5 if bad == "Right" else 0.0)) % 1.0
    on_bad = math.sin(math.pi * phase / 0.2) if phase < 0.2 else 0.0
    side = 1 if bad == "Right" else -1
    pose.turn("Root", rot(0, 0, side * 6.0 * on_bad))
    pose.move("Root", 0, -0.13 * on_bad, 0)
    pose.turn("Waist", rot(-5.0 * on_bad, 0, side * 8.0 * on_bad))
    pose.turn("Neck", rot(3.0 * on_bad, 0, -side * 6.0 * on_bad))
    pose.turn(good + "Shoulder", rot(0, 0, -side * 16.0 * on_bad))
    for s, sole, rotation, knee in feet(t, g):  # the lurch moved the hips: plant the feet again
        L.leg_ik(pose, s, sole, rotation, knee)
    return pose


def hobble_pose(t):
    """Both legs in the red, 4 studs/s: hunched, short dragging steps, hands near the thighs."""
    g = {
        "speed": 4.0, "cycle": 1.0, "duty": 0.7, "pelvis": -0.42, "bob": 0.05, "walk": True, "twist": 6.0,
        "roll": 5.0, "lean": 24.0, "hip_lean": 8.0, "counter": 0.8, "direction": V(0, 0, -1),
        "arm_swing": 8.0, "arm_carry": 20.0, "elbow": 38.0, "arm_out": 12.0, "width": 1.2, "lift": 0.18,
        "strike": 2.0, "push": 8.0, "trail": 6.0, "sway": 0.09, "bob_nod": 2.5, "feet_z": -0.1,
    }
    return gait(t, g)


# --- Air -------------------------------------------------------------------------------------------
def jump_pose(t):
    """Take-off (0.25 s): a quick dip and drive, then the legs tuck."""
    u = t / 0.25
    pose = Pose()
    dip = math.sin(math.pi * min(u / 0.5, 1.0)) if u < 0.5 else 0.0
    tuck = smooth((u - 0.35) / 0.65)
    pose.set("Root", -6.0 * dip - 4.0 * tuck, 0, 0, move=(0, -0.25 * dip + 0.05 * tuck, 0))
    pose.set("Waist", -10.0 * dip + 4.0 * tuck, 0, 0)
    pose.set("Neck", 8.0 * dip, 0, 0)
    for side, sign in (("Left", -1.0), ("Right", 1.0)):
        pose.set(side + "Shoulder", -20.0 * dip + 35.0 * tuck, 0, sign * (8.0 + 14.0 * tuck))
        pose.set(side + "Elbow", 30.0 + 20.0 * tuck, 0, 0)
    for side, x in (("Left", -0.55), ("Right", 0.55)):
        lift = 0.55 * tuck * (1.0 if side == "Right" else 0.75)
        sole, r = L.foot_on_floor(x, 0.05 - 0.2 * tuck * (1 if side == "Right" else -0.5), L.FLOOR + lift, 0, 0, 20.0 * (1 - tuck) * dip)
        if tuck > 0:
            r = L.foot_rotation(0, -25.0 * tuck)
        L.leg_ik(pose, side, sole, r)
    return pose


def fall_pose(t):
    """In the air: knees up a little, arms out for balance, a slow paddle."""
    pose = Pose()
    paddle = math.sin(TAU * t / 1.2)
    pose.set("Root", -6.0, 0, paddle * 2.0, move=(0, 0.1, 0))
    pose.set("Waist", 6.0, 0, -paddle * 2.0)
    pose.set("Neck", -4.0, 0, 0)
    for side, sign in (("Left", -1.0), ("Right", 1.0)):
        pose.set(side + "Shoulder", 30.0 + sign * paddle * 6.0, 0, sign * 34.0)
        pose.set(side + "Elbow", 40.0, 0, 0)
    for side, x, z, lift in (("Left", -0.55, 0.25, 0.55), ("Right", 0.55, -0.25, 0.85)):
        sole = V(x, L.FLOOR + lift + (paddle * 0.06 if side == "Left" else -paddle * 0.06), z)
        L.leg_ik(pose, side, sole, L.foot_rotation(0, -30.0))
    return pose


def land_pose(t):
    """Landing (0.3 s): absorb through the knees and spine, then recover."""
    u = t / 0.3
    squash = math.sin(math.pi * min(u / 0.45, 1.0)) if u < 0.45 else max(0.0, 1 - smooth((u - 0.45) / 0.55)) * 0.35
    pose = Pose()
    pose.set("Root", -10.0 * squash, 0, 0, move=(0, -0.55 * squash, 0.05 * squash))
    pose.set("Waist", -14.0 * squash, 0, 0)
    pose.set("Neck", 16.0 * squash, 0, 0)
    for side, sign in (("Left", -1.0), ("Right", 1.0)):
        pose.set(side + "Shoulder", 12.0 + 14.0 * squash, 0, sign * (8.0 + 18.0 * squash))
        pose.set(side + "Elbow", 25.0 + 20.0 * squash, 0, 0)
    for side, x, z in (("Left", -0.62, -0.1), ("Right", 0.62, 0.15)):
        sole, r = L.foot_on_floor(x, z, L.FLOOR)
        L.leg_ik(pose, side, sole, r, V(x * 0.4, 0, -1))
    return pose


def register():
    gait_set("Run", RUN)
    gait_set("Jog", JOG)
    gait_set("CrouchWalk", CROUCH_WALK)
    Clip("Sprint", SPRINT["cycle"], lambda t: gait(t, SPRINT), loop=True, note="24 studs/s")
    Clip("Idle", 4.0, idle_pose, loop=True)
    Clip("CrouchIdle", 3.6, crouch_idle_pose, loop=True, drop=1.8)
    Clip("LimpRight", JOG["cycle"], lambda t: limp_pose(t, "Right"), loop=True, note="11 studs/s, right leg hurt")
    Clip("LimpLeft", JOG["cycle"], lambda t: limp_pose(t, "Left"), loop=True, note="11 studs/s, left leg hurt")
    Clip("Hobble", 1.0, hobble_pose, loop=True, note="4 studs/s, both legs hurt")
    Clip("Jump", 0.25, jump_pose)
    Clip("Fall", 1.2, fall_pose, loop=True)
    Clip("Land", 0.3, land_pose)  # LandRoll lives in mp_stances (it rolls along the floor)
