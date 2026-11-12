# Architecture

How the game's code is split and how the parts talk. Rebuilt 2026-10-31 for loadouts, stances, cover, shoot-dodge and Last Stand.
Related: [[Movement State Machine]] · [[Loadout and Dual Wielding]] · [[Cover System]] · [[Shoot-Dodge]] · [[Last Stand and Bullet Time]] · [[Animation Hooks]] · [[Test Arena]] · [[Changelog]]

## Ground rules
- **The server decides.** Stances, ammo, hits, damage, what is in each hand and Last Stand all happen on the server. Clients send requests and show the results.
- **Clients predict.** The client changes its own stance the moment a key is pressed, so the controls feel instant. The server checks each request and confirms it (silently), rejects it, or forces a different stance. See [[Movement State Machine]].
- **One stance at a time.** Every script asks `StanceRules` what the current stance allows, so no two scripts fight over the character, and each stance maps to one animation slot.
- **Timers run the game; animations follow.** Reloads, draws, dives and get-ups run on server timers, and the animations are stretched to fit them. See [[Animation Hooks]].
- **Rules live in shared modules.** The same code runs on both sides, so the client's prediction and the server's check agree.

## Where the code lives
### Shared (ReplicatedStorage.Modules)
| Module | Job |
|---|---|
| `StanceRules` | The state machine: every stance, what it allows, its speed, crouch height, spread and recoil, and which stances it can change into. |
| `CoverRules` | Cover geometry: finding walls, high or low, edges, inside and outside corners, headroom. |
| `DodgeRules` | Shoot-dodge numbers and direction helpers. |
| `ShotRules` | Where a shot leaves from (the "virtual muzzle"), blind-fire paths over and round cover, and the stance and movement accuracy modifiers. |
| `LoadoutRules` | Slots, hold modes, the dual-wield drop penalty, pickups and the arm-injury rules, as pure functions that check themselves. |
| `LastStandRules` | Last Stand numbers and who qualifies. |
| `BulletTimeRules` | The adrenaline meter's levels, how long each lasts, who counts as seen, the time scales (0.3 for those seen, 0.6 for the activator), the aim penalty. |
| `VaultRules` | What can be vaulted, the path over it (its apex rises with the avatar's legs), and the timing. The server only uses `find`, reaching `SERVER_SLACK` further for its lagging copy of a running character. |
| `RagdollRules` | The Euphoria-style death: muscles that pull toward a collapse and fade (see [[Euphoria-style Reactions and Ragdolls]]). |
| `AnimationConfig` | Every animation slot and the clip it plays (113 slots, 106 clips made in Blender). In Studio an unpublished slot plays its KeyframeSequence directly. |
| `WeaponConfig`, `WeaponMath`, `LimbRules` | Gun numbers, spread and recoil maths, limb health rules (from the first milestone). |

### Server (ServerScriptService)
| Script | Job |
|---|---|
| `CharacterServer` | Sets up each character in a fixed order (stance, limbs, loadout), takes stance and painkiller requests, runs the stance checks every frame. Replaces `LimbServer`. |
| `StanceService` | The server's state machine: checks requests, runs timed steps, re-checks cover, watches movement speed. |
| `LoadoutService` | Builds guns as models, hangs them on the body, hold modes, dual wield, drop, pickup, switching, reloads. |
| `WeaponServer` | Firing: fire rate, ammo, the gun's path and obstruction, spread with modifiers, hits, damage, adrenaline. Also takes hold, drop, aim and reload requests. |
| `LimbService` | Limb damage, painkillers, arm effects. Sends killing blows to `LastStandService`. |
| `LastStandService` | Decides Last Stand or death, runs the window, success and failure. |
| `BulletTimeService` | `TimeScale` on every character: Last Stand bubbles and player-triggered bullet time (sight checks 10 times a second, the aim penalty), and the adrenaline meter. |
| `RagdollService` | Turns any dying body into a ragdoll; runs the muscles and the killing shot's push for non-players (players' own clients run theirs). |
| `TestArena` | The gun table, target dummies and the gunman in the [[Test Arena]]. |

