# Animation and MP3 Systems: Progress and To Do

Work log for the Max Payne 3-style animation and movement pass (bullet time, vaulting, hit reactions, ragdoll, kill cam, Blender animations). Picks up where the [[Changelog]] entry of 2026-11-01 leaves off. **Nothing is committed yet, and the Roblox place must be saved in Studio (File > Save) to keep the script changes.**

Related: [[Architecture]] · [[Animation Hooks]] · [[Movement State Machine]] · [[Cover System]] · [[Shoot-Dodge]] · [[Last Stand and Bullet Time]] · [[Test Arena]]

---

## Where things stand

### Done and tested in Studio
| Area | What exists | Tested |
|---|---|---|
| Bullet time | `BulletTimeRules`, `BulletTimeService` rewrite: 5 s meter, 3 levels, line-of-sight victims (frustum + raycasts through glass), aim penalty for lower levels, counter-activation, Last Stand needs ≥ level 1 | All 6 scenarios |
| Aim reporting | `CameraController` sends yaw/pitch on `AimUpdate` (≤15/s, resent every 1 s); `CharacterServer` validates (NaN, rate ≤30/s, pitch clamp) and sets the `Aim` attribute | Attribute replicates |
| Vaulting | `VaultRules`, `VaultController`, `Vaulting` stance, free aim and fire during the vault | Earlier session |
| Hit reactions | `HitReactions` (spring flinches per joint, purely visual, never touch movement); springs now run in the character's own time, so flinches slow down in bullet time | Earlier session |
| Ragdoll | `RagdollRules`, `RagdollService`, `RagdollController` | Dummy deaths |
| Kill cam | `KillCamController` (bullet ride, impact, comic panel; local only) | Visually |
| Procedural layer | `ProceduralLayer` (stacks bends after the animations each frame, on `PreSimulation`) | Yes |
| **Aim layer (new)** | `Controllers.AimLayer`: chest turns to the aim (rifle blade −30°, pistol −10°, half the pitch, upright bodies only), exact one-step barrel solve at the shoulder, head look, recoil springs (sized in peak degrees), momentum lean (~6° on starts/stops), run arm pump in step with the legs, left-hand IK onto every two-handed gun's `Support` attachment, and a height ease for stance changes | Barrel error ≤0.03° for pistol, rifle, dual wield and the gunman NPC, at every angle incl. steep near shots; support hand gap 0.000 studs |
| Animation controller | `AnimationController.state()` (aim, action, gait phase, moving), also for other players via their replicated tracks; cover holds while hidden; height-specific corner clips | Yes |
| Cover corners | `CoverController` eases the body's facing over the 0.35 s swing instead of snapping 90° | Round both pillar corners |
| **Clips** | 86 clips made in Blender and imported into `ReplicatedStorage.Assets.Animations`; every `AnimationConfig` slot has one, none unused | See below |

