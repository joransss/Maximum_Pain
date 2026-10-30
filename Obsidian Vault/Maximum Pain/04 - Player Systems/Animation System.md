# Animation System

## Required Animations
- Idle / locomotion
- Sprint
- Aim / weapon hold
- Fire and reload
- Jump / fall / land
- Shoot-dodge
- Hit reaction
- Death

## Notes
- Use original or properly licensed animations.
- Decide which animations are local presentation and which must replicate.
- Keep animation state aligned with gameplay state.
- Avoid animations that obscure enemy visibility or aim feedback.

## Integration
- [[Player Movement]]
- [[Camera System]]
- [[Gunplay]]
- [[Shoot Dodge]]

## R15 animation suite (2026-10-30)
The game runs on **R15** with one standard body for everyone (see [[Implementation Log]]). 40 clips are authored in Blender and played by a state machine; a small procedural layer keeps the gun on the aim.

**Pipeline** (repo `Assets/Blender/Animation/`, Blender file `Assets/Blender/MP_R15_Animations.blend`)
1. `mp_rig.py` builds an armature that matches the default R15 Motor6D layout exactly (bone names = part names, 1 unit = 1 stud) with box proxies, the 9mm pistol at the real grip, and IK controls for hands and feet.
2. `mp_clips.py` authors every clip in Roblox terms (studs, degrees, HumanoidRootPart space). Locomotion is generated from the game's real speeds so planted feet don't slide; action clips are keyed poses with easing, anticipation and overshoot.
3. `mp_export.py` bakes IK at 30 fps to `export/clips.json` (+ one FBX per clip in `FBX/`, + an NLA track per clip). `mp_serve.py` serves it; `studio_import.luau` builds KeyframeSequences in `ReplicatedStorage.Assets.Animations`.
- Round trip verified: a posed Studio rig matched Blender part positions to 0.001 stud.

**Clips** (authored at these numbers; `Animate` scales playback from them)
| Group | Clips | Built to |
|---|---|---|
| Locomotion (Movement) | `Run_F/B/L/R`, `Walk_F/B/L/R` (aim walk), `CrouchWalk_F/B/L/R`, `Sprint`, `TurnL/R` | run 16, aim walk 9.6, crouch 8, sprint 25.6 studs/s; turn 120°/s |
| Idle | `Idle`, `CrouchIdle` | crouch clips raise the feet by `CrouchDrop` (1.3) because the server lowers the root |
| Weapon (Action/2/3) | `Hip`, `Aim`, `CoverIdle`, `Reload` (1.6 s, phases 0.3/0.6/0.82), `RecoilHip`, `RecoilAim` | gun held straight ahead of the chest |
| Shoot-dodge (Action) | `DiveWindup_F/B/L/R` (0.15 s), `DiveAir_F/B/L/R`, `Land_Front/Back/Side`, `Prone_Front/Back/Side`, `Recover_Front/Back/Side` (0.5 s) | authored in the lying root frame (root +Y = head-first along the dive, -Z = chest toward the aim) |

**Runtime**
- `StarterCharacterScripts.Animate` (replaces Roblox's default): base layer = idle / 4-way strafe blends (weights from movement relative to facing, shared cycle phase) / sprint / turn-in-place / dive → land → prone → recover (prone side from which way the chest faces); upper layer = `Hip` / `Aim` / `CoverIdle` with the weapon out; overlays `Reload` (server-timed) and recoil per shot. Bullet time scales every track.
- `PoseController` (all characters): turns the chest so the clip's barrel line meets the aim point (measured 0.0° aimed, 0.5° hip); straight arms on the aim while diving / prone / Last Stand (1.1°); blind-fire arm in cover; head follows the aim.
- Published IDs go in `Shared.AnimationIds`. Empty = Studio plays the local KeyframeSequence (only you see it); **live servers need the clips published**.

**Not done / limits**
- Clips are unpublished: other players (and live servers) don't see them until published.
- Jump/fall, hit reactions, death, climbing and swimming have no clips.
- Small residual foot slip at run speed in game (median ~1.7 studs/s at 16); full foot locking needs in-engine IK.
- Aiming from the ground uses straight arms: the support hand doesn't reach the grip there.
- Poses come from code-generated keys on box proxies: a first pass to refine by hand in Blender, not final AAA polish.
