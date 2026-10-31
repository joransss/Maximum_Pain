# Cover System

Contextual cover on a dedicated key: high and low cover, moving along walls, corners, popping out to aim, blind fire, and how the shoulder camera works with it. Built 2026-10-31.
Related: [[Movement State Machine]] · [[Weapons and Recoil]] · [[Test Arena]] · [[Max Payne 3 Mechanics Reference]] · [[Max Payne 3 Animation Reference]]

## Taking cover
- **E** (gamepad L1) takes the nearest wall in front of the camera. A HUD prompt shows when there is one: TAKE COVER HIGH or TAKE COVER LOW.
- A wall counts when it is near-vertical, within 3.5 studs of the character's centre, and at least **3 studs** tall. Characters, dummies and dropped guns never count.
- **High cover** reaches 5.2 studs above the floor and hides a standing character. **Low cover** is shorter (crates, low walls), and the character crouches behind it (head top about 3.5 studs, under a 3.6-stud wall).
- The character keeps 1.15 studs from the wall and faces it.
- The server repeats the search from its own copy of the character's position and decides high or low itself.

## Moving along cover
- A and D (relative to the camera) slide along the wall: 9.6 studs/s behind high cover, 8 behind low.
- **Ends:** the character stops when the wall doesn't carry on 0.9 studs past its side.
- **High to low:** sliding from a tall section onto a short one switches to low cover, and back.
- **Inside corners** (a second wall ahead) turn onto the new wall automatically.
- **Outside corners:** keep pushing at an end for 0.35 s to swing round it, if the end face is at least about 2.3 studs wide (pillars and crates qualify; ordinary 2-stud walls don't). The way round is checked for obstacles and drops first.
- After either kind of corner the camera turns with it, so the same key keeps going the same way. Tested: holding D circled the 3.5-stud pillar, face by face.

## Leaving cover
Press E again, or pull away from the wall for 0.25 s. A sprint can't start in cover. The server stands the character up if the cover stops being valid for half a second (moved away, or the wall is gone).

## Aiming, peeking and firing
| Situation | What happens | Spread × |
|---|---|---|
| Hidden and firing (blind fire) | Low cover: the gun goes up over the top. High cover: round the edge, only at an end. In the middle of high cover the shots hit the wall. | 2.5 |
| Aim held (pop out) | Low cover: stand up over it. High cover: only at an end; the character steps out to 1.3 studs past it. The first 0.25 s is **peeking** and is shaky. | 1.5 |
| Aim settled (CoverAim) | Braced against the cover. | 0.85 |

- Letting go of aim ducks back in (at high cover, the character steps back to where it was).
- Trying to aim in the middle of high cover shows MOVE TO AN EDGE TO AIM.
- Reloading works in every cover pose.
- Recoil: ×1.3 blind firing, ×0.8 braced.

### Muzzle obstruction
The server builds the gun's path from the body: chest, then shoulder, then muzzle (going over or round the cover for blind fire), and checks it against the world. Whatever is in the way takes the shot instead. A gun can't fire out of a wall, and the camera seeing over cover doesn't mean the gun can. The reticle shows a red cross when the path is blocked.

Tested: blind fire from the middle of the high wall hit the wall face; from its end, the shot went round the corner; popped up over low cover, a headshot landed on the dummy behind it; blind fire over the low wall reached the same dummy.

## Camera
- The shoulder follows the side being worked: moving left puts the camera on the left shoulder; popping out at an edge puts it on that edge's side.
- **Q** still swaps shoulders at any time.
- When the hips drop (crouch, low cover), the camera only drops a quarter as far, so it can see over low cover.

## Server checks
- Entering: the server finds the cover itself; no cover, no stance.
- Every 0.2 s: the wall must still be there (with more slack while popped out). Height changes switch between high and low; half a second without cover stands the character up.
- Popping out of high cover needs an edge at the server's position.
- Firing uses the server's position, stance and cover for the gun's path.

## Numbers (`CoverRules`)
REACH 3.5 · GAP 1.15 · LOW_PROBE 3 · HIGH_PROBE 5.2 · EDGE_MARGIN 0.9 · PEEK_CLEAR 1.3 · CORNER_HOLD 0.35. The pop-out settle time (0.25 s) is in `StanceService` and `CharacterController`.

## Not done
- No vaulting over low cover (Max Payne 3 has it).
- No cover-to-cover moves.
- No animations: the body faces the wall while hidden and sinks into the floor behind low cover.
