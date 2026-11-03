# Animation and MP3 Systems: Progress and To Do

Work log for the Max Payne 3-style animation and movement pass (bullet time, vaulting, hit reactions, ragdoll, kill cam, Blender animations). Picks up where the [[Changelog]] entries of 2026-11-01 leave off; session 3 (2026-11-02) is the newest.

> [!warning] Save the place
> The game's scripts and the 93 imported clips live in the Team Create place ("Untitled Experience", place 70765307359272). Save it (File > Save to Roblox) after each session. The Blender scripts, the clips' keyframes and the `.blend` are committed to the repo.

Related: [[Architecture]] · [[Animation Hooks]] · [[Movement State Machine]] · [[Cover System]] · [[Shoot-Dodge]] · [[Last Stand and Bullet Time]] · [[Test Arena]] · [[Euphoria-style Reactions and Ragdolls]] · [[Max Payne 3 Kill Cam]]

---

## Session 3 (2026-11-02): the play tests, the fixes they needed, and the export
Every play test on the list was run, in Studio play mode on a second avatar (JackT6785's R15: hip height 2.38, root part 3.38 above the floor; the session 2 numbers were on an avatar standing 3.23 high). Each problem below was measured, fixed in the game's scripts and measured again.

### 1. Vault ✅ (to-do 2)
- **Found:** the legs went 0.19 into the LowWall's top and 0.31 into a crate's. As the leading foot reached the obstacle the Vault clip was only at weight 0.78, so the standing legs still pulled the feet down. Every landing played the Fall clip for a frame (weight 0.16). The camera hopped 2 to 4 studs in a tenth of a second, and from low cover it dropped 1.35 and jumped 2.15 on the first frames.
- **Fixed:**
  - `AnimationController`: the Vault clip takes the body over at 30 per second (`VAULT_FADE`, a `Shot.fade`) instead of 10. Weight at the near face: 0.78 → 0.99.
  - `VaultRules.apexAbove(rootHeight)`: the apex rises with the avatar's legs, `max(2.1, 0.6 × root height + 0.2)`: 2.10 for a standard avatar, 2.14 for the session 2 avatar, 2.23 for this one, 2.54 for a tall Rthro.
  - `VaultController`: a finished vault ends in Running, not Freefall (no Fall clip). Its downward velocity is limited so the physics step can't carry the root below the landing; with the higher apex the feet hit the floor and the body bounced 0.2.
  - `CameraController.setVerticalLag(0.5)` while vaulting: the view takes half of each rise and fall at once and eases into the rest.
- **Result:** legs +0.23 over the LowWall, +0.16 over the crate; from low cover the left hand rests on the top (0.00). Slow motion samples the arc three times more densely and found +0.06 at the front edge (a slim but real margin). No Fall clip, no bounce, largest camera step 0.6 to 0.8 (was 1.2 to 2.2).

### 2. The camera and the root on every height change ✅
- **Camera:** `CameraController` now absorbs each hip height change itself, whoever made it, and `absorbRise(rise)` only reports the root jumping. Before, the root didn't jump on vaults from cover or dive landings, so the view popped (−1.35/+2.15 from cover, +1.68 landing a dive).
- **Server-forced stances:** the server's HipHeight reaches the client before the stance it forces (Last Stand, a wakeup, a timed get-up), so the client saw no change, never moved the root, and physics dropped or lifted the body over several frames. Into Last Stand this meant a 2.2-stud free fall, the feet 0.74 under the floor and the camera popping 1.77. `CharacterController` now remembers the hip height it last put the root at (`appliedHip`) and moves the root to the new height over the floor (`CoverRules.floor`). Last Stand now drops at once, with a largest camera step of 0.20.
- **Dive launch:** the feet went 0.39 under the floor for four frames, because AimLayer held the body at the run-up's lower height while the launch carried the root up. `DodgeAir` (and `Dead`) joined AimLayer's `FALLS`, matching CharacterController's `AIRBORNE`: +0.21.
- **Foot guard (to-do 4.1):** while a height change eases out, AimLayer lifts the body just enough that neither foot's box goes more than 0.05 under the floor beneath it (one ray per foot, at most 0.6). Standing up, crouching, dropping into Last Stand and the wakeup now stay within 0.05 (were 0.11 to 0.33).

### 3. Reloads, pickups, painkillers, drops ✅
- **All 13 guns and the dual reload:** each played the right clip, stretched to within 1 to 3% of the server's reload time, with no first-frame restarts and the right ammo after. Every marker moves the right part, and every part comes back.
- **Bug 1, slides and bolts stuck back after reloads** (FAL, M4, Desert Eagle). The engine can drop an instance's Lua handle while the instance still exists, so a weak-keyed table keyed by instances loses entries at random: a Motor6D key vanished after one garbage collection while the motor was still in the gun. BoltForward then took the racked pose as the rest pose. The rest pose now lives on the motor (`RestC0` attribute, `WeaponEffects.restPose`, shared with the gun kick). The same pattern was removed everywhere it appeared:
  - WeaponEffects: the kick, and the muzzle effects, which added a new shadow-casting light and three emitters to a muzzle on every miss.
  - WeaponController: the spray, bloom and ammo state.
  - AimLayer: each body's state.
  - ProceduralLayer.
  - HitReactions: the hit log the death push and the kill cam read.
  
  Only AimLayer's gun-box cache stays weak, on purpose.
- **Bug 2, reload markers moved every gun in the hands:** a pistol reload dropped a spent magazine from the carried rifle and racked its bolt. Markers now move the right-hand gun, or both pistols for `ReloadDual`.
- **Bug 3, dropped guns hung in the air** for the player who dropped them, where the gun left the hand. The move made in the drop frame never reached them, because the gun still belonged to their physics. For everyone else guns floated about 0.45: `GetBoundingBox` turns with the gun, so lying on its side its "height" is a width. In `LoadoutService`:
  - `layDown` measures the real lowest point and rests the gun on the highest floor under its middle and both ends.
  - A drop is laid down 0.1 s after it is let go (`SETTLE_DELAY`, with `DroppedAt` as the token so a stale lay-down can't move it).
  - `dropFront` keeps the gun short of anything ahead, turning it across the feet when there isn't room.
  
  Results, with both views agreeing:
  - **Open floor:** 0.03 above the floor.
  - **Against the gun table:** on the floor, 0.21 short of it.
  - **Swapped on the rack:** on the table top.
- **Pickup (F) ×14 and painkiller (H):** both work. The painkiller clip played once, the torso went from 82 to 100, and painkillers went from 3 to 2. The prompt picked is the one nearest the crosshair.

### 4. Low cover ✅
- **Sliding:** 8 studs/s, stopping 0.74 to 0.85 from the wall's ends.
- **Corner swings round crates were broken.** `CoverRules.outerCorner` probed for the end face from the 1.15 gap, but low cover keeps 2.2 to 2.8 now, so the probes started in front of the wall and never found it. It now takes the character's gap and returns the swing's middle point. Holding D went round two corners of CrateA in a row, with nothing in the crates.
- **Popping up:** the root does **not** move while popped up (the earlier question).
- **Ducking back lunged 0.57 at the wall** and the forearm went 0.83 into it, because the gap was re-measured on the upright pose. `CoverController` now remembers the reach of each cover stance for the whole time in cover, and eases it back (0.5 studs/s) only once settled (0.4 s), still, and not firing (1.5 s). The gap held at 2.54 through popping up and back. After a slide it eases back within the 0.08 deadband (head 0.07 to 0.13 off the wall; it was staying 0.2 out).

### 5. High cover, bullet time, the network, the log ✅
- **High cover:**
  - **Blind fire round the end:** right arm only. The left hand keeps the carried AK by the leg, and three shots left from round the corner and flew 52 to 102 studs.
  - **Popping out with the AK carried:** the AK never came nearer the wall than 1.29.
  - **Idle pose:** the right forearm rests against the wall (its box 0.25 in, flush to the eye).
- **Bullet time:** used the `DebugBulletTime` test hook on a dummy that could see the player.
  - **Vault:** 1.40 s in the air at 0.3 speed (0.45 s at full speed).
  - **Crouch and stand:** smooth, with the feet within 0.05.
- **Network (from the server's side, no second client yet):**
  - Stance and hip height changes replicate.
  - The root's drop arrives smoothed, with no steps over 0.5 except the vault's landing.
  - The Vault clip's speed chase replicates (1.86 → 0.86 → 0.98 seen on the server), and the clips' Studio-only ids reached the server.
- **Output log:** clean after the whole run.

### 6. Export ✅ (to-do 5)
- **Blender 5 support:** `mp_lib.bake` used `action.fcurves`, which Blender 5.0 removed. `_fcurves()` now reads the layered action, and older Blender versions still work.
- **Deterministic exports:** `clip_data` sorts each clip's tracks. A set's order changed every run, so every export rewrote `keyframes.json`; two exports are now byte-identical. The regenerated clips equal the committed ones (0 difference), so Studio didn't need a re-import.
- **FBX copies:** 93 clips in `Exports/FBX` (14.6 MB). Git ignores the folder; `L.export(fbx=True)` rebuilds it in about 10 s. Re-importing two of them gave 16 bones and the right frame ranges.
- **The `.blend`:** `MaximumPain_Animations.blend` holds the rig and all 93 clips as actions (1.95 MB).

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
- [ ] **Save the place in Studio** (File > Save to Roblox): session 3 changed 13 scripts in it.
- [x] Commit the Blender scripts and `Exports/keyframes.json` (done in `ac50a40`).
- [x] Stop tracking `__pycache__` (`3634cce`).
- [ ] Push the session 3 commits (made on JackT6785's PC, not pushed yet).

### 2. Play tests
- [x] Everything in the old list below, in session 3 (see above), apart from:
- [ ] **Two clients** (Studio Test > Clients and Servers, 2 players): watch another player crouch, vault (the clip paced by the way over), dive and drop into a Last Stand. The server side of this checked out in session 3.

<details><summary>The session 2 list, for reference</summary>

- [ ] **Vault over the LowWall** (−10, 86) and a crate (−45, 100), from standing and **straight out of low cover** (Space in CoverLow). Check: no Fall clip, no body lag at the start (Vaulting is now in FALLS/AIRBORNE), legs clear, landing.
- [ ] **Last Stand:** set the server attribute `Adrenaline = 5` on the character and the Gunman's `Hostile = true` (the TestArena loop polls it), stand in its sight. Lethal on the 6th hit (18 torso damage, every 0.8 s). Fire at it during the 4 s window to survive. Check: LastStandFall → LastStand → LastStandWakeup (bound to GettingUp, 3 s); root teleport down 2.2 then up; lying height; carried gun guard.
- [ ] Dives Back/Left/Right (V+S/A/D), DodgeGround spin, GettingUp.
- [ ] Reloads for every gun with marker effects; pickup (F), painkiller (H), drop (G).
- [ ] Low cover: slide along the wall (A/D) with the new gap; stop at the ends; low corner swings (crates); pop up (aim) and back (the root moves 1.1 closer while popped up? CoverAim speed is 0, so it shouldn't move; check).
- [ ] High cover: blind fire round the edge with right arm only; pop out with the AK carried.
- [ ] Bullet time on a vault and a crouch (time scales).
- [ ] **Two clients** (Studio Test > 2 players): root teleport on stance changes and the vault clip's speed chase replicating. Temporary animation ids don't replicate in Studio, so this mostly checks positions.
- [ ] Output log clean after a full run. The only warning seen was the speed check undoing my own test teleport.

</details>

### 3. Low cover pose (decision for the user)
The hunched R15 head reaches 2.2–2.8 studs ahead of the root (2.46 on the session 3 avatar), so it now sits that far from the wall (feet ~2.2 back), leaning in with the head touching the wall. Since session 3 the gap holds through popping up, sliding and corners, so the current pose has no known clipping or drift left. Options:
- **Keep** (current; no clipping, no drift).
- **Side-on crouch** (MP3-like, tried in Blender: `LOW_TURN` 70°, `LOW_BACK` 0.3 cuts head reach to 1.09). But the head then sits about 2 studs along the wall toward the edge, and the root stops 0.9 from an end, so the **head would stick out past wall ends**. That needs the body shifted back along the wall (~1.5) or a bigger low-cover `EDGE_MARGIN`. Reverted for now.

### 4. Remaining polish
- [x] Standing up from a crouch dips about 0.3 for ~0.1 s. Done in session 3 as a foot guard in AimLayer (the body lifts while a height change eases out; within 0.05 now). A full leg IK (each foot on its own floor, bending the knee) would still help slopes and stairs.
- [ ] Transitions: popping up from low cover and ducking back, the gun crosses the cover's top for 0.08 s (its box up to 0.82 in); stepping out of high cover, the right forearm sweeps through the wall's corner (box 0.78). The arms swing straight between the low hold and the aim; they'd need to lift first.
- [ ] Dive landing: the left forearm's box goes 0.30 under the floor for one frame at the impact (the root lands 0.2 low and springs back).
- [ ] Vault margin: the lowest leg point over the top is +0.06 at the front edge (seen in slow motion). Raising `VaultRules.LEG_CLEARANCE` from 0.2 to 0.3 would add margin at the cost of a slightly higher hop.
- [ ] `CarryTwoHandedLow` points the rifle out to the left (needed so it clears low walls). Forward-down might look more MP3 when crouching in the open (a separate crouch clip, low cover keeps the sideways one).
- [ ] Carried gun vs **walls** isn't guarded (only the floor), apart from the cover clip.
- [ ] Sniper and shotgun carries rely on the floor guard (too long for any fixed pose).
- [ ] Vault: take-off from very close (<1.3 studs) brushes the near edge for ~0.05 s. The left hand no longer touches the top at the higher arc. Vault from a run starts on a running stride (a standing vault could start from idle).
- [ ] Blind fire over low cover taller than about 3.7 can't reach the top (R15 arm length); maybe stand up partly for tall low cover.
- [ ] Wake-up: the carry clip overrides the left hand that the clip plants on the floor. Also seen in session 3: the right hand's pistol box touches the floor (0.2) while that hand pushes up, and a holstered gun grazes the floor (0.08) while kneeling.
- [ ] From the earlier list: the wake-up forearm box dips into the floor lying on the side; the gun-arm pump lags the opposite leg by ~0.1 cycle (fine).

### 5. Export and document
- [x] `mp_lib.export(fbx=True)` for FBX copies; `MaximumPain_Animations.blend` saved in `Assets/Blender/Animation` (session 3).
- [ ] **Publishing:** live servers need each KeyframeSequence published and its `rbxassetid://` in its `AnimationConfig` slot `Id` (93 clips). **The place's owner has to do it** (the account that owns "Untitled Experience"): an experience only plays animations owned by its own creator, so animations published from a collaborator's account won't load in live servers.
- [x] Removed the cover-to-cover wording ([[Changelog]], [[Cover System]]) and the out-of-date "no animations" and "no vaulting" lines.
- [x] Updated [[Architecture]], [[Animation Hooks]], [[Cover System]], [[Shoot-Dodge]], [[Last Stand and Bullet Time]], [[Movement State Machine]], [[Test Arena]].
- [x] New research notes: [[Euphoria-style Reactions and Ragdolls]] and [[Max Payne 3 Kill Cam]].

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
- **No weak-keyed tables keyed by instances** (`__mode = "k"`) for anything that must survive: entries vanish while the instance still exists. Keep the state on the instance (attributes) or in a plain table cleared when the instance leaves.

## Test log (session 3, 2026-11-02, Studio play mode)
| Test | Before → after the session 3 fixes |
|---|---|
| Vault from standing (LowWall, 2.46 back) | legs −0.19 → +0.23; Fall clip 0.16 → 0; camera step 1.17 → 0.60 |
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
