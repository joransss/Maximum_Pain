"""Maximum Pain R15 animation suite. Run after mp_rig.py:
    exec(open(path).read(), {"__file__": path})
All numbers are Roblox studs / degrees in HumanoidRootPart space (character faces -Z, +Y up).
Gameplay numbers these clips are built to (GameConfig / WeaponConfig): run 16, aim-walk 9.6, crouch 8 (root lowered
CROUCH_DROP), sprint 25.6 studs/s; dive windup 0.15 s, recovery 0.5 s; reload 1.6 s with phases 0.3 / 0.6 / 0.82.
Locomotion cycles plant the feet: stance sweep = speed x stance time, so feet don't slide at the authored speed
(the game scales playback with actual speed).
"""
import math
from mathutils import Matrix, Vector

exec(open(__import__("os").path.join(__import__("os").path.dirname(__file__), "mp_author.py")).read(), globals())

CROUCH_DROP = 1.3  # GameConfig.Movement.CrouchDrop: the game lowers the root this much, so crouch clips raise the feet
ANKLE_Y = JOINT_POS["RightFoot"].y  # -2.9305 (flat foot on the ground at standard HipHeight)


def T(x=0.0, y=0.0, z=0.0):
    return Matrix.Translation((x, y, z))


def RX(d):
    return Matrix.Rotation(math.radians(d), 4, "X")


def RY(d):
    return Matrix.Rotation(math.radians(d), 4, "Y")


def RZ(d):
    return Matrix.Rotation(math.radians(d), 4, "Z")


def smooth(u):
    return u * u * (3 - 2 * u)


def lerp(a, b, u):
    return a + (b - a) * u


def ankle(x, y_lift, z, yaw=0.0, pitch=0.0, roll=0.0):
    """Ankle joint frame: y_lift is height above the flat-foot ground position."""
    return T(x, ANKLE_Y + y_lift, z) @ RY(yaw) @ RX(pitch) @ RZ(roll)


def wrist(x, y, z, pitch=0.0, yaw=0.0, roll=0.0):
    return T(x, y, z) @ RY(yaw) @ RX(pitch) @ RZ(roll)


def root(t_y=0.0, pitch=0.0, yaw=0.0, roll=0.0, x=0.0, z=0.0):
    return T(x, t_y, z) @ RY(yaw) @ RX(pitch) @ RZ(roll)


def reach(side, direction, frac=0.95, pitch=0.0):
    """Wrist target along a chest-space direction from the shoulder, within arm's length (1.73 studs)."""
    p = JOINT_POS[side + "UpperArm"] + Vector(direction).normalized() * 1.72 * frac
    return wrist(p.x, p.y, p.z, pitch)


# Pistol poses: Handle frames (HRP space, chest at rest). Barrel = Handle -Z, slide on top (+Y).
AIM_GUN = T(0.25, 1.15, -1.45)
HIP_GUN = T(0.6, 0.75, -1.45)  # firing one-handed: arm extended at chest height (Max Payne 3 reference)
CARRY_GUN = T(1.05, -0.35, -0.45) @ RX(-30)  # not firing: pistol low at the side, muzzle forward-down
READY_GUN = T(0.55, 0.35, -1.0) @ RX(-12)  # reload start / end
COVER_GUN = T(0.55, 1.35, -0.75) @ RX(80)
COVERLOW_GUN = T(0.3, 0.55, -0.6) @ RX(75)  # ducked in low cover: gun tucked to the chest, muzzle up
SUPPORT = T(-0.34, -0.2, 0.04) @ RY(-25) @ RX(80)  # left hand on the grip, in Handle space


def support(gun):
    return hand_to_wrist(gun @ SUPPORT, "Left")


def two_hands(clip, t, gun):
    clip.gun(t, gun)
    clip.hand(t, "Left", support(gun))


def stance_feet(clip, t, lift=0.0, spread=0.55, stagger=0.2, yaw=8.0):
    """Relaxed combat stance: right foot back, toes slightly out."""
    clip.foot(t, "Right", ankle(spread, lift, stagger, -yaw))
    clip.foot(t, "Left", ankle(-spread, lift, -stagger, yaw))


def relaxed_arms(clip, t, breath=0.0):
    clip.hand(t, "Right", wrist(1.42, -0.7 + breath, -0.12, 8))
    clip.hand(t, "Left", wrist(-1.42, -0.7 + breath, -0.12, 8))


