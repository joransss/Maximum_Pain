# Maximum Pain — Obsidian Vault

An Obsidian planning vault for an original Roblox multiplayer third-person shooter inspired by cinematic slow-motion gunplay. It is organised around game design, combat, multiplayer, player systems, technical architecture, scripts, testing and references.

## Included planning areas
- Dashboard and development roadmap
- Game Design Document, core loop, modes and maps
- Combat: gunplay, Bullet Time, Shoot-dodge, cover, Last Stand, dual-wielding and destructible environments
- Multiplayer: rounds, objective-chain mode, high-value target mode and cinematic kill camera
- Player systems: movement, camera, tactical abilities, skill scoring and cosmetic progression
- Cosmetic currency and cases with Roblox paid-random-item policy notes
- Roblox client/server architecture, RemoteEvents, persistence and script templates
- [[Combat Architecture and Implementation Plan]] — R6 combat architecture, shoot-dodge, hybrid Bullet Time, weapon framework, networking and implementation milestones
- Testing, bug tracking, balance logs and asset research

## Suggested build order
1. Third-person movement, aiming and one weapon.
2. Server-validated damage, health and respawn.
3. Shoot-dodge and recovery.
4. Line-of-sight Bullet Time with a bounded chain graph.
5. A complete round loop and one compact map with cover.
6. Add advanced mechanics one at a time and playtest.
7. Add progression and monetisation only after the combat loop is stable.

## Important design principles
- Keep damage, ammo, abilities, scoring and currency server-authoritative.
- Do not slow the entire Roblox server simulation for Bullet Time.
- Treat new mechanics as backlog until the core loop is reliable.
- Create original names, maps, characters, UI, audio, animations and assets; use other games as broad design references rather than copying protected content.
- Robux-funded random cosmetic cases must follow Roblox's current paid random items policy, including odds disclosure and player eligibility restrictions.


## Core combat rules
- [[Loadouts and Progression]] — heavy weapon + pistol or dual pistols (a high-recoil, low-ammo heavy pistol plus a low-recoil, higher-capacity 9mm), one starting magazine per weapon, same-type ammo scavenging, separate defeated-player weapon drops and PvP-only scope.
- [[Weapon and Ammunition Pickup Mechanic]] — weapon pickups and exact-type ammo scavenging.
- [[Drop Weapons on Death]] — separate weapon drops, retained ammunition and anti-duplication rules.
- [[Max Payne 3 HUD and Combat UI Reference]] — HUD screenshot, annotated source manual, and original-interface design checklist.
