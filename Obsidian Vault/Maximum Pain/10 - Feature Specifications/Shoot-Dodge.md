# Shoot-Dodge

## Design intent
A short, committed evasive leap that creates a readable risk/reward moment. Inspiration: Max Payne 3's signature move; all character animation, effects and assets must be original or properly licensed.

## Input and behaviour
- Input: configurable key/button.
- Direction: based on movement input, with a documented fallback when no direction is held.
- Duration, distance, cooldown and resource cost: **TBD; tune in Studio**.
- During the move, the character should have a clear trajectory and a limited ability to change direction.
- Define whether aiming/firing is allowed during the move; do not let this be accidental.
- Collisions must prevent clipping through geometry.
- Repeated activation must be blocked by server-side cooldown/state checks.

## Multiplayer requirements
- Server validates alive state, cooldown, resource and legal direction.
- Replicated movement and animation must be readable to other players.
- Do not trust the client to report a successful hit or damage.
- Test with latency and during death/respawn.

## Acceptance tests
- [ ] Starts only when legal.
- [ ] Has consistent movement distance and duration.
- [ ] Cannot be spammed.
- [ ] Does not pass through solid walls.
- [ ] State and animation clean up on death.
- [ ] Other clients see a coherent action.

## Implemented rules (2026-10-30)
- **Input:** Left Shift. **Direction:** any horizontal angle from camera-relative WASD; fallback is current movement, then camera forward.
- 0.65 s driven dive at 45 studs/s, 12 studs/s lift, 0.35× gravity during the window; 1.5 s cooldown from dive start (server-enforced).
- Walls and props never end the dive: velocity into the surface is removed and the body slides along it; no clipping (tested on `TestCover`).
- **Landing:** stays prone until a movement key is pressed, then gets up (0.35 s recovery, no dive during recovery).
- Firing allowed while diving and prone; a reload in progress continues.
- Server states: `Diving` → `Prone` → `Recovering` → none (character attribute `CombatState`).
- Pose is procedural (lying head-first, chest turned toward the aim). Authored R6 animations are still needed.

## Slow-motion dive and R6 landing (2026-10-30)
- In bullet time the dive plays in slow motion (user decision): speed and lift ×s, gravity ×s², duration and recovery ÷s, so the distance stays the same. The motion is rescaled if bullet time starts or ends mid-dive; server timers stretch too.
- Dive poses: arms stretched ahead when not aiming; arms on the aim when aiming (see [[Animation System]]).
- Landing check reaches 2.6 studs below the root (an R6 body on its side rests ~2.1 up).
- Known: the slow-motion arc peaks higher than the normal arc (see [[Implementation Log]]).

## Run-up, arc fix and get-up (2026-10-30)
- **Run-up:** 0.15 s `Windup` (lean into the dive) before launch; no firing or aiming during it.
- **Arc:** vertical speed integrated by the client script (physics applies the same gravity through the lift force; contacts only remove speed), so the arc is the same at every time scale.
- **Get-up:** 0.5 s `Recovering` with a push-up pose; forced upright at the end; no dive or firing until it ends.
- Diving from sprint, crouch or cover is allowed and clears the stance.
