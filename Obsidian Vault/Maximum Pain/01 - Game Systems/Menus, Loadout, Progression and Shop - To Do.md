# Menus, Loadout, Progression and Shop: To Do

Plan and work queue for everything outside the fight: the main menu, the Max Payne 3-style menu look, loadouts and items, skills (Max Payne 3's "Bursts", renamed), levels, titles and cash, the skin shop and crates, and settings. Written 2026-11-10. **Planning only: nothing here has been built yet.**
Related: [[Loadout and Dual Wielding]] · [[Last Stand and Bullet Time]] · [[Limb Health]] · [[HUD Layout]] · [[Architecture]] · [[Gun Skin Ideas]] · [[Max Payne 3 Game Modes - Roblox Engagement]] · [[Max Payne 3 HUD and Combat UI Reference]] · [[Blender and Asset Pipeline]] · [[Multiplayer Networking Research]] · [[Networking and Security]]

> [!important] Ground rules for everything in this note
> - **Original content only.** Max Payne 3 is the reference for *how it feels*, not for names, art, fonts or text. Every Burst, item and title below gets our own name (proposals are in each table). Real gun names (M9, AK-47) are fine, as now.
> - **The server owns levels, XP, cash, unlocks, crates and purchases.** The client only *asks* ("equip loadout 2", "buy skin X", "open crate Y"); the server checks and decides. See [[#9. Server-side economy and anti-exploit]].
> - **UI art is made in Blender** (backgrounds, panels, icons, crates, logo, badges), rendered to images and imported into Roblox. See [[#3. Blender for the UI]].
> - **Every menu shows the live match behind it** (from the mockups): a camera watching the current match on the current map.
> - Wiki numbers below were read on 2026-11-10 from the three Max Payne Wiki pages in [[#Sources]] (community wiki, not official; marked 📰).

---

## Reference screenshots

### Our mockups (the plan to follow)
![[Mockup - Main Menu.png]]
**Main menu.** Title "Maximum Pain" top left, then **Play, Shop, Settings, Loadout** in a column inside a left panel. Right side (most of the screen): a live view of the map currently being played.

![[Mockup - Loadout.png]]
**Loadout.** **Primary / Secondary / Tertiary are the three weapon slots**: between them, **one two-handed and two one-handed** guns (Primary = the two-handed gun, Secondary and Tertiary = the one-handed guns; see [[#5. Loadout]]). Loadout weight: Light, Medium or Heavy. Bursts, **renamed "Skills"**. The live match plays in the background.

![[Mockup - Shop.png]]
**Shop.** Cash balance top left of the panel (`$0000`). Two wide skin cards and one tall featured skin card in the middle, three crates in a column on the right. Under the title: a note that **skins give no advantage**. Live match in the background.

### Max Payne 3 references (look and layout only)
Kept in `Attachments/Menus/Max Payne 3/` and **committed to the repo** so collaborators see them. They are design references only: nothing in them goes into the game.

![[MP3 - Main Menu.png]]
**Max Payne 3 main menu.** What to take: a full-screen, dark, desaturated cinematic backdrop; the menu as a short uppercase list on the left third; a big bold heading (MAIN MENU) above it; **a one-line description of the highlighted item above the heading**; the highlighted item is a **solid white bar with black text** running about a third of the screen wide; soft out-of-focus light blobs (bokeh) and blur behind the list; button prompts (SELECT, SOCIAL CLUB) small, bottom right, with a key/button icon.

![[MP3 - Story Menu.png]]
**Max Payne 3 sub-menu.** Same layout one level deeper: hint line, heading (STORY), list, greyed-out unavailable item (CONTINUE), a gap before a separate group (GRINDS), and **SELECT ↵ / BACK ESC** bottom right. Warm, dim lamp lighting, grain.

![[MP3 - Loadout Screen.png]]
**Max Payne 3 loadout screen.** Character posed with their gun on the left half. On the right: a **dark panel with a grey body silhouette inside a radial ring**; items hang off it with thin leader lines (head gear at the head, armour at the chest, gear at the waist), handguns on the left, the two-handed gun lower right, throwable lower left, the Burst icon bottom right. A **LOADOUT WEIGHT** bar at the bottom with tick marks, and the class under it (HEAVY: slow health regen and low stamina).

![[MP3 - Bursts Summary.png]]
**Bursts summary** (search result screenshot). Superseded by the full per-level table in [[#6. Skills (Max Payne 3's Bursts, renamed)]].

---

## 0. Decisions to make first
- [x] **Primary / Secondary / Tertiary are weapon slots** (decided 2026-11-10). Primary = the two-handed gun, Secondary and Tertiary = the two one-handed guns, matching the built rule in [[Loadout and Dual Wielding]]. **Saved loadouts** are a separate layer on top: several named sets of those slots plus items and a skill.
- [ ] **How many saved loadouts?** Max Payne 3 had **5 custom** + 4 presets. 📰 Proposed: 5 custom slots, the first 3 free and slots 4–5 unlocked at levels 10 and 25.
- [ ] **Level cap:** 50 (as Max Payne 3) or 100? This plan uses **50**, plus a prestige track.
- [ ] **Prestige reset:** Max Payne 3's Legend wiped guns, items, upgrades, cash and earned weight. That's harsh for Roblox (players quit). Proposed: reset level and unlocks only, **keep cash, skins and titles**. Decide.
- [ ] **Crates bought with what?** Proposed: earned Cash only at launch (see [[#10. Shop (skins and crates), Roblox compliant]]). Selling Cash for Robux later turns every crate into a paid random item with all the rules.
- [x] **Skill and title names:** placeholders set (section 6 and section 8). Final names later; ids in config stay the same when names change.
- [ ] **Join flow:** does a new player land on the main menu over a live match (as the mockups suggest) and press Play to spawn? Proposed: yes.

**Open questions added 2026-11-10 (loadout weight, skills, titles):**
- [x] **Two-handed size bonus: yes.** Two-handed guns get +2 weight on top of the stat score (decided 2026-11-10).
- [x] **Same gun twice: yes.** Secondary and Tertiary may hold the same gun (e.g. two Desert Eagles for dual wielding). Assumed: owning the gun once covers both slots.
- [x] **Weight classes change: health regen, stamina and aiming speed.** Walk speed and dive distance stay the same for every class.
- [ ] **Weight allowance by level:** keep a cap that grows with level, or let the Heavy penalties be the only limit?
- [x] **Skill prices: Cash to unlock once the required level is reached** (Max Payne 3's way). Starter skills at level 1 stay free, since new players have no Cash.
- [x] **Bullet Time free from level 1: yes.**
- [ ] **Stats display:** bars + numbers (planned), or numbers only?
- [ ] **Titles:** players pick any unlocked title (planned), or always show the latest?
- [x] **Level and title on enemies' name tags: only at close distance** (placeholder ~60 studs, and only in line of sight). Teammates always see them.

---

## 1. Main menu shell (live match behind every menu)
- [ ] **Menu state on join:** the player joins, their character is *not* spawned (`Players.CharacterAutoLoads = false`, spawn on Play via the server), and the menu opens over the live match.
- [ ] **Live match camera ("viewpoint of the current map being played"):**
  - [ ] Options, in order of effort: (a) slow cinematic dolly between a set of `MenuCam` parts placed per map; (b) spectate a random living player from a chase camera, switching every ~8 s or on their death; (c) mix: dolly, cut to a player when a kill happens nearby.
  - [ ] Start with (a), it never shows anything broken; add (b) later.
  - [ ] **StreamingEnabled:** the menu camera may be far from where the (unspawned) player is, so the map there might not be streamed in. Use `Player:RequestStreamAroundAsync(position)` on the server for each camera point, or set `Player.ReplicationFocus` to a part at the camera. Test with streaming on.
  - [ ] The menu camera is client-only (`Camera.CameraType = Scriptable`), so it can't leak or change anything.
- [ ] **Left panel (mockup):** game title, then Play, Shop, Settings, Loadout. Proposed order: **PLAY, LOADOUT, SHOP, SETTINGS** (most-used first), plus a small player card at the bottom (name, level, title, cash).
- [ ] Each button opens its screen *over the same live background*; BACK (Esc / B) returns. One `MenuController` on the client owns the stack of screens (open, back, close-to-play).
- [ ] Pressing Play: the client asks; the server checks the chosen loadout and spawns the character with it; the menu fades out.
- [ ] **In-match pause menu:** Esc during a match opens a smaller version (Resume, Loadout (applies on next spawn), Settings, Leave). Roblox's own Esc menu: bind our menu to another key or to the in-game menu button, check `GuiService.MenuIsOpen`.
- [ ] Death screen → after the kill cam ([[Max Payne 3 Kill Cam]]) offer **Change Loadout** before respawn, as Max Payne 3 does.

---

## 2. Making the UI feel like Max Payne 3
How the menus should look and behave. This is the "feel" brief; the Blender section says how the pieces get made.

### What makes Max Payne 3's menus recognisable
1. **The background is the star.** Full-screen moody imagery; the UI is a thin layer on top. Our version: the live match, colour-graded.
2. **Left-aligned text list**, uppercase, condensed bold sans-serif, white on dark. No buttons with borders, no rounded corners, no icons in the list.
3. **Selection = a solid white bar, black text.** Hard edges, instant or very fast (≈0.08 s) slide between rows. Unselected rows plain white. Unavailable rows mid grey.
4. **Context line above the heading:** one short sentence describing the highlighted option ("Jump into the match on this map"). Changes as the selection moves.
5. **Big heading** for the current screen (MAIN MENU, STORY): larger, bold, slightly letter-spaced.
6. **Prompts bottom right:** `SELECT [↵]  BACK [ESC]` (or the gamepad button), small, white. Swap to gamepad glyphs when `UserInputService` reports a gamepad.
7. **Film look:** grain, vignette, slight desaturation with teal shadows and warm highlights, soft bokeh blobs, a little blur behind the text column.
8. **Glitch transitions:** Max Payne 3 cuts between scenes with a horizontal tear / chromatic split / brief flicker. Use sparingly: screen changes and big moments (rank up, crate opening). **Turn off with "Reduce motion"** ([[#11. Settings and accessibility]]).
9. **Loadout as a body diagram:** the silhouette-in-a-ring layout from the loadout screenshot.
10. **Sound:** a soft tick on hover, a heavier click on select, a low ambient music bed. No bouncy or cartoon sounds.

### Our version, concretely
- [ ] **Font:** keep **Oswald** (already the HUD font, [[HUD Layout]]): Bold for headings, list items and prompts; Regular for the context line and descriptions. One family across HUD and menus.
- [ ] **Colours:** reuse the HUD palette: white, black, mid grey `#A5A5A5`, red for danger/locked only. Add one accent for the shop and rarities (decide; keep it muted).
- [ ] **Left panel:** in the main menu mockup it's a boxed white panel. To feel like Max Payne 3, make it **a dark, see-through gradient** (black 70% → 0% to the right) instead of a white box, with the list on it. Keep the mockup's position and proportions (left ~40%).
- [ ] **Colour grade on the live view while a menu is open:** client-side `ColorCorrectionEffect` (saturation −0.5, contrast +0.1, tint toward teal), `BlurEffect` size ~6 only behind the left panel area (or on the whole view, lighter), `DepthOfFieldEffect` for the bokeh feel. Remove them all when the match starts.
- [ ] **Overlays (made in Blender, see section 3):** a tiling grain texture animated by offsetting it every frame, a vignette image, a few bokeh/light-leak images that drift slowly.
- [ ] **Animation:** `TweenService` for the selection bar (Quad Out, 0.08 s), screen fade (0.2 s), glitch transition made from 3–4 offset copies of the frame with red/cyan tint for ~0.15 s.
- [ ] **Navigation:** fully playable with mouse, keyboard (arrows / W S, Enter, Esc) and gamepad (`GuiService.SelectedObject`, `NextSelectionUp/Down`). Touch later.
- [ ] **Scaling:** build in `Scale` with `UIAspectRatioConstraint` and a `UIScale` driven by screen height (same rule as the HUD: 1080 p = 1, clamp 0.75–1.25). Test 16:9, 21:9, 4:3, and a phone.
- [ ] **What not to copy:** the Max Payne 3 logo, Max or any character, Rockstar's fonts and icons, Social Club, the exact wording of menu hints, narration lines. All art and text is ours.

---

## 3. Blender for the UI
All non-text UI art is made in **Blender**, rendered to PNG and uploaded. This keeps the menus looking 3D and cinematic without live `ViewportFrame` cost.

- [ ] **New folder** `Assets/Blender/UI/` with one `.blend` per asset group: `UI_Logo.blend`, `UI_Icons_Weapons.blend`, `UI_Icons_Items.blend`, `UI_Icons_Skills.blend`, `UI_Crates.blend`, `UI_Badges.blend`, `UI_Overlays.blend`, `UI_LoadoutBody.blend`.
- [ ] **A render script** (`ui_lib.py`, like `mp_lib.py` for animations): opens a `.blend`, renders every object in a collection one by one through a fixed camera to `Exports/UI/<name>.png`, deterministic, so re-running gives identical files.
- [ ] **Render setup:** orthographic camera, transparent film (`Film > Transparent`), Eevee for speed, a soft three-point light rig shared by all icons, render at 2× the on-screen size and no bigger than **1024 px** (Roblox texture limit to check), PNG RGBA.
- [ ] **Naming:** `UI_` prefix on every object and export (`UI_Icon_AK47`, `UI_Crate_Street`, `UI_Title_Badge_10`), matching CLAUDE.md's prefix rule.
- [ ] **What to make:**
  - [ ] **Logo:** "MAXIMUM PAIN" as an extruded, scuffed metal or worn-print title, rendered flat-on. Variants: full, compact.
  - [ ] **Weapon icons:** side-on, muzzle right (same as the HUD gun list), white and grey versions. Reuse the gun meshes from `ServerStorage.WeaponKit` / the gun `.blend`s.
  - [ ] **Item icons** (helmet, gas mask, goggles, armour, gear) and **skill icons** (one per skill, simple bold silhouettes that read at 48 px).
  - [ ] **Loadout body:** a grey human silhouette inside a radial ring (our own design, inspired by the loadout screenshot), rendered as a single image; slot positions recorded as UV coordinates so the Roblox UI places icons and leader lines on it.
  - [ ] **Crates:** 3D crate models (wooden ammo crate, police evidence box, metal case…) rendered closed, open, and as a short image sequence for the opening animation (sprite sheet).
  - [ ] **Title/level badges:** a patch or stamp per milestone, shown next to names (see section 8).
  - [ ] **Overlays:** grain tile (256 px, seamless), vignette, bokeh blobs, light leaks, glitch strips.
  - [ ] **9-slice panels:** panel frames rendered flat and used with `ImageLabel.ScaleType = Slice` so they stretch cleanly.
  - [ ] Optional: a slimmer **HUD health figure** (already listed under Known limits in [[HUD Layout]]).
- [ ] **Import into Roblox:** upload as images (Asset Manager or Open Cloud), store IDs in one `UiAssets` module (`ReplicatedStorage.Modules`) so nothing hard-codes an asset ID.
- [ ] **Pre-rendered images vs ViewportFrames:** use images for menus (cheap, any number). Keep `ViewportFrame` only where it must react live (the HUD figure tinting limbs, a rotating skin preview in the shop).
- [ ] Add the UI pipeline to [[Blender and Asset Pipeline]] when it's built.

---

## 4. Play
- [ ] **PLAY** spawns into the current server's match with the selected loadout.
- [ ] Sub-menu (later): mode list from [[Max Payne 3 Game Modes - Roblox Engagement]] (Deathmatch, Team Deathmatch, then objective modes), quick play, server list, private servers.
- [ ] Show for the current match: mode, map, time left, score, players. The context line says "Join the match on <map>".
- [ ] Team pick (auto-balance on the server; the client can only ask).
- [ ] Spawn protection for a few seconds after Play.

---

## 5. Loadout
### Weapon slots: Primary, Secondary, Tertiary
From the mockup: the three boxes are weapon slots, and together they hold **one two-handed gun and two one-handed guns**.
| Mockup slot | Holds | In-game key | Slot name in code today ([[Loadout and Dual Wielding]]) |
|---|---|---|---|
| **Primary** | the two-handed gun (rifle, shotgun, SMG, sniper) | 3 | `Two` |
| **Secondary** | one-handed gun 1 (pistol, revolver, one-handed SMG, sawn-off) | 1 | `OneA` |
| **Tertiary** | one-handed gun 2 | 2 | `OneB` |
- [ ] Rename the slots in the UI only (Primary / Secondary / Tertiary); keep the code names, or rename `Two/OneA/OneB` everywhere at once. Decide.
- [ ] Consider re-mapping keys so **1 = Primary** (shooter convention) — affects `Keybinds`, the HUD gun list order and muscle memory from play tests. Decide.
- [ ] A slot can be left empty (lighter weight). Dual wielding (key 4) uses Secondary + Tertiary and still drops the Primary, as built.
- [ ] **The same gun may go in Secondary and Tertiary** (decided 2026-11-10), e.g. two Desert Eagles. Owning the gun once covers both slots. Each copy counts its own weight (two Desert Eagles = 6). Check that `LoadoutRules`, pickups and the HUD gun list handle two guns with the same id (they key some things by gun name today).
- [ ] Each slot's picker only lists guns that fit it (the two-handed list for Primary, the one-handed list for the other two), read from `WeaponConfig.OneHanded`.

### Saved loadouts
A **saved loadout** = Primary + Secondary + Tertiary + throwable + Head + Chest + Gear item + Skill, with a name. Max Payne 3 let players build **up to five** custom loadouts and choose one before each spawn. 📰
- [ ] **5 custom loadouts** (proposal in section 0), plus the **4 presets** below, read-only, which can be copied into a custom slot.
- [ ] Loadout screen: a list of saved loadouts down the left (PRESET: RIFLEMAN … CUSTOM 1 … CUSTOM 5, locked ones greyed with "LEVEL 10"), the selected one's details on the right.
- [ ] Actions: **Select** (use on next spawn), **Edit**, **Copy** (preset → custom), **Rename** (if allowed), **Reset**.
- [ ] Choosing a loadout is possible from: the main menu Loadout screen, the death screen (before respawn), and the pause menu. A change during a life **applies on the next spawn**.
- [ ] Remember the last selected loadout in the profile, so Play uses it straight away.
- [ ] Unlocking: if a saved loadout contains something no longer owned (e.g. after a prestige reset), the server swaps that slot for the default and the screen flags it in red.
- [ ] Saved on the server (section 9); the server re-checks the whole loadout every time it spawns the player, not only when it was saved.

### Screen layout
- [ ] Follow the mockup's text: **Primary / Secondary / Tertiary** weapon slots, **Loadout Weight**, **Skill**, plus the saved-loadout list.
- [ ] Use the loadout screenshot's structure for the selected loadout: left = our character posed with the chosen Primary; right = the body-in-a-ring diagram with slots: Head, Chest, Gear, Secondary, Tertiary, Primary, throwable, Skill; weight bar along the bottom.
- [ ] Selecting a slot opens a list of everything that fits it: icon, name, short stats (damage, fire rate, accuracy, magazine), weight, lock state ("UNLOCKS AT LEVEL 20", "$2,500").
- [ ] Live match in the background (same grade as other menus).
- [ ] Loadout name editable? If yes, filter the text with `TextService:FilterStringAsync` on the server. Simpler: fixed names.
- [ ] Preset loadouts for new players (our originals, inspired by Max Payne 3's four presets):
  - **Rifleman:** Light Vest; Primary AK-47; Secondary M9, Tertiary S&W 500; frag grenade; skill **Hot Lead**. Weight 9 + 2 + 2 + 1 + 1 = **15, Medium**.
  - **Scout:** Soft Soles; Secondary Uzi only; flashbang; skill **Gut Feeling**. Weight 2 + 1 = **3, Light**.
  - **Breacher:** Ammo Pouch; Primary Mossberg 500; Secondary M9; frag grenade; skill **Second Wind**. Weight 4 + 2 + 1 + 1 (pouch) = **8, Light**.
  - **Marksman** (level 3): Stitches; Primary FN FAL; Secondary S&W 500; flashbang; skill **Hot Lead**. Weight 8 + 2 + 1 = **11, Medium**.

### Gun rules (already built, keep)
- Up to two one-handed guns and one two-handed gun per loadout ([[Loadout and Dual Wielding]]). The server already checks this in `LoadoutRules`; the loadout screen must use the same module, so the screen can never allow what the server refuses.
- A loadout may leave a slot empty (lighter weight).

### Gun stats shown on the loadout screen
When the player opens a weapon slot and highlights a gun, a stats panel shows next to the list. Every number is **read from `WeaponConfig`** (the same numbers the server fires with), never typed into the UI, so a balance change updates the screen by itself.
- [ ] **Bars (0–100)**, drawn like the HUD style (white fill on a faint track, Oswald labels):
  | Bar | Worked out from (`WeaponConfig` fields) | Rating formula |
  |---|---|---|
  | **Damage** | `Damage × Pellets` (one shot, body) | `min(100, Damage × Pellets)` |
  | **Fire rate** | `RPM` | `min(100, RPM ÷ 12)` (1,200 RPM = full bar) |
  | **Accuracy** | `BaseSpread`, `SpreadPerShot`, `AimSpreadScale` | `100 ÷ (1 + x)`, x = aimed first-shot spread + half the aimed bloom per shot + 0.1 × hip spread |
  | **Range** | `Range` (studs) | `100 × ln(Range ÷ 50) ÷ ln(30)` (50 studs = 0, 1,500 = full) |
  | **Control** | `RecoilClimb` | `100 ÷ (1 + RecoilClimb ÷ 1.5)` (less kick = longer bar) |
- [ ] **Numbers** under the bars: Fire mode (SEMI / AUTO), Hands (ONE-HANDED, can dual wield / TWO-HANDED), Magazine (`15 + 15 spare`), Reload (`1.6 s`), Draw time (`0.3 s`), Headshot (`×2`), damage per second (body), and **Weight** (big, with its effect on the loadout's class).
- [ ] **Compare with what's equipped:** while highlighting a different gun, each bar shows the difference: the extra part in white with a `+`, the missing part in red with a `−` (colourblind modes swap the red; see section 11). The Weight number shows `9 → 11 (MEDIUM → HEAVY)` when the change would move the loadout to another class.
- [ ] **Locked guns** still show their stats (so players know what they're working toward), greyed, with "UNLOCKS AT LEVEL X" or the price.
- [ ] A short description line per gun (fire mode, role: "Close range, two shells, can dual wield").
- [ ] Skins never change any stat or weight (the shop says so too).
- [ ] Ratings and weight are computed by one shared function (e.g. `WeaponMath.ratings(gunId)` and `WeaponMath.weight(gunId)` in ReplicatedStorage), so the loadout screen and the server always agree.

### Gun weight, worked out from the stats
**Rule: a gun's weight comes from how strong its stats make it, plus its size (one- or two-handed).** Stronger and bigger guns weigh more, so a loadout full of the best guns pays for it in regen and stamina. Retuning a gun in `WeaponConfig` changes its weight automatically; nobody types weights in by hand.

1. **Lethality** = ½ × damage-per-second rating + ½ × Damage rating. DPS rating = `min(100, DPS ÷ 3)` with DPS = `Damage × Pellets × RPM ÷ 60` (body hits). Counting both stops fast weak guns and slow heavy hitters from looking free.
2. **Ammo per magazine** rating = `min(100, MagSize × Damage × Pellets ÷ 8)` (damage in one magazine).
3. **Power** = 0.35 × Lethality + 0.20 × Accuracy + 0.20 × Range + 0.15 × Ammo per magazine + 0.10 × Control.
4. **Weight** = `round((Power − 40) ÷ 4)` + **2 if two-handed**, minimum 1.

With today's numbers ([[Weapons and Recoil]], 2026-11-10):
| Gun | Hands | Damage | Fire rate | Accuracy | Range | Control | DPS | Power | **Weight** |
|---|---|---|---|---|---|---|---|---|---|
| Sawn-off | One | 100 | 25 | 12 | 5 | 25 | 650 | 45.9 | **1** |
| M9 | One | 22 | 33 | 64 | 53 | 62 | 147 | 48.2 | **2** |
| S&W 500 | One | 65 | 10 | 49 | 57 | 27 | 130 | 49.0 | **2** |
| Uzi | One | 14 | 79 | 49 | 44 | 73 | 222 | 49.5 | **2** |
| Glock 18 | One | 14 | 92 | 55 | 47 | 73 | 257 | 49.7 | **2** |
| Desert Eagle | One | 50 | 17 | 52 | 61 | 33 | 167 | 51.0 | **3** |
| Mossberg 500 | Two | 96 | 6 | 19 | 26 | 30 | 112 | 46.1 | **4** |
| SPAS-15 | Two | 80 | 20 | 17 | 26 | 41 | 320 | 53.1 | **5** |
| MP5 | Two | 16 | 67 | 61 | 53 | 77 | 213 | 54.7 | **6** |
| FN FAL | Two | 34 | 33 | 67 | 73 | 48 | 227 | 64.8 | **8** |
| M4 | Two | 22 | 62 | 72 | 68 | 73 | 275 | 67.5 | **9** |
| AK-47 | Two | 26 | 50 | 68 | 68 | 67 | 260 | 68.2 | **9** |
| Barrett M107 | Two | 95 | 8 | 75 | 100 | 20 | 142 | 76.9 | **11** |

What the table says, worth checking in play tests:
- The order feels right: sidearms 1–3, shotguns and SMG 4–6, rifles 8–9, the sniper 11.
- **The sawn-off is the lightest gun** (huge close damage, but 2 shells, no range, no accuracy). That suits a dual-wield gimmick; if it plays too strong, raise its weight by hand (see the override below).
- Shotgun DPS assumes every pellet hits, so close-range shotguns may deserve more weight than the formula gives.
- **Override:** `WeaponConfig` may hold an optional `WeightOverride` for a gun that the formula gets wrong. Use it rarely and write down why.

### Loadout weight (Light / Medium / Heavy)
In Max Payne 3, everything you carry has weight, and the total sets the class. The screenshot shows HEAVY = slow health regeneration and low stamina. 📰 The wiki also says Legend resets "earned loadout weight", so the weight you're allowed grew with rank.
- [ ] **Guns:** weight from their stats (above). **Items and throwables:** fixed weights in `ItemConfig`: Riot Helmet 1, Light Vest 1, Plate Carrier 2, Heavy Plates 4, Street Clothes 0, gear 0 (Ammo Pouch 1), each throwable 1.
- [ ] **Total** = Primary + Secondary + Tertiary + throwables + items. Examples: pistols only (M9 + Glock + vest) = 5; the default spawn (AK + M9 + Uzi + vest + frag) = 15; the heaviest possible (M107 + two Desert Eagles + Heavy Plates + helmet + Ammo Pouch + frag) = 24.
- [ ] Classes (placeholder, tune in play tests): **Light ≤ 10, Medium 11–17, Heavy ≥ 18**.
- [ ] Effects. **Decided: weight changes health regen, stamina and aiming speed only**; walk speed and dive distance are the same for every class. Numbers are placeholders:
  | Class | Health regen delay | Regen rate | Sprint stamina | Aim-in time (hip → aimed) |
  |---|---|---|---|---|
  | Light | 3 s | ×1.25 | ×1.3 | ×0.85 (faster) |
  | Medium | 4 s | ×1.0 | ×1.0 | ×1.0 |
  | Heavy | 5 s | ×0.75 | ×0.7 | ×1.2 (slower) |
- [ ] **Aiming speed** = how long the camera takes to zoom in **and** the server's aim settle time (today a fixed 0.15 s, [[Weapons and Recoil]]): both × the class factor, so a Heavy player's tighter aimed spread really comes later. The sniper scope's second push scales too.
- [ ] Needs a **stamina** system for sprinting (not built yet, check [[Movement State Machine]]) and **health regeneration** rules alongside [[Limb Health]].
- [ ] **Weight allowance by level:** a cap that rises with level (e.g. 18 at level 1 → 24 at level 40) so new players can't carry everything heavy. Shown as the empty end of the weight bar. (Open question: keep it, or let the Heavy penalties be the only limit?)
- [ ] The server computes weight and class from the gun and item IDs with the shared functions; the client only displays the same calculation.

### Guns to add (Max Payne 3's multiplayer list, for ideas)
From the wiki. Our current guns: M9, Glock 18, Desert Eagle, S&W 500, Uzi, sawn-off (one-handed); MP5, M500, SPAS-15, AK-47, FAL, M4, M107 (two-handed).
| Class | In Max Payne 3 | Ideas for us |
|---|---|---|
| Melee | Night stick, cattle prod, pepper spray, stun gun | A baton and a taser as a melee/quick-use slot (needs melee system) |
| Handguns (all dual-wieldable) | PT92, 608 Bull, Auto 9mm, M1911, .38 revolver, DE .50 | Add a .38 revolver, M1911, a machine pistol |
| SMGs | M10, M972, Micro 9mm (dual-wieldable); MPK, SAF .40 (two-handed) | Add a MAC-10 style one-handed SMG; a second two-handed SMG |
| Shotguns | Sawed-off (dual), auto shotgun, M4 Super 90, M500, Super Sport, SPAS-15 | Add a semi-auto shotgun |
| Rifles / MGs | AK-47, FAL, MD-97L, G6 Commando, LMG .30, RPD, M4, others | Add an LMG (heavy weight) |
| Marksman / sniper | Mini-30, FMP G3S, M82A1, M24 | Add a marksman rifle and a bolt-action |
| Launchers | Grenade launchers, LAW, RPG, rotary GL | Only as pickups or skill rewards (see Trigger Happy L3), not in loadouts |
| Throwables | Tin can, flash, smoke, tear gas, frag, molotov | Frag, flashbang, smoke, tear gas, molotov, a decoy (tin can) |
- [ ] **Throwable slot:** one type per loadout, 1–2 of them. Needs a grenade system (throw arc, cook, bounce, damage per limb).
- [ ] **Attachments (later):** Max Payne 3 guns had attachments (a skill removes them). Ideas: suppressor (quieter, no minimap ping, less damage at range), red dot / scope, extended magazine, laser (tighter hip spread), flashlight. Unlocked per gun by kills with that gun.
- [ ] **Unlock levels** for every gun (spread out to level 40, as Max Payne 3 unlocked all guns by 40), and a **Cash price** to buy after unlocking (Max Payne 3 did both).

### Items (3 slots: Head, Chest, Gear)
Max Payne 3 allows **at most 3 items**: one head, one chest, one gear. 📰 Full list from the wiki, with our proposed name and what our game needs before it can work.

**Head slot**
| Max Payne 3 item | Effect | Unlock / cost | Our name (proposed) | Needs |
|---|---|---|---|---|
| Helmet | Head damage −50% | L4, $1,000 | **Riot Helmet** | Fits [[Limb Health]] directly (head limb) |
| Gas Mask | Immune to tear gas | L4, $2,000 | **Respirator** | Tear gas |
| Military Goggles | Immune to flashbangs; spot booby-trapped bodies | L4, $2,000 | **Tinted Goggles** | Flashbang, booby traps |
| Balaclava | Extra adrenaline for non-melee kills from behind | L4, $1,000 | **Ski Mask** | "From behind" check (angle between victim's look and shot) |
| Gorilla Mask | Extra adrenaline for melee kills from behind | DLC | **Party Mask** | Melee |

**Chest slot**
| Max Payne 3 item | Effect | Unlock / cost | Our name | Needs |
|---|---|---|---|---|
| Light Body Armor | Chest damage −15% | L1 | **Light Vest** | Torso limb in [[Limb Health]] |
| Urban Camo | Name and map position less visible | L4, $2,000 | **Street Clothes** | Name tags, minimap |
| Medium Body Armor | Chest −25%, back −10% | L20, $4,000 | **Plate Carrier** | Front/back hit check on the torso |
| Heavy Body Armor | Chest −33%, back −25% | L40, $3,000 | **Heavy Plates** | Same; heaviest weight |

**Gear slot**
| Max Payne 3 item | Effect | Unlock / cost | Our name | Needs |
|---|---|---|---|---|
| Pill Bottle | Carry 3 painkillers | Pre-order | **Pill Case** | Painkillers (built) |
| Listening Device | Detects nearby enemy movement; protects the minimap from false info | Pre-order | **Scanner** | Minimap; counters Grounded |
| Ammunition Pouch | Max ammo +50%; unlimited ammo in Last Stand | L1 | **Ammo Pouch** | Built systems ([[Last Stand and Bullet Time]]) |
| Bounty Orders | Extra cash for killing the top player on the scoreboard | L4, $1,500 | **Contract** | Scoreboard |
| Lockbox | Keep painkillers on death | L4, $1,000 | **Hip Flask** (or Lockbox) | Painkillers |
| ID Cards | Protects your team from team-confusing effects | L4, $1,000 | **Badges** | Counters Paranoia, Sneaky |
| Manufacturer's Guarantee | Protects your weapons from effects that damage them | L4, $1,000 | **Warranty** | Counters Weapon Double-Dealer |
| Field Bandages | Faster health regeneration | L4, $700 | **Bandages** | Health regen |
| Sutures | Health starts regenerating 25% sooner | L4 | **Stitches** | Health regen |
| Sneakers | Quieter movement | L1 | **Soft Soles** | Footstep audio and its range |
| Walkie Talkie | Your map shows enemies spotted by teammates | L4, $500 | **Radio** | Minimap, spotting |
| Autoinjector | Extra adrenaline for kills; no adrenaline loss from enemy effects | L4, $2,000 | **Epi Pen** | Counters Burst Bubble |
| Vampire Fangs | Health for kills | L20, $1,000 | **Bloodlust** | — |
| Multi-Tool | Faster objective interactions | L20, $1,000 | **Multi-Tool** | Objective modes |
| Spray Can | Capture territory faster | L20, $1,000 | **Spray Can** | Territory mode |
| Tracking Device | Vendetta target always on your map | L20, $2,000 | **Tracker** | Vendettas, minimap |
| Quick Holster | Faster reload and weapon switch | L20, $4,000 | **Quick Draw** | Built (`DrawTime`, reload times) |
| Sticky Tape | Grenades stick where they land | L40, $2,000 | **Duct Tape** | Grenades |
| Hollowpoint Rounds | Victims you kill take longer to respawn | L40, $2,500 | **Overkill Rounds** | Respawn timer |
| Pacemaker | Auto bullet time in Last Stand using adrenaline | L40, $3,000 | **Pacemaker** | Built (Last Stand + bullet time) |
| Pocket Watch | Enemy bullet time affects you as friendly | L40, $3,000 | **Stopwatch** | Built bullet time; counters it |
| Badge of Honor | More cash per prestige | At prestige 1 | **Old Badge** | Prestige (section 8) |
| Light Fingers | Faster looting | DLC | **Light Fingers** | Looting |
| Lucky Coin | Extra cash when looting | DLC | **Lucky Coin** | Looting |
| Booby Trap | Your body explodes when looted | DLC | **Rigged** | Looting, explosions |

- [ ] **First wave** (works with what's built): Riot Helmet, Light Vest, Plate Carrier, Heavy Plates, Pill Case, Ammo Pouch, Quick Draw, Pacemaker, Stopwatch, Bandages, Stitches.
- [ ] **Looting bodies** is a Max Payne 3 mechanic several items and adrenaline depend on (loot a body for painkillers, ammo, adrenaline). Plan it as its own system.
- [ ] **Minimap** is needed by Street Clothes, Scanner, Radio, Tracker and two skills. Plan it as its own system.
- [ ] Items are data in an `ItemConfig` module (id, slot, weight, unlock level, price, effect values). Effects applied on the server only.

---

## 6. Skills (Max Payne 3's Bursts, renamed)
### How adrenaline powers them (Max Payne 3) 📰
- The adrenaline meter has **three segments**, filled by kills and looting bodies.
- Each full segment is one **level** of the burst (1 to 3).
- Using the burst **spends all full segments**; timed bursts drain over their duration, instant ones empty at once.
- **Full segments are kept on death; a part-filled segment is lost.**
- One burst per loadout. Bursts unlock by level; each level of a burst unlocks separately (e.g. Bullet Time L1 at rank 6, L2 at 11, L3 at 18), then most cost cash to buy.
- When a burst fires, a narrator line plays ("Time was definitely not on their side.") — ours would be **original lines** or on-screen text.

### What we have now
- `Adrenaline` attribute 0 to 1: +0.004 per damage point, +0.25 per kill; bullet time needs one third; a survived Last Stand empties it ([[Last Stand and Bullet Time]]).
- [ ] **Change to three segments** (0–3 internally, or keep 0–1 with thresholds at 1/3, 2/3, 1), draw the HUD bar as three blocks, apply "lose the part-filled segment on death".
- [ ] Decide how Last Stand's cost fits: it currently takes all adrenaline. Keep, or take one segment?
- [ ] Bullet time today is triggered directly; make it **one skill** among many, chosen in the loadout. Line-of-sight bullet time is already built, which matches Max Payne 3's rule below.
- [ ] Activation key (e.g. **Q** / gamepad L3+R3 or D-pad), shown on the HUD with the skill icon and current level.

### Every Burst, level by level 📰
Unlock column = rank needed for Level 1 / 2 / 3.

| MP3 Burst | Level 1 | Level 2 | Level 3 | Unlock | Cost | Countered by | Our name (proposed) |
|---|---|---|---|---|---|---|---|
| **Trigger Happy** | Armour-piercing ammo for 20 s | Grants an LMG and a .50 pistol, more accuracy | Grants a rotary grenade launcher with extra ammo | 1/2/3 | Free | Weapon Double-Dealer; Big Dog vs L1 | **Hot Lead** |
| **Intuition** | Spotter flares above the enemy team | You see enemies any teammate can see | Your whole team sees every enemy | 1/2/3 | Free | — | **Gut Feeling** |
| **Big Dog** | Heals you and nearby teammates | All *visible* teammates | All teammates | 1/2/3 | Free | Deadly Force | **Second Wind** |
| **Bullet Time** | Slow time for 2.5 s | 4 s | 6 s | 6/11/18 | Free | Pocket Watch; break line of sight (dive, cover) | **Bullet Time** (generic term; or **Dead Slow**) |
| **Paranoia** | Enemies see their own teammates as enemies | + friendly fire and a bounty on one enemy | + friendly fire and bounties on the whole enemy team | 7/9/13 | $1,000 | ID Cards | **Trust Issues** |
| **Sneaky** | You look friendly to enemies for 10 s | 30 s | Until you die | 8/25/34 | $1,000 | ID Cards | **Turncoat** |
| **Grounded** | You vanish from the enemy map for 10 s | Your team vanishes for 20 s | Enemy map scrambled with false info | 14/19/29 | $2,000 | Listening Device | **Off the Grid** |
| **Fresh Blood** | You and 5 teammates respawn with bonus health | More health + adrenaline | More of both | 27/30/35 | $3,000 | Deadly Force; Burst Bubble | **Reinforcements** |
| **Weapon Dealer** | Team uses no ammo for 10 s | 20 s | + incendiary ammo | 32/39/43 | $3,000 | — | **Open Tab** |
| **Burst Bubble** | Enemies can't gain adrenaline or use bursts for 20 s | Team adrenaline +16.5%, enemies −16.5% | Doubles both | 37/41/46 | $3,000 | Autoinjector | **Dead Air** |
| **Weapon Double-Dealer** | Enemies lose all attachments | Enemies lose spare ammo | Enemies drop their grenades, primed | 42/45/48 | $3,000 | Manufacturer's Guarantee | **Sabotage** |
| **Unstoppable** (DLC) | Damage taken −40%, can't run, 10 s | More armour | More armour | 1/1/1 | DLC | — | **Bulletproof** |
| **Hangover** (DLC) | 6 enemies respawn with less health, stamina, blurred vision | Longer, stronger | Longer, stronger | 1/1/1 | DLC | — | **Bad Morning** |
| **Deadly Force** (DLC) | Your damage +50% for 6 s | +100% | Team also +50% | 1/1/1 | DLC | Big Dog; avoid them | **Heavy Hand** |
| **Explosives** (DLC) | Booby-traps every body for the enemy | HE ammo for 10 s | Drops an explosive near visible enemies | 1/1/1 | DLC | Military Goggles (see traps) | **Short Fuse** |
| **Slippery Character** (DLC) | Instant smoke + unlimited stamina 20 s | Lasts until death; visible enemies flashed | L1 and L2 for the whole team | 1/1/1 | DLC | — | **Smoke and Mirrors** |

**Bullet Time's line-of-sight rule** (matches what we built): whoever triggers it slows anyone they see, anyone who sees them, and anyone who sees an affected player. Friendlies get the benefit, enemies the slowdown; players far away aren't affected. Diving or ducking behind cover breaks it. 📰

### Our skills: placeholder names and level locks
**Placeholder names**, to swap for final ones later (the `SkillConfig` id stays the same when a name changes). Every skill is **locked behind levels**: one unlock level per skill level, on our 1–50 scale. Last skill level unlocks at 48, as in Max Payne 3.

| # | Skill (placeholder) | Based on | What it does (short) | Lv 1 unlocks at | Lv 2 at | Lv 3 at | Price after unlock | Needs first |
|---|---|---|---|---|---|---|---|---|
| 1 | **Bullet Time** (working name) | Bullet Time | Slows enemies in line of sight: 2.5 / 4 / 6 s | 1 | 6 | 12 | Free | Built |
| 2 | **Hot Lead** | Trigger Happy | Armour-piercing rounds → a heavy MG and pistol → a grenade launcher | 1 | 3 | 5 | Free | Armour items; skill-granted guns |
| 3 | **Second Wind** | Big Dog | Heal you + nearby team → visible team → whole team | 1 | 4 | 7 | Free | Health regen |
| 4 | **Gut Feeling** | Intuition | Flares over enemies → see what teammates see → team sees all enemies | 2 | 5 | 8 | $500 | Minimap for Lv 2–3 |
| 5 | **Heavy Hand** | Deadly Force | +50% damage for 6 s → +100% → team +50% | 4 | 10 | 16 | $1,000 | — |
| 6 | **Bulletproof** | Unstoppable | −40% damage taken, can't sprint, 10 s → more → more | 6 | 11 | 17 | $1,000 | Stamina/sprint lock |
| 7 | **Trust Issues** | Paranoia | Enemies see teammates as enemies → + friendly fire, one bounty → bounties on all | 8 | 13 | 19 | $1,500 | Own team field, name tags |
| 8 | **Turncoat** | Sneaky | You look friendly to enemies 10 s → 30 s → until death | 10 | 22 | 32 | $1,500 | Own team field, name tags |
| 9 | **Smoke and Mirrors** | Slippery Character | Instant smoke + endless stamina 20 s → until death, flash visible enemies → whole team | 13 | 18 | 24 | $2,000 | Smoke, flash, stamina |
| 10 | **Off the Grid** | Grounded | Off the enemy map 10 s → team 20 s → enemy map shows false dots | 15 | 20 | 28 | $2,000 | Minimap |
| 11 | **Short Fuse** | Explosives | Booby-trap bodies → explosive rounds 10 s → bomb drops near visible enemies | 18 | 25 | 31 | $2,500 | Looting, explosions |
| 12 | **Bad Morning** | Hangover | Next 6 enemy respawns: less health, stamina, blurred view → stronger → stronger | 21 | 27 | 33 | $2,500 | Respawn hooks |
| 13 | **Reinforcements** | Fresh Blood | You + 5 teammates respawn with bonus health → + adrenaline → more of both | 26 | 30 | 36 | $3,000 | Respawn hooks |
| 14 | **Open Tab** | Weapon Dealer | Team uses no ammo 10 s → 20 s → + fire rounds | 30 | 38 | 43 | $3,000 | — |
| 15 | **Dead Air** | Burst Bubble | Enemies can't gain adrenaline or use skills 20 s → drain them, feed your team → double | 37 | 41 | 46 | $3,000 | Adrenaline segments |
| 16 | **Sabotage** | Weapon Double-Dealer | Enemies lose attachments → spare ammo → drop primed grenades | 42 | 45 | 48 | $3,000 | Attachments, grenades |

How the locks work:
- [ ] **Decided: reaching the Lv 1 unlock level makes the skill buyable with Cash; buying it makes it equippable.** Before that level it shows in the list, greyed, with "LEVEL 15" and its description; after it, with its price and a BUY button. The three level-1 starters (Bullet Time, Hot Lead, Second Wind) are free, since new players have no Cash. Bullet Time is free from level 1 (decided).
- [ ] Purchase goes through the server's `BuySkill` remote: level reached, not owned, enough Cash; deduct and grant in one profile update (same pattern as `BuyItem`, section 9).
- [ ] **Lv 2 / Lv 3** unlock by level with no extra price. If a player fills 3 adrenaline segments but only owns Lv 1 of their skill, it fires at **Lv 1 and spends only 1 segment** (the rest stays). The HUD shows the highest usable level, not just the segments.
- [ ] Level-up screen lists new skill levels ("SECOND WIND LV 2 UNLOCKED").
- [ ] The server checks the skill and level on equip **and again on every activation** (from the profile, not from the client).
- [ ] Spread on purpose: by level 10 a player has 4 skills and the first two at Lv 3; the team-faking and map skills come in the 10–30 range; the strongest team-wide ones are late.
- [ ] Every number (durations, %s, levels, prices) lives in `SkillConfig` so it can be tuned without touching code.

### Notes for building skills
- [ ] **Order:** (1) Bullet Time (exists), (2) Second Wind / Big Dog (healing, simple), (3) Hot Lead L1 (armour-piercing = ignore armour items), (4) Heavy Hand, (5) Gut Feeling L1 (flares as a Highlight/Billboard over enemies), (6) Open Tab, (7) Bulletproof. Then the ones needing a minimap, team-faking or attachments.
- [ ] **Data-driven:** `SkillConfig` (id, name, icon, per-level values, unlock levels, price, counters) in ReplicatedStorage; `SkillService` on the server activates, applies timed effects, and replicates state through attributes (`ActiveSkill`, `SkillEndsAt`); clients only draw.
- [ ] **Status effects system** first: a small server module for timed effects with stacking rules (damage multiplier, damage taken multiplier, infinite ammo, revealed, hidden from map…). Most skills and items become rows of effects.
- [ ] **Team faking (Trust Issues, Turncoat):** Roblox's `Player.Team` replicates to everyone, so an exploiter would always see the true team. Use **our own team field the server sends per viewer** for name tags, reticle colour and friendly-fire, so the server can tell each client a different "truth". Friendly-fire rules live in the damage code on the server.
- [ ] **Counters** are item checks in the effect code: e.g. Trust Issues skips players whose team has someone with Badges.
- [ ] **Balance for Roblox:** shorter matches and smaller lobbies than Max Payne 3, so durations and team-wide effects may need trimming. Make every number a config value.
- [ ] **Feedback:** skill activation shows a full-screen tint and a line of narration text (original), plus a kill-feed note ("PlayerName used Second Wind").
- [ ] **Skill challenges** (Max Payne 3 "Grinds"): e.g. use a skill 5/25/75/150 times for 25/100/250/500 XP; trigger level 1/2/3 skills; earn 500/1,000/10,000/25,000 adrenaline. Feed into XP (section 8).

---

## 7. Challenges ("Grinds")
- [ ] Max Payne 3 had tiered challenges (bronze, silver, gold, platinum) for nearly everything, each paying XP. 📰 We call them **Challenges** (or **Jobs**).
- [ ] Per weapon (kills, headshots, kills while diving), per skill (uses, kills during it), per mode, general (adrenaline earned, painkillers used, Last Stands survived).
- [ ] Challenge progress counted by the server from real events, saved in the profile. Also drives the weapon mastery skins in [[Gun Skin Ideas]].
- [ ] A Challenges screen (later), reachable from the main menu or the player card.

---

## 8. Levels, titles and cash multipliers
### Max Payne 3, for reference 📰
- **50 ranks.** XP from kills, assists, challenges, feuds and vendettas. Ranking up gives cash and unlocks guns, items, skills, avatar items, titles.
- **Legend (prestige):** at rank 50 you may reset to rank 1, up to **10 times** (500 ranks total). Each Legend takes away guns, items, upgrades, cash and earned loadout weight, and gives a new title, a unique avatar, and a higher **cash multiplier** through the Badge of Honor gear: Legend 1 = 120%, then +20% each, up to Legend 10 = 300%.
- **Titles:** one per few ranks (14 rank titles from rank 1 to 50, Brazilian military ranks), one per Legend (10), plus achievement titles (all weapons, all bursts, all items, all avatar items, all weapons max rank, all achievements). Titles are shown to other players.

### Our level system (the request: milestones give a cash multiplier and a title others can see)
- [ ] **Levels 1–50.** XP to go from level L to L+1: `500 + 100 × (L − 1)` (placeholder): level 2 needs 500 XP, level 49 → 50 needs 5,300; about 142,000 XP for 1→50. Tune so level 50 takes ~40–60 hours.
- [ ] **XP sources (server-counted):**
  | Event | XP |
  |---|---|
  | Kill | 100 |
  | Assist (≥25% of the damage) | 50 |
  | Headshot kill | +25 |
  | Kill while shoot-dodging / in bullet time | +25 |
  | Kill from Last Stand | +50 |
  | Revenge kill (killed your last killer) | +25 |
  | Skill used | 10 per level |
  | Match finished | 200 |
  | Match won | +300 |
  | Challenge tier | per challenge |
- [ ] **Cash sources:** a share of XP (e.g. Cash = XP ÷ 4) at match end, plus level-up rewards, then × the player's **cash multiplier**.
- [ ] **Milestones every 5 levels** give a new title and a cash multiplier step. All titles below are **placeholders** (ids like `title_lv20` stay when names change):
  | Level | Title (placeholder) | Cash multiplier |
  |---|---|---|
  | 1 | Nobody | ×1.00 |
  | 5 | Lowlife | ×1.05 |
  | 10 | Gunhand | ×1.10 |
  | 15 | Bruiser | ×1.15 |
  | 20 | Enforcer | ×1.20 |
  | 25 | Hired Gun | ×1.25 |
  | 30 | Fixer | ×1.30 |
  | 35 | Shot Caller | ×1.35 |
  | 40 | Kingpin | ×1.40 |
  | 45 | Untouchable | ×1.45 |
  | 50 | Maximum Pain | ×1.50 |
- [ ] **Prestige ("Notoriety", placeholder name, 1–10):** at 50, reset to level 1 for a permanent bonus: +10% on the cash multiplier per Notoriety, a title, a badge, and a mastery skin finish at 5 and 10. Decide what resets (decision 0). The Notoriety bonus stacks with the level bonus (Notoriety 3 at level 40 = ×1.40 + 0.30 = ×1.70).
  | Notoriety | Title (placeholder) | Bonus on top of the level multiplier | Extra |
  |---|---|---|---|
  | 1 | Wanted | +0.10 | Badge 1 |
  | 2 | Marked Man | +0.20 | Badge 2 |
  | 3 | Feared | +0.30 | Badge 3 |
  | 4 | Notorious | +0.40 | Badge 4 |
  | 5 | Infamous | +0.50 | Badge 5, mastery finish |
  | 6 | Most Wanted | +0.60 | Badge 6 |
  | 7 | Street Legend | +0.70 | Badge 7 |
  | 8 | Ghost Story | +0.80 | Badge 8 |
  | 9 | Myth | +0.90 | Badge 9 |
  | 10 | Immortal | +1.00 | Badge 10, top mastery finish |
- [ ] **Achievement titles** (placeholders, unlocked by the server when it sees the condition):
  | Title (placeholder) | Condition |
  |---|---|
  | Arsenal | Every gun unlocked |
  | Wired | Every skill unlocked (all levels) |
  | Fully Stocked | Every item unlocked |
  | Workhorse | Every challenge at its top tier |
  | Gunsmith | Every gun at its top mastery skin |
  | Ten Lives | Survive 100 Last Stands |
  | Airborne | 500 kills while shoot-dodging |
  | Slow Motion | 500 kills during bullet time |
  | Dead Eye | 1,000 headshot kills |
  | Two Fisted | 1,000 kills while dual wielding |
  | Top Dog | Finish #1 on a season leaderboard (seasonal, dated) |
  | Founder | Played during the first month (limited) |
- [ ] Players **choose which unlocked title to show** (in Loadout or a Profile screen). The server checks the title is unlocked.
- [ ] **Where others see it:** the overhead name tag (`BillboardGui`: level badge + name + title). **Decided: enemies see it only up close** (placeholder 60 studs, `MaxDistance`) and only in line of sight, never through walls; teammates always see it, the scoreboard (Tab: level, name, title, K/D, score), the kill feed, the kill cam death panel ("Killed by [Kingpin] PlayerName"), lobby/player card. Respect Turncoat and Street Clothes (they hide or fake parts of the tag).
- [ ] **Level-up moment:** big centred "LEVEL 20 – ENFORCER", glitch transition, sound, unlock list (new guns, items, skill levels). Shown at match end so it doesn't block the fight; a small toast during the match.
- [ ] Roblox **badges** (`BadgeService`) for level 10/25/50 and first prestige (optional, good for discovery).
- [ ] Titles are fixed strings we wrote, so no text filtering needed. Never let players type a title.

---

## 9. Server-side economy and anti-exploit
**Rule: the client can never give itself XP, cash, levels, items or skins.** Values are computed on the server from events the server itself saw.

- [ ] **Profile on the server** (`ProfileService` / `DataService` module in ServerScriptService):
  ```
  Profile = {
    Version, Level, XP, Cash, Notoriety, TitleSelected,
    TitlesUnlocked = {}, Unlocks = { Guns, Items, Skills = { id = levelOwned } },
    Loadouts = { [1..5] = { Name, Primary, Secondary, Tertiary, Throwable, Head, Chest, Gear, Skill } },
    SelectedLoadout,  -- 1..5, or a preset id
    Skins = { owned ids, equipped per gun }, Crates = { id = count },
    Challenges = {}, Stats = { Kills, Deaths, ... },
    Settings = { volumes, keybinds, accessibility },
    Purchases = { receiptIds processed },
  }
  ```
- [ ] **DataStore safety** (see `roblox-datastores` practice): session locking so two servers can't load the same profile (ProfileStore-style), `UpdateAsync` not `SetAsync`, retries with backoff in `pcall`, autosave every ~60–120 s, save on leave and in `game:BindToClose`, schema `Version` with migrations, never save mid-transaction.
- [ ] **XP and cash only from server events:** the damage system (server-side) records who damaged whom; on death the server awards kill/assist XP. Match-end XP/cash computed by the server's match manager. **No remote ever carries an XP or cash amount.**
- [ ] **Remotes the client may call** (all validated, rate-limited):
  | Remote | Carries | Server checks |
  |---|---|---|
  | `SetLoadout` | loadout index + Primary/Secondary/Tertiary/throwable/item/skill ids | index unlocked, ids exist, unlocked & owned, Primary is two-handed and Secondary/Tertiary one-handed (`LoadoutRules`), weight within allowance (applies on next spawn) |
  | `SelectLoadout` | index 1–5 or preset id | valid and unlocked |
  | `BuyItem` | item id | unlocked at this level, not owned, enough Cash; deduct and grant in one profile update |
  | `BuySkill` | skill id | Lv 1 unlock level reached, not owned, enough Cash; deduct and grant in one profile update |
  | `BuySkin` | skin id | for sale now, enough Cash, not owned |
  | `OpenCrate` | crate id | owns one (or enough Cash), policy allows; **roll on the server** |
  | `EquipSkin` | gun id + skin id | owns skin, skin fits gun |
  | `SetTitle` | title id | unlocked |
  | `SaveSettings` | settings table | types and ranges checked, size limit |
- [ ] **Robux purchases:** `MarketplaceService.ProcessReceipt` on the server only; idempotent (store `PurchaseId`, return `PurchaseGranted` only after the profile saved). Never grant from a client message.
- [ ] **Anti-farm:** cap XP per minute; no XP for killing the same player more than N times in a short window when they don't fight back (AFK farming); reduced or no XP in private servers with fewer than N players; no XP from team kills or from your own Trust Issues friendly fire.
- [ ] **Sanity and logging:** log big jumps (cash > X per match, level jumps) to an analytics/log store for review; `AnalyticsService` economy events for every Cash source and sink.
- [ ] **Leaderboards:** `OrderedDataStore` written by the server (level, kills, season XP).
- [ ] **Testing:** a cheat remote that only exists in Studio (`RunService:IsStudio()`) to set level/cash for testing, added to `Tools/TestHarness.luau`. Never shipped.
- [ ] The `roblox-dev:roblox-reviewer` check over all economy code before publishing.

---

## 10. Shop (skins and crates), Roblox compliant
### Layout (from the mockup)
- [ ] Title SHOP, and under it the note: **"Skins are cosmetic only. They give no advantage in combat."**
- [ ] Panel: Cash balance top left (`$12,450`, Oswald Bold), two wide **skin cards** stacked on the left, one tall **featured skin** in the middle, **three crates** in a column on the right. Live match in the background.
- [ ] Skin card: Blender render of the skinned gun, name, line (Gunsmith, Street…), rarity, price, BUY / OWNED / EQUIP. Click → full preview (rotating `ViewportFrame` of the gun with the real `SurfaceAppearance`).
- [ ] Crate card: crate render, name, price, **a "View Odds" / "Details" button with words** (see rules), OPEN.
- [ ] Rotating stock: featured and daily skins change on a timer the server controls (UTC); the client only shows what the server sends.
- [ ] Skin lines and the four layers (Finish, Pattern, Signature, Mastery) are already planned in [[Gun Skin Ideas]]. Mastery skins are never sold or in crates.

### Roblox's paid random items rules (read 2026-11-10) ✅
A crate is a **paid random item** if it can be bought with **Robux, or with any currency that can be bought with Robux** (even indirectly, e.g. keys bought with Robux). Then:
- [ ] Show **every possible outcome and its numerical odds before purchase.**
- [ ] Odds as **percentages that add up to exactly 100%**. Long decimals may be rounded (to at least four decimal places below the first non-zero digit) with a note: "Probabilities are rounded; the total shown may not equal 100%."
- [ ] If the list is too long for the screen, a pop-up opened by a button **with a word on it** ("Odds", "Details"). An ⓘ icon alone is not enough.
- [ ] Items with the same odds may be listed under one line: "Odds for each item below: X%".
- [ ] **No-duplicate crates:** if a player can only get each outcome once, the odds shown must update to that player's remaining outcomes.
- [ ] **Luck boosts / pity:** anything that changes odds must explain the change in numbers before purchase, and the odds shown must update while it's active.
- [ ] **`PolicyService:GetPolicyInfoForPlayerAsync`** per player (server-side):
  - `ArePaidRandomItemsRestricted = true` → that player can't open paid crates. Give them one of: a free earnable path, a fixed disclosed order, **direct purchase of each skin priced from its expected value** (e.g. a 5% skin from a 100-Cash crate → 2,000 Cash), hiding the crates, or a clear "unavailable in your region" message. **Proposed: hide paid crates and show every skin for direct purchase.**
  - `IsPaidItemTradingAllowed = false` → no trading of anything bought (only matters if trading is ever added).
- [ ] Random rewards for actions that cost nothing (e.g. a free crate for reaching a level) don't need odds shown, **but show them anyway** for trust and consistency.

### How we comply (plan)
- [ ] **Launch: crates cost earned Cash only, and Cash can't be bought with Robux.** Then crates aren't paid random items. Still show odds on every crate.
- [ ] **If Robux comes later:** sell skins directly for Robux (Developer Products), not Cash. If Cash or crate keys are ever sold for Robux, every rule above applies at once.
- [ ] **One config, two readers:** `ShopConfig` (ReplicatedStorage) holds each crate's items and weights; the server rolls from it and the odds screen reads from it, so the shown odds can never differ from the real ones. Odds computed as `weight / total weight`, shown to 2+ decimals.
- [ ] **Roll on the server** with `Random.new()` seeded on the server; log every roll (player, crate, result) for support.
- [ ] Example crate (placeholder):
  | Rarity | Chance | Items |
  |---|---|---|
  | Common | 70.00% | 7 skins, 10.00% each |
  | Uncommon | 20.00% | 5 skins, 4.00% each |
  | Rare | 7.50% | 3 skins, 2.50% each |
  | Very Rare | 2.20% | 2 skins, 1.10% each |
  | Exceptional | 0.30% | 1 skin, 0.30% |
  | **Total** | **100.00%** | |
- [ ] **Duplicates:** either convert to Cash (say so and how much before purchase) or make crates no-duplicate with live odds. Proposed: duplicates → Cash refund of 25% of the crate price, shown in the Details pop-up.
- [ ] **Opening animation:** Blender-rendered crate opening, reveal with rarity colour, skip button, under 3 s. No fake "near miss" spins that suggest a better result was close.
- [ ] **Content maturity:** blood-themed skins (e.g. "Bloodwork" in [[Gun Skin Ideas]]) and realistic gore can raise the experience's maturity label. Fill in the Roblox maturity questionnaire honestly and keep skins within the label we choose.
- [ ] Shop purchases go through the server remotes in section 9.

---

## 11. Settings and accessibility
Saved in the server profile (`Settings`), applied on the client. Defaults chosen so a new player never has to open Settings.

### Audio
- [ ] Sliders 0–100: **Master, Music, Sound effects, Weapons, Voice/narration, Menu sounds.** Each maps to a `SoundGroup` (every sound in the game must be in one).
- [ ] Mute when the window loses focus (toggle).
- [ ] Hit marker sound on/off; low-health heartbeat on/off.

### Controls and keybinds
- [ ] **Rebind every action** listed in the `Keybinds` module (fire, aim, reload, slots 1–4, dual wield, drop, pick up, cover, crouch, sprint, dive, painkiller, skill, scoreboard, swap shoulder…), for keyboard/mouse **and** gamepad separately.
- [ ] Rebinding UI: click an action, press a key, **conflict warning** if the key is used ("Already used by RELOAD – swap?"), **Reset to default** per action and for all.
- [ ] `ContextActionService` bindings read from the player's saved map; the HUD keybind list ([[HUD Layout]]) already reads `Keybinds`, so it updates by itself.
- [ ] Server validates the saved map (known actions, allowed `KeyCode`s, size limit) — it's harmless data, but keep it tidy.
- [ ] Mouse sensitivity: general, aiming, scoped (three sliders). Invert Y. Gamepad sensitivity and dead zone.
- [ ] **Hold or toggle** for aim, crouch, sprint.
- [ ] Gamepad aim assist strength (later, if gamepad play needs it).

### Display and camera
- [ ] Field of view slider (e.g. 70–100).
- [ ] Camera shake / recoil camera kick intensity.
- [ ] Bullet time and Last Stand **desaturation/blur strength**.
- [ ] Film grain and menu effects on/off.
- [ ] Brightness / gamma (`ColorCorrectionEffect`).
- [ ] UI scale (the HUD already scales 0.75–1.25 with screen height; add a manual multiplier).
- [ ] Reticle: style, colour, size; dynamic spread ring on/off.

### Accessibility
- [ ] **Colourblind modes** (protanopia, deuteranopia, tritanopia): swap HUD red (limbs, enemy reticle, status text) and team colours for safe pairs; also a pattern/icon cue besides colour (e.g. limb damage shows hatching).
- [ ] **Subtitles** for narration and skill lines; text size; background box.
- [ ] **Reduce flashing:** flashbangs dim to grey instead of full white; no rapid flicker in glitch transitions.
- [ ] **Reduce motion:** turns off glitch transitions, menu camera drift, screen shake.
- [ ] **Text size** for menus.
- [ ] **High-contrast HUD** option (solid backgrounds behind HUD text).
- [ ] Show/hide the keybind list on the HUD.
- [ ] Hide other players' titles (some players want a cleaner screen); streamer mode (hide names).

### Other
- [ ] Gameplay: auto-reload on empty on/off (currently always on), auto-pick up on/off.
- [ ] Settings screen follows section 2's look: categories down the left (AUDIO, CONTROLS, DISPLAY, ACCESSIBILITY), options on the right, context line explains the highlighted setting.

---

## 12. Notes for later
- **Touch/mobile:** the HUD has no touch controls yet ([[HUD Layout]]). Every menu should still be built tap-friendly (big targets, no hover-only info), so phones work once touch controls exist.
- **Order of systems this plan depends on:** minimap, looting bodies, grenades/throwables, stamina and health regen, melee, scoreboard, respawn timer, objective modes, vendettas/bounties. Several items and skills wait on them; build the ones that don't first.
- **Vendettas and feuds** (Max Payne 3): a player who kills you a lot becomes your vendetta target; killing them pays extra XP. Good for XP variety; needs the scoreboard and minimap.
- **Narration:** Max Payne 3 narrates bursts and match events. We could have an original noir narrator (on-screen text first, voice later). Subtitled.
- **Localization:** keep every menu string in a table, not in the UI objects, so it can be translated later.
- **Analytics:** track menu funnel (join → Play), most used loadouts/skills/items, crate opens and Cash flow, to balance.
- **Seasons:** later, a season track (free + premium) that gives Cash, crates, titles; same server rules.
- **Avatars/factions:** Max Payne 3's characters and factions were cosmetic too; a character skin layer could join the shop later.
- **Performance:** menu images are cheap; limit live `ViewportFrame`s to one or two at a time. Disconnect menu loops when the menu closes.
- **Accessibility first:** every menu reachable by keyboard and gamepad from day one; retrofitting is harder.

---

## Suggested build order
1. [ ] Decisions in section 0.
2. [ ] Server profile + DataStore safety (section 9). Nothing else should save data on its own.
3. [ ] Menu shell with live match camera and the section 2 look (main menu only, Play works).
4. [ ] Blender UI pipeline and first assets (logo, overlays, weapon icons) (section 3).
5. [ ] Settings: audio sliders + keybind rebinding + the accessibility toggles that need no new systems.
6. [ ] Loadout screen with the existing guns, three loadouts, weight classes (needs stamina/regen rules).
7. [ ] XP, levels, titles, cash multiplier, name tags and scoreboard (section 8).
8. [ ] Adrenaline as three segments; skills framework; first-wave skills.
9. [ ] Items: first wave.
10. [ ] Shop: direct-purchase skins, then crates with odds and `PolicyService` checks.
11. [ ] Challenges; prestige; the items and skills that need minimap/looting/grenades.

---

## Appendix: Max Payne 3 multiplayer data from the wiki (compiled 2026-11-10)
Exact data read from the three wiki pages and the 16 burst pages, for reference while building. 📰 Community wiki, not official. **Design reference only: names, titles and text here are Max Payne 3's and don't go into our game** (our versions are in the sections above). The full item tables are in [[#Items (3 slots: Head, Chest, Gear)]] and the full burst table in [[#Every Burst, level by level 📰]]; they aren't repeated here.

### Loadouts
- Up to **5 custom loadouts**, each a set of weapons, one burst and items. Weapons, bursts and items together change speed, stamina and health regeneration.
- At most **3 items** (one head, one chest, one gear).
- **4 presets** (3 from the start, 1 at level 3):
  | Preset | Items | One-handed | Two-handed | Throwable | Burst |
  |---|---|---|---|---|---|
  | Soldier | Light Body Armor | PT92, .38 Revolver | AK-47 | Grenade | Trigger Happy |
  | Snitch | Sneakers | M10 | — | Flash Grenade | Intuition |
  | Dealer | Ammunition Pouch | PT92 | M500 | Grenade | Big Dog |
  | Lookout (level 3) | Sutures | .38 Revolver | Mini-30 | Flash Grenade | Trigger Happy |

### Weapons (full list)
| Class | Weapons |
|---|---|
| Melee | Night Stick, Cattle Prod, Pepper Spray, Stun Gun |
| Handguns (all dual-wieldable) | PT92, 608 Bull, Auto 9mm, M1911, .38 Revolver, DE .50 |
| SMGs | M10, M972, Micro 9mm (all three dual-wieldable); MPK, SAF .40 |
| Shotguns | Sawed-Off (dual-wieldable), Hammerhead auto shotgun (DLC), M4 Super 90, M500, Super Sport, SPAS-15 |
| Assault rifles / MGs | AK-47, FAL, MD-97L, G6 Commando, LMG .30, RPD; DLC: M4 Carbine, UAR-21, IMG 5.56, Imbel IA2 |
| Rifles / snipers | Mini-30, FMP G3S, M82A1; DLC: M24 |
| Explosive | RPG, Rotary Grenade Launcher; DLC: G9 Grenade Launcher, LAW |
| Throwables | Tin Can, Flash Grenade, Smoke Grenade, Tear Gas, Grenade; DLC: Molotov Cocktail |

### Adrenaline and bursts
- The adrenaline meter sits bottom right with the HUD, in **3 segments**, filled by **kills and looting bodies**.
- Each full segment raises the burst a level (max 3). Using it **consumes all full segments**: timed bursts drain over their duration (Bullet Time), instant ones empty at once (Trigger Happy).
- **Full segments are kept on death; part-filled ones are lost.**
- Burst themes: deceit, betrayal, paranoia, plus Bullet Time and "Hong Kong-style" action.
- Burst grinds (XP for bronze / silver / gold / platinum):
  | Grind | Condition | Needed | XP |
  |---|---|---|---|
  | Adrenaline Junkie | Adrenaline earned | 500 / 1,000 / 10,000 / 25,000 | 50 / 100 / 500 / 1,000 |
  | Small Beginnings | Level 1 bursts triggered | 5 / 25 / 75 / 150 | 25 / 100 / 250 / 500 |
  | Building It Up | Level 2 bursts triggered | 5 / 25 / 75 / 150 | 25 / 100 / 250 / 500 |
  | As Good As It Gets | Level 3 bursts triggered | 5 / 25 / 75 / 150 | 25 / 100 / 250 / 500 |
  | (each burst) "Times used" | Uses of that burst | 5 / 25 / 75 / 150 | 25 / 100 / 250 / 500 |
  | (some bursts) "Kills in …" | Kills while it's active | 10 / 25 / 100 / 250 | 50 / 100 / 500 / 1,000 |
  | Explosives grinds | Trap, HE-ammo and grenade kills | 10 / 25 / 100 / 250 | 250 / 500 / 1,000 / 2,000 |
  | Big Dog "Pound of Flesh" | Health added | 1,000 / 2,000 / 5,000 / 10,000 | 50 / 100 / 500 / 1,000 |
- In Payne Killer mode, everyone except the two hunted players has Intuition, whatever their loadout says.
- Each burst plays one of four narrator lines when used (Hangover and Unstoppable have none).

### Ranks, titles and Legend
- XP from killing, assisting, grinds, winning feuds and settling vendettas. **50 ranks**; ranking up gives more cash and unlocks avatar items, titles, weapons and loadout items. All weapons are unlocked by **level 40**, all bursts by **48**, all avatar items by **50**.
- **Rank titles:** Soldado 1 · Cabo 4 · 3 Sargento 7 · 2 Sargento 10 · 1 Sargento 13 · Sub-Tenente 16 · Cadete 19 · Aspirante 22 · 3 Tenente 26 · 2 Tenente 30 · 1 Tenente 35 · Capitao 40 · Major 45 · Coronel 50. (Gaps of 3 early, then 4–5.)
- **Achievement titles:** Gun Collector (all weapons), Playboy (all avatar items), Master of Arms (all weapons max rank), Dedicated (all achievements), The Steamroller (all bursts), Quartermaster (all items); more from "Payne Thresholds".
- **Legend:** at rank 50, choose "Legend" from the multiplayer menu to go back to rank 1. Up to **10 times** (500 ranks in all). Each Legend **removes all weapons, items, upgrades, cash and earned loadout weight**, and gives a patch, a title, a unique avatar, and a bigger cash multiplier on the Badge of Honor gear (unlocked at Legend 1):
  | Legend | Title | Cash multiplier |
  |---|---|---|
  | 1 | Respected | 120% |
  | 2 | Trustworthy | 140% |
  | 3 | Warlord | 160% |
  | 4 | Living Legend | 180% |
  | 5 | Renowned | 200% |
  | 6 | Marked | 220% |
  | 7 | Chief | 240% |
  | 8 | Golden | 260% |
  | 9 | Unrivaled | 280% |
  | 10 | Peerless | 300% |
  (Originally 5 Legend levels; 6–10 added later. Each also has a unique avatar outfit.)

### Other
- **Crews:** clans with a leader and emblem; players can join up to 5; crews earn XP faster.
- **Game modes:** Rookie TDM, Deathmatch, Team Deathmatch, Payne Killer, Gang Wars, Large DM/TDM, Hardcore DM/TDM/Gang Wars (details in [[Max Payne 3 Game Modes - Roblox Engagement]]).
- **Maps:** 8 base maps plus DLC packs. Not relevant to menus except that each map needs its own menu camera points (section 1).
- **Items unlock** through levelling, DLC or pre-order bonuses (full table in section 5).

---

## Sources
- 📰 [Max Payne Wiki — Multiplayer Items](https://maxpayne.fandom.com/wiki/Multiplayer_Items) (read 2026-11-10)
- 📰 [Max Payne Wiki — Burst](https://maxpayne.fandom.com/wiki/Burst), and each burst's own page (Trigger Happy, Intuition, Big Dog, Bullet Time (burst), Paranoia, Sneaky, Grounded, Fresh Blood, Weapon Dealer, Burst Bubble, Weapon Double-Dealer, Unstoppable, Hangover, Deadly Force, Explosives, Slippery Character) for the level 1/2/3 effects, costs and counters (read 2026-11-10)
- 📰 [Max Payne Wiki — Max Payne 3 Multiplayer](https://maxpayne.fandom.com/wiki/Max_Payne_3_Multiplayer#Bursts): preset loadouts, weapon list, titles, ranks, Legend and cash multipliers (read 2026-11-10)
- ✅ [Roblox — Paid random items policy](https://create.roblox.com/docs/production/monetization/paid-random-items) (read 2026-11-10)
- Screenshots: our mockups in `Attachments/Menus/`; Max Payne 3 menu, story menu, loadout and bursts screenshots in `Attachments/Menus/Max Payne 3/` (committed for collaborators).
