# Gunplay

## Goal
Make aiming, firing, recoil and hit feedback feel consistent and fair in multiplayer.

## Weapon Data to Track
| Property | Purpose |
|---|---|
| Damage | Health removed per valid hit |
| Fire rate | Maximum firing frequency |
| Magazine size | Rounds before reload |
| Reload duration | Time before firing is allowed again |
| Range / falloff | Damage behaviour over distance |
| Spread | Random deviation from aim |
| Recoil | Camera / aim response to firing |
| Headshot multiplier | Optional damage modifier |
| Equip time | Time before a weapon is ready |

## Architecture
- Client: input, camera feel, local muzzle flash, immediate cosmetic feedback.
- Server: validate fire cadence, ammo, weapon ownership, plausible origin/direction and hit result; apply damage.
- Shared ModuleScripts: weapon configuration and common constants where appropriate.

## Prototype Checklist
- [ ] Single weapon fires
- [ ] Ammo decreases on valid shot
- [ ] Reload works
- [ ] Server rejects impossible fire rates
- [ ] Damage is applied once per shot
- [ ] Effects do not reveal hidden information unfairly
- [ ] Test latency and different frame rates

## Balance Log
| Date | Change | Reason | Result |
|---|---|---|---|
| | | | |
