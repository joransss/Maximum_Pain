# Test Arena

A test area just north of the spawn (`Workspace.TestArena`) with geometry for every system in this milestone. Built 2026-10-31.
**Studio only since 2026-11-21:** the gun table, the dummies and the gunman (the `TestArena` script) run only in Studio, a 2-player Studio test included. On a live server the gun table would hand out guns locked by level or price, and the dummies would fill adrenaline meters, so there the arena is just a map. `LIVE = true` at the top of the script puts them back on live servers.
Related: [[Cover System]] · [[Shoot-Dodge]] · [[Last Stand and Bullet Time]] · [[Loadout and Dual Wielding]] · [[Movement State Machine]]

## Layout (south to north)
| Area | Where | For testing |
|---|---|---|
| Gun table | z 70 | All 13 guns lie on it as pickups (F). A taken gun comes back after 15 s. |
| High wall (14 × 8) | x -30, z 86 | High cover, both ends, popping out, blind fire round the end |
| Low wall (14 × 3.6) | x -10, z 86 | Low cover, popping up, blind fire over the top |
| High-to-low wall | x 8 to 16, z 86 | Sliding from high cover onto low cover |
| Inside corner (L shape) | x 35 to 42, z 81 to 86 | Turning onto the second wall |
| Pillar (3.5 × 3.5 × 8) | x 0, z 100 | Swinging round outside corners |
| Crates (3.8 tall) | x -45, z 100 | Low cover; outside corners on crates |
| Angled wall (30°) | x 28, z 104 | Cover and dive slides on a slanted wall |
| Dive lane | x 0, z 113 to 146 | Open floor ending in a 10-stud wall, for head-on dives |
| Ledge and ramp | x -40, z 108 to 138 | Diving off a 6-stud ledge |
| Crouch tunnel (4 studs high) | x 50, z 115 to 135 | Crouching under a low roof; NO ROOM TO STAND |

Red markers show where the dummies stand. Each area has a floating label.

A large block that isn't part of the arena's plan, `Workspace.Part` (4 × 18 × 18, x 30 to 34, z 38 to 56), stands north of the spawn (found 2026-11-07). Walk round it by (38, 38) and (38, 77).

## Dummies
- **TargetBehindLow** (behind the low wall), **TargetOpen** and **TargetFar**: plain avatars with limb health. They come back 5 s after dying. Since 2026-11-20 a hurt dummy heals like a player (Medium: 4 s after the last hit, 4% of a limb a second, only out of the red), so measure damage within 4 s of the hit.
- **Gunman** (holding an AK): press **T** at it to make it hostile for 20 s. It turns to the nearest player in sight and hits their torso for 18 every 0.8 s (slowed by bullet time). This is how to test Last Stand alone.

## Test log (2026-10-31, Studio play mode)
| Feature | Result |
|---|---|
| Crouch | Hips 2.23 → 0.43, walk speed 8.8, no jumping. Under the tunnel C stays crouched and shows NO ROOM TO STAND. |
| Sprint | 24 studs/s. The trigger ends it without firing; the next click fires. |
| Dual wield | 4 dropped the AK (with a pickup prompt); M9 right, Uzi left; firing alternates hands; the 3 s dual reload topped both guns up correctly. |
| Pickups | Picking the AK up while dual wielding ended dual wielding. SWAP M9 FOR DESERT EAGLE swapped them and left the M9 (13 rounds) on the table. |
| Reloads | Cut off by a switch: no ammo moved. Completed: 7/5. |
| High cover | 1.15 studs from the wall, facing it; stops at the ends; pops out to 1.37 past the end; ducks back to the same spot. |
| Corners | The inside corner turned onto the second wall; holding D circled the pillar. |
| Firing from cover | Aimed shots from the high wall's end killed TargetFar. Blind fire round the end cleared the wall; blind fire mid-wall hit the wall. |
| Low cover | Head top 3.49 under a 3.6 wall. A pop-up headshot hit the dummy behind; blind fire over the top reached it. |
| Shoot-dodge | Forward 17 studs, 1.6 high, about 0.5 s in the air. Sideways and backward dives. A head-on dive stopped at the end wall. A movement key gets up. |
| Last Stand | See [[Last Stand and Bullet Time]]. |
| Arms | Right arm in the red ended dual wielding; a painkiller restored it. |
| Speed check | A faked 200 studs/s run was pulled back by the server. |