def pole(clip, t, name, pos):
    b = ARM.data.bones[name]
    rest = b.matrix_local
    clip._key(name, rest.inverted() @ Matrix.Translation(C @ Vector(pos)) @ rest.to_3x3().to_4x4(), t)


# ---------------------------------------------------------------- locomotion
def toe_roll(pitch):
    """Ankle offset (up, foot-local z) when the foot pitches by `pitch` degrees about its toe tip instead of the ankle.
    R15 foot: toe tip 0.5 ahead of and 0.262 below the ankle."""
    th = math.radians(pitch)
    return 0.262 * math.cos(th) - 0.5 * math.sin(th) - 0.262, 0.262 * math.sin(th) + 0.5 * math.cos(th) - 0.5


def gait(name, direction, speed, period, duty, fwd, lift, bob, drop, lean, hip_yaw=0.0, feet_up=0.0, swing=0.35,
         arm_bend=45.0, twist=6.0, width=0.5, priority="Movement"):
    """Foot-planted cycle. direction: (x, z) of travel in character space. fwd: share of the stance sweep in front of the hip."""
    clip = Clip(name, period, loop=True, priority=priority)
    d = Vector((direction[0], 0, direction[1])).normalized()
    sweep = speed * duty * period
    front, back = sweep * fwd, sweep * (1 - fwd)
    lean_axis = Vector((0, 1, 0)).cross(d)
    n = int(round(period * FPS))
    for k in range(n + 1):
        t = k / FPS
        p = k / n
        y = -drop - bob * math.cos(4 * math.pi * (p - duty / 2))  # lowest at mid-stance of each foot
        tw = twist * math.sin(2 * math.pi * p)
        r = T(0, y, 0) @ Matrix.Rotation(math.radians(lean), 4, lean_axis) @ RY(hip_yaw + tw)
        clip.fk(t, "LowerTorso", r)
        clip.fk(t, "UpperTorso", RY(-(hip_yaw + tw * 0.8)) @ RX(-lean * 0.25))
        clip.fk(t, "Head", RX(lean * 0.6) @ RY(tw * 0.3))
        for side, off, sign in (("Right", 0.0, 1), ("Left", 0.5, -1)):
            q = (p + off) % 1.0
            base = (RY(hip_yaw) @ Vector((sign * width, 0, 0, 0))).xyz
            if q < duty:  # planted: foot moves back under the body at exactly the travel speed
                u = q / duty
                s = front - sweep * u
                pitch = -max(0.0, u - 0.6) / 0.4 * 30  # heel peels up, rolling on the toes
                dy, dz = toe_roll(pitch)
                h = 0.0
            else:  # swing: lift and bring forward (Hermite curve)
                u = (q - duty) / (1 - duty)
                # The foot touches down already moving back at travel speed (still in the world), so it never skims
                # the ground; it leaves at half that (the heel is already up).
                ts = (1 - duty) * period
                m0, m1 = -0.5 * speed * ts, -speed * ts
                u2, u3 = u * u, u * u * u
                s = (2 * u3 - 3 * u2 + 1) * -back + (u3 - 2 * u2 + u) * m0 + (-2 * u3 + 3 * u2) * front + (u3 - u2) * m1
                pitch = lerp(-30, 5, smooth(u))
                fade = 1 - smooth(min(u / 0.3, 1.0))  # toe-roll offset carried off the ground, then let go
                dy, dz = toe_roll(min(pitch, 0.0))
                dy, dz = dy * fade, dz * fade
                h = lift * math.sin(math.pi * u)
            pos = base + d * s + (RY(hip_yaw) @ Vector((0, 0, dz, 0))).xyz
            clip.foot(t, side, ankle(pos.x, feet_up + h + dy, pos.z, hip_yaw, pitch))
            # arms swing against the legs; forward = +1
            a = -math.cos(2 * math.pi * p) if side == "Right" else math.cos(2 * math.pi * p)
            clip.hand(t, side, wrist(sign * 1.32, -0.45 + 0.12 * a + (0.25 if arm_bend > 60 else 0), -0.2 - swing * a, arm_bend + 25 * a))
        knee_dir = (RY(hip_yaw) @ Vector((0, 0, -3, 0))).xyz
        for side, sign in (("R", 1), ("L", -1)):
            k_pos = (RY(hip_yaw) @ Vector((sign * 0.5, 0, 0, 0))).xyz + Vector((0, -1.92, 0)) + knee_dir
            pole(clip, t, "Pole_Knee." + side, k_pos)
    return clip.done()


