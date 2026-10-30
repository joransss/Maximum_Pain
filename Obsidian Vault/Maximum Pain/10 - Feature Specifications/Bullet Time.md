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

## Implemented rules (2026-10-30)
See [[Combat Architecture and Implementation Plan#Design updates — 2026-10-30 (supersede conflicting text above)]] and [[Implementation Log]].
- **Input:** F toggles. **Resource:** 100 max, 25 to activate, 15/s drain, 3 s cap, 1 s cooldown after it ends; +5 per hit, +25 per kill.
- **Trigger:** someone is in view of the activator, or the activator is in view of someone: clear line of sight ≤ 80 studs, and either party facing the other within 140°.
- **Effects:** activator ×0.6 movement, fire rate and bullet speed, with free aim; victims ×0.3 movement, aim, fire rate and bullet speed. Gameplay effect, not cosmetic. Recheck at 10 Hz; targets released when out of view; the session ends 0.5 s after nobody is in view.
- **Interactions:** cannot activate while a victim or in Last Stand; death ends the session; every combatant is reset to normal speed each tick when not in a role.
- **Open:** sightline chain (B sees C), team rules, and victim aim slowdown being client-side (not server-enforceable).
- **Dive interaction (2026-10-30):** a slowed character's shoot-dodge runs in slow motion at the same scale (see [[Shoot-Dodge]]).
