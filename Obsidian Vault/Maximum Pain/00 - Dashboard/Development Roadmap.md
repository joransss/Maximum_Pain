# Development Roadmap

## Milestone 1 — Combat Prototype
- [ ] Third-person camera and aiming — *implemented 2026-10-30, solo-tested; two-client test pending ([[Implementation Log]])*
- [ ] Basic movement and sprint — *sprint + crouch implemented 2026-10-30, solo-tested ([[Implementation Log]])*
- [ ] One test weapon — *implemented 2026-10-30, solo-tested; two-client test pending ([[Implementation Log]])*
- [ ] Server-validated hit and damage — *implemented 2026-10-30, solo-tested; two-client test pending ([[Implementation Log]])*
- [ ] Health and respawn — *implemented 2026-10-30, solo-tested; two-client test pending ([[Implementation Log]])*
- [ ] Basic hit feedback — *implemented 2026-10-30, solo-tested; two-client test pending ([[Implementation Log]])*

**Exit criteria:** Two players can join and fight reliably.

## Milestone 2 — Signature Combat
- [ ] Shoot-dodge with recovery window — *implemented 2026-10-30, solo-tested; two-client test pending ([[Implementation Log]])*
- [ ] Bullet Time resource and cooldown — *implemented 2026-10-30, solo-tested; two-client test pending ([[Implementation Log]])*
- [ ] Server-authoritative line-of-sight and bounded chain logic — *line of sight implemented, chain not yet; 2026-10-30, solo-tested; two-client test pending ([[Implementation Log]])*
- [ ] Per-player movement/weapon handling effects; never global time slowdown
- [ ] Ability telegraphs, camera feedback and cleanup — *implemented 2026-10-30, solo-tested; two-client test pending ([[Implementation Log]])*
- [ ] Cover raycast rules match weapon and Bullet Time rules

**Exit criteria:** Abilities are readable, counterable and stable with multiple clients.

## Milestone 3 — Match Loop
- [ ] Lobby and round start
- [ ] Team or free-for-all spawns
- [ ] Kill feed and scoreboard
- [ ] Round timer and win condition
- [ ] Post-round screen and reliable reset

**Exit criteria:** A complete match can start, end and restart.

## Milestone 4 — Tactical Depth
- [ ] Prone shooting after Shoot-dodge — *implemented 2026-10-30, solo-tested; two-client test pending ([[Implementation Log]])*
- [ ] Contextual cover/peek only if needed — *implemented on request 2026-10-30 (high/low cover, corners, peek), solo-tested*
- [ ] Last Stand prototype (test whether it harms kill reliability) — *implemented 2026-10-30; timeout tested solo, comeback needs two clients ([[Implementation Log]])*
- [ ] Dual-wield sidearms with clear trade-offs
- [ ] Limited breakable props
- [ ] Short, skippable final-kill camera

**Exit criteria:** New mechanics improve decisions without breaking combat readability or performance.

## Milestone 5 — Modes and Progression
- [ ] Team Deathmatch polish
- [ ] Prototype one objective mode
- [ ] Skill scoring and challenges
- [ ] Cosmetic inventory and earnable currency
- [ ] Cases with policy-compliant odds disclosure if any Robux-funded path exists
- [ ] Additional abilities only after core balance

**Exit criteria:** Players have reasons to replay without paid combat advantages.

## Milestone 6 — Testing and Release
- [ ] Test at different player counts and latency levels
- [ ] Check exploit resistance and remote validation
- [ ] Profile client and server performance
- [ ] Balance weapon damage and ability cooldowns
- [ ] Test respawning, disconnects and round resets
- [ ] Prepare thumbnail, icon and store description
