# Cover System

Contextual cover on a dedicated key: high and low cover, moving along walls, corners, popping out to aim, blind fire, and how the shoulder camera works with it. Built 2026-10-31.
Related: [[Movement State Machine]] · [[Weapons and Recoil]] · [[Test Arena]] · [[Max Payne 3 Mechanics Reference]] · [[Max Payne 3 Animation Reference]]

## Taking cover
- **E** (gamepad L1) takes the nearest wall in front of the camera. A HUD prompt shows when there is one: TAKE COVER HIGH or TAKE COVER LOW.
- A wall counts when it is near-vertical, within 3.5 studs of the character's centre, and at least **3 studs** tall. Characters, dummies and dropped guns never count.
- **High cover** reaches 5.2 studs above the floor and hides a standing character. **Low cover** is shorter (crates, low walls), and the character crouches behind it (head top about 3.5 studs, under a 3.6-stud wall).
- The character faces the wall and keeps what its body needs from it: how far the head, torso and upper arms reach toward the wall, plus 0.05. The upper arms count only below the cover's top, and not while firing, so blind fire and aiming over low cover don't push the body back.
  - **Low cover:** an R15 leaning over reaches 2.2 to 2.8 studs ahead of its root, depending on the avatar, so the root stays that far back and the head touches the wall. Keeping less pressed the head into the wall and slid the body along it.
  - **High cover:** at least 1.15. The side idles turn the body about 40° toward the side being worked, which brings the leading shoulder toward the wall, so on JackT6785's avatar the gap is 1.5 (working right, AK carried) to 1.8 (at the east end). At 1.15 the leading upper arm went half a stud into the wall (fixed 2026-11-04).
- That reach is remembered for each cover stance for as long as the character stays in cover. Ducking back from aiming over the wall uses the hunched reach straight away; measuring the upright pose made the body lunge 0.57 at the wall. It eases back toward what the pose needs (0.5 studs/s) once the character is settled, still and hasn't fired for 1.5 s. A slide leans further, and blind fire straightens the back, which mustn't pull the body in.
- **Arms and guns stay out of the wall:** the aim layer turns any arm that would go into it at the shoulder, just enough (see [[Animation Hooks]]). Popping up over low cover the gun comes up over the top as the body rises, and ducking back it lifts over the lip before dropping behind it.
- The server repeats the search from its own copy of the character's position and decides high or low itself.

