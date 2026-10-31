# HUD Layout

Blueprint of the in-game HUD. The health figure and gun list copy the look of Max Payne 3's single-player HUD in your AK screenshots ([[Reference Images]]). The keybind list and prompts use the black-and-white tile style from [[Max Payne 3 HUD and Combat UI Reference]]. Built 2026-10-31, restyled the same day, then extended for loadouts, cover, shoot-dodge and Last Stand.
Related: [[Weapons and Recoil]] · [[Loadout and Dual Wielding]] · [[Limb Health]] · [[Last Stand and Bullet Time]] · [[Changelog]]

## Screen map
```
+----------------------------------------------------------------------+
|                         BULLET TIME (while slowed)                   |
|                                                                      |
|                      (o)  reticle (red X when blocked)               |
|                     NO ROOM TO STAND (short messages)                |
|                       LAST STAND  [=========    ]                    |
|                                                                      |
| [LMB] FIRE                                                           |
| ...                                                                  |
| [ 4 ] DUAL WIELD [DROPS AK-47]   [F] PICK UP M9          1 [M9]  15 15|
| [ G ] DROP GUN                   [E] TAKE COVER LOW      2 [UZI] 32 32|
| [ F ] PICK UP                         figure | bar       3 [AK]  30 30|
|                                       CROUCHED                       |
|                                       ONE ARM                        |
+----------------------------------------------------------------------+
  keybinds: bottom left   prompts: bottom centre   figure + guns: bottom right
```

## Style
- **Font:** Oswald (condensed, built into Roblox). Bold for keybinds, magazine counts, slot numbers and status text; regular for spare-ammo counts.
- **Colours:** white, black, mid grey `#A5A5A5` (spare ammo, slot numbers, guns not in hand), figure grey `#CDCDCD`, and red for danger only (limbs, status text, the reticle over a target).
- **Health figure and gun list:** no boxes, as in Max Payne 3. See-through grey 3D shapes with soft shading, and plain numbers with a faint shadow.
- **Keybinds:** flat black and white tiles.
- **Spacing:** 24 px from the screen edges. Both corner panels scale with screen height (1080 p = 1, limited to 0.75–1.25).

## Components
| Component | Position | Details |
|---|---|---|
| Reticle | Screen centre | A 4 px dot inside a ring with four outward ticks. The ring's radius shows the current spread with all the stance modifiers (minimum 6 px). Turns red over a living character. A red cross and grey reticle when the gun's path is blocked (the shot would hit the wall in front). Hidden when unarmed, scoped, or in a stance that can't fire (sprinting, getting up). |
| Scope overlay | Full screen | Round see-through lens, 90% of screen height, everything outside it black, thin black crosshair lines. Appears at 85% of the sniper's scope zoom with a 0.2 s fade from black. |
| Keybinds | Bottom left | Key in a white tile (56 px wide, black text), action in a black tile (white text), 22 px high. Read from the `Keybinds` module, so the list can't drift from the controls. A red warning tile can follow an action: DROPS AK-47 after DUAL WIELD while a two-handed gun is carried. |
| Prompts | Bottom centre | Same tiles: [F] PICK UP X, or SWAP Y FOR X when a slot is full, or CAN'T CARRY X; [E] TAKE COVER HIGH/LOW, or LEAVE COVER. Gun prompts are Roblox ProximityPrompts drawn by the HUD (Custom style), so they only show for guns on screen. |
| Short messages | Under the reticle | White text that fades after 1.4 s: NO COVER HERE, NO ROOM TO STAND, MOVE TO AN EDGE TO AIM, TOO HURT TO DIVE, SURVIVED - GET UP. |
| Health figure | Bottom right, left of the guns | A human figure 150 px tall, seen from behind the way the player sees their character, drawn in see-through grey (60% visible). Each limb fills red from its lowest part up as it takes damage, so a leg goes foot first, then shin, then thigh, and an arm goes hand first. The torso fills from the waist and the head tints as a whole. A limb in the red is red all over. |
| Painkiller count | On the figure's upper back | Bold black number in a white square, as in Max Payne 3. |
| Adrenaline bar | Right of the figure | White, 5 px wide, 85% of the figure's height, filling from the bottom with the `Adrenaline` attribute (0 to 1) over a faint track. Emptied by a survived Last Stand. |
| Stance tag | Under the figure | Small grey text: SPRINTING, CROUCHED, HIGH COVER, LOW COVER, PEEKING, AIMING FROM COVER, SHOOT-DODGE, ON THE FLOOR, GETTING UP, DEFENSELESS (after a Last Stand), LAST STAND. Hidden when standing. |
| Status text | Under the stance tag | Red bold text, no box: LIMPING, CRAWLING, ONE ARM, DISARMED, joined with " / ". Hidden when normal. |
| Gun list | Bottom right | Three fixed rows: 1 and 2 (one-handed), 3 (two-handed), 28 px high: slot number (small grey), the gun as a see-through grey side-on shape (muzzle pointing right), then the ammo written like Max Payne 3's "30 120" (magazine in bold white, spare rounds in grey). An empty slot shows a faint dash. |
| Guns in hand | In the gun list | Bright white (both one-handed rows when dual wielding). Other guns sit back at 60% in grey. |
| Gun the arms can't hold | In the gun list | Almost invisible (20%). |
| Reloading | In the gun list | The magazine number reads RELOAD in grey. |
| Last Stand | Centre, below the reticle | LAST STAND in red over a white bar that runs out with the window. |
| Bullet time | Top centre | BULLET TIME while this player is slowed. The screen also loses most of its colour and blurs slightly during bullet time and the player's own Last Stand. |

