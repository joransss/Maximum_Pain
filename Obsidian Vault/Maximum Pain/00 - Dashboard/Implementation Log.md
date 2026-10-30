# Implementation Log

## 2026-10-30 — Combat sandbox (Claude Code)

**Status:** implemented in Roblox Studio and tested solo against the Studio test dummy. **Not yet tested with two clients**, so no milestone is marked complete (see [[Acceptance Test Plan]]).

### Controls
| Action | Input |
|---|---|
| Fire (semi-auto) | Left mouse |
| Reload | R |
| Use medicine | Q |
| Shoot-dodge (any direction from WASD; no input = current movement, else camera forward) | Left Shift |
| Bullet time (toggle) | F |
| Pick up weapon / ammo | E (prompt); medicine is automatic |
| Aim (ADS) | Hold right mouse |

Keys live in `ReplicatedStorage.Shared.GameConfig.Controls`.

### What exists in Studio
See [[Script Registry]], [[RemoteEvents]] and [[Roblox Explorer Structure]] for the full list.
- `9mm Pistol` tool (WeaponId `Pistol9mm`) in `ReplicatedStorage.Assets.Weapons` and a copy in `StarterPack` (kept on purpose for now).
- Combat HUD `StarterGui.CombatHUD` (static layout, editable in Studio).
- Studio-only `Workspace.TestDummy`, `Workspace.Map.TestCover` wall, 3 medicine spawns in `Workspace.Map.MedicineSpawns`.
- `StarterCharacterScripts.Health` (empty) disables Roblox's default health regeneration.
- `StarterPlayer`: camera zoom 6–14 studs, built-in shift-lock disabled (Shift is the dive key).

### Design decisions made in this pass
- **Bullet time (user decision; supersedes "activator unaffected" in [[Combat Architecture and Implementation Plan]]):** triggers only if an enemy is in view of the activator or the activator is in view of an enemy: clear line of sight within 80 studs, and either character faces the other within a 140° cone. Activator: movement, fire rate and bullet speed ×0.6, aim free. Victims (everyone in view): movement, fire rate, bullet speed ×0.3 and mouse aim sensitivity ×0.3. Targets are acquired and released at 10 Hz; the session ends after 0.5 s with nobody in view, at 3 s, at 0 meter, on death, or on toggle. First activator wins: victims cannot activate, and other sessions cannot slow an activator. Meter: 100 max, 25 to activate, 15/s drain, +5 per hit, +25 per kill. No chain propagation (B → C) yet.
- **Shoot-dodge:** 0.65 s driven dive at 45 studs/s with 0.35× gravity for longer air time. Walls never end the dive: velocity into the wall is removed and the body slides along it. After landing the player **stays prone until a movement key is pressed**, then gets up (0.35 s recovery). Firing is allowed while diving, prone and in Last Stand. A reload in progress continues during a dive.
- **Health and medicine** ("medicine" replaces "painkillers"): 100 HP, no regeneration. Medicine heals 40 (1 s cooldown), carry max 5, start with 0. Medicine spawns refill after 30 s.
- **Last Stand:** lethal damage while carrying ≥1 medicine downs the player (once per life) for 4 s at 1 HP. Killing the player who downed you consumes 1 medicine and restores 30 HP (+100 LAST STAND). Any damage while downed eliminates. Timeout eliminates, with credit to the original attacker.
- **Ballistics:** server-simulated bullets with travel time (900 studs/s, scaled by bullet time), 300 stud range, 0.6° server-side spread, headshot ×2. No lag compensation.
- **Drops on death:** every carried weapon with its remaining ammo, plus all carried medicine as one pickup; 40 s lifetime. A same-type weapon pickup gives ammo only (capped at 60 reserve). Shortcut: a 2-weapon cap stands in for the loadout package rules until a second weapon type exists.
- **Score:** Kill 100, Headshot +50, Shoot-dodge +50, Bullet time +25, Last Stand comeback +100 (leaderstats `Score`, `Kills`).
- **Test dummy:** Studio-only test fixture, a deliberate exception to the PvP-only rule. It never attacks. It takes damage, respawns after 3 s, faces the nearest player it can see and shows its line-of-sight state. `TestDummyService` deletes it on live servers.
- **Audio:** Pro Sound Effects (Roblox-licensed): 9mm Beretta shot `9114714021`, gun handling for reload `9116345318`.