## Moving along cover
- A and D (relative to the camera) slide along the wall: 9.6 studs/s behind high cover, 8 behind low.
- **Ends:** the character stops when the wall doesn't carry on 0.9 studs past its side.
- **High to low:** sliding from a tall section onto a short one switches to low cover, and back.
- **Inside corners** (a second wall ahead) turn onto the new wall automatically.
- **Outside corners:** keep pushing at an end for 0.35 s to swing round it, if the end face is at least about 2.3 studs wide (pillars and crates qualify; ordinary 2-stud walls don't). The way round is checked for obstacles and drops first. The search and the way round are measured from the character's real distance off the wall, so behind low cover the character also keeps its hunched distance off the new face. Until 2026-11-02 they assumed 1.15, so swinging round crates in low cover never happened.
- After either kind of corner the camera turns with it, so the same key keeps going the same way. Tested: holding D circled the 3.5-stud pillar, face by face.

## Leaving cover
Press E again, or pull away from the wall for 0.25 s. A sprint can't start in cover. The server stands the character up if the cover stops being valid for half a second (moved away, or the wall is gone).

## Aiming, peeking and firing
| Situation | What happens | Spread × |
|---|---|---|
| Hidden and firing (blind fire) | Low cover: the gun goes up over the top. High cover: round the edge, only at an end. In the middle of high cover the shots hit the wall. | 2.5 |
| Aim held (pop out) | Low cover: stand up over it. High cover: only at an end; the character steps out to 1.3 studs past it. The first 0.25 s is **peeking** and is shaky. | 1.5 |
| Aim settled (CoverAim) | Braced against the cover. | 0.85 |

- Letting go of aim ducks back in (at high cover, the character steps back to where it was). The step out and back walks no faster than reaches the spot by the next frame, so it can't overshoot (it went back and forth at low frame rates until 2026-11-04), and bullet time slows it.
- Trying to aim in the middle of high cover shows MOVE TO AN EDGE TO AIM, and the gun stays in the cover hold. Until 2026-11-04 the aim clip played anyway and raised the gun into the wall.
- Reloading works in every cover pose.
- Recoil: ×1.3 blind firing, ×0.8 braced.

### Muzzle obstruction
The server builds the gun's path from the body: chest, then shoulder, then muzzle (going over or round the cover for blind fire), and checks it against the world. Whatever is in the way takes the shot instead. A gun can't fire out of a wall, and the camera seeing over cover doesn't mean the gun can. The reticle shows a red cross when the path is blocked.

Tested: blind fire from the middle of the high wall hit the wall face; from its end, the shot went round the corner; popped up over low cover, a headshot landed on the dummy behind it; blind fire over the low wall reached the same dummy.

## Animations
| What | Clips |
|---|---|
| Hidden, idle | CoverHighLeft/Right, CoverLowLeft/Right (the side being worked) |
| Sliding | CoverHighMoveLeft/Right (9.6 studs/s), CoverLowMoveLeft/Right (8) |
| Outside corners | CoverCornerHighLeft/Right, CoverCornerLowLeft/Right. They start and end on the cover idle and hold their last frame while blending back into it. |
| Gun while hidden | High: CoverHoldHighOne/Two/Dual, the gun up close to the chest. Low: CoverHoldLowOne (pistol by the right knee), CoverHoldLowDual, and CoverHoldLowTwoLeft/Right (the rifle low across the front, one per side because the body turns 24° each way). |
| Carried rifle | CarryTwoHandedCover beside the left leg behind high cover, CarryTwoHandedLow behind low cover |
| Blind fire | BlindFireHighLeft/Right (right arm only, round the end), BlindFireLowLeft/Right (right arm and waist, up over the top) |
| Popped out | CoverAim, AimPistol/AimRifle/AimDual |

Max Payne 3 holds the gun low in cover, and an R15's chest lies on its thighs when hunched, so the low holds are a crouched low ready. A raised gun beside the face isn't possible. An R15 arm only reaches the top of a wall about 3.7 studs tall from the crouch. Blind fire over a 3.6 wall clears the top by 0.26 to 0.30; over anything taller the gun stays below the top.

## Camera
- The shoulder follows the side being worked: moving left puts the camera on the left shoulder; popping out at an edge puts it on that edge's side.
- **Q** still swaps shoulders at any time.
- When the hips drop (crouch, low cover), the camera only drops a quarter as far, so it can see over low cover.

## Server checks
- Entering: the server finds the cover itself; no cover, no stance.
- Every 0.2 s: the wall must still be there (with more slack while popped out). Height changes switch between high and low; half a second without cover stands the character up.
- Popping out of high cover needs an edge at the server's position.
- Firing uses the server's position, stance and cover for the gun's path.

## Numbers
- `CoverRules`: REACH 3.5 · GAP 1.15 · LOW_PROBE 3 · HIGH_PROBE 5.2 · EDGE_MARGIN 0.9 · PEEK_CLEAR 1.3 · CORNER_HOLD 0.35.
- `CoverController`: the gap is the body's reach toward the wall (head, torso, and the upper arms below the top when not firing) + 0.05, at least GAP, with a 0.08 deadband. The reach eases back at REACH_RELAX 0.5 studs/s once settled for REACH_SETTLE 0.4 s and not fired for FIRED_HOLD 1.5 s. Stepping out of high cover: STEP_SPEED 10, done within STEP_DONE 0.05.
- The pop-out settle time (0.25 s) is in `StanceService` and `CharacterController`.
- Space in low cover vaults over the wall ([[Movement State Machine]], Vaulting).

## Tested (2026-11-02)
- **Low wall:** sliding stops 0.74 to 0.85 from each end. Popping up doesn't move the root, and ducking back holds the gap (2.54). After a slide the head eases back to within 0.13 of the wall, with nothing more than 0.05 into it.
- **Crate:** pushing at its end swings round two corners in a row, without touching it.
- **High wall:** blind fire from the end leaves from round the corner. Popping out carrying the AK keeps the AK at least 1.29 off the wall. Details in [[Animation and MP3 Systems - Progress and To Do]].

## Tested (2026-11-04)
- **Low wall:** popping up and ducking back, nothing goes more than 0.05 into the wall (the gun went 0.73 and 0.56 in before). The gap stays 2.52.
- **High wall:**
  - At rest on either side, nothing is in the wall (the leading arm went up to 0.55 in before).
  - Aim held mid-wall keeps the cover hold.
  - Stepping out round the east end is clear. Stepping back, a 0.1 s brush (0.20).
- Details in [[Animation and MP3 Systems - Progress and To Do]] (session 4).

## Decided
- **Low cover pose:** keep the hunched pose facing the wall (JackT6785, 2026-11-04). Side-on like Max Payne 3 would have meant remaking 12 clips and the wall-end logic.

## Not done
- **Tall low cover:** blind fire over low cover taller than about 3.7 can't reach the top.
- **High cover, stepping back to the edge:** for about 0.2 s, while the edge idle blends back in, the leading upper arm reaches up to 0.43 into the wall before settling.
