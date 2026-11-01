# Animation and MP3 Systems: Progress and To Do

Work log for the Max Payne 3-style animation and movement pass (bullet time, vaulting, hit reactions, ragdoll, kill cam, Blender animations). Picks up where the [[Changelog]] entries of 2026-11-01 leave off.

> [!warning] Save first
> All script changes and the 93 imported clips live **only in the open Studio place**. Save it (File > Save) before closing Studio. The Blender scripts in `Assets/Blender/Animation` are changed but **not committed**.

Related: [[Architecture]] · [[Animation Hooks]] · [[Movement State Machine]] · [[Cover System]] · [[Shoot-Dodge]] · [[Last Stand and Bullet Time]] · [[Test Arena]]

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

### 1. Save, review, commit
- [ ] **Save the place in Studio.**
- [ ] Commit the Blender scripts and `Exports/keyframes.json` when the user asks (repo is public; no screenshots).
- [ ] Remove the `__pycache__/*.pyc` files from git and add `__pycache__/` to `.gitignore` (they change on every import).

### 2. Finish the play tests (not yet done this session)
- [ ] **Vault over the LowWall** (−10, 86) and a crate (−45, 100), from standing and **straight out of low cover** (Space in CoverLow). Check: no Fall clip, no body lag at the start (Vaulting is now in FALLS/AIRBORNE), legs clear, landing.
- [ ] **Last Stand:** set the server attribute `Adrenaline = 5` on the character and the Gunman's `Hostile = true` (the TestArena loop polls it), stand in its sight. Lethal on the 6th hit (18 torso damage, every 0.8 s). Fire at it during the 4 s window to survive. Check: LastStandFall → LastStand → LastStandWakeup (bound to GettingUp, 3 s); root teleport down 2.2 then up; lying height; carried gun guard.
- [ ] Dives Back/Left/Right (V+S/A/D), DodgeGround spin, GettingUp.
- [ ] Reloads for every gun with marker effects; pickup (F), painkiller (H), drop (G).
- [ ] Low cover: slide along the wall (A/D) with the new gap; stop at the ends; low corner swings (crates); pop up (aim) and back (the root moves 1.1 closer while popped up? CoverAim speed is 0, so it shouldn't move; check).
- [ ] High cover: blind fire round the edge with right arm only; pop out with the AK carried.
- [ ] Bullet time on a vault and a crouch (time scales).
- [ ] **Two clients** (Studio Test > 2 players): root teleport on stance changes and the vault clip's speed chase replicating. Temporary animation ids don't replicate in Studio, so this mostly checks positions.
- [ ] Output log clean after a full run. The only warning seen was the speed check undoing my own test teleport.

### 3. Low cover pose (decision for the user)
The hunched R15 head reaches 2.2–2.8 studs ahead of the root, so it now sits that far from the wall (feet ~2.2 back), leaning in with the head touching the wall. Options:
- **Keep** (current; no clipping, no drift).
- **Side-on crouch** (MP3-like, tried in Blender: `LOW_TURN` 70°, `LOW_BACK` 0.3 cuts head reach to 1.09). But the head then sits about 2 studs along the wall toward the edge, and the root stops 0.9 from an end, so the **head would stick out past wall ends**. That needs the body shifted back along the wall (~1.5) or a bigger low-cover `EDGE_MARGIN`. Reverted for now.

### 4. Remaining polish
- [ ] Standing up from a crouch dips about 0.3 for ~0.1 s (joint-angle blend between bent and straight legs). Options: a leg IK floor guard in AimLayer (raycast under each foot, lift with 2-bone IK; would also help slopes, stairs and other avatars), or easing the hold a little slower than the blend.
- [ ] `CarryTwoHandedLow` points the rifle out to the left (needed so it clears low walls). Forward-down might look more MP3 when crouching in the open (a separate crouch clip, low cover keeps the sideways one).
- [ ] Carried gun vs **walls** isn't guarded (only the floor), apart from the cover clip.
- [ ] Sniper and shotgun carries rely on the floor guard (too long for any fixed pose).
- [ ] Vault: take-off from very close (<1.3 studs) brushes the near edge for ~0.05 s. The left hand no longer touches the top at the higher arc. Vault from a run starts on a running stride (a standing vault could start from idle).
- [ ] Blind fire over low cover taller than about 3.7 can't reach the top (R15 arm length); maybe stand up partly for tall low cover.
- [ ] Wake-up: the carry clip overrides the left hand that the clip plants on the floor.
- [ ] From the earlier list: the wake-up forearm box dips into the floor lying on the side; the gun-arm pump lags the opposite leg by ~0.1 cycle (fine).

### 5. Export and document (from the old list)
- [ ] `mp_lib.export(fbx=True)` for FBX copies; save a `.blend` into `Assets/Blender/Animation`.
- [ ] **Publishing:** live servers need each KeyframeSequence published and its `rbxassetid://` in its `AnimationConfig` slot `Id` (93 clips).
- [ ] Remove the cover-to-cover wording: [[Changelog]] ("cover-to-cover moves") and [[Cover System]] ("No cover-to-cover moves"; also its "No animations" and "no vaulting" lines are out of date).
- [ ] Update these notes:
  - [[Architecture]]: AimLayer, `AimUpdate`, attributes, `absorbRise`, `bodyReach`, `VaultController.progress`.
  - [[Animation Hooks]]: slots incl. the new ones, layers, carry selection, vault pacing, markers, pipeline.
  - [[Cover System]]: low cover gap, holds, blind fire per side.
  - [[Shoot-Dodge]], [[Last Stand and Bullet Time]], [[Movement State Machine]] (root moves with the hip height), [[Test Arena]] (test log below).
  - New notes for Euphoria-style reactions and ragdoll research, and the MP3 kill cam research.

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

## Test log (this session)
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
