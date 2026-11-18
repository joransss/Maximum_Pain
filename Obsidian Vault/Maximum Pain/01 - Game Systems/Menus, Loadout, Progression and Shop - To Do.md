# Menus, Loadout, Progression and Shop: To Do

Plan and work queue for everything outside the fight: the main menu, the Max Payne 3-style menu look, loadouts and items, skills (Max Payne 3's "Bursts", renamed), levels, titles and cash, the skin shop and crates, and settings. Written 2026-11-10, decisions updated 2026-11-14. **Built so far: Phase A of the [[#Suggested build order]] (2026-11-14): the slot rename, the server profile and the match manager; Phase B (2026-11-18): the main menu, the menu kit and the first UI art ([[Changelog]]). Phase C's code (steps 7 and 8) is in the place too, but these notes don't describe it yet (found 2026-11-18). Everything else here is still a plan.**
Related: [[Loadout and Dual Wielding]] · [[Last Stand and Bullet Time]] · [[Limb Health]] · [[HUD Layout]] · [[Architecture]] · [[Gun Skin Ideas]] · [[Max Payne 3 Game Modes - Roblox Engagement]] · [[Max Payne 3 HUD and Combat UI Reference]] · [[Blender and Asset Pipeline]] · [[Multiplayer Networking Research]] · [[Networking and Security]]

> [!important] Ground rules for everything in this note
> - **Original content only.** Max Payne 3 is the reference for *how it feels*, not for names, art, fonts or text. Every Burst, item and title below gets our own name (proposals are in each table). Real gun names (M9, AK-47) are fine, as now.
> - **The server owns levels, XP, cash, unlocks, crates and purchases.** The client only *asks* ("equip loadout 2", "buy skin X", "open crate Y"); the server checks and decides. See [[#9. Server-side economy and anti-exploit]].
> - **UI art is made in Blender** (backgrounds, panels, icons, crates, logo, badges), rendered to images and imported into Roblox. See [[#3. Blender for the UI]].
> - **Every piece of UI follows the UI style** in [[#2. Making the UI feel like Max Payne 3]] (Oswald, white/black/grey, hard edges, white selection bar, film look). This applies to every UI item in this note, including the ones added later (player card, prestige icons, server-switch prompt, stats panel); items below marked 🎨 are reminders of it.
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

![[Mockup - Player Card.png]]
**Player card** (added 2026-11-14). A square on the left holding **the player's avatar**; to its right, stacked: **Title**, **Name**, then **Level:** with the **money ($) shown alongside the level**. Shown in the main menu (see [[#Player card and stats (main menu)]]). The mockup is a layout sketch only: the finished card is drawn in the UI style of section 2. 🎨

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
- [x] **5 saved loadouts** (decided 2026-11-14), plus the 4 read-only presets. **Slots 1–3 are free from level 1; slot 4 unlocks at level 10 and slot 5 at level 25.** Slots 4 and 5 **lock again on prestige** (their contents are kept for when they're re-earned).
- [x] **Level cap: 50** (decided 2026-11-14). At 50 the player may **prestige**, which resets their level to 1.
- [x] **Prestige** (decided 2026-11-14): **max prestige 5 (V)**. On prestige the player **keeps everything cosmetic** (skins, titles, accessories) and **loses guns, skills and cash** (cash resets to $0). They gain a **prestige icon next to their title** (Roman numerals **I–V**) and a **+20% cash multiplier per prestige**, stacking (I = +20% … V = +100%). Details in [[#8. Levels, titles and cash multipliers]].
- [x] **Crates are bought with $ (Cash)** (decided 2026-11-14), earned from match performance: **$10 per kill, $1,000 for a win**; XP uses the same values (10 XP per kill, 1,000 XP for a win). Cash can't be bought with Robux, so crates aren't paid random items (see [[#10. Shop (skins and crates), Roblox compliant]]).
- [x] **Skill and title names:** placeholders set (section 6 and section 8). Final names later; ids in config stay the same when names change.
- [x] **Join flow, server choice** (decided 2026-11-14): on join the game checks for **higher-population servers** and offers the player a switch (**ask first**, never forced). **Roblox private servers are exempt.** Plan in [[#Join flow: send players to fuller servers (plan for later)]].
- [x] **Join flow, menu** (decided 2026-11-14): a new player **lands on the main menu over the live match** and presses PLAY to spawn.
- [x] **Main menu key: M** (decided 2026-11-14). It shows the player card (title, name, level, money, avatar) and stats, and loadouts can be switched there at any time; **a new loadout is only received on death** (next spawn). Built 2026-11-18. The gamepad's button is an open question (below).

**Questions added 2026-11-14 (all settled the same day):**
- [x] **Loadout slots: 3 free, 2 by level.** Slot 4 at level 10, slot 5 at level 25; both lock again on prestige and are re-earned.
- [x] **Level cash multipliers stay alongside prestige** (decided 2026-11-14). The milestone table's ×1.05 every 5 levels (up to ×1.50 at 50) and the prestige +20% add together: highest possible is prestige V at level 50 = 1.50 + 1.00 = ×2.50. The level part drops back to ×1.00 on each prestige; the prestige part is permanent.
- [x] **Other rewards:** assists, bonus kills (headshot, shoot-dodge / bullet time, Last Stand, revenge), **losing a match ($250 / 250 XP)** and challenges all pay. Full table in section 8.
- [x] **Gameplay items reset on prestige** (Riot Helmet, vests, gear), with guns and skills. Only cosmetics are kept.
- [x] **XP curve: level 1 → 50 in about 20 hours** (about 100 hours for all five prestiges). Curve `300 + 50 × (L − 1)`, 73,500 XP in total; working in section 8.
- [x] **M during a fight: the character stays in the match and can be shot.** No pause, no protection, no combat lock on the menu.

**Open question added 2026-11-18:**
- [ ] **Which gamepad button opens the main menu?** Start was the plan (2026-11-14), but Start opens Roblox's own menu whatever a game binds to it (tested 2026-11-18), and Select, the plan's fallback, is bullet time. Options: (a) Select opens the menu and bullet time moves to another button, e.g. R3, the right-stick click (swap shoulder now), which then moves too; (b) holding Select for half a second opens the menu and a tap is still bullet time (it would then fire as the button is let go, a fraction later than now). Until it's decided, a gamepad player gets the menu on joining and B closes it, but can't open it mid-match.

**Open questions added 2026-11-10 (loadout weight, skills, titles):**
- [x] **Two-handed size bonus: yes.** Two-handed guns get +2 weight on top of the stat score (decided 2026-11-10).
- [x] **Same gun twice: yes.** Secondary and Tertiary may hold the same gun (e.g. two Desert Eagles for dual wielding). Assumed: owning the gun once covers both slots.
- [x] **Weight classes change: health regen, stamina and aiming speed.** Walk speed and dive distance stay the same for every class.
- [x] **Weight allowance does not increase with level** (decided 2026-11-14). Every player has the same limits from level 1; the Light / Medium / Heavy penalties are what limit a heavy loadout.
- [x] **Skill prices: Cash to unlock once the required level is reached** (Max Payne 3's way). Starter skills at level 1 stay free, since new players have no Cash.
- [x] **Bullet Time free from level 1: yes.**
- [x] **Gun stats display: bars plus numbers** (decided 2026-11-14).
- [x] **Titles: players pick any unlocked title** (decided 2026-11-14).
- [x] **Slot keys stay as they are** (decided 2026-11-14): 1 and 2 = the one-handed guns, 3 = the two-handed gun, 4 = dual wield.
- [x] **Slot names renamed in code too, for continuity** (decided 2026-11-14): `Two` → `Primary`, `OneA` → `Secondary`, `OneB` → `Tertiary`, everywhere at once.
- [x] **Last Stand always takes all adrenaline** (decided 2026-11-14), however many segments are full.
- [x] **Loadout names are editable** (decided 2026-11-14), filtered on the server.
- [x] **Level and title on enemies' name tags: only at close distance** (placeholder ~60 studs, and only in line of sight). Teammates always see them.

---

## 1. Main menu shell (live match behind every menu)
**Built 2026-11-18** (Phase B, [[Changelog]]): `MenuController`, `MenuCamera` and `MenuKit` on the client, `SpawnService` on the server, `MenuRules` shared.
- [x] **Menu state on join** (decided 2026-11-14: main menu first): the player joins, their character is *not* spawned (`Players.CharacterAutoLoads = false`, spawn on Play via the server), and the menu opens over the live match.
- [x] **Live match camera ("viewpoint of the current map being played"):**
  - [x] Options, in order of effort: (a) slow cinematic dolly between a set of `MenuCam` parts placed per map; (b) spectate a random living player from a chase camera, switching every ~8 s or on their death; (c) mix: dolly, cut to a player when a kill happens nearby.
  - [x] Start with (a), it never shows anything broken; add (b) later. **Built:** four shots of the Test Arena in `Workspace.MenuCams.TestArena` (Models Shot1–4, each a From and a To part and an optional `Fov`), 12 s each, dipping to black at the cuts, the shot on screen taken from the server's clock. (b) is still to do.
  - [x] **StreamingEnabled:** the menu camera may be far from where the (unspawned) player is, so the map there might not be streamed in. Use `Player:RequestStreamAroundAsync(position)` on the server for each camera point, or set `Player.ReplicationFocus` to a part at the camera. Test with streaming on. **Built:** `ReplicationFocus` on the shot's From part (2 s ahead of each cut); `MenuCams` is a Persistent model. Tested with streaming on.
  - [x] The menu camera is client-only (`Camera.CameraType = Scriptable`), so it can't leak or change anything.
- [x] **Left panel (mockup):** game title, then Play, Shop, Settings, Loadout. Proposed order: **PLAY, LOADOUT, SHOP, SETTINGS** (most-used first), plus the **player card** and stats (below). Built in that order; the card bottom left.
- [x] **M opens and closes the main menu** at any time, including mid-match (decided 2026-11-14). Add `Menu = Enum.KeyCode.M` to the `Keybinds` module (M is unused today) so it's rebindable and shows in the HUD keybind list.
- [x] **Gamepad: Start opens the menu** (decided 2026-11-14), `Enum.KeyCode.ButtonStart`. **Test this first:** Roblox's own in-game menu also uses Start on gamepad (as it uses Esc on keyboard), and games can't reliably take that button over. If both menus open, or ours never gets the press, fall back to **Select/View** (`Enum.KeyCode.ButtonSelect`) and keep Start for Roblox's menu. **Tested 2026-11-18: Start opens Roblox's menu and ours never gets it.** The fallback, Select, is bullet time, so this is an open question in [[#0. Decisions to make first]]; `Keybinds.Menu` is M alone until then.
- [x] Each button opens its screen *over the same live background*; BACK (Esc / B) returns. One `MenuController` on the client owns the stack of screens (open, back, close-to-play). **BACK is Backspace (B on a gamepad):** Esc is Roblox's own menu and a game can't take it.
- [x] Pressing Play: the client asks; the server checks the chosen loadout and spawns the character with it; the menu fades out. Built without the loadout check, which comes with the loadout screen (step 10).
- [x] **In-match menu:** **M** during a match opens the same main menu (PLAY reads RESUME; add LEAVE). Esc stays Roblox's own menu; check `GuiService.MenuIsOpen` so the two never overlap. **The match does not pause and the character stays vulnerable** (decided 2026-11-14): it stands where it was and can be shot, so the menu can't be used as cover. Keep a small damage indicator visible over the menu so the player knows to close it. **Built:** UNDER FIRE and a red flash on each hit; dying closes the menu. LEAVE MATCH asks to confirm and is refused within 5 s of being hurt or in a Last Stand; after leaving, PLAY waits 10 s (both in `MenuRules`, my numbers, 2026-11-18), so leaving can't be used to heal, refill or get back to a spawn quicker than fighting on.
- [ ] **Loadouts can be switched freely in the menu, but the new loadout is only received on death** (decided 2026-11-14): the server stores the selection at once and uses it at the next spawn. The menu shows "APPLIES ON NEXT SPAWN" while the equipped and selected loadouts differ. 🎨
- [ ] Death screen → after the kill cam ([[Max Payne 3 Kill Cam]]) offer **Change Loadout** before respawn, as Max Payne 3 does.

### Player card and stats (main menu)
Decided 2026-11-14. Layout from the player card mockup (see [[#Our mockups (the plan to follow)]]). **Built:** `PlayerCard`, a component that was already in the place on 2026-11-18 (with Phase C's code; the scoreboard shows it too). The main menu shows it bottom left, refreshed as the profile's attributes change; checked on screen 2026-11-18 (avatar, NOBODY, the name, LEVEL: 1, $0, the XP bar, the stats).
- [x] **Layout:** a square with **the player's avatar** on the left; to its right, three stacked lines:
  ```
  ┌────────┐  [prestige icon] TITLE
  │ avatar │  PlayerName
  │        │  LEVEL: 27        $12,450
  └────────┘
  ```
- [x] **Avatar:** `Players:GetUserThumbnailAsync(userId, Enum.ThumbnailType.HeadShot, Enum.ThumbnailSize.Size150x150)` in an `ImageLabel` (in `pcall`, with a grey silhouette until it loads). Square frame with a hard white border, as in the mockup.
- [x] **Title line:** the selected title, with the **prestige icon (I–V) directly before it** once the player has prestiged (section 8). The icon is a text plate until the Blender badges exist.
- [x] **Level line:** `LEVEL: 27` with the **money shown alongside it** on the same line (`$12,450`). Under it, a thin **XP bar** with `XP earned / XP needed` for the next level.
- [x] **Stats block** under the card (numbers only, two columns):
  | Stat | Source (server profile `Stats`) |
  |---|---|
  | Kills, Deaths, K/D | `Kills`, `Deaths`, `Kills ÷ max(1, Deaths)` to 2 decimals |
  | Matches, Wins, Win rate | `Matches`, `Wins`, `Wins ÷ Matches` as % |
  | Headshot kills | `HeadshotKills` (and % of kills) |
  | Time played | `PlaySeconds`, shown as hours and minutes |
- [x] All values come from the server profile (replicated read-only, e.g. attributes on the player or one `ProfileChanged` remote); the client never computes or sends them. Attributes on the Player (`Level`, `XP`, `Cash`, `Prestige`, `Title`, `Stat<name>`).
- [x] 🎨 **Drawn in the UI style of section 2:** Oswald Bold for name and level, Oswald Regular for stat labels, white on the dark gradient panel, mid grey labels, no rounded corners. The mockup's boxes are placement only.

### Join flow: send players to fuller servers (plan for later)
Decided 2026-11-14: when a player joins, the game checks whether a **higher-population server** exists and offers to switch them to it. **Roblox private servers are exempt.** Basic plan only; build after the menu shell.
- [ ] **Skip the check when:**
  - the server is private: `game.PrivateServerId ~= ""` (covers paid/VIP private servers and reserved servers; `game.PrivateServerOwnerId ~= 0` means a player-owned private server);
  - the player followed a friend in (`Player.FollowUserId ~= 0`) or arrived by our own switch (flag in `TeleportData` / `Player:GetJoinData()`), so nobody gets bounced twice or pulled away from a friend;
  - in Studio (`RunService:IsStudio()`).
- [ ] **Server list:** every public server writes `{ jobId, playerCount, maxPlayers, mode, map }` to a `MemoryStoreService` sorted map every ~30 s with a ~90 s expiry (dead servers drop out by themselves), and removes its entry in `BindToClose`. Sort key = player count.
- [ ] **On join (server-side):** read the top entries; pick the fullest server that still has room (leave 1–2 slots spare for the race between check and arrival). Offer a switch only if it's clearly better: e.g. this server has fewer than `MIN_POPULATION` players (placeholder 4) **and** the other has at least `MIN_GAIN` more (placeholder 3).
- [ ] **Ask first** (decided): the menu shows a prompt, "A FULLER MATCH IS AVAILABLE (9/12 PLAYERS) – SWITCH / STAY". 🎨 Drawn in the UI style of section 2 (white selection bar, context line, prompts bottom right). STAY is remembered for the session.
- [ ] **Switch:** the client only answers yes/no; the server calls `TeleportService:TeleportAsync(game.PlaceId, { player }, options)` with `TeleportOptions.ServerInstanceId = jobId`, inside `pcall` with one retry. On failure (server filled or closed) the player simply stays, with a short message.
- [ ] **Save first:** release the profile's session lock before teleporting (section 9), so the new server can load it.
- [ ] **Limits to remember:** MemoryStore and teleport calls are rate-limited; check once on join, not on a loop. Parties: if several friends join together, offer the switch only when the target has room for all of them (later).
- [ ] All thresholds in one `MatchmakingConfig` module.

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
**Built 2026-11-18** as `MenuKit` (client): every menu screen is put together from it (the canvas, the shade, the page with its heading, context line, list and notice, the prompts, the film, the grade, the glitch). Ticked below where built; the rarity colours wait for the shop.
- [x] **Font:** keep **Oswald** (already the HUD font, [[HUD Layout]]): Bold for headings, list items and prompts; Regular for the context line and descriptions. One family across HUD and menus.
- [ ] **Colours:** reuse the HUD palette (done: white, black, grey, red only for UNDER FIRE and refusals): white, black, mid grey `#A5A5A5`, red for danger/locked only. **Rarity colours (decided 2026-11-14): each rarity gets its own colour**, used only in the shop, crate reveals and skin lists; the rest of the UI stays white/black/grey. All muted so they sit in the film look, none of them red (red stays danger/locked). Placeholder values, to tune on screen:
  | Rarity | Colour (placeholder) | Pips |
  |---|---|---|
  | Common | Grey `#A5A5A5` (the HUD grey) | 1 |
  | Uncommon | Dull teal `#5FA39A` | 2 |
  | Rare | Steel blue `#6F8FA8` | 3 |
  | Very Rare | Muted violet `#8B78A8` | 4 |
  | Exceptional | Worn amber `#C9973F` | 5 |
  - [ ] Colour is never the only cue: every rarity also shows its **name and 1–5 pips**, so it reads in the colourblind modes (section 11). Check the five colours in each mode and against the teal-tinted background.
  - [ ] Stored once in `ShopConfig` (or a `UiTheme` module), so the shop, the odds pop-up and the crate reveal all read the same values. Prices and the Cash balance stay white.
- [x] **Left panel:** in the main menu mockup it's a boxed white panel. To feel like Max Payne 3, make it **a dark, see-through gradient** (black 70% → 0% to the right) instead of a white box, with the list on it. Keep the mockup's position and proportions (left ~40%). Built: 70% black at the edge, half that at about a third of the screen, clear by 62%.
- [x] **Colour grade on the live view while a menu is open:** client-side `ColorCorrectionEffect` (saturation −0.5, contrast +0.1, tint toward teal), `BlurEffect` size ~6 only behind the left panel area (or on the whole view, lighter), `DepthOfFieldEffect` for the bokeh feel. Remove them all when the match starts. Built with the whole view at blur 4; eased on and off in 0.25 s.
- [x] **Overlays (made in Blender, see section 3):** a tiling grain texture animated by offsetting it every frame, a vignette image, a few bokeh/light-leak images that drift slowly. Built: the grain jumps 18 times a second, three bokeh drift, the light leak swells and fades in the top right corner.
- [x] **Animation:** `TweenService` for the selection bar (Quad Out, 0.08 s), screen fade (0.2 s), glitch transition made from 3–4 offset copies of the frame with red/cyan tint for ~0.15 s. Built: the glitch splits each new screen's heading (two copies).
- [x] **Navigation:** fully playable with mouse, keyboard (arrows / W S, Enter, Esc) and gamepad (`GuiService.SelectedObject`, `NextSelectionUp/Down`). Touch later. Built with the menu's own highlight instead of `GuiService.SelectedObject` (one highlight for every device): arrows / W S / D-pad / left stick, Enter / A, and BACK on Backspace / B, since Esc is Roblox's menu. Opening it on a gamepad mid-match is the open question in section 0.
- [ ] **Scaling:** build in `Scale` with `UIAspectRatioConstraint` and a `UIScale` driven by screen height (same rule as the HUD: 1080 p = 1, clamp 0.75–1.25). Test 16:9, 21:9, 4:3, and a phone. Built (2026-11-18) as a canvas laid out in 1080p pixels with the HUD's rule, shrunk further where the screen is under 1100 × 960; only seen in Studio's window (1609 × 793). **The four screen shapes are still to test.**
- [x] **What not to copy:** the Max Payne 3 logo, Max or any character, Rockstar's fonts and icons, Social Club, the exact wording of menu hints, narration lines. All art and text is ours. Kept: the logo is set in Oswald (the HUD's font), and every hint is our own wording.

---

## 3. Blender for the UI
All non-text UI art is made in **Blender**, rendered to PNG and uploaded. This keeps the menus looking 3D and cinematic without live `ViewportFrame` cost.

**Built 2026-11-18:** `Assets/Blender/UI/ui_lib.py` and the first images (the logo and the film overlays), uploaded and in `UiAssets`. How to run it: [[Blender and Asset Pipeline#UI art for the menus]].
- [x] **New folder** `Assets/Blender/UI/` with one `.blend` per asset group: `UI_Logo.blend`, `UI_Icons_Weapons.blend`, `UI_Icons_Items.blend`, `UI_Icons_Skills.blend`, `UI_Crates.blend`, `UI_Badges.blend`, `UI_Overlays.blend`, `UI_LoadoutBody.blend`. Made so far: `UI_Logo.blend`; `ui_lib.py` builds `UI_Icons_Weapons.blend` when the guns' FBX files are there. The overlays need no `.blend`: they are worked out pixel by pixel (exact, seamless, and identical every run).
- [x] **A render script** (`ui_lib.py`, like `mp_lib.py` for animations): opens a `.blend`, renders every object in a collection one by one through a fixed camera to `Exports/UI/<name>.png`, deterministic, so re-running gives identical files. Built; the images go to `Assets/Blender/UI/Exports/<name>.png` with `manifest.json` (sizes and hashes). Two runs gave byte-identical files.
- [x] **Render setup:** orthographic camera, transparent film (`Film > Transparent`), Eevee for speed, a soft three-point light rig shared by all icons, render at 2× the on-screen size and no bigger than **1024 px** (Roblox texture limit to check), PNG RGBA. Built with **Cycles on the CPU** instead of Eevee, so the same file comes out every time (a render takes seconds), no denoiser, Standard colour (no tone curve), and no metadata in the PNGs.
- [x] **Naming:** `UI_` prefix on every object and export (`UI_Icon_AK47`, `UI_Crate_Street`, `UI_Title_Badge_10`), matching CLAUDE.md's prefix rule.
- [ ] **What to make:**
  - [x] **Logo:** "MAXIMUM PAIN" as an extruded, scuffed metal or worn-print title, rendered flat-on. Variants: full, compact. Built: Oswald Bold, worn off-white paint over steel (chips, fine scratches, worn edges); `UI_Logo_Full` (one line, 1024 × 147, in the menu at 104 px high at 1080p) and `UI_Logo_Compact` (two lines, 628 × 320, not used yet).
  - [ ] **Weapon icons:** side-on, muzzle right (same as the HUD gun list), white and grey versions. Reuse the gun meshes from `ServerStorage.WeaponKit` / the gun `.blend`s. **The renderer is built and tried on the M9** (512 × 160 each, white; the grey is the same image tinted with `ImageColor3`, so one upload per gun). **The 13 icons wait for the guns' source:** `build_weapons.py`'s `Exports/FBX` isn't in the repo or on JordanSaa's PC, and Studio won't hand out the uploaded meshes (2026-11-18). Put the FBX files in `Assets/Blender/Weapons/Exports/FBX` and run `ui_lib.py weapons`.
  - [ ] **Item icons** (helmet, gas mask, goggles, armour, gear) and **skill icons** (one per skill, simple bold silhouettes that read at 48 px).
  - [ ] **Loadout body:** a grey human silhouette inside a radial ring (our own design, inspired by the loadout screenshot), rendered as a single image; slot positions recorded as UV coordinates so the Roblox UI places icons and leader lines on it.
  - [ ] **Crates:** 3D crate models (wooden ammo crate, police evidence box, metal case…) rendered closed, open, and as a short image sequence for the opening animation (sprite sheet).
  - [ ] **Title/level badges:** a patch or stamp per milestone, shown next to names (see section 8).
  - [x] **Overlays:** grain tile (256 px, seamless), vignette, bokeh blobs, light leaks, glitch strips. Built: `UI_Overlay_Grain`, `UI_Overlay_Vignette`, `UI_Overlay_Bokeh1` (warm) and `2` (cool), `UI_Overlay_LightLeak`. The glitch is done in code (`MenuKit.glitch`), so it needs no strips.
  - [ ] **9-slice panels:** panel frames rendered flat and used with `ImageLabel.ScaleType = Slice` so they stretch cleanly.
  - [ ] Optional: a slimmer **HUD health figure** (already listed under Known limits in [[HUD Layout]]).
- [x] **Import into Roblox:** upload as images (Asset Manager or Open Cloud), store IDs in one `UiAssets` module (`ReplicatedStorage.Modules`) so nothing hard-codes an asset ID. Done 2026-11-18 through Studio (signed in as 83tg); the ids are also kept in `Assets/Blender/UI/Exports/ui_ids.json`.
- [x] **Pre-rendered images vs ViewportFrames:** use images for menus (cheap, any number). Keep `ViewportFrame` only where it must react live (the HUD figure tinting limbs, a rotating skin preview in the shop).
- [x] Add the UI pipeline to [[Blender and Asset Pipeline]] when it's built.

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
| Mockup slot | Holds | In-game key | Slot name in code ([[Loadout and Dual Wielding]]) | Until 2026-11-14 |
|---|---|---|---|---|
| **Primary** | the two-handed gun (rifle, shotgun, SMG, sniper) | 3 | `Primary` | `Two` |
| **Secondary** | one-handed gun 1 (pistol, revolver, one-handed SMG, sawn-off) | 1 | `Secondary` | `OneA` |
| **Tertiary** | one-handed gun 2 | 2 | `Tertiary` | `OneB` |
- [x] **Rename the slots in code as well as in the UI** (decided 2026-11-14, for continuity): `Two` → `Primary`, `OneA` → `Secondary`, `OneB` → `Tertiary`, everywhere in one change (`LoadoutRules`, `WeaponConfig` users, remotes, attributes, the HUD gun list, `Keybinds`, tests). Grep for all three old names first, do it before the server profile is built so no saved data ever holds the old names, and update [[Loadout and Dual Wielding]] afterwards. **Done 2026-11-14**, before the profile existed: six scripts (`LoadoutRules`, `LoadoutService`, `WeaponController`, `Keybinds`, `AnimationController`, `Hud`); no script holds an old name. The clip names with "Two" in them (`CoverHoldHighTwo`, `BlindFireHighTwoLeft`…) mean two-handed, are published animations, and stay.
- [x] **Keys stay as they are** (decided 2026-11-14): 1 = Secondary, 2 = Tertiary, 3 = Primary, 4 = dual wield. No re-mapping to 1 = Primary.
- [ ] A slot can be left empty (lighter weight). Dual wielding (key 4) uses Secondary + Tertiary and still drops the Primary, as built.
- [ ] **The same gun may go in Secondary and Tertiary** (decided 2026-11-10), e.g. two Desert Eagles. Owning the gun once covers both slots. Each copy counts its own weight (two Desert Eagles = 6). Check that `LoadoutRules`, pickups and the HUD gun list handle two guns with the same id (they key some things by gun name today).
- [ ] Each slot's picker only lists guns that fit it (the two-handed list for Primary, the one-handed list for the other two), read from `WeaponConfig.OneHanded`.

### Saved loadouts
A **saved loadout** = Primary + Secondary + Tertiary + throwable + Head + Chest + Gear item + Skill, with a name. Max Payne 3 let players build **up to five** custom loadouts and choose one before each spawn. 📰
- [ ] **5 saved loadouts** (decided 2026-11-14), plus the **4 presets** below, read-only, which can be copied into a custom slot. **Slots 1–3 are free; slot 4 unlocks at level 10, slot 5 at level 25.** On prestige slots 4 and 5 lock again until those levels are reached; what was saved in them is kept, and if one was selected the selection falls back to slot 1.
- [ ] Loadout screen: a list of saved loadouts down the left (PRESET: RIFLEMAN … CUSTOM 1 … CUSTOM 5, locked ones greyed with "LEVEL 10" / "LEVEL 25"), the selected one's details on the right. 🎨 In the UI style of section 2.
- [ ] Actions: **Select** (use on next spawn), **Edit**, **Copy** (preset → custom), **Rename**, **Reset**.
- [ ] Choosing a loadout is possible from: the main menu Loadout screen (**M**, at any time) and the death screen (before respawn). Players can switch freely, but **the new loadout is only received on death** (next spawn), never mid-life.
- [ ] Remember the last selected loadout in the profile, so Play uses it straight away.
- [ ] Unlocking: if a saved loadout contains something no longer owned (e.g. after a prestige reset), the server swaps that slot for the default and the screen flags it in red.
- [ ] Saved on the server (section 9); the server re-checks the whole loadout every time it spawns the player, not only when it was saved.

### Screen layout
- [ ] Follow the mockup's text: **Primary / Secondary / Tertiary** weapon slots, **Loadout Weight**, **Skill**, plus the saved-loadout list.
- [ ] Use the loadout screenshot's structure for the selected loadout: left = our character posed with the chosen Primary; right = the body-in-a-ring diagram with slots: Head, Chest, Gear, Secondary, Tertiary, Primary, throwable, Skill; weight bar along the bottom.
- [ ] Selecting a slot opens a list of everything that fits it: icon, name, short stats (damage, fire rate, accuracy, magazine), weight, lock state ("UNLOCKS AT LEVEL 20", "$2,500").
- [ ] Live match in the background (same grade as other menus).
- [ ] **Loadout names are editable** (decided 2026-11-14). The client sends the typed name through a `RenameLoadout` remote; the server trims it, limits it to ~20 characters, runs `TextService:FilterStringAsync` (in `pcall`) and stores the filtered result; if filtering fails the old name stays. Default names are CUSTOM 1 … CUSTOM 5. Only the owner ever sees their loadout names; if they are ever shown to other players (kill cam, scoreboard), filter per viewer with `GetNonChatStringForBroadcastAsync`. 🎨 The text box follows the UI style of section 2.
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
- [x] **Weight allowance does not increase with level** (decided 2026-11-14). No level-based cap: every player may build any loadout they own from level 1, and the class penalties above are the limit. The weight bar's full length is the heaviest possible loadout (24 today). Nothing about weight is reset or earned through prestige.
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
- [x] **Last Stand takes all adrenaline, no matter what** (decided 2026-11-14): every full segment and any part-filled one, as it does today. It still needs at least one full segment to start ([[Last Stand and Bullet Time]]).
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
- [ ] **Levels 1–50** (cap decided 2026-11-14). **Target (decided 2026-11-14): level 1 → 50 in about 20 hours**, so all five prestiges take about 100 hours.
  - XP to go from level L to L+1: **`300 + 50 × (L − 1)`**: level 2 needs 300 XP, level 49 → 50 needs 2,700; **73,500 XP** for 1→50.
  - Working (estimates, to check against real match data): a 12-minute match pays about 750 XP on average (half wins at 1,000 and half losses at 250 = 625, plus ~10 kills = 100, plus ~25 in assists and bonuses). 73,500 ÷ 750 ≈ 98 matches ≈ 20 hours.
  - If matches turn out shorter or longer, or kills per match differ, change the two curve numbers, not the rewards.
- [ ] **Rewards for match performance (server-counted).** **Decided 2026-11-14: Cash and XP use the same values**, and every row below pays:
  | Event | Cash ($) | XP | Status |
  |---|---|---|---|
  | **Kill** | **$10** | **10** | Decided |
  | **Match won** | **$1,000** | **1,000** | Decided |
  | **Match lost** (played to the end) | **$250** | **250** | Decided |
  | Assist (≥25% of the damage) | $5 | 5 | Decided |
  | Headshot kill | +$3 | +3 | Decided |
  | Kill while shoot-dodging / in bullet time | +$3 | +3 | Decided |
  | Kill from Last Stand | +$5 | +5 | Decided |
  | Revenge kill (killed your last killer) | +$3 | +3 | Decided |
  | Challenge tier | same as its XP | per challenge | Decided to pay; amounts per challenge (section 7) |
- [ ] Win and loss payouts only go to players who were in the match for most of it (placeholder: at least half the match time), so joining at the last minute doesn't pay $1,000.
- [ ] **Cash** is paid by the server as the events happen (or totalled at match end), then × the player's **cash multiplier**. **XP is not multiplied.** Cash is what buys crates, skins, skills and items.
- [ ] Match-end screen lists what was earned: kills × $10, win bonus, multiplier, total. 🎨 In the UI style of section 2.
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
- [ ] **Prestige (decided 2026-11-14): levels I to V.** At level 50 the player may prestige from the main menu, which **resets their level to 1**. Max prestige is **5 (V)**; at prestige V, level 50 is the end.
  | Prestige | Icon | Cash multiplier bonus | Title (placeholder) | Extra |
  |---|---|---|---|---|
  | 1 | **I** | +20% | Wanted | |
  | 2 | **II** | +40% | Marked Man | |
  | 3 | **III** | +60% | Feared | |
  | 4 | **IV** | +80% | Notorious | |
  | 5 | **V** | +100% | Infamous | Mastery skin finish (idea) |
  - [ ] **Kept on prestige (everything cosmetic):** skins (owned and equipped), titles (unlocked and selected), accessories, unopened crates, stats, settings, and the contents of all saved loadouts.
  - [ ] **Reset on prestige:** level and XP (to level 1, 0 XP), **guns**, **skills** (all levels, bought or free), **gameplay items** (helmet, vests, gear; decided 2026-11-14), **cash (to $0)**, and **loadout slots 4 and 5** (locked again until levels 10 and 25).
  - [ ] Saved loadouts that hold something no longer owned fall back to defaults slot by slot (rule already in [[#Saved loadouts]]); equipped skins stay attached to the gun for when it's unlocked again.
  - [ ] **Cash multiplier: +20% per prestige, stacking** (I = ×1.20 … V = ×2.00), applied to all earned Cash. **Decided 2026-11-14: the level milestone multipliers stay and the two add** (prestige III at level 40 = 1.40 + 0.60 = ×2.00; maximum prestige V at level 50 = ×2.50). The level part resets to ×1.00 with the level on each prestige.
  - [ ] **Prestige icon:** a **Roman numeral (I, II, III, IV, V)** shown **next to the player's title** everywhere the title appears: player card, name tag, scoreboard, kill feed, kill cam panel. One small badge per numeral, made in Blender (`UI_Prestige_I` … `UI_Prestige_V`, section 3). 🎨 In the UI style of section 2: white numeral, hard-edged plate, no colour except where the palette allows.
  - [ ] **Confirm screen** before prestiging, listing exactly what is lost and kept, with a hold-to-confirm. 🎨 Same style. The server performs the reset in one profile update (`Prestige` remote: checks level 50 and prestige < 5).
  - [ ] The "Old Badge" gear item (Max Payne 3's Badge of Honor) is no longer needed: the multiplier is built into prestige.
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
- [ ] Players **choose which unlocked title to show** (decided 2026-11-14; in Loadout or a Profile screen). The server checks the title is unlocked.
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
    Version, Level, XP, Cash, Prestige,  -- Prestige 0..5
    TitleSelected,
    TitlesUnlocked = {}, Unlocks = { Guns, Items, Skills = { id = levelOwned } },
    Loadouts = { [1..5] = { Name, Primary, Secondary, Tertiary, Throwable, Head, Chest, Gear, Skill } },
    SelectedLoadout,  -- 1..5, or a preset id
    Skins = { owned ids, equipped per gun }, Crates = { id = count },
    Challenges = {}, Stats = { Kills, Deaths, HeadshotKills, Matches, Wins, PlaySeconds, ... },
    Settings = { volumes, keybinds, accessibility },
    Purchases = { receiptIds processed },
  }
  ```
  - **Built 2026-11-14 (Phase A):** `ProfileService`, with `ProfileSchema` (the fields) and `ProfileStorage` (the DataStore), in ServerScriptService. The profile holds `Version, Level, XP, Cash, Prestige` and `Stats = { Kills, Deaths, HeadshotKills, Matches, Wins, PlaySeconds }` so far. **Each later step adds its own fields** (titles, unlocks, loadouts, skins, crates, challenges, settings, purchases) with a default in `ProfileSchema.new` and a check in `ProfileSchema.validate`; old saves get the default when they load, with no version change.
  - **How code uses it:** `ProfileService.get(player)` returns the profile, frozen. `ProfileService.update(player, function(profile) … end)` is the only way to change one: the function edits a copy, which replaces the profile only if it finishes without an error or a wait and passes `validate` (so a save never catches a change half done, and a negative balance or level 51 is refused). `ProfileService.release(player)` saves and unlocks before a teleport. `Loaded` and `Changed` signals. Level, XP, Cash and Prestige are copied to attributes on the Player for the menus to read.
- [x] **DataStore safety** (see `roblox-datastores` practice): session locking so two servers can't load the same profile (ProfileStore-style), `UpdateAsync` not `SetAsync`, retries with backoff in `pcall`, autosave every ~60–120 s, save on leave and in `game:BindToClose`, schema `Version` with migrations, never save mid-transaction. **Built 2026-11-14:** one key per player (`Player_<UserId>` in the `PlayerProfiles` DataStore; Studio play tests use `PlayerProfiles_Studio`), the lock taken in the same `UpdateAsync` that loads, refreshed by each autosave (60 s) and free after 180 s without one; every save first checks the lock is still this server's; a player whose profile can't be loaded is kicked, never given a fresh one. Tested against a stand-in DataStore; **not yet against the real one** (Studio's API access is off, see the [[Changelog]]).
- [ ] **XP and cash only from server events:** the damage system (server-side) records who damaged whom; on death the server awards kill/assist XP. Match-end XP/cash computed by the server's match manager. **No remote ever carries an XP or cash amount.**
- [ ] **Remotes the client may call** (all validated, rate-limited):
  | Remote | Carries | Server checks |
  |---|---|---|
  | `SetLoadout` | loadout index + Primary/Secondary/Tertiary/throwable/item/skill ids | index unlocked (slots 4 and 5 need levels 10 and 25), ids exist, unlocked & owned, Primary is two-handed and Secondary/Tertiary one-handed (`LoadoutRules`) (applies on next spawn) |
  | `RenameLoadout` | index 1–5 + name | index unlocked, length limit, filtered with `TextService`; stores the filtered text only |
  | `SelectLoadout` | index 1–5 or preset id | valid; stored now, used at the next spawn |
  | `Prestige` | nothing | level 50, prestige < 5; reset and grant in one profile update |
  | `SwitchServer` | yes / no | an offer is pending for this player; the server picks the target, never the client |
  | `BuyItem` | item id | unlocked at this level, not owned, enough Cash; deduct and grant in one profile update |
  | `BuySkill` | skill id | Lv 1 unlock level reached, not owned, enough Cash; deduct and grant in one profile update |
  | `BuySkin` | skin id | for sale now, enough Cash, not owned |
  | `OpenCrate` | crate id | owns one (or enough Cash), crate not complete for this player, policy allows; **roll on the server** among skins not yet owned |
  | `EquipSkin` | gun id + skin id | owns skin, skin fits gun |
  | `SetTitle` | title id | unlocked |
  | `SaveSettings` | settings table | types and ranges checked, size limit |
- [ ] **Robux purchases:** `MarketplaceService.ProcessReceipt` on the server only; idempotent (store `PurchaseId`, return `PurchaseGranted` only after the profile saved). Never grant from a client message.
- [ ] **Anti-farm:** cap XP per minute; no XP for killing the same player more than N times in a short window when they don't fight back (AFK farming); reduced or no XP in private servers with fewer than N players; no XP from team kills or from your own Trust Issues friendly fire.
- [ ] **Sanity and logging:** log big jumps (cash > X per match, level jumps) to an analytics/log store for review; `AnalyticsService` economy events for every Cash source and sink.
- [ ] **Leaderboards:** `OrderedDataStore` written by the server (level, kills, season XP).
- [x] **Testing:** a cheat remote that only exists in Studio (`RunService:IsStudio()`) to set level/cash for testing, added to `Tools/TestHarness.luau`. Never shipped. **Built 2026-11-14:** `ServerStorage.Tools.ProfileCheats` (in the repo as `Tools/ProfileCheats.luau`), cloned into ServerScriptService for a play session, and `mp.profile({ Level = 20, Cash = 5000, Prestige = 1 })` in the harness; how to install is in [[Test Arena]]. It goes through `ProfileService.update`, so it can't set a value the rules refuse.
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
- [x] **Decided 2026-11-14: crates are bought with $ (Cash), earned from match performance** ($10 per kill, $1,000 per win, section 8), **and Cash can't be bought with Robux.** Then crates aren't paid random items. Still show odds on every crate. Crate prices to set against those earnings (e.g. a crate at $2,500 ≈ two wins).
- [ ] **If Robux comes later:** sell skins directly for Robux (Developer Products), not Cash. If Cash or crate keys are ever sold for Robux, every rule above applies at once.
- [ ] **One config, two readers:** `ShopConfig` (ReplicatedStorage) holds each crate's items and weights; the server rolls from it and the odds screen reads from it, so the shown odds can never differ from the real ones. Odds computed as `weight / total weight`, shown to 2+ decimals.
- [ ] **Roll on the server** with `Random.new()` seeded on the server; log every roll (player, crate, result) for support.
- [ ] Example crate (placeholder; the odds a new player sees, before any skin is owned):
  | Rarity | Chance | Items |
  |---|---|---|
  | Common | 70.00% | 7 skins, 10.00% each |
  | Uncommon | 20.00% | 5 skins, 4.00% each |
  | Rare | 7.50% | 3 skins, 2.50% each |
  | Very Rare | 2.20% | 2 skins, 1.10% each |
  | Exceptional | 0.30% | 1 skin, 0.30% |
  | **Total** | **100.00%** | |
- [ ] **No-duplicate crates** (decided 2026-11-14): a crate never gives a skin the player already owns.
  - [ ] Before rolling, the server removes every owned skin from that crate's list and rolls among the rest by their weights. Skins bought directly from the shop count as owned too.
  - [ ] **The odds shown are per player:** recomputed from the skins that player still lacks (`weight ÷ total weight of what's left`), still adding up to 100%. The Details pop-up greys out owned skins and marks them OWNED. Same shared function for the roll and the display, so they can't differ.
  - [ ] **Crate complete:** when the player owns everything in a crate, it shows COMPLETE and can't be bought or opened; the server refuses `OpenCrate` for it. 🎨 In the UI style of section 2.
  - [ ] Crate cards show progress (`7 / 18 SKINS`).
  - [ ] Unopened crates already held are opened against what's owned at the moment of opening, not at purchase. If one is held for a crate that has since been completed, refund its full price.
  - [ ] Completed crates stop taking Cash, so plan new crates over time to keep something to spend on.
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
Reordered 2026-11-14, after every decision in section 0 was settled. Starts after the animation work's blockers ([[Animation and MP3 Systems - Progress and To Do#To do (in order)|its to-do]]: save, publish, two-client test). The rule behind the order: **each step only uses things built in the steps before it**, and each step ends with something that can be played and tested.

**Phase A: foundations (nothing visible, everything else stands on it)**
**Phase A was built on 2026-11-14** ([[Changelog]]), ahead of two of the animation work's blockers (publishing the place and the two-client test, both still open). To do before it reaches live players: turn on Studio's API access and test saving against the real DataStore, the two-client test (kills scoring between two players), and the `roblox-dev:roblox-reviewer` check.
1. [x] **Rename the weapon slots in code** (`Two/OneA/OneB` → `Primary/Secondary/Tertiary`, section 5). First, because every later step (profile, remotes, loadout screen) would otherwise be written with the old names and renamed twice. Done 2026-11-14.
2. [x] **Server profile + DataStore safety** (section 9), with the Studio-only cheat remote to set level, cash and prestige. Nothing else may save data on its own. Every later step reads and writes through this. Done 2026-11-14: `ProfileService` (`get`, `update`, `release`), `ProfileSchema`, `ProfileStorage`, `ProfileCheats`; details in section 9.
3. [x] **Match manager** (new step; nothing like it exists in the code yet): match start and end, timer, who won and lost, how long each player was in the match. The win and loss payouts ($1,000 / $250) can't exist without it, and the menu's "current match" line reads from it. Done 2026-11-14: `MatchService` and `MatchRules` ([[Architecture]]). Free-for-all only, a kill is a point, the most points wins (ties share it, nobody wins on 0). Placeholders in `MatchRules`: 8-minute matches, 15 s between them, 2 players to start, half the match to count as won or lost. For step 7: `MatchService.Ended` carries each player's `won` and `eligible` (pay the win or loss only when `eligible`), and `LastStandService.Killed` gives each kill with its killer. For the menu: the attributes on `ReplicatedStorage.Match` (`State`, `Mode`, `Map`, `Number`, `EndsAt`).

**Phase B: the menu shell**
**Phase B was built on 2026-11-18** ([[Changelog]]). Left open: a gamepad button to open the menu mid-match (the question in section 0), the 13 weapon icons (waiting for the guns' FBX files, section 3), and testing on 21:9, 4:3 and a phone.
4. [x] **Shared UI kit in the section 2 style:** the list with the white selection bar, heading, context line, prompts, panel gradient, film overlays, `UIScale` rule, keyboard/gamepad navigation. Built once as modules, so every later screen is assembled from it instead of restyled. Placeholder art is fine here. Done 2026-11-18: `MenuKit`. A new screen is one entry in `MenuController`'s `SCREENS` (a heading, a context line, and rows that say what choosing them does).
5. [x] **Menu shell:** `CharacterAutoLoads = false`, main menu on join over the live match camera, PLAY spawns through the server, **M** opens and closes it mid-match (test **Start** on gamepad now, section 1). Player card with avatar, title, name, level and money, showing real profile values (all zeros for now). Done 2026-11-18: `MenuController`, `MenuCamera`, `SpawnService`, `MenuRules`; plus LEAVE MATCH. Start turned out to be Roblox's (section 0).
6. [x] **Blender UI pipeline and first assets** (logo, overlays, weapon icons, section 3). Can run alongside steps 4–5; the images swap in for the placeholders when ready. Done 2026-11-18 apart from the weapon icons: `ui_lib.py`, the logo and the five overlays, uploaded and in the menu. The icons' renderer is ready; the guns' source isn't on this PC.

**Phase C: progression (so later screens have real levels and cash to lock things behind)**
Found in the place on 2026-11-18, built outside these notes: `ProgressionService`, `CombatLog`, `ProgressionRules`' curve, rewards and titles, `PlayerCard`, `Scoreboard`, `MatchHud`, `KillFeed`, `NameTags` and `MatchEndScreen` cover most of steps 7 and 8 ([[Architecture]] lists them). Not checked against the plan here and not ticked: whoever built them should write them up and tick what's done.
7. [ ] **XP, cash, levels and stats** (section 8): rewards from the server's own kill and match events, the level curve, the level cash multiplier, the stats on the player card, the XP bar, the match-end earnings screen, the level-up moment.
8. [ ] **Titles, name tags and scoreboard:** milestone titles, picking a title, the name tag (distance and line-of-sight rule), Tab scoreboard, kill feed.

**Phase D: loadouts**
9. [ ] **Stamina and health regeneration:** the weight classes change regen, stamina and aiming speed, and neither system is built yet ([[Movement State Machine]], [[Limb Health]]).
10. [ ] **Loadout screen:** five saved loadouts (slots 4 and 5 locked to levels 10 and 25), presets, rename, gun stats as bars plus numbers, weight and classes, switch any time and receive on death, change loadout on the death screen. Gun unlock levels and prices, bought with Cash (`BuyItem` pattern).

**Phase E: skills and items**
11. [ ] **Adrenaline as three segments**, then the **status effects module**, then the **skills framework** and first-wave skills with `BuySkill`.
12. [ ] **Items, first wave** (the ones that work with what's built), on the same status effects module.

**Phase F: shop**
13. [ ] **Shop, direct-purchase skins** first: rarity colours, skin cards, preview, equip.
14. [ ] **Crates:** no-duplicate rolls on the server, per-player odds pop-up, COMPLETE state, opening animation, `PolicyService` check.

**Phase G: the long tail**
15. [ ] **Prestige (I–V).** Late on purpose: it resets guns, skills, items, cash and loadout slots, so all of those must exist first. Needs the prestige icons from Blender.
16. [ ] **Settings:** audio sliders, keybind rebinding, the accessibility toggles that need no new systems. Nothing waits on it, so it can be pulled earlier whenever a break from systems work is wanted; a minimal version (volume, sensitivity) could ship with step 5.
17. [ ] **Challenges** (section 7).
18. [ ] **Join flow: offer a switch to a fuller server** (section 1), once there are enough players for it to matter.
19. [ ] The items and skills that need minimap, looting, grenades, melee or objective modes, as those systems arrive.

Before publishing any step that touches cash, XP or purchases: run the `roblox-dev:roblox-reviewer` check (section 9).

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
