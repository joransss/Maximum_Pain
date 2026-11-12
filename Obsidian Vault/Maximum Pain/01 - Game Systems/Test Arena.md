# Test Arena

A test area just north of the spawn (`Workspace.TestArena`) with geometry for every system in this milestone. Built 2026-10-31.
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
- **TargetBehindLow** (behind the low wall), **TargetOpen** and **TargetFar**: plain avatars with limb health. They come back 5 s after dying.
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
`ServerStorage.Tools.TestHarness` (in the repo as `Tools/TestHarness.luau`) records play tests frame by frame and measures them: boxes against the floor and against an obstacle (exact depth), clearance over a top, camera steps, the clip timeline. It can also walk the character, point the camera and frame screenshots. Install it once per play session (see its header):
- Server: `game.ServerStorage.Tools.TestHarness:Clone().Parent = game.ReplicatedStorage`
- Client: `_G.mp = require(game.ReplicatedStorage:WaitForChild("TestHarness"))`

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
