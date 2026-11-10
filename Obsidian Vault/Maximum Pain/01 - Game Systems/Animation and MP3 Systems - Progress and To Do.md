# Animation and MP3 Systems: Progress and To Do

Work log and work queue for the Max Payne 3-style animation and movement pass (bullet time, vaulting, hit reactions, ragdoll, kill cam, Blender animations, cover). Picks up where the [[Changelog]] entries of 2026-11-01 leave off; session 6 (2026-11-09 to 10: blind fire on the low and high cover runs, carried guns over vaults, running vaults, bullet time checked) is the newest. The [[#To do (in order)|to-do list]] was updated on 2026-11-09.

> [!note] Two "session 4"s
> Two sessions ran in parallel from session 3's notes, on different PCs, and both called themselves session 4: **2026-11-04** (JackT6785's PC, the polish pass) and **2026-11-07** (this PC, side-on cover). They were merged on 2026-11-08 (`85d5b61`) and the notes reconciled on 2026-11-09. Each is named by its date below. The 2026-11-04 pass's open polish items were 4.14 to 4.17 in its own list; they are now **4.21 to 4.24**, since the 2026-11-07 list had used 4.14 to 4.20.

> [!warning] Save the place
> The game's scripts and the 102 imported clips live in the Team Create place ("Untitled Experience", place 70765307359272). Save it (File > Save to Roblox) after each session. If Studio's Drafts window lists scripts, commit them first. The Blender scripts, the clips' keyframes and the `.blend` are in the repo.
> **The game's code isn't in git, on purpose** (decided 2026-11-07: the repo is public). The repo's `Maximum-Pain.rbxl` is the 80 KB file from the first commit (2026-10-29, before the restart), so the place is the only copy of the code.

Related: [[Architecture]] · [[Animation Hooks]] · [[Movement State Machine]] · [[Cover System]] · [[Shoot-Dodge]] · [[Last Stand and Bullet Time]] · [[Loadout and Dual Wielding]] · [[Test Arena]] · [[Euphoria-style Reactions and Ragdolls]] · [[Max Payne 3 Kill Cam]]

## Where things stand (2026-11-10)
| Item | State | Who | Next step |
|---|---|---|---|
| **Place** | The 2026-11-04 session changed 9 scripts and added the test harness; the 2026-11-07 session changed 5 scripts and 25 clips (24 remade, 1 new); session 5 changed 3 scripts and 5 clips (4 new); session 6 changed 6 scripts and added 4 clips. Not saved since | Whoever opens Studio next | Commit any drafts, save ([[#1. Save and push]]) |
| **Repo** | Pushed up to `d6c9401` (2026-11-09: the notes fixed after the merge `85d5b61`). Session 6's `mp_hands.py`, export, `.blend` and notes are changed, not committed | JordanSaa | Commit and push ([[#1. Save and push]]) |
| **Play tests** | Every single-player test passes, the new cover included (sessions 4 and 5); the two-client test hasn't been run | Anyone, in Studio | [[#2. Play tests]] |
| **Cover pose** | Decided: side-on for high and low cover, as Max Payne 3 (2026-11-07). Done in session 4; the low cover turns in session 5 | — | Polish 4.15 to 4.20 |
| **Polish** | Done: 4.1 to 4.4, 4.13, 4.14, 4.19, 4.23 to 4.25, 4.27. Open: 4.5 to 4.12, 4.15 to 4.18, 4.20, 4.21, 4.22 (2026-11-04), and 4.26 (new in session 6). None blocks anything | Anyone | [[#4. Polish]] |
| **Animations** | All 102 clips play in Studio. None of the 109 slots has a published id, so live servers play Roblox's default animations | JordanSaa (the place's owner) | [[#5. Publish and document]] |

---

## Session 6 (2026-11-09 to 10): blind fire on the low and high cover runs (4.19, 4.25), carried guns over vaults (4.23), running vaults, bullet time checked
- **When and who:** 2026-11-09, on this PC (jorda), Studio signed in as 83tg, Claude Code driving Blender 5.2.3 (headless) and Studio. JordanSaa decided 4.19 the same day: keep the slide and make new clips (its second option).
- **The fault:** `BlindFireLowLeft/Right` twist the waist for the still body's hips, which face out from the wall. On the run the hips face the way it goes, so the chest turned the wrong way and the gun swung 2.7 out from the wall, pointing back along it. Measured again in Blender: on the run the head's top rose to 3.25 over the floor, and going left the free hand went 0.19 into the wall.

### 1. The clips (`mp_hands.blind_fire_move`, `RUN_FIRE`)
| Clip | What it does |
|---|---|
| `BlindFireLowMoveLeft` | Going left the gun arm is on the wall side. The chest comes partly out of the run's fold (about 50° from upright; the run's is 85°) and turns toward the wall, lifting the gun shoulder. The arm goes straight up and the gun points across the wall, as high as `BlindFireLow` holds it (`LOW_TOP + 0.7`). The head stays ducked under the raised arm, looking down ahead along the wall |
| `BlindFireLowMoveRight` | Going right the gun arm is on the open side: the chest rolls onto its left side, gun shoulder on top, facing out from the wall, and the arm goes straight up from it |

- Both key the right arm, the waist and the neck, as `BlindFireLow` does, loop at 0.5 s with the same firing judder, and are made on the run's body at the start of its cycle (Action2).
- **Found by a search, then checked:** the poses were searched for in Blender (waist angles, where the head looks, the grip, the elbow's way, the gun's cant), each candidate scored on the run's whole cycle and on the blends into it, then rounded and checked again on the shipped code. On the default R15, over the run's cycle and with the judder:
  - the gun's box 0.37 (left) and 0.38 (right) over a 3.6 top, pointing across the wall;
  - the head's box at most 3.32 and 3.31 over the floor, as high as `BlindFireLow`'s (3.31; the run's own is 2.98);
  - nothing of the gun arm or gun in the wall, and the torso no nearer the wall than the run's upper arms, so the game's gap holds;
  - dual pistols (the second gun from `CoverHoldLowDual`), the carried AK (`CarryTwoHandedCoverLow`) and a rifle in the right hand also out of the wall.
- **Head height, measured honestly:** these notes' "head top" has been the centre of the head's top face. With the head tilted forward the box's back corner rises higher: 3.49 for a first version of the left clip. The new clips are checked on the box's highest corner.
- **Self-check** in `mp_hands.register` (`check_run_fire`): each clip on 16 points of the run's cycle, the gun's box 0.3 over the top, the head's box under 3.35, the gun arm and gun out of the wall (sampled through each box), the torso's reach under `BACK_REACH`. The export stops if not.

### 2. How Roblox blends, and why going right can't cross-fade
- **Measured in Studio** (two tracks on one joint of a cloned rig with no scripts): tracks of the same priority blend joint by joint, weight-normalised, by normalised linear interpolation of the rotations, the short way round. 110° and −110° at weights 0.68 and 0.32 gave 151.7°, exactly that; 100° and −100° at 0.5 each gave 180°. A higher priority overrides the lower ones by its total weight: one track at 0.5 over the rest pose gave half its turn.
- **Going right the chest turns about 150°** between the still clip (chest facing away from the right edge, gun shoulder at the wall) and the run (hips the way it goes, gun arm on the open side). The waist changes only 63° (the hips take the rest), but the gun arm has to turn as far as the chest to keep the gun pointing across: the shoulder ended 169.5° from the still clip's.
- **Near a half turn the way round flipped** with the firing judder (a few degrees). At the start and end of a slide right the gun swung round to point back along the wall for about 0.1 s (barrel −0.66 to −0.95 across), and on a reversal the head (0.62) and the carried AK (0.82) went into the wall. A cloned rig playing only the clips at the game's weights did the same, and so did Blender with Roblox's blending; the first simulation had sampled the clips at slightly different times and shown a clean blend. A search for a pose that keeps the gun pointing across through those blends found none: the joints can be kept under 135° apart, but the gun still swings.
- **The fix, in `AnimationController`:** `BlindFireLowMoveRight` (`DIP_CLIP`, now `DIP_ANY`) never cross-fades with another blind fire clip. The clip being left goes down into the cover hold at `DIP_FADE` (50 per second: under 0.05 in 0.06 s, before a reversal's hips have swung round), then the new one comes up at the usual rate. Going left, the still and run clips cross-fade: checked at many weight mixes and clip times, the gun keeps pointing across.

### 3. Scripts changed in session 6
| Script | Where | Change |
|---|---|---|
| `AnimationController` | client | `cover()` records the way the body runs along cover each frame (`rig.sliding`); hidden in cover and sliding, blind fire plays `BlindFire<Low/High>Move<way>` (the still clip if it's missing), picked the same frame as the run; `DIP_ANY` (first `DIP_CLIP`), `DIP_FADE`, `dipFor` (first `blindFireShowing`), `rig.dropping`: the low run going right never cross-fades with another blind fire clip, nor the two high runs with each other (part 8) |
| `AnimationConfig` | shared | `BlindFireLowMoveLeft/Right`, `BlindFireHighMoveLeft/Right` (109 slots) |
| `AimLayer` | client | `guardArm` tests where the body will be drawn (`ahead`: the root's velocity × `math.max(physicsDt, renderDt)`); `renderDt` from `PreRender`; `update` gets `physicsDt` |
| `VaultRules` | shared | `SERVER_SLACK` 2.5 → 7.5 (the server's copy of a running character lags) |
| `BulletTimeRules` | shared | `ACTIVATOR_SCALE` 0.6, and a self-check that it's between `VICTIM_SCALE` and 1 (part 9) |
| `BulletTimeService` | server | `refresh` slows a character with its own session to `ACTIVATOR_SCALE`, except in a Last Stand (part 9) |

### 4. In game (83tg's avatar, the LowWall; M9 in hand, Uzi holstered, AK carried)
- **Sliding while firing, both ways** (held with `LastShot`, and with real shots through `FireWeapon`): the run's clip plays exactly while its run plays; the muzzle 0.52 to 0.72 over the top, pointing across (0.95 to 0.99); the head's box 0.32 to 0.45 under the top; nothing in the wall; the gap unchanged.
- **Starting to fire mid-slide, both ways:** the gun comes up muzzle first and points across in 0.12 to 0.25 s; nothing in the wall.
- **Starting, stopping and five reversals while firing:** nothing in the wall; the gun never points back along the wall (on the right-hand switches it dips and comes up again, muzzle up); the head under the top.
- **Dual pistols** (M9 and Uzi): the Uzi rests on the wall's face (0.05, the arm guard's slack) going right. **A rifle** (FAL, from the gun table): rests on the top (0.05), held upright through the dips.
- Output log clean.
- **Found:** high cover has the same fault while sliding (4.25, done in part 8), and a rifle goes into the wall in high cover blind fire (4.26).

### 5. The arm guard checks where the body will be drawn (to-do 4.23)
- **The fault:** the carried AK went 0.29 to 0.33 into the wall's top edge for 7 to 9 frames at every vault's take-off (default loadout: M9 in hand, AK carried in the left hand). The vault leans the body onto its left hand over the top, so a gun carried in that hand rides down into it.
- **Why the guard missed it:** `ProceduralLayer` applies on `PreSimulation`, before physics. `guardArm` cleared the arm for where the root stood then, and the physics step moved the body on by its velocity before the frame was drawn: 0.3 at the take-off's 14 to 20 studs/s. Redone by hand on a recorded frame, a 15° lift (well inside its 60° limit) would have cleared it.
- **Fix (`AimLayer`):** the guard tests against where the body will be when the next frame is drawn: obstacles are queried round `pivot + ahead` and moved back by `ahead`, the root's velocity times `math.max(physicsDt, renderDt)`. Physics moves a walking body by its velocity over the physics step; a vault (or a dive's mover) places the root by the render step's time, whatever the physics step took (0.013 against 0.016 left one frame at 0.11). `renderDt` comes from `PreRender`; `update` gets the real, uncapped step as `physicsDt` (its own `dt` is capped at 1/20 for the springs).
- **Tried and dropped:** a vault carry clip (the rifle held up behind the shoulder or upright at the side) cleared every obstacle in Blender, but no one pose blends cleanly from the four carries a vault can start from (they differ by up to 162°): the rifle swept 0.5 to 0.8 through the body, and from low cover the joints were a half turn apart. A wider guard limit (110° while vaulting) changed nothing, which led to the timing above.
- **Result** (83tg's avatar, the LowWall, AK carried): the AK rests on the top edge, 0.05 (the guard's slack), drawn and after physics, standing, running and sprinting. Out of low cover: nothing drawn; 0.20 for one frame after physics in the take-off turn (4.15's frame).

### 6. Running vaults refused by the server (new)
- **Found:** a vault started while running (16 studs/s, 3 studs out) played for 3 frames, then the server answered `Rejected … NoVault`: the client let go (`Freefall`), the body dropped onto the top of the wall with the legs through it (up to 1.58), and ran off along the top.
- **Why:** the server checks the vault from its own copy of the character (`VaultRules.find` with `SERVER_SLACK`). That copy lagged about 0.25 s: when the client vaulted 3.2 from the wall, 0.26 s into the run, the server's copy was still 6.9 from it and not yet moving, past `REACH` + 2.5. From the client's place the server's check passes.
- **Fix (`VaultRules`):** `SERVER_SLACK` 2.5 → 7.5, a sprint's lag (24 studs/s × 0.3 s) with some room. The client itself never vaults from further than `REACH` (3.6), and the server still checks the obstacle's height, depth, far side and landing room.
- **Result:** running (16) and sprinting (24) vaults accepted and completed; nothing in the wall but the AK resting on the top (0.05). A sprint vault pressed late (1.4 from the face) touched the face with the sprinting stride for one frame before the take-off (the holstered Uzi 0.19): 4.5's close take-off.

### 7. High cover, stepping out and back (to-do 4.24)
- Re-measured at both ends of the HighWall (83tg's avatar, AK carried): stepping out, the gun forearm 0.09 for 9 frames working left, everything else at or under 0.08; stepping back, the M9 0.05 for 2 frames. No upper arm in the wall: the 0.43 of 2026-11-04 was the old pose facing the wall, before cover went side-on.

### 8. Blind fire on the high cover run (to-do 4.25, 2026-11-10)
- **The fault:** on `CoverHighMove` the still `BlindFireHigh` clip twists the chest for the idle's body, and the gun turned back along the wall. The still clip reaches round a wall's end; mid-wall there's no end to reach round.
- **The clips** (`RUN_FIRE` `HighLeft` and `HighRight`, made by the same `blind_fire_move` as the low ones):

| Clip | What it does |
|---|---|
| `BlindFireHighMoveRight` | Going right the gun arm is on the open side. It points straight out ahead along the wall, a little above the shoulder, the barrel level; the waist as the run's, the head looking ahead along the wall |
| `BlindFireHighMoveLeft` | Going left the gun arm is on the wall side. The chest turns 27° from the run's so the gun shoulder leads, and the arm points ahead with the gun in front of the chest, the head looking along it |

- **Searched and checked as the low ones, with one more rule:** the gun arm and gun clear of the head and torso. The first left pose put the forearm 0.6 into the head's box (the gun across the face); the search had only checked the wall. On the default R15, over the run's cycle and with the judder: nothing in the wall, the barrel within 8° of the way the body runs, the forearm at most 0.10 into the torso's box (the boxes are crude: the cover hold's own is 0.79), nothing in the head.
- **Self-check** (`check_run_fire`, now per height): each high clip on 16 points of the run's cycle, the gun arm and gun out of the wall, the barrel within 14° of straight ahead, the torso's reach under `BACK_REACH`. All four run clips are now also checked for the forearm, hand and gun out of the head; it rejects the first left pose.
- **Blends,** simulated in Blender with Roblox's blending and `AnimationController`'s fades for every switch: starting and stopping a slide (also from the other side), and raising or lowering the gun mid-slide, cross-fade cleanly with the pistol, a rifle and dual pistols. The joints stay within 135° of the still clips and the holds, apart from two at 137° and 138° (the dual and rifle holds), which blend cleanly.
- **A reversal can't cross-fade.** The two runs' gun arms are on opposite sides (the wrist 146° apart), and with the velocity flipping in under 0.05 s the gun swept up to 1.0 into the wall. So they dip on a reversal (`dipFor`), as the low run going right does: nothing in the wall at any reversal speed with the pistol or dual pistols. A rifle still sweeps 0.5 to 0.9 in for an instant reversal in the simulation, less than the still clips' own (4.26).
- **`dipFor`** replaces `blindFireShowing`: it looks for any blind fire clip still showing that the new one mustn't cross-fade with. `blindFireShowing` took the first showing clip it found, so a dip could be missed with two showing (a reversal can pass through the still clip for a frame).
- **In game** (83tg's avatar, the HighWall; the M9, then the AK-47 in hand, then dual M9 and Uzi; blind fire held with `LastShot`):
  - Sliding both ways: the barrel 0.99 to 1.00 along the wall the way the body runs; nothing in the wall; the new clips' arm and gun 0.00 to 0.02 into the head's box. The still `BlindFireHighRight`'s own is 0.39: its forearm passes beside the head, under the hood in a screenshot.
  - Reversals: Roblox flips the slide's velocity in one physics frame (9.6 to −8.3 to −9.6). The old clip dips into the hold (the pistol's muzzle down, the rifle's up) and the new one comes up. Nothing in the wall.
  - Starting and stopping, also from the other side: cross-fades; nothing in the wall; the arm and gun at most 0.09 into the head's box mid-blend.
  - The AK rests on the wall (0.05) in the still clips, held off by the arm guard, and is clear while sliding. Dual pistols: the left gun and arm clear too.
  - Output log clean.

### 9. Bullet time checked against [[Last Stand and Bullet Time]] (2026-11-10)
- **Why:** in a play test the player moved freely, with no penalty, in their own bullet time.
- **What the note says:** everyone the activator can see slows to 0.3, lower-level victims also aim at 0.35, and the activator keeps full speed unless someone else's bullet time sees them. `BulletTimeService` does exactly that.
- **In game** (83tg's avatar, the TargetOpen dummy about 20 studs away):
  - The player triggering it with a full meter (X): level 3 for 5 s, the meter drained to 0. The dummy went to 0.3; the player stayed at 1 and walked at 16 studs/s. The player's screen showed the BULLET TIME label and the drained colour.
  - The dummy triggering it on the player (`DebugBulletTime`): the player at 0.3, walking at 4.8, `AimPenalty` 0.35; back to 1 after 5 s.
  - The player counter-activating at the same level: the penalty cleared at once; both at 0.3 while they could see each other; both back to 1 with the pillar between them.
- **So it worked as the note said: moving freely in your own bullet time was the rule.** Max Payne 3 differs: there the user is slowed too, less than their victims, and the slow-down chains through the victims' sight ([[Max Payne 3 Mechanics Reference]]).
- **Changed the same day (to-do 4.27, JordanSaa's decision): the activator slows to 0.6.** `BulletTimeRules.ACTIVATOR_SCALE` (a self-check keeps it between the victims' 0.3 and 1); `BulletTimeService.refresh` applies it to a character with its own session. A Last Stand is left out: its bubble keeps the downed player at full speed, and a bullet time started before the killing blow would otherwise slow them through the stand. Everything that reads `TimeScale` follows (walking, sprinting, fire rate, reloads, dives, vaults, the clips); the aim isn't slowed.
  - Triggered mid-sprint with a full meter: 0.6 at once, sprinting at 14.4, walking at 9.6, back to 1 after 5 s; the dummy in view at 0.3; no movement-check strike; output log clean.
  - A Last Stand during it (the gunman's hit on a torso set to 10): 0.6 until the killing blow, then 1 for the whole stand while the player's own bullet time ran on; the gunman at 0.3 in the stand's bubble.
  - Not done: the chain through the victims' sight.
- Not checked here: one or two levels (1.67 s each; `BulletTimeRules`' self-check covers the maths), and two real players (the two-client test).

### Repo changes in session 6 (not committed yet)
- `mp_hands.py`: `RUN_FIRE` (low and high), `blind_fire_move`, `check_run_fire` and its limits, the four clips registered with the self-check, the module's opening note.
- `Exports/keyframes.json` (102 clips) and `MaximumPain_Animations.blend`. Only the four new clips differ from session 5's export.
- This note, the [[Changelog]], [[Cover System]], [[Animation Hooks]], [[Architecture]], [[Test Arena]] and the README.

---

## Session 5 (2026-11-08): the low cover turns (to-do 4.14)
- **When and who:** 2026-11-08, on this PC (jorda), Studio signed in as 83tg, Claude Code driving Blender 5.2 (headless) and Studio (`/mcp` had reconnected it; Studio's id changes when it restarts).
- **The fault:** side-on, the low idle faces out from the wall and the aim faces over it. Popping up and ducking back turned the body about 166° in the body layer's 0.2 s blend: a foot went 0.43 and a shin 0.55 into the wall's base, and the aim clip's arm 1.2 into the top on the first frame.

### 1. The turn clips (`mp_stances.cover_turn`)
| Clip | What it does |
|---|---|
| `CoverPopUpLeft/Right` (0.25 s) | Rises, leaves the wall, then turns toward the edge being worked to face over the wall (working right from -180° through -90° to the aim's 14°; working left through 90°). The hips sway 0.6 out from the wall halfway round (`TURN_SWAY`), so the side-on torso doesn't go into it. The foot on the outside of the turn steps first. Bound to `CoverPeek`, which is as long |
| `CoverDuckLeft/Right` (0.3 s) | Turns and folds over first (the turn in the first 55%, the fold in 70%), then goes down once the feet are round (`DUCK_DROP` 0.2 to 1), and settles back against the wall |

- **Built for the height ease:** the game changes the hip height at once and `AimLayer` holds the body where it was, easing it to the new height at 10 per second (63% in the first 0.1 s). The clips plant the feet where that hold leaves the floor. Ducking, the clip's root also takes back what the hold has eased, so the hips' height over the floor follows `DUCK_DROP` whatever the hold does.
- **Knees** turn with the feet (75%) and the hips (25%), from the bend in the pose the clip starts on to the bend in the pose it ends on. Each clip starts on the legs of the pose before it (within 3°) and ends on the next one's, apart from what the height ease still has to do: the pop-up ends 0.15 low, the knees up to 20° more bent, and the aim takes over at the rate the ease finishes. Where a knee, or a gun holstered on the left thigh (the Uzi's box, measured in the game), would reach past the wall's face (1.15 from the root part), the knee turns out from the wall by the least that clears it (`leg_reach`, `LEG_REACH`).
- **Sampled at 60 per second** (the other clips are 30): they turn half round in a quarter second.
- **`CoverAim`'s back heel is up 22°** (6° before). Flatter, its shin leant 31° over the foot and the box went 0.12 into the floor.
- **Faults found and fixed while making them** (measured in Blender on the default R15's boxes):
  - The first version bent the knees away from the wall whichever way the feet pointed: once the feet had stepped round, the knees bent backward over them, and the legs ended 100° to 146° twisted from the aim pose they hand over to.
  - Following the feet, the front knee went 0.17 into the wall (the aim's front foot is 0.2 from it) and the holstered Uzi 0.2.
  - Ducking, `AimLayer`'s hold dropped the hips halfway in 0.06 s while the feet were still stepping round: the hips swung out over the planted feet, the knees folded forward and the shins went 0.3 into the floor (now 0.09 to 0.12, box corners).
  - Folding the body over across the whole duck kept the head over the wall until 0.19 s; folded with the turn, it's under at 0.17 s. Folding any faster put the chest in the wall.
- **Checks** (scripts kept in the session's scratchpad, not the repo): each clip frame by frame against a wall 1.15 from the root and the floor where the hold leaves it: every box's depth in the wall and under the floor, the knee bends, the head top, and each end against the pose it joins (joint by joint).

### 2. Scripts changed in session 5
| Script | Side | What changed |
|---|---|---|
| `AnimationController` | client | `POP_TIME` 0.25, `DUCK_TIME` 0.3, `TURN_FADE` 25, `POP_AIM` 0.15. `stanceChanged`: low cover to `CoverPeek` plays `CoverPopUp<side>` bound to the stance; `CoverPeek` or `CoverAim` back to low cover plays `CoverDuck<side>`; in real time (the height ease is). `poppingUp`: for `POP_AIM` the gun keeps the low cover hold and carry (`ready` is false). Other players' characters use the right-hand clips, as their cover idles do. |
| `AnimationConfig` | shared | `CoverPopUpLeft/Right`, `CoverDuckLeft/Right` (105 slots). |
| `AimLayer` | client | The foot guard runs in every cover stance, not only while a height change eases. |

### 3. In game (83tg's avatar, the LowWall)
- **Popping up and ducking back, both sides:** no leg in the wall; a shin 0.08 under the floor for one frame at most (0.22 with the first version of the clips); feet within 0.05; camera steps ≤ 0.08.
- **The gun coming up:** at `POP_AIM` 0.1 s, working left, the gun went 0.59 and the forearm 0.48 into the wall's face: the turn takes the gun shoulder past the wall. At 0.15 s, 0.05 for a few frames. Aiming over the top the forearm rests on it (0.05), as in session 4.
- **Left over:** at the start of ducking back working right, the holstered Uzi is 0.14 in the wall for 2 frames (the clip blending in over the aim); the right upper arm rests on the wall's top edge (0.08) as the aim lowers.
- **Sliding along low cover:** starting and stopping, the idle blends into the run a quarter turn round, and the feet went 0.36 under the floor. With the foot guard on in cover they stay within 0.05. The shins, thighs and holstered Uzi still go 0.33 under it, from the run itself: 4.20.

### Repo changes in session 5 (committed in `35c5e2d`)
- `mp_stances.py`: `cover_turn`, `knee_spot`, `wrap`, `HOLSTER`, `leg_reach`, the turn numbers, `AIM_FEET`'s back heel, the four clips registered at 60 per second, and a self-check in `register()` that each turn starts on the legs of the pose it leaves (within 5°; the export stops if not).
- `Exports/keyframes.json` (98 clips) and `MaximumPain_Animations.blend`. Only the four new clips and `CoverAim` differ from session 4's export.
- This note, the [[Changelog]], [[Cover System]], [[Animation Hooks]], [[Architecture]], [[Test Arena]] and the README.

---

## Session 4 (2026-11-07): side-on cover, the open decisions, the harness
- **When and who:** 2026-11-07 from 19:26 (UK time), on this PC (jorda), with Studio signed in as 83tg and Claude Code driving Blender 5.2 (headless) and Studio.
- **Studio connection:** Studio had updated itself at 19:18 (version 0.746) and Claude Code's Studio MCP link was down. The session drove Studio's own `StudioMCP.exe` over stdio instead; how is in [[#How to resume (tools and tricks)]].
- **Decisions** (from the to-do): the game's code stays out of git; the test harness goes into the repo; cover goes side-on, high and low, as Max Payne 3.
- **Avatar:** 83tg's, a slim R15 (torso 1.4 wide where the default is 1.94; root part 1.4 × 1.8 × 0.9, 3.13 above the floor). The clips are made on the default R15. Numbers differ by avatar: the low blind fire's gun came out 0.28 lower on this one.

### 1. Max Payne 3's cover, from footage
Steam trailer frames, cut with Blender's sequencer at 2 to 4 fps (nothing stored):
- *Design and Tech Video 2* 2:53–2:54: back flat against a tall cabinet, facing out, SMG low, the left hand by the face, head turned to the edge.
- Same, 2:56–2:57: crouched with the back to a low counter, knees up, gun by the shoulder, head turned to the edge; popping up, he turns round over it.
- *Multiplayer* 1:35–1:36: back to a wall at its edge, pistol low, head turned along the wall. 1:43: a rifle upright beside the face.
- The official screenshot `ss_4ae054ce…`: back to the wall, pistol low in both hands, head turned to the window.

So side-on here means back and inner shoulder on the wall, turned toward the edge being worked, head looking along the wall. Moving, the body runs side-on, facing the way it goes. The to-do's earlier "side-on" (shoulder to the wall, `LOW_TURN` 70°) was a guess; the footage is back to the wall.

### 2. How the clips fit the game
- The game keeps the root part facing the wall and keeps the gap the body's reach needs (`CoverController.bodyReach`: head, torso and the upper arms below the top, + 0.05, at least 1.15).
- So the clips turn the body round inside the root part (150° high, 180° low) and slide it back until those parts reach 1.1 toward the wall (`mp_stances.onto_wall`, `BACK_REACH`). The gap comes out at 1.15 and the back rests on the wall.
- Nothing in the gameplay code had to change: cover detection, edges, peeking, the server's checks and the virtual muzzle don't depend on which way the body faces.
- **Wall ends:**
  - The root stops 0.9 short of an end, and an R15's shoulders and edge-side arm reach 1.3 to 1.8 along the wall. Centred on the root, the arm stuck out 0.5 to 0.7 past the end.
  - The idles sit back along the wall, away from the edge (`HIGH_BACK` 0.35, `LOW_BACK` 0.75). Any further, and the right arm can't blind fire round the end working right (it's the arm away from the edge, back to the wall).
  - The runs sit back so the head leads the root by at most 0.8 (high) or 1 (low).
- **Checking in Blender:** each pose was measured against a wall placed where the game would keep it: the head top over the floor, any box inside the wall or the floor, how far along the wall toward the edge, and the guns over the top or round the corner. Contact sheets with a face marker on the head show where it looks.

### 3. The clips (24 remade, 1 new)
| Clip | Now |
|---|---|
| `CoverHighLeft/Right` | Back and inner shoulder on the wall, turned 150° from it toward the edge, feet out from the wall, knees soft, head turned along the wall to the edge |
| `CoverLowLeft/Right` | A deep squat on the balls of the feet, back to the wall, folded over the knees, hands on the knees, the head aimed along the wall to the edge (a look-at: a neck turn on a folded body rolls the head). Head top 2.80 on the default R15 (3.22 before) |
| `CoverHighMoveLeft/Right` | A hunched side-on jog along the wall at 9.6 studs/s, facing the way it goes, the chest open 10° to the room |
| `CoverLowMoveLeft/Right` | A crouched side-on run at 8 studs/s, the fold mostly at the waist (folded at the hips, the trailing shin went 0.63 through the floor); head top 2.98 |
| `CoverCornerHigh/Low…` | The idle, a side-on stride round the corner, the idle |
| `CoverHoldHighOne/Two/Dual` | The pistol low in front of the belly, muzzle down; the rifle upright across the chest (top 4.5, under the 5.2 wall); two pistols up in front of the chest |
| `CoverHoldLowOne/Dual`, `CoverHoldLowTwoLeft/Right` | The gun up beside the face; the rifle upright past the face, leaning away from the edge |
| `BlindFireLowLeft/Right` | Keys the waist and neck: the chest twists 105° to put the gun shoulder to the wall, the arm goes straight up, the gun over the top, the head ducked. The hand stays in front of the wall's face |
| `BlindFireHighLeft/Right` | Keys the waist and neck: the gun arm out along the wall, the gun round the edge. Working right the arm reaches across, the chest leaning out |
| `CarryTwoHandedCover` | The carried rifle muzzle down in front of the left thigh |
| `CarryTwoHandedCoverLow` (new) | The carried rifle by the knee, muzzle forward and down, away from the wall. `CarryTwoHandedLow` stays for crouching and getting up |

### 4. Scripts changed in session 4
| Script | Side | What changed |
|---|---|---|
| `AimLayer` | client | The head's look-at eases to 0 while hidden in cover (`gaze`, `GAZE_EASE` 8): the aim is past the wall, behind the turned head. The momentum lean is worked out in the hips' frame (in the root part's it went the wrong way once the body turned round). The stance is read once per frame. |
| `AnimationController` | client | `carryFor`: `CarryTwoHandedCoverLow` in low cover. |
| `AnimationConfig` | shared | The `CarryTwoHandedCoverLow` slot; cover comments. |
| `CoverController`, `CoverRules` | client, shared | Comments only. |

### 5. Found in the place: work after 2026-11-03 that the notes didn't have
Found reading the scripts (not re-tested, except through the cover tests):
- `AimLayer.guardArm`: each arm, its gun and the carried gun are turned at the shoulder (lift, swing or yaw, up to 60°) just enough to stay out of walls. This covers to-do 4.2 and 4.7.
- The dive landing is held and eased like a crouch (`DodgeGround` is no longer in `FALLS`), so the root no longer falls 2.4 and bounces (4.3). `MAX_FOOT_LIFT` is 1.2.
- `VaultRules.LEG_CLEARANCE` = 0.3 (4.4).
- `AnimationController.watchReloads`: each client runs the reload markers on everyone else's reload tracks (4.13). `restGun` puts a gun back to rest when a reload is cut short. Every clip is loaded at spawn.
- `CoverController`: `bodyReach` counts the upper arms below the cover's top; `stepToward` caps the step out of high cover at what lands on the spot by the next frame.
- `ServerStorage.Tools.TestHarness` (733 lines) and a module version of `AnimationImporter`.
- A large block, `Workspace.Part` (4 × 18 × 18 at x 32, z 47), between the spawn and the arena.
- The clips themselves matched the repo's `keyframes.json` exactly (fingerprints of all 93), so no Blender work had been done outside the repo.

### 6. In game (83tg's avatar)
- **Low cover:** head top 2.77, 0.83 under the 3.6 LowWall (3.49 in the 2026-10-31 test). Root 1.21 off the wall, nothing in the wall or the floor, camera steps ≤ 0.08.
- **Ends:**
  - Low: the head 0.47 inside the end and the edge-side upper arm 0.33 past it (0.73 before the idle sat back). While the run blends out, the head is 0.21 past (0.64).
  - High: the head 0.39 inside; arm 0.29, legs 0.15 and the holstered Uzi 0.47 past (head 0.84 and arm 0.96 past before).
- **Blind fire:**
  - Low: the head 0.34 under the top, the gun 0.11 over it, nothing in the wall, the gap held at 1.21. An earlier version with the hand over the wall had the forearm 1.2 in the wall's top edge, and one aimed lower had the gun 0.05 under the top on this avatar.
  - High, working left: the gun 1.07 past the end, round the corner. Working right: just past the corner (0.33), the body leaning out.
- **Popping up and out, ducking back:** the right clips. Aiming over the wall, the forearm only rests on the top (0.05, within the guard's slack). Ducking back into high cover, the gun is 0.22 in the wall for 3 frames.
- **Corners round CrateA:** nothing in the crate during the swings.
- **Vault out of low cover:** flies clear.
- **Faults found:** see 4.14 to 4.19.
- **Screenshots** (taken with the debug camera, not kept): high cover reads like the screenshot, back to the wall, pistol low, rifle hanging, head to the edge. Low cover reads as crouched against the wall, head down and turned along it. Blind fire low is a twist with the gun over the top, the head ducked.

### Repo changes in session 4 (committed in `35c5e2d`)
- `mp_stances.py` (the cover bodies, `onto_wall`, `look`, `HIGH_BACK`/`LOW_BACK`), `mp_hands.py` (holds and blind fire), `mp_arms.py` (`facing`, `placed`, `pole`, `by_part`; the two cover carries).
- `Exports/keyframes.json` (94 clips) and `MaximumPain_Animations.blend`.
- `Tools/TestHarness.luau` (new) and `studio_import.luau` (matches the place's importer).
- This note, [[Changelog]], [[Cover System]], [[Animation Hooks]], [[Architecture]], [[Test Arena]], [[Max Payne 3 Animation Reference]] and the README.

---

## Session 4 (2026-11-04): the polish pass
- **When and who:** 2026-11-04, on JackT6785's PC, with Claude Code driving Studio through the Studio MCP. Before starting: session 3's commits were already pushed (`695e191`, 12:54 UTC) with no screenshots, bytecode or FBX copies on GitHub, and the place had been saved (its copy on Roblox was updated 12:56 UTC).
- **Decisions taken:** keep the hunched low-cover pose (to-do 3, JackT6785); run the two-client test at the end. It then had to wait, because the Studio MCP can't reach the test windows.
- **Setup:** Studio play mode, JackT6785's R15 avatar (hip height 2.38, root 3.38 above the floor), the default loadout (M9 in hand, Uzi holstered, AK-47 carried in the left hand).
- **How things were measured:** the new harness (`Tools/TestHarness.luau`, see [[#How to resume (tools and tricks)]]) records every frame twice:
  - **render:** at the end of the render step. This is what the player sees, including the root moves made in the render step.
  - **post:** after physics, as session 3 did.
  - Wall depths and clearances are exact box-against-box results (separating axes), not sampled points:
    - **Depth** is the shortest move that separates a box from a wall.
    - **Over** is how far a box could drop before touching an obstacle's top.
- **Frame rate:** with Studio in the background, frames are drawn about 15 times a second while physics runs at 60. Render-step code (camera, stances, movers, clip weights) runs in 66 ms steps. Several faults below only showed at that rate, but each also hits players on slow machines, so each was fixed instead of being put down to the test.
- Before any change, a copy of all 40 scripts was taken from the place (kept outside the repo) and compared with the place again at the end.

### 1. Height changes drawn a frame early ✅ (new)
- **Found:**
  - On every stance height change (crouch, stand, cover in or out, pop-up, get-up, the dive's run-up) the first frame drawn showed the whole body a stance's height out. The feet were 1.80 into the floor on a crouch, 1.89 above it standing up, and 0.60 in on the run-up.
  - The camera jumped 0.87 crouching, 0.88 standing and 0.87 popping up from low cover (at 15 fps; about 0.3 at 60).
- **Cause:**
  - `CharacterController.applyHeight` moved the root at once (on the key press, or in the render step), so the body moved with it. The aim layer's hold, which keeps the body where it was, only comes before the next physics step, after that frame was drawn.
  - The camera watched `HipHeight` itself and heard of the root's move separately (`absorbRise`), with its ease in between. Part of one eased away before the other arrived.
- **Fix:**
  - The hip height and the root now change together just before physics. `CharacterController.moveRoot` is the first procedural layer (`ProceduralLayer`; `ClientMain` starts `CharacterController` before `AimLayer`), run right before the aim layer holds the body.
  - `applyHeight` only records the move (`movingFrom`, and `movingGrounded` for whether the character stood on the floor). It keeps `HipHeight` at the height the root stands at until then.
  - A first try changed `HipHeight` at once and moved only the root later. The humanoid checks its floor between the render step and physics, lost the floor and fell (the feet went 0.48 in), so both now move together.
  - `CameraController.absorbHeight(rise, drop)` replaces `absorbRise`: `moveRoot` reports the root's move and the new hip drop in one call, between two camera frames. The camera no longer reads `HipHeight`, which also keeps it steady when the server's hip height arrives before the client's stance.
- **Result:**
  - Crouch and stand: no frame drawn out of place; the feet stay within −0.05 when drawn; the humanoid stays in Running throughout.
  - The camera's largest step is 0.22, which is the ease itself.
  - One physics step on standing up has the feet at −0.10, but it isn't drawn at 15 fps. See 4.21.

### 2. The dive's landing ✅ (to-do 4.3)
- **Found:** the body fell the last 2.4 to 2.8 studs onto the floor at up to 31 studs/s, then bounced, and the camera dropped 1.38 in one frame. Session 3's 0.30 forearm dip didn't occur in this pass (the left forearm stayed at +0.02).
- **Cause:**
  - During the flight the hip height is the standing one (DodgeAir has no hip drop), so the humanoid "lands" and catches the root at standing height before the client's own check (`fly`) calls `land()`.
  - Then DodgeGround drops the hips 2.2. DodgeGround was in `AIRBORNE` and `FALLS`, so nothing moved the root or held the body. The humanoid lost the floor and free-fell.
- **Fix:** DodgeGround left `CharacterController.AIRBORNE` and `AimLayer.FALLS`. The landing now puts the root on the floor at once (measured from the floor: 3.51 → 1.13 → settling at 1.18), and the aim layer eases the body down as for a crouch.
- **Result:**
  - No free fall, no bounce, and the humanoid stays in Running.
  - The landing's camera step is 0.35. The 0.6 to 0.8 steps before it are the flight's own fall at 15 fps, about 0.2 at 60.
  - Hands and forearms ≥ −0.02 against the floor.
  - The body now settles quickly and smoothly rather than slamming down. A fall-shaped ease would feel heavier if it reads as soft (4.22).

### 3. Arms and guns kept out of walls ✅ (to-do 4.2; 4.7 in part)
- **Found (before):**

| Where | What went into the wall |
|---|---|
| Popping up over the LowWall (M9) | gun 0.73, right hand 0.25 |
| Ducking back | gun 0.56 (cutting down through the top) |
| High cover, aim held mid-wall | gun 0.67: the pop-out is refused away from an edge, but the aim clip played anyway |
| High cover at the east end, at rest (working the left side) | right upper arm 0.55, hand 0.45, forearm 0.30, M9 0.11 |
| High cover mid-wall, at rest (working the right side) | the carried AK's left upper arm 0.32 |
| Stepping out round the east end | M9 1.00, forearm 0.85, hand 0.83 |

- **Causes:**
  - Popping up, the aim clip extends the gun forward at 18/s while the body is still held low (it rises at 10/s).
  - Ducking back, the gun is mid-blend between the aim and the low hold while the body sinks.
  - `AnimationController.ready()` let the aim clip play while hidden in cover.
  - Behind high cover the side idles turn the torso about 40° toward the side worked, which puts the leading shoulder about 0.6 from the wall at the 1.15 gap, with the hold's elbow forward.
- **Fixes:**
  - **No aim clip while hidden** (`ready()`): holding aim where you can't pop out keeps the cover hold, as the camera already did.
  - **Arm guard** (`AimLayer.guardArm`), after the arms are posed:
    - Each arm's boxes (upper arm, forearm, hand, the gun in that hand) are tested against collidable parts near the shoulder: `GetPartBoundsInRadius`, ignoring characters, dropped guns and anything tagged NotCover.
    - Any overlap beyond `GUARD_SLACK` 0.05 (the boxes are bigger than the meshes) turns the arm at the shoulder by the smallest clearing angle.
    - The angle is found in 8° steps, then narrowed by bisection. It is at most `GUARD_LIMIT` 60°, or `GUARD_SHOULDER_LIMIT` 30° while the upper arm itself is in the wall. If the upper arm can't be cleared, the forearm, hand and gun still are.
    - Three ways out:
      - **lift** turns the arm toward upright. An aimed gun comes up as from a high ready, and popping up the turn shrinks to nothing as the body rises. Swinging the gun down in front of the wall instead would have had to snap level at the end.
      - **swing** turns the deepest part straight out of what it went into: a hanging arm, the carried gun.
      - **yaw** flares the arm out about the vertical. This is for the bent hold arm (elbow below the shoulder, gun up by the chest), where lifting or swinging moves the elbow and the gun opposite ways.
    - A new contact takes the smallest turn. A raised gun takes the lift unless another way is 12° smaller (`GUARD_PREFER_LIFT`). The way taken is kept while it still works, so the arm never flicks between ways.
    - Order: held guns before the left hand is put back on a rifle (so it follows), the carried gun after its floor lift, and free arms too.
  - **High cover keeps room for the shoulders** (`CoverController.bodyReach`):
    - The gap is the body's reach, now counting the upper arms.
    - Only their parts below the cover's top count, and not at all while firing. Blind fire and aiming over low cover don't push the body back.
    - On JackT6785's avatar this is 1.52 (right side, AK carried) to 1.78 (east end) instead of 1.15. Low cover is unchanged (2.52).
    - A first try relied on the guard alone: clearing the leading upper arm took 63° to 83° turns, which look thrown rather than braced.
- **Result:**

| Where | After |
|---|---|
| Popping up and ducking back (LowWall) | ≤ 0.05 (the slack). The gun comes up over the lip (+19°) then onto the target; ducking it lifts over the lip (+21°) then drops behind it |
| Aim held mid-wall | gun stays in the cover hold |
| High cover at rest, both sides | nothing in the wall |
| Stepping out round the east end | clear; stepping back, a 0.1 s brush (M9 0.20, forearm 0.13) |

  - Camera popping up and ducking back: largest step 0.22 (was 0.87).
- **The step out of high cover overshot back and forth** (the root went −21.44, −21.93, −21.44, −21.97 every frame at 15 fps; 0.33 a frame at 30). It walked at `STEP_SPEED` 10 until within 0.2 of the spot.
  - Now `CoverController.stepToward` walks no faster than reaches the spot by the next frame and stops within 0.05 (`STEP_DONE`).
  - The step also takes `TimeScale` now; it used to run at full speed in bullet time.
- **Not fixed (4.7's remainder):** walking flush along a wall in the open, the root about 1.4 from it, the shoulder is closer to the wall than the upper arm's half-thickness (0.4 against 0.53). No shoulder turn can clear it, so the left arm and the carried AK clip (0.5 to 0.9). Walking into an inside corner presses the legs, head and torso into both walls. This needs the movement to keep the shoulders off walls.

### 4. Vaults ✅ (to-do 4.4; 4.5 in part)
- **Found:**

| Fault | Measured | Cause |
|---|---|---|
| The root sagged between frames | up to 0.47 below the path over the top | in the Physics state, gravity acts for the four physics steps between two placements of the root |
| The root overshot at take-off | 0.7 above the path (6.58 against 5.83), then snapped down; camera 1.60 | the velocity handed to physics was last frame's step, carried on into the steep start of the climb |
| The first vault of a life played its first frames unstretched | legs 0.3 into the obstacle | a track reads a `Length` of 0 until its animation has loaded, and both the stretch and the vault chase skip when it is 0. This also hit the first reload and draw of a life |
| Later vaults sat frozen on frame 0 for a frame | legs 0.78 into the obstacle | a stopped track keeps its old time (the last vault's end), but `Play()` starts it from 0, so the chase computed a negative speed |
| The root left the start a frame before the clip | from 2.18 back, the shin 0.23 into the near face | the mover advanced the clock before placing the root |
| Slow-motion margin | −0.05 at the far edge (0.03 deep) | `LEG_CLEARANCE` 0.2 |

- **Fixes:**
  - `VaultController`:
    - A `VectorForce` the character's weight (`VaultWeightless`) cancels gravity for the vault.
    - The root is placed where the path is now, then the clock advances and physics is aimed at the next frame's place, so it runs along the path's chords at any frame rate.
    - The landing cap is gone, and the landing carries the path's even ground pace on.
  - `AnimationController`:
    - Every clip is loaded when the character is set up.
    - The vault chase counts from 0 for a track it is about to start.
    - The clip chases `VaultController.progress()`, the place the root is aimed at.
  - `VaultRules.LEG_CLEARANCE` 0.2 → 0.3. This adds 0.1 for avatars taller than standard (this one flies 2.33 above the top). A standard avatar stays at 2.1. The self-check now allows for rounding (3 × 0.6 + 0.3 lands just under 2.1).
- **Result:**

| Vault | Lowest point over the top | Notes |
|---|---|---|
| LowWall from standing, 2.5 back | +0.19, no contact at all | no Fall clip, no bounce, feet 0.00 after |
| LowWall from the north, 2.09 back | +0.18 crossing; touches the near face by 0.02 at take-off | was 0.23 |
| Out of low cover | +0.26 | camera 1.55 at take-off (the 4.35-stud rise from a crouch at 15 fps) |
| Bullet time (0.3), 1.86 back | far edge −0.05 with the old clearance; near face 0.13 for 3 slow frames at take-off | 1.52 s in the air (session 3: 1.40) |

  - The take-off camera step is still 1.2 to 1.7 at 15 fps: the path's climb is steepest at its start. That is about 0.4 at 60 fps.
  - The carried AK brushes the top for 7 to 9 physics frames in mid-vault (0.28 to 0.34). See 4.23.

### 5. Others' reloads, and reloads cut short ✅ (to-do 4.13; to be confirmed with two players)
- **Fix (`AnimationController`):**
  - `wireMarkers` connects a reload track's markers to the guns they move: both pistols for ReloadDual, otherwise the right-hand gun. When the track stops, `restGun` puts those guns back at rest (magazine shown, every moving part home).
  - The owner's tracks use it (wired once).
  - `watchReloads` wires everyone else's reload tracks: other players and anything a server script animates, found by their animation id (`slotOf`). Each track is wired when it plays and let go when it stops.
- **Also fixed:** a reload cut short between MagOut and MagIn left the magazine hidden until the next reload, for the owner too.
- **Tested on one client:**
  - A rifle reload played on the gunman by another script moved its AK's magazine and bolt. MagOut hid it, MagIn brought it back, BoltBack moved 0.18 and BoltForward went home, and a spent magazine dropped.
  - One stopped after MagOut brought the magazine back.
  - The owner's M9 reload still went 12 → 15 rounds with every part home.
- **Studio finding:** the temporary ids `KeyframeSequenceProvider` gives a clip differ between processes. The server registered ReloadRifle as `de7f…` and the client as `eab9…`. So in a Studio two-player test, one player can't identify, or even play, the other's clips. A server-played track can't stand in for another player either. With published ids (live servers) every client uses the same id.

### 6. Big drops at a low frame rate ✅ (new)
- **Found:** dropping into a Last Stand (2.2) sank the feet 0.47 for 3 drawn frames.
- **Cause:** the clips' weights change once a drawn frame, while the body's hold eases every physics step. For four steps the legs were still straight, and the foot guard's lift was capped at 0.6.
- **Fix:** `AimLayer.MAX_FOOT_LIFT` 0.6 → 1.2.
- **Result:** a survived Last Stand:
  - Into the Last Stand (2.38 → 0.18): feet −0.05, camera 0.12.
  - Wakeup (0.18 → 1.18) and stand (1.18 → 2.38): feet ≥ −0.05, camera ≤ 0.14.
  - The humanoid stayed in Running; painkillers 3 → 2.

### Scripts changed in session 4
All in the Team Create place (client controllers in `StarterPlayer.StarterPlayerScripts.Controllers`, shared modules in `ReplicatedStorage.Modules`).

| Script | Side | What changed |
|---|---|---|
| `CharacterController` | client | `moveRoot` (first procedural layer): `HipHeight` and the root change together before physics; `movingFrom`, `movingGrounded`; DodgeGround out of `AIRBORNE`. |
| `CameraController` | client | `absorbHeight(rise, drop)` replaces `absorbRise` and the `HipHeight` watching (`lastHip`, `lastHumanoid` gone; `drop` reported). |
| `AimLayer` | client | Arm guard: `guardArm`, `overlap`, `armBoxes`, `deepest`, `clearAngle`, `refreshObstacleFilter`; `GUARD_SLACK` 0.05, `GUARD_LIMIT` 60°, `GUARD_SHOULDER_LIMIT` 30°, `GUARD_STEP` 8°, `GUARD_PREFER_LIFT` 12°. DodgeGround out of `FALLS`. `MAX_FOOT_LIFT` 1.2. |
| `AnimationController` | client | `ready()` refuses aim while hidden; every clip preloaded; the vault chase counts from 0 for a track about to start and follows the mover's place; `wireMarkers`, `restGun`, `watchReloads`. |
| `CoverController` | client | `bodyReach(root, normal, armsBelow?)` counts the upper arms; `stepToward` (`STEP_DONE` 0.05, `TimeScale`). |
| `VaultController` | client | `VaultWeightless` force; place, then advance, then aim at the next place; landing momentum from the path; `lastPosition` and the landing cap removed. |
| `VaultRules` | shared | `LEG_CLEARANCE` 0.3; the `apexAbove(3)` self-check allows for rounding. |
| `ProceduralLayer` | client | Header: it also runs the stance's root move, first. |
| `ClientMain` | client | Comment on why `CharacterController` starts before `AimLayer`. |
| `ServerStorage.Tools.TestHarness` | Studio only | New: the play-test harness. The same file is `Tools/TestHarness.luau` in the repo. |

### Repo changes in session 4
- `Tools/TestHarness.luau` added (to-do 2's optional item).
- This note, the [[Changelog]] and the system notes updated.
- Committed on JackT6785's PC; not pushed.

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
- [ ] **Save the place in Studio again.**
  - **Who:** whoever opens Studio next.
  - **How:** if the Drafts window (View > Drafts) lists scripts, commit them; then File > Save to Roblox.
  - **Why:** the 2026-11-04 session changed 9 scripts and added `ServerStorage.Tools.TestHarness`; the 2026-11-07 session changed 5 scripts, replaced 24 clips and added one; session 5 changed 3 scripts and added 4 clips; session 6 changed 6 scripts and added 4 clips (see [[#Scripts changed in session 4]], [[#4. Scripts changed in session 4]], [[#2. Scripts changed in session 5]] and [[#3. Scripts changed in session 6]]). The place is the only copy of the game's code.
- [ ] **Commit and push session 6** (JordanSaa): `mp_hands.py`, `Exports/keyframes.json`, `MaximumPain_Animations.blend` and the notes (see [[#Repo changes in session 6 (not committed yet)]]).
- [x] **Push the 2026-11-04 session** (JackT6785): `48ee647`, on `origin/main`.
- [x] **Commit and push sessions 4 (2026-11-07) and 5** (JordanSaa): `35c5e2d`, merged with `48ee647` in `85d5b61` (2026-11-08), on `origin/main`.
- [x] **Fix the merge** (2026-11-09): this note had conflict markers in six places, and the [[Changelog]] had lost its 2026-11-04 entry. Both reconciled. [[Cover System]], [[Animation Hooks]], [[Architecture]] and [[Test Arena]] kept the 2026-11-07 version, which was written from what the 2026-11-04 session had left in the place, so their facts are current; the 2026-11-04 wording is in `48ee647`.
- [x] Push session 3's commits: `3634cce`, `7f86ec1`, `a608dc7` and `695e191` are on `origin/main` (pushed 2026-11-04 12:54 UTC).
- [x] Commit the Blender scripts and `Exports/keyframes.json` (done in `ac50a40`).
- [x] Stop tracking `__pycache__` (`3634cce`).
- [x] Commit session 3's export fix, the `.blend` and the notes (`7f86ec1`, `a608dc7`), then the detailed notes update (2026-11-03).
- [x] **Decided 2026-11-07 (JordanSaa): the game's code stays out of git.** The repo is public, so anyone could copy the game. The place is the only copy: save it after every session.

### 2. Play tests
- [x] Everything on the session 2 list below, done in session 3 (see above), apart from:
- [ ] **Two clients.** It has to be run by hand: on 2026-11-04 the Studio MCP couldn't reach the test windows (only the editing window was connected), so it was left for later.
  - **Start it:** Studio > Test tab > Clients and Servers, 2 players, Start. A server window and two player windows open. Do each thing with Player1 and watch it from Player2's window.
  - **Already checked from the server's side** (session 3): stance and hip height changes, the root's smoothed drop, and the Vault clip's speed chase all replicate.
  - **Studio limit (found in session 4):** each Studio process gives a clip its own temporary id. The server and a client registered ReloadRifle as different ids. So Player2 may not be able to play or identify Player1's clips at all: expect default poses, and no reload markers from Player1. Positions, heights, guns, hits and bullet time can still be checked. The clips between players are really tested once the animations are published (to-do 5), when every client uses the same id.
  - Checks:
    - [ ] **Crouch and stand (C):** the other body drops at once and eases down, with no fall clip and no float.
    - [ ] **Vault (Space at the LowWall, −10, 86):** the clip is paced by the way over, and the legs clear the top as seen from Player2.
    - [ ] **Dive** (V or Left Alt with a direction): the flight, the landing on (not in) the floor, lying, getting up.
    - [ ] **Last Stand** for real: Player2 shoots Player1, who has a painkiller and a loaded gun. Check that the drop is instant, the body lies on the floor, and the wakeup.
    - [ ] **Drop (G) and pickup (F):** the gun lies at the same spot on the floor in both windows, and the other player can pick it up.
    - [ ] **Reloads:** Player2 should see Player1's magazine drop and the bolt move: each client now runs the markers itself (4.13, session 4). In Studio this may fail because of the id limit above, so note what happens.
    - [ ] **High cover:** from Player2's window, Player1's arms and guns stay out of the wall, and the body stands 1.5 to 1.8 off it.
    - [ ] **Hits:** flinches on the other body, the death ragdoll, and the kill cam on the dying player's screen.
    - [ ] **Bullet time between players:** Player1's line of sight slows Player2 (`TimeScale`), with the aim penalty, and a counter-activation clears it.
    - [ ] **Clips:** note what Player2 shows of Player1's clips (see the Studio limit above). Live servers use published ids and don't have this limit.
    - [ ] **Cover (new in session 4):** Player1 in high and low cover, sliding, at an end, blind firing, popping out: does Player2 see the side-on body against the wall, the head along it, the gun round or over the cover? The head's look-at is off while hidden for every character, so Player2's view of Player1 should match Player1's.
- [x] **Add the test harness to the repo** (decided 2026-11-07): `Tools/TestHarness.luau`, the same script as the place's `ServerStorage.Tools.TestHarness`. Its header says how to install it each play session and what it reports; see also [[Test Arena]].

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

### 3. Cover pose (decided: side-on)
- [x] **Decided 2026-11-07 (JordanSaa): side-on for all cover, high and low, like Max Payne 3, with every animation it needs redone.** Done in session 4 (above).
  - The old low pose crouched facing the wall, hunched so far over that the head reached 2.2 to 2.8 ahead of the root. The footage shows Max with his back and shoulder to cover instead (session 4, part 1).
  - Wall ends were the known risk; the idles now sit back from the edge (session 4, part 2), and what still shows past an end is 4.18.
  - [[Cover System]]'s "Not done" line about the decision is gone.
  - This replaced JackT6785's decision of 2026-11-04 to keep the hunched pose facing the wall, which the 2026-11-07 session hadn't seen (the two ran in parallel). That decision's comparison table is in `48ee647`.

### 4. Polish
None of these blocks anything. Numbers are from sessions 2 to 5 on the avatars named in each session. Where the two parallel sessions both wrote an item, the one that measured it last is kept.
- [x] **4.1 Standing up from a crouch dipped about 0.3 for ~0.1 s.** Done in session 3 as the foot guard in AimLayer: the body lifts while a height change eases out, and the feet stay within 0.05.
- [x] **4.2 Arm transitions in cover.** Done in session 4 (see its section 3, "Arms and guns kept out of walls"):
  - The arm guard in `AimLayer`; no aim clip while hidden.
  - High cover keeps room for the shoulders.
  - Popping up and ducking back ≤ 0.05; high cover clear at rest and stepping out.
  - Left: a 0.1 s brush stepping back round the east end (M9 0.20, forearm 0.13), and up to 0.43 of the upper arm for about 0.2 s while the edge idle blends in (4.24).
  - Popping up from the side-on pose (2026-11-07), the gun now waits 0.15 s for the turn (4.14, session 5).
- [x] **4.3 Dive landing.** Done in session 4: the landing puts the root on the floor and eases the body, instead of a 2.4-stud fall and bounce. Hands and forearms ≥ −0.02; the camera step is 0.35 (was 1.38).
- [x] **4.4 Vault margin.** Done in session 4:
  - In slow motion the far edge was cleared by nothing (−0.05), so `LEG_CLEARANCE` is now 0.3.
  - The vault now follows its path exactly at any frame rate, and the clip keeps pace from the first frame.
  - From 2.5 back: +0.19 crossing with no contact; out of low cover: +0.26.
- [ ] **4.5 Vault take-off and style.** The take-off part is mostly done (session 4). Still open:
  - From very close the shin still touches the near face: 0.02 from 2.09 back, 0.13 for 3 frames from 1.86 in slow motion. Starting the clip a little way in (its first 10%), or tucking the leading leg sooner in the clip, would cover it.
  - At the higher arc the left hand no longer touches the top from standing (it still rests on it from low cover).
  - A vault from a run starts on a running stride; a standing vault could start from idle.
  - The take-off camera step at 15 fps is 1.2 to 1.7 (about 0.4 at 60), because the path's climb is steepest at its start. A gentler start to the climb, or more camera lag at take-off, would soften it.
  - **Measured again in session 6** (83tg's avatar, the LowWall, about 60 fps, the M9 with the left hand free):
    - From 2.4 and 2.1 back: no leg in the wall.
    - The left hand: in the clip it reaches the near face early (9 to 18% of the clip, 0.5 to 0.9 below the top, on the game's path replayed in Blender), and the arm guard holds it off: 0.07 to 0.11 above the top in game. A clip can't fit every obstacle and start, so planting it properly would be procedural: `AimLayer` placing a free left hand on the top under the body while it passes over (`VaultController` knows the top and where the faces are).
    - The camera's vertical lag works: it held back up to 0.77 of the rise and eased in, and the take-off step was 0.39. A 62 ms frame on the session's first vault made the view jump +1.25, −0.71, +0.81 over three frames.
    - A sprint vault pressed late (1.4 from the face) touched the face with the sprinting stride for one frame before the take-off (the holstered Uzi 0.19, the shin 0.05).
- [ ] **4.6 `CarryTwoHandedLow` points the rifle out to the left.** That was so it cleared low walls. Low cover has its own carry now (`CarryTwoHandedCoverLow`, session 4), so `CarryTwoHandedLow` only plays crouching in the open and getting up, and could point forward-down, more like Max Payne 3.
- [ ] **4.7 The carried gun against walls.** Done in part (session 4): the arm guard keeps the carried gun and its arm out of walls whenever the shoulder has room. Examples: behind high cover the AK's upper arm went from 0.32 in to clear.
  - **Still open:** walking flush along a wall in the open (the root about 1.4 from it) or into an inside corner, the shoulder is closer to the wall than the upper arm's half-thickness. No turn at the shoulder can clear that, and the left arm and the AK clip by 0.5 to 0.9; walking into a corner also presses the legs, head and torso in.
  - **Idea:** keep the shoulders off walls in the movement itself (a small push away from walls on the arm's side), or a side-carry clip that tucks the arm in.
  - **Check:** walk west along CornerWallA's face with the wall on the left, then into the CornerWallA/B corner (`mp.inside` on both walls).
- [ ] **4.8 Sniper and shotgun carries** rely on the floor guard and now the arm guard: they're too long for any fixed pose. Not tried with the M107 yet: pick it up and carry it into cover, along walls and through a dive.
- [ ] **4.9 Blind fire over tall low cover.**
  - From the crouch, an R15 arm reaches the top of a wall about 3.7 tall. Over anything taller the gun stays below the top and the shots hit the wall.
  - Session 4's twisted blind fire puts the gun 0.39 over a 3.6 top on the default R15 (0.11 on 83tg's slimmer avatar), so it may now clear the 3.8 crates on some avatars: measure on CrateA.
  - **Idea:** stand up partly, by the wall's height, for taller low cover.
- [ ] **4.10 Wake-up hands.**
  - The carry clip overrides the left hand that the wake-up clip plants on the floor.
  - Also seen in session 3: the right hand's pistol box touches the floor (0.2) while that hand pushes up, and a holstered gun grazes the floor (0.08) while kneeling.
- [ ] **4.11 Wake-up forearm:** its box dips into the floor lying on the side (from session 2).
- [ ] **4.12 Leg IK.** The foot guard lifts the whole body. A full leg IK (each foot on its own floor, bending the knee) would help slopes and stairs.
- [x] **4.13 Reload markers on other players' screens.** Done in session 4 (`AnimationController.watchReloads`):
  - Each client runs the markers itself on everyone else's reload tracks.
  - A reload that stops puts the gun back at rest, which also fixed the magazine staying hidden after a reload cut short.
  - Tested on one client. Confirm with two players once the animations are published: Studio's temporary ids differ between processes, see [[#2. Play tests]].
- [x] **4.14 Popping up and ducking back in low cover turn the body round in a blend** (session 4). Done in session 5: `CoverPopUpLeft/Right` and `CoverDuckLeft/Right`, played on the stance changes; the gun waits 0.15 s for the turn. In game nothing of the legs goes in the wall, a shin 0.08 under the floor for a frame at most (session 5).
  - **Seen (session 4):** the low idle faces out from the wall and the aim faces over it, so the 0.2 s body blend turned the body about 166°.
    - The feet swept round with the hips: a foot went up to 0.43 and a shin 0.55 into the wall's base, for 8 to 12 frames.
    - On the first frame the aim clip's arm pointed through the top, 1.2 deep, while the body was still low.
    - The same in reverse when ducking back (a shin 0.48 in on the last frame).
  - **Left over:** ducking back working right, the holstered gun is 0.14 in the wall for 2 frames while the clip blends in over the aim.
- [ ] **4.15 Vaulting out of low cover: one frame of a foot in the wall** (session 4). The body turns from facing out to the vault in the vault's 0.1 s blend, and on the frame the hips rise, a foot is 0.74 inside the wall. The same turn clip idea, or start the vault's blend from a pose facing the wall. Session 6: the right foot 0.64 and the legs up to 0.35 for 1 to 2 frames, the carried AK 0.20 for one frame after physics; the camera step 0.95 at 60 fps.
- [ ] **4.16 The inside-corner snap** (session 4).
  - At an inside corner `CoverController` turns the root to the new wall in one frame, and the body turns with it about the root.
  - The low run's body sits up to 1.8 behind the root (to keep the head from leading past wall ends), so it swings round. Sliding along CrateA's north face into the crate next to it, the hips and legs went up to 1.1 into CrateA for about 3 frames.
  - The old wall-facing run sat about 2.8 off the root, so this isn't new, but it's more visible now.
  - **Ideas:** ease the root's turn over 0.2 s at inside corners, or hold the body's yaw and ease it out in `AimLayer` (like the height hold).
- [ ] **4.17 Blind fire working right reaches only just past the corner** (session 4). With the back to the wall the gun arm is the one away from the edge; the chest leans out and the arm reaches across, and the gun ends 0.33 past the end, at the corner (working left it's 1.07 past). A full-body clip that turns the body to the corner would reach further, but its legs would freeze if the player slid while firing.
- [ ] **4.18 What still shows past a wall's end** (session 4). Settled at an end, the edge-side upper arm shows 0.29 to 0.33 past it, the legs 0.15, a holstered gun on the thigh up to 0.47. The head is 0.4 inside. Sitting the idles further back stops the right-edge blind fire reaching; a wider `CoverRules.EDGE_MARGIN` (1.4, with `PEEK_STEP` 3.2) would hide it but moves where peeking and blind fire work.
- [x] **4.19 Firing while sliding along low cover.** Done in session 6 (JordanSaa, 2026-11-09: keep the slide, new clips): `BlindFireLowMoveLeft/Right`, made on the run that goes that way and picked with it; the run going right dips into the cover hold instead of cross-fading with another blind fire clip. In game, both ways and through every switch: the gun over the top and pointing across, nothing in the wall, the head under the top, the gap held.
  - **Seen** (blind fire held, sliding along the LowWall at 8 studs/s): nothing goes in the wall, but on the run the gun is 2.7 out from the wall's face and 2.5 to the side, pointing back along the wall, 0.7 to 0.8 over the top's height. Settled, it's over the top (0.42) with the muzzle over the wall. The shots themselves leave from the server's virtual muzzle, so only the look is wrong.
  - **Why:** `BlindFireLowLeft/Right` key the waist for the idle's hips, which face out from the wall. The run's hips face along it, so the same twist turns the chest a quarter turn the wrong way. Firing doesn't stop a slide (`CoverController` only reads the last shot to hold the reach).
  - **Decided:** keep the slide and make blind fire clips on the run (the other option was to stop the slide while blind firing).
- [ ] **4.20 The crouch walk and the low cover run fold the trailing leg into the floor** (session 5).
  - **Seen:** in the second half of each step the planted foot goes back 1.25 behind the low hips, and the knee comes down to 0.19 over the floor, almost kneeling, until the foot has swung forward under the body. On the default R15's boxes the shin goes 0.44 to 0.47 under the floor, the thigh 0.24 to 0.26 and a gun holstered on the thigh 0.28 to 0.37. In game on 83tg's avatar, sliding along the LowWall: shins, thighs and the Uzi 0.33 under. The feet stay on the floor. The crouch walk's numbers are unchanged since they were committed on 2026-11-01; it wasn't caught because the checks looked at the feet.
  - **Tried in Blender** (`mp_locomotion.CROUCH_WALK`; the low run is made from it): raising the heel at push-off (18° to 45°) changed nothing; turning the knees out, 0.35 at best and worse sideways; shorter, quicker steps (cycle 0.55 to 0.4) with the feet further forward, 0.35 (0.23 at the shortest); the hips 0.2 to 0.3 higher with short steps, 0.16 to 0.3, but the head comes up 0.2 to 0.33.
  - **Ideas:** hips higher with the waist folding more, so the head stays where it is (the low run's head top must stay under about 3); shorter steps; and a leg check like the turn clips', which lifts a knee that would go under the floor. Or accept it on slim and mesh avatars, whose legs are thinner than the default's boxes (0.33 in game against 0.44 on the boxes).
  - **Check:** the shins, thighs and holstered gun over the floor through the crouch walk in all four directions and the low run both ways, in Blender and with `mp.floor()` in game.
- [ ] **4.21 Standing up: the feet go 0.10 into the floor for one physics step** (the first after the root rises). It isn't drawn at 15 fps but would be at 60. The foot guard measures the posed feet before physics, and the first step still moves them. (2026-11-04)
- [ ] **4.22 The dive's landing ease (optional).** The body now settles onto the floor quickly and smoothly. A fall-shaped ease (carrying on the flight's downward speed, ending on the floor) would land harder, more like Max Payne 3, if this reads as soft. (2026-11-04)
- [x] **4.23 The carried AK brushes the top in a vault** for 7 to 9 physics frames in mid-vault (0.28 to 0.34). (2026-11-04) Done in session 6: the arm guard cleared the arm for where the body stood before the physics step, not where it would be drawn; it now tests the place the body will be (session 6, part 5). The AK rests on the top edge (0.05) standing, running and sprinting.
- [x] **4.24 High cover, stepping back to the edge:** while the edge idle blends back in (about 0.2 s), the leading upper arm reaches up to 0.43 into the wall before the gap and the guard settle it to 0.05. (2026-11-04) Re-measured in session 6 with the side-on pose: no upper arm in the wall at either end; the gun forearm 0.09 for 9 frames stepping out, the M9 0.05 stepping back (session 6, part 7).
- [x] **4.25 Blind fire while sliding along high cover** (session 6). 4.19's fault on high cover: on `CoverHighMove` the still `BlindFireHigh` clip twists the chest for the idle's body and turns the gun back along the wall (barrel 0.9 along it, away from the way the body runs). Mid-wall the shots hit the wall anyway (blind fire works round an end), so it's the look. Fix as 4.19: clips made on the high run (check the switches with Roblox's blending), or keep the cover hold while sliding mid-wall. Done in session 6 (part 8, 2026-11-10): `BlindFireHighMoveLeft/Right`, made on the high run, the gun arm straight out ahead along the wall; the two runs dip into the hold on a reversal.
- [ ] **4.26 Rifles in high cover blind fire** (session 6). With a rifle (the FAL) the high blind fire clips put it 1.9 into the HighWall, still and sliding, and the support hand up to 0.49 in: the clips were made with a pistol and point the gun along the wall. A rifle needs its own pose (round the end, the support hand on it), or the hold while hidden mid-wall.
- [x] **4.27 Bullet time: slow the player who triggers it too?** (a decision, session 6). They keep full speed, as [[Last Stand and Bullet Time]] says (checked in session 6, part 9). In Max Payne 3 the user is slowed too, less than their victims, and the slow-down chains through the victims' sight ([[Max Payne 3 Mechanics Reference]]). Following it means a scale between 0.3 and 1 for the activator in `BulletTimeService` (and sight checks from the victims for the chain). **Decided by JordanSaa and done on 2026-11-10** (session 6, part 9): the activator slows to 0.6 (`ACTIVATOR_SCALE`), except in a Last Stand. The chain isn't done.
- Accepted as it is: the gun-arm pump lags the opposite leg by about 0.1 of a cycle.

### 5. Publish and document
- [x] `mp_lib.export(fbx=True)` for FBX copies; `MaximumPain_Animations.blend` saved in `Assets/Blender/Animation` (session 3).
- [ ] **Publish the animations.**
  - **Who:** JordanSaa, the account that owns "Untitled Experience". An experience only plays animations its own creator owns, so animations published from a collaborator's account won't load in live servers.
  - **Until then:** live servers play none of the clips. `AnimationConfig.resolve` only plays a KeyframeSequence directly in Studio, so `AnimationController` keeps Roblox's default `Animate` script, and the gun parts don't move on reloads.
  - **Steps:**
    1. Open the place in Studio as JordanSaa.
    2. Publish each of the 102 KeyframeSequences in `ReplicatedStorage.Assets.Animations` as an animation owned by JordanSaa (or the group, if the game moves to one).
    3. Paste each `rbxassetid://<id>` into the matching slot's `Id` in `AnimationConfig`. There are 109 slots for 102 clips: `ReloadPistol` serves 4 slots (Desert Eagle, M9, Glock 18, Uzi) and `ReloadRifle` 5 (AK-47, FAL, M4, MP5, SPAS-15), so those slots share an id.
    4. Publish the place and test in a live server: locomotion, cover, dives, vaults, Last Stand, every reload and its markers.
    5. When a clip changes later in Blender, re-export and re-import it, publish it again, and update its slot's `Id`.
  - Scripted publishing isn't an option for now: `AssetService:CreateAssetAsync` returned "not available yet", even from a plugin, when it was tried for the weapon kit (2026-10-30).
- [ ] After publishing: compare each clip with [[Max Payne 3 Animation Reference]] again (from [[Animation Hooks]]).
- [ ] Check the kill cam's death panel against Max Payne 3 multiplayer footage, with timestamps (from [[Max Payne 3 Kill Cam]]'s "Not done").
- [x] Removed the cover-to-cover wording ([[Changelog]], [[Cover System]]) and the out-of-date "no animations" and "no vaulting" lines.
- [x] Updated [[Architecture]], [[Animation Hooks]], [[Cover System]], [[Shoot-Dodge]], [[Last Stand and Bullet Time]], [[Movement State Machine]], [[Test Arena]].
- [x] New research notes: [[Euphoria-style Reactions and Ragdolls]] and [[Max Payne 3 Kill Cam]].
- [x] This note and the [[Changelog]] rewritten in detail (2026-11-03).
- [x] Session 4: this note, the [[Changelog]], [[Cover System]], [[Animation Hooks]], [[Architecture]], [[Test Arena]], [[Max Payne 3 Animation Reference]] and the README updated for side-on cover and what was found in the place (2026-11-07).

---

## How to resume (tools and tricks)
- **Blender:** `sys.path.insert(0, r"…\Assets\Blender\Animation")`, `import mp_lib as L, mp_locomotion as M, mp_arms as A, mp_stances as S, mp_hands as H`, `L.build_rig()`, `L.CLIPS.clear()`, then `M.register(); A.register(); S.register(); H.register()` (102 clips). `L.export()` (or `L.export(["Name"])`), `import mp_serve; mp_serve.start()`. In Studio **Edit mode**: `require(game.ServerStorage.Tools.AnimationImporter:Clone())()`.
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
  - **The test harness:** session 3's 220-line version was rewritten in the place (733 lines, `ServerStorage.Tools.TestHarness`) and is in the repo as `Tools/TestHarness.luau` since session 4. Its header has the install lines and every helper. In short:
    - **Install** each play session: on the Server, clone it into ReplicatedStorage; on the Client, `_G.mp = require(game.ReplicatedStorage:WaitForChild("TestHarness"))`.
    - **Recording:** `mp.start("render")` logs every frame at the end of the render step (or on `PostSimulation`, or both): each part's frame, the guns, velocity, hip height, camera, stance, humanoid state, `TimeScale`, and every playing clip by name (weight, time, speed). `mp.stop()` ends it.
    - **Reports:** `mp.floor()`, `mp.inside(part)` (exact box-against-box depth), `mp.over(part)` (clearance over a top), `mp.camera(limit)`, `mp.timeline()`, `mp.clip(name)`. The building blocks are public too: `mp.boxes(frame)`, `mp.penetration(a, b)`, `mp.boxOf(part)`.
    - **Driving:** `mp.walk(points)`, `mp.halt()`, `mp.look(yaw, pitch)`, `mp.view(eye, at, rootSpace)` / `mp.unview()` for screenshots, `mp.status()`.
  - **Reload checks:** pick each gun up from the rack with F, fire a couple of shots, reload, then compare each moving part's `C0` with its `RestC0`. Count the spent magazines in Workspace (a pistol reload with a rifle carried should drop one).
- **Learned in session 4:**
  - **When Claude Code's Studio link is down** (Studio updated itself and the server shows "Connection closed"), Studio's own MCP program still works. Run `%LOCALAPPDATA%\Roblox\Versions\<version>\StudioMCP.exe` over stdio, as `mcp.bat` does:
    - Send `initialize` and `notifications/initialized`, wait about 4 s for its proxy to find Studio, then `tools/call`.
    - `list_roblox_studios` gives the `studio_id` every call needs. Asking at once answers "No Roblox Studio instances are connected".
    - Or run `/mcp` in Claude Code to reconnect.
  - **Importing clips from the MCP:** `execute_luau` can't reach `127.0.0.1` (the Assistant's HTTP allowlist), so `AnimationImporter` can't fetch from `mp_serve`. Instead, embed the clips' JSON in the Luau code with the importer's `build` function, in batches of about 60 KB. Run it in **Edit** mode (play-mode changes are thrown away), then compare a fingerprint of every KeyframeSequence (pose count and a weighted sum of the CFrames) with `keyframes.json`.
  - **Keyboard and mouse tools:** `user_keyboard_input` needs `datamodel_type: "Client"` and `wait_time_ms` for waits. `user_mouse_input` needs a `moveTo` in each call before clicks, or the clicks don't register. Right button held = aim, left click = fire.
  - **Holding blind fire for a screenshot:** set the character's `LastShot` attribute on the client to `os.clock() + 25`. `AnimationController` keeps the blind fire up for 1.2 s after it; it isn't replicated.
  - **Blender** on this PC is `D:\blender.exe` (5.2.3). All 102 clips export in under a minute with the FBX copies.
  - **Walking to the arena:** a block (`Workspace.Part`, x 30–34, z 38–56) stands north of the spawn. Go round it by (38, 38) and (38, 77), then west along z 78 or 80.
  - **Cover checks in Blender:** measure each pose against a wall placed where the game keeps it. Use the gap from the head, torso and upper arms' reach + 0.05, at least 1.15, then check the head top over the floor, boxes in the wall or floor, the reach toward the edge, and the gun over the top or past the end. Put a face marker on the head in contact sheets to see where it looks.
  - **Folded bodies:** a neck yaw on a chest folded over the knees rolls the head instead of turning it; aim it with a look-at (`mp_stances.look`). Place guns in a part's frame but aim them in the body's facing frame (`mp_arms.placed`, `by_part`).
- **Learned in session 5:**
  - **Clips that play through a height change** must plant their feet where `AimLayer`'s hold leaves the floor: `hold = drop × e^(-10 t)`, in real time from the hip change. Play them in real time too, and their ends will differ from the poses they join by what the hold still has to do.
  - **Check legs as boxes, not just feet:** the default R15's legs are a stud thick. A shin leant more than about 25° over a flat foot puts its box corner under the floor, and a knee folded forward over the toes near a wall reaches it before the foot does. A gun holstered on the left thigh hangs past the knee.
  - **Knees in IK:** a fixed knee direction bends them backward once the feet have turned round. Turn the knee with the foot, from the start pose's bend to the end pose's.
  - **Working the left side without sliding:** press Q before E; the cover side starts on the camera's shoulder.
  - **Re-importing a few clips:** build the import batch from `keyframes.json` with just those clips (about 33 KB for four), run it in Edit mode, and check their fingerprints; the rest of the place's clips stay as they are.
- **Learned in session 6:**
  - **How Roblox blends tracks** (measured on a cloned rig, 2026-11-09): tracks of the same priority blend joint by joint, weight-normalised, by normalised linear interpolation, the short way round; a higher priority overrides the lower ones by its total weight (at most 1). A Blender check of a blend must do the same, at several clip times and weight mixes: near a half turn the way round depends on small differences.
  - **Clips that blend into each other:** keep every joint well short of a half turn from its partner's (under about 135°). Where the body turns a long way under a held pose (blind fire going right), don't cross-fade: drop the old clip into a pose both sides blend with, then bring the new one up.
  - **Searching for a pose:** a scored random search over a handful of numbers (waist angles, where the head looks, the grip, the elbow's way, the gun's cant), scoring each candidate on the body's whole cycle and on its blends, found poses that hand-tuning didn't. Round the result and check it again on the shipped code.
  - **Head height:** use the head box's highest corner, not its top face's centre; tilted forward, the corner is up to half a stud higher.
  - **Firing in a test:** `Remotes.FireWeapon:FireServer(point, "Right")` in a loop runs the whole chain (the server's shot, `WeaponFired`, the client's blind fire). `LastShot = os.clock() + 60` holds blind fire without spending ammo.
  - **A rifle in the right hand:** dual wield (4) drops the carried AK, so pick a rifle up from the gun table (F; the prompt nearest the crosshair) and press 3.
  - **Import batches** use a `[==[ … ]==]` string: the clips' JSON holds `]]`.
  - **The procedural layer runs before physics** (`PreSimulation`). Anything it checks against the world must use where the body will be when the frame is drawn: the root's velocity × the larger of the physics and render steps (a mover such as the vault's places the root by the render step).
  - **The server's copy of a character the client moves lags it** by about 0.25 s in Studio (0.26 s into a run it hadn't started moving). Server checks of a place must reach that much further, or check from the client's place within limits.
  - **Testing vaults on the run:** go round the dummy behind the LowWall (x −10, z 92) and the pillar (x 0, z 100): through the gap at x 1. Hold W from 7 studs out and press Space 0.26 s in (16 studs/s, the vault starts about 3 out); for a sprint, hold LeftShift too and press at 0.42 s from 11 out. Log `Remotes.StanceResult` on the client to see the server's answer.
- **No weak-keyed tables keyed by instances** (`__mode = "k"`) for anything that must survive: entries vanish while the instance still exists. Keep the state on the instance (attributes) or in a plain table cleared when the instance leaves.
- **Learned in session 4:**
  - **The test harness** is `ServerStorage.Tools.TestHarness` in the place and `Tools/TestHarness.luau` in the repo (the same script; it never reaches players). Install it each play session:
    - Server: `game.ServerStorage.Tools.TestHarness:Clone().Parent = game.ReplicatedStorage`
    - Client: `_G.mp = require(game.ReplicatedStorage:WaitForChild("TestHarness"))`
  - **Using it:**
    - **Recording:** `mp.start("both")` … `mp.stop()` records every frame at the end of the render step (what is drawn) and after physics. The command bar's VM can't see the game's module state, so it reads instances and attributes; `Stance` is the server's.
    - **Reports** take `{ phase, from, to, parts, guns }`:
      - `mp.floor()`: lowest point of each box over the floor.
      - `mp.inside(part)`: depth into a wall, and how far it would have to rise.
      - `mp.over(part)`: clearance over a top.
      - `mp.camera(limit)`, `mp.timeline()`, `mp.clip(name)`.
      - `mp.penetration`, `mp.drop` and `mp.boxes` for your own checks.
    - **Driving:** `mp.look(yaw, pitch)` (yaw π faces +Z), `mp.yawTo(point)`, `mp.walk(points)`, `mp.walking()`, `mp.halt()`, `mp.status()`, and `mp.view(eye, at, rootSpace)` / `mp.unview()` for a debug camera.
  - **Frame rate:** Studio in the background draws about 15 frames a second while physics runs at 60. Render-step code runs in 66 ms steps, so timing faults show up larger; every fix should hold at that rate.
  - **Keys:**
    - Aim can be held with the keyboard tool's `ButtonL2` (keyDown and keyUp).
    - Facing a wall at +Z, D slides toward −X (the character's right).
    - Pressing R with a full magazine does nothing (the server refuses), so fire first. `Remotes.FireWeapon:FireServer(point, "Right")` works.
  - **Halt the walker before using keys:** a walk that times out stays bound and keeps walking. After a vault it walked the character back into the wall.
  - **Bullet time for tests:** re-arm `DebugBulletTime` every 0.25 s from a server loop. An activation lasted under 4 s, and a 4 s re-arm left gaps.
  - **A Last Stand you survive:** connect a client listener on the character's `Stance` attribute that fires at the gunman as soon as it becomes LastStand. Tool calls are too slow for the 4 s window.
  - **Studio clip ids differ between processes:** `KeyframeSequenceProvider` gives the same clip different temporary ids on the server and a client. A track played on one side can't be named or played on the other.
  - **The Studio MCP can't reach Clients and Servers test windows;** only the editing window stays connected.
  - **Screenshots in play mode came out blank** (the HUD drew, the 3D view was white) with Studio in the background. Measure instead, or bring Studio to the front first.
  - **`get_console_output`** does show play-session prints and warnings, so an empty result means a clean log.
  - **A copy of every script on disk:**
    - Run a small receiver on 127.0.0.1.
    - Post each script's `Source` to it from Studio, switching `HttpEnabled` on only for the copy, as the animation importer does.
    - This gives grep and before/after diffs of a session's changes. The copies stay outside the repo.

## Test log (session 4, 2026-11-04, Studio play mode, drawn at about 15 fps)
| Test | Before → after the session 4 fixes |
|---|---|
| Crouch / stand, first drawn frame | feet −1.80 / +1.89 → in place; camera 0.87 / 0.88 → 0.22; humanoid stays Running |
| Dive run-up, first drawn frame | feet −0.60 → −0.03 |
| Dive landing | fell 2.4 at up to 31 studs/s and bounced, camera −1.38 → root on the floor at once, eased; camera 0.35; hands ≥ −0.02 |
| Low cover pop-up / duck-back | gun 0.73 / 0.56 into the wall → ≤ 0.05; camera 0.87 → 0.22; gap 2.52 (unchanged) |
| High cover, aim held mid-wall | gun 0.67 into the wall → stays in the cover hold |
| High cover at rest | east end: right arm 0.55, hand 0.45, M9 0.11; right side: AK's arm 0.32 → nothing in the wall (gap 1.78 / 1.52) |
| High cover step out / back | M9 1.00, forearm 0.85 → clear; back: 0.1 s brush (0.20); no overshoot (was ±0.5 each frame) |
| Walking flush along a wall, into a corner | left arm and AK 0.5 to 0.9 in → unchanged (4.7) |
| Vault, 2.5 / 2.09 back | take-off −0.12…−0.56 → +0.19, no contact / near face 0.02 (was 0.23) |
| Vault out of low cover | +0.26 over the top; no Fall clip; feet 0.00 after |
| Vault in bullet time (0.3) | 1.52 s in the air; far edge −0.05 → `LEG_CLEARANCE` 0.3 |
| Last Stand, survived | drop: feet −0.47 → −0.05, camera 0.12; wakeup and stand ≥ −0.05, camera ≤ 0.14; painkillers 3 → 2 |
| Dive get-up | feet ≥ −0.05; camera 0.15 |
| First reload of a life | stretched from its first frame (was unstretched until the clip loaded) |
| Others' reloads (one client) | a reload this client didn't start moved the gunman's AK magazine and bolt; one cut short brought the magazine back |
| Output log | clean |

## Test log (session 6, 2026-11-09 to 10, Studio play mode, 83tg's avatar)
| Test | Result |
|---|---|
| Low cover, blind fire while sliding, both ways (held, and real shots) | the run's clip plays with its run; the muzzle 0.52 to 0.72 over the top, pointing across (0.95 to 0.99); the head's box 0.32 to 0.45 under the top; nothing in the wall; the gap unchanged |
| Starting to fire mid-slide, both ways | muzzle up, across in 0.12 to 0.25 s; nothing in the wall |
| Starting and stopping a slide while firing, both ways | going left: a cross-fade, the gun across throughout; going right, before the dip: the gun pointed back along the wall for about 0.1 s (−0.66 to −0.95); with the dip: never |
| Five reversals while firing | before `DIP_FADE` 50 (at 30): head 0.64 and carried AK 0.95 in the wall for 4 to 5 frames; at 50: nothing in the wall |
| Dual pistols; a rifle (FAL) | the Uzi rests 0.05 on the wall's face going right; the rifle rests 0.05 on the top |
| High cover, blind fire while sliding (FAL), before 4.25 | the gun turns back along the wall on the run (4.25); the rifle 1.9 into the wall still and sliding, the support hand 0.49 (4.26) |
| Vaults with the AK carried, before the guard fix | standing: AK 0.29 to 0.33 into the top for 7 to 9 frames at take-off |
| … after (2026-11-10) | standing, running (16), sprinting (24): AK 0.05 on the top edge; out of low cover: nothing drawn, 0.20 one frame after physics |
| Running vault, before `SERVER_SLACK` 7.5 | refused (`NoVault`) after 3 frames; the body dropped onto the top, legs 1.58 in |
| … after | running and sprinting vaults accepted and completed |
| Low cover blind fire slides after the guard fix (regression) | nothing in the wall, 216 frames, both ways and a reversal |
| High cover, stepping out and back at both ends (4.24) | no upper arm in the wall; forearm 0.09 (9 frames), everything else ≤ 0.08 |
| High cover, blind fire while sliding, after 4.25 (2026-11-10): M9, AK-47, dual M9 and Uzi | nothing in the wall; the barrel 0.99 to 1.00 ahead along the wall; the new clips' arm and gun ≤ 0.02 into the head's box (0.09 mid-blend) |
| … reversals, starting, stopping | the velocity flips in one physics frame and the old clip dips into the hold; starts and stops cross-fade; nothing in the wall |
| Bullet time, the player's own (full meter) | 5 s, the meter drained; the dummy at 0.3; the player at full speed (the rule) |
| … after `ACTIVATOR_SCALE` 0.6, triggered mid-sprint | the player at 0.6: sprinting 14.4, walking 9.6, back to 1 after 5 s; no movement-check strike |
| … a Last Stand during it | 0.6 until the killing blow, then 1 through the stand; the gunman at 0.3 |
| Bullet time, a dummy's on the player; a counter-activation | the player at 0.3, walking 4.8, aim 0.35; the counter-activation cleared the penalty; both back to 1 behind the pillar |
| Output log | clean |

## Test log (session 5, 2026-11-08, Studio play mode, 83tg's avatar)
| Test | Result |
|---|---|
| Low cover, pop up and duck back, working right and left | the turn clips play; no leg in the wall; a shin 0.08 under the floor for one frame at most (0.22 with the clips' first version); feet within 0.05 |
| Popping up, the gun | working left: 0.59 into the wall's face with `POP_AIM` 0.1 → 0.05 with 0.15; aiming over the top, the forearm rests on it (0.05) |
| Ducking back working right | the holstered Uzi 0.14 in the wall for 2 frames; the right upper arm 0.08 on the top edge |
| Low cover, sliding (start, stop) | feet 0.36 under the floor → within 0.05 (the foot guard in cover); shins, thighs and the Uzi 0.33 under (4.20) |
| Low cover, blind fire while sliding (4.19) | nothing in the wall, but the gun 2.7 out from the face pointing back along the wall; over the top only once settled |
| Camera | largest step 0.08 |
| Output log | clean |

## Test log (session 4, 2026-11-07, Studio play mode, 83tg's avatar)
| Test | Result |
|---|---|
| Low cover, settled | head top 2.77 (0.83 under the 3.6 wall; 3.49 on 2026-10-31); root 1.21 off the wall; nothing in the wall or floor |
| Low cover, slides to both ends | the root stops 0.80 from each end; settled: head 0.47 inside, upper arm 0.33 past; the run blending out: head 0.21 past |
| Low cover, pop up and duck back | the right stances and clips; aiming, the forearm rests on the top (0.05); see 4.14 for the turn |
| Low cover, blind fire | head 0.34 under the top, gun 0.11 over it, nothing in the wall, gap held (1.21) |
| High cover, ends | root 0.73 to 0.82 from the end; settled: head 0.39 inside, arm 0.29 past |
| High cover, blind fire | working left: gun 1.07 past the end; working right: 0.33 past, at the corner |
| High cover, pop out and back | pops out round the end and steps back; ducking back, the gun 0.22 into the wall for 3 frames |
| CrateA, outer corners | nothing in the crate during the swings; the inside-corner snap into the next crate is 4.16 |
| Vault out of low cover | clears; one frame of a foot in the wall (4.15) |
| Camera | largest step 0.08 |
| Output log | clean |

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
