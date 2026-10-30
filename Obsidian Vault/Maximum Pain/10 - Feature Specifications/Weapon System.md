# Weapon System

## Initial scope
Start with one test hitscan weapon before implementing a full arsenal, dual wielding, projectile weapons or complex attachment systems.

## Weapon definition
Each weapon should have server-owned configuration for:
- Damage and range
- Fire rate
- Magazine size and reserve ammo
- Reload duration
- Spread / recoil behaviour
- Equip time
- Head/body multipliers, if used
- Movement restrictions
- Animation and VFX identifiers

Exact balance values are **TBD** until prototype testing.

## Rules
- Client handles input, crosshair and responsive local effects.
- Server checks fire cadence, ammo, reload and target validity.
- Damage is calculated by server-owned code.
- Raycast filtering excludes the shooter's own character and irrelevant effects.
- Reloads are interruptible only according to explicit rules.
- Ammo state must survive normal replication but not be exploitable through client writes.

## Acceptance tests
- [ ] Fire rate matches configuration.
- [ ] Ammo decrements exactly once per accepted shot.
- [ ] Reload cannot duplicate ammunition.
- [ ] Hits through static walls are rejected.
- [ ] Invalid targets and malformed remote payloads are rejected.


## Loadout package restrictions

The loadout has exactly two supported packages:

- `HeavyAndPistol`: one heavy weapon (shotgun, assault rifle, SMG or precision weapon) plus one pistol.
- `DualPistols`: one heavy pistol plus one light 9mm pistol, with no primary/heavy weapon.

Dual pistols count as one loadout package for slot restrictions but consist of two distinct weapon instances. The heavy pistol has higher damage/recoil and limited ammunition; the 9mm has lower recoil and more ammunition. Track ammo and fire cadence independently. The heavy pistol is a sidearm, not a primary weapon. Server-side equip and pickup code must reject any state containing both `DualPistols` and a primary/heavy weapon.

## World pickups and defeated-player drops

- On a PvP elimination, drop the defeated player's carried weapons at the elimination location.
- `HeavyAndPistol` produces separate primary/heavy-weapon and pistol pickups. `DualPistols` produces two separate pickups: the heavy pistol and the light 9mm. Each retains its own weapon ID and server-owned remaining ammo.
- Pickups preserve the actual weapon type. Remaining ammo may be transferred according to the agreed server-side rule; never trust client-supplied ammo.
- The server checks pickup distance, obstruction rules, current ownership, replacement consequences and whether another player already claimed the pickup.
- Inventory transfer and world-pickup removal must be one atomic server operation to prevent duplication.
- Each elimination/drop event needs an idempotency guard. World pickups expire after a configured lifetime and are cleaned up on round teardown.
- A pickup that would violate the loadout restriction must replace an existing slot/package or be rejected; it must never silently add a third weapon slot.

## PvP-only scope

There are no PvE enemies, enemy bots or AI combatants. Target selection, damage, kill credit, bullet-time effects and weapon drops operate on eligible player characters only. Environmental objects can block shots and movement but are not combatants.


## Dual-pistol weapon identities

The dual-pistol package is specifically composed of two different pistols:

- **Heavy pistol (Desert-Eagle-style):** high damage per hit, strong recoil, slower cadence, small magazine and scarce reserve ammunition.
- **Light pistol (9mm-style):** lower damage per hit, lower recoil, faster follow-up shots, larger magazine and more plentiful reserve ammunition.

Prototype magazine targets: heavy pistol 7–8 rounds; light 9mm 15–17 rounds. These are initial tuning values only and must be validated through PvP playtests. Keep each pistol's magazine, reserve, fire cadence, reload and recoil state independent. When a dual-pistol player is eliminated, drop each pistol as its own world pickup; a player may claim either one subject to loadout replacement rules.


## Starting ammunition and scavenging

- Every weapon starts with one magazine/clip and no additional reserve ammunition.
- Dual-pistol starting ammunition is independent: Desert-Eagle-style heavy pistol starts with 8 rounds; light 9mm starts with one full magazine at its own configured capacity (initial target 15–17 rounds). No shared ammo pool.
- A player can collect ammunition from a weapon on the ground only when they carry the exact same weapon type. The server transfers only ammo actually remaining on the ground weapon and cannot duplicate it.
- See [[Weapon and Ammunition Pickup Mechanic]] and [[Drop Weapons on Death]] for full rules and acceptance tests.
