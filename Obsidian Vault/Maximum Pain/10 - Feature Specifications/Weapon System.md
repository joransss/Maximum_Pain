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
