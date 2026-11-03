# Shoot-Dodge

The dive, in any direction: a run-up, a long low flight, wall collisions, a slide, lying on the floor aiming, and getting up. Built 2026-10-31.
Related: [[Movement State Machine]] · [[Max Payne 3 Mechanics Reference]] · [[Max Payne 3 Animation Reference]] · [[Limb Health]]

## Controls
**Left Alt** or **V** (gamepad R1) dives the way the movement keys point, relative to the camera: forward, sideways, backward or diagonally. With no movement key it dives forward. The body keeps facing where the camera aims, so a sideways dive keeps the gun on target, as in Max Payne 3.

## Phases
| Phase (stance) | Time | What happens |
|---|---|---|
| Run-up (DodgePrep) | 0.2 s | A step toward the dive with the hips dipping 0.6 studs. It makes the dive read as deliberate, and hides the network delay before the server agrees. |
| Flight (DodgeAir) | about 0.5 s on flat ground | Launch at 26 studs/s level and 15 up. Gravity is cut to a quarter in the air, giving a long, low dive about 1.6 studs high and 17 studs long. The character can fire and aim. |
| On the floor (DodgeGround) | until a movement key | Keeps 40% of the speed as a 0.35 s slide, then lies down (hips 2.2 studs lower). Can fire, aim, reload, switch and take a painkiller, turning to shoot in any direction. |
| Getting up (GettingUp) | 0.6 s | Defenseless, as in Max Payne 3: no firing or moving. |
| Cooldown | 1 s after standing up | No new dive. |

## Collisions
- Hitting a wall more head-on than 45° ends the dive against it. Tested: a dive at the arena's end wall stopped just short of it.
- Glancing hits slide along the wall, keeping 80% of the speed.
- After 2.5 s in the air (diving off a ledge) normal gravity takes over until the body lands.

## Injuries
Dive speed and distance scale with `ShootDodgeScale` from [[Limb Health]]: 1 normally, 0.4 limping, 0 crawling (no dive; the HUD shows TOO HURT TO DIVE).

## Accuracy
Spread ×1.3 in the run-up and in the air, ×0.9 on the floor. Recoil ×1.2 in the air.

## Server checks
The server accepts a dive only from Standing, Sprinting or Crouching, with a valid level direction, off cooldown, not too hurt, and with ground under the character. It runs its own timeline: run-up 0.2 s, landing no sooner than 0.2 s after launch (forced at 2.5 s), getting up forced after 8 s on the floor. The movement check allows dive speed (with 30% slack) only during and just after a dive.

## How it flies
Roblox lets each player's own computer simulate their character, so the client flies the dive: a `LinearVelocity` holds the level speed, a `VectorForce` cancels three quarters of gravity, and a sphere cast ahead finds walls. Landing is detected when the body is past the shortest flight, no longer rising, and the floor is right under it.

## Animations
| Phase | Clip |
|---|---|
| Run-up | DodgePrepForward/Back/Left/Right, held at its last frame until the launch |
| Flight | DodgeAirForward/Back/Left/Right |
| Landing | DodgeLandForward/Back/Left/Right (the impact, 0.45 s) |
| On the floor | DodgeGround (propped on the elbows; the aim layer turns the chest and arms to aim any way) |
| Getting up | GettingUp, held until the stance ends |

The direction's clips are picked by comparing the dive's direction with where the body faces, so a sideways dive with the gun forward plays the sideways clips.

**Height:**
- **Launch and landing:** these move the root for real, so the aim layer leaves the body with the root (since 2026-11-02 for the launch too, which had pushed the feet 0.39 into the floor).
- **The landing drop:** the hips drop 2.2 and the root falls the rest of the way through physics, while the camera holds its height and eases down after it. It used to jump 1.7 up first.
- **Getting up:** the root rises at once, whether from a movement key or the server's forced get-up after 8 s. Before 2026-11-02 the forced get-up rose through physics over 8 frames.

## Compared with Max Payne 3
- Same: any direction, aiming through the dive, sliding on landing, staying down until a direction is pressed, a plain exposed get-up, walls ending the dive.
- Different: no slow motion during the dive. Max Payne 3's single player slows time; for multiplayer it isn't confirmed ([[Max Payne 3 Mechanics Reference]]). No turning and rolling on the floor yet: the body just turns to aim.

## Tested (2026-10-31)
Forward dive: 17 studs, 1.6 studs high, about 0.5 s in the air. Sideways and backward dives went the right way with the body still facing forward. A head-on dive stopped at the end wall. A movement key got the character up, back to Standing after 0.6 s. The ledge and the angled wall weren't tested.

## Tested (2026-11-02)
- **Distance:** backward and sideways dives went 17.9 studs.
- **Feet at launch:** −0.39 → +0.21 after the fix.
- **Landing camera:** steady (largest step 0.56, was a 1.7 jump).
- **Lying:** turning a full circle in 45° steps kept the lowest point 0.04 to 0.06 above the floor and the carried gun 0.38 above it.
- **Getting up:** a key press and the forced 8-second get-up both lifted the root at once.
- **Still open:** the left forearm's box dips 0.3 into the floor for one frame at the landing impact. See [[Animation and MP3 Systems - Progress and To Do]].
