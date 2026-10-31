# Architecture

How the game's code is split and how the parts talk. Rebuilt 2026-10-31 for loadouts, stances, cover, shoot-dodge and Last Stand.
Related: [[Movement State Machine]] · [[Loadout and Dual Wielding]] · [[Cover System]] · [[Shoot-Dodge]] · [[Last Stand and Bullet Time]] · [[Animation Hooks]] · [[Test Arena]] · [[Changelog]]

## Ground rules
- **The server decides.** Stances, ammo, hits, damage, what is in each hand and Last Stand all happen on the server. Clients send requests and show the results.
- **Clients predict.** The client changes its own stance the moment a key is pressed, so the controls feel instant. The server checks each request and confirms it (silently), rejects it, or forces a different stance. See [[Movement State Machine]].
- **One stance at a time.** Every script asks `StanceRules` what the current stance allows, so no two scripts fight over the character, and each stance maps to one animation slot.
- **Timers run the game; animations follow.** Reloads, draws, dives and get-ups run on server timers. Animations (none yet) will be stretched to fit them. See [[Animation Hooks]].
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
| `AnimationConfig` | Every animation slot (all empty for now). |
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
| `BulletTimeService` | Localized bullet time (`TimeScale`) and the adrenaline meter. |
| `TestArena` | The gun table, target dummies and the gunman in the [[Test Arena]]. |

### Client (StarterPlayer.StarterPlayerScripts)
`ClientMain` starts the controllers in this order: `Hud`, `CameraController`, `CharacterController`, `CoverController`, `DodgeController`, `WeaponController`, `LastStandController`, `AnimationController`.

| Controller | Job |
|---|---|
| `Keybinds` | Every control in one table. The HUD's keybind list reads it. |
| `CharacterController` | The client's state machine: predicts stances, sprint and crouch keys, walk speed, crouch height, jumping, the painkiller key. Hands the body to the cover and dodge controllers. Reads WASD and the left stick itself (this place has no PlayerModule). |
| `CoverController` | Taking cover, moving along it, corners, popping out to aim, the cover prompt. |
| `DodgeController` | The dive: run-up, flight, wall collisions, landing, lying down, getting up. |
| `WeaponController` | Hold modes, trigger, aim, reload, pickups, recoil, reticle. |
| `WeaponEffects` | Muzzle flash, gun kick, tracers, impacts. |
| `CameraController` | Shoulder camera, aim and scope zoom, recoil, cover shoulder and corner turns, dive field of view, Last Stand lock. |
| `LastStandController` | Camera lock and drag, killer outline, countdown, the bullet-time look. |
| `AnimationController` | Plays animation slots as stances and actions change (nothing until ids are filled in). |
| `Hud` | Draws everything; holds no rules. |

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
| `LastStandEnds`, `Wakeup` | When the Last Stand window ends; set while getting up after one. |
| `BaseHipHeight` | Standing hip height. Crouching lowers HipHeight from it. |
| Limb attributes | See [[Limb Health]]. |

Gun models carry `WeaponId`, `Slot`, `Place` (Right, Left, Holster or Dropped), `Limb`, `Ammo`, `Reserve`, `Reloading`, and on the floor `DroppedAt` or `RackId`.
Tags: `NotCover` (characters, dummies and dropped guns are never cover) and `Combatant` (non-player characters bullet time can slow).

## Studio test hooks
- A Vector2 `DebugLook` attribute on the player (yaw and pitch in radians) points their camera, in Studio only. Automated play tests use it to aim.
- `StanceService._records` exposes the server's stance records in Studio.
