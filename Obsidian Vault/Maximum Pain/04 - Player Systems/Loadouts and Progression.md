# Loadouts and Progression

## Core loadout rule

Maximum Pain is a **PvP-only shooter**. A player chooses one of two mutually exclusive weapon packages:

1. **Heavy weapon + one pistol** — carry one primary-sized weapon (for example, a shotgun, assault rifle, SMG or precision rifle) and one sidearm.
2. **Dual pistols** — carry a pistol in each hand and no heavy/primary weapon.

The dual-pistol package is a deliberate alternative, not an extra slot. A player must never equip dual pistols and a heavy weapon at the same time. The loadout should create a meaningful choice between the range, capacity and role flexibility of a heavy weapon and the mobility/style of dual sidearms.

## Slot model

Represent the loadout as a server-validated package type rather than allowing arbitrary weapon combinations:

- `HeavyAndPistol`: `PrimarySlot` contains exactly one allowed heavy weapon; `SidearmSlot` contains exactly one pistol.
- `DualPistols`: contains exactly one heavy pistol (Desert-Eagle-style) and one light 9mm pistol; `PrimarySlot` is empty.

Treat `DualPistols` as one loadout package for slot restrictions, but store its two pistols as distinct weapon instances. The heavy pistol has high damage, strong recoil and scarce ammunition; the 9mm has lower recoil, a larger magazine and more reserve ammunition. Track each pistol's magazine, reserve, fire cadence and reload state independently. A heavy pistol is still a pistol and does not occupy the primary/heavy-weapon slot.

### Equip and switch rules

- Switching between the heavy weapon and the pistol is allowed only within `HeavyAndPistol`, subject to equip timing and any state restrictions.
- `DualPistols` is the heavy pistol plus light 9mm combination. Prototype with separate magazines and reserve pools so the heavy pistol's limited ammunition remains meaningful. Decide whether firing alternates between hands or uses separate inputs; server-validate each pistol's cadence independently.
- Picking up a heavy weapon while using `DualPistols` replaces the dual-pistol package with `HeavyAndPistol`. The player must also obtain a compatible pistol to complete the package; if the dropped heavy weapon is paired with a pistol drop from the same defeated player, the pickup flow can offer both as a package.
- Picking up a second heavy weapon while already using `HeavyAndPistol` must replace the current heavy weapon or be rejected. Never create an extra hidden slot.
- Picking up a pistol while using `HeavyAndPistol` replaces the sidearm only if the game supports pistol variants. It must not silently create dual wielding.
- A player may drop an equipped weapon voluntarily if enabled, but the resulting package must remain valid. Dropping the only heavy weapon can leave the player with a pistol-only fallback, but does not automatically grant dual pistols.
- All inventory changes are validated and committed by the server. The client can request a pickup/drop and show predicted UI, but cannot assert ownership or ammo.

## Defeated-player weapon drops

When a player is eliminated, their eligible carried weapons become world pickups that other players can collect. This is a central combat loop: winning a fight can change the winner's available weapon options.

### Recommended drop behaviour

- Drop each carried weapon separately at or near the elimination location, with a safe offset so it does not spawn inside a wall or floor.
- Drop the actual carried weapon types, preserving each weapon's remaining server-recorded ammunition. Never refill a weapon on death or trust client-provided ammo.
- If the defeated player had `HeavyAndPistol`, create one pickup for the heavy weapon and one for the pistol. If they had `DualPistols`, create two independent pickups: the Desert-Eagle-style heavy pistol and the light 9mm. Each can be looted individually, subject to loadout restrictions; taking one never grants the other.
- A pickup should communicate weapon name/type, ammo state if shown, and whether taking it will replace the player's current weapon or package.
- Use a short pickup prompt and explicit confirmation only where the replacement is consequential; avoid a lengthy menu in the middle of a firefight.
- A pickup can be claimed by only one player. The server atomically checks that it still exists, validates distance and line of sight if required, then transfers it and removes/updates the world pickup.
- Each weapon starts with one magazine only and no additional reserve ammunition. Dual pistols have separate magazines: the heavy pistol starts with 8 rounds; the light 9mm starts with one full magazine at its configured capacity (initial target 15–17 rounds).
- Players may scavenge ammo from a ground weapon only if they carry the exact same weapon type. The server transfers only ammunition actually remaining on that ground weapon; no compatible weapon means no ammo refill. See [[Weapon and Ammunition Pickup Mechanic]].
- Prevent pickup through walls, from excessive distances, or after the pickup has been claimed. Add a brief anti-race lock during the server transaction.
- If a player is eliminated while carrying a dropped weapon, follow one consistent rule: drop their current package again, or destroy it. Recommended: drop it again, subject to a short drop cooldown and a maximum number of world pickups to prevent duplication/exploit loops.
- Clean up unclaimed pickups after a configurable lifetime and on round/server teardown. Initial prototype lifetime: 30–45 seconds; tune in playtests.
- Dropped weapons must not be usable as physics projectiles or cause damage merely by touching a character.