DIRS = {"F": (0, -1), "B": (0, 1), "L": (-1, 0), "R": (1, 0)}
HIP_YAW = {"F": 0, "B": 0, "L": 40, "R": -40}


def locomotion():
    for k, d in DIRS.items():
        back = k == "B"
        gait("Run_" + k, d, 16, 0.5, 0.25, 0.4, 0.75, 0.08, 0.38, -4 if back else 10, HIP_YAW[k], swing=0.4, arm_bend=80)
        gait("Walk_" + k, d, 9.6, 0.62, 0.34, 0.45, 0.45, 0.05, 0.42, -2 if back else 6, HIP_YAW[k] * 0.8, swing=0.2, arm_bend=40, twist=4)
        gait("CrouchWalk_" + k, d, 8, 0.7, 0.45, 0.5, 0.5, 0.04, 0.0, 10 if back else 26, HIP_YAW[k] * 0.7,
             feet_up=CROUCH_DROP, swing=0.15, arm_bend=50, twist=3)
    gait("Sprint", (0, -1), 25.6, 0.42, 0.18, 0.4, 1.0, 0.1, 0.42, 16, swing=0.65, arm_bend=85, twist=9)


def idle():
    c = Clip("Idle", 3.0, loop=True, priority="Idle")
    for t, b in ((0, 0.0), (1.5, 1.0), (3.0, 0.0)):  # slow breath
        c.fk(t, "LowerTorso", root(-0.08 - 0.02 * b, 0, 10))
        c.fk(t, "UpperTorso", RX(-2 + 1.5 * b) @ RY(-8))
        c.fk(t, "Head", RX(-1 * b) @ RY(-2))
        stance_feet(c, t)
        relaxed_arms(c, t, 0.03 * b)
    c.done()

    c = Clip("CrouchIdle", 2.4, loop=True, priority="Idle")
    for t, b in ((0, 0.0), (1.2, 1.0), (2.4, 0.0)):
        c.fk(t, "LowerTorso", root(-0.05 - 0.03 * b, -25, 12))
        c.fk(t, "UpperTorso", RX(-9 + 1.5 * b) @ RY(-10))
        c.fk(t, "Head", RX(26))
        c.foot(t, "Right", ankle(0.6, CROUCH_DROP + 0.18, 0.75, -15, -35))  # back foot on its toes
        c.foot(t, "Left", ankle(-0.55, CROUCH_DROP, -0.55, 10))
        c.hand(t, "Right", wrist(1.25, -0.45 + 0.02 * b, -0.6, 40))
        c.hand(t, "Left", wrist(-1.25, -0.45 + 0.02 * b, -0.6, 40))
    c.done()


def turns():
    """Stepping while the body turns in place (the game rotates the root ~120 deg/s at full playback)."""
    for name, sgn in (("TurnL", 1), ("TurnR", -1)):
        c = Clip(name, 0.6, loop=True, priority="Movement")
        n = 18
        for k in range(n + 1):
            t, p = k / FPS, k / n
            c.fk(t, "LowerTorso", root(-0.1 - 0.04 * math.sin(4 * math.pi * p), 0, sgn * 6 * math.sin(2 * math.pi * p)))
            c.fk(t, "UpperTorso", RY(sgn * 4))
            lead = "Left" if sgn > 0 else "Right"
            for side, off in ((lead, 0.0), ("Right" if lead == "Left" else "Left", 0.5)):
                q = (p + off) % 1.0
                if q < 0.5:  # planted: appears to rotate against the turn
                    yaw = sgn * lerp(18, -18, q / 0.5)
                    h = 0.0
                else:
                    u = (q - 0.5) / 0.5
                    yaw = sgn * lerp(-18, 18, smooth(u))
                    h = 0.3 * math.sin(math.pi * u)
                sign = 1 if side == "Right" else -1
                pos = (RY(yaw) @ Vector((sign * 0.55, 0, 0, 0))).xyz
                c.foot(t, side, ankle(pos.x, h, pos.z, yaw))
            relaxed_arms(c, t)
        c.done()


