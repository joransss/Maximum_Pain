# Combat State Machine

## Purpose
Prevent incompatible actions from running simultaneously and provide a predictable base for movement, shooting, reloads, Shoot-dodge, Bullet Time, cover and Last Stand.

## Proposed states
- `Idle`
- `Aiming`
- `Firing`
- `Reloading`
- `ShootDodging`
- `InBulletTime`
- `InCover`
- `Downed` (only if Last Stand design is approved)
- `Dead`

The exact state list may change during implementation. Do not create one monolithic script that owns every mechanic.

## Rules
- Death overrides all active combat states.
- Reloading blocks firing until completed or cancelled by a documented rule.
- Shoot-dodge temporarily restricts normal movement and may restrict aiming depending on balance.
- Cover is optional and should not make players invulnerable.
- Bullet Time effects must be fair and legible in multiplayer; global time manipulation is not assumed.
- Every timed state needs cleanup on death, respawn, character removal and disconnect.

## Acceptance criteria
- No simultaneous reload and fire unless explicitly designed.
- No stuck state after interrupted action.
- Server validates competitive state transitions.
- UI and animations reflect authoritative state without excessive remote traffic.
