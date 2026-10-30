# Script Registry

Track the scripts that actually exist in Roblox Studio. Details and test status: [[Implementation Log]].

| Script name | Explorer location | Type | Responsibility | Status |
|---|---|---|---|---|
| GameConfig | ReplicatedStorage/Shared | ModuleScript | Shared tuning: health, medicine, Last Stand, dodge, bullet time, score, controls | In progress |
| WeaponConfig | ReplicatedStorage/Shared | ModuleScript | Weapon data by ID (`Pistol9mm`), with config asserts | In progress |
| CharacterStates | ReplicatedStorage/Shared | ModuleScript | Shared state machine: stance/action rules, spread multiplier by state | In progress |
| MoveInput | ReplicatedStorage/Shared | ModuleScript | Client movement input (keys + left stick) | In progress |
| CombatMain | ServerScriptService | Script | Starts services; per-player remote rate limits | In progress |
| CombatService | ServerScriptService/Services | ModuleScript | Damage, Last Stand, medicine use, eliminations, score | In progress |
| WeaponService | ServerScriptService/Services | ModuleScript | Fire validation, simulated bullets, aiming state, spread bloom, ammo, reload | In progress |
| DodgeService | ServerScriptService/Services | ModuleScript | Dive run-up / dive / prone / recovery state and cooldown | In progress |
| StanceService | ServerScriptService/Services | ModuleScript | Sprint/crouch/cover validation, cover geometry, clearance, posture, movement guard | In progress |
| BulletTimeService | ServerScriptService/Services | ModuleScript | Line-of-sight bullet time sessions and per-character slow | In progress |
| PickupService | ServerScriptService/Services | ModuleScript | Death drops, weapon/ammo pickups (prompt), automatic medicine pickup | In progress |
| TestDummyService | ServerScriptService/Services | ModuleScript | Studio-only test dummy (deleted on live servers) | In progress |
| CombatController | StarterPlayerScripts | LocalScript | Shoulder camera, aiming (ADS), fire/reload/medicine/bullet-time input, recoil, muzzle flash, audio, tracers, aim-direction sync | In progress |
| DiveController | StarterPlayerScripts | LocalScript | Run-up, slow-motion-aware omnidirectional dive, prone landing, get-up | In progress |
| HUDController | StarterPlayerScripts | LocalScript | HUD, hit/kill feedback, score pop-ups, screen grading, aim zoom | In progress |
| PoseController | StarterPlayerScripts | LocalScript | Live aim layer on top of the clips for all characters: chest onto the aim point, straight-arm aim while down, blind fire, head (R15; Motor6D or AnimationConstraint joints) | In progress |
| StanceController | StarterPlayerScripts | LocalScript | Sprint/crouch/cover input; cover snapping, sliding, corners, peeking | In progress |
| Health | StarterCharacterScripts | Script (empty) | Disables Roblox's default health regeneration | In progress |
| Animate | StarterCharacterScripts | LocalScript | R15 animation state machine (replaces the default): locomotion blends, weapon holds, reload, recoil, dive / land / prone / recover | In progress |
| AnimationIds | ReplicatedStorage/Shared | ModuleScript | Published animation IDs per clip (empty = Studio-only playback) | In progress |
| AbilityService | — | — | Replaced by DodgeService + BulletTimeService | Deprecated |
| RoundService | ServerScriptService/Services | ModuleScript | Match phases and scoring | Planned |

## Status Key
- Planned
- In progress (implemented, single-client tested; two-client test pending)
- Tested
- Needs refactor
- Deprecated

Update this registry whenever you add, rename or remove a script.