# ---------------------------------------------------------------- weapon (upper body)
def weapon():
    c = Clip("Aim", 2.0, loop=True, priority="Action", joints=ARMS)
    for t, b in ((0, 0.0), (1.0, 1.0), (2.0, 0.0)):
        c.fk(t, "UpperTorso", RX(-3) @ RY(-6))
        c.fk(t, "Head", RX(-6 + 0.5 * b) @ RY(4) @ RZ(-6))  # cheek toward the sights
        two_hands(c, t, AIM_GUN @ T(0, 0.01 * b, 0))
    c.done()

    c = Clip("Hip", 2.0, loop=True, priority="Action", joints=RIGHT_ARM)
    for t, b in ((0, 0.0), (1.0, 1.0), (2.0, 0.0)):
        c.gun(t, HIP_GUN @ T(0, 0.015 * b, 0))
    c.done()

    c = Clip("Carry", 2.0, loop=True, priority="Action", joints=RIGHT_ARM)
    for t, b in ((0, 0.0), (1.0, 1.0), (2.0, 0.0)):
        c.gun(t, CARRY_GUN @ T(0, 0.01 * b, 0))
    c.done()

    c = Clip("CoverIdle", 2.0, loop=True, priority="Action", joints=ARMS)
    for t, b in ((0, 0.0), (1.0, 1.0), (2.0, 0.0)):
        c.fk(t, "UpperTorso", RX(-2 + b))
        c.fk(t, "Head", RY(-12) @ RX(-4))
        two_hands(c, t, COVER_GUN @ T(0, 0.02 * b, 0))
    c.done()

    # Low cover: curled down behind the wall, head ducked below the edge glancing along it, gun tucked in.
    c = Clip("CoverLow", 2.0, loop=True, priority="Action", joints=ARMS)
    for t, b in ((0, 0.0), (1.0, 1.0), (2.0, 0.0)):
        c.fk(t, "UpperTorso", RX(-24 + b) @ RY(-8))
        c.fk(t, "Head", RX(-18) @ RY(-20))
        two_hands(c, t, COVERLOW_GUN @ T(0, 0.015 * b, 0))
    c.done()

    # Recoil pulses: sharp kick (2 frames), recovery with a small overshoot. Aimed shots barely move the body
    # (Max Payne 3 reference); one-handed hip shots kick harder.
    c = Clip("RecoilAim", 0.25, priority="Action3", joints=ARMS)
    for t, kick, back, chest in ((0, 0, 0, 0), (0.05, 6, 0.08, 1.5), (0.13, -1, -0.01, -0.3), (0.25, 0, 0, 0)):
        c.fk(t, "UpperTorso", RX(-3 + chest) @ RY(-6))
        c.fk(t, "Head", RX(-6 + chest * 0.5) @ RY(4) @ RZ(-6))
        two_hands(c, t, AIM_GUN @ T(0, 0.03 * kick / 6, back) @ RX(kick))
    c.done()

    c = Clip("RecoilHip", 0.22, priority="Action3", joints=RIGHT_ARM)
    for t, kick, back in ((0, 0, 0), (0.045, 14, 0.14), (0.12, -2, -0.02), (0.22, 0, 0)):
        c.gun(t, HIP_GUN @ T(0, 0.04 * kick / 14, back) @ RX(kick))
    c.done()

    # Reload, 1.6 s: mag out by 0.48 s, fresh mag from the belt, seated at 0.96 s, slide racked at 1.31 s.
    c = Clip("Reload", 1.6, priority="Action2", joints=ARMS)
    tilt = T(0.3, 0.55, -0.95) @ RY(30) @ RZ(-25) @ RX(-8)  # mag well turned toward the support hand
    belt = wrist(-1.1, -0.75, 0.1, 10, 20)
    keys = [
        # t, gun, left wrist, head pitch
        (0.0, READY_GUN, support(READY_GUN), -4),
        (0.16, tilt, support(tilt), -24),
        (0.3, tilt @ T(0, 0.02, 0), hand_to_wrist(tilt @ T(-0.3, -0.45, 0.1) @ RX(70), "Left"), -26),  # thumb drops the mag
        (0.5, tilt, wrist(-0.85, -0.55, -0.05, 20, 25), -20),
        (0.66, tilt, belt, -12),  # grab a magazine
        (0.82, tilt, hand_to_wrist(tilt @ T(-0.15, -0.9, 0.1) @ RX(85), "Left"), -24),
        (0.96, tilt @ T(0, 0.04, 0), hand_to_wrist(tilt @ T(-0.12, -0.5, 0.08) @ RX(85), "Left"), -26),  # seat it (gun bumps up)
        (1.12, tilt @ RY(-10), hand_to_wrist(tilt @ T(-0.25, 0.75, 0.25) @ RX(170), "Left"), -22),  # over the slide
        (1.31, tilt @ RY(-10) @ T(0, 0, -0.05), hand_to_wrist(tilt @ T(-0.25, 0.75, 0.75) @ RX(170), "Left"), -18),  # rack
        (1.42, READY_GUN @ RX(6), support(READY_GUN), -8),  # slide snaps home: small overshoot
        (1.6, READY_GUN, support(READY_GUN), -4),
    ]
    for t, gun, lw, head in keys:
        c.fk(t, "UpperTorso", RX(-4) @ RY(6 if 0.1 < t < 1.45 else 0))
        c.fk(t, "Head", RX(head) @ RY(8 if 0.1 < t < 1.45 else 0))
        c.gun(t, gun)
        c.hand(t, "Left", lw)
    c.done()


