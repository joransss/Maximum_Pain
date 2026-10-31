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
| 2026-10-31 | Who decides "aiming"? | The server needs it to tighten spread. | The client sends an aiming flag with each shot. | Cheatable (always claiming aim). Later, tie aiming to something the server can check. **Superseded below.** |
| 2026-10-31 | Who applies limb movement penalties? | Character movement is owned by each player's own machine on Roblox. | The server owns limb health and status; the client sets walk speed from it. | A speed cheat would ignore limping; the same is true of all Roblox movement. **Partly covered by the movement check below.** |
| 2026-10-31 | Who owns stances (sprint, crouch, cover, dives)? | Waiting a round trip before crouching or diving feels sluggish; trusting the client is cheatable. | The client predicts at once; the server checks every request against the shared rules and confirms, rejects or forces. After 0.75 s of disagreement the client takes the server's stance. See [[Movement State Machine]]. | Test under real lag. |
| 2026-10-31 | Where do shots come from? | The camera can see over cover the gun can't; a client-sent muzzle is cheatable. | The server places the muzzle from its own copy of the character and blocks shots whose gun path hits something. See [[Weapons and Recoil]]. | — |
| 2026-10-31 | Aiming, second version | The flag-per-shot version was cheatable at no cost. | The client reports aim on and off; the server applies the tighter spread only after 0.15 s and never while hidden in cover. Aiming slows walking to 70%. | A cheater can still aim all the time, paying the slower walk. |
| 2026-10-31 | Movement cheats | Roblox characters are moved by their own player's machine. | The server checks speed against the stance's limit every 0.5 s and puts the character back after two bad windows. Tested with a faked 200 studs/s run. | The slack (×1.35 + 6 studs/s) still lets small cheats through. |
| 2026-10-31 | Who flies the shoot-dodge? | The client simulates its own character; server-side forces would stutter. | The client flies it; the server checks the direction, cooldown, timing and speed. See [[Shoot-Dodge]]. | — |
| 2026-10-31 | Who decides Last Stand? | It decides life and death. | The server only: eligibility, the window, line of sight, success and costs. The client just shows it. See [[Last Stand and Bullet Time]]. | — |
