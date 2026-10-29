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
