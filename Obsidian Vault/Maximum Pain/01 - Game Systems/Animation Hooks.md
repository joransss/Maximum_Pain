# Animation Hooks

How the game's animations are made, named, played and published. The slots were built empty on 2026-10-31; since 2026-11-01 every slot plays a clip made in Blender (93 clips).
Related: [[Animation and MP3 Systems - Progress and To Do]] · [[Animation References]] · [[Max Payne 3 Animation Reference]] · [[Movement State Machine]] · [[Loadout and Dual Wielding]]

## From Blender to the game
1. **Authoring:** the clips are Python in `Assets/Blender/Animation`. `mp_lib` holds the R15 rig, IK and the tools; `mp_locomotion`, `mp_arms`, `mp_stances` and `mp_hands` register the clips. Everything is authored in Roblox space (studs, Y up, facing −Z), so a joint rotation is exactly the Transform Roblox applies and nothing needs converting.
2. **Export:** `mp_lib.export()` writes `Exports/keyframes.json`, every clip with only the keys it needs. Two exports of the same clips are byte-identical. `export(fbx=True)` also writes one FBX per clip to `Exports/FBX` for Studio's Animation Editor; that folder isn't kept in git. `MaximumPain_Animations.blend` holds the rig and every clip as an action.
3. **Import:** `mp_serve.start()` serves the file at `http://127.0.0.1:8765`. Then, in Studio edit mode, `require(game.ServerStorage.Tools.AnimationImporter:Clone())()` builds a KeyframeSequence per clip in `ReplicatedStorage.Assets.Animations`. HTTP is switched on only for the fetch.
4. **Playing:** in Studio, a slot with no `Id` plays its KeyframeSequence directly, so nothing has to be published to test.
5. **Publishing:** live servers need each KeyframeSequence published and `rbxassetid://<id>` pasted into its slot's `Id` in `AnimationConfig`. An experience only plays animations its own creator owns, so **the place's owner has to publish them**.

Headless rebuild, Blender 5.2: `blender --background --factory-startup --python <script>`. The steps are in the to-do note's "How to resume".

## Layers (`AnimationController`)
| Layer | Priority | Plays | Blend rate (per second) |
|---|---|---|---|
| body | Movement | Locomotion: idle, jog, run, sprint, crouch walk, limp and hobble, in four directions, all on one shared phase and played at real speed ÷ the clip's authored speed so the feet don't slide. Air: jump, fall, land, landing roll. One clip per stance: cover, the dive, the vault, getting up, Last Stand. | 10 (the vault takes over at 30) |
| hold | Action | The arms' pose for the guns in hand, the carried two-handed gun, injured arms | 12 |
| aim | Action2 | The gun raised (aiming, just fired, diving, on the floor, popped out, Last Stand), or blind fire | 18 up, 7 down |
| action | Action3 | Reloads and draws stretched to the server's `ActionEnds`, pickups, painkillers, drops | 12 |

On top of the clips, every frame, the procedural layers bend the joints (`ProceduralLayer`):
- **AimLayer:** puts the gun exactly where the player aims, plus the chest blade, head look, recoil springs, momentum lean, a run arm pump, and the left hand on the gun's Support point. It also keeps a carried gun out of the floor and eases the body through height changes without the feet going through the floor.
- **HitReactions:** flinches.

## Rules
- **Timers stay in charge.** The server's timers decide when a reload, draw, dive or get-up ends; the clips are stretched to fit. The server never waits for a marker.
- **One-off clips hold their last frame** while they fade (Play() would restart them from frame 0). Wanted again while fading, as on a second corner, they restart.
- **Clips bound to a stance** (DodgePrep, GettingUp, LastStandWakeup) hold until the stance ends, then fade with the height change.
- **Markers are cosmetic.** MagOut, MagGrab, MagIn, BoltBack, BoltForward, ShellIn, Pump, CylinderOut, CylinderIn, BreakOpen and BreakClose move the parts of the gun being reloaded through its own Motor6Ds: the right-hand gun, or both pistols for ReloadDual. A gun part's resting pose is kept on its motor (`RestC0`).
- **Bullet time:** locomotion follows the slowed velocity, and everything else plays at the character's `TimeScale`. The blends run in real time.
- **Animator only**, never the old `Humanoid:LoadAnimation`. Roblox's `Animate` script is switched off for the character once the clips can play.
- **Arm clips are chest-relative.** Author them with IK on the body they'll play on, then check them by FK on every body that plays them (rifle box against the floor, the wall and the body).

## Slots (`ReplicatedStorage.Modules.AnimationConfig`)
| Group | Slots |
|---|---|
| Locomotion | Idle, Jog/Run/CrouchWalk + Forward/Back/Left/Right, Sprint, CrouchIdle, LimpLeft/Right, Hobble |
| Air | Jump, Fall, Land, LandRoll |
| Cover | CoverHigh/Low + Left/Right, CoverHigh/LowMove + Left/Right, CoverCornerHigh/Low + Left/Right, CoverAim |
| Shoot-dodge | DodgePrep, DodgeAir and DodgeLand + Forward/Back/Left/Right, DodgeGround, GettingUp |
| Vault | Vault (a speed vault, paced by the way over) |
| Last Stand | LastStandFall, LastStand, LastStandWakeup |
| Holds | Hold + Pistol/Revolver/SMG/SawnOff/Rifle/Shotgun/Sniper/Dual (the gun's `AnimSet`), CarryTwoHanded, CarryTwoHandedLow, CarryTwoHandedCover, CoverHoldHighOne/Two/Dual, CoverHoldLowOne/Dual, CoverHoldLowTwoLeft/Right, InjuredArmLeft/Right |
| Aim and blind fire | AimPistol, AimRifle, AimDual, BlindFireHigh/Low + Left/Right |
| Actions | DrawOneHanded, DrawTwoHanded, DrawDual, Pickup, Painkiller, DropGun |
| Reloads | Reload_<gun> for all 13 guns, sharing ReloadPistol, ReloadRevolver, ReloadRifle, ReloadSniper, ReloadPump and ReloadSawnOff; ReloadDual |

## How clips are chosen
- **Carried two-handed gun:**
  - CarryTwoHanded standing.
  - CarryTwoHandedLow crouching, in low cover and getting up (held at the left side, pointing out left-forward, so it clears low walls).
  - CarryTwoHandedCover behind high cover (nearly vertical beside the left leg).
  - If the gun would still go into the floor (dives, rolls, the longest guns), AimLayer swings the arm up at the shoulder just enough.
- **Dive clips:** picked by comparing the dive's direction with where the body faces, so a sideways dive with the gun forward plays the sideways clips.
- **The vault:** the clip's playback chases the way over the obstacle. The legs are tucked (25% of the clip) when the leading knee reaches the near face (1.3 studs ahead of the root), and stay up (72%) until the trailing foot passes the far face (0.9 behind). The playback speed (at most 6) replicates to other players.
- **Cover:** the idle follows the side being worked, the move clips run at the speed along the wall, and the corner clips play while swinging round.
- **Blind fire:** high cover uses the right arm only (the left keeps the carried rifle). Low cover uses the right arm and the waist, one clip per side.

## Not done
- Publishing for live servers (the place's owner). See the to-do note.
- Compare each clip with [[Max Payne 3 Animation Reference]] again after publishing.
