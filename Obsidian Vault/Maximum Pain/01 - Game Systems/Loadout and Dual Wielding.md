# Loadout and Dual Wielding

What a player carries and how they hold it: dual wielding and its cost, dropping and picking up guns, switching and reloads. Built 2026-10-31.
Related: [[Weapons and Recoil]] · [[Limb Health]] · [[Architecture]] · [[Max Payne 3 Mechanics Reference]]

## Slots
As in Max Payne 3, every player carries up to **two one-handed guns and one two-handed gun**.
| Slot | Key | Holds |
|---|---|---|
| Secondary | 1 | a one-handed gun |
| Tertiary | 2 | a one-handed gun |
| Primary | 3 | the two-handed gun |

The slots were called `OneA`, `OneB` and `Two` in the code until 2026-11-14, when they took the loadout screen's names ([[Menus, Loadout, Progression and Shop - To Do]]). The keys didn't move. The names are in `LoadoutRules` (`Slot`, `HoldMode`), each gun's `Slot` attribute, the character's `HoldMode` attribute, the `WeaponAction` remote's "Hold" value and `Keybinds` (`SlotSecondary`, `SlotTertiary`, `SlotPrimary`).

| One-handed (slots 1 and 2; can be dual wielded) | Two-handed (slot 3) |
|---|---|
| M9, Glock 18, Desert Eagle, S&W 500, Uzi, sawn-off | MP5, M500, SPAS-15, AK-47, FAL, M4, M107 |

- The Uzi is a one-arm SMG, so it is now one-handed. The MP5 stays two-handed.
- The sawn-off stays one-handed, as in Max Payne 3 (it already was in [[Limb Health]]). Change `OneHanded` in `WeaponConfig` to move it.
- Default loadout on every spawn: M9 (1), Uzi (2), AK-47 (3), with the M9 in hand.

## Holding
| Mode | Key | Right hand | Left hand |
|---|---|---|---|
| None | the drawn gun's key again | — | the two-handed gun, carried |
| Secondary or Tertiary | 1 or 2 | that gun | the two-handed gun, carried |
| Dual | 4 | gun 1 (Secondary) | gun 2 (Tertiary) |
| Primary | 3 | the two-handed gun (both hands) | — |

The mouse wheel and gamepad Y cycle through the single guns the arms can hold.
**The two-handed gun is never holstered.** While a one-handed gun is out it rides in the left hand, as in Max Payne 3. One-handed guns not in use sit in thigh holsters (gun 1 on the right thigh, gun 2 on the left).

**Carried by its middle** (since 2026-11-11): the left fist is round the gun halfway along its length, at the handguard's height, with the gun's length running front to back through it, like a bag's handle. `LoadoutService.carryOffset` works this out from each gun's own parts and `Support` point, and the carry clips are made for exactly that offset. Before, the gun hung from its pistol grip like a stick held at one end, and crouched or behind cover the carry clips pushed it into the legs and torso. Dual pistols are still held by their grips.

## Dual wielding and the drop penalty
- Press 4 to draw both one-handed guns. Both hands are then full, so **the two-handed gun is dropped on the floor** and stays there until someone picks it up. The keybind list warns in red, for example DROPS AK-47.
- Picking up or drawing a two-handed gun ends dual wielding: gun 2 goes back to its holster and the two-handed gun goes into the left hand or both hands.
- Firing alternates hands. Semi-automatic guns fire once per click; automatic guns keep firing while the trigger is held.
- Spread ×1.35 and recoil ×1.25 while dual wielding.
- Reloading both takes the longer reload time ×1.5 (M9 and Uzi: 3 s).
- Needs both arms: one arm in the red ends dual wielding.

## Switching
Drawing takes the gun's `DrawTime` (one-handed 0.3 s, two-handed 0.55 s, M107 0.7 s), and it can't fire until then. Switching cancels a reload.