No errors appeared in the output during the tests.

## Test log (2026-11-02, Studio play mode, with animations)
| Feature | Result |
|---|---|
| Vaults | LowWall from standing and out of low cover, and CrateA: legs clear the top (+0.16 to +0.23), no Fall clip, no bounce, smooth camera. In bullet time: 1.40 s in the air at 0.3. |
| Dives | Back, left and right: 17.9 studs, feet clear at the launch, steady camera on landing, a full turn while lying stays off the floor. |
| Last Stand | Gunman hostile, four shots during the window: survived. Drop and wakeup move the root at once; feet within 0.05. |
| Guns | All 13 guns and the dual reload: right clip, right parts, nothing stuck. Pickups ×14, a painkiller, drops in the open, against the table and swapped on the rack. |
| Low cover | LowWall slides and ends, two corner swings round CrateA, popping up and back with a steady gap. |
| High cover | Blind fire round the HighWall's end; popping out carrying the AK. |
| Output | Clean. |

Details and the before/after numbers: [[Animation and MP3 Systems - Progress and To Do]].

## Test log (2026-11-07, Studio play mode, side-on cover, 83tg's avatar)
| Feature | Result |
|---|---|
| Low wall | Head top 2.77 (0.83 under the top); back on the wall (root 1.21 off it); at the ends the head stays 0.47 inside; blind fire clears the top by 0.11 with the head 0.34 under it |
| High wall | At the ends the head stays 0.39 inside; blind fire round the end (1.07 past it working left, at the corner working right); popping out and back |
| CrateA | Outer corner swings clean; the inside-corner snap into the next crate went 1.1 into CrateA for about 3 frames (to-do 4.16) |
| Vault out of low cover | Clears; one frame of a foot in the wall (to-do 4.15) |
| Output | Clean |

## Test log (2026-11-08, Studio play mode, 83tg's avatar)
| Feature | Result |
|---|---|
| Low wall: popping up and ducking back, both sides | The turn clips play; no leg in the wall; a shin 0.08 under the floor for one frame at most; the gun 0.05 in the wall's face as it comes up |
| Low wall: sliding, starting and stopping | Feet on the floor (within 0.05); the trailing shin, thigh and the holstered Uzi still go 0.33 under it (to-do 4.20) |
| Low wall: blind fire while sliding | The gun swings 2.7 out from the wall, pointing back along it, until the slide stops (to-do 4.19). Hold blind fire for a test by setting the character's `LastShot` attribute to `os.clock() + 25` on the client |
| Output | Clean |

