# Roblox Explorer Structure

> Suggested starting layout; adjust to the actual project as it grows.

## ReplicatedStorage
- `Remotes`
  - `FireWeapon`
  - `ReloadWeapon`
  - `RequestAbility`
  - `MatchStateChanged`
- `Shared`
  - `WeaponConfig`
  - `GameConfig`
- `Assets`
  - `Animations`
  - `Effects`

## ServerScriptService
- `Services`
  - `CombatService`
  - `WeaponService`
  - `AbilityService`
  - `RoundService`
  - `SpawnService`
  - `DataService` (later)

## StarterPlayer
- `StarterPlayerScripts`
  - `PlayerController`
  - `CameraController`
  - `InputController`
  - `UIController`

## StarterGui
- `HUD`
- `MainMenu`
- `ResultsScreen`

## Workspace
- `Map`
- `SpawnPoints`

## Important
These names are a proposed convention, not built-in Roblox requirements. Create objects deliberately and keep the actual Explorer tree documented here.