**The two-handed gun changes hands partway through a switch** (since 2026-11-12), while both hands are on it:
- **Drawing it (3):** the left hand lifts it out of the carry by its middle, and the right hand takes it 40% of the way through the draw (`DrawTwoHanded`); both then bring it up to the ready hold.
- **Putting it back for a one-handed gun (1, 2):** the left hand takes it from the right 33% of the way through and lowers it into the carry; from 53% the right hand draws the one-handed gun from its holster (`SwapToOneHanded`).
- The server moves each gun at the same shares of the switch's time (`LoadoutRules.HANDOVER`, `LoadoutService.handOver`). Moved at the start, as before, the rifle jumped from one hand to the other (2.4 studs and 50° in one frame drawing it; putting it back it snapped round 90° or more). A switch cut short, or replaced by another, puts every gun where it belongs at once.
- The clips meet the hands on the gun for the default R15. On narrower avatars (83tg's shoulders are 0.26 narrower each side) the hands are about 0.4 apart at the handover, so `AimLayer` eases a gun that changed hands from where the old hand had it into its new grip over 0.12 s. IK that really meets the hands on any body is to-do 4.29.

## Dropping and picking up
- **G** drops the gun in the right hand (or the carried two-handed gun when nothing is drawn).
- Dropped guns lie on the floor with their ammo and a pickup prompt, and disappear after 45 s.
- **F** picks up the gun the prompt shows. The HUD says PICK UP X or SWAP Y FOR X.
  - One-handed: goes into an empty slot. With both full it replaces the gun in the right hand (or gun 1), which lands where the new one lay.
  - Two-handed: goes into slot 3, swapping out any carried one, and ends dual wielding.
  - With both arms in the red nothing can be picked up.
- Dying drops whatever was in the hands.
- The server checks the distance (8 studs), the stance (no pickups while diving, in cover, getting up or in a Last Stand) and the loadout rules.

## Reloads
- R reloads the gun or guns in use. The server times it and moves the ammo **only when the timer finishes**: up to a full magazine from the spare rounds.
- Switching, dropping, picking up, diving, getting up, a Last Stand or death cancel it, and nothing moves. Tested: a reload cut off by a switch left the Desert Eagle at 5/7; a full one gave 7/5.
- Reloading works while sprinting, crouched, in any cover pose and lying on the floor after a dive.
- Pulling the trigger on an empty gun reloads it.
- **With a two-handed gun carried**, a one-handed gun is reloaded by the right hand alone, against the belt at the right hip (since 2026-11-11): `ReloadPistolOneHand` (M9, Glock 18, Desert Eagle, Uzi), `ReloadRevolverOneHand` (S&W 500), `ReloadSawnOffOneHand`. The two-handed reloads bring the left hand over, and it brought the carried gun through the gun being reloaded. The one-handed clips have the same markers at the same times; dual wielding still uses `ReloadDual`.

## Arm injuries ([[Limb Health]])
| Arms | Effect |
|---|---|
| One arm in the red | A two-handed gun in use is dropped. Dual wielding ends (gun 2 is holstered). One-handed guns still work. A carried two-handed gun stays carried but can't be drawn. |
| Both arms in the red | Everything in the hands is dropped, including the carried two-handed gun. Nothing can be drawn or picked up. |

## How guns are built
Guns are **Models, not Tools**: a Roblox character can hold only one Tool, and dual wielding needs two guns in hand. `LoadoutService` clones each gun whole from `ServerStorage.WeaponKit` (so its own Motor6Ds keep working) and hangs it from a Motor6D: `RightGrip` (RightHand → Handle), `LeftGrip`, or `Holster` (thigh). Animations can move guns through these joints ([[Animation Hooks]]). Gun parts don't collide and can't be hit, so shots pass through to the body behind.

## Adding a new gun
1. Put the gun in `ServerStorage.WeaponKit` as a Tool with a `Handle` that has `Grip` and `Muzzle` attachments, and moving parts on Motor6Ds named Slide, Bolt or Pump if it has them.
2. Add an entry to `WeaponConfig` with the Tool's name, including `OneHanded`, `DrawTime` and `AnimSet`, plus a short name in `DisplayNames`. The module stops the game with a clear error if anything is missing.
3. Add an untextured icon copy to `ReplicatedStorage.Assets.UI.WeaponIcons` with the same name ([[HUD Layout]]).
4. Pick its reload clip in `AnimationConfig`: add it to `RELOADS` (ReloadPistol, ReloadRevolver, ReloadRifle, ReloadSniper, ReloadPump or ReloadSawnOff), and a one-handed gun to `ONE_HAND_RELOADS` too (its reload while a two-handed gun is carried). `AnimationConfig`'s self-check stops the game with a clear error if either is missing.
5. Nothing else: the [[Test Arena]] puts it on the gun table if there's a free spot. The table has 13 spots, so a 14th gun needs one more `Spot` attachment on `GunTable`.

`LoadoutRules` holds the slot, hold, pickup and arm rules and the switch's handover shares as pure functions, and checks itself when it loads (dual wielding drops the two-handed gun, a two-handed pickup ends dual wielding, one arm drops a two-handed gun in use, drawing the two-handed gun hands it over late, a one-handed switch hands nothing over).