# ---------------------------------------------------------------- shoot-dodge
# In the air and on the ground the game lays the root along the dive (root +Y = travel, root -Z = chest toward
# the aim), so these poses are authored "standing" in that frame: up = head-first, -Z = where the chest faces.
OVERHEAD_R = wrist(0.55, 2.4, -0.35, 170)
OVERHEAD_L = wrist(-0.55, 2.35, -0.3, 170)


def windups():
    poses = {  # pelvis (drop, pitch, roll), right ankle, left ankle, arm swing (x, z) — loaded just before launch
        "F": ((0.4, -30, 0), ankle(0.5, 0.25, 0.65, -10, -35), ankle(-0.5, 0, -0.45), (0, 0.7)),
        "B": ((0.35, 18, 0), ankle(0.55, 0, 0.25), ankle(-0.55, 0, -0.1), (0, -0.6)),
        "L": ((0.3, -8, 18), ankle(0.95, 0, 0.1, -10, -15, 15), ankle(-0.45, 0.35, -0.05), (-0.5, 0.2)),
        "R": ((0.3, -8, -18), ankle(0.45, 0.35, -0.05), ankle(-0.95, 0, 0.1, 10, -15, -15), (0.5, 0.2)),
    }
    for k, ((drop, pitch, roll), rf, lf, (ax, az)) in poses.items():
        c = Clip("DiveWindup_" + k, 0.15, priority="Action")
        for t, u in ((0, 0.0), (0.15, 1.0)):
            c.fk(t, "LowerTorso", root(-drop * u, pitch * u, 0, roll * u))
            c.fk(t, "UpperTorso", RX(-8 * u))
            c.fk(t, "Head", RX(10 * u))
            c.foot(t, "Right", ankle(0.55, 0, 0) if u == 0 else rf)
            c.foot(t, "Left", ankle(-0.55, 0, 0) if u == 0 else lf)
            for side, sign in (("Right", 1), ("Left", -1)):
                c.hand(t, side, wrist(sign * 1.35 + ax * u, -0.6 + 0.1 * u, -0.1 + az * u, 20 - 40 * u * (1 if az > 0 else -1)))
        c.done()


def air_pose(c, t, k, flutter=0.0):
    # Max Payne 3 reference: in the air the legs are straight and together, trailing slightly behind the body.
    if k == "F":  # face down, head-first: back arched, head up the line of travel
        c.fk(t, "LowerTorso", root(0, 6))
        c.fk(t, "UpperTorso", RX(12))
        c.fk(t, "Head", RX(50))
        c.foot(t, "Right", ankle(0.3, 0.12 + flutter, 0.45, 0, -70))
        c.foot(t, "Left", ankle(-0.3, 0.12 - flutter, 0.45, 0, -70))
        c.hand(t, "Right", OVERHEAD_R)
        c.hand(t, "Left", OVERHEAD_L)
    elif k == "B":  # face up, head-first backwards: curled, looking down the body at the target past the feet
        c.fk(t, "LowerTorso", root(0, -8))
        c.fk(t, "UpperTorso", RX(-15))
        c.fk(t, "Head", RX(-40))
        c.foot(t, "Right", ankle(0.3, 0.15 + flutter, -0.45, 0, -60))
        c.foot(t, "Left", ankle(-0.3, 0.15 - flutter, -0.45, 0, -60))
        two_hands(c, t, T(0.15, 0.6, -1.45) @ RX(-35))
    else:  # side dive: chest to the target, legs together trailing
        s = 1 if k == "L" else -1
        c.fk(t, "LowerTorso", root(0, 0, s * 8, s * 6))
        c.fk(t, "UpperTorso", RY(-s * 6))
        c.fk(t, "Head", RX(8) @ RZ(s * 10))
        c.foot(t, "Right", ankle(0.3, 0.12 + flutter, 0.4, 0, -65))
        c.foot(t, "Left", ankle(-0.3, 0.12 - flutter, 0.4, 0, -65))
        two_hands(c, t, AIM_GUN)


