# Cover System

Contextual cover on a dedicated key: high and low cover, moving along walls, corners, popping out to aim, blind fire, and how the shoulder camera works with it. Built 2026-10-31; side-on poses since 2026-11-07.
Related: [[Movement State Machine]] · [[Weapons and Recoil]] · [[Test Arena]] · [[Max Payne 3 Mechanics Reference]] · [[Max Payne 3 Animation Reference]]

## Taking cover
- **E** (gamepad L1) takes the nearest wall in front of the camera. A HUD prompt shows when there is one: TAKE COVER HIGH or TAKE COVER LOW.
- A wall counts when it is near-vertical, within 3.5 studs of the character's centre, and at least **3 studs** tall. Characters, dummies and dropped guns never count.
- **High cover** reaches 5.2 studs above the floor and hides a standing character. **Low cover** is shorter (crates, low walls), and the character crouches behind it (head top about 2.8 studs, under even the lowest 3-stud cover).
- **Side-on, as Max Payne 3** (since 2026-11-07): the back and the inner shoulder are against the wall, the body turned toward the edge being worked, the head looking along the wall to it. Behind low cover the character squats with the back to the wall, folded over the knees to keep the head down. The footage this follows is in [[Max Payne 3 Animation Reference]].
- The root part faces the wall; the cover clips turn the body round inside it. The game keeps the gap the body's reach toward the wall needs: the head, torso and upper arms below the top, + 0.05, at least 1.15 (`GAP`). The clips lean the body back until that reach is 1.1, so the gap comes out at 1.15 and the back rests on the wall. Avatars differ, so it's measured, not assumed.
- That reach is remembered for each cover stance for as long as the character stays in cover, so popping up and ducking back don't make the body lunge at the wall. It eases back toward what the pose needs (0.5 studs/s) once the character is settled, still and hasn't fired for 1.5 s.
- The server repeats the search from its own copy of the character's position and decides high or low itself.

## Moving along cover
- A and D (relative to the camera) slide along the wall: 9.6 studs/s behind high cover, 8 behind low. The body runs side-on, facing the way it goes: a hunched jog behind high cover, a crouched run behind low cover with the head under 3 studs.
- **Ends:** the character stops when the wall doesn't carry on 0.9 studs past its side. The idles sit back along the wall, away from the edge (0.35 high, 0.75 low), so at an end the head is about 0.4 inside it and only the edge-side arm shows past it (about 0.3).
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

- Letting go of aim ducks back in (at high cover, the character steps back to where it was).
- Trying to aim in the middle of high cover shows MOVE TO AN EDGE TO AIM.
- Reloading works in every cover pose.
- Recoil: ×1.3 blind firing, ×0.8 braced.

### Muzzle obstruction
The server builds the gun's path from the body: chest, then shoulder, then muzzle (going over or round the cover for blind fire), and checks it against the world. Whatever is in the way takes the shot instead. A gun can't fire out of a wall, and the camera seeing over cover doesn't mean the gun can. The reticle shows a red cross when the path is blocked.

Tested: blind fire from the middle of the high wall hit the wall face; from its end, the shot went round the corner; popped up over low cover, a headshot landed on the dummy behind it; blind fire over the low wall reached the same dummy.

## Animations
| What | Clips |
|---|---|
| Hidden, idle | CoverHighLeft/Right (back and inner shoulder on the wall, turned 150° toward the edge), CoverLowLeft/Right (squatting, back to the wall, folded over the knees, head along the wall to the edge). One per side worked. |
| Sliding | CoverHighMoveLeft/Right (a side-on jog, 9.6 studs/s), CoverLowMoveLeft/Right (a crouched side-on run, 8) |
| Outside corners | CoverCornerHighLeft/Right, CoverCornerLowLeft/Right: a side-on stride round the corner. They start and end on the cover idle and hold their last frame while blending back into it. |
| Gun while hidden | High: CoverHoldHighOne (the pistol low in front of the belly, muzzle down), CoverHoldHighTwo (the rifle upright across the chest), CoverHoldHighDual (both pistols up in front of the chest). Low: CoverHoldLowOne and CoverHoldLowDual (the gun up beside the face), CoverHoldLowTwoLeft/Right (the rifle upright past the face, leaning away from the edge). |
| Carried rifle | CarryTwoHandedCover (muzzle down in front of the left thigh) behind high cover, CarryTwoHandedCoverLow (by the knee, muzzle forward and down) behind low cover |
| Blind fire | BlindFireHighLeft/Right (the gun arm out along the wall and round the end; working right the arm reaches across, the chest leaning out), BlindFireLowLeft/Right (the chest twists the gun shoulder to the wall and the arm goes straight up, the gun over the top, the head ducked). Sliding along low cover: BlindFireLowMoveLeft/Right, made on the run (the chest leans the gun shoulder up, the arm goes straight up, the gun across the wall); going right it never cross-fades with another blind fire clip, it dips into the hold first. Sliding along high cover: BlindFireHighMoveLeft/Right, made on the run (the gun arm straight out ahead along the wall, the barrel level); the two dip into the hold on a reversal. A two-handed gun behind high cover has its own: BlindFireHighTwoLeft/Right (both hands on it across the body, pointing toward the edge and turned round it; working left the chest turns to the corner) and BlindFireHighMoveTwoLeft/Right (ahead along the wall on the run). All key the waist and neck too. |
| Popping up and ducking back (low) | CoverPopUpLeft/Right (0.25 s): the body rises, leaves the wall and turns round toward the edge to face over it, the feet stepping round. CoverDuckLeft/Right (0.3 s): it turns and folds over first, and goes down once the feet are round. The gun comes up 0.15 s into a pop-up. |
| Popped out | CoverAim (the back heel up), AimPistol/AimRifle/AimDual |

