# Weapons and Recoil

## Weapon Roles
Start with a small, distinct set:
- **Automatic rifle:** reliable at close-to-mid range
- **Heavy pistol (Desert-Eagle-style):** high damage, strong recoil, slower firing
- **Shotgun or precision weapon:** add only after core balance is stable
- **Light 9mm pistol:** lower recoil and higher ammunition capacity than the heavy pistol; intended for controllable sustained fire.
- **Dual-wield sidearms:** one heavy pistol plus one light 9mm, with distinct ammo pools and recoil; see [[Dual Wielding]]

## Weapon Definition Template
- Name:
- Role:
- Damage:
- Fire rate:
- Magazine:
- Reload time:
- Recoil pattern:
- Spread:
- Effective range:
- Strengths:
- Weaknesses:

## Design Rules
- Each weapon needs a clear role.
- Avoid a single weapon being best at every range.
- Recoil should be learnable and consistent.
- Server validates fire cadence and ammunition.
- Each weapon starts with one magazine and no extra reserve ammo; ammo scavenging from a ground weapon requires an exact weapon-type match. See [[Weapon and Ammunition Pickup Mechanic]].
- Keep weapon configuration separate from the firing implementation.
- Cosmetic skins never alter weapon stats or hitboxes.


## Loadout restriction

The player chooses either one heavy weapon plus one pistol, or dual pistols with no heavy weapon. Dual pistols are a mutually exclusive package, not an extra pair of sidearm slots. See [[Loadouts and Progression]], [[Weapon and Ammunition Pickup Mechanic]] and [[Drop Weapons on Death]] for pickup, ammo-transfer, replacement and defeated-player drop rules.

## PvP-only target scope

Maximum Pain has no PvE enemies or hostile AI. All combat targets and elimination/drop logic refer to player characters; world geometry remains relevant for raycast obstruction and collision only.

## Implemented recoil and aiming (2026-10-30)
- **Camera recoil:** pitch kick per shot plus small random yaw; fully recovers, so it stays learnable. ×0.6 while aiming.
- **Bloom (server-side):** each shot adds spread that decays over time. Total spread = (base + bloom) × (0.3 while aiming). 9mm: base 1.2°, +0.5° per shot, max +2.5°, decay 4°/s.
- **Visual kick:** the gun arm kicks on every shot, for every player.
- **Aiming (ADS):** hold right mouse: zoom, tighter spread, less recoil, slower movement (×0.6, server-applied).

## Accuracy modifiers by state (2026-10-30)
Spread = (base + bloom) × state multiplier × (0.3 if aiming), all server-side (`GameConfig.Accuracy`):
| State | Multiplier |
|---|---|
| Standing | 1 |
| Walking | 1.5 |
| Sprinting | 3 (firing blocked) |
| Crouching | 0.7 |
| Airborne (jumping/falling) | 2.5 |
| Shoot-dodge (run-up / diving) | 1.3 |
| Prone / Last Stand | 0.9 |
| Cover, blind fire | 8 |
| Cover, aiming (peek / pop-up) | 1 |
Progressive bloom (spread growth that recovers to baseline) and camera recoil are separate systems.

### Update (2026-10-30, later)
- Cover blind fire is now ×8 (was ×2): `Accuracy.BlindFire`. Peeking (head clear of the wall, server-checked) uses the normal aimed accuracy.
- **Impact effects:** bullet holes on surfaces and blood clouds on characters at the server's real hit points, for observing accuracy and bullet patterns.
