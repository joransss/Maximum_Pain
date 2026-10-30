# Weapon and Ammunition Pickup Mechanic

## Design intent

Players can recover weapons and ammunition from world pickups created by defeated players. Pickups retain a clear weapon identity; ammunition is only compatible with the same weapon type.

## Starting ammunition rule

- Each weapon starts with **one magazine/clip only** and no additional reserve ammunition.
- For the dual-pistol loadout, the Desert-Eagle-style heavy pistol starts with **8 rounds in its magazine**; the light 9mm starts with one full magazine at its configured capacity (initial target 15–17 rounds). The magazines are independent. Neither pistol receives an extra reserve clip at spawn.
- Each weapon's magazine and reserve are tracked independently. No weapon starts with a bonus reserve clip unless a future mode explicitly changes this rule.
- Exact magazine capacity is weapon-specific. Starting ammunition is one magazine per weapon, not one universal ammo amount.

## Weapon pickup behaviour

- Pickups represent a specific weapon type and preserve the server-recorded weapon identity and ammunition state.
- The server validates pickup distance, line of sight/obstruction rules, pickup availability, inventory revision and loadout compatibility.
- Picking up a weapon must obey `HeavyAndPistol` and `DualPistols` restrictions. It replaces a compatible slot/package or is rejected; it never creates an extra slot.
- A pickup can be claimed by one player only. The server commits the inventory change and removes/updates the pickup atomically.
- If the pickup is a weapon the player already carries, do not silently duplicate the weapon. Instead, treat it as an ammunition source under the ammo-pickup rules below, or reject it if no compatible ammo can be transferred.

## Ammunition pickup behaviour

- A player may collect ammunition from a weapon lying on the ground **only when it is the same weapon type** as a weapon in their current inventory.
- Weapon type matching uses the canonical weapon ID/type, not a broad category. For example, 9mm ammunition for the light 9mm pistol cannot refill the Desert-Eagle-style heavy pistol; ammunition for one rifle model does not automatically fit another unless explicitly configured as a shared ammo family.
- Transfer only the compatible ammunition actually available from the world weapon. The server calculates the transfer; clients cannot submit an ammo quantity.
- Ammunition transferred from a ground weapon is capped by the recipient weapon's configured reserve capacity, if reserve capacity is enabled. Excess ammunition remains on the ground or is discarded according to one consistent pickup rule. Do not exceed magazine/reserve limits.
- Do not grant ammunition twice: a successful transfer must update the ground weapon's remaining ammo and the player's ammo state in one atomic server transaction.
- If the player has no matching weapon type, they cannot take that weapon's ammunition as a standalone ammo refill. They may still pick up the weapon itself if loadout rules permit.
- Because players start with one magazine only, ammo scavenging from compatible dropped weapons is the intended way to replenish ammunition during a match.

## Server authority and anti-exploit requirements

- Server owns magazine count, reserve count, weapon identity, pickup state and transfer calculations.
- Reject pickups that are out of range, obstructed, already claimed, stale, or incompatible with the loadout.
- Use an atomic claim/transfer operation and an idempotency guard so concurrent requests cannot duplicate weapons or ammunition.
- All ammo values must remain finite, non-negative and within configured limits.

## Acceptance tests

- [ ] Every starting weapon has exactly one magazine and no bonus reserve ammunition.
- [ ] The dual-pistol loadout starts with independent magazines: 8 rounds for the heavy pistol and the configured full magazine for the 9mm.
- [ ] A player can take ammunition from a ground weapon only when carrying the exact matching weapon type.
- [ ] An incompatible pistol/rifle/weapon type cannot transfer ammunition.
- [ ] Ammo transfers never exceed configured capacity and cannot be claimed twice.
- [ ] A player without a matching weapon can take the ground weapon itself only if loadout rules allow it; they cannot take its ammo as a refill.
- [ ] Pickup distance, obstruction, race conditions and stale inventory requests are server-validated.

## Related notes

- [[Drop Weapons on Death]]
- [[Loadouts and Progression]]
- [[Weapon System]]
- [[Dual Wielding]]
- [[Server Authority Rules]]