### Death, respawn and persistence

- The eliminated player's dropped package is created once per elimination event. Use a unique elimination/drop identifier to prevent duplicate drops from duplicate event handling.
- On respawn, the player receives the mode's standard spawn loadout. Do not silently restore the old dropped weapons unless a game mode explicitly defines that rule.
- Decide the spawn loadout before balancing: recommended prototype is a reliable basic pistol for every player, with the heavy-weapon/sidearm and dual-pistol choices available through the spawn loadout selection or map pickups.
- If a player disconnects while alive, apply an explicit rule. Recommended: remove their character and inventory pickups rather than leaving free weapons indefinitely; if disconnect drops are desired, reuse the same validated drop path.
- Do not persist live-match weapon ownership across sessions. Persistent progression should be cosmetic or statistical unless a future mode has a clear reason to do otherwise.

## No PvE — explicit scope boundary

There are **no PvE enemies, hostile NPCs, enemy bots or AI combatants** in the intended game. Combat, eliminations, bullet-time target selection and weapon drops are player-versus-player systems. Training dummies or bots should not be added as ordinary gameplay targets without a deliberate scope change. Environment objects may block shots, affect movement or provide cover, but are not enemies.

Consequences for implementation:

- Target validation should identify living player characters, not NPC Humanoids generally.
- Bullet-time candidate selection should consider only eligible opposing players with server-verified line of sight.
- Kill credit, weapon drops and combat statistics should be tied to player-versus-player elimination events.
- Map props and physics objects are environmental interactions, not combatants.

## Server-side data model

Suggested inventory fields:

- `LoadoutType`: `HeavyAndPistol` or `DualPistols`
- `PrimaryWeaponId`: weapon ID or `nil`
- `SidearmWeaponId`: pistol ID or `nil`
- `DualPistolHeavyWeaponId`: heavy-pistol weapon instance ID or `nil`
- `DualPistolLightWeaponId`: light-9mm weapon instance ID or `nil`
- `AmmoByWeapon`: server-owned magazine/reserve state keyed by weapon instance or defined weapon slot
- `EquippedSlot`: currently active slot/package
- `InventoryRevision`: incremented on every successful equip, drop or pickup to reject stale requests

Enforce invariants after every inventory mutation:

- `HeavyAndPistol` has one valid heavy weapon and one valid pistol, except during a clearly defined pickup/replacement transaction or a supported pistol-only fallback state.
- `DualPistols` has exactly one heavy-pistol instance and one light-9mm instance, each with independent server-owned ammo, and no primary/heavy weapon.
- A weapon instance cannot be owned by two players or exist in both inventory and the world at once.
- Ammo is finite, non-negative and server-owned.

## Initial acceptance tests

- [ ] A player can spawn with `HeavyAndPistol` or `DualPistols`.
- [ ] The heavy pistol and light 9mm are distinct weapon IDs with different recoil, damage and ammunition profiles.
- [ ] Dual pistols and a primary/heavy weapon can never coexist in the same loadout.
- [ ] Dual-pistol ammo is tracked independently, and the two pistols drop as separate pickups on elimination.
- [ ] Each starting weapon has one magazine only; no extra reserve ammunition is granted at spawn.
- [ ] Ground-weapon ammo can be collected only by a matching weapon type, without duplication.
- [ ] Switching weapons does not duplicate, refill or lose ammo unexpectedly.
- [ ] Eliminating a player drops the correct carried package exactly once.
- [ ] A heavy-and-pistol loadout creates the intended two pickups; dual pistols create two distinct pickups (heavy pistol and light 9mm).
- [ ] Two players trying to take the same pickup cannot both acquire it.
- [ ] Pickup requests outside range, through blocked geometry or for already-claimed pickups are rejected.
- [ ] Pickup replacement preserves the loadout invariant and follows the chosen replacement rule.
- [ ] Respawn uses the defined spawn-loadout rule and does not restore weapons that were dropped.
- [ ] There are no AI enemies or PvE damage/loot pathways in the combat loop.

## Progression options for later

- Cosmetic unlocks and weapon skins that do not change hitboxes or weapon statistics.
- Match statistics and challenges.
- Weapon mastery that does not create severe pay-to-win advantages.

## Related notes

- [[Weapon System]]
- [[Weapon and Ammunition Pickup Mechanic]]
- [[Drop Weapons on Death]]
- [[Weapons and Recoil]]
- [[Combat Architecture and Implementation Plan]]
- [[Server Authority Rules]]