### Verified (Studio, one client, 2026-10-30)
- Fire → server ammo 15 → 12 and dummy 100 → 40 HP (3 × 20 body damage).
- Headshot and bullet-time kill → 175 points (100 + 50 + 25); kill marker and pop-ups shown.
- Bullet time: player Activator ×0.6 (WalkSpeed 16 → 9.6), dummy Victim ×0.3, meter charged 25.
- Dive right: horizontal head-first pose, about 32–37 studs, server `Diving → Prone`; prone holds still (no jitter) until W, then upright.
- Forward dive into `TestCover`: stopped at the wall, no clipping; dive state ran its full duration.
- Medicine pickup (+1 each, spawn hides and refills), Q heals 30 → 70 HP, no health regen.
- Last Stand: downed at 1 HP, prone on back, banner and countdown shown; timeout eliminates; drops created pistol (10/0) and medicine (1).
- Same-type pickup: 15/0 → 15/15; ground pickup removed.
- Malformed / NaN / far-origin / spammed remotes: no errors; 30 spammed shots → 1 accepted.
- No Output errors after fixes.

### Not verified
- Two clients: player-vs-player damage, `ShotEffects` on other clients, victim aim slowdown on a real player, Last Stand comeback, simultaneous lethal damage, overlapping bullet-time sessions.
- Latency, performance at full player count, gamepad, other resolutions.
- R6: the place still spawns **R15** characters (Game Settings → Avatar → R6 is needed; it can't be set by script).

### Known issues / follow-ups
- Gun arm does not track aim while diving or prone (needs authored R6 animations); shots still go to the crosshair.
- No server-side movement-bounds check on dives (client-owned physics).
- No damage-direction indicator, kill feed or dry-fire sound yet.
- Bullet-time victim aim slowdown is client-side and cannot be enforced by the server.
- Pickup prompts: Roblox shows one prompt per key, so overlapping pickups need the player to step closer (drops are spaced 2.5 studs apart).

## 2026-10-30 (later) — Slow-motion dive, aiming, recoil, auto medicine, dot cursor, poses

**Status:** implemented and tested solo in Studio on **R6** (the place now spawns R6). Not yet tested with two clients.

### Changes
- **Slow-motion dive (Option 1):** bullet time now applies to the dive. The dive runs in slowed time: speed and lift ×s, gravity ×s², duration and recovery ÷s, so it covers the same distance more slowly. If bullet time starts or ends mid-dive, the current motion is rescaled. The server stretches its `Diving` and `Recovering` timers by the same scale.
- **Medicine pickup is automatic:** walking within 3.5 studs of medicine picks it up (server proximity check at about 7 Hz; it also works when standing still or prone on it). Prompts removed. At max carry it stays on the ground.
- **Aiming (ADS):** hold right mouse (gamepad: left trigger). Zoom ×0.72, tighter shoulder camera, mouse sensitivity ×0.7, walk speed ×0.6 (server-applied), spread ×0.3 (server-applied). The server owns the aiming state (`SetAiming`); unequipping stops aiming.
- **Recoil:** camera kick (×0.6 while aiming) that fully recovers, plus server-side **bloom**: +0.5° spread per shot up to +2.5°, decaying 4°/s. The gun arm kicks visibly and other players see it too. Hip spread raised 0.6° → 1.2° so aiming matters.
- **Cursor:** the reticle is a single round precision dot.
- **Poses (procedural, R6 and R15, visible to all players):** hip = gun arm on the aim, one-handed. Aiming = both hands on the gun and the head follows the aim. Diving/prone = arms stretched ahead and legs together. Aiming while diving/prone (and in Last Stand) = arms on the aim from the lying body. Smooth ~0.15 s blends. Aim direction replicates at ≤10 Hz (`AimDirection`, unreliable).
- **Bug fixed:** on R6 the dive never ended in prone (the landing check was too short for an R6 body lying on its side); the probe went from 1.6 to 2.6 studs.

### Verified (Studio, one client, R6)
- Bullet-time dive at ×0.6: window 1.11 s versus 0.67 s at normal speed; distance 26.7 versus 26.1 studs; lands prone; server `Diving → Prone` stretched.
- Walking onto the 3 map medicine spawns: 0 → 3 automatically.
- Aim on: server `Aiming = true`, walk 16 → 9.6, FOV 70 → ~51, aim direction replicated. Aim off: walk back to 16.
- Hip pose: gun arm aligned with the aim (dot 1.00), left arm hanging. Aiming pose: both hands on the gun (1.6 studs apart); firing while aiming works and the arm kicks.
- Prone + aiming: gun arm aligned with the camera aim (dot 1.00) while the body lies flat. Prone, not aiming: arms stretched ahead (0.92 along the body).
- No Output errors.

### Not verified
- **Visual check of the poses:** Studio's 3D view rendered black during this session's screenshots, so the poses were checked numerically only.
- The spread and bloom numbers themselves (code path exercised, dispersion not measured), other players seeing poses and arm kick, gamepad aiming.

### Known issues
- In slow motion the dive arc peaks higher (~2.5 studs above the start versus ~0.5 at normal speed); cause not pinned down. Tune with `Dodge.Lift` / `Dodge.GravityScale` if it feels floaty.
- Procedural poses are a stand-in for authored R6 animations; there are no reload, hit-reaction or landing animations yet.

## 2026-10-30 (evening) — Dive arc fix, run-up, get-up, reload animation, sprint, crouch, cover, accuracy, state machine

**Status:** implemented and tested solo in Studio on R6 in the new test arena. Not yet tested with two clients. Studio's 3D view still rendered black in screenshots, so poses were checked by measurement, not visually.

### Controls (new)
| Action | Input |
|---|---|
| Sprint | Hold Left Ctrl |
| Crouch | C (toggle) |
| Cover | V near a wall (toggle); S pulls away; A/D slide; hold A/D at an edge to round the corner; aim at a high-cover edge to peek |

Shift stays the dive key; all keys live in `GameConfig.Controls`.

### Changes
- **Slow-motion dive arc fixed:** vertical motion is now integrated by the dive script (the lift force makes physics apply the same gravity). Contacts can only remove speed. Result: peak +0.74 studs at normal speed versus +0.84 in bullet time (was +0.5 vs +2.6).
- **Shoot-dodge run-up:** 0.15 s `Windup` (÷ bullet-time scale) with a lean into the dive direction, then launch. Firing and aiming are blocked during the run-up. The server runs `Windup → Diving → Prone`. Diving from sprint, crouch or cover is allowed and clears the stance.
- **Get-up:** movement input → `GetUp` (0.5 s ÷ scale): push-up pose while the humanoid stands; at the end the character is forced upright if still lying, and the server's `Recovering` state times out. No firing or new dive during recovery.
- **Reload animation:** gun held in front of the chest; the support hand goes to the gun → down to fetch a magazine → back in → racks the slide. Phases come from `WeaponConfig.ReloadPose` (weapon-specific) and are timed by the server's `Reloading` attribute, so the animation ends when the server moves the ammo. Other players see the animation and hear the reload sound. Unequip or death still cancels without moving ammo.
- **Sprint:** hold Left Ctrl, ×1.6 speed (server-set). Cannot fire or aim while sprinting: firing or aiming ends the sprint, and the next click fires. Not allowed in cover (leave cover first). A reload continues through a sprint. Pose: forward lean, gun carried low.
- **Free crouch:** C toggles, ×0.5 speed, no jumping, spread ×0.7. The body really lowers by 1.6 studs (server-set `HipHeight`), so **server hitboxes match what players see**. Standing up is refused under an overhang ("NO ROOM TO STAND", server Blockcast). Distinct from low cover.
- **Cover:** V near a wall (≤3.5 studs, in the camera direction). The server raycasts and classifies the wall by height: **high** (≥4.8 studs, standing) or **low** (≥2.4, crouched). The character faces the wall at 1.1 studs and slides with A/D (client-driven, server speed-guarded). It stops at endpoints, and holding a direction there for 0.35 s rounds **inner and outer corners** (the server re-validates the new wall). **Peek:** aiming at a high-cover edge steps out 1.6 studs; aiming in low cover pops up (server posture). Blind fire from cover is allowed at spread ×2. Reloading works in cover. The server drops cover if no wall stays behind the character for 0.5 s.
- **Accuracy modifiers (server, `GameConfig.Accuracy`):** standing 1, walking 1.5, sprinting 3 (firing blocked anyway), crouching 0.7, airborne 2.5, diving 1.3, prone 0.9, cover blind fire 2, peeking 1; aiming ×0.3 on top. Progressive bloom and camera recoil are unchanged (separate systems).
- **State machine:** `ReplicatedStorage.Shared.CharacterStates` is the single rule set (see [[Combat State Machine]]). The server validates stance, dive, aim and fire requests with it; clients use it to predict input; PoseController uses the same states with a fixed priority, so poses never compete.
- **Exploit prevention:** new `RequestStance` remote (rate-limited, validated). Cover is checked by server raycasts; stand-up clearance by server Blockcast; the muzzle must be reachable from the head (directly or by raising the gun over low cover), so shots can't start on the far side of a wall. A **movement guard** pulls a character back after two consecutive 0.5 s samples above the state's allowed speed (×1.5 + 6). It tolerates one-off teleports, lag and speed-limit changes (the previous limit is honoured for one sample).
- **Test arena** (`Workspace.Map.TestArena`, west of spawn): `HighWall` (20 long, 8 tall), `CornerWall` (L with HighWall: inner + outer corners), `LowWall` and `Crate` (3.5 tall low cover), `Pillar` (4 outer corners), `Overhang` (underside 4.0: crouch-only).

### Verified (Studio, one client, R6)
- Dive: run-up 0.14 s (0.23 s at ×0.6); landing 0.78 s vs 1.32 s; peak +0.74 vs +0.84; get-up ends upright and `Running`.
- Sprint: walk 25.6, `Fire` and `Aim` refused, spread ×3. Crouch: walk 8, hip −1.6, jump 0, root 3.0 → 1.4, spread ×0.7.
- Under the overhang, C → "NO ROOM TO STAND" and still crouched; in the open → stands (hip 0, walk 16).
- High cover: snap to 1.1 studs, slide at ~7.2 studs/s, stop at the endpoint, outer corner → end face → back face (server normals followed). Inner corner at `CornerWall` (turned to face −X). Cover granted from 3.25 studs.
- Peek: aiming at the edge stepped out 1.57 studs; shot accepted, spread ×0.3; cover kept. Aiming at the wall face: shot refused (muzzle inside the wall).
- Low cover: crouched (hip −1.6, spread ×2 blind); aiming pops up (hip 0, spread ×0.3); shot over the wall accepted; release crouches again.
- Reload: support-hand phases measured (to gun → down → back → rack); server ammo 14/30 → 15/29 exactly as the pose ended.
- Movement guard: a client-side walk speed of 120 was pulled back (127 studs/s logged).
- Dive out of cover clears the stance. Malformed / NaN / spammed `RequestStance` and `SetAiming` payloads: no errors.

### Not verified
- Visual look of the sprint, crouch, cover, run-up and get-up poses (no screenshots); two-client replication of stances and poses; gamepad; slopes/stairs/ledges; corner transitions under latency.

### Known issues / limits
- R6 has no knees, so the crouch and low-cover pose is a low lunge; authored animations would look better.
- In high cover away from an edge, aiming points the gun into the wall (shots are correctly refused).
- The movement guard pulled back once during scripted test teleports. Watch for false positives in real play and tune `Movement.GuardTolerance`.
- Low cover must be ≥3.4 studs tall to hide a crouched R6 head (crouched head top is 3.4).

## 2026-10-30 (night) — Back-to-wall cover, peek & blind fire, corner wrapping removed, bullet holes and blood

**Status:** implemented and tested solo in Studio on R6, **with screenshots** (Studio rendered again). Not yet tested with two clients.

### Changes
- **Back-to-wall cover (Max Payne 3 style):** in cover the character's back is to the wall and it faces away from it. It eases onto the wall (~0.2 s) and turns smoothly instead of snapping. A/D slide along the wall; the ends of the wall stop you.
- **Corner wrapping removed** (it was too snappy). Endpoints are now just peek spots.
- **Peek and shoot:** aiming at a high-cover edge leans 1.6 studs out past the edge and turns the body to the target; aiming in low cover pops up (server posture) and turns to the target. Releasing aim returns to back-to-wall.
- **Blind fire:** firing without peeking (not aiming, or aiming mid-wall in high cover) keeps the body in cover and holds the gun out over low cover or around a high-cover edge, at **spread ×8** (`Accuracy.BlindFire`). The server decides peek vs blind fire itself: aimed accuracy applies only when the head has a clear line past the wall (`CharacterStates.Exposed`). The muzzle check also allows a gun held out along the wall then around the edge.
- **Impacts:** the server sends every bullet's real hit point (`ImpactEffects`, unreliable remote). Clients draw **bullet holes** on surfaces (dark discs, last 30 s, max 150, welded to moving parts) and **blood clouds** on characters. Because these use server hit points, they show the true spread and bloom.
- **Camera:** the shoulder offset is built from the camera's right vector, so the camera stays over the right shoulder even when the body faces the camera (back to wall). Body turns are smoothed (≈50 ms) so leaving cover doesn't snap.

### Verified (Studio, one client, R6, with screenshots)
- Hip and aim poses (side and front): arm, barrel and aim aligned; gun upright; head follows the aim. Sprint (forward lean, gun low) and crouch (low lunge) look right.
- High cover: back to the wall at 1.1 studs, gun up at the head. Aiming at the edge stepped out to x −19.5 (wall ends at −20) and turned to face the target.
- Peek fire: 5 aimed shots → 5 holes within 0.10 studs at ~12 studs range. Blind fire from the same spot: 5 shots → holes 3.8 studs off on average, up to 11.9.
- Blind-fire pose at the edge: gun arm reaches around the corner while the body stays in cover.
- Low cover: crouched back-to-wall; aiming pops up (root 1.4 → 3.0) and turns to the target; only the head, arm and gun show over the wall.
- Blood: 3 real hits on the dummy → 3 blood impacts, HP 100 → 40. Cloud rendered.
- No Output errors.

### Not verified
- Dive, prone and reload poses on screen this round (they were verified by measurement earlier). Two clients. Blood on another player (only the dummy).

### Notes
- One misclassification of the low wall as high cover happened right after a scripted teleport (the server still had the old position); a retry from the same spot classified correctly.
- Torso shots on R6 register on the invisible `HumanoidRootPart` (same box as the torso), so blood appears at the torso as expected.

## 2026-10-30 (late) — R15 migration: Blender animation suite, Animate state machine, R15 tuning

**Status:** implemented and tested solo in Studio on R15, with screenshots. Not tested with two clients. Animations are **not published** (Studio-only playback).

### Changes
- **Rig decision:** R6 → **R15** (user decision; supersedes "R6-first" in [[Combat Architecture and Implementation Plan]]). Everyone gets the **standard R15 body** (default parts and scale; avatar animation packs cleared) via `CombatService` after the avatar loads; clothes, accessories, face and colours stay. Same hitboxes for all, and clips line up.
- **40 Blender-authored clips** (repo `Assets/Blender/Animation/`, `.blend` in `Assets/Blender/`): locomotion with 4-way strafes, sprint, turn-in-place, crouch, hip/aim/cover holds, reload, recoil, 4-direction dive windup and air, land/prone/recover per side. Pipeline and clip list: [[Animation System]]. Clips live in `ReplicatedStorage.Assets.Animations`.
- **New `StarterCharacterScripts.Animate`** (replaces Roblox's default) and **`Shared.AnimationIds`** (paste published IDs).
- **`PoseController` rewritten:** only live aim adjustments now (chest turn onto the aim point, straight-arm aim while down, blind fire, head). Handles Roblox's new `AnimationConstraint` joints as well as `Motor6D` (the avatar uses AnimationConstraints).
- **`DiveController`:** no longer stops every animation track while diving/prone; landing probe 2.6 → 1.6 studs (lying R15 root rests ~0.6 up).
- **Tuning (`GameConfig.Movement`):** `CrouchDrop` 1.6 → 1.3; `HighCoverMin` 4.8 → 5.6 (standing R15 head top 5.4).
- **Test arena:** `LowWall` and `Crate` 3.5 → 4.0 tall; `Overhang` raised to 4.4 clearance. **TestDummy** rebuilt as a standard R15 rig.
- Backup of every changed script, the old R6 dummy and the old arena: `ServerStorage.PreR15Backup`.

### Verified (Studio, one client, R15)
- Studio rig posed from an imported clip matches Blender to 0.001 stud.
- Standard body applied (scale 1, HipHeight 2.192, default head); no avatar animation tracks; no warnings or errors.
- Barrel vs aim point: aimed 0.0°, hip 0.5°, aiming while prone 1.1°.
- Full shoot-dodge in game: Windup → `DiveWindup_F` → `DiveAir_F` (0.6 s) → `Land_Front` → `Prone_Front` → `Recover_Front` → Idle. Prone on the back after a side dive looks right on screen.
- Run plays `Run_F` at ~1.0× for 16 studs/s; walk→run blend on acceleration. Crouch: planted foot exactly on the ground; crouched head top 3.96.
- Reload clip plays at 1.0× for the 1.6 s server reload; a shot plays `RecoilHip` (Action3).
- In Blender: every IK target reached (except the reload support hand, 0.12 short); planted feet move < 0.7 studs/s median at authored speeds.

### Not verified
- Two clients / other players seeing clips (needs publishing). Cover poses, sprint, strafes and turn-in-place on screen. Bullet time playback. FBX import into Studio's Animation Editor (files exported, not import-tested).

### Known issues
- In game, run foot slip median ~1.7 studs/s (spikes at touchdown).
- Aiming from the ground: support hand doesn't reach the grip.
- No jump/fall, hit-reaction, death, climb or swim clips.
- "Avatar Type" in Game Settings must be R15 (not Player Choice); an R6 player would get no clips and no aim layer.

## 2026-10-30 (night) — Max Payne 3 animation reference (research; no game changes)

**Status:** documentation only.

- New note [[Max Payne 3 Animation Reference]]: every Maximum Pain animation compared against Max Payne 3, from Rockstar's official trailers on Steam ("Multiplayer", "Design and Tech Video 2 and 3", frames viewed at 5 fps; none stored in the repo) and interviews and reviews about the animation system.
- Main findings: Max Payne 3's weight comes from physics reactions (hits, deaths, collisions) layered on top of movement; players roll 360° to aim on the ground; the pistol is carried low when not firing.
- Gaps added to [[Development Roadmap]] (Milestone 2 and 4) and [[Current Sprint]]. Known minor issues logged in [[Bug Tracker]]. Combat Architecture plan updated for R15 (pillar 5, milestones 1, 3 and 6). [[Combat State Machine]] now describes the Animate / PoseController layers.
