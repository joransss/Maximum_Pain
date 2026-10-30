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
| | | | | |
