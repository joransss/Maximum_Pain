# HUD Layout

Blueprint of the in-game HUD. The health figure and gun list copy the look of Max Payne 3's single-player HUD in your AK screenshots ([[Reference Images]]). The keybind list uses the black-and-white tile style from [[Max Payne 3 HUD and Combat UI Reference]]. Built 2026-10-31, restyled the same day.
Related: [[Weapons and Recoil]] · [[Limb Health]] · [[Changelog]]

## Screen map
```
+---------------------------------------------------------------------+
|                                                                     |
|                          (o)  reticle, screen centre                |
|                               (sniper: round scope overlay)         |
|                                                                     |
| [LMB] FIRE                                         1  [pistol]  15 15|
| [RMB] AIM                                          2  [pistol]  17 17|
| [ R ] RELOAD                                          ...           |
| [SHI] SPRINT                         figure   |      0  [AK, bright] 26 30|
| [ Q ] SWAP SHOULDER                  [3] on   |      ...           |
| [ H ] PAINKILLER                     its back |                     |
| [1-0] WEAPON SLOT                    ONE ARM                         |
| [WHL] NEXT WEAPON                                                    |
+---------------------------------------------------------------------+
  keybinds: bottom left      health figure + bar      gun list: bottom right
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
| Reticle | Screen centre | A 4 px dot inside a ring with four outward ticks. The ring's radius shows the current spread (minimum 6 px). Turns red over a living character. Hidden when unarmed or scoped. |
| Scope overlay | Full screen | Round see-through lens, 90% of screen height, everything outside it black, thin black crosshair lines. Appears at 85% of the sniper's scope zoom with a 0.2 s fade from black. |
| Keybinds | Bottom left | Key in a white tile (56 px wide, black text), action in a black tile (white text), 22 px high. |
| Health figure | Bottom right, left of the guns | A human figure 150 px tall, seen from behind the way the player sees their character, drawn in see-through grey (60% visible). Each limb fills red from its lowest part up as it takes damage, so a leg goes foot first, then shin, then thigh, and an arm goes hand first. The torso fills from the waist and the head tints as a whole. A limb in the red is red all over. |
| Painkiller count | On the figure's upper back | Bold black number in a white square, as in Max Payne 3. |
| Slim bar | Right of the figure | White, 5 px wide, 85% of the figure's height. **Placeholder for the bullet-time meter**: it always shows full until bullet time exists. |
| Status text | Under the figure | Red bold text, no box: LIMPING, CRAWLING, ONE ARM, DISARMED, joined with " / ". Hidden when normal. |
| Gun list | Bottom right | One row per gun, top to bottom in slot order, 28 px high: slot number (small grey), the gun as a see-through grey side-on shape (muzzle pointing right), then the ammo written like Max Payne 3's "30 120" (magazine in bold white, spare rounds in grey). |
| Gun in hand | In the gun list | The gun shape and numbers are bright white. Other guns sit back at 60% in grey. |
| Gun the arms can't hold | In the gun list | Almost invisible (20%). |
| Reloading | In the gun list | The magazine number reads RELOAD in grey. |

Roblox's own hotbar and health bar are switched off, since this HUD replaces both.

## How the 3D shapes are made
- **Figure:** `ReplicatedStorage.Assets.UI.HealthFigure` is Roblox's own "Man" body (bundle 238) with textures removed. It has 15 R15 body parts, named as usual (`LeftFoot`, `RightUpperArm`, and so on). The HUD tints each part separately.
- **Guns:** `ReplicatedStorage.Assets.UI.WeaponIcons` holds a plain, untextured copy of each gun from `ServerStorage.WeaponKit`. The HUD tints the whole view grey or white.
- Both are drawn in ViewportFrames with a narrow lens so they look flat, and lit softly for a little shading.
- **Adding a gun:** copy its parts into a new model in `WeaponIcons` (clear `TextureID`, white SmoothPlastic, anchored, `PrimaryPart` = Handle), named exactly like the Tool.

## Code
- The `Hud` module (StarterPlayerScripts.Controllers) draws everything. It only draws; it holds no game rules.
- `WeaponController` sends it each gun's slot key, magazine, spare rounds, and whether it is reloading, in hand or usable (`Hud.setWeapons`). It also sends the reticle size and colour (`Hud.setReticle`) and the scope zoom (`Hud.setScope`).
- The HUD reads the limb attributes itself and recolours the figure when they change.

## Known limits
- The "Man" body is chunkier than Max's slim figure. A custom slimmer figure could be modelled in Blender and swapped in as `HealthFigure` with the same part names.
- The bullet-time bar is a placeholder until bullet time is built.
- Keyboard and mouse first. Gamepad works for the basics: right stick to look, L2 aim, R2 fire, X reload, Y next weapon, R3 swap shoulder, L3 sprint, D-pad up painkiller. **There are no touch controls, so phones and tablets can't play yet.**
- With all 13 test guns the list is tall; real loadouts will be shorter.
- The keybind list is written by hand. When a control changes, update it in `Hud` too.
- Slot numbers follow the list order. When a gun drops, the numbers below it move up, and the labels move with them.
