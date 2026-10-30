# Player Movement

## Movement States
- Idle
- Walk
- Sprint
- Jump / fall
- Shoot-dodge
- Recovery
- Dead

## Design Questions
- Sprint speed:
- Acceleration:
- Air control:
- Jump height:
- Can the player sprint while aiming?
- Can the player fire while sprinting?
- What cancels sprint or dive?

## Requirements
- [ ] Movement feels responsive
- [ ] State transitions do not get stuck
- [ ] Death and respawn reset movement state
- [ ] Abilities cannot be spammed
- [ ] Movement is tested on slopes, stairs and edges

## Implemented (2026-10-30)
- **Speeds (×16 base):** sprint ×1.6 (hold Left Ctrl), crouch ×0.5 (C toggle), aiming ×0.6, cover slide ×0.45, bullet-time scale on top. All server-set.
- **Sprint:** no firing or aiming (either ends the sprint); not from cover; a reload continues.
- **Crouch:** body lowered 1.3 studs (server `HipHeight`; R15 crouch clips bend the knees to match, head top ~3.9), no jumping, overhead clearance required to stand.
- **What cancels sprint or dive:** sprint ends on release, aim, fire, crouch, cover or dive; a dive can't be cancelled (walls slide it), and death ends everything.
- State rules: [[Combat State Machine]]. Speed is guarded server-side (see [[Implementation Log]]).
- Not yet tested: slopes, stairs, ledges.
