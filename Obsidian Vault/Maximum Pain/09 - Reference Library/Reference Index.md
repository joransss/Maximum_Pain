# Reference Index

Use references to make specific design or implementation decisions. Link the relevant source from a feature specification and record the resulting requirement or test. Prefer official documentation and primary sources.

## Official Roblox documentation
| Topic | Reference | Why it matters |
|---|---|---|
| Camera | https://create.roblox.com/docs/workspace/camera | Camera behaviour and camera API fundamentals |
| Raycasting | https://create.roblox.com/docs/workspace/raycasting | Hitscan weapons, line of sight and interaction queries |
| Remote events | https://create.roblox.com/docs/scripting/events/remote | Client/server message flow |
| Client-server security | https://create.roblox.com/docs/scripting/security/client-server-boundary | Server validation and anti-exploit boundaries |
| Security tactics | https://create.roblox.com/docs/scripting/security/security-tactics | Practical security patterns and threat modelling |
| Network ownership | https://create.roblox.com/docs/physics/network-ownership | Physics replication and client ownership risks |
| Server authority | https://create.roblox.com/docs/projects/server-authority | Server-authoritative simulation and prediction concepts |
| Animation editor | https://create.roblox.com/docs/animation/editor | Creating and editing character animations |
| Animation overview | https://create.roblox.com/docs/animation | Animation workflow and publishing |
| Humanoid | https://create.roblox.com/docs/reference/engine/classes/Humanoid | Character movement and state handling |
| TweenService | https://create.roblox.com/docs/reference/engine/classes/TweenService | Smooth camera and presentation transitions |
| UI | https://create.roblox.com/docs/ui | HUD construction and UI behaviour |
| Data stores | https://create.roblox.com/docs/cloud-services/data-stores | Persistent progression and player data |
| Performance optimisation | https://create.roblox.com/docs/performance-optimization | Performance profiling and optimisation |
| MicroProfiler | https://create.roblox.com/docs/performance-optimization/microprofiler | Find expensive frames and scripts |
| MicroProfiler network | https://create.roblox.com/docs/performance-optimization/microprofiler/network | Investigate network traffic and replication costs |
| Instance streaming | https://create.roblox.com/docs/workspace/streaming | Large-map loading and memory management |
| Model export requirements | https://create.roblox.com/docs/art/modeling/export-requirements | Preparing imported assets for Roblox |

## Art and production tools
- [[Blender and Asset Pipeline]]
- [Blender Manual](https://docs.blender.org/manual/en/latest/) — modelling, materials, rigging and animation.
- [[Animation References]]
- [[Sound and VFX References]]
- [[Reference Videos]] — selected Roblox gameplay videos and observation checklist.
- [[Reference Images]]
- [[Max Payne 3 HUD and Combat UI Reference]] — multiplayer HUD screenshot, annotated manual reference, and design checklist for an original Maximum Pain HUD.

## Game design case studies
- [[Reference Games]]
- [Max Payne 3 — Rockstar screenshots](https://www.rockstargames.com/newswire/article/25o241181oo49k/new-max-payne-3-screenshots.html) — visual and combat reference.
- [Max Payne 3 — dual-wielding screenshots](https://www.rockstargames.com/newswire/article/25o241181ok413/new-max-payne-3-screenshots-the-art-of-dual-wielding.html)
- [Max Payne 3 on Steam](https://store.steampowered.com/app/204100/Max_Payne_3/)
- [Counter-Strike 2 on Steam](https://store.steampowered.com/app/730/CounterStrike_2/) — competitive weapon readability, recoil and map sightlines.
- [THE FINALS on Steam](https://store.steampowered.com/app/2073850/THE_FINALS/) — objective combat and environmental destruction.
- [Call of Duty: Modern Warfare on Steam](https://store.steampowered.com/app/2000950/Call_of_Duty_Modern_Warfare/) — check this listing's edition/platform details before using it as a product reference; use gameplay footage for killcam and match-flow study.

## Networking and multiplayer research
- [[Multiplayer Networking Research]]
- Focus topics: client prediction, latency compensation, hit registration, server authority, replication cost and exploit resistance.

## How to use a reference
Every reference should answer: **what exact decision does this inform?** Record the observation, the original implementation idea for Maximum Pain, and a testable acceptance criterion. Do not copy protected characters, names, story, maps, audio, UI, animations or assets. Check licences and permissions before using third-party assets.


## Roblox shooter case studies
- [[Reference Games]] — Phantom Forces, FRONTLINES, RIVALS, Criminality, Blackhawk Rescue Mission 5 and Bad Business.
- [[Reference Videos]] — selected video footage and what to observe.
- [[Reference Images]] — externally hosted screenshots with specific visual-analysis prompts.
- Official game pages: [Phantom Forces](https://www.roblox.com/games/292439477/Phantom-Forces), [FRONTLINES](https://www.roblox.com/games/5938036553/FRONTLINES), [RIVALS](https://www.roblox.com/games/17625359962/RIVALS), [Blackhawk Rescue Mission 5](https://www.roblox.com/games/2916899287/Blackhawk-Rescue-Mission-5), [Criminality](https://www.roblox.com/games/4588604953/Criminality), [Bad Business search](https://www.roblox.com/discover/?Keyword=Bad%20Business).
