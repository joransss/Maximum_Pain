# Technical Architecture Overview

## Principles
- Keep the first prototype small, then split systems when real complexity warrants it.
- Prefer clear modules with single responsibilities over large all-in-one controllers.
- Server is authoritative for competitive state; client is responsible for input and presentation.
- Keep remote payloads small, typed and documented.
- Use shared configuration only for data safe to replicate. Never place secrets or authority-critical logic in replicated modules.
- Add abstractions only when they reduce repeated complexity.

## Proposed Roblox services
- `ReplicatedStorage`: shared configuration/modules and remotes that both sides need.
- `ServerScriptService`: authoritative services and server-only modules.
- `ServerStorage`: server-only assets/templates.
- `StarterPlayer/StarterPlayerScripts`: client controllers.
- `StarterGui`: HUD and menus.
- `Workspace`: active map, spawn points and runtime world.
- `SoundService`: sound groups and mix configuration.

## Suggested modules (not all needed for Phase 1)
- `CombatService`
- `WeaponService`
- `CharacterStateService`
- `MatchService`
- `SpawnService`
- `RemoteValidation`
- `CameraController` (client)
- `InputController` (client)
- `HUDController` (client)
- `WeaponConfig` (shared, non-secret data)

## Change discipline
Before implementation, inspect the current Explorer and scripts. Extend existing systems where appropriate. Avoid replacing unrelated code. Test with Studio's multi-client tools and review Output errors.


## Detailed combat design
- [[Combat Architecture and Implementation Plan]] — end-to-end R6 combat architecture, server/client boundaries, shoot-dodge, hybrid Bullet Time, arsenal configuration, networking contract and acceptance tests.

## Implemented state machine (2026-10-30)
`ReplicatedStorage.Shared.CharacterStates` is the shared rule set for stances and actions, used by server validation, client prediction and poses. See [[Combat State Machine]].
