# Acceptance Test Plan

## Phase 1 — Playable foundation
- [ ] Character spawns at an intended spawn point.
- [ ] Character moves, jumps and respawns reliably.
- [ ] Third-person camera is controllable and does not become stuck.
- [ ] Greybox arena is navigable and has basic cover.
- [ ] Placeholder health/ammo HUD is readable.
- [ ] Test server with two clients; both can spawn and move.
- [ ] No unexpected Output errors.
- [ ] No publishing performed without approval.

## Phase 2 — First weapon
- [ ] Fire, ammo, reload and damage work.
- [ ] Server validates fire rate, ammo and hit targets.
- [ ] Static walls block shots.
- [ ] Invalid remote calls do not cause errors or damage.

## Phase 3 — Combat states and advanced movement
- [ ] State transitions and interruption cases pass.
- [ ] Shoot-dodge has consistent movement and cooldown.
- [ ] Bullet Time does not create unfair or desynchronised multiplayer behaviour.

## Phase 4 — Modes and polish
- [ ] Match starts and ends correctly.
- [ ] Scoring and objectives are server-owned.
- [ ] HUD, audio, VFX and animations are tested for clarity.
- [ ] Performance is profiled under a representative player count.

Record results in `07 - Testing and Bugs/`.
