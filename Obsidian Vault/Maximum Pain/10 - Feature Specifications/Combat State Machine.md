# Combat State Machine

## Purpose
Prevent incompatible actions from running at the same time and give movement, shooting, reloading, shoot-dodge, bullet time, cover and Last Stand one predictable base.

## Implemented model (2026-10-30)
Rules live in one shared module, `ReplicatedStorage.Shared.CharacterStates`. The **server** validates every request with it (stance, dive, get-up, aim, fire); **clients** use the same rules to predict input; **Animate** (R15 clips) and **PoseController** (live aim layer) derive animation from the same state, so animations never compete.

| Layer | Attribute | Values (exclusive within a layer) | Owner |
|---|---|---|---|
| Stance | `Stance` (nil = Stand) | Stand, Sprint, Crouch, CoverHigh, CoverLow | Server (StanceService) |
| Action | `CombatState` | Windup, Diving, Prone, Recovering, LastStand | Server (DodgeService, CombatService) |
| Overlays | `Aiming`, tool `Reloading`, `BTRole` | — | Server |
| Death | Humanoid health | Overrides everything; a new character starts clean | Engine |

### Rules
| Request | Allowed when |
|---|---|
| Sprint | No action, not aiming, standing or crouched (leave cover first); needs room to stand |
| Crouch | No action, standing or sprinting |
| Stand | No action; needs overhead clearance |
| Cover | No action; a valid wall within 3.5 studs |
| Dive | No action; from any stance (clears sprint, crouch and cover) |
| Get up | Diving or prone |
| Aim | Not sprinting, not in run-up or recovery |
| Fire | Not sprinting, not in run-up or recovery |
| Reload | Always; continues through sprint, dives and cover; unequip or death cancels it without moving ammo |

### Transitions
- Dive: `Windup` (0.15 s) → `Diving` (0.65 s) → `Prone` → (movement input) `Recovering` (0.5 s) → none. All durations ÷ the bullet-time scale.
- Lethal damage with medicine: any → `LastStand` (stance cleared). Recover → `Prone`; fail → dead.
- Aiming in `CoverLow` pops the body up (server posture); releasing crouches again.

### Animation layers (R15, 2026-10-30; details in [[Animation System]])
- **Base (`Animate`):** windup > dive air > land > prone > recover > locomotion (crouch / sprint / walk / run 4-way blends) > turn in place > idle.
- **Upper body (`Animate`, weapon out, not diving / downed / sprinting):** cover hold (not peeking) > aim (incl. peeking) > hip. Overlays: reload (server-timed), recoil per shot.
- **Live aim (`PoseController`, all characters):** straight arms on the aim while down and aiming > blind-fire arm in cover > chest turned onto the aim point (hip / aim) > head follows the aim.

## Rules
- Death overrides all active combat states.
- Reloading blocks firing until it completes or is cancelled by unequip or death.
- Shoot-dodge restricts normal movement; aiming and firing are allowed while diving and prone.
- Cover does not make players invulnerable; it only changes posture, accuracy and what geometry blocks.
- Every timed state uses a token so stale timers cannot overwrite a newer state; death and respawn start clean.

## Acceptance criteria
- [x] No simultaneous reload and fire (server-checked) — 2026-10-30
- [x] No stuck state after an interrupted action (get-up forces upright; server timers expire) — solo test 2026-10-30
- [x] Server validates competitive state transitions — 2026-10-30
- [ ] UI and animations reflect authoritative state without excessive remote traffic — single client only so far
