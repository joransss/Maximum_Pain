# Changelog

Every change to the game, newest first. Each entry says what changed, the decisions behind it, what was tested, and what was left out.
System details: [[Architecture]] · [[Movement State Machine]] · [[Loadout and Dual Wielding]] · [[Cover System]] · [[Shoot-Dodge]] · [[Last Stand and Bullet Time]] · [[Animation Hooks]] · [[Test Arena]] · [[Weapons and Recoil]] · [[Limb Health]] · [[HUD Layout]]

## 2026-11-08: Popping up and ducking back in low cover turn the body round
Session 5 ran on this PC (Studio signed in as 83tg), 2026-11-08, with Claude Code driving Blender headless and Studio. It did to-do 4.14, ran 4.19's first test, and found two new faults on the way (the cover slide's feet, fixed, and 4.20).
- Side-on, the low cover idle faces out from the wall and the aim faces over it. Popping up and ducking back used to turn the body about 166° in the body layer's 0.2 s blend, and the feet swept through the wall's base.
- Four new clips take the turn (98 clips now). Three scripts changed in the Team Create place.
- Details and numbers: [[Animation and MP3 Systems - Progress and To Do]] (session 5).

**Added: the turn clips** (`mp_stances.cover_turn`)
- `CoverPopUpLeft/Right` (0.25 s, as long as `CoverPeek`) and `CoverDuckLeft/Right` (0.3 s). Sampled at 60 per second, not 30: they turn the body half round in a quarter second.
- **The turn:** toward the edge being worked, so the head that was looking along the wall leads it. Working right the body goes from facing out (-180°) through facing the edge (-90°) to the aim (14°), working left through 90°.
- **Popping up:** the body rises, leaves the wall and only then turns (turning in place, the side-on torso went 0.47 into the wall). The hips sway 0.6 out from the wall halfway round. The foot on the outside of the turn steps first.
- **Ducking back:** the body turns and folds over first, and goes down once the feet are round. Left to `AimLayer`'s height ease, the hips dropped halfway in 0.06 s with the feet still stepping: the knees folded forward over them and the shins went 0.3 into the floor.
- **The game's height ease is built in:** the game changes the hip height at once, and `AimLayer` holds the body where it was and eases it to the new height (10 per second). The clips plant the feet where that hold leaves the floor, so they stay on it.
- **Knees:** they turn with the feet, from the way they bend in the pose the clip starts on to the way they bend in the one it ends on, so each clip starts and ends on its neighbours' legs. Where a knee, or a gun holstered on the left thigh, would reach past the wall's face, the knee turns out from the wall, no further than it needs.
- **`CoverAim`:** the back heel is up (22°). Flatter, the shin leant over the foot and its box went 0.12 into the floor.