Max Payne 3 holds the gun low or upright in front while hidden, back to the wall. An R15's head and torso are long for its legs, so behind low cover it has to fold far over its knees to get its head under the top. Folded, its shoulders are 2 studs out from the wall, too far to blind fire over the top with the back to the wall, so low blind fire twists the chest round instead. That clears a 3.6 wall by 0.39 on the default R15 (0.11 on a slim avatar) with the head 0.3 under it.

## Camera
- The shoulder follows the side being worked: moving left puts the camera on the left shoulder; popping out at an edge puts it on that edge's side.
- **Q** still swaps shoulders at any time.
- When the hips drop (crouch, low cover), the camera only drops a quarter as far, so it can see over low cover.
- While hidden, the head doesn't look where the camera aims (the aim is past the wall, behind the turned head); it keeps the clip's look along the wall, and eases back onto the aim when popping out.

## Server checks
- Entering: the server finds the cover itself; no cover, no stance.
- Every 0.2 s: the wall must still be there (with more slack while popped out). Height changes switch between high and low; half a second without cover stands the character up.
- Popping out of high cover needs an edge at the server's position.
- Firing uses the server's position, stance and cover for the gun's path.

## Numbers
- `CoverRules`: REACH 3.5 · GAP 1.15 · LOW_PROBE 3 · HIGH_PROBE 5.2 · EDGE_MARGIN 0.9 · PEEK_CLEAR 1.3 · CORNER_HOLD 0.35.
- `CoverController`: the gap is GAP or the body's reach toward the wall + 0.05, whichever is more, with a 0.08 deadband. The reach eases back at REACH_RELAX 0.5 studs/s once settled for REACH_SETTLE 0.4 s and not fired for FIRED_HOLD 1.5 s.
- The cover clips (`mp_stances.py`): HIGH_TURN 150° · LOW_TURN 180° · BACK_REACH 1.1 · HIGH_BACK 0.35 · LOW_BACK 0.75. The low cover turns: POP_TIME 0.25 · DUCK_TIME 0.3 · TURN_SWAY 0.6 · KNEE_FOLLOWS_FOOT 0.75 · DUCK_DROP 0.2–1 · DUCK_FOLD 0–0.7 · LEG_REACH 1.15.
- `AnimationController`: TURN_FADE 25 (the turns take the body over) · POP_AIM 0.15 s (the gun stays in the low hold) · DIP_FADE 50 (blind fire on the run going right goes down into the hold before another blind fire clip comes up).
- The pop-out settle time (0.25 s) is in `StanceService` and `CharacterController`.
- Space in low cover vaults over the wall ([[Movement State Machine]], Vaulting).

## Tested (2026-11-07, side-on, 83tg's avatar)
- **Low wall:** head top 2.77, 0.83 under the top; root 1.21 off the wall; nothing in the wall or floor. At the ends the head is 0.47 inside and the edge-side arm 0.33 past. Blind fire: the gun 0.11 over the top, the head 0.34 under it, the gap held.
- **High wall:** at the ends the head is 0.39 inside and the arm 0.29 past. Blind fire working left puts the gun 1.07 past the end; working right, at the corner (0.33 past).
- **Crate:** the outer corner swings stay out of it.
- **Popping up and ducking back** (2026-11-08), both sides: no leg in the wall, a shin 0.08 under the floor for one frame at most, the gun 0.05 in the wall's face while it comes up. Sliding along the low wall, the feet stay on the floor (the foot guard runs in cover).
- **Blind fire while sliding along low cover** (2026-11-09), both ways, starting, stopping and reversing: the gun over the top and pointing across, nothing in the wall, the head under the top, the gap held.
- **Blind fire with a long gun behind high cover** (2026-11-10; the AK-47, the FAL and the M107): mid-wall, at both ends, sliding and reversing, nothing in the wall and the support hand on the gun throughout; at the ends the muzzle 1.9 past it.
- Details in [[Animation and MP3 Systems - Progress and To Do]] (sessions 4 to 6). The 2026-11-02 tests of the old wall-facing pose are there too (session 3).

## Not done
- **Vaulting out of low cover** turns the body round in the vault's blend, and a foot dips into the wall for a frame (to-do 4.15).
- **The low run's legs:** the trailing knee comes down to 0.19 over the floor, and the shin's and thigh's boxes (and a holstered gun) go up to a third of a stud under it, as in the crouch walk (4.20).
- **Long guns' blind fire clips aren't published yet** (2026-11-10): until 83tg publishes them, live servers play the one-handed clips with a rifle, as before.
- **Inside corners:** the root turns in one frame, and the running body swings with it (4.16).
- **Blind fire working right** only reaches the corner (4.17).
- **Past the ends:** the edge-side arm shows about 0.3 past a wall's end (4.18).
- **Tall low cover:** blind fire can't reach over low cover taller than about 3.7 to 4, depending on the avatar (4.9).
