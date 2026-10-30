# Drop Weapons on Death

## Design intent

When a player is eliminated in PvP, each weapon they carry becomes its own world pickup. Dropped weapons are also the source of compatible scavenged ammunition.

## Drop rules

- Create one separate pickup for each carried weapon at or near the elimination location, offset safely so it does not spawn inside the floor or a wall.
- `HeavyAndPistol` drops two separate pickups: the primary/heavy weapon and the sidearm.
- `DualPistols` drops two separate pickups: the Desert-Eagle-style heavy pistol and the light 9mm pistol. They are not a combined pickup; a player may claim either individually if loadout rules allow it.
- Preserve the exact weapon type and server-recorded remaining magazine/reserve state. Do not refill dropped weapons on death.
- Each weapon pickup is independently claimable by only one player. Picking up one pistol never grants the other pistol automatically.
- Pickup replacement must maintain the loadout rules. A player may not combine dual pistols with a primary/heavy weapon; the server must perform a valid package transition/replacement or reject the pickup.
- Use a unique elimination/drop identifier so duplicate death events cannot create duplicate weapons.
- A dropped weapon may be dropped again if its new owner is eliminated, but the inventory-to-world transfer must be atomic and protected against duplication loops. Use a short drop cooldown and configured maximum number of active pickups if needed.
- Initial proposed despawn lifetime: 30–45 seconds, subject to playtesting. Clean up pickups on round teardown.
- Dropped weapons are world pickups, not physics projectiles, and do not damage characters on contact.

## Ammunition rules for dropped weapons

- Every weapon starts with one magazine only and no extra reserve ammunition, unless a mode explicitly overrides this.
- Dropped weapons retain their actual remaining ammunition. This is important: a weapon that was emptied before its owner died must not become a full-ammo pickup.
- Players can scavenge ammunition from a dropped weapon only if they carry the exact same weapon type. The server transfers only ammunition that is actually present and does not duplicate it.
- An incompatible weapon can still be collected as a weapon if the recipient's loadout allows it; it cannot be used as an ammo refill for another weapon type.
- Ammo transfer from a dropped weapon must update the player's ammo and the ground pickup's remaining ammo atomically. If no transferable ammo remains, do not grant any.
- For the dual-pistol starting loadout, the heavy pistol starts with 8 rounds and the 9mm starts with one full magazine at its own configured capacity; these pools remain independent.

## Server implementation requirements

- Server authoritatively determines elimination, inventory contents, weapon identity, ammo state and drop location.
- Validate pickup range and obstruction; atomically claim, transfer and remove/update the pickup.
- Never trust client-provided weapon IDs or ammunition quantities.
- A weapon instance cannot exist in a player's inventory and in the world at the same time, nor be owned by two players.
- Validate loadout invariants after every pickup, ammo transfer, drop, elimination and respawn.
- On respawn, use the configured spawn loadout; do not restore the dropped weapons automatically.

## Acceptance tests

- [ ] A heavy-weapon-plus-pistol loadout drops two separate, correctly typed pickups on elimination.
- [ ] A dual-pistol loadout drops the Desert Eagle and 9mm as two independent pickups.
- [ ] Each pickup retains its remaining ammo; empty weapons do not respawn full on the ground.
- [ ] Starting loadout ammunition is one magazine per weapon, with no bonus reserve.
- [ ] Ammo can be scavenged only from the exact same weapon type.
- [ ] Concurrent pickup attempts cannot duplicate weapons or ammunition.
- [ ] Repeated elimination events do not create duplicate drops.
- [ ] Respawn does not restore weapons that were dropped.
- [ ] Dropped weapons expire after the configured lifetime and are removed on round teardown.

## Related notes

- [[Weapon and Ammunition Pickup Mechanic]]
- [[Loadouts and Progression]]
- [[Weapon System]]
- [[Dual Wielding]]
- [[Server Authority Rules]]
