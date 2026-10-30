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
