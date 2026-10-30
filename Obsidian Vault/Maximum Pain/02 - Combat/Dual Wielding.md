# Dual-Wield Sidearms

## Design Goal

Dual wielding uses **two different pistols**, not two copies of the same weapon:

- **Heavy pistol — Desert-Eagle-style:** high per-shot damage and strong recoil, but a small magazine and limited reserve ammunition.
- **Light pistol — 9mm-style:** lower per-shot damage, lower recoil and a larger magazine/reserve, making it the more sustainable and controllable weapon.

These are fictional weapon-role references, not a requirement to reproduce real-world weapon specifications. Use original in-game names, models, audio and animations.

The two pistols create a deliberate contrast: the heavy pistol rewards deliberate, well-placed shots, while the 9mm supports faster follow-up shots and sustained pressure. Dual wielding must not simply double the output of the best single pistol without meaningful trade-offs.

## Weapon Identity and Suggested Prototype Tuning

All values below are **starting hypotheses for playtesting**, not final balance commitments. Tune them against actual time-to-kill, hit rate and reload frequency in PvP.

| Attribute | Heavy pistol | Light 9mm pistol |
|---|---|---|
| Combat role | High-damage, deliberate shots | Fast, controllable follow-up fire |
| Damage per hit | Higher | Lower |
| Recoil/kick | High | Low to moderate |
| Magazine | Small (e.g. 7–8 rounds) | Larger (e.g. 15–17 rounds) |
| Reserve ammunition | Scarce | More plentiful |
| Fire cadence | Slower | Faster |
| Best use | Accurate opening/finishing shots | Sustained pressure and easier tracking |
| Main weakness | Misses are costly; frequent reloads | Lower damage per hit |

Do not balance the heavy pistol only through raw damage. Its recoil, fire cadence and scarce ammunition should create a genuine precision-versus-sustainability choice. Do not make the 9mm a strict upgrade by giving it both high capacity and near-equal damage.

## Dual-Pistol Loadout Rules

- The dual-pistol package contains exactly one heavy pistol and one light 9mm pistol.
- These are two distinct weapon IDs and two independently configured weapon instances.
- This package occupies the complete sidearm loadout choice and **cannot include a primary/heavy weapon** such as a shotgun, SMG, rifle or precision weapon.
- The term *heavy pistol* does not mean a primary/heavy weapon slot; it remains a pistol.
- Each pistol has its own magazine, reserve ammo, fire rate, recoil profile, reload state and server-owned ammo values.
- Each weapon starts with one magazine only and no extra reserve ammunition. For the dual-pistol package, the Desert-Eagle-style heavy pistol starts with 8 rounds; the light 9mm starts with one full magazine at its own configured capacity (initial target 15–17 rounds). These are independent magazines, not a shared `8 + 8` pool.
- Decide whether shots alternate between hands or can be fired independently. Recommended first prototype: each trigger input fires one pistol, alternating by default; explicitly test whether holding both inputs is allowed and enforce each pistol's fire cadence server-side.
- Reloading one pistol should not silently refill the other. Decide whether the player can reload one while firing the other; prototype with independent reload state only if the animation and input scheme can communicate it clearly.
- Dual-wield accuracy should deteriorate at medium/long range compared with aiming a single pistol. Keep the 9mm controllable, but do not remove the heavy pistol's recoil cost.

## Drops and Pickups

When a dual-pistol player is eliminated, **drop the two pistols as two separate world pickups**:

1. Heavy pistol pickup — preserves the heavy pistol's identity and server-recorded remaining magazine/reserve ammo.
2. Light 9mm pickup — preserves the 9mm's identity and server-recorded remaining magazine/reserve ammo.

The two drops are not a single paired pickup. A player can take either pistol individually, subject to the normal loadout rules. Picking up one pistol must not automatically grant the other. The dual-pistol player drops only weapons actually carried, and each pickup can be claimed by only one player.

A player in the `DualPistols` package who takes a primary/heavy weapon must leave the dual-pistol package and transition to `HeavyAndPistol`. The heavy weapon and a compatible single pistol must be obtained according to the replacement rules; the heavy pistol is a valid pistol-sidearm candidate if the game permits it. Taking a pistol while already using `DualPistols` should replace the matching pistol or follow a clear prompt—never create a third pistol slot.

The server must atomically validate pickup ownership, range, obstruction rules, inventory revision and ammo transfer. Client-provided ammo values are never trusted.

## Tasks

- [ ] Implement separate heavy-pistol and 9mm configurations.
- [ ] Track each pistol's magazine and reserve independently on the server.
- [ ] Spawn with one magazine per pistol and no bonus reserve ammo.
- [ ] Allow ammo scavenging only from a ground weapon of the exact same type.
- [ ] Choose and test alternating fire versus independent hand inputs.
- [ ] Add distinct recoil, fire cadence, sound, animation and reload feedback.
- [ ] Make the heavy pistol's limited ammunition meaningful without making it unusable.
- [ ] Test both pistols separately and as a pair at close, medium and long range.
- [ ] Drop two distinct pickups on elimination, preserving weapon identity and server-owned ammo.
- [ ] Verify that taking either pickup individually respects the current loadout package.

## Balance Rule

Dual wielding should offer flexibility and cinematic close-range pressure, not a free damage multiplier. The heavy pistol supplies burst damage at a cost; the 9mm supplies control and sustained fire at a cost. Validate the combined package against `HeavyAndPistol` using time-to-kill, hit rate, ammo consumption, reload downtime and win rate—not animation feel alone.


See [[Weapon and Ammunition Pickup Mechanic]] for matching-type ammo scavenging and [[Drop Weapons on Death]] for death-drop rules.