**Changed: the game** (Team Create place)
- `AnimationController`:
  - Low cover to `CoverPeek` plays `CoverPopUp<side>`, bound to the stance. `CoverPeek` or `CoverAim` back to low cover plays `CoverDuck<side>`. They play in real time, as the height ease does (bullet time doesn't slow them), and take the body over at 25 per second (`TURN_FADE`).
  - For the first 0.15 s of a pop-up (`POP_AIM`) the gun stays in the low cover hold. Raised at once it went through the wall's top; at 0.1 s it still went 0.5 into the wall's face working left, where the turn takes the gun shoulder past the wall.
  - Other players' characters use the right-hand clips, as their cover idles already do.
- `AnimationConfig`: the four slots (105 slots now).
- `AimLayer`: the foot guard (the body lifts so no foot is under the floor) now runs in every cover stance, not only while a height change eases. Sliding along low cover, the idle blends into the run a quarter turn round, and the feet went 0.36 under the floor.

**Tested** (Studio play mode, 83tg's avatar, the LowWall)
| Test | Result |
|---|---|
| Pop up and duck back, working right and left | the clips play on the stance changes. A shin 0.08 under the floor for one frame at most (0.22 with the clips' first version); feet 0.05; no leg in the wall |
| The gun coming up while popping up | working left, the gun 0.05 in the wall's face for a few frames (0.59 with `POP_AIM` at 0.1); aiming over the top, the forearm rests on it (0.05), as before |
| Sliding along low cover, start and stop | feet 0.05 under the floor (0.36 before the guard ran in cover); shins, thighs and holstered gun still go 0.33 under (4.20) |
| Blind fire while sliding along low cover (4.19, first test) | nothing in the wall, but on the run the gun is 2.7 out from the wall pointing back along it |
| Camera | largest step 0.08 |
| Output log | clean (client and server) |

**Not fixed**
- **New, 4.20:** the crouch walk and the low cover run fold the trailing leg so low that the knee is 0.19 above the floor: the shin's box goes 0.44 to 0.47 under it, the thigh's 0.26, a holstered gun's 0.34 (default R15; 0.33 in game). Tried in Blender: the push-off heel, the knees turned out, shorter strides, the feet further forward: no better than 0.35. Hips 0.2 to 0.3 higher with short strides: 0.16 to 0.3, the head 0.2 to 0.33 higher.
- At the start of ducking back working right, the holstered gun is 0.14 in the wall for 2 frames while the clip blends in over the aim. The right upper arm rests on the wall's top edge (0.08) as the aim lowers.
- **4.19, tested:** blind firing while sliding along low cover turns the chest the wrong way (the clip twists the waist for the idle's hips, which face out; the run's face along the wall). Needs a call: stop the slide while blind firing, or blind fire clips made on the run.

## 2026-11-07: Side-on cover, as Max Payne 3 does it
Session 4 ran on this PC (Studio signed in as 83tg), 2026-11-07 from 19:26 (UK time), with Claude Code driving Blender headless and Studio. Studio had updated itself at 19:18 and dropped Claude Code's Studio connection, so the session drove Studio's own `StudioMCP.exe` directly (see "How to resume" in [[Animation and MP3 Systems - Progress and To Do]]).
- The three open decisions in the to-do were made: the game's code stays out of git, the test harness goes into the repo, and cover goes side-on, high and low, like Max Payne 3.
- 24 cover clips were remade in Blender and one added (94 clips now). Five scripts changed in the Team Create place, two of them only in comments.
- Everything was measured in Studio play mode, frame by frame, on 83tg's avatar (a slim R15: torso 1.4 studs wide where the default is 1.94, root 3.13 above the floor).
- Details, numbers and what's left: [[Animation and MP3 Systems - Progress and To Do]] (session 4).

**What Max Payne 3 does** (frames from the Steam trailers, studied at 2 to 4 fps; nothing stored in the repo)
- *Design and Tech Video 2*, 2:53–2:54: Max runs to a tall cabinet and puts his **back flat against it**, facing out, SMG low in the right hand, the left hand up by his face, head turned toward the edge.
- Same video, 2:56–2:57: behind a low counter he **crouches with his back against it**, knees up, gun up by his shoulder, head turned to the edge. Popping up, he turns round to face over it.
- *Multiplayer* trailer, 1:35–1:36: players stand with their **back to a wall at its edge**, pistol low, head turned along the wall. 1:43: a rifle held **upright beside the face**.
- The official screenshot `ss_4ae054ce…` (see [[Reference Images]]): back to the wall beside a window, the pistol low in both hands, head turned to the window.
- So "side-on" here is Max's version: back and inner shoulder on the wall, the body turned toward the edge being worked, the head looking along the wall to it. Moving along the wall, the body runs side-on, facing the way it goes.

**Changed: the cover clips** (`mp_stances.py`, `mp_hands.py`, `mp_arms.py`)
- **How they fit the game:** the game keeps the root part facing the wall, and keeps the gap the body's reach toward the wall needs (`CoverController.bodyReach`). So the clips turn the body round inside the root part and lean it back until the head, torso and upper arms reach 1.1 toward the wall: the gap comes out at 1.15 and the back rests on the wall. No gameplay code depends on which way the body faces.
- **High cover idle** (`CoverHighLeft/Right`): turned 150° from facing the wall, so the back and inner shoulder are on it, knees soft, feet out from the wall, the head turned along the wall to the edge.
- **Low cover idle** (`CoverLowLeft/Right`): a deep squat on the balls of the feet, back against the wall, folded over the knees. The head is aimed along the wall to the edge with a look-at, since a neck turn on a folded body rolls the head instead. Head top 2.80 above the floor on the default R15, so it's under even the lowest (3-stud) cover. The old pose's was 3.22, and 3.49 in game.
- **Moving along cover** (`Cover…Move…`): side-on, facing the way it goes. High is a hunched jog at 9.6 studs/s; low is a crouched run at 8 studs/s, folded at the waist to keep the head under 3 studs. Folding at the hips put the trailing shin through the floor.
- **Corners** (`CoverCorner…`): from the idle, a side-on stride round the corner, and back to the idle.
- **Wall ends:** the root stops 0.9 short of an end (`EDGE_MARGIN`), and an R15's shoulders reach further than that along the wall. So the idles sit back along the wall, away from the edge: 0.35 (high) and 0.75 (low). The runs sit back so the head leads the root by no more than 0.8 (high) and 1 (low).
- **Holds while hidden:**
  - High: `CoverHoldHighOne` (the pistol low in front of the belly, muzzle down, as in the screenshot), `CoverHoldHighTwo` (the rifle upright across the chest, muzzle up and to the left, its top 4.5 above the floor, under the 5.2 wall) and `CoverHoldHighDual` (both pistols up in front of the chest).
  - Low: `CoverHoldLowOne` and `CoverHoldLowDual` (the gun up beside the face), and `CoverHoldLowTwoLeft/Right` (the rifle upright past the face, leaning away from the edge the head looks to).
  - The guns are placed in a body part's frame and aimed in the body's facing frame, so one clip fits both sides.
- **Blind fire:**
  - **Low** (`BlindFireLowLeft/Right`, now keys the waist and neck): the hips stay against the wall and the chest twists 105° to put the gun shoulder to it. The arm goes straight up, and the gun goes over the top, the head ducked and facing away.
    - With the back to the wall the arm can't reach over: folded to keep the head down, the shoulders are 2 studs out from the wall, and upright the head is above it.
    - The hand stays in front of the wall's face. With the hand over the wall, the forearm cut 1.2 into the top edge of the 2-stud-thick LowWall.
  - **High** (`BlindFireHigh…`, now keys the waist and neck): the gun arm out along the wall and the gun turned round the edge, the head looking along the wall, not round it.
    - Working right, the gun arm is on the side away from the edge (back to the wall), so the chest leans out and toward the edge and the arm reaches across.
- **Carried rifle:** `CarryTwoHandedCover` now hangs the rifle muzzle down in front of the left thigh, off the wall on either side. The new `CarryTwoHandedCoverLow` holds it by the knee, muzzle forward and down, away from the wall. `CarryTwoHandedLow` is now only for crouching and getting up.

**Changed: the game** (Team Create place)
- `AimLayer`:
  - The head no longer looks at the aim while hidden in cover. The aim is past the wall, behind the turned head, and would wring the neck round. It eases on and off at 8 per second (`gaze`).
  - The momentum lean is worked out in the hips' frame. In the root part's frame it went the wrong way once the body turned round, and it was 45 to 50° off on strafes too.
- `AnimationController.carryFor`: low cover uses `CarryTwoHandedCoverLow`.
- `AnimationConfig`: the new slot, and the cover comments.
- `CoverController`, `CoverRules`: comments only (no more "hunched").

**Found in the place** (done after the 2026-11-03 notes, without notes or commits; found reading the code)
- `AimLayer.guardArm` keeps each arm, its gun and the carried gun out of walls (to-do 4.2 and 4.7).
- The dive landing is held and eased like a crouch, so the root no longer falls 2.4 and bounces (`DodgeGround` left `FALLS`; 4.3). The foot guard now lifts up to 1.2.
- `VaultRules.LEG_CLEARANCE` is 0.3 (4.4).
- `AnimationController.watchReloads` runs the reload markers on other players' guns (4.13). A reload cut short puts the gun back to rest, and every clip is loaded at spawn so the first vault isn't unstretched.
- `CoverController.bodyReach` counts the upper arms below the cover's top. The high-cover step out is capped at what lands on the spot by the next frame.
- `ServerStorage.Tools.TestHarness`: a 733-line play-test harness. `ServerStorage.Tools.AnimationImporter` was rewritten as a module.
- A large block, `Workspace.Part` (4 × 18 × 18 at x 32, z 47), stands between the spawn and the arena.

**Added: repo**
- `Tools/TestHarness.luau`: the place's harness (to-do decision 2). How to install and use it is in the file's header and in [[Test Arena]].
- `Assets/Blender/Animation/studio_import.luau` now matches the place's `AnimationImporter`.
- 94 clips in `Exports/keyframes.json` and in `MaximumPain_Animations.blend`. Only the 24 cover clips changed, plus the new one; the other 69 are byte-identical.

**Decisions**
- The game's code stays out of git: the repo is public (JordanSaa's call, to-do 1).
- Cover is side-on as Max Payne 3 has it: back and inner shoulder to the wall, turned to the edge (to-do 3). Moving is side-on, facing the way it goes.
- The body is turned inside the root part, not the root part itself, so cover detection, the gap, edges, peeking, the server's checks and the virtual muzzle all stay as they were.
- The wall ends are handled in the clips (sitting back from the edge), not by widening `EDGE_MARGIN`. A wider margin would change where peeking and blind fire work.

**Tested** (Studio play mode, 83tg's avatar)
| Test | Result |
|---|---|
| Low cover, settled | head top 2.77, 0.83 under the 3.6 wall (3.49 before); root 1.21 off the wall; nothing in the wall or the floor |
| Low cover at the wall's ends | head 0.47 inside the end; the edge-side upper arm 0.33 past it (0.73 before the idle sat back) |
| Low cover, the run stopping at an end | head 0.21 past the end while the run blends out (0.64 before) |
| High cover at the wall's ends | head 0.39 inside; arm 0.29, legs 0.15, holstered Uzi 0.47 past (head 0.84 and arm 0.96 past before the idle sat back) |
| Blind fire over the LowWall | head 0.34 under the top, gun 0.11 over it (0.39 on the default R15); nothing in the wall; gap held at 1.21 |
| Blind fire round the HighWall's ends | working left: gun 1.07 past the end, round the corner; working right: just past the corner, the body leaning out |
| Popping up and out, ducking back | right clips; aiming over the wall the forearm only rests on the top (0.05); ducking back into high cover the gun is 0.22 in the wall for 3 frames |
| Corner swings round CrateA | nothing in the crate |
| Vault out of low cover | flies clear; see Not fixed |
| Camera | largest step 0.08 |
| Output log | clean |

**Not fixed** (in the to-do as 4.14 to 4.19)
- Popping up and ducking back in low cover turn the body round in a 0.2 s blend. A foot goes up to 0.43 into the wall's base, and the gun arm 1.2 into the top for the first frame. A turn clip for each would fix it.
- Vaulting out of low cover: for one frame a foot is 0.74 inside the wall as the body turns.
- At an inside corner the root turns 90° in one frame, and the run's body (up to 1.8 off the root) swings with it. Sliding round CrateA into the next crate, it went 1.1 into CrateA for about 3 frames.
- Blind fire working right reaches only just past the corner.
- Not tested: two players, other avatars in game, firing while sliding along low cover.

## 2026-11-02: Play tests, the fixes they needed, and the Blender export
Session 3 ran on JackT6785's PC, with Claude Code driving Studio: 2026-11-02 20:58 to 22:20, then 2026-11-03 01:51 to 02:00 (UK time).
- Every play test left on the to-do list was run in Studio play mode on JackT6785's R15 avatar, and measured frame by frame: each body part's box, the root, the camera and each clip's weight.
- Every fault found was fixed and measured again.
- 13 scripts changed, all in the Team Create place. The Blender export and the notes changed in the repo.
- The per-gun reload table, every measurement and the code details are in [[Animation and MP3 Systems - Progress and To Do]] (session 3).

**Fixed: vaults** (`AnimationController`, `VaultRules`, `VaultController`, `CameraController`)
- **The legs went into the top of the obstacle:** 0.19 into the LowWall, 0.31 into a crate.
  - Cause: when the leading foot reached the near face, the Vault clip had only blended in to 0.78. The standing clips' straight legs still pulled the feet down.
  - Fix: the Vault clip blends in at 30 per second (`VAULT_FADE`) instead of the body layer's 10, so it is at 0.99 by the near face. The arc also rises with the avatar's legs (see Changed).
  - Result:
    - The lowest point over the top is +0.23 over the LowWall and +0.16 over a crate.
    - Out of low cover the left hand rests on the top (0.00).
    - In slow motion the tightest point is +0.06, at the front edge.
- **Every landing played the Fall clip** for about 0.2 s (weight 0.16).
  - Cause: a finished vault handed the humanoid back in Freefall, which plays Fall until it finds the floor.
  - Fix: `VaultController.release(landed)` puts it straight into Running. Only a vault cut short falls.
- **Landings bounced 0.2** once the arc was higher.
  - Cause: the speed handed to physics in the last frames carried the root below the landing, so the feet hit the floor and the body sprang up.
  - Fix: on the way down the vault caps that speed, so one physics step ends at the landing height.
- **The camera jumped 2 to 4 studs in a tenth of a second:** 1.17 in one frame at take-off, and −1.35 then +2.15 out of low cover.
  - Cause: the view followed the hop rigidly.
  - Fix: new `CameraController.setVerticalLag(share)`. While vaulting (`CAMERA_LAG` 0.5), the view takes half of each rise and fall at once and eases into the rest. An earlier try fed each step of the path to the camera; landings juddered, so it was dropped.
  - Result: largest step 0.6 to 0.8 (0.22 in bullet time).

**Fixed: height changes** (`CameraController`, `CharacterController`, `AimLayer`)
- **The camera popped when the hips moved without the root jumping:** out of low cover into a vault (above), and +1.68 on a dive's landing.
  - Cause: the camera only held its height back when `CharacterController` reported moving the root.
  - Fix: the camera watches the hip height itself every frame, whoever changed it. It holds 75% of each change (`CROUCH_CAMERA_KEEP`) and eases it out at 10 per second. `absorbRise` now only reports the root jumping.
- **Stances the server forces moved the body by physics.** Dropping into a Last Stand was a 2.2-stud free fall, with the feet 0.74 under the floor and a 1.77 camera pop. A timed get-up rose over 8 frames.
  - Cause: for a Last Stand, a wakeup and a timed get-up, the server's HipHeight reaches the client before the stance does. The client saw no change and never moved the root.
  - Fix: `CharacterController` compares with the hip height it last put the root at (`appliedHip`). It moves the root to the new height over the floor in the same frame, or only the rest of the way if physics already moved it.
  - Result: the drop is instant, the feet are at −0.05 and the largest camera step is 0.20.
- **A dive's launch pushed the feet 0.39 into the floor** for four frames.
  - Cause: the aim layer held the body at the run-up's lower height while the launch carried the root up.
  - Fix: `DodgeAir` and `Dead` count as real moves of the root in `AimLayer`; its `FALLS` now matches `CharacterController`'s `AIRBORNE`.
  - Result: +0.21.
- **The feet dipped into the floor while a height change eased out:** 0.11 crouching, 0.14 to 0.30 standing up, 0.33 into a Last Stand (to-do 4.1).
  - Cause: the clips bend and straighten the legs at their own pace, not the body's.
  - Fix: a foot guard in `AimLayer`. For 1 s after a height change, the body is lifted just enough that neither foot's box is more than 0.05 under the floor beneath it (one ray per foot, at most 0.6).
  - Result: within 0.05 in every case.

**Fixed: guns** (`WeaponEffects`, `AnimationController`, `WeaponController`, `AimLayer`, `ProceduralLayer`, `HitReactions`)
- **Slides and bolts stayed racked back after reloads** (FAL, M4, Desert Eagle).
  - Cause: the marker that sends them home fired on time, but the part's resting pose had been lost.
    - Resting poses were kept in a weak-keyed table (`__mode = "k"`) keyed by the guns' Motor6Ds.
    - The engine can drop an instance's Lua handle while the instance still exists, so entries vanish at random. This was reproduced: a key vanished after one garbage collection while the motor was still in the gun.
  - Fix: the resting pose is stored on the motor (`RestC0` attribute) and read through `WeaponEffects.restPose`, shared by the reload markers and the firing kick.
- **The same pattern was removed everywhere:** 10 tables in six controllers. Each is now a plain table, emptied when its instance leaves the game:
  - `WeaponEffects`: the kick's resting poses. If an entry was lost while a part was kicked back, the next shot took the kicked pose as the rest.
  - `WeaponEffects`: the muzzle effects. Each lost entry added another shadow-casting light and three particle emitters to the muzzle. They're now found by name, and the flash counter is the muzzle's `Flashes` attribute.
  - `WeaponController`: each gun's spray, bloom and predicted ammo, which restarted when lost.
  - `AimLayer`: each body's state. A lost entry reset a height change mid-move.
  - `ProceduralLayer`: the joints' base poses.
  - `HitReactions`: the flinch springs, the joint cache, and the hit log that the death push and the kill cam read.
  - Kept on purpose: `AimLayer`'s gun-box cache, where a lost entry only costs a rebuild.
- **A pistol reload moved the carried rifle's parts too.** A Desert Eagle reload dropped a spent magazine from the M4 in the left hand and moved its bolt.
  - Fix: reload markers move only the gun in the right hand, or both pistols for `ReloadDual`.
- **Result:**
  - All 13 guns and the dual reload play their clip once at full weight, with no restart.
  - Each clip is stretched to its gun's reload time, from 0.81× speed (Desert Eagle, Uzi, dual) to 1.15× (MP5).
  - Every part comes back to rest, and the ammo is right after each reload.

**Fixed: dropped guns** (`LoadoutService`)
- **For the player who dropped it, the gun hung in the air** where it left the hand.
  - Cause: the gun was still part of that player's physics (their client owns it). The server moved it in the same frame as it released it, and that move never reached them.
  - Fix: the gun is anchored and released at once, then laid down 0.1 s later (`SETTLE_DELAY`). Its `DroppedAt` time doubles as a token, so a late lay-down can't move a gun that was picked up or dropped again.
- **For everyone else, guns floated about 0.45 above the floor.**
  - Cause: `GetBoundingBox` turns with the gun, so for a gun on its side the box's "height" was a width.
  - Fix: `bottomOf` measures the real lowest point. `layDown` rolls the gun onto its side and rests it 0.03 above the highest floor under its middle and both ends.
- **Result** (server and client agree):
  - Open floor: 0.03 above the floor.
  - Against the gun table: on the floor, 0.21 short of it.
  - A swap at the rack: on the table top.

**Fixed: cover** (`CoverRules`, `CoverController`)
- **Corner swings behind low cover had stopped working** (tested on CrateA).
  - Cause: `CoverRules.outerCorner` looked for the wall's end face from the high-cover distance (1.15). Low cover keeps 2.2 to 2.8 since session 2, so its probes started in front of the wall and found nothing.
  - Fix: it now takes the character's real distance from the wall, and returns the swing's middle point as well as its target.
  - Result: holding D went round two corners of the crate in a row, with nothing inside it.
- **Ducking back from aiming over low cover lunged at the wall:** the root moved 0.57 toward it and the forearm went 0.83 into it.
  - Cause: the distance from the wall was re-measured on the upright aiming pose while it blended out.
  - Fix: `CoverController` remembers the body's deepest reach for each cover stance while in cover. It eases that back (0.5 studs/s) only when settled (0.4 s after a stance change), still, and not firing (1.5 s after a shot).
  - Result: the gap held at 2.54 through popping up and back. After a slide the body eases back to the wall (head 0.07 to 0.13 off it; it stayed 0.2 out before).

**Fixed: the Blender export** (`mp_lib.py`)
- **It crashed on Blender 5.** `mp_lib.bake` used `action.fcurves`, which Blender 5.0 removed; F-curves now sit in the action's layers, strips and channel bags. The new `_fcurves(action)` reads either layout, so older Blender versions still work.
- **Every export rewrote `keyframes.json`.** `clip_data` walked a Python set, whose order changes every run; the tracks are now sorted. Two exports are byte-identical, and the regenerated clips equal the committed ones, so Studio didn't need a re-import.

**Changed**
- **The vault's arc depends on the avatar:** `VaultRules.apexAbove(rootHeight)` = max(2.1, 0.6 × the root's standing height + 0.2). A standard avatar still flies 2.1 above the top, JackT6785's 2.23 and a tall Rthro 2.54.
- **Vault landing:** a finished vault lands straight into running, and the camera eases over the hop.
- **Reload markers** move only the gun being reloaded.
- **Dropped guns** lie on their side on the highest floor under them, about 2 studs ahead of the feet. `dropFront` checks for the gun's length ahead at shin height: the gun stops short of anything in the way, or lies across the feet when there's less than 0.6 of room.
- **Low cover:** the distance from the wall is the deepest reach of the stance since taking cover. It relaxes only when the character is settled, still and not firing.

**Added**
- **Code:**
  - `CameraController.setVerticalLag`.
  - `WeaponEffects.restPose`.
  - `VaultRules.apexAbove`, `LEG_TUCK` 0.6 and `LEG_CLEARANCE` 0.2, with self-checks.
  - A `gap` argument for `CoverRules.outerCorner`, and its returned `apex`.
  - `AimLayer`'s foot guard (`footDip`, `FOOT_SLACK` 0.05, `MAX_FOOT_LIFT` 0.6).
  - `LoadoutService.bottomOf`, `layDown` and `dropFront`.
  - `CharacterController`'s `appliedHip`.
  - `CoverController`'s `REACH_SETTLE` 0.4, `REACH_RELAX` 0.5 and `FIRED_HOLD` 1.5.
- **Attributes,** set by each client on its own copy:
  - `RestC0` on gun motors (the part's resting pose).
  - `Flashes` on muzzles (the flash counter).
- **Repo:**
  - `MaximumPain_Animations.blend`: the rig and all 93 clips as actions (1.95 MB).
  - FBX copies of every clip in `Exports/FBX` (93 files, 14.6 MB). They're kept out of git: `L.export(fbx=True)` rebuilds them in about 12 s.
- **Notes:** [[Euphoria-style Reactions and Ragdolls]], [[Max Payne 3 Kill Cam]].

**Removed**
- Ten weak-keyed tables (above).
- The "cover-to-cover moves" lines from this changelog's 2026-10-31 entry and from [[Cover System]], as the to-do asked.
- Python bytecode from git (`__pycache__/` is now ignored).

**Decisions**
- State that must survive is kept on the instance (as attributes) or in plain tables emptied when the instance leaves. It never goes in weak-keyed tables keyed by instances; only caches may stay weak.
- The camera handles every hip height change itself, instead of relying on each script that changes it.
- The server lays a dropped gun down 0.1 s after the drop, not in the drop frame.
- The FBX copies aren't committed, since they're rebuilt in seconds; the `.blend` is.
- The low-cover pose stays hunched until JackT6785 and JordanSaa decide (to-do 3).
- The commits stay local until JackT6785 pushes them, as it's JordanSaa's public repo.
- Publishing the animations is left to JordanSaa, because an experience only plays animations its owner owns.

**Tested** (Studio play mode, JackT6785's avatar; before → after)
| Test | Result |
|---|---|
| Vault over the LowWall from standing | lowest point −0.19 → +0.23; Fall clip 0.16 → 0; camera step 1.17 → 0.62 |
| Vault over a crate | −0.31 → +0.16 |
| Vault out of low cover | camera −1.35/+2.15 → 0.83; the hand rests on the top (0.00) |
| Vault landing | bounce 0.20 → 0 |
| Vault in bullet time (0.3) | 1.40 s in the air; +0.06 at the front edge; camera 0.22 |
| Dive launch / landing | feet −0.39 → +0.21 / camera +1.68 → 0.56 |
| Last Stand drop and wakeup | free fall, feet −0.74, camera +1.77 → instant, feet −0.05, camera 0.20 |
| Crouch and stand | feet −0.11 / −0.14 to −0.30 → −0.05 |
| Get-up forced after 8 s | rose by physics over 8 frames → at once |
| Turning while lying (8 angles) | lowest point +0.04 to +0.06; guns +0.38 |
| Reloads: 13 guns and dual | 3 guns left racked, and the carried rifle dropped a magazine too → all correct |
| Pickup (F) ×14, painkiller (H) | worked: torso 82 → 100, painkillers 3 → 2 |
| Drop (G) | hung (the dropper) / floated 0.45 (everyone else) → 0.03 above the floor |
| Low cover: slide and ends | 8 studs/s; stops 0.74 to 0.85 from the ends |
| Low cover: corner swings | never swung → two corners in a row |
| Low cover: pop up and back | lunge 0.57 → gap steady at 2.54 |
| High cover: blind fire and pop out | right arm only; shots round the corner; the carried AK ≥ 1.29 off the wall |
| Network (the server's view) | stance, hip height, the root's drop and the Vault clip's pacing replicate |
| Output log | clean |

**Scripts changed** (in the Team Create place; not in git)
| Script | Change |
|---|---|
| `CameraController` | follows every hip height change; `setVerticalLag` |
| `CharacterController` | `appliedHip`; moves the root over the floor, including for forced stances |
| `AimLayer` | DodgeAir and Dead in `FALLS`; foot guard; plain `bodies` table |
| `AnimationController` | `VAULT_FADE`; resting poses from `WeaponEffects`; markers on the reloaded gun only |
| `VaultController` | lands in Running; caps the landing speed; turns the camera lag on and off |
| `VaultRules` | `apexAbove`, `LEG_TUCK`, `LEG_CLEARANCE`, self-checks |
| `WeaponEffects` | `restPose`; muzzle effects found by name; `Flashes` |
| `WeaponController` | plain `gunStates` table |
| `ProceduralLayer` | plain `bases` and `applied` tables |
| `HitReactions` | plain `springs`, `hits` and `joints` tables |
| `LoadoutService` | `bottomOf`, `layDown`, the delayed lay-down, `dropFront` |
| `CoverRules` | `outerCorner` takes the gap and returns the apex |
| `CoverController` | reach remembered per cover stance; corner swing from the real gap |

**Repo:** committed on JackT6785's PC on 2026-11-02 and 03: `3634cce` (stop tracking bytecode), `7f86ec1` (the Blender export on Blender 5, deterministic, and the `.blend`), `a608dc7` (notes).

**Not done**
- Saving the place in Studio after these changes (File > Save to Roblox).
- A two-player test (Studio's Clients and Servers). Only the server's view was checked.
- Publishing the 93 animations: JordanSaa has to do it, as the place's owner.
- The low-cover pose decision.
- 12 polish items, listed in the to-do with ideas for each.

## 2026-11-01 (later): Animation fixes, carried guns, low cover and the vault (in progress)
Full detail, measurements and next steps: [[Animation and MP3 Systems - Progress and To Do]].

**Changed**
- **One-off clips** (landings, getting up, corners, reloads, draws) hold their last frame while fading instead of flashing their first frame.
- **Stance height changes** (crouch, low cover, getting up, Last Stand) move the root at once; the body and camera ease over. The body no longer sinks up to a stud into the floor, and crouching no longer plays the fall clip.
- **Carried two-handed gun:** new crouched and high-cover carries, plus a floor guard. It no longer goes through the floor when crouching, in cover, diving or lying.
- **Low cover:** guns held low (pistol, dual, rifle per side); blind fire per side over the top; the character keeps the distance its hunched body needs, which stops it sliding along the wall.
- **Corner swings** start and end on the cover idle. **Lying poses** float 0.10 instead of 0.18.
- **Vault:** a higher, level arc over the obstacle and a speed-vault clip paced by the way over, so the legs clear the top.

**Not finished:** the to-do lists the remaining play tests (Last Stand, vault from low cover, two clients), a low-cover pose decision, and publishing. The place must be saved in Studio; nothing is committed.

## 2026-11-01: Bullet time levels, vaulting, hit reactions, ragdoll, kill cam, aim layer and 86 animations (in progress)
Full detail and the next steps: [[Animation and MP3 Systems - Progress and To Do]].

**Changed**
- **Bullet time** rebuilt: 5 s meter in 3 levels; slows players in the activator's direct line of sight; lower-level victims get a mouse-sensitivity penalty; counter-activation at an equal or higher level clears it; Last Stand needs at least one level.
- **Vaulting** over low obstacles (Space), with free aim and firing throughout.
- **Euphoria-style hit flinches** (visual only, movement untouched), **physics ragdoll** on death, and a local **multi-shot kill cam**.
- **Aim layer**: guns point exactly where each player aims from any pose (≤0.03° barrel error), with chest blading, head look, recoil kicks, momentum lean, a run arm pump, the left hand kept on every rifle's handguard, and smooth height changes between stances. Players report their aim to the server (`AimUpdate`), so everyone sees it.
- **86 animations** made in Blender and imported: locomotion, holds, aims, cover (idle, shuffle, corners, holds, blind fire, aiming out), shoot-dodge (run-up, flight, landing, floor), getting up, Last Stand (fall, stand, wakeup), vault, landing roll, draws, pickup, painkiller, drop, and seven reloads with markers.
- **Fixes:** R15 arm IK no longer bends elbows backward; the low-ready holds no longer cross the belly; corner swings turn the body smoothly instead of snapping 90°; flinches slow down in bullet time.

**Not finished:** one-off clips flash their first frame when they end (fix planned first), low-cover hold clips, blind fire over low cover, and several mechanics still to test in play. See the to-do list.

## 2026-10-31: Loadouts, stances, cover, shoot-dodge and Last Stand
**Changed**
- **Loadouts:** two one-handed guns (keys 1, 2) and one two-handed gun (3). **Dual wielding** on 4; drawing both one-handed guns **drops the two-handed gun** on the floor. The two-handed gun is never holstered: it rides in the left hand while a one-handed gun is out, as in Max Payne 3. See [[Loadout and Dual Wielding]].
- **Guns are now Models, not Tools** (a character can only hold one Tool). They hang from Motor6Ds (`RightGrip`, `LeftGrip`, `Holster`) that animations can move.
- **Dropping and picking up:** G drops, F picks up or swaps; guns keep their ammo. Death drops what was in the hands. The Uzi is now one-handed.
- **Reloads** move ammo only when the server's timer finishes, so interruptions lose and duplicate nothing. Dual reloads take the longer time ×1.5. Switching guns takes a short draw time.
- **Movement state machine** (`StanceRules`): one stance at a time (standing, sprinting, crouching, four cover stances, three dive stances, getting up, Last Stand, dead), with what each allows and which stances follow. The client predicts and the server confirms, rejects or forces. See [[Movement State Machine]].
- **Sprint** is now a stance: firing ends it (0.2 s before the gun can fire), it can't start in cover, and reloads carry on.
- **Free crouch** on C, with a headroom check under low ceilings.
- **Cover** on E: high and low cover, sliding along walls, stopping at ends, inside corners, swinging round outside corners, popping out to aim, blind fire, and the shoulder camera following the side. See [[Cover System]].
- **Shoot-dodge** on Left Alt or V: a 0.2 s run-up, dives in any direction, a long low flight, wall stops and slides, a floor slide, lying down aiming, getting up. See [[Shoot-Dodge]].
- **Last Stand:** a killing blow on a player with a painkiller and a loaded gun drops them into localized bullet time with the camera dragged onto the killer; killing or downing the killer in 4 s costs a painkiller and all adrenaline, followed by a 3 s defenseless wakeup. See [[Last Stand and Bullet Time]].
- **Bullet time** exists as a local bubble (`TimeScale` on characters), and the HUD's slim bar is now the **adrenaline** meter.
- **Accuracy modifiers** for walking, sprinting, crouching, jumping, diving, blind fire, peeking, aiming from cover and dual wielding.
- **Shots leave from a server-placed muzzle** and are blocked by anything solid in the gun's path; the reticle shows a cross when blocked.
- **Aiming is tracked by the server** (0.15 s settle time) instead of a flag on each shot; aiming slows walking to 70%.
- **Server checks** for every stance request, dive, cover claim, hold, drop and pickup, plus a movement-speed check that puts speeders back.
- **Animation preparation:** every animation has an empty slot in `AnimationConfig`; `AnimationController` will play them, stretching reloads to the server's timers. See [[Animation Hooks]].
- **HUD:** three fixed gun rows, pickup and cover prompts, short messages, a stance tag, the Last Stand countdown, a bullet-time label, the dual-wield warning, a blocked reticle.
- **Code layout:** new shared modules `StanceRules`, `CoverRules`, `DodgeRules`, `ShotRules`, `LoadoutRules`, `LastStandRules`, `AnimationConfig`; new server modules `StanceService`, `LoadoutService`, `LastStandService`, `BulletTimeService`; `CharacterServer` replaces `LimbServer`; `WeaponServer` rewritten; new client controllers `Keybinds`, `CoverController`, `DodgeController`, `LastStandController`, `AnimationController`, `WeaponEffects`; `CharacterController`, `WeaponController`, `CameraController` and `Hud` rewritten or extended. New remotes `StanceRequest`, `StanceResult`, `WeaponAction`, `LastStandEvent`. See [[Architecture]].
- **Test arena** north of the spawn: cover walls, a pillar, crates, an inside corner, a dive lane, a ledge, a crouch tunnel, a table with every gun, target dummies and a gunman that shoots back (press T). See [[Test Arena]].

**Decisions**
- The sawn-off stays one-handed (as in Max Payne 3 and the previous build), even though it is a shotgun. One line in `WeaponConfig` changes it.
- Dodge on Left Alt or V, cover on E, pick up on F, drop on G, crouch on C. Space stays jump. Shift stays sprint.
- During a Last Stand the downed player can't be hurt; only the window and line of sight decide. The killer's way out is to hide.
- High cover can only be aimed or blind fired from an end, as in Max Payne 3 (lean out at a pillar).
- No slow motion during dives: Max Payne 3's multiplayer isn't confirmed to have it, and slowing a whole server isn't possible.
- This place has no Roblox PlayerModule, so the client reads WASD and the left stick directly.

**Tested in Studio play mode** (details in [[Test Arena]])
- Crouch, the tunnel's headroom check, sprint and the trigger ending it.
- Dual wield and the drop, pickups and swaps, interrupted and full reloads, dual reloads, dropping with G.
- High and low cover, ends, pop-out and back, inside corner, circling the pillar, aimed shots and blind fire from cover, blocked blind fire.
- Forward, sideways and backward dives, a head-on dive into a wall, getting up.
- Last Stand: start, camera lock, bullet time on the killer, success with its costs, the wakeup, failure by timeout, instant death without painkillers.
- Arm injuries ending dual wielding; the server pulling back a faked speed hack. No errors in the output.

**Not done or not tested**
- No animations (as requested); the body sinks for crouches and guns hang from the hands. No sounds.
- Not tested with two real players or under lag; no touch controls.
- The angled wall, the ledge dive and Last Stand's line-of-sight failure weren't tried in play. Studio's Script Analysis wasn't checked.
- Player-triggered bullet time from the adrenaline meter, vaulting and rolling on the floor aren't built.

## 2026-10-31: HUD restyled to match the Max Payne 3 reference
**Changed**
- **Health display:** the boxy body figure is replaced by a 3D human figure, matching your AK screenshots. It is Roblox's "Man" body, seen from behind in see-through grey. Each limb fills red from its lowest part up (feet first), and a limb in the red is red all over.
- **Painkiller count:** now a black number in a white square on the figure's back.
- **Slim bar:** a white bar beside the figure, a placeholder for the future bullet-time meter.
- **Status text:** red text with no box.
- **Gun list:** restyled to match the figure. No black tiles or white outlines; the guns are see-through grey shapes and the gun in hand is bright white. Ammo is written like Max Payne 3's "30 120": magazine in bold white, spare rounds in grey.
- **Keybinds:** unchanged, as asked.
- `ReplicatedStorage.Assets.UI.HealthFigure` added. `WeaponController` now sends the HUD numbers instead of a ready-made ammo string.

**Tested**
- Previewed in edit mode, then checked in play mode with no errors.
- The equipped AK row read "0 | 26 | 30" after a burst.
- With the left leg half damaged, the foot showed red, the shin half red and the thigh grey. The right arm in the red was fully red, and its two-handed guns faded in the list.

**Not done**
- The figure is chunkier than Max's slim one; a custom figure would need modelling.
- The bullet-time bar doesn't move yet.

## 2026-10-31: Weapon overhaul, camera, limb health and HUD
**Changed**
- **Ammo:** every gun now spawns with a full magazine plus **one spare magazine** (was several spare magazines).
- **Recoil:** CS2-style. Server-side spread grows while firing and settles after a pause. A fixed spray pattern per gun moves the camera, and each shot adds a sharp jerk.
- **Aiming:** right mouse button. The camera zooms in and spread tightens. The Barrett M107 gets a heavy second zoom into a scope overlay.
- **Tracers:** the thin instant line is replaced by a two-beam glowing streak that travels at the gun's bullet speed.
- **Muzzle flash:** the glowing ball is replaced by a real light that briefly lights the surroundings, plus flame, spark and smoke particles.
- **Impacts:** sparks and dust on surfaces, blood on bodies.
- **Camera:** locked to third person over the shoulder, with no first-person view. Q swaps shoulders. The character always faces where the camera points.
- **Limb health:** head, torso, both arms and both legs each have their own health. Limping, crawling, one-arm and disarmed rules apply, and the head or torso in the red kills.
- **Painkillers (H)** heal every limb. Players start with 3.
- **Shoot-dodge hooks:** the `ShootDodgeScale` attribute (1, 0.4 or 0) is ready for the dive when it's built.
- **Sprint** on Shift, blocked by limping or aiming.
- **HUD:** keybinds bottom left; weapon slots with white outline icons and ammo bottom right; body figure with painkiller count and status tag. Roblox's own hotbar and health bar are off.
- **Weapon switching:** keys 1–0 and the mouse wheel, since the Roblox hotbar is gone.
- **Code layout:** split into modules. Server: `WeaponServer`, `LimbServer`, `LimbService`. Shared: `WeaponConfig`, `WeaponMath`, `LimbRules`. Client: `ClientMain` starting `CameraController`, `CharacterController`, `WeaponController` and `Hud`. The old `WeaponClient` was removed.
- `StarterPlayer.EnableMouseLockOption` turned off, so Roblox's shift-lock doesn't fight the camera or the sprint key.

**Decisions**
- Hits stay instant (hitscan), as the networking notes recommend for the first prototype. The tracer only shows the bullet's travel.
- Recoil lives on the client camera; spread stays on the server. A no-recoil cheat is possible, but a no-spread cheat isn't.
- The client tells the server whether it is aiming. This is cheatable for now and logged as a follow-up.
- Weapon icons are drawn from untextured copies of the real gun models, so no images had to be uploaded.
- The "one magazine, no reserve" line in [[Max Payne 3 HUD and Combat UI Reference]] was replaced by this milestone's rule: one spare magazine.

**Tested in Studio play mode**
- No errors in the output log.
- Camera: locked third person on the right shoulder; Q moved it to the left shoulder and back.
- Aim zoom: 70 to 52 for normal guns. The sniper reached its overlay at 0.45 s, and switching guns mid-aim blended smoothly both ways.
- Firing: the MP5 fired at its rate. The muzzle light lit up during the burst and switched off after. The camera climbed 3.7° and recovered within 1.5 s.
- Spread on the server: AK hip 0.2° growing to 4°; aimed 0.3° growing to 1.8°.
- Tracers travelled at the configured speed (AK 2,000 studs/s) with a 7-stud streak.
- Reload used the single spare magazine (MP5 21 rounds → 30 / 21).
- Sprint: walk speed 24, back to 16 on release.
- Every limb rule, painkiller use and cooldown, gun dropping and equip blocking, real shots hitting the right limbs on a dummy, and torso death with a clean respawn. Details in [[Limb Health]].

**Not done or not tested**
- No animations (as requested), sounds, ammo pickups or touch controls.
- The shoot-dodge itself isn't built; only its hooks exist.
- Not yet tested with two real players or under network lag. Not tested on phones or consoles.
- Studio's Script Analysis (strict type warnings) wasn't checked. Only runtime errors were watched.

## 2026-10-31: First working guns
- Made the 13 guns in `ServerStorage.WeaponKit` usable: server-checked hitscan shots, ammo and reloads, fire-rate limits, spread that grows while firing, slide kick, muzzle flash and tracers, an ammo readout, and a Studio-only test loadout.
- Tested: fire rate, spam and bad-data rejection, walls blocking shots, shotgun pellets, headshots, reload cancelling, respawn.
- Superseded the same day by the overhaul above.
