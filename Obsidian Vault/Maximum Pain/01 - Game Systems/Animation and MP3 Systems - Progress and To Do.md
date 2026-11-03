# Animation and MP3 Systems: Progress and To Do

Work log and work queue for the Max Payne 3-style animation and movement pass (bullet time, vaulting, hit reactions, ragdoll, kill cam, Blender animations). Picks up where the [[Changelog]] entries of 2026-11-01 leave off; session 3 (2026-11-02 to 03) is the newest. The [[#To do (in order)|to-do list]] was rewritten in detail on 2026-11-03.

> [!warning] Save the place
> The game's scripts and the 93 imported clips live in the Team Create place ("Untitled Experience", place 70765307359272). Save it (File > Save to Roblox) after each session. The Blender scripts, the clips' keyframes and the `.blend` are committed to the repo.
> **The game's code isn't in git.** The repo's `Maximum-Pain.rbxl` is the 80 KB file from the first commit (2026-10-29, before the restart), so the place is the only copy of the code.

Related: [[Architecture]] · [[Animation Hooks]] · [[Movement State Machine]] · [[Cover System]] · [[Shoot-Dodge]] · [[Last Stand and Bullet Time]] · [[Loadout and Dual Wielding]] · [[Test Arena]] · [[Euphoria-style Reactions and Ragdolls]] · [[Max Payne 3 Kill Cam]]

## Where things stand (2026-11-03)
| Item | State | Who | Next step |
|---|---|---|---|
| **Place** | Session 3 changed 13 scripts in the Team Create place; not saved since | Whoever opens Studio next | Save it ([[#1. Save and push]]) |
| **Repo** | `3634cce`, `7f86ec1`, `a608dc7` and the 2026-11-03 notes update are committed on JackT6785's PC, not pushed | JackT6785 | Push ([[#1. Save and push]]) |
| **Play tests** | Every single-player test passes (session 3); the two-client test hasn't been run | Anyone, in Studio | [[#2. Play tests]] |
| **Low-cover pose** | Decision pending: keep hunched and facing the wall, or go side-on | JackT6785 and JordanSaa | [[#3. Low-cover pose (decision)]] |
| **Polish** | 12 open items, none blocking | Anyone | [[#4. Polish]] |
| **Animations** | All 93 clips play in Studio. None of the 100 slots has a published id, so live servers play Roblox's default animations | JordanSaa (the place's owner) | [[#5. Publish and document]] |

---

## Session 3 (2026-11-02 to 03): the play tests, the fixes they needed, and the export
- **When and who:** 2026-11-02 20:58 to 22:20, then 2026-11-03 01:51 to 02:00 after a usage-limit pause (UK time). It ran on JackT6785's PC, with Claude Code driving Studio through the Studio MCP. JackT6785 was alone in the Team Create session, so nothing clashed with JordanSaa's work.
- **Setup:** Studio play mode (one client and the server) on JackT6785's R15 avatar: hip height 2.38, root part 3.38 above the floor, 2.46 from the wall in low cover. The session 2 numbers were on JordanSaa's avatar (root 3.23 high, 2.24 from the wall), so some numbers differ for that reason alone.
- **How things were measured:** a test harness on the client recorded every frame on `RunService.PostSimulation` (the state that is drawn next). It logged every body part's box, the guns' handles, the root, the camera, the stance, the humanoid state, `TimeScale`, and each playing clip with its weight, time and speed. Studio's clip ids are content hashes (the same every time), so each playing track could be named. In the numbers below:
  - **Clearance** (lowest point over the top) is the lowest point of any body part's box over an obstacle's top while it is above it. Negative means inside it.
  - **Feet lowest** is the lowest point of either foot's box against the floor under it.
  - **Camera step** is the largest change in the camera's height from one frame to the next.
  - **Weight** is a clip's blend weight, 0 to 1.
- Each problem was measured, fixed in the game's scripts and measured again the same way. The 13 changed scripts are listed in [[#Scripts changed in session 3]].

### 1. Vault ✅ (to-do 2)
Tested from standing 2.46 studs short of the LowWall (−10, 86), straight out of low cover at the LowWall (Space in CoverLow), over CrateA (3.8 high), and in bullet time.

- **Found:**
  - **Legs in the top:**
    - LowWall: −0.19 (left foot, 4 frames).
    - CrateA: −0.31 (left foot).
    - Cause: as the leading foot reached the near face, the Vault clip was only at weight 0.78. The standing clips still had 0.22, and their straight legs pulled the feet down.
  - **Fall clip on every landing:** weight 0.16 for about 0.2 s. A finished vault handed the humanoid back in Freefall, which plays Fall until the floor is found.
  - **Camera:** it followed the hop rigidly.
    - From standing: a 1.17 step in one frame at take-off.
    - Out of low cover: down 1.35 then up 2.15 in the first frames. The hips rose 1.8 from the crouch without the root jumping (see section 2).
- **Fixed:**
  - **`AnimationController`:** the Vault clip takes the body over at 30 per second (`VAULT_FADE`, passed as the shot's `fade`) instead of `BODY_FADE` 10. Weight at the near face: 0.78 → 0.99.
  - **`VaultRules.apexAbove(rootHeight)`** = max(`APEX_ABOVE_TOP` 2.1, `LEG_TUCK` 0.6 × root height + `LEG_CLEARANCE` 0.2).
    - Tucked legs hang about 0.6 of the standing root height below the root, so the apex rises with the avatar's legs.
    - Values: 2.10 for a standard avatar (root 3.0), 2.14 for the session 2 avatar, 2.23 for this one, 2.54 for a tall Rthro.
    - `VaultRules.find` uses it. The module's self-check now asserts that a standard avatar flies at 2.1 and that longer legs fly higher.
  - **`VaultController.release(landed)`:** a finished vault puts the humanoid straight into Running. Only a vault cut short falls (Freefall).
  - **`VaultController`'s mover:** on the way down, the velocity handed to physics is capped so one physics step can't carry the root below the landing height. Without the cap, the higher apex drove the feet into the floor and the body bounced 0.20.
  - **`CameraController.setVerticalLag(share)`:**
    - VaultController sets `CAMERA_LAG` 0.5 at take-off and 0 when the vault ends.
    - The view takes half of each rise and fall of the root at once and eases into the other half, at 10 per second.
    - A first try fed each step of the path into the camera like a stance change. The landing juddered, so it was replaced.
- **Result:**

| Vault | Lowest point over the top | Camera's largest step | Fall clip | Landing |
|---|---|---|---|---|
| LowWall, from standing | −0.19 → +0.23 (now the left hand; the legs are higher) | 1.17 → 0.62 | 0.16 → 0 | no bounce; feet −0.06 after |
| LowWall, out of low cover | 0.00: the left hand rests on the top | −1.35/+2.15 → 0.83 | 0 | no bounce; feet −0.06 after |
| CrateA, from standing | −0.31 → +0.16 (left foot) | 0.64 | 0 | no bounce; feet −0.07 after |
| LowWall in bullet time (0.3 speed) | +0.06 at the front edge, with the arc sampled 3× more densely | 0.22 | 0 | 1.40 s in the air (0.45 s at full speed) |

### 2. Height changes: the root, the camera and the feet ✅
- **The camera popped when the hips moved without the root:**
  - **Cause:** the camera's pivot sits 1.6 above the root (`PIVOT_HEIGHT`), lowered by 75% of the hips' drop (`CROUCH_CAMERA_KEEP`). It was only held back when CharacterController moved the root and called `absorbRise`. On a vault from cover (CoverLow → Vaulting) and a dive's landing the hip height changes but the root doesn't jump, so the view popped: −1.35/+2.15 out of cover, +1.68 landing a dive.
  - **Fix:** `CameraController` watches the humanoid's HipHeight every frame and holds 75% of each change (`heightHold`), easing it out at 10 per second, whoever made the change.
    - `lastHip` is tied to the humanoid (`lastHumanoid`), so a respawn can't compare two bodies.
    - `absorbRise(rise)` now only reports the root jumping.
  - **Result:** 0.83 out of cover; the dive landing is smooth (largest step 0.56).
- **Stances the server forces moved the body by physics:**
  - **Cause:** for a Last Stand, a wakeup and a timed get-up, the server sets HipHeight, and that property reaches the client before the stance does. `CharacterController.applyHeight` compared the stance's height with the HipHeight already there and saw no change. So it didn't move the root, and physics dropped (or lifted) the body over several frames.
  - **Measured:**
    - Into a Last Stand: a 2.2-stud free fall (root 3.38 → 1.18), the feet 0.74 under the floor, the camera popping 1.77.
    - A get-up forced after 8 s rose by physics over 8 frames.
  - **Fix:**
    - CharacterController compares with the hip height it last put the root at (`appliedHip`, cleared on respawn).
    - The root goes to the new height over the floor (`CoverRules.floor`). If physics already moved it part of the way, only the rest is added.
    - A floor reading more than 0.5 off the expected move (another floor) is ignored, and the expected move is used.
  - **Result:** a Last Stand drops at once, with the feet at −0.05 and a largest camera step of 0.20. The get-up moves at once.
- **Dive launch:**
  - **Cause:** AimLayer held the body at the run-up's lower height (hips 0.6 down) while the launch carried the root up for real. The feet went 0.39 under the floor for four frames.
  - **Fix:** `DodgeAir` and `Dead` joined AimLayer's `FALLS`, the stances whose height changes are real moves of the root. It's now DodgeAir, DodgeGround, Vaulting and Dead, the same as CharacterController's `AIRBORNE`.
  - **Result:** +0.21.
- **Foot guard (to-do 4.1):**
  - **Cause:** while a height change eases out, the clips bend or straighten the legs at their own blend rate, not the body's. The feet dipped into the floor:
    - crouching: 0.11
    - standing up: 0.14 to 0.30
    - into a Last Stand: 0.33
  - **Fix:** `AimLayer.footDip`, for 1 s after a height change on the ground:
    - For each foot, the lowest corner of its box as posed this frame, against the floor under it. One ray per foot, from 1 stud above, 4 down, ignoring characters and dropped guns.
    - The body is lifted by the deepest dip less `FOOT_SLACK` 0.05 (the box is bigger than the foot), at most `MAX_FOOT_LIFT` 0.6.
  - **Result:** over two crouch and stand cycles, the Last Stand drop and the wakeup, the feet never went more than 0.05 under the floor.

### 3. Reloads, pickups, painkillers and drops ✅
**Reloads**, through real F pickups from the gun table, after the fixes below. Every gun played its clip once at full weight (no first-frame restart), stretched to the reload time the server set, with the right ammo after. Every moving part came back to rest.

| Gun | Clip (length) | Reload: `WeaponConfig` / seen by the client | Clip speed | Moving parts (share of the reload) | Ammo |
|---|---|---|---|---|---|
| M9 | ReloadPistol (1.6 s) | 1.6 / 1.57 s | 1.02 | magazine out 13%, in 49%; slide back 60%, home 66% | 13 → 15 |
| Glock 18 | ReloadPistol (1.6) | 1.6 / 1.56 | 1.02 | as the M9 | 15 → 17 |
| Desert Eagle | ReloadPistol (1.6) | 2.0 / 1.96 | 0.81 | as the M9 | 5 → 7 |
| S&W 500 | ReloadRevolver (3.0) | 3.0 / 2.96 | 1.01 | cylinder out 11%, in 79% | 3 → 5 |
| Uzi | ReloadPistol (1.6) | 2.0 / 1.96 | 0.81 | magazine 13% / 49%; bolt 59% / 66% | 30 → 32 |
| MP5 | ReloadRifle (2.5) | 2.2 / 2.16 | 1.15 | magazine out 16%, in 62%; bolt back 78%, home 80% | 28 → 30 |
| AK-47 | ReloadRifle (2.5) | 2.5 / 2.46 | 1.01 | as the MP5 | 28 → 30 |
| FAL | ReloadRifle (2.5) | 2.7 / 2.66 | 0.94 | as the MP5 | 18 → 20 |
| M4 | ReloadRifle (2.5) | 2.3 / 2.27 | 1.10 | magazine 16% / 62%; bolt 77% / 80% | 28 → 30 |
| SPAS-15 | ReloadRifle (2.5) | 2.6 / 2.57 | 0.97 | magazine 16% / 62%; bolt 77% / 81% | 4 → 6 |
| M107 | ReloadSniper (3.5) | 3.5 / 3.48 | 1.00 | magazine 16% / 62%; bolt 77% / 80% | 8 → 10 |
| Sawn-off | ReloadSawnOff (2.4) | 2.4 / 2.36 | 1.01 | barrels and shells open 11%, closed 80% | 0 → 2 |
| Mossberg 500 | ReloadPump (3.0) | 3.0 / 2.96 | 1.01 | pump back 88%, forward 92% | 4 → 6 |
| Dual (M9 + Uzi) | ReloadDual (2.4) | 3.0 (1.5 × the longer) / 2.96 | 0.81 | both guns: magazines 11% / 57%; slide and bolt 71% / 75% | both full |

The client sees each reload a few hundredths of a second after the server starts it, so its time is a little shorter than the config's.

- **Bug 1: slides and bolts stuck back after reloads** (FAL, M4 and Desert Eagle on the first pass).
  - **What happened:** the `BoltForward` marker fired on time (2.00 s into the 2.50 s ReloadRifle clip). But the part's resting pose had been lost, so "forward" was the racked pose.
  - **Cause:** the resting poses were kept in a weak-keyed table (`__mode = "k"`) keyed by the guns' Motor6Ds. The engine can drop an instance's Lua handle while the instance still exists, so entries vanish at random. In a test, a Motor6D key vanished after one garbage collection while the motor was still in the gun.
  - **Fix:** the resting pose lives on the motor (`RestC0` attribute, set the first time anything moves the part). It is read through `WeaponEffects.restPose(motor)`, shared by the reload markers (`AnimationController`'s `nudge`) and the firing kick (`WeaponEffects.kick`).
  - **The same pattern was in 11 tables across six controllers.** Ten are now plain tables, each emptied when its instance leaves the game:

| Controller | Table | What a lost entry did | Now |
|---|---|---|---|
| AnimationController | `rest` (motor → resting C0) | slides and bolts left racked back | removed: `WeaponEffects.restPose` |
| WeaponEffects | `restC0` (the kick's resting C0) | if the entry was lost while the part was kicked back, the next shot took the kicked pose as the rest | removed: `restPose` |
| WeaponEffects | `muzzleEffects` (light, emitters, flash counter) | another shadow-casting light and three emitters added to the muzzle | found by name (`MuzzleLight`, `MuzzleFlame`, `MuzzleSparks`, `MuzzleSmoke`); the counter is the muzzle's `Flashes` attribute |
| WeaponController | `gunStates` (spray, bloom, predicted ammo) | that gun's spray and bloom restarted | plain; pruned in `refreshHud` once the gun has left the game |
| AimLayer | `bodies` (each character's height ease, springs) | a body's height ease reset mid-move | plain; pruned each step for characters no longer there |
| ProceduralLayer | `bases`, `applied` | a joint's base pose lost between layers | plain; both empty themselves every frame |
| HitReactions | `springs`, `hits`, `joints` | flinch springs, the hit log (death push, kill cam) and the joint cache lost | plain; pruned once the character has no parent (the kill cam reads them while the body still exists) |
| AimLayer | `gunBoxes` | only a rebuild | **kept weak on purpose:** a cache |

- **Bug 2: reload markers moved every gun in the hands.** With an M4 carried in the left hand, a Desert Eagle reload also hid the M4's magazine, dropped a spent copy of it (two spent magazines) and moved its bolt.
  - **Fix:** `AnimationController` connects marker handlers that only touch the gun whose `Place` is `Right`, or both pistols for `ReloadDual`.
- **Bug 3: dropped guns hung in the air or floated.**
  - **For the player who dropped it:** the gun hung where it left the hand. It was still part of that player's physics (their client owns it), and the server anchored and moved it in the same frame as it took it out of the hand. That move never reached the owning client.
  - **For everyone else:** the gun floated about 0.45 above the floor. `GetBoundingBox` turns with the gun, so for a gun on its side the box's "height" was a width.
  - **Fix (`LoadoutService`):**
    - `bottomOf(model)`: the real lowest point of every part, whichever way it is turned.
    - `layDown(gun, near)`: rolls the gun onto its side at the spot, keeping its yaw. It then rests the gun 0.03 above the highest floor under its middle and both ends (three rays), so a gun across a table edge lies on the table.
    - `placeDropped`: a drop is laid down `SETTLE_DELAY` 0.1 s later, once it is out of the player's physics. `DroppedAt` doubles as a token, so a late lay-down can't move a gun that was picked up or dropped again. Rack guns (`keep`) are laid down at once.
    - `dropFront(record, gun)`: a drop lands about 2 studs ahead of the feet. A ray at shin height checks for the gun's length ahead (its reach past the grip, plus 0.2). A blocked drop stops that far short of the obstacle. With less than 0.6 of room, the gun is laid across the feet, 0.3 to 1.2 ahead.
  - **Result** (server and client agree):
    - Open floor: 0.03 above the floor.
    - Against the gun table: on the floor, 0.21 short of it.
    - Swapped at the rack: on the table top.
- **Pickups (F) ×14:** all worked.
  - The prompt picked is the one nearest the crosshair, not the nearest gun: standing 3.3 from the AK, F took the FAL 5.4 away because the FAL was nearer the crosshair.
  - A one-handed gun goes into the hand it replaces. A two-handed gun goes to slot 3 and has to be drawn before it can be reloaded.
- **Painkiller (H)** after one gunman hit (torso 100 → 82): the clip played once (weight 1.00, 0.90 s, no restart), the torso went back to 100, and painkillers went from 3 to 2.

### 4. Low cover ✅
- **Sliding:** 8 studs/s along the LowWall. The wall runs x −17 to −3 and the root ranged −16.26 to −3.83, so it stops 0.74 to 0.85 from the ends. The gap to the face stayed 2.46 to 2.75 while moving.
- **Corner swings round crates were broken:**
  - **Cause:** `CoverRules.outerCorner` looked for the wall's end face from 1.15 (the high-cover `GAP`). Since session 2, low cover keeps 2.2 to 2.8, so the probes started in front of the wall and never found it.
  - **Fix:** `outerCorner(position, normal, side, params, gap)` takes the character's real gap, which CoverController measures each time. It returns the swing's middle point (`apex`) as well as the target, and the swing is checked and flown through that point.
  - **Result:** holding D went round two corners of CrateA in a row, with no body part inside the crate.
- **Popping up:** the root doesn't move while popped up. This answers the session 2 question.
- **Ducking back lunged at the wall:**
  - **Cause:** the gap was re-measured on the upright pose while it blended out. The root lunged 0.57 toward the wall and the forearm went 0.83 into it.
  - **Fix:** `CoverController` remembers the body's reach for each cover stance for the whole time in cover (`reachHeld`, cleared when cover ends), and keeps the gap for the larger reach. It eases back at `REACH_RELAX` 0.5 studs/s only when all three hold:
    - settled: `REACH_SETTLE` 0.4 s after the last stance change (`CharacterController.since()`)
    - still: sideways input ≤ 0.2
    - not firing: `FIRED_HOLD` 1.5 s since the character's `LastShot` attribute
  - **Result:** the gap held at 2.54 through popping up and back. After a slide it eases back within the 0.08 deadband: the head ends 0.07 to 0.13 off the wall (it stayed 0.2 out before).

### 5. High cover, bullet time, the network, the log ✅
- **High cover** (the HighWall's east end):
  - **Blind fire round the end:** right arm only. The left hand keeps the carried AK by the leg. Three shots left from round the corner and flew 52 to 102 studs.
  - **Popping out with the AK carried:** the AK never came nearer the wall than 1.29.
  - **Idle pose:** the right forearm rests against the wall (its box 0.25 in, flush to the eye).
- **Bullet time**, through the `DebugBulletTime` test hook: a dummy with `Adrenaline` 1, an `Aim` attribute facing the player and `DebugBulletTime` true put the player at `TimeScale` 0.3.
  - **Vault:** 1.40 s in the air (0.45 s at full speed); lowest point +0.06; largest camera step 0.22.
  - **Crouch and stand:** smooth, with the feet within 0.05.
- **Network** (from the server's side; no second client yet):
  - Stance and hip height changes replicate.
  - The root's drop arrives smoothed, with no steps over 0.5 except the vault's landing.
  - The Vault clip's speed chase replicates (1.86 → 0.86 → 0.98 seen on the server).
  - The server saw up to 6 tracks at once on the character, with the clips' Studio-only ids.
- **Output log:** clean after the whole run.

### 6. Export ✅ (to-do 5)
- **Blender 5 support:** `mp_lib.bake` used `action.fcurves`, which Blender 5.0 removed (F-curves now sit in the action's layers, strips and channel bags). `_fcurves()` reads the layered action, and older Blender versions still work. `bake` now removes a clip's old action and makes a new one.
- **Deterministic exports:** `clip_data` sorts each clip's tracks. A Python set's order changed every run, so every export rewrote `keyframes.json`; two exports are now byte-identical. The regenerated clips equal the committed ones (0 difference), so Studio didn't need a re-import.
- **FBX copies:** 93 clips in `Exports/FBX` (14.6 MB). Git ignores the folder, and `L.export(fbx=True)` rebuilds it in about 10 s. Re-importing two of them gave one armature with 16 bones and the right frame range (ReloadRifle: frames 1 to 76, 2.5 s at 30 fps).
- **The `.blend`:** `MaximumPain_Animations.blend` holds the rig and all 93 clips as actions (1.95 MB).
- **How it ran:** headless Blender 5.2 (`blender --background --factory-startup --python <script>`). The script deletes the default objects, builds the rig, registers the four clip modules, runs `L.export(fbx=True)` and saves the `.blend`. About 12 s in all.

### Scripts changed in session 3
All in the Team Create place (client controllers in `StarterPlayer.StarterPlayerScripts.Controllers`, shared modules in `ReplicatedStorage.Modules`, services in `ServerScriptService`).

| Script | Side | What changed |
|---|---|---|
| `CameraController` | client | `absorbRise(rise)` only reports the root jumping. The view follows every HipHeight change itself (`lastHip`, `lastHumanoid`, 75% held and eased at 10/s). New `setVerticalLag(share)` (`verticalLag`, `lastRootY`). All of it resets on respawn. |
| `CharacterController` | client | `appliedHip`: `applyHeight` compares with the height the root was last put at and moves the root to the new height over the floor (`CoverRules.floor`), including for stances the server forces. |
| `AimLayer` | client | `FALLS` adds DodgeAir and Dead. Foot guard `footDip` (`FOOT_SLACK` 0.05, `MAX_FOOT_LIFT` 0.6) inside the height ease. `bodies` is a plain table pruned each step. |
| `AnimationController` | client | `Shot.fade` and `VAULT_FADE` 30 for the Vault clip. `nudge` reads `WeaponEffects.restPose` (its `rest` table is gone). Reload markers only touch the right-hand gun, or both pistols for `ReloadDual`. |
| `VaultController` | client | `CAMERA_LAG` 0.5 on at take-off, off at the end. `release(landed)` ends a finished vault in Running. The downward velocity is capped at the landing height. |
| `VaultRules` | shared | `LEG_TUCK` 0.6, `LEG_CLEARANCE` 0.2, `apexAbove(rootHeight)` used by `find`; two new self-checks. |
| `WeaponEffects` | client | `restPose(motor)` (`RestC0` attribute). Muzzle effects are found by name, and the flash counter is the `Flashes` attribute. The `restC0` and `muzzleEffects` tables are gone. |
| `WeaponController` | client | `gunStates` is a plain table, pruned in `refreshHud`. |
| `ProceduralLayer` | client | `bases` and `applied` are plain tables. |
| `HitReactions` | client | `springs`, `hits` and `joints` are plain tables, pruned once a character has no parent. |
| `LoadoutService` | server | `SETTLE_DELAY` 0.1, `bottomOf`, `layDown`, the delayed lay-down in `placeDropped` (with the `DroppedAt` token), `dropFront`. |
| `CoverRules` | shared | `outerCorner(position, normal, side, params, gap?)` probes from the character's gap and returns `(hit, target, apex)`. |
| `CoverController` | client | `reachHeld` per cover stance with `REACH_SETTLE` 0.4, `REACH_RELAX` 0.5 and `FIRED_HOLD` 1.5. The corner swing passes the measured gap and flies through the returned apex. |

### Repo changes in session 3
- `3634cce` Stop tracking Python bytecode: `.gitignore` gains `__pycache__/`, and the six `.pyc` files are untracked.
- `7f86ec1` Blender export: `mp_lib.py` (`_fcurves`, sorted tracks, `bake` makes a fresh action), `Exports/keyframes.json` regenerated (same content, sorted), `MaximumPain_Animations.blend` added (1.95 MB), and `.gitignore` gains `Assets/Blender/Animation/Exports/FBX/`.
- `a608dc7` Notes: this note, [[Changelog]], [[Cover System]], [[Shoot-Dodge]], [[Last Stand and Bullet Time]], [[Movement State Machine]], [[Architecture]], [[Animation Hooks]], [[Test Arena]] and the README updated. Two research notes added: [[Euphoria-style Reactions and Ragdolls]] and [[Max Payne 3 Kill Cam]].
- 2026-11-03: this note and the [[Changelog]] rewritten in detail.

---

## Session 2 (2026-11-01, second half): what was done

### 1. One-off clips no longer flash their first frame (AnimationController) ✅ tested
- **Cause (confirmed in Studio):** a non-looped track that reaches its end stops dead, and `Play()` always restarts from frame 0. `apply()` saw the stopped track while its weight was still fading and played it again.
- **Fix in `apply()`:**
  - A one-off track freezes on its last frame (speed 0, `TimePosition = Length - 0.001`) once it is within 0.03 s (real time) of its end, and holds there while it fades out.
  - The margin was first `2·dt`, which skipped half a clip after an 81 ms frame; it is now a fixed 30 ms.
  - If a long frame lets a track reach its end anyway, the next frame replays it **frozen at its end** (not from the start).
  - New `rig.wanted` (last frame's targets): a one-off clip wanted again while fading (a second corner swing) restarts from 0.
  - `shoot()` clears the stale weight of a track that stopped by itself.
- **Stance-bound body clips:** `Shot.stance`. GettingUp, LastStandWakeup and DodgePrep hold full weight until their stance ends, then fade at the same rate as the height ease. Before, they handed back to the standing Idle while the hips were still lowered, which sank the legs 0.55 into the floor.
- **Tested:** dive run-up and landing (hold at end, no restart), corner swings ×2, reload, two draws.

### 2. Stance height changes without free-fall (CharacterController, AimLayer, CameraController) ✅ tested
- **Problem:** lowering the hip height (crouch, low cover, run-up, Last Stand) made the root **free-fall** for about 0.12 s. The aim layer's height hold faded before the root arrived, and the body sank up to **0.98** into the floor. The drop also briefly played the Fall clip, and the camera popped up then down.
- **Fix:**
  - `CharacterController.applyHeight`: on the ground the root now moves with the hip height in the same frame (`root.CFrame += rise`). Not for `AIRBORNE` stances: DodgeAir, DodgeGround, Vaulting, Dead.
  - `CameraController.absorbRise(rise)`: the view holds and eases to the new height (`heightHold`, rate 10).
  - `AimLayer` height hold: measured from **last frame's** root (`lastY`), carrying over any unfinished hold (`hold`). `FALLS` now includes Vaulting.
- **Result:** crouch-down dip 0.98 → ≤0.11; Humanoid stays in Running (no Fall clip); camera smooth. Standing back up still dips about 0.3 for ~0.1 s. That's joint-angle blending between a deep crouch and straight legs, not fixed (see To do 4).

### 3. Corner clips start and end on the cover idle (to-do item 4) ✅
- `mp_stances.cover_corner`: keys at 0 / 0.175 / 0.35 s. The first and last keys are exactly `cover_high`/`cover_low` at rest (checked: within 0.08°). The middle key squares up (high: root yaw −10°, crossover step; low: yaw −8°, trailing foot closes up). High corner now floor-guarded.
- In game: the corner clip holds its end frame and blends into the idle with no jump.

### 4. Carried two-handed gun fixed in every pose (new; found in testing) ✅ tested
- **Problem:** with a one-handed gun out, the carried rifle (left hand) went through the floor in almost every pose except standing:
  - crouch −0.92 (seen on screen: barrel straight down)
  - crouch walk −1.0 to −1.16
  - low cover −0.9, getting up −0.74, dive landing −2.8
  - sprint −0.25; strafes cut into the legs; high cover poked into the wall
- **Fix:**
  - `CarryTwoHanded` retuned: grip −1.55, −0.9, −0.05; muzzle 28° down (was 40°).
  - New `CarryTwoHandedLow` (made on the crouch body: held at the left side, barrel level, pointing out left-forward) for Crouching, CoverLow and GettingUp.
  - New `CarryTwoHandedCover` (nearly vertical beside the left leg) for CoverHigh.
  - `AnimationController.carryFor(stance)` picks the clip.
  - Safety net `AimLayer.liftCarried`: swings the left arm up at the shoulder just enough to keep the gun's box 0.12 above the floor under the character (binary search, max 120°). It asks for extra room by the root's fall speed × dt, because it runs before physics.
- **Measured in game:** crouch AK +0.85; low cover +0.56 and 0.26 from the wall; high cover 0.48 from the wall; whole dive ≥ +0.09; lying +0.36.

### 5. Low cover holds and blind fire (to-do items 2 and 3) ✅ tested
- "Gun up beside the face" is impossible: the hunched R15 chest lies on the thighs and the 2-stud torso fills the space beside the head. MP3 holds the gun low in cover, so the low holds are a crouched low ready:
  - `CoverHoldLowOne`: pistol beside the right knee, muzzle 60° down.
  - `CoverHoldLowDual`: mirrored.
  - `CoverHoldLowTwoRight/Left`: rifle low across the front by the feet, muzzle along the wall; per side, because the body turns ±24° per side.
  - Upright ones renamed `CoverHoldHighOne/Two/Dual`.
- `BlindFireLowRight/Left` (per side) key the **right arm + Waist** (waist −28°, yaw +s·18° to square to the wall). An R15 arm from the crouch reaches only the top edge of a 3.6 wall, so the slide clears the top by 0.26–0.30 with the hand at the edge. The head stays at 3.42 (under 3.6). On taller low cover the shots go into the wall.
- `BlindFireHigh*`: right arm only (the left hand used to lift the carried AK onto the wall).
- **Measured:**
  - pistol hold +0.47 above the floor, 1.03 from the wall
  - rifle hold +0.16, 0.58 from the wall, support hand 0.00 off
  - dual: M9 +0.47, Uzi −0.02

### 6. Low cover drift fixed (new; found in testing) ✅ tested
- **Problem:** the cover mover always pushed the root toward `GAP` 1.15, but the hunched low pose reaches 2.2 studs (this avatar) to 2.8 (default R15). The head pressed into the wall (0.36 in), physics deflected the push sideways, and the character **slid along the wall at about 0.4 studs/s**, past the wall's end.
- **Fix (`CoverController`):** the target gap is `max(GAP, reach + 0.05)`.
  - `reach` is how far Head, UpperTorso and LowerTorso reach toward the wall (`bodyReach`), held at its maximum since the stance began (`reachHeld`, reset on stance change), so blind fire straightening the back doesn't pull the body in.
  - Deadband 0.08.
- **Result:** 0.00 studs drift in 16.8 s; root 2.24 from the wall; head front within ±0.03 of the wall face.

### 7. Lying poses float less (to-do item 5) ✅
- `mp_stances.LYING = −0.06` clearance for `dive_impact`, `on_floor` (DodgeGround, LastStand, wake-up start) and the Last Stand sitting key. The clips' floor guards use `floor + LYING` too.
- DodgeGround lowest point in game: 0.18 → **0.10**. Not checked on a default blocky avatar (boxes sink 0.06 by design).

### 8. Vault rebuilt so the legs clear the obstacle (to-do item 6, vault) ✅ tested on the gun table
- **Problem:** with the root only 1.5 above the top, even the pelvis barely cleared. The legs went about 1 stud through the gun table, and the clip ran on the clock while the obstacle's place in the vault varies.
- **Fix:**
  - `VaultRules`: `APEX_ABOVE_TOP = 2.1`, `MIN_RISE = 1`. `Vault` gains `near`/`far` (ground distance to each face). `position()` rises (cubic ease-out) to the apex height by the near face, stays level across, and drops (cubic ease-in) after the far face. The self-check was updated. The server only uses `find`, so this is client-side.
  - `VaultController.progress()` returns travelled, near, far and total (studs).
  - `AnimationController.vaultShare()` maps progress to the clip: legs tucked (25 %) when the leading knee reaches the near face (1.3 ahead of the root), still up (72 %) until the trailing foot passes the far face (0.9 behind). The clip chases that point with its playback speed (≤6), which also replicates.
  - New Vault clip: speed vault. Pelvis tips up to 65° toward the left hand, legs swing out right (hip roll 65–80), tucked 0.15–0.43 s, reach forward under the body at 0.52.
- **Simulated** (wall 3.6×2, table 2.6×3, crate 3.8×4, low 1.5×1, max 4.3×1): clearance +0.14 to +0.24.
- **Game, gun table:** +0.03 to +0.65 over the crossing; −0.06/−0.12 for 2 frames at take-off when starting 1.3 studs from the table (accepted).
- Arc is visibly higher than before: hips about 1.35 above the top.

### 9. Pipeline check
- Blender rebuild reproduced all 86 committed clips exactly before changes. Now **93 clips**: +11 added, 4 removed (CoverHoldOne/Two/Dual, BlindFireLow), 16 changed.
- Exported to `Exports/keyframes.json` and imported. Every slot has a clip, none unused.

---

## To do (in order)

### 1. Save and push
- [ ] **Save the place in Studio.**
  - **Who:** whoever opens Studio next.
  - **How:** File > Save to Roblox.
  - **Why:** session 3 changed 13 scripts (see [[#Scripts changed in session 3]]), and the place is the only copy of the game's code.
- [ ] **Push the session 3 commits** to `origin/main` (github.com/joransss/Maximum_Pain, a public repo).
  - **Who:** JackT6785. They were committed on that PC and haven't been pushed, because it's JordanSaa's repo.
  - **What:** `3634cce` (bytecode), `7f86ec1` (Blender export and `.blend`), `a608dc7` (notes), and the 2026-11-03 notes update.
  - **How:** in GitHub Desktop, Fetch origin first. If it offers Pull origin (JordanSaa pushed after `ac50a40`), pull and resolve any clash in the notes, then Push origin.
  - **Check:** GitHub shows the commits, and no screenshots (`Pasted image *`), `__pycache__` or FBX copies went up.
- [x] Commit the Blender scripts and `Exports/keyframes.json` (done in `ac50a40`).
- [x] Stop tracking `__pycache__` (`3634cce`).
- [x] Commit session 3's export fix, the `.blend` and the notes (`7f86ec1`, `a608dc7`), then the detailed notes update (2026-11-03).
- [ ] **Optional, JordanSaa's call: keep the game's code in git.** A saved `.rbxl` (or exported scripts) in the repo would give a backup and a history of the code. But the repo is public, so anyone could copy the game.

### 2. Play tests
- [x] Everything on the session 2 list below, done in session 3 (see above), apart from:
- [ ] **Two clients.**
  - **Start it:** Studio > Test tab > Clients and Servers, 2 players, Start. A server window and two player windows open. Do each thing with Player1 and watch it from Player2's window.
  - **Already checked from the server's side** (session 3): stance and hip height changes, the root's smoothed drop, and the Vault clip's speed chase all replicate.
  - Checks:
    - [ ] **Crouch and stand (C):** the other body drops at once and eases down, with no fall clip and no float.
    - [ ] **Vault (Space at the LowWall, −10, 86):** the clip is paced by the way over, and the legs clear the top as seen from Player2.
    - [ ] **Dive** (V or Left Alt with a direction): the flight, the landing on (not in) the floor, lying, getting up.
    - [ ] **Last Stand** for real: Player2 shoots Player1, who has a painkiller and a loaded gun. Check that the drop is instant, the body lies on the floor, and the wakeup.
    - [ ] **Drop (G) and pickup (F):** the gun lies at the same spot on the floor in both windows, and the other player can pick it up.
    - [ ] **Reloads:** does Player2 see Player1's magazine drop and the bolt move? Probably not (see 4.13), so note what happens.
    - [ ] **Hits:** flinches on the other body, the death ragdoll, and the kill cam on the dying player's screen.
    - [ ] **Bullet time between players:** Player1's line of sight slows Player2 (`TimeScale`), with the aim penalty, and a counter-activation clears it.
    - [ ] **Clips:** in Studio each client registers a clip the first time its own character loads it, so Player2 may not show one of Player1's clips until Player2 has used it too. Note any default poses. Live servers use published ids and don't have this limit.
- [ ] **Optional:** add the session 3 test harness to the repo, so the next tests don't start from scratch (see [[#How to resume (tools and tricks)]]).

<details><summary>The session 2 list, for reference (all done in session 3 apart from two clients)</summary>

- [ ] **Vault over the LowWall** (−10, 86) and a crate (−45, 100), from standing and **straight out of low cover** (Space in CoverLow). Check: no Fall clip, no body lag at the start (Vaulting is now in FALLS/AIRBORNE), legs clear, landing.
- [ ] **Last Stand:** set the server attribute `Adrenaline = 1` on the character (the meter runs 0 to 1; this list said 5) and the Gunman's `Hostile = true` (the TestArena loop polls it), stand in its sight. It hits the torso for 18 every 0.8 s until the killing blow. Fire at it during the 4 s window to survive. Check: LastStandFall → LastStand → LastStandWakeup (bound to GettingUp, 3 s); root teleport down 2.2 then up; lying height; carried gun guard.
- [ ] Dives Back/Left/Right (V+S/A/D), DodgeGround spin, GettingUp.
- [ ] Reloads for every gun with marker effects; pickup (F), painkiller (H), drop (G).
- [ ] Low cover: slide along the wall (A/D) with the new gap; stop at the ends; low corner swings (crates); pop up (aim) and back (the root moves 1.1 closer while popped up? CoverAim speed is 0, so it shouldn't move; check).
- [ ] High cover: blind fire round the edge with right arm only; pop out with the AK carried.
- [ ] Bullet time on a vault and a crouch (time scales).
- [ ] **Two clients** (Studio Test > 2 players): root teleport on stance changes and the vault clip's speed chase replicating. Temporary animation ids don't replicate in Studio, so this mostly checks positions.
- [ ] Output log clean after a full run. The only warning seen was the speed check undoing my own test teleport.

</details>

### 3. Low-cover pose (decision)
**Who decides:** JackT6785 and JordanSaa.

**The current pose:** behind low cover the R15 crouches facing the wall, hunched far over to keep its head under the top. In `mp_stances.cover_low` the root is pitched 32° forward, the waist 46°, and the neck turned 56° back up. The head reaches 2.2 to 2.8 studs ahead of the root (2.46 on JackT6785's avatar). So the root stays that far from the wall and the feet about 2.2 back, with the head touching the wall. Max Payne 3 crouches side-on to low cover instead.

| | Keep: hunched, facing the wall (current) | Side-on crouch (like Max Payne 3) |
|---|---|---|
| Look | Reads as taking cover, but the body sits well back from the wall, leaning in | Closer to Max Payne 3 |
| Head reach ahead of the root | 2.2 to 2.8 | 1.09 (tried in Blender in session 2 with `LOW_TURN` 70° and `LOW_BACK` 0.3, then reverted; neither is in the code now) |
| Clipping and drift | None known: since session 3 the gap holds through popping up, sliding and corners | Untested in game |
| Wall ends | The head stays in front of the wall | The head sits about 2 studs along the wall toward the end, and the root stops 0.9 from an end, so the head would stick out past wall ends |
| Work | None | Remake the 12 low-cover clips: CoverLowLeft/Right, CoverLowMoveLeft/Right, CoverCornerLowLeft/Right, CoverHoldLowOne, CoverHoldLowDual, CoverHoldLowTwoLeft/Right, BlindFireLowLeft/Right. Check `CarryTwoHandedLow` against the new body. Shift the body about 1.5 back along the wall at ends, or give low cover a bigger `EDGE_MARGIN` (now 0.9) in `CoverRules`/`CoverController`. Then re-run session 3's low-cover tests (slide, ends, corners, pop up and back, blind fire). |

**Recommendation:** keep the current pose. It's the only one with no known faults, and side-on is a rework of 12 clips plus the wall-end logic. Revisit it if it still looks wrong next to Max Payne 3 multiplayer footage.
- [ ] Decision made: keep (then remove the line from [[Cover System]]'s "Not done"), or side-on (then do the work in the table).

### 4. Polish
None of these blocks anything. Numbers are from sessions 2 and 3 on the avatars above.
- [x] **4.1 Standing up from a crouch dipped about 0.3 for ~0.1 s.** Done in session 3 as the foot guard in AimLayer: the body lifts while a height change eases out, and the feet stay within 0.05.
- [ ] **4.2 Arm transitions in cover.**
  - **Seen:**
    - Popping up from low cover and ducking back, the gun crosses the cover's top for 0.08 s (its box up to 0.82 inside).
    - Stepping out of high cover, the right forearm sweeps through the wall's corner (box 0.78 inside).
  - **Why:** the arms blend straight between the low hold and the aim (`AnimationController`: `AIM_IN` 18/s, `AIM_OUT` 7/s) while the body rises or steps out, so the gun cuts the corner.
  - **Ideas:**
    - Hold the aim back until the body has risen or cleared the corner.
    - Or lift the hold first, then point.
    - Or add a gun-against-cover guard in `AimLayer`, like `liftCarried` does for the floor.
  - **Check:** log the gun's box against the cover's top, and the forearm against the wall's corner, frame by frame while popping up/back and stepping out/in.
- [ ] **4.3 Dive landing forearm.**
  - **Seen:** the left forearm's box goes 0.30 under the floor for one frame at the impact.
  - **Why:** the root lands 0.2 low and springs back.
  - **Idea:** cap the landing's downward speed in the dive's flight (`DodgeController`) the way the vault now does, so one physics step can't end below the landing height.
  - **Check:** forearm boxes against the floor through a dive's landing.
- [ ] **4.4 Vault margin.**
  - **Seen:** in slow motion, the lowest leg point over the LowWall's front edge is +0.06: slim but clear.
  - **Idea:** raise `VaultRules.LEG_CLEARANCE` from 0.2 to 0.3.
    - Avatars taller than standard would fly about 0.1 higher; a standard avatar stays at `APEX_ABOVE_TOP` 2.1, and the self-check still holds.
    - The cost is a slightly higher hop and camera move.
  - **Check:** the bullet-time vault (see "Slowing the player" below) and the camera step.
- [ ] **4.5 Vault take-off and style.**
  - Taking off from very close (under 1.3 studs) brushes the near edge for about 0.05 s (−0.06/−0.12 for 2 frames on the gun table).
  - At the higher arc the left hand no longer touches the top from standing (it still rests on it from low cover).
  - A vault from a run starts on a running stride; a standing vault could start from idle.
- [ ] **4.6 `CarryTwoHandedLow` points the rifle out to the left.** That's needed so it clears low walls. Forward-down might look more like Max Payne 3 when crouching in the open: a separate crouch clip, with low cover keeping the sideways one. `AnimationController.carryFor(stance)` picks the clip.
- [ ] **4.7 The carried gun against walls.**
  - Only the floor is guarded (`AimLayer.liftCarried`), plus the high-cover carry clip.
  - **Idea:** a ray along the gun's box toward walls, swinging the arm in.
  - **Check:** walk along a wall and into a corner with a pistol out and the AK carried.
- [ ] **4.8 Sniper and shotgun carries** rely on the floor guard: they're too long for any fixed pose.
- [ ] **4.9 Blind fire over tall low cover.**
  - From the crouch, an R15 arm reaches the top of a wall about 3.7 tall. Over anything taller the gun stays below the top and the shots hit the wall.
  - **Idea:** stand up partly, by the wall's height, for taller low cover.
- [ ] **4.10 Wake-up hands.**
  - The carry clip overrides the left hand that the wake-up clip plants on the floor.
  - Also seen in session 3: the right hand's pistol box touches the floor (0.2) while that hand pushes up, and a holstered gun grazes the floor (0.08) while kneeling.
- [ ] **4.11 Wake-up forearm:** its box dips into the floor lying on the side (from session 2).
- [ ] **4.12 Leg IK.** The foot guard lifts the whole body. A full leg IK (each foot on its own floor, bending the knee) would help slopes and stairs.
- [ ] **4.13 Reload markers on other players' screens** (found reading the code; confirm in the two-client test).
  - `AnimationController` animates only the player's own character; other players' characters are animated by their own clients. So the markers (magazine out, bolt back) run only on the reloading player's client, and gun parts moved there don't replicate.
  - Others probably see the reload clip but no magazine or bolt movement.
  - **Idea:** each client watches other characters' Animators (`AnimationPlayed`) for reload clips and runs the same markers locally.
- Accepted as it is: the gun-arm pump lags the opposite leg by about 0.1 of a cycle.

### 5. Publish and document
- [x] `mp_lib.export(fbx=True)` for FBX copies; `MaximumPain_Animations.blend` saved in `Assets/Blender/Animation` (session 3).
- [ ] **Publish the animations.**
  - **Who:** JordanSaa, the account that owns "Untitled Experience". An experience only plays animations its own creator owns, so animations published from a collaborator's account won't load in live servers.
  - **Until then:** live servers play none of the clips. `AnimationConfig.resolve` only plays a KeyframeSequence directly in Studio, so `AnimationController` keeps Roblox's default `Animate` script, and the gun parts don't move on reloads.
  - **Steps:**
    1. Open the place in Studio as JordanSaa.
    2. Publish each of the 93 KeyframeSequences in `ReplicatedStorage.Assets.Animations` as an animation owned by JordanSaa (or the group, if the game moves to one).
    3. Paste each `rbxassetid://<id>` into the matching slot's `Id` in `AnimationConfig`. There are 100 slots for 93 clips: `ReloadPistol` serves 4 slots (Desert Eagle, M9, Glock 18, Uzi) and `ReloadRifle` 5 (AK-47, FAL, M4, MP5, SPAS-15), so those slots share an id.
    4. Publish the place and test in a live server: locomotion, cover, dives, vaults, Last Stand, every reload and its markers.
    5. When a clip changes later in Blender, re-export and re-import it, publish it again, and update its slot's `Id`.
  - Scripted publishing isn't an option for now: `AssetService:CreateAssetAsync` returned "not available yet", even from a plugin, when it was tried for the weapon kit (2026-10-30).
- [ ] After publishing: compare each clip with [[Max Payne 3 Animation Reference]] again (from [[Animation Hooks]]).
- [ ] Check the kill cam's death panel against Max Payne 3 multiplayer footage, with timestamps (from [[Max Payne 3 Kill Cam]]'s "Not done").
- [x] Removed the cover-to-cover wording ([[Changelog]], [[Cover System]]) and the out-of-date "no animations" and "no vaulting" lines.
- [x] Updated [[Architecture]], [[Animation Hooks]], [[Cover System]], [[Shoot-Dodge]], [[Last Stand and Bullet Time]], [[Movement State Machine]], [[Test Arena]].
- [x] New research notes: [[Euphoria-style Reactions and Ragdolls]] and [[Max Payne 3 Kill Cam]].
- [x] This note and the [[Changelog]] rewritten in detail (2026-11-03).

---

## How to resume (tools and tricks)
- **Blender:** `sys.path.insert(0, r"…\Assets\Blender\Animation")`, `import mp_lib as L, mp_locomotion as M, mp_arms as A, mp_stances as S, mp_hands as H`, `L.build_rig()`, `L.CLIPS.clear()`, then `M.register(); A.register(); S.register(); H.register()` (93 clips). `L.export()` (or `L.export(["Name"])`), `import mp_serve; mp_serve.start()`. In Studio **Edit mode**: `require(game.ServerStorage.Tools.AnimationImporter:Clone())()`.
- **Checks used:** `L.validate(clip, speed, dir)`; `L.render_sheet(clip, path, frames, views)` / `L.render_grid`.
- **Arm clips are chest-relative.** Author with IK on the body they'll play on, then check by FK on every body that plays them (rifle box vs floor, wall, body).
- **Studio testing:**
  - `execute_luau` runs in a separate VM (keep helpers in `_G` within one play session; re-install after restarting play).
  - Log on `RunService.PostSimulation` (that's what gets rendered next frame).
  - `script_grep` takes Lua patterns: no `|`.
  - Teleports trip the server speed check (2 strikes, then it moves you back). Walk instead, or vault the gun table (z 68.5–71.5, x −28…28). Spawn is around (0, 4, 0).
  - `player:SetAttribute("DebugLook", Vector2.new(yaw, pitch))` only applies when the value changes (nudge it by 0.001); yaw π faces +Z.
  - Debug camera: BindToRenderStep at Camera+50 with `_G.debugCamEye/_G.debugCamAt` in root space, restored on PreAnimation (re-install each play session).
  - The server's BulletTimeService resets `TimeScale`, so it can't be used to slow-mo a vault for screenshots.
  - The Studio MCP id can change after a reconnect (`list_roblox_studios`).
- Luau gotcha: `local a, b, c = if x then f() else nil, y, z` keeps only `f()`'s first value.
- **Learned in session 3:**
  - **Blender headless:** `blender --background --factory-startup --python script.py`, with Blender 5.2 at `C:\Program Files\Blender Foundation\Blender 5.2`. The script deletes the default objects, then `build_rig`, registers the clips, `export(fbx=True)` and `bpy.ops.wm.save_as_mainfile`. About 12 s for all 93 clips.
  - **Walking the character in tests:** the navigation tool doesn't move it (the control script cancels `MoveTo`). Bind a render step after the control script (`Camera + 20`) that calls `Humanoid:Move(direction)` toward each waypoint. Route round the gun table (x −28…28, z 68.5–71.5) and through the gaps in the wall row (x −23…−17 and −3…4 at z 85–87).
  - **Teleports:** a teleport replicates across two of the speed check's 0.5 s windows, so even one trips it and the character is moved back. Walk instead.
  - **Pickups:** the prompt picked is the one nearest the crosshair (the shoulder camera sits 2.6 to the right), so aim the camera at the gun. `ProximityPrompt:InputHoldBegin()` from the command bar doesn't trigger these prompts; press F with the keyboard tool.
  - **Firing without the mouse:** `Remotes.FireWeapon:FireServer(point, "Right")`. The server checks it like a click, but no local effects play.
  - **Slowing the player** (bullet time on them): give a dummy `Adrenaline = 1`, an `Aim` attribute (yaw, pitch) facing the player and `DebugBulletTime = true`. Each activation lasts 5 s, so re-arm it from a server loop.
  - **Naming playing clips:** `KeyframeSequenceProvider:RegisterKeyframeSequence` returns a content hash, the same id every time, so playing tracks can be mapped back to clip names.
  - **Shared state:** the command bar's `require` gives its own copy of a module (requiring StanceService gives empty `_records`). Use the game's attributes and remotes instead.
  - **Screen captures in play mode:** they work, but the scripted camera ignores `camera_position`. Take over the camera with a render step at `Camera + 50` (the debug camera trick above).
  - **The test harness** (about 220 lines, not in the repo yet). Installed in the Client datamodel as `_G.mp`, and re-installed after every play restart.
    - **Recording:** a recorder on `PostSimulation` logs each part's box, the guns' handles, the root, velocity, hip height, camera, stance, humanoid state, `TimeScale`, and every playing track by clip name (weight, time, speed).
    - **Helpers:**
      - `start()` and `stop()` begin and end a recording.
      - `clearance(obstacle)`: the lowest point over an obstacle's top, per frame.
      - `floorClearance(floorY)`: the lowest point against the floor.
      - `timeline()`: the stance, state and heaviest clips whenever they change.
      - `cameraJumps(limit)`: camera steps above `limit`.
      - `clipPeak(name)`: a clip's peak weight and when it was up.
  - **Reload checks:** pick each gun up from the rack with F, fire a couple of shots, reload, then compare each moving part's `C0` with its `RestC0`. Count the spent magazines in Workspace (a pistol reload with a rifle carried should drop one).
- **No weak-keyed tables keyed by instances** (`__mode = "k"`) for anything that must survive: entries vanish while the instance still exists. Keep the state on the instance (attributes) or in a plain table cleared when the instance leaves.

## Test log (session 3, 2026-11-02, Studio play mode)
| Test | Before → after the session 3 fixes |
|---|---|
| Vault from standing (LowWall, 2.46 back) | legs −0.19 → +0.23; Fall clip 0.16 → 0; camera step 1.17 → 0.62 |
| Vault over a crate (3.8) | legs −0.31 → +0.16 |
| Vault out of low cover | camera −1.35/+2.15 → 0.83; hand rests on the top (0.00) |
| Vault landing | bounce +0.20 (higher apex) → 0 |
| Vault in bullet time (0.3) | 1.40 s in the air; legs +0.06 (dense sampling); camera 0.22 |
| Dive launch / landing camera | feet −0.39 → +0.21 / pop +1.68 → smooth (0.56) |
| Get-up forced after 8 s | root rose by physics over 8 frames → moves at once |
| Turning while lying (8 angles) | lowest point +0.04 to +0.06; guns +0.38 |
| Last Stand drop / wakeup | free fall, feet −0.74, camera +1.77 → root drops at once, feet −0.05, camera 0.20 |
| Crouch / stand up | feet −0.11 / −0.14 to −0.30 → −0.05 |
| Reloads, 13 guns + dual | slides/bolts stuck back (FAL, M4, Desert Eagle); carried rifle dropped a magazine → all parts back, carried gun untouched |
| Reload timing | each clip stretched to its gun's reload (speed 0.81 to 1.15); table in session 3 |
| Drop (G) | hung in the air for the dropper; floated 0.45 → 0.03 above the floor for everyone |
| Pickup (F) ×14, painkiller (H) | worked (torso 82 → 100, painkillers 3 → 2) |
| Low cover slide / ends | 8 studs/s; stops 0.74 to 0.85 from the ends |
| Low cover corner swing (crates) | never swung → swings, twice in a row, nothing in the crate |
| Low cover pop up and back | ducking back lunged 0.57 into the wall → gap steady at 2.54 |
| High cover blind fire / pop out | right arm only; shots round the corner; carried AK ≥ 1.29 from the wall |
| Network (server's view) | stance, hip height, the root's drop and the Vault clip's speed chase replicate |
| Output log | clean |

## Test log (session 2)
| Test | Result |
|---|---|
| Dive landing, run-up | Clips hold their end frame; landing body on the floor (+0.11…+0.18) |
| Get up after a dive | Dip 0.55 → within ±0.07 |
| Crouch down / up | Dip 0.98 → 0.11 / ~0.3 for 0.1 s; no Fall clip; camera smooth |
| Corner swings ×2 | No restart, smooth blend into idle |
| Reload, draws | Play once, hold end, fade |
| Carried AK | Crouch +0.85, low cover +0.56, high cover 0.48 off the wall, dive ≥ +0.09 |
| Low cover holds | Pistol, rifle, dual all clear of floor and wall |
| Blind fire low | Slide 0.26–0.30 above a 3.6 top; head under the top |
| Low cover drift | 0.4 studs/s → 0 |
| Lying height | 0.18 → 0.10 |
| Vault (gun table) | Legs +0.03…+0.65 over the top (was about −1) |