To work the left side without moving along the wall (the move's floor dips would cloud the numbers), press Q before E: the cover side starts on the camera's shoulder.

## Test harness
**Since 2026-11-18 a play test starts in the main menu, with no character:** press Enter on PLAY (or click it), or call `mp.play()` from the harness, which asks the server the way the menu does and waits for the character. `mp.leave()` goes back to the menu (refused within 5 s of a hit), and PLAY then waits 10 s. While in the menu, the camera dollies through four shots of the arena (`Workspace.MenuCams.TestArena`).

`ServerStorage.Tools.TestHarness` (in the repo as `Tools/TestHarness.luau`) records play tests frame by frame and measures them: boxes against the floor and against an obstacle (exact depth), clearance over a top, camera steps, the clip timeline. It can also walk the character, point the camera and frame screenshots. Install it once per play session (see its header):
- Server: `game.ServerStorage.Tools.TestHarness:Clone().Parent = game.ReplicatedStorage`
- Client: `_G.mp = require(game.ReplicatedStorage:WaitForChild("TestHarness"))`

**Profile cheats** (since 2026-11-14; Studio only): also on the server, `game.ServerStorage.Tools.ProfileCheats:Clone().Parent = game.ServerScriptService` (in the repo as `Tools/ProfileCheats.luau`). Then on the client `mp.profile({ Level = 20, Cash = 5000, Prestige = 1 })` sets your own profile's values (XP goes back to 0 with a new level), `mp.profile({ Reset = true })` starts it afresh and `mp.profile()` reports it. Values the rules don't allow (level 51, negative cash) are refused.

**A match alone:** in play mode, on the server, `game.ServerScriptService.MatchService:SetAttribute("DebugMinPlayers", 1)` starts matches with one player, once they have pressed PLAY (players in the menu don't count); `DebugIntermission` and `DebugLength` (seconds) shorten them. `DebugNpcKills = true` makes the dummies score and pay like players, and `DebugMinContestants = 1` lets the match be won alone (a match otherwise needs two players who fought; since 2026-11-19). Read the match from `game.ReplicatedStorage.Match`'s attributes and `mp.progress()`.

**Phase D tests** (since 2026-11-20; the results are in [[Changelog]]):
- **Loadouts:** pick one in the menu (LOADOUT), or fire the remotes from a client test: `game.ReplicatedStorage.Remotes.SetLoadout:FireServer(1, { Primary = "AR_A_AK47", Secondary = "HeavyPistol_A_DesertEagle" })`, `SelectLoadout:FireServer(1)`, `BuyItem:FireServer("HeavyPistol_A_DesertEagle")` (level and Cash from `mp.profile` first). Refusals come back on `LoadoutEvent` ("Refused", the request, why). Past a short burst (3 saves or selections, 2 purchases, 1 filtered name) the server refuses with "TooFast" until its rate allows another (`ArmoryService`'s `RATES`).
- **Stamina:** the server's count is `StanceService._records[character].stamina` (read it from a test Script in the game's VM) and the `Stamina` attribute in tenths; the client's is `CharacterController.stamina()` (from a test LocalScript under PlayerGui).
- **Regeneration:** `LimbService.damage(character, "RightLeg", 60)` from a test Script puts the leg in the red, where it stays; `LimbService.usePainkiller(character)` lifts it out, and it heals on.
- **Weight class:** the `LoadoutWeight` and `WeightClass` attributes on the character; 4 (dual wield) drops the AK and makes a CUSTOM 1 Light, F picks it back up.
- **The death screen** needs the M (or Select) press inside the 3 s before the respawn: the tools' delays between calls are longer, so do the death and the press in one input sequence (a test LocalScript under PlayerGui that kills on a key; it is cleared at each respawn).
- **Screen sizes:** `StudioDeviceSimulatorService` (Edit mode, before Play) with a custom device of 1920 × 1080 or 1024 × 768; `StopSimulationAsync()` afterwards.
- **The speed check:** `StanceService._records[character].moveBank` is the distance left before a pull-back (a second of the stance's speed plus 4 studs when full); sample it every half second from a test Script, with the root's speed. A cheating client is a test LocalScript under PlayerGui that pushes the root on `RunService.Heartbeat` (`root.CFrame += humanoid.MoveDirection * extra * dt`); since 2026-11-21 setting `Humanoid.WalkSpeed` from a script no longer speeds the character up in Studio (it did on 2026-11-20). Network lag: `settings().Network`'s six values (`InboundNetworkMinDelayMs`, `…JitterMs`, `…LossPercent` and the Outbound ones; Studio's "Bad Connection (3G)" is 150/70/0.5 in, 180/90/0.5 out), live during a play test; read them first, and put them back afterwards (they persist across Studio sessions). `mp.look(math.pi / 2)` faces −X, where the arena's floor runs 300 studs clear from the spawn. To move the character from a test Script (`PivotTo`), call `StanceService.moved(character)` first, or the check puts it back.
- **The mouse in the menus:** the Studio MCP's `user_mouse_input` counts from below Roblox's top bar (58 pixels in Studio's window), so aim 58 pixels above where a screenshot shows the row.

**Phase E tests** (since 2026-11-21; the results are in [[Changelog]]):
- **Buying:** `mp.profile({ Level = 50, Cash = 30000 })`, then from a client test `Remotes.BuySkill:FireServer("skill_heavy_hand")` and `Remotes.BuyItem:FireServer("item_riot_helmet")`, 0.6 s apart (both count against one rate: 2 at once, then one each 0.5 s). Refusals come back on `LoadoutEvent`.
- **A loadout with items and a skill:** `Remotes.SetLoadout:FireServer(2, { Primary = "AR_A_AK47", Secondary = "LightPistol_A_M9", Tertiary = "SMG_B_Uzi", Head = "item_riot_helmet", Chest = "item_heavy_plates", Gear = "item_pill_case", Skill = "skill_heavy_hand" })`, `SelectLoadout:FireServer(2)`, `mp.play()`. Painkillers, spare magazines and the weight are set at a spawn only, so test those with a real spawn.
- **Firing a skill:** set the character's `Adrenaline` from the server (a third is one segment), then `Remotes.SkillRequest:FireServer()` from a client test, or X. To try another skill on the same character, `SkillService.setup(player, character, id)` from a game-VM Script (the profile must own a skill with a price). `ActiveSkill`, `ActiveSkillLevel` and `ActiveSkillEnds` show it running; `SkillEvent` says "Used" or why not.
- **Items on a live character:** `StatusEffects.setup(character, { Head = ..., Chest = ..., Gear = ... })` from a game-VM Script swaps them for what they do now (regeneration, reloads and draws, the Stopwatch, the Pacemaker, the Ammo Pouch in a Last Stand).
- **Armour:** put items on a dummy the same way (`StatusEffects.setup(dummy, { Chest = "item_plate_carrier" })`; it comes back without them when it dies), stand 12 studs in front of TargetOpen at (10, 3.35, 108) facing it (`StanceService.moved` first) and `mp.shoot("TargetOpen", "UpperTorso", 1)`; behind it is (10, 3.35, 132). The gunman's hits on the player go through the same rules (18 a hit; 12.06 through Heavy Plates from in front). Set the gunman's `Hostile` attribute for a few hits only, and heal the torso between tests: it kills.
- **Keep a test Script alive until what it started has finished:** destroying a Script kills every thread it started, including the game's (a Last Stand begun by its `LimbService.damage` never ended once the Script was gone).
- **Gut Feeling's markers** are BillboardGuis, which Studio's screenshots don't draw: check them by their properties and `camera:WorldToViewportPoint`.
- **`DebugLook` only applies when its value changes**, so after a respawn set a slightly different value, or the camera keeps facing −Z.

**Phase F tests** (since 2026-11-22; the results are in [[Changelog]]):
- **What's on sale:** `ShopConfig.stock(os.time())` (from any script: `.featured`, `.daily[1]`, `.daily[2]`, and when each changes); `ShopConfig.stock(t)` for any UTC time `t` shows that day's. The daily skins change at 00:00 UTC, the featured one at 00:00 UTC on Mondays.
- **Buying and opening:** `mp.profile({ Cash = 200000 })`, then from a client test `Remotes.BuySkin:FireServer(skinId)` (a skin on sale) and `Remotes.OpenCrate:FireServer("crate_gunsmith")`, 0.6 s apart (both count against one rate: 2 at once, then one each 0.5 s). The answers come on `ShopEvent`: "Bought", "Opened" (the crate, the skin, what was paid, whether in order), "Refused" (the request, why), and "State" after every change. A crate's 18 skins come in 18 opens (fewer once some are owned); the next is refused, Complete. The shop screen also sends whether it showed the crate opening in order (`OpenCrate:FireServer(id, true)`); a test may leave it out, but a wrong one is refused, Changed.
- **Crates held:** nothing hands them out yet, so put some in the profile from a game-VM Script: `ProfileService.update(player, function(draft) draft.Crates.crate_street = 2 end)`. An open uses one before any Cash; once the crate is complete the rest are refunded ("Refunded"), and so are any found as the profile loads.
- **In order** (as where Roblox restricts random items): `game.ServerScriptService.ShopService:SetAttribute("DebugCratesInOrder", true)` on the server in play mode. The crate screen then shows ORDER and the next skin by name, and opens give the crate's skins in their shown order. (A real player's first "State" also says in order until `PolicyService` answers.)
- **Equipping:** `Remotes.EquipSkin:FireServer("AR_A_AK47", "skin_ak47_stainless")`, or `""` to take it off. It shows from the next spawn: the gun's `Skin` attribute, and a `SurfaceAppearance` named SkinFinish on each part it dresses.
- **The odds and the roll** are pure functions: `ShopConfig.odds(crateId, owned)` and `ShopConfig.roll(crateId, owned, Random.new(seed))`, with `owned` a set of skin ids (`ShopConfig.set({...})`); run them in bulk from a game-VM Script.

## Not tested yet
Two real players, network lag, phones and tablets (there are no touch controls), the angled wall, the ledge dive, the line-of-sight failure in Last Stand, and Studio's Script Analysis (type warnings).

## Test log (2026-11-09, Studio play mode, 83tg's avatar)
| Feature | Result |
|---|---|
| Low wall: blind fire while sliding, both ways (held, and real shots) | The run's own blind fire clip: the gun over the top and pointing across, the head under it, nothing in the wall |
| Low wall: starting, stopping, reversing while firing | Clean; going right the gun dips into the hold and comes up again |
| Low wall: dual pistols, a rifle | The Uzi and the rifle rest on the wall (0.05) |
| High wall: blind fire while sliding, with a rifle | The gun turns back along the wall on the run (to-do 4.25); the rifle goes 1.9 into the wall (to-do 4.26) |
| Output | Clean |

## Test log (2026-11-10, Studio play mode, 83tg's avatar)
| Feature | Result |
|---|---|
| Vaults with the AK carried: standing, running, sprinting | The AK rests on the top edge (0.05); before the arm guard fix it went 0.33 into it |
| Running vaults | Accepted by the server (refused before `SERVER_SLACK` 7.5, and the body dropped onto the wall) |
| High cover, stepping out and back at both ends | No upper arm in the wall; forearm 0.09 |
| High wall: blind fire while sliding, both ways and reversing (M9, AK-47, dual) | The run's own clip, the gun straight out ahead along the wall; nothing in the wall; on a reversal the gun dips into the hold |
| Bullet time near TargetOpen: the player's own, the dummy's (`DebugBulletTime`), a counter-activation | As [[Last Stand and Bullet Time]] said: the activator at full speed, those in sight at 0.3, the aim penalty cleared by an equal level, free behind the pillar. After the change the same day, the activator at 0.6 (back to full speed in a Last Stand) |
| Output | Clean |

## Test log (2026-11-10, late, Studio play mode, 83tg's avatar)
| Feature | Result |
|---|---|
| High wall: blind fire with a long gun (AK-47, FAL, M107), mid-wall, at both ends, sliding, reversing | The two-handed clips: both hands on the gun throughout, nothing in the wall (0.05 for 2 physics frames on a reversal), the muzzle 1.9 past the ends. Before: the arm swung about 50° round mid-wall, the support arm 0.44 into the end's corner, the support hand off the gun working left and sliding |
| Output | Clean |

## Tips
- In Studio only, a Vector2 `DebugLook` attribute on your player (yaw and pitch in radians) points the camera. Set it from the command bar to aim precisely; it only applies when the value changes.
- **Getting slowed by bullet time:** give a dummy `Adrenaline = 1` and an `Aim` facing you, then set `DebugBulletTime = true` on it (5 s per activation).
- **Picking up a gun:** the F prompt is the one nearest the crosshair, so point the camera at the gun you want (aim from the camera's own position: the shoulder camera is off to one side).
- **Moving around:** don't teleport the character, since the server's speed check moves it back; walk instead. The walls at z 85 to 87 have gaps at x −23 to −17 and −3 to 4, and the gun table blocks x −28 to 28 at z 70.
