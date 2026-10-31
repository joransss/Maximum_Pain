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

## Not tested yet
Two real players, network lag, phones and tablets (there are no touch controls), the angled wall, the ledge dive, the line-of-sight failure in Last Stand, and Studio's Script Analysis (type warnings).

## Tips
In Studio only, a Vector2 `DebugLook` attribute on your player (yaw and pitch in radians) points the camera. Set it from the command bar to aim precisely.
