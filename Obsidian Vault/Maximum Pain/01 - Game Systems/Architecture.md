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
| `LoadoutRules` | Slots, hold modes, the dual-wield drop penalty, pickups, the arm-injury rules, and when a switch passes the two-handed gun from hand to hand (`HANDOVER`, `handoverTimes`), as pure functions that check themselves. |
| `LastStandRules` | Last Stand numbers and who qualifies. |
| `BulletTimeRules` | The adrenaline meter's levels, how long each lasts, who counts as seen, the time scales (0.3 for those seen, 0.6 for the activator), the aim penalty. |
| `VaultRules` | What can be vaulted, the path over it (its apex rises with the avatar's legs), and the timing. The server only uses `find`, reaching `SERVER_SLACK` further for its lagging copy of a running character. |
| `RagdollRules` | The Euphoria-style death: muscles that pull toward a collapse and fade (see [[Euphoria-style Reactions and Ragdolls]]). |
| `AnimationConfig` | Every animation slot and the clip it plays (123 slots, 113 clips made in Blender), and each clip's published id (`IDS`, all 113 since 2026-11-14). In Studio a slot with no id, or a clip listed in `STALE`, plays its KeyframeSequence directly. Checks that every gun has a reload slot, and a one-handed gun a one-handed one. |
| `WeaponConfig`, `WeaponMath`, `LimbRules` | Gun numbers, spread and recoil maths, limb health rules (from the first milestone). `LimbRules.totalHealth`: every limb's health added up, which only drops on a hit (the menu's leave rule and UNDER FIRE use it). |
| `MatchRules` | The match's states and timings (placeholders: 8-minute free-for-all, 15 s between matches, 2 players to start), and `results`: who won and lost, counting only players in the match for half of it. Checks itself. |
| `ProgressionRules` | The level cap (50) and the highest prestige (5); by 2026-11-18 also the level curve, the rewards (XP and Cash), assists, the Cash multipliers and the titles (Phase C's code, not yet described in these notes). Checks itself. |
| `MenuRules` | The main menu's rules (2026-11-18): what a client may ask (`Play`, `Leave`) and why the server may refuse; `LEAVE_SAFE_TIME` (5 s), `REDEPLOY_DELAY` (10 s), the gap between requests; the menu camera's shot clock (`shot`, `blackness`) and where its shots are (`shots`: `Workspace.MenuCams.<Map>`). Checks itself. |
| `UiAssets` | Every image the UI draws, by name: its size and its uploaded id (2026-11-18). No other script holds an asset id. Made by `Assets/Blender/UI/ui_lib.py` ([[Blender and Asset Pipeline#UI art for the menus]]). |

### Server (ServerScriptService)
| Script | Job |
|---|---|
| `CharacterServer` | Sets up each character in a fixed order (stance, limbs, loadout), takes stance and painkiller requests, runs the stance checks every frame. Replaces `LimbServer`. |
| `StanceService` | The server's state machine: checks requests, runs timed steps, re-checks cover, watches movement speed. |
| `LoadoutService` | Builds guns as models, hangs them on the body (a carried two-handed gun by its middle, `carryOffset`), hold modes, dual wield, drop, pickup, switching (the two-handed gun handed over partway through, `handOver`), reloads. |
| `WeaponServer` | Firing: fire rate, ammo, the gun's path and obstruction, spread with modifiers, hits, damage, adrenaline. Also takes hold, drop, aim and reload requests. |
| `LimbService` | Limb damage, painkillers, arm effects. Sends killing blows to `LastStandService`. |
| `LastStandService` | Decides Last Stand or death, runs the window, success and failure. Announces every death it deals with whoever dealt the blow (`Killed`: character, killer), which the match's scores read. |
| `GameServer` | Starts `ProfileService`, `MatchService`, `ProgressionService` and `SpawnService`, in that order. |
| `ProfileService` | Every player's saved profile (level, XP, cash, prestige, stats), and **the only code that saves data**. Loads and locks the profile when the player joins, saves it every 60 s, on leaving and on shutdown; kicks a player whose profile can't be loaded instead of giving them a fresh one. `get(player)` returns it frozen; `update(player, change)` is the only way to change it (the change is kept whole or not at all, and refused if it breaks a rule); `release(player)` before a teleport; `Loaded` and `Changed` signals. See [[Menus, Loadout, Progression and Shop - To Do#9. Server-side economy and anti-exploit]]. |
| `ProfileSchema` | The profile's fields and defaults, its `VERSION` and migrations, `validate` (types, ranges, storable as JSON). Checks itself. |
| `ProfileStorage` | The DataStore side: one key per player, session locking inside `UpdateAsync` (a lock is free after 180 s without a save), retries with backoff. Its lock rules are pure functions that check themselves; it runs against a stand-in DataStore in tests. |
| `MatchService` | Runs matches on a timer: Waiting (too few players), Intermission, Running. Everyone who spawns while one runs is in it. Counts kills (from `LastStandService.Killed`), deaths and each player's time in the match; at the end `Ended` carries the results (`MatchRules.results`). Pays nothing itself: `ProgressionService` listens to `Ended`. `sitOut(player)` (2026-11-18): the player went back to the main menu, so their stretch in the match ends as if they had left the server, until they spawn again. |
| `SpawnService` | Who is in the fight and who is in the main menu (2026-11-18). `Players.CharacterAutoLoads` is off: players join into the menu and get a character when they ask (`MenuRequest` "Play"); then they are `Deployed`, respawned `RespawnTime` after each death (or after losing their character any other way) until they ask to leave (`"Leave"`: refused within 5 s of a hit, in a Last Stand or dead; `MatchService.sitOut`; PLAY then waits 10 s). Points menu players' `ReplicationFocus` at the menu camera's shot. Refusals go back on `MenuResult`. |
| `ProgressionService` | XP, Cash, levels, titles and lifetime stats, paid from events the server saw (kills from `LastStandService.Killed` with bonuses and assists from `CombatLog`, wins and losses from `MatchService.Ended`); tells each player what was paid (`ProgressionEvent`) and takes one request, the title shown (`SetTitle`). Phase C's code, found in the place on 2026-11-18 (from its header). |
| `CombatLog` | Who hurt whom in each life: `LimbService` reports every point of limb damage here, and the rewards ask what the killing blow was like and who else did damage. Phase C's code, found 2026-11-18 (from its header). |
| `BulletTimeService` | `TimeScale` on every character: Last Stand bubbles and player-triggered bullet time (sight checks 10 times a second, the aim penalty), and the adrenaline meter. |
| `RagdollService` | Turns any dying body into a ragdoll; runs the muscles and the killing shot's push for non-players (players' own clients run theirs). |
| `TestArena` | The gun table, target dummies and the gunman in the [[Test Arena]]. |

### Client (StarterPlayer.StarterPlayerScripts)
`ClientMain` starts the controllers in this order: `Hud`, `CameraController`, `CharacterController`, `CoverController`, `DodgeController`, `VaultController`, `WeaponController`, `LastStandController`, `ProceduralLayer`, `AimLayer`, `HitReactions`, `RagdollController`, `KillCamController`, `AnimationController`, then the match and progression screens (`MatchHud`, `KillFeed`, `NameTags`, `Scoreboard`, `MatchEndScreen`), and last `MenuController`, which covers the HUD and takes the input from all of them while the menu is up.

| Controller | Job |
|---|---|
| `Keybinds` | Every control in one table. The HUD's keybind list reads it. |
| `CharacterController` | The client's state machine: predicts stances, sprint and crouch keys, walk speed, jumping, the painkiller and bullet-time keys. Sets the hip height and moves the root with it (`applyHeight`, which also handles heights the server forces first). Hands the body to the cover, dodge and vault controllers. Reads WASD and the left stick itself. `setControlEnabled(false)` (the main menu) stills the body: Roblox's PlayerModule (2026) reads the movement keys through the Input Action System and moves the humanoid in the Input render step, so `update`, later in the same frame, puts the move back to nothing, and jumping is off. |
| `CoverController` | Taking cover, moving along it, corners, popping out to aim, the cover prompt. Keeps the root part facing the wall and the gap the body's reach needs (`bodyReach`, remembered per cover stance); the side-on cover clips turn the body round inside the root part and lean its back onto the wall. |
| `DodgeController` | The dive: run-up, flight (the Humanoid kept from landing by itself, `holdInAir`; slowed by bullet time along the same arc), wall collisions, landing, lying down, getting up. |
| `VaultController` | The vault: flies the body along `VaultRules`' path with free aim; `progress()` paces the Vault clip; softens the camera over the hop. |
| `WeaponController` | Hold modes, trigger, aim, reload, pickups, recoil, reticle. `setInputEnabled(false)` (the main menu): no trigger, aim or gun keys. |
| `WeaponEffects` | Muzzle flash, gun kick, tracers, impacts. `restPose(motor)`: a gun part's resting pose, kept on the motor. |
| `CameraController` | Shoulder camera, aim and scope zoom, recoil, cover shoulder and corner turns, dive field of view, Last Stand lock. Holds its height through hip-height changes and eases (`absorbRise` for the root jumping, `setVerticalLag` for a vault). Reports where the player looks (`AimUpdate`). `setLookEnabled(false)` (the main menu): the mouse is free and nothing turns the view. |
| `LastStandController` | Camera lock and drag, killer outline, countdown, the bullet-time look. |
| `ProceduralLayer` | Applies every procedural joint bend (aim, recoil, flinches) once a frame, before physics, on top of the animations. |
| `AimLayer` | Points every character's gun where its owner aims from any pose, the chest blade, head look (off while hidden in cover), recoil springs, momentum lean, the left hand on the gun, the carried gun's floor guard, arms and guns kept out of walls (`guardArm`, checked where the body will be drawn after the physics step), and the height easing (with the foot guard, which also runs all the time in cover). A gun that changes hands in a switch eases into its new grip (`easeHandovers`). |
| `HitReactions` | Euphoria-style flinches on every character, and the recent-hit log the death push and kill cam read. |
| `RagdollController` | This player's own death: the body goes physical here at once, pushed by the killing shot. |
| `KillCamController` | This player's kill cam: the bullet, the impact in slow motion, the comic-style panel ([[Max Payne 3 Kill Cam]]). |
| `AnimationController` | Plays the clips in layers (body, hold, aim, one-off arm actions), stretched to the server's timers, slowed by bullet time; moves gun parts on reload markers. Plays one-off body clips on stance changes, the turns popping up out of low cover and ducking back among them. Sliding along cover, blind fire plays the run's own clips; the low run going right, and the high runs on a reversal, drop into the hold rather than cross-fading. A two-handed gun behind high cover has blind fire clips of its own (the one-handed ones stand in where those can't load). Crouched, a two-handed gun has holds of its own (`Hold<set>Low`); with one carried, a one-handed gun reloads with the right hand alone; `SwapToOneHanded` passes the two-handed gun back to the left hand, and the switch clips fade in fast (`SWITCH_FADE`). |
| `Hud` | Draws everything; holds no rules. `setCovered` hides it while the main menu is up, apart from `setVisible` (the kill cam), so neither undoes the other. |
| `MenuController` | The main menu (2026-11-18) and the one owner of which menu screen is up (a stack: choose opens, BACK returns). Opens on joining (no character) and on M mid-match (RESUME, LOADOUT, SHOP, SETTINGS, LEAVE MATCH); asks `SpawnService` to play or leave (`MenuRequest`) and reads `Deployed` and `RedeployAt`. While up it covers the HUD, takes every game key, stills the body, camera and guns, grades the picture, hides the match-end screen, shows UNDER FIRE on a hit and closes when the player dies. LOADOUT, SHOP and SETTINGS are placeholders until their phases: a screen is one entry in `SCREENS`. |
| `MenuKit` | The parts every menu screen is built from, in the menu plan's style: the 1080p canvas, the left shade, the page (context line, glitching heading, the list with the white bar, the notice), the prompts, the film overlays (from `UiAssets`), the grade on the live view, the glitch. `reducedMotion` for the reduce-motion setting to come. |
| `MenuCamera` | The live match behind the main menu for a player with no character: a dolly through the map's shots (`MenuRules`), the same shot for everyone, dipping to black at the cuts. |
| `UiStyle` | The look the match and progression screens share: the HUD's font and colours, flat tiles, shadowed text, the screen-height scale rule, and how numbers, money, times and titles are written; `modeName` and `mapName`. Phase C's code (found 2026-11-18); the menu uses it. |
| `PlayerCard` | The player card: avatar, prestige plate and title, name, LEVEL with the money, the XP bar, and the lifetime stats, all read from the Player's attributes. Shown by the scoreboard and the main menu. Phase C's code (found 2026-11-18). |
| `Scoreboard` | Held open with Tab: the match, the player's card and title picker (left and right arrows, `SetTitle`), and everyone in the server, best first. Replaces Roblox's player list. Phase C's code (found 2026-11-18, from its header). |
| `MatchHud` | Top centre of the HUD: the score bar (own score, the clock, the best rival in red) and what the server just paid this player. Phase C's code (found 2026-11-18, from its header). |
| `KillFeed` | The kill feed on the left edge (`KillFeed` remote). Phase C's code (found 2026-11-18, from its header). |
| `NameTags` | Name tags over other players: level, name, prestige and title; enemies' only up close and in line of sight. Phase C's code (found 2026-11-18, from its header). |
| `MatchEndScreen` | The end of a match: VICTORY, DEFEAT or MATCH OVER, the standings, what the match paid and the XP bar, then the level-up moment (`ProgressionEvent` "MatchEnd"). Phase C's code (found 2026-11-18, from its header). |

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
| `MenuRequest` | client → server | "Play" or "Leave", nothing else (2026-11-18) | Play: a loaded profile, no character, 10 s since leaving; Leave: alive, not hurt for 5 s, not in a Last Stand; one request each 0.5 s |
| `MenuResult` | server → owner | "Refused", the request, why (NotReady, Failed, Cooldown, Dead, UnderFire) | — |
| `ProgressionEvent`, `KillFeed` | server → owner / all | what was paid ("Reward", "MatchEnd"); each death | — (Phase C's code, found 2026-11-18) |
| `SetTitle` | client → server | a title id | the title is unlocked in the player's profile; 4 requests/s (Phase C's code, found 2026-11-18) |

## Character attributes (set by the server)
| Attribute | Meaning |
|---|---|
| `Stance`, `StanceSince` | Current stance and when it started (server time). |
| `HoldMode` | None, Secondary, Tertiary, Dual or Primary (OneA, OneB and Two until 2026-11-14). |
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

Gun models carry `WeaponId`, `Slot` (Primary, Secondary or Tertiary), `Place` (Right, Left, Holster or Dropped), `Limb`, `Ammo`, `Reserve`, `Reloading`, and on the floor `DroppedAt` (also the drop's token) or `RackId`.

## Player and match attributes (set by the server, since 2026-11-14)
| Where | Attribute | Meaning |
|---|---|---|
| Player | `Level`, `XP`, `Cash`, `Prestige` | Copies of the profile's values, for the menus and name tags to read. Changing them does nothing: the profile is on the server. |
| Player | `ProfileLoaded` | True once the profile is in memory. |
| Player | `ProfileOffline` | Studio only: the profile is kept in memory and not saved (Studio can't reach DataStores, or the load failed). |
| Player | `MatchScore`, `MatchKills`, `MatchDeaths` | This player's part in the match under way (kept from the last one until the next starts). |
| Player | `Title`, `Titles`, `Stat<name>` | The title shown, the titles unlocked (ids joined by commas), and each lifetime stat (`StatKills`…). Phase C's code (found 2026-11-18). |
| Player | `Deployed` | True while the player is in the fight (spawned, or dead and waiting to respawn); nil while in the main menu (`SpawnService`, 2026-11-18). |
| Player | `RedeployAt` | After leaving the match: the server time from which PLAY may put them back in. |
| `ReplicatedStorage.Match` | `State` | Waiting, Intermission or Running. |
| `ReplicatedStorage.Match` | `EndsAt` | When the intermission or match ends, as a server time (`Workspace:GetServerTimeNow()`); nil while waiting. |
| `ReplicatedStorage.Match` | `Mode`, `Map`, `Number` | FreeForAll, TestArena, and how many matches have started on this server. |
Set on each client only, never replicated: `LastShot` on the character (when this player last fired), `RestC0` on a gun's moving-part motors (their resting pose), `Flashes` on a muzzle (its flash counter).
Tags: `NotCover` (characters, dummies and dropped guns are never cover) and `Combatant` (non-player characters bullet time can slow).
`Workspace.MenuCams` (a Persistent model, 2026-11-18): the main menu camera's shots, per map (`MenuCams.TestArena.Shot1`…), each a Model with two invisible parts, From and To, and an optional `Fov` attribute. Place new shots by hand; `MenuRules.shots` reads them.

## Studio tools and test hooks
- `ServerStorage.Tools` (never reaches players): `AnimationImporter` builds the clips from Blender's export, and `TestHarness` records and measures play tests. Both are in the repo: `Assets/Blender/Animation/studio_import.luau` and `Tools/TestHarness.luau`. The game's own scripts are not in git, on purpose (the repo is public).
- `ServerStorage.Tools.ProfileCheats` (in the repo as `Tools/ProfileCheats.luau`): Studio-only cheats that set your own Level, XP, Cash and Prestige. Clone it into ServerScriptService for a play session, then `mp.profile({ Level = 20, Cash = 5000 })` from the harness ([[Test Arena]]). It stops at once outside Studio.
- `DebugMinPlayers`, `DebugLength` and `DebugIntermission` (numbers) on the `MatchService` module change the match's timings in Studio only: `DebugMinPlayers = 1` starts a match alone. Set them in play mode, so they aren't saved with the place. `DebugNpcKills = true` there makes the arena's dummies score and pay like players (Phase C's code).
- Characters only spawn when asked for (2026-11-18): in a play test press Enter on PLAY, or `mp.play()` from the harness; `mp.leave()` goes back to the menu.
- A Vector2 `DebugLook` attribute on the player (yaw and pitch in radians) points their camera, in Studio only. Automated play tests use it to aim. It only applies when the value changes.
- `DebugBulletTime = true` on any character activates its bullet time (it needs `Adrenaline`; a dummy needs an `Aim` toward its target).
- `StanceService._records` exposes the server's stance records to game scripts in Studio. The command bar's `require` makes its own copy of a module, so it can't see them.
