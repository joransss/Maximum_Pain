# Animation Hooks

How the game's animations are made, named, played and published. The slots were built empty on 2026-10-31; since 2026-11-01 every slot plays a clip made in Blender (113 clips in 123 slots since 2026-11-12: the cover clips went side-on on 2026-11-07, low cover got its turns on 2026-11-08, blind fire got clips for the low and high runs on 2026-11-09 and 10, two-handed blind fire behind high cover late on 2026-11-10, and on 2026-11-11 and 12 the low cover squat, guns carried by the middle, crouched two-handed holds, one-handed reloads and the switch's handover). Every clip is published (since 2026-11-14).
Related: [[Animation and MP3 Systems - Progress and To Do]] · [[Animation References]] · [[Max Payne 3 Animation Reference]] · [[Movement State Machine]] · [[Loadout and Dual Wielding]]

## From Blender to the game
1. **Authoring:** the clips are Python in `Assets/Blender/Animation`. `mp_lib` holds the R15 rig, IK and the tools; `mp_locomotion`, `mp_arms`, `mp_stances` and `mp_hands` register the clips. Everything is authored in Roblox space (studs, Y up, facing −Z), so a joint rotation is exactly the Transform Roblox applies and nothing needs converting.
2. **Export:** `mp_lib.export()` writes `Exports/keyframes.json`, every clip with only the keys it needs. Two exports of the same clips are byte-identical. `export(fbx=True)` also writes one FBX per clip to `Exports/FBX` for Studio's Animation Editor; that folder isn't kept in git. `MaximumPain_Animations.blend` holds the rig and every clip as an action.
3. **Import:** `mp_serve.start()` serves the file at `http://127.0.0.1:8765`. Then, in Studio edit mode, `require(game.ServerStorage.Tools.AnimationImporter:Clone())()` builds a KeyframeSequence per clip in `ReplicatedStorage.Assets.Animations`. HTTP is switched on only for the fetch. (Code run through Studio's MCP can't reach `127.0.0.1`; see the to-do note's "How to resume" for importing from there.)
4. **Playing:** in Studio, a slot with no `Id` plays its KeyframeSequence directly, so nothing has to be published to test. So does a clip listed in `AnimationConfig`'s `STALE` (re-made since it was published): Studio plays the new version, live servers the published one, until it's uploaded again.
5. **Publishing:** live servers need each clip published, and an experience only plays animations its own creator owns, so **the place's owner (83tg) publishes them**. Studio can't publish in bulk, so `Assets/Blender/Animation/publish_animations.ps1` does it through Open Cloud, with an API key made on 83tg in `ROBLOX_API_KEY`: `-Build` writes an `.rbxmx` per clip from `Exports/keyframes.json` (built the way the importer builds the place's clips), `-Upload` uploads the ones without an id and records the ids in `Exports/animation_ids.json`, `-Only <clips>` limits either step, and `-Force` uploads a re-made clip again. The ids go into `AnimationConfig`'s `IDS` table by clip name, which every slot playing that clip reads.
6. **After changing a clip:** export and import it, add its name to `STALE`, then `-Build -Only <clip>`, `-Upload -Only <clip> -Force`, copy its new id into `IDS` and take it off `STALE`.

Headless rebuild, Blender 5.2: `blender --background --factory-startup --python <script>`. The steps are in the to-do note's "How to resume".

## Layers (`AnimationController`)
| Layer | Priority | Plays | Blend rate (per second) |
|---|---|---|---|
| body | Movement | Locomotion: idle, jog, run, sprint, crouch walk, limp and hobble, in four directions, all on one shared phase and played at real speed ÷ the clip's authored speed so the feet don't slide. Air: jump, fall, land, landing roll. One clip per stance: cover, the dive, the vault, getting up, Last Stand. The turns popping up out of low cover and ducking back. | 10 (the vault takes over at 30, the low cover turns at 25) |
| hold | Action | The arms' pose for the guns in hand (crouched, a two-handed gun has its own), the carried two-handed gun, injured arms | 12 |
| aim | Action2 | The gun raised (aiming, just fired, diving, on the floor, popped out, Last Stand), or blind fire | 18 up, 7 down |
| action | Action3 | Reloads and draws stretched to the server's `ActionEnds`, pickups, painkillers, drops | 12 (the switch clips that pass the two-handed gun between the hands at 40, `SWITCH_FADE`) |

On top of the clips, every frame, the procedural layers bend the joints (`ProceduralLayer`):
- **AimLayer:** puts the gun exactly where the player aims, plus the chest blade, head look (not while hidden in cover, where the clip looks along the wall), recoil springs, momentum lean (worked out in the hips' frame), a run arm pump, and the left hand on the gun's Support point. It also keeps a carried gun out of the floor, keeps arms and guns out of walls (`guardArm`), and eases the body through height changes without the feet going through the floor. That foot guard is on all the time in cover, where clips turned far apart blend. A gun that changes hands in a switch eases from where the old hand had it into its new grip over 0.12 s (`easeHandovers`), since the clips' hands only meet exactly on the default R15.
- **HitReactions:** flinches.

## Rules
- **Timers stay in charge.** The server's timers decide when a reload, draw, dive or get-up ends; the clips are stretched to fit. The server never waits for a marker.
- **One-off clips hold their last frame** while they fade (Play() would restart them from frame 0). Wanted again while fading, as on a second corner, they restart. One that passes its end within a long frame and stops is played again and put straight back on its last frame, so `Animator.AnimationPlayed` fires twice for it.
- **Clips bound to a stance** (DodgePrep, GettingUp, LastStandWakeup, CoverPopUp) hold until the stance ends, then fade (with the height change, where there is one).
- **Clips made for the height ease:** when the hip height changes, `AimLayer` holds the body where it was and eases it to the new height at 10 per second, in real time. The low cover turns (CoverPopUp, CoverDuck) plant their feet where that hold leaves the floor, so they play in real time too, not at the character's `TimeScale`.
- **Markers are cosmetic.** MagOut, MagGrab, MagIn, BoltBack, BoltForward, ShellIn, Pump, CylinderOut, CylinderIn, BreakOpen and BreakClose move the parts of the gun being reloaded through its own Motor6Ds: the right-hand gun, or both pistols for ReloadDual. A gun part's resting pose is kept on its motor (`RestC0`).
- **Bullet time:** locomotion follows the slowed velocity, and everything else plays at the character's `TimeScale`. The blends run in real time.
- **Animator only**, never the old `Humanoid:LoadAnimation`. Roblox's `Animate` script is switched off for the character once the clips can play.
- **Roblox blends tracks joint by joint** (same priority: weight-normalised, the short way round; a higher priority overrides by its total weight). Clips that blend into each other need every joint well short of a half turn from its partner's, or the way round flips with small changes (measured 2026-11-09).
- **Arm clips are chest-relative.** Author them with IK on the body they'll play on, then check them by FK on every body that plays them (rifle box against the floor, the wall and the body).

## Slots (`ReplicatedStorage.Modules.AnimationConfig`)
| Group | Slots |
|---|---|
| Locomotion | Idle, Jog/Run/CrouchWalk + Forward/Back/Left/Right, Sprint, CrouchIdle, LimpLeft/Right, Hobble |
| Air | Jump, Fall, Land, LandRoll |
| Cover | CoverHigh/Low + Left/Right, CoverHigh/LowMove + Left/Right, CoverCornerHigh/Low + Left/Right, CoverPopUp/CoverDuck + Left/Right, CoverAim |
| Shoot-dodge | DodgePrep, DodgeAir and DodgeLand + Forward/Back/Left/Right, DodgeGround, GettingUp |
| Vault | Vault (a speed vault, paced by the way over) |
| Last Stand | LastStandFall, LastStand, LastStandWakeup |
| Holds | Hold + Pistol/Revolver/SMG/SawnOff/Rifle/Shotgun/Sniper/Dual (the gun's `AnimSet`), HoldRifleLow/ShotgunLow/SniperLow (crouched), CarryTwoHanded, CarryTwoHandedLow, CarryTwoHandedCover, CarryTwoHandedCoverLow, CoverHoldHighOne/Two/Dual, CoverHoldLowOne/Dual, CoverHoldLowTwoLeft/Right, InjuredArmLeft/Right |
| Aim and blind fire | AimPistol, AimRifle, AimDual, BlindFireHigh/Low + Left/Right, BlindFireLowMove/HighMove + Left/Right, BlindFireHighTwo/HighMoveTwo + Left/Right (a two-handed gun) |
| Actions | DrawOneHanded, DrawTwoHanded, SwapToOneHanded, DrawDual, Pickup, Painkiller, DropGun |
| Reloads | Reload_<gun> for all 13 guns, sharing ReloadPistol, ReloadRevolver, ReloadRifle, ReloadSniper, ReloadPump and ReloadSawnOff; ReloadOneHand_<gun> for the 6 one-handed guns, sharing ReloadPistolOneHand, ReloadRevolverOneHand and ReloadSawnOffOneHand; ReloadDual |

## How clips are chosen
- **Carried two-handed gun,** held by its middle (`LoadoutService` hangs it so; the clips are made for that exact offset):
  - CarryTwoHanded standing (at the side, the arm hanging, bent a little).
  - CarryTwoHandedLow crouching and getting up (beside the left knee, pointing ahead).
  - CarryTwoHandedCover behind high cover (in front of the left hip, pointing ahead, the elbow down), CarryTwoHandedCoverLow behind low cover and while turning to pop up over it (by the left knee, tipped up about 30°, the butt toward the floor).
  - If the gun would still go into the floor (dives, rolls, the longest guns), AimLayer swings the arm up at the shoulder just enough, and keeps it out of walls the same way.
- **Crouched with a two-handed gun in hand** (the crouch idle or walk, not in the air): `Hold<set>Low` for the Rifle, Shotgun and Sniper sets, which cover every two-handed gun: across the front of the body, the muzzle to the front-left and down, both hands on it, the elbows down. The standing holds pointed it into the floor and through the thighs. Where a crouched hold can't load, the standing one plays.
- **Reloading with a two-handed gun carried:** `ReloadOneHand_<gun>`, the right hand alone against the belt (not when dual wielding). Where it can't load, the two-handed reload plays.
- **Switching:** `DrawTwoHanded` draws the carried gun (the right hand takes it 40% of the way through); `SwapToOneHanded` plays instead of `DrawOneHanded` when the two-handed gun is still in the right hand as a switch to a one-handed gun starts. Both fade in at 40 a second: at the usual 12 the hold clips under them still showed at the handover and pulled the hands apart. See [[Loadout and Dual Wielding]] for when the server moves the gun.
- **Dive clips:** picked by comparing the dive's direction with where the body faces, so a sideways dive with the gun forward plays the sideways clips.
- **The vault:** the clip's playback chases the way over the obstacle. The legs are tucked (25% of the clip) when the leading knee reaches the near face (1.3 studs ahead of the root), and stay up (72%) until the trailing foot passes the far face (0.9 behind). The playback speed (at most 6) replicates to other players.
- **Cover:** side-on (back and inner shoulder to the wall, turned to the edge). The root part keeps facing the wall, so the cover clips turn the body round inside it. The idle follows the side being worked, the move clips (side-on, facing the way it goes) run at the speed along the wall, and the corner clips play while swinging round. The holds are made on the cover bodies: each gun is placed in a body part's frame and aimed in the body's facing frame, so one clip fits both sides.
- **Popping up out of low cover and ducking back:** `CoverPopUp<side>` plays on the change to `CoverPeek` (bound to it, 0.25 s) and `CoverDuck<side>` on the way back (0.3 s). The body turns toward the edge being worked, the feet stepping round. For the first 0.15 s of a pop-up the gun stays in the low hold, then the aim takes it. Other players' characters use the right-hand clips.
- **Blind fire:** the gun arm, the waist and the neck, one clip per side. High cover: the arm out round the end (the left hand keeps the carried rifle). Low cover: the chest comes up out of the squat's lean, leaning off the gun side, and the arm goes straight up past the ducked head, the gun over the top tipped up about 25°. Sliding along cover: the run's own clip (`BlindFireLowMove<way>`, `BlindFireHighMove<way>`), picked the same frame as the run. Some never cross-fade: the low run going right with any other blind fire clip, and the high runs with each other (a reversal). The old one goes down into the hold first (`DIP_FADE`).
- **Blind fire with a two-handed gun behind high cover:** clips of its own, both hands on the gun across the body (the support hand is AimLayer's, on each gun's own Support point): still, `BlindFireHighTwo<side>` points it toward the edge worked and round it; sliding, `BlindFireHighMoveTwo<way>` points it ahead along the wall. Where they can't load, the one-handed clips play.

## Not done
- Publishing the place itself (83tg): every clip is published and its id is in `IDS` (2026-11-14), but live servers run the place's last published version until then. See the to-do note.
- Compare each clip with [[Max Payne 3 Animation Reference]] again after publishing.
- On bodies unlike the default R15, the switch's hands meet only through `AimLayer`'s ease; IK on the receiving hand near the handover would make them really meet (to-do 4.29).
