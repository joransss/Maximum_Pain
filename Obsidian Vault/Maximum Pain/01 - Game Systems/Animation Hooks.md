# Animation Hooks

There are no animations yet, as requested, but everything is ready for them: every animation has a named slot, the game runs on timers that animations will follow, and guns hang from joints that animations can move. Built 2026-10-31.
Related: [[Animation References]] · [[Max Payne 3 Animation Reference]] · [[Movement State Machine]] · [[Loadout and Dual Wielding]]

## Adding an animation
1. Make and publish it (Blender or the Animation Editor).
2. Paste `rbxassetid://<id>` into its slot in `ReplicatedStorage.Modules.AnimationConfig`.

That's all. `AnimationController` loads it through the character's Animator and plays it when its stance or action comes up. Empty slots are skipped.

## Rules
- **Timers stay in charge.** The server's timers decide when a reload finishes, a gun is drawn or a dive lands. Reload and draw tracks are sped up or slowed to fit the server's time (`ActionEnds`).
- **Markers are cosmetic.** Use them for sounds and moving gun parts (MagOut, MagIn, BoltBack...). The server never waits for a marker. Register what a marker does with `AnimationController.onMarker`.
- **Animator only**, never the old `Humanoid:LoadAnimation`.
- **Guns:** animate the gun through the Motor6Ds `RightGrip` (RightHand → gun Handle) and `LeftGrip`. The gun's own Motor6Ds (Magazine, Slide, Bolt, Pump, Cylinder...) move its parts.
- **Bullet time** slows playing tracks by the character's `TimeScale`.

## Slots
| Group | Slots | Priority |
|---|---|---|
| Stances | Standing, Walk, Sprinting, SprintStart, SprintStop, Crouching, CrouchWalk | Core, Movement |
| Cover | CoverHigh, CoverLow, CoverHighMoveLeft/Right, CoverLowMoveLeft/Right, CoverEnter, CoverCornerLeft/Right, CoverPeekHighLeft/Right, CoverPeekLow, CoverAim | Core, Movement, Action |
| Shoot-dodge | DodgePrep (marker Launch), DodgeAirForward/Back/Left/Right, DodgeLand (Impact), DodgeGround, GettingUp | Action2 |
| Last Stand | LastStandFall (Impact), LastStand, LastStandWakeup, Dead | Action4 |
| Holding | HoldPistol, HoldRevolver, HoldSMG, HoldSawnOff, HoldRifle, HoldShotgun, HoldSniper, HoldDual, CarryTwoHanded | Idle |
| Aim and fire | AimPistol, AimDual, AimRifle, FirePistol, FireRifle | Action, Action2 |
| Guns | DrawOneHanded, DrawTwoHanded, DrawDual (Grab), DropTwoHanded (Release), Pickup (Grab), Painkiller | Action |
| Reloads | Reload_<gun> for each of the 13 guns, and ReloadDual. Markers: MagOut, MagIn, BoltBack, BoltForward, ShellIn, Pump, CylinderOut, CylinderIn | Action |

The hold set a gun uses is its `AnimSet` in `WeaponConfig` (Pistol, Revolver, SMG, SawnOff, Rifle, Shotgun, Sniper). The dive's air slot is picked from the dive direction compared with where the body faces.

## Stand-ins until then
| Now | With animations |
|---|---|
| Crouch, low cover and lying down drop the hips (HipHeight) and sink the legs into the floor | Keep the hip drop; the animation folds the legs to match |
| Guns hang from the hands while Roblox's walk swings the arms | Hold and aim poses |
| Shots leave from a "virtual muzzle" at arm's length from the shoulder | Unchanged: animations never decide where shots go |
| Roblox's default walk and idle | Replace the default `Animate` script's ids, or turn it off once the stance slots are filled |
| The carried two-handed gun points forward from the left hand | CarryTwoHanded: rifle under the arm, Max Payne 3 style |

Compare each new animation with [[Max Payne 3 Animation Reference]].