def prone_pose(c, t, k, breath=0.0):
    if k == "Front":
        c.fk(t, "LowerTorso", root(0, 2))
        c.fk(t, "UpperTorso", RX(16 + breath))
        c.fk(t, "Head", RX(38))
        c.foot(t, "Right", ankle(0.65, 0.05, 0.15, -10, -75))
        c.foot(t, "Left", ankle(-0.6, 0.0, 0.2, 8, -75))
        c.hand(t, "Right", T(0, -0.35, -0.2) @ OVERHEAD_R)
        c.hand(t, "Left", T(0, -0.35, -0.2) @ OVERHEAD_L)
    elif k == "Back":
        c.fk(t, "LowerTorso", root(0, -4))
        c.fk(t, "UpperTorso", RX(-14 - breath))
        c.fk(t, "Head", RX(-38))
        c.foot(t, "Right", ankle(0.55, 0.65, -0.75, -5, 15))  # right knee up
        c.foot(t, "Left", ankle(-0.6, 0.0, -0.05, 10, 25))
        two_hands(c, t, T(0.15, 0.4, -1.4) @ RX(-30))
    else:
        c.fk(t, "LowerTorso", root(0, 0, 0, 4))
        c.fk(t, "UpperTorso", RX(breath) @ RZ(-4))
        c.fk(t, "Head", RX(6) @ RZ(8))
        c.foot(t, "Right", ankle(0.4, 0.55, -0.75, 0, -30))
        c.foot(t, "Left", ankle(-0.45, 0.35, 0.35, 0, -40))
        two_hands(c, t, AIM_GUN @ T(0, -0.2, 0.1))


def dives():
    windups()
    for k in DIRS:
        c = Clip("DiveAir_" + k, 0.6, loop=True, priority="Action")
        for t, f in ((0, 0.0), (0.3, 0.06), (0.6, 0.0)):
            air_pose(c, t, k, f)
        c.done()
    for k, air in (("Front", "F"), ("Back", "B"), ("Side", "L")):
        c = Clip("Prone_" + k, 2.0, loop=True, priority="Action")
        for t, b in ((0, 0.0), (1.0, 2.0), (2.0, 0.0)):
            prone_pose(c, t, k, b)
        c.done()
        # Land: hit, limbs bounce off the ground, settle (0.35 s).
        c = Clip("Land_" + k, 0.35, priority="Action")
        air_pose(c, 0, air)
        prone_pose(c, 0.07, k)
        c.fk(0.07, "Head", RX({"Front": 20, "Back": -20, "Side": -6}[k]))  # head whips on impact
        c.fk(0.07, "LowerTorso", root(-0.12, 0))
        prone_pose(c, 0.17, k)
        c.foot(0.17, "Right", ankle(0.6, 0.4, {"Front": 0.6, "Back": -0.6, "Side": -0.4}[k], 0, -40))
        c.foot(0.17, "Left", ankle(-0.6, 0.3, {"Front": 0.5, "Back": -0.3, "Side": 0.3}[k], 0, -40))
        c.fk(0.17, "LowerTorso", root(0.04, 0))
        prone_pose(c, 0.35, k)
        c.done()


