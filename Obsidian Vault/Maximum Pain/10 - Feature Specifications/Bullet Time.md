# Bullet Time

## Design intent
A limited tactical focus mode that creates a brief opportunity for precision and counterplay. It must not undermine multiplayer fairness or make the game unreadable.

## Multiplayer design decision
Do not assume that changing global Workspace time is acceptable. Prototype a **player-local presentation effect** first (camera, animation/effects, audio and UI). Any gameplay speed modification requires explicit design and multiplayer tests.

## Rules to define
- Activation conditions and input.
- Resource meter, drain rate, recharge and cooldown.
- Duration and cancellation conditions.
- Effects on the activating player, opponents and projectiles.
- Whether the effect is purely cosmetic or changes authoritative gameplay.
- Counterplay and visibility to opponents.
- Interaction with Shoot-dodge, reload, death and Last Stand.

## Security
The server validates resource, cooldown, alive state and activation frequency. The client cannot grant itself extra duration or change other players' authoritative movement/damage.

## Acceptance tests
- [ ] Activation cannot be spammed.
- [ ] Resource never goes below zero.
- [ ] Effect ends on timeout, death or cancellation.
- [ ] Other players retain responsive controls.
- [ ] No desynchronised state remains after respawn.
- [ ] Multiplayer fairness has been reviewed before release.