### Clips (Blender toolkit in `Assets/Blender/Animation`)
- `mp_lib.py` toolkit (rig, IK, keys, export). New: `lowest()`, `ground()` (rest a lying pose on the floor), `floor_guard()` (lift any hand or foot that dips through the floor), and an **IK fix**: R15's shoulder pivot sits at the upper arm's inner corner, so a straight arm reaches 1.66 studs, not 1.73; reaching further bent elbows backward by up to 33°. Now capped (also in the game's support-hand IK). No clip has a backward elbow.
- `mp_locomotion.py`: idle, run/jog/crouch-walk ×4, sprint, limps, hobble, jump, fall, land.
- `mp_arms.py`: holds and aims. Pistol, revolver, dual, SMG and sawn-off holds moved beside the thigh/hip (they crossed the belly); the carried rifle hangs from a nearly straight arm, 40° down so even the sniper clears the floor.
- `mp_stances.py` (new): DodgePrep/Air/Land ×4, DodgeGround, GettingUp, LastStandFall, LastStand, LastStandWakeup, Vault, CoverHigh/Low ×2, CoverHigh/LowMove ×2, CoverCornerHigh/Low ×2, CoverAim, LandRoll (rebuilt so it rolls along the floor; it used to sink 0.59).
- `mp_hands.py` (new): CoverHoldOne/Two/Dual, BlindFireLow/HighLeft/HighRight, DrawOneHanded/TwoHanded/Dual, Pickup, Painkiller, DropGun, ReloadPistol/Revolver/Rifle/Sniper/Pump/SawnOff/Dual (with MagOut/MagGrab/MagIn/BoltBack/BoltForward/ShellIn/Pump/CylinderOut/CylinderIn/BreakOpen/BreakClose markers).
- Pipeline: in Blender run the toolkit, `mp_lib.export()` writes `Exports/keyframes.json`; `mp_serve.start()` serves it; in Studio **Edit mode** run `require(game.ServerStorage.Tools.AnimationImporter:Clone())()`.

### Checked in play (2026-11-01)
- Low cover: head top 2.87 studs (under the 3.6 wall). Shuffle and aim-up over the wall look right.
- High cover: close to the wall, head turned along it, pistol held up by the chin. Shuffle at 9.6 studs/s plays at speed 1.0. Blind fire round the edge: gun level, muzzle 0.8 studs past the wall's end.
- Dive: flight, landing, lying with the root 1.0 above the floor. Exposed the restart bug below.

---

## To do (in order)

### 1. Fix the one-off clip restart bug (AnimationController) - important
When a non-looped track (landing, getting up, corner, reload, draw...) reaches its end while still fading out, `apply()` sees `not track.IsPlaying` and calls `Play()` again, so its **first frame flashes back**. Seen in the dive log: the landing clip restarted and put the body 2 studs into the floor for ~0.2 s.
- In `apply()`: for non-looped tracks, when `TimePosition >= Length - max(0.04, 2*dt*speed)`, `AdjustSpeed(0)` to hold the last frame while it fades; don't override that speed afterwards.
- `shoot()` already resets `TimePosition = 0` when re-shooting a playing track, which un-freezes it. Check a re-shot reload/draw still plays from the start.
- Re-test: dive landing (log the lowest body point: must never go below the floor), corner swing (the 20° chest jump at the end should become a smooth blend), a reload, a draw.

### 2. Low cover hold clips
`CoverHold*` were authored on an upright chest; the low-cover body leans ~78° forward, so the gun ends up pointing into the wall near the knees.
- In `mp_hands.py` add `CoverHoldLowOne/Two/Dual`, authored with `arms(..., body=S.cover_low("Right")(0))` with a side-neutral root yaw (as `blind_fire("Low")` does): gun up beside the face, muzzle up in the world. Rename the upright ones to `CoverHoldHighOne/Two/Dual`.
- `AnimationConfig`: slots `CoverHold{High,Low}{One,Two,Dual}` (Action, looped).
- `AnimationController.arms()`: `"CoverHold" .. (stance == "CoverLow" and "Low" or "High") .. hold`.

### 3. Blind fire fixes
- Key **only the right arm** (`joints=R`) in all three BlindFire clips: with both arms, the left hand lifted the carried AK onto the wall. Two-handed guns still get the left hand from the aim layer's support IK.
- `BlindFireLow` only reaches the wall's top edge from the hunched pose. Add a `Waist` key (straighten from −46° to about −28°) and aim the grip at about (0.3, 2.7, −1.7) in root space (0.5 above a 3.6 wall, 0.55 past its near face). Check reach with `L.solve`, then confirm in game from a camera above the wall.

### 4. Corner clip end pose
`cover_corner` ends at root yaw 0 but the cover idle is turned 34° (high) / 18° (low), which causes the blend jump at the end of a swing. Use `-s*(34 - 24*sin(pi*u))` (high) and `-s*(18 - 10*sin(pi*u))` (low).

### 5. Lying poses float 0.18 studs on this avatar
The default boxes are thicker than this avatar's parts. Lower `on_floor` / `LastStand` / landing impacts slightly (`ground(..., clearance=-0.06)`), then check in game that a default blocky avatar doesn't sink visibly.

### 6. Still to test in play
- **Vault** over the LowWall at (−10, 86): stand at (−6, 3.4, 80.5) facing +Z, hold W, press Space. Log root path and feet height; screenshot mid-vault (left hand on the top, legs swinging right) and landing.
- **Dives** Back/Left/Right (V + S/A/D) and the floor spin into `DodgeGround`; then **GettingUp** (any movement key).
- **Last Stand**: fall, lying, wakeup (3 s). Needs a lethal hit with a painkiller, loaded gun and ≥1 bullet-time level (gunman: press T near it, or a server-side damage call).
- **Reloads** for every gun (R), with marker effects (mag drops, slide, cylinder, pump, break-open); **draws** (1/2/3/4); **pickup** (F), **painkiller** (H), **drop** (G).
- **Crouch height ease**: press C and log the lowest foot each frame. The dive run-up showed the feet 0.16 below the floor on its first frame, so check the ease starts on the right frame (it needs the root to have moved; maybe use the HipHeight change itself for the first frame).
- **Two clients** (Studio Test > 2 players): remote aim, remote recoil, `AimUpdate` rate. Note: Studio's temporary animation ids don't replicate, so remote players only animate on live servers with published ids.
- Console clean after a full run.

### 7. Polish noticed but not done
- The carried rifle's muzzle pokes ~0.4 into the wall in high cover (it points 40° forward-down). Option: a more vertical carry while hidden.
- Low-cover knee box sits ~0.18 below the floor in the Blender box model (deep squat); looked fine in game, recheck with other avatars.
- Gun arm pump lags the opposite leg by ~0.1 cycle (reads as follow-through; fine).
- Wake-up: the lower forearm box dips 0.25 into the floor while lying on the side (box geometry).

### 8. Export, save, document
- `mp_lib.export(fbx=True)` for FBX copies; save the `.blend` into `Assets/Blender/Animation`.
- **Publishing:** live servers need each KeyframeSequence published (Animation Editor > Save to Roblox, or Open Cloud) and its `rbxassetid://` pasted into the slot's `Id` in `AnimationConfig`. About 86 clips. Studio plays them unpublished.
- Remove cover-to-cover wording from the docs but keep the cover system: [[Changelog]] ("cover-to-cover moves") and [[Cover System]] ("No cover-to-cover moves").
- Update [[Architecture]] (AimLayer, PostureLayer-in-AimLayer height ease, `AimUpdate`, `Aim`/`AimPenalty`/`BulletTimeLevel`/`BulletTimeEnds`/`LastShot`/`LastHit*`/`Ragdolled` attributes), [[Animation Hooks]] (slots, layers, markers, pipeline), [[Last Stand and Bullet Time]] (LoS rules, levels, penalty, counter-activation), [[Shoot-Dodge]], [[Cover System]], [[Movement State Machine]], [[Test Arena]], and add notes for Euphoria-style reactions + ragdoll research and the MP3 kill cam research.
- Commit and push only when asked (repo is public; link screenshots, don't commit them).

### Testing tricks (Studio)
- `execute_luau` runs in a separate VM: never `require` game modules with side effects there; use attributes.
- Point the camera: `player:SetAttribute("DebugLook", Vector2.new(yaw, pitch))`.
- A render-only debug camera (BindToRenderStep at Camera+50, restore the gameplay CFrame on `PreAnimation`) lets screenshots be taken from outside without changing what the aim layer aims at. `_G.debugCamEye/_G.debugCamAt` in root space; `_G.debugCamWorld = true` for world axes.
- Teleport with `HumanoidRootPart.CFrame = ...` (`PivotTo` did not stick while leaving cover).
- Luau gotcha that cost an hour: `local a, b, c = if x then f() else nil, y, z` keeps only `f()`'s first value.