def recoveries():
    stand = lambda c, t: (c.fk(t, "LowerTorso", root(-0.08, 0, 10)), c.fk(t, "UpperTorso", RY(-8)), c.fk(t, "Head", RX(0)),
                          stance_feet(c, t), relaxed_arms(c, t))
    # Front: push up off the hands, right knee under, drive up.
    c = Clip("Recover_Front", 0.5, priority="Action")
    c.fk(0, "LowerTorso", root(-1.15, -45, 5)); c.fk(0, "UpperTorso", RX(-15)); c.fk(0, "Head", RX(30))
    c.foot(0, "Right", ankle(0.55, 0.05, 0.95, 0, -60)); c.foot(0, "Left", ankle(-0.55, 0, -0.2))
    # hand directions are in chest space: the chest is pitched ~60 deg forward, so "forward" reaches the ground
    c.hand(0, "Right", reach("Right", (0.1, -0.2, -1), 0.98, 80)); c.hand(0, "Left", reach("Left", (-0.1, -0.2, -1), 0.98, 80))
    c.fk(0.2, "LowerTorso", root(-0.75, -28, 5)); c.fk(0.2, "UpperTorso", RX(-8)); c.fk(0.2, "Head", RX(18))
    c.foot(0.2, "Right", ankle(0.55, 0.15, 0.55, 0, -30)); c.foot(0.2, "Left", ankle(-0.55, 0, -0.25))
    c.hand(0.2, "Right", reach("Right", (0.15, -0.6, -0.8), 0.9, 50)); c.hand(0.2, "Left", reach("Left", (-0.15, -0.6, -0.8), 0.9, 50))
    c.fk(0.38, "LowerTorso", root(-0.05, -4, 8)); c.fk(0.38, "Head", RX(-3))  # slight overshoot to full height
    stand(c, 0.5)
    c.done()
    # Back: sit up and roll forward onto the feet.
    c = Clip("Recover_Back", 0.5, priority="Action")
    c.fk(0, "LowerTorso", root(-1.6, 28)); c.fk(0, "UpperTorso", RX(-10)); c.fk(0, "Head", RX(-15))
    c.foot(0, "Right", ankle(0.6, 0.1, -1.3, -10, 30)); c.foot(0, "Left", ankle(-0.6, 0.0, -1.1, 10, 30))
    c.hand(0, "Right", reach("Right", (0.4, -0.77, 0.88), 0.97, -40)); c.hand(0, "Left", reach("Left", (-0.4, -0.77, 0.88), 0.97, -40))
    c.fk(0.18, "LowerTorso", root(-1.25, -38)); c.fk(0.18, "UpperTorso", RX(-12)); c.fk(0.18, "Head", RX(25))
    c.foot(0.18, "Right", ankle(0.55, 0, -0.1, 0, -10)); c.foot(0.18, "Left", ankle(-0.55, 0, -0.35))
    c.hand(0.18, "Right", reach("Right", (0.15, -0.3, -1), 0.95, 70)); c.hand(0.18, "Left", reach("Left", (-0.15, -0.3, -1), 0.95, 70))
    c.fk(0.34, "LowerTorso", root(-0.45, -14, 6)); c.fk(0.34, "Head", RX(6))
    stand(c, 0.5)
    c.done()
    # Side: shoulder roll to one knee, then rise.
    c = Clip("Recover_Side", 0.5, priority="Action")
    c.fk(0, "LowerTorso", root(-1.05, -20, 0, 28)); c.fk(0, "UpperTorso", RZ(-12) @ RX(-10)); c.fk(0, "Head", RZ(-10))
    c.foot(0, "Right", ankle(1.0, 0, 0.2, -20)); c.foot(0, "Left", ankle(-0.45, 0.1, 0.85, 0, -55))
    c.hand(0, "Right", reach("Right", (0.4, -0.5, -0.8), 0.85, 40)); c.hand(0, "Left", reach("Left", (-0.75, -0.8, 0), 0.97, 10))
    c.fk(0.22, "LowerTorso", root(-0.65, -16, 0, 10)); c.fk(0.22, "UpperTorso", RX(-6))
    c.foot(0.22, "Right", ankle(0.75, 0, 0.1, -12)); c.foot(0.22, "Left", ankle(-0.5, 0.05, 0.45, 0, -25))
    c.hand(0.22, "Left", reach("Left", (-0.5, -0.8, -0.3), 0.9, 20))
    stand(c, 0.5)
    c.done()


locomotion()
idle()
turns()
weapon()
dives()
recoveries()
CLIPS = sorted(a.name for a in bpy.data.actions if "length" in a)
