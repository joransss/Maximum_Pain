# Roblox Explorer Structure

Actual tree as of 2026-10-30 (see [[Implementation Log]]). Items marked *planned* do not exist yet.

## ReplicatedStorage
- `Remotes`: `FireWeapon`, `ReloadWeapon`, `RequestDodge`, `RequestGetUp`, `RequestBulletTime`, `UseMedicine`, `RequestStance`, `SetAiming`, `AimDirection` (unreliable), `ShotEffects`, `ImpactEffects` (unreliable), `CombatFeedback` (*planned:* `MatchStateChanged`)
- `Shared`: `GameConfig`, `WeaponConfig`, `CharacterStates` (state machine), `MoveInput`
- `Assets`
  - `Weapons`: `9mm Pistol` (Tool, WeaponId `Pistol9mm`; Handle has `Muzzle` attachment with `Flash` + `FlashLight`, `Fire` and `Reload` sounds)
  - `Animations`, `Effects` (empty)

## ServerScriptService
- `CombatMain` (Script)
- `Services`: `CombatService`, `WeaponService`, `DodgeService`, `BulletTimeService`, `PickupService`, `StanceService`, `TestDummyService` (*planned:* `RoundService`, `SpawnService`, `DataService`)

## StarterPack
- `9mm Pistol` (temporary spawn loadout)

## StarterPlayer
- `StarterPlayerScripts`: `CombatController`, `DiveController`, `HUDController`, `PoseController`, `StanceController`
- `StarterCharacterScripts`: `Health` (empty; disables regeneration)

## StarterGui
- `CombatHUD`: `Crosshair` (dot), `HitMarker`, `KillMarker`, `Popups`, `Message`, `LastStand`, `Score`, `Status` (`Weapon`, `BulletTime`, `Health`, `Medicine`) (*planned:* `MainMenu`, `ResultsScreen`)

## Workspace
- `Map`: `TestCover`, `TestArena` (HighWall, CornerWall, LowWall, Crate, Pillar, Overhang), `MedicineSpawns` (3 × `Medicine`, tag `MedicineSpawn`)
- `SpawnPoints` (empty)
- `TestDummy` (tag `TestDummy`; Studio-only)
- `Pickups` (created at runtime for drops)
- `Impacts` (client-side bullet holes; each client creates its own)

## Tags
- `TestDummy`: Studio-only combat target
- `MedicineSpawn`: respawning medicine pickup (collected automatically within 3.5 studs)