### Client (StarterPlayer.StarterPlayerScripts)
`ClientMain` starts the controllers in this order: `Hud`, `CameraController`, `CharacterController`, `CoverController`, `DodgeController`, `VaultController`, `WeaponController`, `LastStandController`, `ProceduralLayer`, `AimLayer`, `HitReactions`, `RagdollController`, `KillCamController`, `AnimationController`.

| Controller | Job |
|---|---|
| `Keybinds` | Every control in one table. The HUD's keybind list reads it. |
| `CharacterController` | The client's state machine: predicts stances, sprint and crouch keys, walk speed, jumping, the painkiller and bullet-time keys. Sets the hip height and moves the root with it (`applyHeight`, which also handles heights the server forces first). Hands the body to the cover, dodge and vault controllers. Reads WASD and the left stick itself. |
| `CoverController` | Taking cover, moving along it, corners, popping out to aim, the cover prompt. Keeps the root part facing the wall and the gap the body's reach needs (`bodyReach`, remembered per cover stance); the side-on cover clips turn the body round inside the root part and lean its back onto the wall. |
| `DodgeController` | The dive: run-up, flight, wall collisions, landing, lying down, getting up. |
| `VaultController` | The vault: flies the body along `VaultRules`' path with free aim; `progress()` paces the Vault clip; softens the camera over the hop. |
| `WeaponController` | Hold modes, trigger, aim, reload, pickups, recoil, reticle. |
| `WeaponEffects` | Muzzle flash, gun kick, tracers, impacts. `restPose(motor)`: a gun part's resting pose, kept on the motor. |
| `CameraController` | Shoulder camera, aim and scope zoom, recoil, cover shoulder and corner turns, dive field of view, Last Stand lock. Holds its height through hip-height changes and eases (`absorbRise` for the root jumping, `setVerticalLag` for a vault). Reports where the player looks (`AimUpdate`). |
| `LastStandController` | Camera lock and drag, killer outline, countdown, the bullet-time look. |
| `ProceduralLayer` | Applies every procedural joint bend (aim, recoil, flinches) once a frame, before physics, on top of the animations. |
| `AimLayer` | Points every character's gun where its owner aims from any pose, the chest blade, head look (off while hidden in cover), recoil springs, momentum lean, the left hand on the gun, the carried gun's floor guard, arms and guns kept out of walls (`guardArm`, checked where the body will be drawn after the physics step), and the height easing (with the foot guard, which also runs all the time in cover). |
| `HitReactions` | Euphoria-style flinches on every character, and the recent-hit log the death push and kill cam read. |
| `RagdollController` | This player's own death: the body goes physical here at once, pushed by the killing shot. |
| `KillCamController` | This player's kill cam: the bullet, the impact in slow motion, the comic-style panel ([[Max Payne 3 Kill Cam]]). |
| `AnimationController` | Plays the clips in layers (body, hold, aim, one-off arm actions), stretched to the server's timers, slowed by bullet time; moves gun parts on reload markers. Plays one-off body clips on stance changes, the turns popping up out of low cover and ducking back among them. Sliding along cover, blind fire plays the run's own clips; the low run going right, and the high runs on a reversal, drop into the hold rather than cross-fading. A two-handed gun behind high cover has blind fire clips of its own (the one-handed ones stand in where those can't load). |
| `Hud` | Draws everything; holds no rules. |

**Rule:** no weak-keyed tables keyed by instances (`__mode = "k"`) for state that must survive. The engine can drop an instance's Lua handle while the instance still exists, and the entry vanishes with it; this left slides racked back after reloads until 2026-11-02. Keep such state on the instance (attributes) or in a plain table cleared when the instance leaves. AimLayer's gun-box cache is the one weak table left, on purpose.

## Remotes (ReplicatedStorage.Remotes)
| Remote | Direction | Carries | Server checks |
|---|---|---|---|
| `StanceRequest` | client → server | request and data: Sprint, Crouch, EnterCover, LeaveCover, CoverAim, Dodge, DodgeLand, GetUp | transition allowed, injuries, headroom, cover geometry, dive direction, cooldown, on the ground; 20 requests/s |
| `StanceResult` | server → owner | "Rejected" or "Forced", the server's stance, a reason or get-up time | — |
| `FireWeapon` | client → server | aim point, hand ("Right" or "Left") | stance, Last Stand fall, sprint delay, switching or reloading, gun in that hand, arms, fire rate (with bullet time), ammo, the gun's path; 45 requests/s |
| `ReloadWeapon` | client → server | — | stance, not switching, a gun that needs ammo |
| `WeaponAction` | client → server | "Hold" + mode, "Drop", "Aim" + on/off | stance allows switching, the loadout plan; 20 requests/s |
| `WeaponFired` | server → all | shooter, gun, muzzle, end points, which hit flesh | — |
| `UsePainkiller` | client → server | — | alive, has one, hurt, stance allows it, 1 s cooldown |
| `LastStandEvent` | server → owner | "Start" (killer, fall time, window), "Survived" (wakeup time), "Failed" | — |
| `AimUpdate` (unreliable) | client → server | where the player looks (yaw, pitch), at most 15 times a second | becomes the `Aim` attribute: other clients' aim layers point this player's gun with it, and bullet time's sight check uses it |
| `BulletTimeRequest` | client → server | — | not already active, alive, not in a Last Stand, at least one level in the meter; 4 requests/s |

## Character attributes (set by the server)
| Attribute | Meaning |
|---|---|
| `Stance`, `StanceSince` | Current stance and when it started (server time). |
| `HoldMode` | None, OneA, OneB, Dual or Two. |
| `Action`, `ActionEnds` | Reloading or Switching, and when it finishes (server time). |
| `Aiming` | Aiming down the sights, as the server sees it. |
| `CoverNormal`, `CoverHeight`, `CoverTop`, `CoverSide` | The cover in use. |
| `DodgeDirection`, `DodgeScale` | The current dive. |
| `TimeScale` | 1, or lower while slowed by bullet time. |
| `Adrenaline` | 0 to 1; the HUD's slim bar. |
| `BulletTimeLevel`, `BulletTimeEnds` | Set while this character's own bullet time runs. |
| `AimPenalty` | Set while slowed by a higher level than this character's own; the camera multiplies mouse speed by it. |
| `Aim` | Where the character looks (Vector2 yaw, pitch), from `AimUpdate` (the test gunman sets its own). |
| `LastHitDamage`, `LastHitDirection`, `LastHitPosition` | The last hit, for the death push. |
| `Ragdolled` | Set while the body is a ragdoll. |
| `LastStandEnds`, `Wakeup` | When the Last Stand window ends; set while getting up after one. |
| `BaseHipHeight` | Standing hip height. Crouching lowers HipHeight from it. |
| Limb attributes | See [[Limb Health]]. |

Gun models carry `WeaponId`, `Slot`, `Place` (Right, Left, Holster or Dropped), `Limb`, `Ammo`, `Reserve`, `Reloading`, and on the floor `DroppedAt` (also the drop's token) or `RackId`.
Set on each client only, never replicated: `LastShot` on the character (when this player last fired), `RestC0` on a gun's moving-part motors (their resting pose), `Flashes` on a muzzle (its flash counter).
Tags: `NotCover` (characters, dummies and dropped guns are never cover) and `Combatant` (non-player characters bullet time can slow).

## Studio tools and test hooks
- `ServerStorage.Tools` (never reaches players): `AnimationImporter` builds the clips from Blender's export, and `TestHarness` records and measures play tests. Both are in the repo: `Assets/Blender/Animation/studio_import.luau` and `Tools/TestHarness.luau`. The game's own scripts are not in git, on purpose (the repo is public).
- A Vector2 `DebugLook` attribute on the player (yaw and pitch in radians) points their camera, in Studio only. Automated play tests use it to aim. It only applies when the value changes.
- `DebugBulletTime = true` on any character activates its bullet time (it needs `Adrenaline`; a dummy needs an `Aim` toward its target).
- `StanceService._records` exposes the server's stance records to game scripts in Studio. The command bar's `require` makes its own copy of a module, so it can't see them.
