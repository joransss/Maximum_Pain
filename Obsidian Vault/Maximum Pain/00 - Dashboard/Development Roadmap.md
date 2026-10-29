# Development Roadmap

## Milestone 1 — Combat Prototype
- [ ] Third-person camera and aiming
- [ ] Basic movement and sprint
- [ ] One test weapon
- [ ] Server-validated hit and damage
- [ ] Health and respawn
- [ ] Basic hit feedback

**Exit criteria:** Two players can join and fight reliably.

## Milestone 2 — Signature Combat
- [ ] Shoot-dodge with recovery window
- [ ] Bullet Time resource and cooldown
- [ ] Server-authoritative line-of-sight and bounded chain logic
- [ ] Per-player movement/weapon handling effects; never global time slowdown
- [ ] Ability telegraphs, camera feedback and cleanup
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
- [ ] Prone shooting after Shoot-dodge
- [ ] Contextual cover/peek only if needed
- [ ] Last Stand prototype (test whether it harms kill reliability)
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