Roblox's own hotbar and health bar are switched off, since this HUD replaces both.

## How the 3D shapes are made
- **Figure:** `ReplicatedStorage.Assets.UI.HealthFigure` is Roblox's own "Man" body (bundle 238) with textures removed. It has 15 R15 body parts, named as usual (`LeftFoot`, `RightUpperArm`, and so on). The HUD tints each part separately.
- **Guns:** `ReplicatedStorage.Assets.UI.WeaponIcons` holds a plain, untextured copy of each gun from `ServerStorage.WeaponKit`. The HUD tints the whole view grey or white.
- Both are drawn in ViewportFrames with a narrow lens so they look flat, and lit softly for a little shading.
- **Adding a gun:** copy its parts into a new model in `WeaponIcons` (clear `TextureID`, white SmoothPlastic, anchored, `PrimaryPart` = Handle), named exactly like the gun's id in `WeaponConfig` (the kit Tool's name). The full checklist for a new gun is in [[Loadout and Dual Wielding]].

## Code
- The `Hud` module (StarterPlayerScripts.Controllers) draws everything. It only draws; it holds no game rules.
- `WeaponController` sends it the three slots (`Hud.setWeapons`), the reticle (`Hud.setReticle`, with the blocked flag), the scope zoom (`Hud.setScope`), the pickup prompt (`Hud.setPrompt`), the dual-wield warning (`Hud.setKeyHint`) and the stance tag (`Hud.setStance`).
- `CoverController` sends the cover prompt; `CharacterController`, `CoverController` and `DodgeController` send short messages (`Hud.flash`); `LastStandController` sends the countdown (`Hud.setLastStand`) and the bullet-time label (`Hud.setBulletTime`).
- The HUD reads the limb, painkiller and adrenaline attributes itself and updates when they change.

## Known limits
- The "Man" body is chunkier than Max's slim figure. A custom slimmer figure could be modelled in Blender and swapped in as `HealthFigure` with the same part names.
- Keyboard and mouse first. Gamepad: right stick to look, left stick to move, L2 aim, R2 fire, X reload, Y next gun, B crouch, L1 cover, R1 dive, R3 swap shoulder, L3 sprint, D-pad up painkiller, D-pad down pick up, D-pad left dual wield, D-pad right drop. **There are no touch controls, so phones and tablets can't play yet.**
- The keybind list now has 14 rows; it may need folding into a shorter list or a help screen later.
