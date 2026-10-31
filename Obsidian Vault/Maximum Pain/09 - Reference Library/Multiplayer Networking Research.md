# Multiplayer Networking Research

This note is a research checklist, not a claim that a particular networking model has already been implemented. Start with Roblox's official documentation and test latency-sensitive decisions in a multiplayer session.

## Core sources
- [Client-server security](https://create.roblox.com/docs/scripting/security/client-server-boundary)
- [Security tactics](https://create.roblox.com/docs/scripting/security/security-tactics)
- [Remote events](https://create.roblox.com/docs/scripting/events/remote)
- [Network ownership](https://create.roblox.com/docs/physics/network-ownership)
- [Server authority](https://create.roblox.com/docs/projects/server-authority)
- [MicroProfiler](https://create.roblox.com/docs/performance-optimization/microprofiler)
- [Network profiling](https://create.roblox.com/docs/performance-optimization/microprofiler/network)

## Questions to resolve
### Server authority
- Which state is authoritative on the server? At minimum: damage, ammo, fire rate, reloads, cooldowns, scoring, currency, objectives and match outcome.
- What does the client request, and what does the server independently validate?
- Are remote payloads typed, bounded, rate-limited and checked against player state?

### Hit registration and latency
- Is the weapon hitscan, projectile-based or a mixture?
- What does the client predict immediately for responsiveness?
- How are hit claims and obstructions validated by the server?
- Would latency compensation or limited rewind be necessary, and what exploit/balance risks would it introduce? Do not add rewind without a concrete tested need.

### Replication and performance
- Which state must replicate to every player, and which can remain local?
- Are frequent updates sent only when needed?
- What happens at expected player counts and under high latency?
- Are physics ownership choices safe for competitive gameplay?

## Minimum multiplayer test matrix
- [ ] Two clients can join and see consistent match state
- [ ] Invalid and malformed remote requests are rejected
- [ ] Fire rate, ammo and reload rules cannot be bypassed by remote spam
- [ ] Static cover blocks shots
- [ ] Client-reported damage and score are never accepted as authoritative
- [ ] Behaviour is tested under latency and packet delay where tooling permits
- [ ] Performance is checked with the intended player count

## Decisions log
| Date | Question | Evidence/test | Decision | Follow-up |
|---|---|---|---|---|
| 2026-10-31 | Hitscan or projectile? | [[Weapons and Raycasting]] recommends server-validated hitscan first. Walls, spam and bad data were tested. | Hitscan. Tracers only show the bullet travelling at each gun's speed. | Revisit (for example FastCast) if bullet travel time ever needs to matter in play. |
| 2026-10-31 | Where does recoil live? | CS2 splits recoil (learnable pattern) from inaccuracy (random spread). | Spray pattern and per-shot jerk on the client camera; random spread on the server. | A no-recoil cheat is possible; a no-spread cheat isn't. |
| 2026-10-31 | Who decides "aiming"? | The server needs it to tighten spread. | The client sends an aiming flag with each shot. | Cheatable (always claiming aim). Later, tie aiming to something the server can check. |
| 2026-10-31 | Who applies limb movement penalties? | Character movement is owned by each player's own machine on Roblox. | The server owns limb health and status; the client sets walk speed from it. | A speed cheat would ignore limping; the same is true of all Roblox movement. |
