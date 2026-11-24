# Changelog

Every change to the game, newest first. Each entry says what changed, the decisions behind it, what was tested, and what was left out.
System details: [[Architecture]] · [[Movement State Machine]] · [[Loadout and Dual Wielding]] · [[Cover System]] · [[Shoot-Dodge]] · [[Last Stand and Bullet Time]] · [[Animation Hooks]] · [[Test Arena]] · [[Weapons and Recoil]] · [[Limb Health]] · [[HUD Layout]]

## 2026-11-23: Phase F of the menu plan: the skin shop, 54 skins and three crates
On this PC (Studio signed in as 83tg), with Claude Code driving Studio and Blender. JordanSaa asked for Phase F (steps 13 and 14 of [[Menus, Loadout, Progression and Shop - To Do#Suggested build order]]), of high quality and with no mistakes; built 2026-11-22 and 23, nothing past it.
- 3 scripts added (`ShopConfig`, `ShopService`, `ShopScreen`) and 7 changed (`ProfileSchema`, `LoadoutService`, `CharacterServer`, `GameServer`, `MenuController`, `MenuKit`, `UiAssets`) in the Team Create place; 4 remotes added (`BuySkin`, `OpenCrate`, `EquipSkin`, `ShopEvent`); `ReplicatedStorage.Assets.Skins` (the 22 finishes) and `ReplicatedStorage.Assets.UI.GunModels` (the 13 guns, textured, for the shop's 3D views) added. In the repo: `Assets/Blender/Skins/skin_lib.py` (new) and the crates in `Assets/Blender/UI/ui_lib.py`, with their images and ids. No clip changed.
- **What players will notice:** SHOP in the main menu is open. It sells two skins a day and one a week for Cash, and three crates at $2,500 that each give a skin the player doesn't own yet, with that player's odds shown first. A skin is a finish for one gun (blued steel, desert paint, chrome, black and gold...), shown on a slowly turning 3D gun; the one equipped for a gun is on it from the next spawn, and stays on it when it is dropped and picked up by someone else. Looks only: no stat reads a skin.

**Decided with JordanSaa** (asked and answered 2026-11-22; all in the plan's section 0, Phase F questions)
- **Skins are finishes for now:** every gun is coloured from one 4 × 4 palette texture, so a skin colours its 16 squares again (colour, metal, shine), some with a second finish on the moving parts and magazine. No patterns until guns have real UVs.
- **54 skins in three lines of 18, a crate each:** GUNSMITH (factory and gunsmith finishes), STREET (paint jobs) and CARTEL (plating); per crate 7 common, 5 uncommon, 3 rare, 2 very rare and 1 exceptional.
- **Sold two ways:** 2 skins a day (new at 00:00 UTC) and 1 featured a week, the same in every server; every skin also comes from its crate, which never gives one the player owns.
- **Prices:** a crate $2,500; a skin bought directly by its rarity: $1,500 / $3,000 / $6,000 / $10,000 / $20,000.
- **Where Roblox restricts random items** (`PolicyService`): crates open in a shown order instead, the next skin named before buying.

**My calls, not asked**
- The storefront: the featured skin is rare or better, the daily two common to rare, the three always of different guns, picked from the date with a fixed hash (`ShopConfig.stock`), so it can't drift between servers or engine versions. A purchase sent just before the turnover still goes through in the 30 s after it.
- A crate bought with Cash opens at once (`OpenCrate`); crates held (the profile's `Crates`) are for rewards later, and nothing hands them out yet. An open uses a crate held before any Cash.
- Until `PolicyService` answers for a player (three tries, 5 s apart), and for good if it never does or its answer lacks the field, their crates open in order: the safe side.
- A skin goes on from the next spawn, as a loadout does, and equipping is free. A gun keeps its skin wherever it goes; the test arena's rack guns wear none.
- The opening: the crate shakes until the server answers (then 0.55 s more), opens in a flash of the skin's rarity colour (0.45 s), and the skin rises (0.5 s): about 1.5 s, under the plan's 3 s. SKIP shows it at once, reduce motion skips it, and nothing spins past other skins, so there is no near miss to see. Made from the closed and open crate pictures, so the plan's sprite sheet isn't needed.
- Odds shown exactly to the hundredth when they are exact (10.00%), else rounded to four places below their first digit (66.667%, 0.33333%) with Roblox's rounding note.
- A skin's name is its gun's short name and its finish's (AK-47 IVORY & GOLD).
- The economy dashboard takes at most 100 SKUs an experience, so a skin bought logs its rarity as the SKU (skin_rare) and the skin in a custom field; a crate logs its id.

**New: the catalogue and the rules both sides share** (`ShopConfig`, ReplicatedStorage.Modules)
- Five rarities, each a colour (section 2's: grey, teal, steel blue, violet, amber; never red), 1 to 5 pips, a direct price and a weight in a crate (100 / 40 / 25 / 11 / 3: a full crate gives 70 / 20 / 7.5 / 2.2 / 0.3%, section 10's example exactly).
- 22 finishes and 54 skins (ids `skin_<gun>_<finish>`, which never change once owned); TWO-TONE and BLACK & GOLD wear one finish on the frame and another on the moving parts and magazine. Three crates of 18 in their shown order, every gun in every crate.
- `odds(crate, owned)`: the skins the player lacks, each its weight over the weight left. `roll` picks with the same numbers (a whole-number ticket), `nextInOrder` takes the first lacking in the shown order (commons first), `progress` and `isComplete` count. One module for the server's roll and the screen's odds, so they can't differ.
- `stock(now)` and `onSale` (above); `dress(model, gun, skin)` puts each finish's `SurfaceAppearance` on the parts by their names (Handle: the frame; Slide, Bolt, Pump, Cylinder, Hammer, Barrels: the moving parts; Magazine), leaves shells as they are and sets the gun's `Skin` attribute; `wearing` keeps only owned skins that fit.
- Checks itself as it loads: every id and reference, the odds and the roll over every crate as it fills, names and prices; in Studio also a year of storefronts.

**New: the shop on the server** (`ShopService`)
- `BuySkin` (a skin on sale now, not owned, the Cash), `OpenCrate` (a crate not complete, a crate held or its price; since the review also the mode the screen showed), `EquipSkin` (an owned skin for that gun, or nothing): every argument type- and length-checked, everything decided from the player's own profile. Buying and opening share one rate (2 at once, then one each 0.5 s); equipping has its own (3, then one each 0.25 s).
- The Cash and the skin change together in one profile update, checked again inside it; a crate's skin is picked inside the update that pays for it, so a crate can't give a duplicate or give without being paid.
- Each purchase, opening and refund prints a line (the player's id, what, the skin, the Cash left) and logs a Cash event with `AnalyticsService`.
- The owner is sent their shop ("State": skins owned and equipped, crates held, whether crates open in order, the storefront) on every change, at each daily turnover and when their screen asks; "Bought", "Opened", "Equipped", "Refunded" and "Refused" answer requests.
- Crates held for a complete crate are refunded their price, as it completes or as the profile loads.

**The screens** (`ShopScreen`; `MenuController`, `MenuKit`)
- **SHOP**, laid out as the mockup: the Cash and the cosmetic-only note top left with the time to the next daily skins, the two TODAY cards and the tall FEATURED card (the gun in its finish in 3D, the rarity's chip and pips, the price or OWNED / EQUIPPED), and the three crate cards (picture, price or crates held or COMPLETE, progress). The list on the left has the same things as rows, then YOUR SKINS; hovering or clicking a card is its row.
- **A skin:** the gun turning slowly in its finish on a grey plate, its rarity, its gun and crate, whether it is on sale; BUY while it is, EQUIP or TAKE OFF once owned, and a row to its crate.
- **A crate:** its picture (COMPLETE across it when done), its finishes, a progress bar, and the odds by rarity (skins left, each one's chance, the rarity's total); OPEN and ODDS. **ODDS:** each rarity's line of odds over the skins it covers, the owned ones apart; in order, ORDER lists every skin numbered with the next marked.
- **The opening** (above), then EQUIP, OPEN ANOTHER or DONE; drawn from the crate as it was, so nothing gives the skin away early.
- **YOUR SKINS:** each gun with what it wears and how many of its skins are owned; then STANDARD and its skins.
- Refusals show in red under the list; purchases, equips (APPLIES ON NEXT SPAWN while in the fight), refunds and skins out of a crate in white, and ones that come while the menu is closed show one by one as soon as it opens again.

**Skins on guns** (`ProfileSchema`, `LoadoutService`, `CharacterServer`)
- The profile gained `Skins` (`Owned`, `Equipped` per gun) and `Crates` (held, 1 to 999 per crate), checked by `validate`; older saves load with none.
- Every spawn dresses the guns in the owner's equipped skins (`ShopService.wearing`, `LoadoutService.makeGun`).

**The art**
- **Finishes:** `Assets/Blender/Skins/skin_lib.py` works out each finish's colour, metalness and roughness maps square by square (which square colours what was found with two probe palettes on all 13 guns) and keeps a record of the uploads (`pending`, `record`); 66 maps, 54 distinct images, uploaded by 83tg; one `SurfaceAppearance` per finish in `ReplicatedStorage.Assets.Skins`.
- **Crates:** `ui_lib.py crates` builds `UI_Crates.blend` and renders six 1024 × 640 pictures: a wooden ammunition crate (GUNSMITH), a police evidence box (STREET) and a black hard case (CARTEL), each closed and open; uploaded by 83tg and in `UiAssets` ([[Blender and Asset Pipeline#UI art for the menus]]).
- **The 3D views** dress `ReplicatedStorage.Assets.UI.GunModels`, a textured copy of each kit gun.

**The review** (the `roblox-dev:roblox-reviewer` agent over 13 scripts: the three new ones, every changed one but `UiAssets`, and `ProfileService`, `ArmoryService`, `UiStyle` and `WeaponConfig` for context)
- No client can get Cash, a skin or a crate it shouldn't, pay less or twice, buy a skin that isn't on sale, open a complete crate, equip a skin it doesn't own or that doesn't fit, or make the server error or wait inside a profile update. The odds and the roll match exactly, a duplicate can't happen, and the new profile fields, the refunds, the storefront's turnover and the screens' connections were sound.
- It found three medium and nine low problems, and six design questions. All twelve are fixed below and tested.
- **A second pass over the fixes** (the same agent, the changed scripts) found all twelve correct, no new security or data problem, and two small new ones in the screen (13 and 14 below), fixed and tested.

**Fixed**
1. **The opening could give the skin away early** (medium). The reveal draws the crate as it was before the skin, but the server's new "State" (with the skin owned) could arrive before "Opened", so during the shake the crate could already count the skin (NONE LEFT for the one exceptional, COMPLETE for the last skin, NEXT naming the skin after it). The crate's "before" now always leaves the skin out.
2. **OPEN ANOTHER said "picked by the odds" where crates open in order** (medium), and quoted Cash when a crate held would be used. OPEN and OPEN ANOTHER now share one hint: COMPLETE, else the next skin by name where crates open in order, else a crate held, else the odds and the Cash.
3. **The catalogue's self-check held up every player's join** (medium): a year of storefronts, about 5,000 of them, worked out as the module loaded, 0.9 s on this PC before the menu could show. The year's check now runs in Studio only, each skin id's hash is worked out once, and the storefront is kept per day (it only changes with the day); the catalogue now loads in 33 ms in the server's VM in Studio and less live. The storefront is the same as before (2026-11-22's checked).
4. **A crate could open differently from what its screen said** (low): a player whose first "State" said in order (no answer from `PolicyService` yet) could press OPEN on "THE NEXT SKIN IN ITS ORDER: M9 PARKERIZED" just as the answer came, and get a random skin. The screen now sends the way it showed the crate; if that no longer holds the server refuses ("Changed": THIS CRATE NOW OPENS DIFFERENTLY FOR YOU) and sends the shop again. And an answer missing its field now counts as restricted, not as free.
5. **A result arriving with the menu closed was lost** (low): a crate opened just before dying (the menu closes) gave its skin but never said which. Such notices are now kept and shown when the menu is next open (13).
6. **A 3D view that failed once stayed wrong** (low): had a gun's model or a finish not been there when a card was first drawn, the card stayed blank or in the kit's colours all session. A view now keeps its gun only once it is drawn whole, and `ShopConfig.dress` says whether every finish was found.
7. **The turning gun snapped back** (low) whenever the screen redrew (hovering, an answer from the server). It now turns on through redraws.
8. **The odds read as covering owned skins** (low): ODDS FOR EACH SKIN BELOW: 11.111% sat over names some of which were owned (a 0% chance). Owned skins now follow apart, under OWNED: NOT IN THE ODDS.
9. **The odds list had 24 rows** (low): a bigger crate would have lost skins off it. Rows are now made as needed.
10. **BUY could stay at BUYING** (low) if the server dropped the request for coming too fast. It now gives up after 6 s, says NO ANSWER, and BUY works again.
11. **BACK after clicking a card went to the wrong row** (low): the click skipped the menu's record of the row chosen. Cards now choose their row the way a click on the row does (`Nav.choose`).
12. **Refunds weren't on the economy dashboard** (low): each crate refunded now logs a Cash source.
13. **Notices kept while the menu was closed overwrote each other** (low, from the second pass): a crate's last skin and the refund it brought arrive together, and only the refund was kept, so the player still never learned the skin. They are now kept in order and shown one by one (3 s apart) as soon as the menu is open again, on whatever screen it opens at (fix 5 first showed them only once the shop was opened, which a player going straight to LOADOUT might never do).
14. **The odds could run over the prompts on short screens** (low, from the second pass): with the owned skins apart (fix 8) a crate's odds list grows to 22 rows, and on 1366 × 768 and smaller its panel ran over SELECT and BACK. The shop's panel now shrinks to the screen's height as well as its width.

**Design questions from the review** (left for later)
- A crate handed out free by a future reward is refunded the full $2,500 once its crate is complete: a Cash source. When rewards come: give only crates of incomplete crates, or refund less?
- Anyone can work out a year of storefronts from the public module and the date. Intended: it's what makes every server agree.
- A mistake in the catalogue stops the game as it loads (as `WeaponConfig`'s do), and the module is required by the guns' setup and the menu: every catalogue change needs a Studio play test before publishing.
- Prestige keeps cosmetics (section 0): when it is built it must keep `Skins` and `Crates`, not rebuild the profile from `ProfileSchema.new()`.
- `dress` assumes the kit's MeshParts have no `SurfaceAppearance` of their own and that every part is named by its role: checked, none has one, and only the shotguns' Shell and Shells fall outside the roles, on purpose.
- `ShopService` waits for its remotes as it loads and `CharacterServer` requires it, so a missing remote would hold up every character's setup. The four remotes are in the place.

**Found and fixed in the checks** (not from the review)
- While building (2026-11-22): long crate descriptions ran under the panel on the context line (crates got a short tagline); crates held were refunded only as a profile loaded (now also the moment their crate completes, with a notice); an "Opened" arriving with the menu closed pushed the opening onto the closed menu's screens (guarded).
- The crate pictures, looked at up close (2026-11-23): the wooden crate's stencil stood 3.6 cm off the boards and cast a shadow, and its boards showed their grain edge-on as even stripes, like corrugated card (each board now gets its grain along its own length); its rope handles and the case's handle floated off the surface with open tube ends (the ropes now go into the end boards, the handle sits in two gold mounts, and tube ends are closed); the evidence box's split seal sat by the flaps' hinges instead of on their cut edges.
- The economy dashboard takes at most 100 SKUs an experience; 54 skins as SKUs would have used most of them. Skins now log their rarity as the SKU and the skin in a custom field.

**Tested** (Studio play mode, 83tg's avatar, one player; Cash set with `mp.profile`)
| Test | Result |
|---|---|
| Self-checks | `ShopConfig` (the catalogue, odds and rolls over every crate as it fills, a year of storefronts) and `ProfileSchema` (the new fields, old saves) pass on load |
| A new player's odds | 70 / 20 / 7.5 / 2.2 / 0.3%, the plan's example exactly |
| 200,000 rolls in the game's VM | 70.188 / 19.831 / 7.484 / 2.193 / 0.303%; with half a crate owned, every skin within 1.66 standard errors of its odds and no owned skin rolled |
| `BuySkin` the day's M4 BURNT BRONZE with $200,000 | $194,000 (its $6,000); then refused: Owned, NotForSale (a skin not on sale), Unknown, BadData |
| `OpenCrate` GUNSMITH 17 times (its 18th skin already bought) | 17 different skins, none owned before; $194,000 → $151,500 (17 × $2,500); the next two refused, Complete |
| `EquipSkin` | AK-47 STAINLESS on; then refused: WrongGun, NotOwned, Unknown (a skin, then a gun), BadData; the M9 TWO-TONE; the Uzi's skin on and off |
| A spawn | The AK-47 in stainless, the M9 two-tone (frame and magazine midnight, slide stainless), the Uzi in the kit's look |
| Two STREET crates held, 17 of its 18 skins owned, $0 | The open used a crate held (paid 0) and gave the last, AK-47 ARCTIC; the other crate refunded ($2,500, "Refunded"); STREET COMPLETE and a further open refused |
| Cash and rate | Three skins too dear: Cash each time; a fourth request at once: TooFast |
| The AK-47 ARCTIC dropped and picked up | Still arctic: each dressed part's SkinFinish and the `Skin` attribute |
| Equipping mid-match | DESERT ON YOUR UZI. APPLIES ON NEXT SPAWN |
| The policy | The first "State" said in order (no answer yet); the next, once `PolicyService` answered, not |
| The screens | The storefront, a skin, BUY, EQUIP, a crate and its odds, the opening, ODDS with the rounding note (66.667%, 11.111%), YOUR SKINS and the Uzi's skins; in order (NEXT: M9 PARKERIZED, the ORDER list); hovering and clicking cards |
| After the review: `OpenCrate` with the screen's mode | Shown in order while the server rolled: refused, Changed, and the shop sent again; "yes" for the mode: BadData; the same mode: opened; in order (the Studio hook): M9 PARKERIZED, then GLOCK 18 SNIPER GREY; no mode: opened |
| A purchase and a refund on the dashboard | FAL OD GREEN for $1,500 and one Cash sink; a STREET crate held gave AK-47 ARCTIC (paid 0) and the other was refunded with a Cash source |
| The catalogue's load | 33 ms in the server's VM, the year's check included (Studio); about 0.9 s before |
| The crate pictures | On the cards and the crate screens; all six drawn in the game; a new session's storefront loads them with no errors |
| ODDS with four GUNSMITH commons owned | COMMON  ODDS FOR EACH SKIN BELOW: 16.667% over the three left, then OWNED: NOT IN THE ODDS and the four |
| In order, after the fix | OPEN: THE NEXT SKIN IN ITS ORDER: UZI OD GREEN; after the opening, OPEN ANOTHER: ... M500 PARKERIZED |
| The opening during the shake | The crate as it was: 4 OF 18 SKINS OWNED, NEXT: UZI OD GREEN |
| Clicking the CARTEL card, the mouse moved away, BACK | The highlight back on CARTEL CRATE |
| A crate opened with the menu closed | OUT OF THE CRATE: GLOCK 18 COPPER under the list when the shop was next shown (fix 5, before the second pass) |
| After the second pass: a STREET crate held opened with the menu closed (its last skin, so a refund too), then M | On the main menu at once: OUT OF THE CRATE: AK-47 ARCTIC; 3 s later $2,500 BACK FOR CRATES OF A CRATE YOU COMPLETED; then nothing |
| The longest odds list (22 rows) in Studio's 1325 × 753 window | The panel at 0.88 of its size, its backing 9 px clear of the prompts (it would have run 60 px over them); the odds right (COMMON 19.194% each, 57.582%) |
| The turning gun across a redraw | No jump between frames |
| Output log | Clean apart from the DataStore line, and Roblox's "asset content representation is being generated" while it processed the new crate pictures on their first showing (gone in the next session) |

**Not done**
- Two players: another player seeing a skinned gun, dropped and picked up, and the shop's state staying each player's own. In the two-client test with the rest.
- The new profile fields saved to the real DataStore (Studio's API access is off, so profiles stay in memory).
- Pattern, Signature and Mastery skins, Wear, Matched Pairs and Body Count ([[Gun Skin Ideas]]): they need guns with real UVs, or challenges.
- Nothing hands out crates yet (rewards will), so the held crates and their refunds were tested by setting the profile.
- Metal finishes look flatter in the shop's 3D views than on the guns in the world (a ViewportFrame has no reflections). The first visit to the shop shows the finishes and pictures loading for a moment.
- The rarity colours in the colourblind modes (section 11 isn't built), and the shop on 21:9, 4:3 and a phone.
- Studio's Script Analysis (type warnings) wasn't run, as before.
- Nothing is committed: these notes, `skin_lib.py`, `ui_lib.py` and the new images and ids are in the working copy only.

## 2026-11-22: A Last Stand counts only the adrenaline a running skill hasn't claimed
On this PC (Studio signed in as 83tg), with Claude Code driving Studio. JordanSaa settled the question the Phase E review left (the entry below): the part of the meter a running skill has yet to spend no longer opens a Last Stand ("free ones only").
- 4 scripts changed (`AdrenalineService`, `SkillService`, `LastStandService`, and `LastStandRules`' comment). No remote or clip changed.
- **What players will notice:** a skill fired with every full segment leaves no Last Stand while it runs, unless the player earns a full segment more; one fired with segments to spare leaves those for a Last Stand. Before, the segments a skill had yet to spend paid for a Last Stand as well.
- **How:** a timed skill spends its cost over its time, so the meter still holds what it hasn't spent. `SkillService` now tells `AdrenalineService` how much that is as the skill runs (`claim`: its cost at the start, less what it has spent at each step, nothing once it ends or its character goes), and `LastStandService` counts the meter less it (`free`). A stand that does open still takes the whole meter and settles the running skill, as the review's fix 3 made it. A death without a stand keeps the full segments of the whole meter, as before.

**Tested** (Studio play mode, 83tg's avatar, one player; a level-1 profile, so Hot Lead fires at level 1 and claims a third)
| Test | Result |
|---|---|
| No skill running, a meter of 0.4, a killing blow | A Last Stand (free 0.4) |
| Hot Lead fired at 0.5, a killing blow a second later | Meter 0.484, free 0.167: dead at once, no Last Stand; the next life began with 0.333, the one full segment the death kept |
| Hot Lead fired at 0.9, a killing blow a second later | Meter 0.883, free 0.567: a Last Stand. Survived (the gunman killed): the meter emptied, Hot Lead ran on, nothing left claimed (the meter put at 0.5: free 0.5) |
| Output log | Clean apart from the DataStore line |

**Not done**
- The HUD doesn't show which segments a running skill has claimed: they look full until spent.
- Two players: a real Last Stand refused while a skill claims the meter (the gunman's blow stood in). In the two-client test with the rest of Phase E.
- Nothing is committed: these notes.

## 2026-11-21: Phase E of the menu plan: adrenaline segments, seven skills, eleven items and the status effects behind them
On this PC (Studio signed in as 83tg), with Claude Code driving Studio. JordanSaa asked for Phase E (steps 11 and 12 of [[Menus, Loadout, Progression and Shop - To Do#Suggested build order]]), every step "of high quality"; nothing past it was built.
- 7 scripts added (`AdrenalineRules`, `SkillConfig`, `ItemConfig`, `StatusEffects`, `AdrenalineService`, `SkillService`, `SkillController`) and 22 changed in the Team Create place, `LoadoutScreen` rewritten (the Phase D one kept in `ServerStorage.PhaseDBackups`); 3 remotes added (`SkillRequest`, `SkillEvent`, `BuySkill`) and `BulletTimeRequest` removed. No clip changed.
- **What players will notice:** the adrenaline bar is three segments, and bullet time's key (X) now fires the loadout's skill: Bullet Time unless another of the seven is picked, at as many levels as there are full segments, as far as the player's level allows. Its name and level sit under the HUD's figure; as it fires, a banner with a bar, a line of narration and a white flash, and a line in everyone's kill feed. A death keeps the full segments. Loadouts also carry a Head, a Chest and a Gear item: armour that cuts damage from in front (less from behind), more painkillers or spare magazines, quicker healing, reloads and draws, a counter to Bullet Time, a Last Stand without adrenaline. Items and skills unlock by level, some cost Cash, the presets carry theirs, and the level-up moment lists what the new levels opened. Armour weighs, so a loadout can be Heavy now.

**Decided with JordanSaa** (asked and answered 2026-11-21; all in the plan's section 0, Phase E questions)
- **Skill levels do more for their user alone** (the game has no teams yet): Bullet Time 2.5 / 4 / 6 s (it was 5 s for a full meter); Hot Lead armour-piercing for 20 s; Second Wind heals every limb by half its maximum / to full / to full and gives a painkiller back; Gut Feeling marks every other player through walls for 6 / 10 / 15 s; Heavy Hand +50% damage for 6 s / +100% for 6 s / +100% for 10 s; Bulletproof damage taken −40% / −55% / −70% for 10 s, no sprinting; Open Tab no ammo used for 10 / 20 s. Hot Lead's levels 2 and 3 (a heavy machine gun, a .50 pistol, a grenade launcher) and Open Tab's level 3 (fire rounds) need things the game doesn't have, so those skills stop at 1 and 2 for now. Unlocks and prices are the plan's table: Bullet Time (levels 1, 6, 12), Hot Lead (1, 3, 5) and Second Wind (1, 4, 7) free; Gut Feeling (2, 5, 8) $500; Heavy Hand (4, 10, 16) and Bulletproof (6, 11, 17) $1,000; Open Tab (30, 38, 43) $3,000.
- **The Pacemaker is a Last Stand without adrenaline** (every Last Stand here already slows everyone near, which was Max Payne 3's Pacemaker).
- **The Pill Case gives 5 painkillers a life**; everyone else keeps 3.
- **Items as proposed:** Light Vest (Chest, 1: torso −15% from in front) and Ammo Pouch (Gear, 1: two spare magazines a gun, no ammo used in a Last Stand) free from level 1; Stitches (healing starts 25% sooner) free from 3; Riot Helmet (Head, 1: head −50%) 4, $1,000; Bandages (healing 50% faster) 6, $700; Pill Case 10, $1,500; Quick Draw (reloads and draws in 75% of the time) 18, $3,000; Plate Carrier (Chest, 2: −25% in front, −10% behind) 20, $3,500; Stopwatch (others' Bullet Time doesn't slow you or your aim) 26, $3,000; Pacemaker 30, $3,000; Heavy Plates (Chest, 4: −33% in front, −25% behind) 36, $4,000. Other gear weighs nothing. Presets: RIFLEMAN the Light Vest and Hot Lead, SCOUT Bullet Time only (Gut Feeling opens at level 2), BREACHER the Ammo Pouch and Second Wind, MARKSMAN Stitches and Hot Lead. Throwables stay greyed. Every loadout has a skill, Bullet Time by default.
- My calls, not asked: the skill key is bullet time's (X, the middle mouse button, gamepad Select; Q is the shoulder swap); Hot Lead pierces armour items but not Bulletproof; the Stopwatch counters the Bullet Time skill, not a Last Stand's slow motion; no skill in the defenseless wakeup after a Last Stand; Second Wind is refused when nothing is hurt and no painkiller would come back; a death mid-skill keeps the full segments of what it hadn't spent; the narration lines are our own.

**New: adrenaline in three segments** (`AdrenalineRules`, shared; `AdrenalineService`, server; `Hud`)
- Still the `Adrenaline` attribute, 0 to 1, now read as three segments of a third. The gains are as before (0.004 a point of damage, 0.25 a kill), but the damage is now the health a hit really took, after armour and boosts (the review's fix 1), and every gain and spend goes through `AdrenalineService`.
- **A death keeps the full segments** for the next life (Max Payne 3's rule) and loses the one filling; from the start of a Last Stand it keeps nothing, since the stand takes the whole meter (a survived one still empties it). Leaving to the menu keeps nothing.
- A Last Stand needs one full segment, as before, or the Pacemaker.
- The HUD draws three blocks beside the figure: a full segment white, the one filling grey (a death loses it).

**New: status effects** (`StatusEffects`, server)
- One place every system asks what a character's items and running skill do. A loadout's items are one source for the whole life, a running skill another that ends with its time; multipliers multiply, on-off effects combine, spare magazines take the most, painkillers add. A Bulletproof user's `NoSprint` is copied to an attribute for the client.
- **Damage** (`damageScale`): the attacker's boost (Heavy Hand) × the victim's damage taken (Bulletproof) × their armour: the helmet on the head, chest armour on the torso by the side the shot came in (the way it travelled through the torso part it hit; a shot from the side counts as the front). Hot Lead ignores armour items, not Bulletproof. Players' shots and the test arena's gunman both go through it.

**New: the skills** (`SkillConfig`, shared; `SkillService`, server; `SkillController`, client)
- `SkillConfig` holds the seven skills, each level's numbers, unlocks, prices and narration line; the screens' words are worked out from the numbers (`describe`), and a level the game can't do yet reads NOT IN THE GAME YET and is never offered. Its self-check uses made-up skills, so tuning never stops the game.
- **The key sends `SkillRequest` with nothing in it.** The server checks the user is alive and able (not in a Last Stand or the wakeup after one), that nothing of theirs is running, that the skill is still theirs and open at their level (from the profile, every time) and how many full segments there are; it fires at the most both allow and spends that many, a timed skill over its time and an instant one at once. Requests closer than 0.25 s are dropped. The owner hears "Used" (the skill, level and time) or why not on `SkillEvent`; everyone's kill feed gets NAME  USED HEAVY HAND  LV 2.
- **Bullet Time is now this skill** (`BulletTimeService.activate`, with the level's time); the meter and the key moved out of `BulletTimeService`. Its Studio hook (`DebugBulletTime`) is answered by `SkillService` and spends the meter.
- Second Wind heals through `LimbService` (and gives back painkillers, never past the life's start); Hot Lead, Heavy Hand, Bulletproof and Open Tab are a status effect for their time; Gut Feeling is drawn by its user's client, which marks every other character (players and the arena's dummies) with a small red diamond over the head, seen through walls.
- **On the HUD** (`Hud`, `SkillController`, `KillFeed`, `Keybinds`): the keybind list names the skill on X; a line under the stamina bar shows it with the level it would fire at now (white when it can fire); as it fires, a half-second white wash, the banner at the top (its name and level, a bar running out with its time, its line for 3 s); a refusal flashes why under the reticle (NOT ENOUGH ADRENALINE, SKILL ALREADY RUNNING, NOTHING TO HEAL…), and with no full segment or a skill running the client says so without asking the server.

**New: the items** (`ItemConfig`, shared; `StatusEffects`, `LimbService`, `LoadoutService`, `LastStandService`, `BulletTimeService`, `StanceService`, `WeaponServer`)
- `ItemConfig` holds the eleven items (slot, weight, unlock, price, effects) and words for each worked out from its numbers. Items go on at spawn (`ItemHead`, `ItemChest`, `ItemGear`) and stay for the whole life.
- Where each one acts: armour in `damageScale`; the Ammo Pouch's magazines in `LoadoutService` at spawn and its free Last Stand shots in `WeaponServer`; Stitches and Bandages in `LimbService`'s regeneration; the Pill Case in `LimbService`'s painkillers; Quick Draw in `LoadoutService`'s reload and switch times; the Stopwatch in `BulletTimeService`; the Pacemaker in `LastStandRules.eligible`.
- **Their weight counts** (`ItemConfig.carried`): the heaviest loadout is 23 and Heavy (18) is reachable, for example the AK-47, M9 and Uzi with the Riot Helmet and Heavy Plates.

**Loadouts, purchases and the profile** (`LoadoutRules`, shared; `ProfileSchema`, `ArmoryService`, `CharacterServer`)
- A saved loadout also holds `Head`, `Chest`, `Gear` and `Skill` (old saves get none and Bullet Time), and `Unlocks` gained `Items` and `Skills` beside `Guns`. Gun, item, skill and preset ids share one length (40) and must never clash (checked).
- `SetLoadout` checks a whole loadout (`checkLoadout`: only the seven fields, each a thing of the right kind for its slot that the player may use, at least one gun); every spawn checks it again (`resolveKit`): an item no longer allowed is left off, a skill becomes Bullet Time.
- `BuyItem` now buys items as well as guns, and `BuySkill` skills, on the same checks (level reached, has a price, not owned, the Cash), checked again inside the one profile update that takes the Cash and gives the thing; both share the purchase rate (2 at once, then one each 0.5 s), print a line and log a Cash sink.
- A spawn sets up, in order: the kit, the stance, the items, the limbs (painkillers), the adrenaline, the guns (magazines), the skill.

**The screens** (`LoadoutScreen` rewritten; `MatchEndScreen`)
- A saved loadout's screen has HEAD, CHEST, GEAR and SKILL rows under the guns (the throwable still greyed, NOT IN THE GAME YET). Each item slot has a list, NONE first, and SKILL a list of the seven, in the order they unlock. A row shows IN USE, or its weight (a skill: the highest level the player's level allows, LV 2), or the level it opens at or its price; a locked row is grey but can be highlighted; one with a price opens BUY.
- The panel shows an item's description, what it does and its weight, with the loadout's weight with it; a skill's three levels (LV 2  LEVEL 6, then OPEN, BUY TO USE or NOT IN THE GAME YET; white only once the player can fire it) and its price; a loadout's items and skill, and anything the player can't carry in red with what spawns instead (SPAWNS WITHOUT IT, SPAWNS WITH BULLET TIME). RESET puts back the M9, Uzi, AK-47 and Bullet Time, with no items.
- The level-up moment has an UNLOCKED row: the first four of the guns, items, skill levels and loadout slots the new levels opened, then +N MORE (`LoadoutRules.unlocksBetween`).

**The review** (the `roblox-dev:roblox-reviewer` agent over 30 scripts: every new and changed one but `ClientMain`, whose one new line starts `SkillController`, plus `ProfileService` and `WeaponConfig` for context)
- No client can give itself Cash, a gun, an item or a skill, pay less, buy twice or leave a purchase half done: `BuyItem`, `BuySkill`, `SetLoadout` and `SkillRequest` check everything they're sent, a purchase is checked again inside the one profile update that takes the Cash, and every spawn and every skill read the profile again. Profiles, saves and leaks were sound.
- It found eight problems (two high, one medium, five low) and three design questions. All eight are fixed below and the fixes tested. Two of them couldn't happen in the place as it is (5 and 8), and one only once the arena is published (2).

**Fixed**
1. **The meter filled from damage that never landed** (high). Adrenaline counted every point of damage a shot asked for. Shooting a body lying in a Last Stand, which takes no damage, filled a meter in a few seconds; a limb already at nothing (a limb in the red doesn't heal) could be shot for ever; an overkill counted in full (an M107 headshot, 0.76 of the meter whatever the head had left). `LimbService.damage` now returns the health it really took (nothing when it ignores a hit, never more than the limb had), and `WeaponServer` counts that, or the health a humanoid without limbs really lost.
2. **The test arena would give guns away on a live server** (high if it is published, and it is the game's only map): its gun table holds every gun, the M107 and M4 included, free to anyone at any level, and its dummies, back every 5 s, fill meters. Its script now runs in Studio only, so a live server gets the map alone (`LIVE` at the top of `TestArena` turns it back on).
3. **A running skill was paid for twice after a Last Stand** (medium). A survived stand empties the meter, the skill's unspent part with it, and the skill then went on charging its schedule out of adrenaline earned afterwards: Bulletproof at three segments, downed half a second in and up at 3 s, cost about 1.7 of the meter instead of 1. A Last Stand now settles a running skill: it runs on to its time and charges nothing more.
4. **One field the player had lost blocked every edit of a saved loadout** (low). The screen sent the stored loadout with the change, and the server, checking every field, refused it whole (NOT OPEN AT YOUR LEVEL YET) if anything in it was no longer the player's: a level lost to a prestige, a retuned unlock, an item taken out of the game. The equip after a purchase failed the same way. The screen now sends the change on top of what the loadout spawns with (anything lost already swapped or left off, as the panel shows in red), and the server is as strict as before. The panels weigh a change the same way, so the preview matches the save (CUSTOM 2 at level 1 read 18 → 13 for the M500; it is 13 → 8).
5. **Items could be skipped at a spawn** (low, and it didn't happen here: every spawn had its items). `StatusEffects.setup` made nothing for a character not yet in the workspace, and CharacterAdded can come before it is (with immediate signals). Such a character is now set up all the same.
6. **Bullet Time could look busy just after it ended** (low). The skill and the slow-down ended on separate 0.1 s timers, so a press between the two was refused, SKILL ALREADY RUNNING (nothing charged). The skill now ends its Bullet Time itself (`BulletTimeService.deactivate`).
7. **Every effect query made a list** (low): about 40 small tables a shotgun blast, and one a frame for each sprinting character. The queries now walk the sources in place.
8. **The skill key while dead** (low; a guess, and it can't happen here). Without the menu's code the reviewer couldn't tell whether the skill key swallowed gamepad Select, the death screen's button. It doesn't: the menu binds Select above every game key. The skill key now lets every key through while its user is dead all the same.

**Design questions from the review** (left as they are)
- The part of the meter a running skill hasn't spent yet still opened a Last Stand, and the stand then took it while the skill ran on (fix 3). Should only the segments a running skill hasn't claimed count? Decided and built 2026-11-22: yes (the entry above).
- Heavy Hand's boosted damage refilled the meter that paid for it. Since fix 1 a hit counts only the health it took, so a boost speeds a kill but makes no more meter than the victim had.
- Nothing resets the meter at a new match (matches don't respawn anyone), so the living keep theirs and the dead the segments their death kept. Left as it is.

**Found and fixed in the checks** (not from the review)
- Setting up a character's skill again while one ran (only test scripts do) left the running skill's attributes behind and its cost unspent; `SkillService.setup` now ends it first.
- A skill's level the player hadn't reached, or hadn't bought, had its words in white like one they could fire; they're grey now, like its name.
- The player's own Bullet Time said BULLET TIME twice (its banner, and the slowed-time label over it). The label now stays hidden while the banner is their own Bullet Time, and sits under the banner during any other skill.

**Tested** (Studio play mode, 83tg's avatar, one player)
| Test | Result |
|---|---|
| Self-checks | `AdrenalineRules`, `SkillConfig`, `ItemConfig`, `LoadoutRules` (ids unique, presets free at their levels, items and skills bought and resolved, the unlock list), `VitalsRules` (the regeneration changes), `LastStandRules` and `ProfileSchema` (the new fields, old saves) pass on load |
| A new player's spawn | Bullet Time, no items, M9, Uzi, AK-47: 13, Medium; 3 painkillers; one spare magazine each (15 + 15, 32 + 32, 30 + 30) |
| The screens: LOADOUT, RIFLEMAN, a saved loadout's edit screen, a skill's panel | Items NONE, BULLET TIME LV 1, the throwable greyed, 13 Medium; RIFLEMAN with the Light Vest and Hot Lead, 14; the HEAD, CHEST, GEAR and SKILL rows; the three levels of a skill |
| Level 20, $10,000: Gut Feeling bought through the screens, then the Riot Helmet, then the free Ammo Pouch picked | $9,500 after the skill, which went straight into the slot; the helmet's panel read $1,000 TO BUY, 50% LESS DAMAGE TO THE HEAD, 13 → 14; the Gear list: NONE in use, the free gear with its weight, the gear for sale with its price, the Stopwatch and Pacemaker grey with their levels; CUSTOM 1 with the Riot Helmet, Ammo Pouch and Gut Feeling, 15 |
| Spawning with it | Gut Feeling, the Riot Helmet and the Ammo Pouch: 15, Medium; two spare magazines each (15 + 30, 32 + 64, 30 + 60). X reads GUT FEELING in the keybind list; with half a meter, GUT FEELING LV 1 under the figure, one segment white and the next grey |
| Gut Feeling with a full meter | Level 3: the banner, its line, the meter running out, USED GUT FEELING LV 3 in the kill feed. A red marker over each of the arena's four characters, always on top, at their heads' places on screen (Studio's screenshots don't draw billboards, so checked by their properties and screen positions) |
| 26 requests straight to `BuySkill` and `BuyItem`, 0.6 s apart, at levels 1 and 50 | 14 refused, each with the right reason (Locked, Cash, BadData, Unknown, Free, Owned); 4 skills and 8 items bought: $30,000 → $4,800, exactly their prices |
| 7 bad loadouts sent to `SetLoadout` | An item or skill in the wrong slot (WrongSlot, 3), a throwable field (BadData), no gun (Empty), an unknown skill (Unknown), a number for an item (BadData); the good one saved |
| CUSTOM 2 (AK-47, M9, Uzi, Riot Helmet, Heavy Plates, Pill Case, Heavy Hand) at level 50 | 5 painkillers; 18, **Heavy**, the first loadout that reaches it; one spare magazine each |
| Heavy Hand with two segments and a tenth | Level 2 for 6 s; the meter fell evenly from 0.77 to 0.10 over the 6 s (two segments exactly) and the skill ended |
| The M9 (22 a hit) from 12 studs in front of a dummy with the Riot Helmet and Plate Carrier | Torso 16.50 (×0.75), a headshot 22 (44 × 0.5); under Heavy Hand level 1, torso 24.75 and a bare arm 33 |
| Hot Lead | Level 1 for 20 s: the torso took 22 and the head 44 through the same armour |
| From behind | 19.80 on the upper and the lower back (×0.9) |
| The armour sums in the game's VM (20 checks) | All pass: no armour, each armour item, front, back, a sideways shot, Hot Lead through items but not Bulletproof, Bulletproof with plates (×0.45), Heavy Hand after the cuts, a timed effect running out, `NoSprint` set and cleared |
| The gunman (18 a hit) against Heavy Plates from in front | 12.06 a hit (×0.67), 7 hits |
| Bulletproof at three segments | Level 3 for 10 s: 3.618 a hit (18 × 0.67 × 0.3); a sprint refused (NoSprint) during it; `NoSprint` gone after it |
| Healing after a 30 hit to a leg (70 → 40), Heavy | No gear: began 5.1 s after the hit (Heavy's 5 s), 2 a second (3% of 70), 48.2 at 9 s; Stitches: began 3.9 s after (3.75 and a 0.25 s tick), 50.7; Bandages: began 5.0 s after, 3.1 a second (×1.5), 53.1 |
| Quick Draw | The M9's reload 1.200 s (1.6 without) and the AK-47's draw 0.412 s (0.55 without); the reload still moved the rounds |
| Deaths: meter 0.9, no painkiller (so no Last Stand) | The next life began with 0.667: two segments kept |
| Meter 0.9, a Last Stand, not survived | The next life began with nothing |
| No adrenaline: without the Pacemaker; with it | Dead at once; a Last Stand all the same, and nothing kept |
| The Ammo Pouch in a Last Stand | 4 shots at the gunman, the M9 still 15 |
| Open Tab at full | Level 2 for 20 s: three shots used no rounds (a shot before it used one) |
| Second Wind at one segment | Leg 33.8 → 69.9, an arm in the red 10 → 40.5, torso 69.6 → 100 (half of each maximum, and regeneration); the meter 0.38 → 0.05 at once |
| Second Wind at three | Leg 30 → 70, torso 40 → 100, painkillers 3 → 4, the meter emptied; asked again with no segment: NoAdrenaline |
| Second Wind with nothing hurt (one segment, a painkiller short) | Refused (Unhurt), nothing spent |
| A dummy's Bullet Time at full (the hook), without and with the Stopwatch | Level 3 for 6 s, its meter emptied by the end; without: my time 0.3 and aim penalty 0.35; with: neither |
| My Bullet Time at one segment, then two | 2.5 s, me at 0.6, one segment spent; 4 s, the dummy in view at 0.3, two spent |
| The level-up moment (a made-up match end, level 3 → 12) | LEVEL 12 - GUNHAND, then UNLOCKED: RIOT HELMET, HEAVY HAND LV 1, SECOND WIND LV 2, GLOCK 18, +13 MORE (17 in all) |
| CUSTOM 2 at level 1 | Its three items in red, SPAWNS WITHOUT IT, and Heavy Hand SPAWNS WITH BULLET TIME; 13, Medium; APPLIES ON NEXT SPAWN. The next life: Bullet Time, no items, 3 painkillers |
| X at level 1 with a full meter | Bullet Time level 1, two segments left; the banner, its bar and line, no second BULLET TIME label; NOBODY [JORDAN] USED BULLET TIME LV 1 in the kill feed |
| After the review: self-checks | All pass on load, the new one with them (a saved loadout taken as it spawns can always be saved again) |
| The M9 at a dummy's leg already at nothing (the hit confirmed), then a whole leg, then an arm with 10 left | The meter +0, +0.088 (22 × 0.004), +0.040 (10 × 0.004); each would have been +0.088 before |
| Hot Lead at half a meter; 2 s in, a killing blow (meter 0.47, 3 painkillers); the gunman killed during the stand | The stand survived, the meter emptied, Hot Lead still running; the meter then put at 0.5 stayed at 0.5 for 4 s while Hot Lead ran on (before the fix it would have gone on falling) |
| Bullet Time at one segment; again, with the skill set up afresh half a second in | The skill and the slow-down ended in the same frame (2.583 s); the fresh setup ended the slow-down at once (time scale 1) |
| Effects on a model set up before it is in the workspace, then put in it, then destroyed (15 checks in the game's VM) | All pass: its armour and painkillers count, it outlasts the sweeps once in, timed effects and `NoSprint` come and go, the queries agree, its record goes with it |
| RIFLEMAN spawned | The Light Vest, Hot Lead, 14 |
| CUSTOM 2 at level 1 (its Riot Helmet, Heavy Plates, Pill Case and Heavy Hand no longer open), its Primary set to the M500 through the screens | The panel read 13 → 8, MEDIUM → LIGHT; saved as M500, M9, Uzi, no items, Bullet Time: 8, Light. The old screen's request (the stored loadout with the M500) refused, Locked; the guns alone saved |
| Gamepad Select alive, the meter empty | NOT ENOUGH ADRENALINE: Select reaches the skill key |
| Dead, X, then gamepad Select | LOADOUT over the kill cam on Select; no error |
| Output log | Clean apart from the DataStore line, the purchase lines and the test tools' own |

**Not done**
- Two players: skills, armour and the Stopwatch between real players, Gut Feeling's markers on a real player, the kill feed's skill lines, Bullet Time slowing another player under lag, and fix 1's Last Stand case (shooting a body in a stand gives no meter; the limb at nothing and the overkill were tested). Added to the two-client test ([[Animation and MP3 Systems - Progress and To Do#3. Play tests]]).
- Fix 2 wasn't seen on a live server (Studio, a 2-player Studio test included, always runs the arena). Fix 5's new path was tried on a made-up model only: this place's spawns already set characters up in the workspace.
- How the markers look: Studio's screenshots don't draw billboards.
- Skills were fired with X and straight through `SkillRequest`, never with gamepad Select (it reached the skill key, with an empty meter) or the middle mouse button (not tried). There are no touch controls.
- The screens were checked only in Studio's window (1325 × 753), not at 1920 × 1080 or 1024 × 768 as in Phase D.
- Skill and item icons (Blender art); the throwable slot (grenades); the skills and items that need team modes, a minimap, looting, explosions, sounds, respawn hooks or attachments (plan step 19); sounds; balance from real play.
- Saving the new profile fields against the real DataStore (Studio's API access is still off).
- Studio's Script Analysis (type warnings) wasn't run over the new and changed scripts.
- The place isn't published (Team Create keeps the changes). Nothing is committed: these notes.

## 2026-11-20: Phase D of the menu plan: stamina, health regeneration, weight classes, the loadout screen and gun unlocks
On this PC (Studio signed in as 83tg), with Claude Code driving Studio, started 2026-11-19 by the session that wrote up Phase C. JordanSaa asked for Phase D (steps 9 and 10 of [[Menus, Loadout, Progression and Shop - To Do#Suggested build order]]), "of high quality"; nothing past it was built.
- 3 scripts added (`VitalsRules`, `ArmoryService`, `LoadoutScreen`) and 18 changed in the Team Create place; 5 remotes added (`SelectLoadout`, `SetLoadout`, `RenameLoadout`, `BuyItem`, `LoadoutEvent`). No clip changed.
- **What players will notice:** they spawn with the loadout they pick in the main menu (LOADOUT): one of four presets or five loadouts of their own, the last two from levels 10 and 25. Guns unlock by level and some cost Cash. Sprinting runs out of breath. A wound out of the red heals by itself a few seconds after the last hit; one in the red still needs a painkiller. How heavy the guns carried are (LIGHT, MEDIUM or HEAVY LOADOUT, under the HUD's figure) sets how fast both happen and how quickly aiming zooms in, and dropping or picking up a gun changes it. Dying offers CHANGE LOADOUT [M], and the respawn waits while the list is open.

**Decided with JordanSaa** (asked 2026-11-19 through the session that started this one, answered 2026-11-19 and 20; all in the plan's section 0)
- Gun unlock levels and prices, as proposed: M9, Uzi, AK-47, S&W 500 and M500 free from level 1, the FAL free from 3, then the Glock 18 (level 5, $500), MP5 (8, $1,000), Desert Eagle (12, $1,500), sawn-off (16, $2,000), SPAS-15 (22, $2,500), M107 (28, $3,500) and M4 (34, $3,000). Every gun a preset carries is free.
- Health regeneration **only above the red** (not my proposal, which healed red limbs too): after the class's delay (Light 3 s, Medium 4 s, Heavy 5 s) a limb heals 5% / 4% / 3% of its maximum a second up to full; a limb in the red stays injured until a painkiller lifts it out.
- Stamina: Medium sprints 6 s from full (Light 7.8, Heavy 4.2); it fills in 4 s from 1 s after the sprint; once dry, a sprint can start again at a quarter.
- **The class follows the guns carried right now** (not my proposal, which fixed it at spawn): picked up, dropped or lost, the weight and class change at once; the stamina keeps the share left; regeneration and aiming use the class of the moment; the HUD names it.
- The plan's class thresholds stay (Light up to 10, Medium 11 to 17, Heavy from 18). Guns alone reach 17 at most (the M107 and two Desert Eagles), so Heavy arrives with Phase E's items.
- The death screen offers CHANGE LOADOUT and the respawn waits while the list is open, up to 15 s after the death; on a gamepad, **Select** (bullet time's button, useless while dead).
- The body-in-a-ring diagram and the posed character wait for Blender art; the throwable, Head, Chest, Gear and Skill slots show greyed until Phase E; presets carry only their guns until then.
- My calls, not objected to: new players' CUSTOM 1 to 5 hold the old default spawn (M9, Uzi, AK-47) and CUSTOM 1 is selected; a loadout needs at least one gun; copying a preset keeps the saved loadout's name; names are up to 20 characters.

**New: gun weight and ratings, worked out from the stats** (`WeaponMath`, `WeaponConfig`, shared)
- `WeaponMath.ratings` (the loadout screen's five bars), `dps`, `power` and `weight`: the plan's formulas exactly; with today's numbers every gun weighs what the plan's table says (sawn-off 1, M9, S&W 500, Uzi and Glock 2, Desert Eagle 3, M500 4, SPAS-15 5, MP5 6, FAL 8, AK-47 and M4 9, M107 11). A gun the formula gets wrong can take a `WeightOverride` in `WeaponConfig` (none does).
- `WeaponConfig` also holds each gun's description line and its unlock (`Unlocks`: level and price), and checks both.

**New: saved loadouts, unlocks and the armory** (`LoadoutRules`, shared; `ArmoryService`, `ProfileSchema`, server)
- The profile has three new fields: `Loadouts` (five, each a name and a gun per slot), `SelectedLoadout` (1 to 5, or a preset's id) and `Unlocks.Guns` (the guns bought). Old saves get the defaults; gun and preset ids aren't checked against the game when a profile loads, so a gun taken out of the game can't stop anyone loading.
- `LoadoutRules` holds the rules the screen and the server share: the slots that open at levels 10 and 25, the four presets (RIFLEMAN, SCOUT, BREACHER, MARKSMAN from level 3, their guns only for now), which guns a player may carry (level reached, bought if it has a price) and buy, a loadout checked whole as a client sends it (`checkGuns`: only the three slots, each a gun that fits it and is allowed, at least one) and again at every spawn (`resolve`: a gun no longer allowed is swapped for the default loadout's gun in that slot), weight and class, and names (tidied: no control or hidden characters, single spaces, 20 characters).
- `ArmoryService` answers four requests, each checked against the player's own profile and rate-limited (a short burst, then TOO FAST; fix 5 below): `SelectLoadout`, `SetLoadout` (also copying a preset and resetting), `RenameLoadout` (filtered with `TextService` for its owner, the only one who sees it; the old name stays if filtering fails) and `BuyItem` (a gun with a price at its level, not owned, with the Cash: the Cash taken and the gun given in one profile update, checked again inside it). It sends the owner their armory (`LoadoutEvent`) whenever it changes.
- **Every spawn takes the selected loadout** (`ArmoryService.spawnLoadout`, called by `CharacterServer`), checked again whole; the first one-handed gun spawns in hand. Players used to spawn with the M9, Uzi and AK-47 whatever happened.

**New: the loadout screens** (`LoadoutScreen`; `MenuKit`, `MenuController` changed)
- LOADOUT in the main menu: the four presets, a gap, then the five saved loadouts (the locked ones grey, with LEVEL 10 / LEVEL 25); a preset can be selected or copied into a saved loadout; a saved loadout can be selected, its three slots changed, renamed (a text box that stops at 20 characters) and reset (after a confirm).
- A slot's list holds EMPTY and every gun that fits it, in the order they unlock, with its weight, level or price. A locked gun is grey but can be highlighted, so its stats can be read; choosing a gun with a price opens BUY.
- A panel on the right, on a dark plate (Max Payne 3's loadout panel), shows the highlighted row: a loadout's three guns (one it may no longer carry in red, SPAWNS WITH THE M9), the five slots still to come in grey, and its weight bar (Light and Heavy marked) with its class and what the class does; or a gun's 3D view (the HUD's icon model, one at a time), its description, its five ratings as bars against the gun in that slot now (the gain white with +, the loss red with −), its numbers (fire mode, fire rate, magazine, reload, draw, headshot, damage a second, hands), its weight, its lock or price, and the loadout's weight and class with it (13 → 15).
- APPLIES ON NEXT SPAWN shows in the panel, and NEXT SPAWN: … on the main menu's LOADOUT row, while the next spawn would bring other guns than this life carries.
- `MenuKit`: rows can be `dim` (grey, still chosen), the page tells the screen what is highlighted, notices can be white (something done) as well as red (a refusal), and the `Screen`, `Entry` and `Nav` types are shared. `MenuController` gives each screen a `Nav` and calls its `shown` and `highlight` hooks.
- Checked on screen at 1920 × 1080, 1024 × 768 (the panel fits beside the list) and Studio's own small window, in the plan's style (Oswald, white, black and grey, hard edges, the white bar).

**New: stamina and health regeneration** (`VitalsRules`, shared; `StanceService`, `LimbService`, `LoadoutService`, `CharacterController`, `CameraController`, `Hud`)
- **Stamina:** the server counts it (`StanceService`), ends a sprint that runs dry (Forced, "Tired") and refuses one before a quarter (Rejected, "Tired"); the client predicts the same count so the stop is instant, takes the server's when it is clearly lower, and Shift must be pressed again after running dry. A slim bar under the HUD's figure shows it while it isn't full (grey once dry).
- **Regeneration** (`LimbService`, every 0.25 s): after the class's quiet spell, limbs out of the red heal to full; never in a Last Stand or dead; bullet time slows it. The test arena's dummies heal too.
- **The weight class** is worked out by `LoadoutService` from the guns carried now (`LoadoutWeight`, `WeightClass`), again whenever one is picked up, dropped or lost; stamina keeps its share; the HUD names the class under the figure (LIGHT LOADOUT…), white for a moment when it changes.
- **Aiming in** is the class's share of the usual time: the camera's zoom and the sniper scope's push, and the server's 0.15 s aim settle (Light ×0.85, Heavy ×1.2). Walk speed and dive distance are the same for every class.

**New: change loadout on the death screen** (`KillCamController`, `MenuController`, `SpawnService`, `MenuRules`, `Keybinds`)
- The kill cam shows CHANGE LOADOUT [M] bottom right (SELECT after a gamepad). It opens the menu straight at LOADOUT over the kill cam and asks the server to hold the respawn (`MenuRequest` "Hold"); closing the menu (M, Select, BACK) releases it ("Release", never throttled: it only brings the player back sooner), and `MenuRules.HOLD_LIMIT` (15 s after the death) ends any hold. The respawn closes the menu.
- On a gamepad Select opens it only while dead (`Keybinds.ChangeLoadout`); alive, Select is still bullet time.

**The review** (the `roblox-dev:roblox-reviewer` agent over 21 scripts: every new and changed one, the armory's remotes first)
- No client can give itself Cash, guns, levels or a locked loadout, or spend Cash it doesn't have: every argument is checked, every request runs against the server's own copy of the profile, a purchase is checked again inside the one profile update that takes the Cash and gives the gun, and only the filtered name is kept. Regeneration, stamina and the class read only what the server set.
- It found ten problems (one high, one medium that depends on a place setting, eight low), all fixed below and tested. It then checked the fixes (2026-11-20): nine right, one still beatable, and a few things the fixes uncovered, fixed on 2026-11-21 (**The second check**, below).

**Fixed**
1. **Walking could stand in for a sprint** (high). The server only drained stamina in its Sprinting stance, and its speed check let every stance move at 1.35 times its speed plus 6 studs a second: a client that set its own walk speed to 26 outran a sprint for ever, could aim and fire while doing it (a sprint can't), and ignored limping. Now (`StanceService.checkSpeed`) each stance is held to its own speed with the legs' state (limping 11, crawling 4, as the client sets it), a sprint's speed only while sprinting (and a second after the server ends one; second check, 1), a vault's while vaulting. A bank of distance fills at 1.1 times that, holds a second of it (of walking at least) plus 4 studs for late position updates and a client a moment ahead of the server, and once overdrawn puts the character back where it last moved legally. A self-check keeps walking short of a sprint. Server code that teleports a character (none in the game yet; test scripts do) must call `StanceService.moved(character)` first, or the move is undone.
2. **Per-character tables could leak** (medium, if old characters weren't destroyed). Here they are: Roblox now destroys a character when the player respawns (tested; the place setting the reviewer named no longer exists in Studio), and the stance table stayed at one record. Backstops anyway: `StanceService` drops a record whose character is gone, `LoadoutService` clears a leaving player's, and the menu lets go of the last character's connections.
3. **Broken text in a name** (low, and not possible here). The reviewer expected Luau's `utf8` to let UTF-16 surrogates through; in Studio it refuses them, anything past U+10FFFF and overlong bytes (`utf8.len` gives nil and `JSONEncode` refuses them), so names and saves already reject them. Names now also drop noncharacters (U+FDD0 to U+FDEF, U+FFFE, U+FFFF), the armory is sent after a spawn rather than during it, so a failure there can't stop the spawn, and sending checks its encoding.
4. **A balance change would have stopped the game** (low): the self-checks pinned the plan's weights, prices and levels, so tuning a gun would have broken every script that needs `LoadoutRules`. The rules are now checked with guns picked from `WeaponConfig`, and the plan's weights only warn ("AR_A_AK47 weighs 10; the menu plan worked out 9"); `VitalsRules` checks read its own numbers.
5. **Requests past the rate were dropped without a word** (low): a reset right after a rename kept the old name, and two saves bunched together by lag lost the second. Each kind of request now has a burst (3 selections or saves, then one each 0.25 s; 2 purchases, then one each 0.5 s; a name of the player's own every 2 s, while putting the default name back counts as a save), and past it the screen says TOO FAST. TRY AGAIN IN A MOMENT.
6. **A refused sprint emptied the predicted stamina** (low): only a forced stop does now. A refusal (the server's count a moment behind) waits just under a quarter, and the sprint starts then if Shift is still held.
7. **Hold shared PLAY and LEAVE's half-second gap** (low), so M, M, M on the death screen could lose the hold. It isn't throttled now: it holds only until 15 s after the death, and only the sender.
8. **Limits that had to agree weren't tied together** (low): gun and preset ids now share one length (`LoadoutRules.ID_LENGTH`, 40, checked against every id), and a profile whose saved loadouts don't fit (a longer name, a bad slot, more loadouts than this version has) is mended when it loads instead of refused, so changing the number of loadouts or the name length needs no profile version.
9. **Purchases left no record** (low): each now prints a line (the player's id, the gun, the price, the Cash left) and logs a Cash sink to Roblox's economy dashboard (`AnalyticsService`).
10. **Every attribute change redrew the HUD's figure** (low; the server sets `Aim` up to 30 times a second): the figure, and the server's and the menu's hit tracking, now react only to what they show (limb health, painkillers, adrenaline, the class).
- Not in its files, and left as a question: Roblox's Reset Character is on, so a player can die on purpose and change loadout on the death screen (in the plan's section 9).

**The second check** (the reviewer over the fixes' diff, 2026-11-20; fixed and tested 2026-11-21)
1. **Sprint speed could still be had for free** (high): the second after any sprint allowed a sprint's speed, so a client asking to sprint and to stop in the same frame, every 0.9 s, never spent stamina and could run at 24 for ever. The grace now follows only a sprint the server ended itself (Tired, a hit); a stop the client asks for needs none, since it slowed as it asked.
2. **A new character could teleport anywhere** (high; older than Phase D): the speed check trusted every position for 2 s after a spawn. It now starts at the spawn point, so a jump right after spawning is held to the usual allowance.
3. **Bullet time could pull back a player on a slow connection** (medium): when the scale fell, the allowance fell at once, while the player runs on at full speed until they hear. The old scale now counts for a second after it falls.
4. **Two walk speeds** (low): the check now reads the client's (`LimbRules.WALK_SPEED`), and a self-check warns if `StanceRules`' copy differs; the walking-below-a-sprint check warns rather than stops, as finding 4 asks.
5. **Aiming's slower walk and a landed dive weren't held by the server** (low): aiming now limits walking to 70% on the server too (the client already slowed), and lying after a dive allows the dive's speed only for the second of its slide, not up to 8 s.
6. **A rename could win over a reset** (low): RESET just after renaming, while the name was still being filtered, kept the filtered name. The latest rename of a loadout now wins, and putting the default name back is never refused as Busy.
7. **Odd keys in a stored loadout list** (low, theoretical): `reconcile` turns them back into a list rather than leaving a profile that can't be saved.
- Small: going back to a screen where nothing was chosen opens on its first row (`start`).
- Left for a later anti-cheat pass: a blink of up to the allowance (about 20 studs) is still possible in one step, through a wall too (it needs a wall check on each step), and height isn't checked.

**Found and fixed in the last checks** (not from the review)
- A locked preset's panel showed its guns as swapped for the default (MARKSMAN at level 1: the FAL in red, SPAWNS WITH THE AK-47, 11, Medium), though they open with it. A locked loadout now shows as it will be when it opens (FAL, 10, Light) with a red OPENS AT LEVEL 3 tile.
- Going back always put the bar at the top, and a gun list opened on EMPTY, so Enter by habit emptied the slot. BACK now returns to the row chosen there (`MenuKit` keeps a row by id; a screen can name its first row), LOADOUT opens on the selected loadout (the death screen too), a gun list on the gun in use, and RESET's confirm lists CANCEL first, as LEAVE MATCH lists STAY.
- A pull-back fired once while the test harness walked the character after a dive and wasn't seen again in five tries; likely the server's own get-up after 8 s on the floor leaving the server a moment behind. The bank now holds at least a second of walking in every stance, and the warning says where it happened and how far the last step went.

**Tested** (Studio play mode, 83tg's avatar, one player)
| Test | Result |
|---|---|
| Self-checks | `WeaponConfig`, `WeaponMath` (the plan's weights), `LoadoutRules` (presets free at their levels, saving, spawning, buying, weights, names), `VitalsRules` (sprint lengths, the refill, the quarter rule, no healing in the red or within the delay), `ProfileSchema` (the new fields, old saves, bad values) and `MenuRules` pass on load |
| A new player's CUSTOM 1, PLAY | M9 in hand, Uzi holstered, AK-47 carried: 13, Medium |
| SCOUT selected in the menu, PLAY | The Uzi alone, in hand: 2, Light; the main menu's LOADOUT row reads SCOUT |
| Sprint, Light, Shift held 11 s | Sprinted 7.8 s (client and server within 0.02 all the way) and stopped at empty on both; filling began 1 s later and took 4 s; Shift still held didn't start it again |
| Sprint, Medium, the AK-47 dropped 3.1 s in (dual wielding, 4) | Drained a sixth a second to 0.50, then from that share at Light's rate (1/7.8 a second); dry at 7.1 s, the sprint ended (Tired); filling began 1 s later and was full 4 s after. The HUD read LIGHT LOADOUT, white, as the AK-47 left |
| The AK-47 picked up again (F) | 13, Medium, the HUD's line white for a moment |
| Holding the AK-47, the right arm hit into the red | The AK-47 dropped (one arm): 4, Light |
| Right leg hit to 10 of 70 (in the red), Medium | Not healed in 10 s, still limping; a painkiller lifted it to 52 (walking) and it healed about 2.8 a second (4% of 70) to 70 within 7 s |
| Aim settle (server), each class | Light 0.135 s, Medium 0.151 s, Heavy 0.184 s (0.15 × 0.85 / 1 / 1.2, plus a frame) |
| Aim zoom (camera), each class | Exactly 14.12, 12.00 and 10.00 a second (12 ÷ the class's aim time) |
| Level 12, $5,000: the Desert Eagle bought through the menu | $3,500 left, owned, put straight in CUSTOM 1's Secondary; the panel showed 13 → 14 before buying |
| CUSTOM 1 selected mid-match | SELECTED, and APPLIES ON NEXT SPAWN in the panel |
| Rename: 37 characters typed, with M, W, S and Backspace among them | The box stopped at 20; M, W and S typed instead of closing or moving the menu; Backspace deleted instead of going back; saved with its three spaces made one (Studio's filter ran without error) |
| 20 bad requests sent straight to the remotes | Each refused with the right reason (Locked, WrongSlot, NotOwned, Empty, BadData, Unknown, Free, Owned, Cash…); a real Glock 18 purchase went through ($3,500 → $3,000) |
| The Desert Eagle taken off the profile, then a respawn | The M9 in its place (13, Medium); the panel showed the Desert Eagle in red, SPAWNS WITH THE M9 |
| Two Desert Eagles and the AK-47 saved, PLAY | One in hand, one holstered, the AK-47 carried: 15, Medium. Dual wielded (4): the shots alternated hands, a reload filled both (7 + 5 each), and with the AK-47 dropped, 6, Light |
| Death, M during the kill cam, SCOUT picked, the menu closed at 8 s | Hold at 1.1 s, Release at 8.3 s, respawned at 8.6 s with the Uzi |
| Death, M, the menu left open | Respawned at 15.4 s (the limit); the menu closed by itself |
| Death, a gamepad's Select, then Select again | LOADOUT over the kill cam; Hold at 1.3 s, Release at 13.7 s (the tools' delay), respawned 0.4 s later |
| Select alive, adrenaline full | Bullet time, as before |
| Death without the menu | Respawned at 3.3 s, as before |
| The screens at 1920 × 1080, 1024 × 768 and in Studio's window (1325 × 793) | The list, the panel and the gun picker fit side by side and read cleanly; nothing clipped. The Test Arena's floating signs show through the panel's plate (it is 60% opaque) |
| The mouse through LOADOUT | Hovering moves the bar and the panel; clicks open a loadout, a slot and its guns, and set one (CUSTOM 2's Primary to the M500: 8, Light) |
| After the review: self-checks | All pass on load; with the AK-47's damage at 40 (in a copy), every module still loads and two warnings explain the new weights |
| Walking, sprinting, limping, crouching, a dive, a vault, a running jump over the low wall, sliding along high cover, bullet time, getting up after 8 s on the floor | No pull-back and no warning; the bank never fell below 11 studs |
| A client setting its own walk speed to 26, no sprint | Ran 2.6 s, then was put back 7 times in 9 s: 17.6 studs a second on average (walking's 16 × 1.1), a warning every 5 s |
| The same at 16 while limping | Put back at its 12 studs a second |
| Respawning twice | One record left in the stance table |
| A 50-stud `PivotTo` from the server, then another after `StanceService.moved` | The first put back at once (the warning: "50.0 studs in the last step"); the second stayed |
| After the second check (2026-11-21): a client pushed to 24–26 studs a second while asking to sprint and to stop every 0.9 s | Put back 7 times in 9 s: 16.7 studs a second on average. (Forcing a humanoid's walk speed from a client script no longer speeds it up in this Studio, so the cheating tests now push the root) |
| Releasing Shift mid-sprint; then running dry | No pull-back; the bank never fell below 18.6 |
| Walking aimed; then aimed but pushed to 17 | No pull-back at 11.2; the push put back to its 12.3 studs a second |
| A client jumping 60 studs 0.3 s after respawning | Held to the usual allowance: 16.5 studs kept, the rest put back |
| A name and the default name sent in one frame | The default name kept, the filtered one dropped, no Busy |
| Studio's "Bad Connection (3G)" network (150 to 180 ms each way, jitter, 0.5% loss): walking, sprinting, stopping, crouching, a dive, sprinting into bullet time | No pull-back; the bank never fell below 13. The network settings were put back to none |
| BACK after the change | LOADOUT on CUSTOM 1, then the main menu on LOADOUT, as before |
| 5 saves at once; two names 0.5 s apart; a reset just after a name | The fourth save refused, TOO FAST; the second name refused; the reset's guns and name both applied |
| The server refusing a sprint, then forcing a stop | Predicted stamina to 0.24, then to 0 |
| Hold, Release, Hold 0.1 s apart while dead | Still dead at 6 s; back at the 15 s limit |
| A purchase | The line in the output, and Roblox's economy event |
| Limb hits, a painkiller, the AK-47 dropped | The figure, the painkiller count (3 → 2) and LIGHT LOADOUT follow; UNDER FIRE over the menu and LEAVE refused after a hit, as before |
| BACK and the first rows | LOADOUT opened on CUSTOM 1 (selected), the Primary list on the AK-47 (in use; Enter changed nothing and went back to PRIMARY), BACK to CUSTOM 1, then to LOADOUT; RESET's confirm on CANCEL, and CANCEL back to RESET |
| A locked preset and a locked slot | MARKSMAN: the FAL and S&W 500, 10, Light, OPENS AT LEVEL 3; CUSTOM 4: OPENS AT LEVEL 10 |
| Again after all the changes: the Desert Eagle bought through the screens (level 12) | The Secondary list opened on the M9 (in use); BUY, then back on SECONDARY with BOUGHT THE DESERT EAGLE in white and the panel showing it OWNED, 14 |
| Then death, M, BACK | LOADOUT on CUSTOM 1 (selected), the respawn held; BACK closed it and the new life came with the Desert Eagle in hand: 14, Medium |
| Output log | Clean apart from the DataStore line |

**Not done**
- Heavy can't be reached yet (guns alone weigh 17 at most): its aiming was measured with the class set by hand, and its stamina and healing only in `VitalsRules`' self-checks.
- Two players: seeing someone else's guns and class change, a purchase or a rename while others play, the death screen's hold in a busy match. Added to the two-client test ([[Animation and MP3 Systems - Progress and To Do#3. Play tests]]).
- The text filter only ran in Studio, which hands the text back unchanged; what a live server's filter does to a name wasn't seen. Renaming with a gamepad (the on-screen keyboard) wasn't tried.
- Saving the new profile fields against the real DataStore (Studio's API access is still off).
- The death screen's offer isn't shown on touch (the menus have no touch controls yet). No sounds: running out of breath, buying.
- The offer's SELECT label (shown after a gamepad was used last) wasn't seen on screen: the Studio MCP's gamepad buttons count as keyboard input, so Select was tested working but the label stayed M. The menu's own prompts name the gamepad's buttons as before (RESPAWN [B] on the death screen, which B does).
- The body-in-a-ring diagram, the posed character and the weapon icons (Blender art), and the Phase E slots (above).
- The speed check doesn't look at height or walls: climbing, flying or teleporting upwards, and a blink of up to its allowance (about 20 studs) in one step, through a wall too, are for a later anti-cheat pass. Bullet time slowing another player (to 0.3) under lag wasn't tried (one player; the activator's own 0.6 was). Roblox's Reset Character is still on (above).
- `LoadoutService`'s clean-up when a player leaves couldn't be run alone in Studio (stopping the test ends everything); it was checked by reading.
- Studio's Script Analysis (type warnings) wasn't run over the new and changed scripts.
- The place isn't published (Team Create keeps the changes). Nothing is committed: these notes.

## 2026-11-19: The reviewer's check over the economy code, its nine fixes, and Phase C checked against the plan
On this PC (Studio signed in as 83tg), with Claude Code driving Studio. JordanSaa asked for the `roblox-dev:roblox-reviewer` check over the progression code, then to fix everything it found and begin Phase C.
- 9 game scripts changed in the Team Create place (none added), and the two Studio tools (`ProfileCheats`, `TestHarness`) with their repo copies. No clip changed.
- **What players will notice:** a match only starts with 2 players in the fight (the menu doesn't count); a player who never fought, or had nobody else who counted, gets no win or loss pay; when everyone who counts ties, it's a DRAW, paid as a loss; after 5 kills or assists on the same victim in a match, more pay nothing.

**The review** (the `roblox-dev:roblox-reviewer` agent over 19 scripts: the profile, match and progression servers, their shared rules, the cheats and the six progression screens)
- No client can give itself XP, Cash, kills, titles or stats: `SetTitle` and `MenuRequest` are checked, throttled and checked again on the server, and no remote carries an amount. The DataStore side (locking, retries, `BindToClose`, number checks, migrations) and memory use were sound.
- It found nine problems, all fixed below. Two things it couldn't see from those files were checked here: `BulletTimeLevel` is cleared to nil when bullet time ends (so the +3 bonus can't pay on every kill), and the `Remotes` folder is saved in the place.

**Fixed**
1. **Win and loss pay could be farmed** (high). Two accounts tied 1–1 both "won" $1,000 a match, and an idle account with a second one sitting in the menu was paid $250 a match for nothing. Now (`MatchRules.results`): a player counts only if they were in the match for half of it **and fought** (`MIN_DAMAGE`: took 10 limb health off other players, or killed one); a match needs **two players who count** (`MIN_CONTESTANTS`) to be won or lost at all; a tie at the top still shares the win when someone else scored less, but when everyone who counts ties it's a **draw**: nobody wins and all are paid the loss. `MatchService` counts only `Deployed` players towards the 2 a match needs, and adds up the damage each player deals (`CombatLog.Hurt`). The end screen says DRAW (MATCH DRAWN on the loss row), or why the match didn't count: JOINED TOO LATE, NO DAMAGE DEALT or NOBODY TO BEAT. My calls, as placeholders: the 10 damage, and a draw paying the loss.
2. **Kills of the same victim paid without limit** (medium): an alt standing at a spawn was $13 a kill. Now at most 5 kills and assists on one victim pay per match (`ProgressionRules.PAID_PER_VICTIM`, my number); more still score and count in the lifetime stats.
3. **Leaving and rejoining while the profile loaded** could open two sessions of one profile on the same server (medium), kicking the player and losing up to a minute. One player's loads now run one at a time (`ProfileService`).
4. **A last save that failed was thrown away** (medium), and a rejoin to the same server then loaded the older autosave. It's now tried again every 10 s for as long as the server runs, and a rejoin to that server waits for it (up to 90 s, then "still being saved, please rejoin in a minute"). `ProfileStorage` no longer ignores a lock left by an earlier session on the same server.
5. **Up to about 35 s of play time was lost on each leave or shutdown** (low). `ProfileService.beforeRelease(callback)` runs just before the last save, and `ProgressionService` writes the play time there.
6. **Name tags could go missing with StreamingEnabled** (low): a tag waited only 10 s for the head and was dropped when the character streamed out. A player's tag now lasts their whole visit and finds their character and head again at every sight check (`NameTags`).
7. **A kill wasn't paid if the killer respawned before the victim died** (low), and their revenge could never pay. `CombatLog.killerOf` names the player the log saw land the killing blow; the match's score and the rewards both use it.
8. **`CombatLog` took infinite damage** (low; `LimbService` caps damage at the limb's health, so it can't happen today): refused now.
9. **`ProfileCheats` had no allowlist** (low; it can't run outside Studio). It now answers only the place's owner and Studio's own test players (ids below 1); anyone else goes in `EXTRA_USER_IDS`. Its install note now says Play mode only (in Edit mode the copy would be saved into the place). The repo's `Tools/ProfileCheats.luau` matches.

**Phase C checked against the plan**
- Everything in steps 7 and 8 of [[Menus, Loadout, Progression and Shop - To Do#Suggested build order]] is in the place: the level curve, every reward, the eligibility rule, the Cash multiplier (the prestige part too), the player card's stats and XP bar, the match-end screen and the level-up moment, milestone titles, the title picker (Tab, then the left and right arrows), name tags (60 studs, line of sight), the scoreboard, the kill feed, and titles on the kill cam's KILLED BY panel. Section 8 and the build order are ticked, and [[Architecture]] now describes each part instead of quoting its header.
- Missing from the plan's list: the level-up sound (the game has no sound yet). Not part of steps 7 and 8 and not built: achievement titles, Roblox badges, prestige (step 15).
- `TestHarness`: playing a match alone now also needs `DebugMinContestants = 1`, and PLAY pressed first.

**Tested** (Studio play mode, 83tg's avatar, one player; `DebugNpcKills` on, so the dummies count)
| Test | Result |
|---|---|
| Self-checks | `MatchRules` (with the new draw, idle and alone cases), `ProfileStorage` (with the same-server lock case) and `ProgressionRules` pass on load |
| One player in the menu, `DebugMinPlayers = 1` | Stays WAITING; the match starts once they press PLAY |
| Six headshot kills of the same dummy in one match | Score and stats 6; paid 5 (65 XP, $65) |
| That match ending (`DebugMinContestants = 1`) | Win: $1,000 and 1,000 XP; the summary says won, not drawn; level 1 → 4 with 15 XP |
| The next match | The first kill paid again (the cap is per match) |
| Alone, with the default 2 contestants | MATCH OVER (`Alone`): the kill paid, no win or loss, Matches not counted |
| A match without firing | `Idle`, nothing paid; the end screen reads NO DAMAGE DEALT: THIS ONE DIDN'T COUNT, and it fits |
| A last save failing twice (a copy of `ProfileService` on a stand-in DataStore) | Tried again at 10 s and 20 s, saved on the third try; the `beforeRelease` callback ran once before it and its change was saved; the lock given up |
| A name tag on a dummy whose head is taken away and a new copy put back (as streaming does) | Shown; hidden with no head; hung on the new head and shown; back on the original |
| `mp.profile()` as the place's owner | Answers as before |
| Output log | Clean apart from the DataStore line and the stand-in's own warnings |

**Not done**
- The two-client test is still owed: kills, assists, revenge, a draw, name tags and the kill feed between two real players, and a kill credited after the killer respawned (fix 7). The one-load-at-a-time fix (3) wasn't run: it needs the same player to leave and rejoin while their profile loads.
- Saving against the real DataStore (Studio's API access is still off).
- Private servers (lower or no rewards there?) and an XP-per-minute cap: decisions, in section 9 of the plan.
- Studio's Script Analysis (type warnings) wasn't run over the changed scripts.
- The place isn't published (Team Create keeps the changes). Nothing is committed: `Tools/ProfileCheats.luau`, `Tools/TestHarness.luau` and these notes.

## 2026-11-18: Phase B of the menu plan: the main menu, the menu kit and the first UI art
On this PC (Studio signed in as 83tg, Blender 5.2.3), with Claude Code driving Studio and Blender. JordanSaa asked for Phase B ("the menu shell") of [[Menus, Loadout, Progression and Shop - To Do#Suggested build order]]; nothing past it was built.
- 6 scripts added and 12 changed in the Team Create place (65 game scripts now). No clip changed.
- **Players no longer spawn by themselves:** they join into the main menu and press PLAY. In Studio play tests, press Enter (or `mp.play()`, [[Test Arena]]) to get a character.

**New: the main menu** (`MenuController`, client)
- A player joins with no character, into the main menu over the live match: the MAXIMUM PAIN logo, MAIN MENU, then PLAY, LOADOUT, SHOP, SETTINGS (the plan's proposed order); the player card and stats bottom left (`PlayerCard`); the mode, map, player count and match clock top right; SELECT [ENTER] bottom right.
- PLAY asks the server for a character; the menu fades when it arrives.
- **M** opens the same menu mid-match, over the player's own view: RESUME, LOADOUT, SHOP, SETTINGS, then LEAVE MATCH set apart. M, RESUME, Backspace or B closes it. The match doesn't pause and the character can be shot: a hit shows UNDER FIRE and a red flash over the menu, and dying closes it at once for the kill cam.
- LEAVE MATCH asks to confirm (STAY / LEAVE); the server takes the character away and the player is back in the menu they joined into.
- LOADOUT, SHOP and SETTINGS open their screen with NOT OPEN YET: each becomes a real screen when its phase builds it (one entry in `MenuController`'s `SCREENS`).
- While it is open: the HUD is covered, the mouse is free, the camera doesn't turn, the body doesn't move or jump, and no gun, prompt or game key does anything. Roblox's own menu (Esc) covers it, and it comes back when that closes. The match-end screen waits behind it.
- Keys: the up and down arrows or W/S (D-pad, left stick) move the white bar, which wraps round; Enter (A) selects; Backspace (B) goes back. Esc can't be BACK: it is Roblox's menu. The mouse works too: hovering moves the bar, a click selects.

**New: spawning goes through the server** (`SpawnService` in ServerScriptService; `MenuRules` in ReplicatedStorage.Modules; the `MenuRequest` and `MenuResult` remotes)
- `Players.CharacterAutoLoads` is off. A client may ask for two things only, "Play" and "Leave" (`MenuRequest`, no values, at most one every half second); a refusal comes back with why (`MenuResult`).
- **Play** needs a loaded profile and no character. From then on the player is deployed (`Deployed` on the Player): respawned `Players.RespawnTime` (3 s) after each death, as Roblox did, and given a character back after 3 s if theirs goes any other way (a fall out of the world).
- **Leave** is refused within 5 s of being hurt (`LEAVE_SAFE_TIME`: any drop in limb health), in a Last Stand, or dead, so the menu is never a way out of a fight. It takes the character away (no death is counted) and ends the player's stretch in the match (`MatchService.sitOut`), as leaving the server does; they are back in the match when they spawn again. Someone out of the match when it ends is in no results, so gets no win or loss pay.
- **Redeploy delay:** PLAY waits 10 s after leaving (`REDEPLOY_DELAY`; the menu counts down READY IN 10, 9…, and the server refuses anything earlier). Without it, leaving and playing again would be a free instant heal, ammo refill and trip back to a spawn point. My call (not in the plan): change the number in `MenuRules`.
- While a player is in the menu, the server points their `ReplicationFocus` at the menu camera's shot, so StreamingEnabled streams the map in where they look.

**New: the menu camera** (`MenuCamera`, client; shots in `Workspace.MenuCams`)
- The plan's option (a): a slow dolly through four shots of the Test Arena, 12 s each, dipping to black at the cuts. The shot on screen comes from the server's clock, so everyone in the menu sees the same one and the server knows where to stream.
- Shots are placed in Studio: `Workspace.MenuCams.<Map>` holds Models named Shot1, Shot2…, each with two invisible Parts, From and To, facing the way the camera looks, and an optional `Fov` attribute. `MenuCams` is a Persistent model, so its parts reach every client. A map with no shots gets a slow turn round the middle of the world.

**New: the menu kit** (`MenuKit`, client): the parts every menu screen is built from, in section 2's style.
- A canvas laid out in 1080p pixels (the HUD's scale rule, shrunk further on screens smaller than 1100 × 960); the dark gradient down the left; the context line, the big heading (it arrives with a red and cyan glitch) and the list with the white selection bar (Quad Out, 0.08 s), grey unavailable rows and gaps between groups; a red notice line; the prompts bottom right, named for the keyboard or the gamepad, whichever was used last (hidden on touch); the film overlays; and the colour grade on the live view (saturation −0.5, contrast +0.1, a teal tint, blur 4, the far distance out of focus).
- `MenuKit.reducedMotion` turns off the glitch, the bar's slide and the film's drift, for the reduce-motion setting when settings exist.

**New: UI art from Blender** (`Assets/Blender/UI/ui_lib.py`; `UiAssets` in ReplicatedStorage.Modules)
- `ui_lib.py` builds and renders the menus' images: the logo (`UI_Logo.blend`: MAXIMUM PAIN in Oswald Bold, the HUD's own font, extruded, worn white paint over steel; one-line and two-line versions), the film overlays (a grain tile, a vignette, two bokeh images and a light leak, worked out pixel by pixel) and weapon icons (below). Re-running it gives byte-identical files. How to run it: [[Blender and Asset Pipeline#UI art for the menus]].
- The seven images were uploaded by 83tg through Studio. Their ids are in `UiAssets` and in `Assets/Blender/UI/Exports/ui_ids.json`; nothing else holds an asset id. The menu shows the logo, the vignette, the bokeh, the light leak and the grain; each falls back to a placeholder (the title in text, dark bars, nothing) if its id is taken out.
- **Weapon icons:** the renderer is built and was tried on the M9 (side-on, muzzle right, white, tinted the HUD's grey in game), but the 13 icons aren't made, because the guns' source isn't here: `Assets/Blender/Weapons/build_weapons.py` and its `Exports/FBX` aren't in the repo or on this PC. JackT6785's reverted commit `ed11f9d` has FBX files for 9 of the 13 guns and a `WeaponKit.blend` with only the M9, and Studio won't hand out the uploaded meshes ("no permission to load asset"). With the FBX folder in place, `ui_lib.py weapons` makes all 13.

**Changed**
- `CharacterController.setControlEnabled`. Off, the body stands still. Roblox's new PlayerModule (2026) reads the movement keys through the Input Action System, not ContextActionService, so the menu can't take the keys from it; instead `update`, later in the same frame, sets the humanoid's move back to nothing (as it already did in cover), and jumping is off. A dive or vault under way finishes.
- `CameraController.setLookEnabled`, `WeaponController.setInputEnabled`, `Hud.setCovered` (kept apart from `setVisible`, so the menu and the kill cam don't undo each other).
- `Keybinds.Menu` (M, also in the HUD's keybind list). `LimbRules.totalHealth`. `UiStyle.modeName` and `mapName` (the scoreboard's, now shared). `MatchService.sitOut`. `GameServer` starts `SpawnService`; `ClientMain` starts `MenuController` last.
- `TestHarness`: `mp.play()` and `mp.leave()`. The repo's copy (`Tools/TestHarness.luau`) was behind the place's (it lacked `mp.progress`, `mp.title` and `mp.shoot`); they are the same script again.

**Found**
- **A gamepad's Start opens Roblox's own menu**, whatever a game binds to it (tested, as the plan asked). The plan's fallback, Select, is bullet time, so the menu has no gamepad button to open it mid-match yet: a decision for JordanSaa, in [[Menus, Loadout, Progression and Shop - To Do#0. Decisions to make first]]. In the menu, B resumes.
- **Phase C's code is already in the place**, and these notes don't describe it: `ProgressionService` and `CombatLog` (server); `ProgressionRules`' level curve, rewards and titles; `UiStyle`, `PlayerCard`, `Scoreboard`, `MatchHud`, `KillFeed`, `NameTags` and `MatchEndScreen` (client); the `ProgressionEvent`, `KillFeed` and `SetTitle` remotes. No Claude session on this PC built it, and GitHub has nothing newer (checked 2026-11-18). Phase B builds on `UiStyle` and `PlayerCard`. [[Architecture]] now lists them from their own headers; the rest (the to-do's steps 7 and 8, tests) is for whoever built them to write up.
- One Studio window showed only a flat grey world in play-mode screenshots (the HUD and menus drew, the 3D view didn't); after Studio restarted, screenshots were normal. Nothing in the game caused it.

**Tested** (Studio play mode, 83tg's avatar, one player)
| Test | Result |
|---|---|
| Joining | No character; the menu over the live match (the dolly, the grade, the film overlays); HUD covered, mouse free; `ReplicationFocus` on the shot |
| Moving through the menu | Arrows, W/S, Enter, Backspace; the bar wraps round; mouse hover and click; LOADOUT opens NOT OPEN YET with BACK [BACKSPACE] |
| PLAY | The character spawns and the menu fades as it arrives; HUD back, mouse locked, grade off; the match counts the player |
| M mid-match | RESUME … LEAVE MATCH over the player's own view, with RESUME [M]; M again closes |
| Walking with the menu open | Before the fix, W held kept walking (16.5 studs in 1 s); after, 0.00 studs in 1 s and no jump, and walking goes on as soon as it closes |
| Gun keys with the menu open | 3 and R did nothing |
| A hit with the menu open | UNDER FIRE and the red flash |
| LEAVE within 5 s of a hit | Refused: YOU CAN'T LEAVE WHILE YOU ARE UNDER FIRE |
| LEAVE | The character gone, no death counted; out of the running match (`isPlaying` false); back in the menu, focus on the shot |
| PLAY right after leaving | The server refused a direct request (Cooldown); the row counted down READY IN 10, 9… in place; PLAY early showed TOO SOON AFTER LEAVING THE MATCH |
| Dying with the menu open | It closed at once; the kill cam; respawned 3.4 s later; `MatchDeaths` 1 |
| A match ending with the menu open | The match-end screen waited behind it and showed when it closed |
| Esc | Roblox's menu covered it; it came back after |
| Gamepad Start | Opened Roblox's menu, not this one |
| `mp.play()`, `mp.leave()` | Work |
| The art | All 7 images load in game; two runs of `ui_lib.py` gave byte-identical files |
| Output log | Clean apart from the DataStore line |

**Not done**
- A gamepad button to open the menu mid-match (above).
- The weapon icons (above). Item, skill and crate icons, badges and 9-slice panels come with later phases.
- No menu sounds (the game has none yet), no touch controls, no reduce-motion setting (the switch is there for it).
- Screen shapes: only Studio's window (1609 × 793) was seen. 21:9, 4:3 and a phone weren't tried.
- Two players: someone in the menu, seen from the match (they have no character), and the menu camera showing the other player. Added to the two-client test ([[Animation and MP3 Systems - Progress and To Do#3. Play tests]]).
- Studio's Script Analysis (type warnings) wasn't run over the new scripts.
- The place isn't published (Team Create keeps the changes). Nothing is committed: `Assets/Blender/UI/` (new), `Tools/TestHarness.luau` and these notes.

## 2026-11-14 (later): Phase A of the menu plan: slots renamed, the server profile, the match manager
On this PC (Studio signed in as 83tg), with Claude Code driving Studio. JordanSaa asked for Phase A ("foundations") of [[Menus, Loadout, Progression and Shop - To Do#Suggested build order]] and nothing past it. Nothing here is visible to a player yet.
- 8 scripts added and 8 changed in the Team Create place (50 scripts now). No clip changed.
- Started ahead of two of the animation work's blockers: the place isn't published and the two-client test hasn't been run.

**Changed: the weapon slots are Primary, Secondary and Tertiary in code**
- `Two` → `Primary` (key 3), `OneA` → `Secondary` (key 1), `OneB` → `Tertiary` (key 2), as the loadout screen will call them. The keys, the order and every rule are as before.
- Where: `LoadoutRules` (`Slot`, `HoldMode`, `Inventory`, its self-checks), `LoadoutService`, `WeaponController`, `Keybinds` (`SlotSecondary`, `SlotTertiary`, `SlotPrimary`), `AnimationController`, `Hud` (a comment). So the guns' `Slot` attribute, the character's `HoldMode` attribute and the `WeaponAction` remote's "Hold" value carry the new names.
- Left alone: `OneArm` (an arm state), and the clip names with "Two" in them (`CoverHoldHighTwo`, `BlindFireHighTwoLeft`…), which mean two-handed and are published animations.
- Done before any profile was saved, so no saved data ever holds the old names.

**New: the server profile** (`ProfileService`, `ProfileSchema`, `ProfileStorage` in ServerScriptService; `ProgressionRules` in ReplicatedStorage.Modules; `GameServer` starts it)
- Each player has one saved profile: `Version, Level, XP, Cash, Prestige` and `Stats` (kills, deaths, headshot kills, matches, wins, seconds played). Later steps add their own fields; old saves get the defaults when they load.
- **`ProfileService` is the only code that saves data.** Other code reads with `get(player)` (the table is frozen) and changes with `update(player, function(profile) … end)`: the function edits a copy, which replaces the profile only if it ran without an error or a wait and the result passes `ProfileSchema.validate`. A change is kept whole or not at all, so a save can't catch one half done, and a negative balance or level 51 is refused.
- DataStore safety: one key per player (`Player_<UserId>`), `UpdateAsync` only, each call in `pcall` and tried again after 1, 2, 4… s. The profile is locked to the server that loaded it, inside the same `UpdateAsync`; each autosave (60 s, spread out per player, skipped while the server's budget is spent) refreshes the lock, and a lock 180 s old belongs to a dead server and may be taken. Every save first checks the lock is still its own, so a server that lost it can't write over the new holder. Saved on leaving and in `BindToClose` (which waits up to 25 s for the last saves).
- **A player whose profile can't be loaded is kicked** with a message (still saving on another server, a save from a newer version, an unreadable save, DataStores down). They never play on a fresh profile, since saving that would wipe their real one.
- Level, XP, Cash and Prestige are copied to attributes on the Player for the menus. No remote carries them and nothing a client sends changes them.
- Studio play tests save to a DataStore of their own (`PlayerProfiles_Studio`), never the live one. With Studio's API access off, as now, profiles are kept in memory and one line in the output says so.

**New: the match manager** (`MatchService` in ServerScriptService, `MatchRules` in ReplicatedStorage.Modules)
- States: Waiting (fewer than 2 players), Intermission (15 s), Running (8 minutes). All placeholders in `MatchRules`. Free-for-all: a kill is a point, the most points wins, ties share the win, nobody wins on 0.
- Everyone who spawns while a match runs is in it, joining midway too. It counts kills, deaths and each player's time in the match (time out of the server doesn't count; a rejoin keeps its score).
- At the end, `MatchService.Ended` carries the results: each player's score, kills, deaths, seconds, `won`, and `eligible` (in the match for at least half of it), which the win and loss payouts will need. Nothing is paid yet.
- `LastStandService` now announces every death it deals with whoever dealt the blow (`Killed`), a killing shot or a Last Stand that failed. Kills are scored from it, only between two players.
- Clients read the match from attributes on `ReplicatedStorage.Match` (`State`, `Mode`, `Map`, `Number`, `EndsAt`) and their own `MatchScore`, `MatchKills`, `MatchDeaths`.

**New: Studio tools**
- `ServerStorage.Tools.ProfileCheats` (repo: `Tools/ProfileCheats.luau`) and `mp.profile(...)` in the test harness (repo: `Tools/TestHarness.luau`): set your own Level, XP, Cash and Prestige in a play test, or start afresh. It only runs when cloned into ServerScriptService in Studio, and stops at once anywhere else.
- `DebugMinPlayers`, `DebugLength`, `DebugIntermission` on the `MatchService` module (Studio only), to run a match alone and quickly.

**Tested** (Studio play mode, 83tg's avatar, one player)
| Test | Result |
|---|---|
| Keys 1, 2, 3, 4, G, F, gamepad Y | `HoldMode` Secondary, Tertiary, Primary, Dual as before; `DrawTwoHanded` and `SwapToOneHanded` played; dual wield dropped the AK and F took it back; G while dual left the Uzi (Tertiary) in hand; Y cycled |
| Firing, reload, dual fire | M9 15 → 12, reload moved 3 from the spare rounds; dual wielding fired both hands |
| Last Stand with nothing in hand | `prepareLastStand` drew the Secondary |
| HUD | rows 1, 2, 3; DROPS AK-47 shows and hides with the Primary |
| `ProfileStorage` against a stand-in DataStore (21 checks) | new player; autosave refreshes the lock; a second server is refused and writes nothing; the final save unlocks; an old session's save is refused; a lock 179 s old holds and 180 s old is taken; saves retry after errors and give up after their tries; a write that raced still ends locked; newer and bad saves are refused and left untouched; an old save is filled in |
| `ProfileService` in play (15 checks) | the profile is frozen; a change goes through whole; a change that errors, waits or breaks a rule is dropped whole; on copies of the service with a stand-in DataStore: autosave, release, "no changes after release"; a save that throws doesn't leave the profile stuck; a session whose lock another server took writes nothing, ends at its next autosave and kicks the player with a message |
| Cheats: `mp.profile` | sets and reports; level 51, level 0, negative, fractional and NaN cash, prestige 6, unknown fields and wrong types all refused |
| Match alone (`DebugMinPlayers = 1`) | Waiting → Intermission → Running → results → Intermission → Waiting; `EndsAt` right; a killing blow and a failed Last Stand from the Gunman each fired `Killed`, counted a death and scored nobody; results: eligible, not won (score 0) |
| All 50 scripts | compile, `--!strict`; nothing left over from testing; output log clean apart from the DataStore line |

**Not done**
- **Saving against the real DataStore.** Studio's API access is off (Game Settings > Security > Enable Studio Access to API Services), so loading, locking and saving were tested against a stand-in only. Turn it on and check a value set with `mp.profile` is still there in the next play test, before any of this reaches live players.
- **Kills scoring between two players**: it needs the two-client test ([[Animation and MP3 Systems - Progress and To Do]], to-do 3). Add to that list: Player1 kills Player2 → Player1's `MatchKills` and `MatchScore` go up, Player2's `MatchDeaths`; the winner at the end.
- Studio's Script Analysis (type warnings) wasn't run over the new scripts.
- The `roblox-dev:roblox-reviewer` check over the profile code, due before publishing anything that touches cash or XP.
- The place hasn't been saved (File > Save to Roblox) since these changes, and isn't published.
- The repo: `Tools/ProfileCheats.luau` (new), `Tools/TestHarness.luau` and these notes aren't committed.

## 2026-11-14: Every clip published, checked against the place, and the place saved
On this PC (Studio signed in as 83tg). No clip or game code changed apart from `AnimationConfig`'s ids.
- Details: [[Animation and MP3 Systems - Progress and To Do]] (to-do 1 and 2, and the 2026-11-14 test log).

**Published: the 30 clips made since the first upload**
- The first 102 clips were published on 2026-11-10 through Open Cloud (`Assets/Blender/Animation/publish_animations.ps1`, an API key made on 83tg), their ids in `AnimationConfig`'s `IDS`.
- On 2026-11-14 83tg uploaded the rest the same way: session 7's 4 two-handed blind fire clips, session 8's 7 new clips, and with `-Force` the 19 it re-made. The `.rbxmx` files were rebuilt from the current export first.

**Changed: the game** (Team Create place)
- `AnimationConfig`: the 30 new ids in `IDS`, and `STALE` emptied. All 113 clips and all 123 slots now have a published id: Studio plays the published animations, and live servers will once the place is published.

**Tested**
| Test | Result |
|---|---|
| Every id in `IDS`, loaded back in Studio, against the place's clip | all 113 equal: 13,928 keyed poses, keyframe times, markers, easing, priority, looping |
| Control: three re-made clips against their old 2026-11-10 uploads | differ by up to 113°, so a stale upload would show |
| Play mode (83tg's avatar): crouch, draw the AK, stand, back to the M9, fire, reload with the AK carried | `CarryTwoHandedLow`, `DrawTwoHanded`, `HoldRifleLow`, `SwapToOneHanded`, `ReloadPistolOneHand` and the rest all played from their published ids |
| The place before saving | no test leftovers, `HttpEnabled` off, all 42 scripts compile and are `--!strict`; output log clean |

**Not done**
- Publishing the place (83tg). Until then live servers run its last published version, without these ids.
- The two-client test and the live test ([[Animation and MP3 Systems - Progress and To Do]], to-do 2 and 3).

## 2026-11-12: Switching between the carried rifle and a one-handed gun
Session 8 went on into 2026-11-12 (this PC, Studio signed in as 83tg). JordanSaa asked for polish only, so it took the most visible fault left by the 2026-11-11 changes; the notes waited until after.
- Two clips (one re-made, one new; 113 clips, 123 slots), not published. Five scripts changed in the Team Create place.
- Details and numbers: [[Animation and MP3 Systems - Progress and To Do]] (session 8, part 7).

**Fixed: the rifle jumped between the hands on a switch** (`mp_hands.HANDOVER`, `draw_two`, `swap_to_one`, `check_switch`)
- The server re-hung the gun as a switch began. Drawing the carried rifle (3), it jumped 2.4 studs and turned 50° in one frame; putting it back for a one-handed gun (1, 2), it snapped round 90° to 112°.
- The clips now bring both hands onto the gun partway through, in one pose (`HANDOVER`): the right hand on the grip, the left round the middle, the gun across the front of the body pointing left. Found by a scored search on the idle.
  - `DrawTwoHanded` (0.55 s, re-made): the left hand lifts the rifle out of the carry by its middle, the right hand takes it 40% of the way through, then both port it across the chest and up to the ready hold. On the way up the left arm passes a waypoint with the gun level beside the hip; going straight there, the stock swept 0.5 into the left thigh (the M107 0.76).
  - `SwapToOneHanded` (0.3 s, new): the left hand takes the rifle from the right 33% of the way through and lowers it into the carry; from 53% the right hand draws the one-handed gun from the holster.
- Checked in `register()` with every long gun (`check_switch`): never in the head; in the left hand at most 0.05 into the legs and torso (the M107 0.1), in the right no deeper than the rifle hold's own + 0.1; more than 0.3 over the floor; and at the handover the gun within 0.03 and 3° of where it was in the other hand.

**Fixed: the hands meet on the gun on any body** (`AimLayer`, `AnimationController`)
- The clips are made on the default R15. 83tg's avatar has shoulders 0.26 narrower on each side, so at the exact handover frame its hands still missed each other by about 0.4 studs (6° to 20° of turn).
- A gun that changes hands now starts where the old hand had it and eases into its new grip over 0.12 s (in the character's own time). Further apart than 1.2 it just moves, as a second pistol going to the right hand does.
- At the arm clips' usual fade-in (`ARM_FADE`), the swap clip was only 73% in at its handover and the hold clips under it pulled the hands apart. The two switch clips now fade in at 40 a second (`SWITCH_FADE`). They start from the hold they replace, so nothing jumps.

**Changed: the game** (Team Create place)
- `LoadoutRules`: `HANDOVER` (draw 0.4; swap 0.33, then the one-handed draw 0.53) and `handoverTimes`, with self-checks.
- `LoadoutService`: a gun the switch hands over waits where it is until its share of the switch's time (`handOver`, `record.waiting`). A switch cut short, or replaced by another, puts every gun where it belongs at once.
- `AnimationController`: plays `SwapToOneHanded` when the rifle is still in the right hand as a switch to a one-handed gun starts (`DrawOneHanded` where it can't load); `SWITCH_FADE`.
- `AimLayer`: the handover ease (`easeHandovers`, `noteGrips`).
- `AnimationConfig`: the `SwapToOneHanded` slot; `DrawTwoHanded` added to `STALE` (Studio plays the new clip, live servers the published old one).

**Tested** (Studio play mode, 83tg's avatar)
| Test | Result |
|---|---|
| Imported clips | both match the export (every keyframe's rotation matrix exactly) |
| Draw (3) and put back (1), the gun on the frame it changes hands | on the frame it moves it's 0.38 off its new grip, where the old hand had it, and on the grip the next frame; no jump beyond the clip's own motion |
| The clips frozen on a copy of the avatar, front view | lifted by the middle, taken across the chest, ported, ready; putting back, the rifle lowers to the carry as the pistol comes out of the holster |
| 3 → 1 → 3 within a third of a second | the rifle ends in the right hand, both pistols holstered |
| 4 during the swap | dual wields; the rifle is dropped |
| Output log | clean |

**Not done**
- Publishing `DrawTwoHanded` and `SwapToOneHanded` (83tg). Until then live servers play the old `DrawTwoHanded`, which wasn't made for the later handover, and `DrawOneHanded` instead of the swap.
- On bodies unlike the default the receiving hand could be placed on the gun with IK near the handover (to-do 4.29); the ease covers it for now.

## 2026-11-11: The low cover squat, guns carried by the middle, crouched rifle holds, one-handed reloads, a longer dive
Session 8 ran on this PC (Studio signed in as 83tg), 2026-11-11, with Claude Code driving Blender headless and Studio. JordanSaa sent what a play test showed (with a screenshot), asked for the dive's distance and airtime to change, and asked that animations be judged on whether they look natural. Each fix below was looked at on 83tg's avatar in screenshots as well as measured.
- 24 clips (6 new, 18 re-made; 112 clips, 122 slots), not published. Five scripts changed in the Team Create place.
- Details and numbers: [[Animation and MP3 Systems - Progress and To Do]] (session 8, parts 1 to 6).

**Fixed: the low cover squat folded into itself** (`mp_stances.cover_low`: `LOW_ROOT`, `LOW_WAIST`, `LOW_FEET`)
- Behind low cover the body folded over the knees on the balls of the feet: the pelvis tipped 30°, the waist 46° more (76° from upright), the chest 0.95 into the thighs' boxes. It read as the body falling into itself.
- Now a deep squat, the way a person sits on their heels: the pelvis upright, the lean from the waist alone (47°), the feet wide and turned out, heels down, the knees over the toes, the chest between the knees. Found by a search that kept the head's box under 3 studs over the floor (2.99 on the default R15) and the body out of the floor.
- Everything made on the squat was made again: `CoverLowLeft/Right`, the low cover holds (`CoverHoldLowOne`, `CoverHoldLowDual`, `CoverHoldLowTwoLeft/Right`), `CoverPopUpLeft/Right`, `CoverDuckLeft/Right`, `CoverCornerLowLeft/Right` and the low carry.
- **Low blind fire** (`mp_hands.LOW_FIRE`): the old clip's 105° chest twist left the gun 0.02 under the top on the squat, and the torso 0.42 in the wall. Now the chest comes up out of the lean and leans off the gun side, the arm goes straight up past the ducked head, and the gun pokes over the top tipped up about 25°. Level, it cleared the top by at most 0.22: with the arm straight up the wrist can't bend back far enough.

**Fixed: two-handed guns carried by the stock** (`mp_arms.CARRIES`, `carried`, `check_carry`; `mp_lib.carry_grip`; `LoadoutService.carryOffset`)
- The carried gun hung from the left hand by its pistol grip, like a stick held at one end, and the carries pushed it into the body: crouched it stuck out to the side, 0.66 into the legs and 0.56 into the torso; behind high cover 0.7 into the legs; running 0.47.
- Now the fist is round the middle of the gun's length at the handguard's height, the gun running front to back through it like a bag's handle. `LoadoutService` hangs it that way, worked out from each gun's own parts and Support point (`carryOffset`). Dual pistols are still held by the grip.
- The four carries were made again for it: at the side standing; beside the left knee pointing ahead crouched (to-do 4.6); in front of the left hip behind high cover; by the left knee behind low cover, tipped up with the butt toward the floor.
- Found by a search with every long gun, each hanging at its own middle, on every body the carry plays over, AimLayer's arm swing on the run included. `register()` checks it again (`check_carry`).

**Fixed: crouched with a two-handed gun, the gun went through the thighs and the right arm into the chest** (`mp_arms.LOW_HOLDS`, `two_handed_hold_low`, `check_low_hold`)
- Crouched, the game played the standing low-ready hold, made on an upright chest. On the crouched body the gun went up to 0.78 into the legs and 1.3 into the floor, the forearms 0.9 into the thighs, and the right arm folded into the chest.
- `HoldRifleLow`, `HoldShotgunLow`, `HoldSniperLow` (new): made on the crouch idle, the gun across the front of the body, muzzle to the front-left and down, both hands on it, the elbows down. Checked with every gun of each set on the crouch idle and the whole crouch walk, the support hand placed as AimLayer places it.

**Fixed: reloading a one-handed gun pulled the carried rifle through it** (`mp_hands.reload_pistol_one`, `reload_revolver_one`, `reload_sawn_off_one`, `check_one_hand_reload`)
- The reloads were made for a free left hand. With a rifle carried, the left hand brought it over to the gun being reloaded, through that gun.
- New clips that key the right arm only, the gun reloaded against the belt at the right hip, with the same markers as the two-handed clips: `ReloadPistolOneHand` (the M9, Glock 18, Desert Eagle and Uzi), `ReloadRevolverOneHand` (the SW500), `ReloadSawnOffOneHand`. Checked against the two-handed reloads on the standing, crouched and cover bodies.

**Changed: a longer, lower dive** (`DodgeRules`, `DodgeController`)
- Launch 26 → 24 studs/s across and 15 → 9 up; gravity in the air 0.25 → 0.1 of the place's.
- **Fixed on the way: every dive ended at its highest point.** The Humanoid senses the floor from well above standing height, so once the body stopped rising it "landed" in mid-air and pulled the body down to its feet. Retuned without the fix, the dive lasted 0.52 s over 11.5 studs, where the numbers gave 0.76 s and 18. `DodgeController` now switches the Humanoid's Landed, Running and RunningNoPhysics states off while the dive flies (`holdInAir`), and lands it itself.
- **Fixed: bullet time shortened the dive.** It slowed the dive's speeds but not its fall, so a slowed dive came down far too soon (worked out: about 0.24 s and 3 studs at half speed). The lift now scales with the square of the time scale, so the whole arc slows.
- Before: about 0.5 s in the air and 17 studs to rest, 1.6 high. Now: 0.78 s in the air over 18.6 studs, 1.4 high, sliding to rest at 20.2.

**Changed: the game** (Team Create place)
- `LoadoutService`: the carried gun hangs by its middle (`carryOffset`).
- `AnimationController`: crouched with a two-handed gun it plays `Hold<set>Low` (the standing hold where that can't load); with a two-handed gun carried, a one-handed gun's reload plays `ReloadOneHand_<gun>` (the two-handed reload where that can't load).
- `AnimationConfig`: the 3 crouched hold slots and 6 one-handed reload slots (122 slots). A `STALE` list of the 18 re-made clips: in Studio they play their new KeyframeSequences, not their published ids, so the new clips can be tested before they're published; live servers play the published ones.
- `DodgeRules`, `DodgeController`: the dive.

**Tested** (Studio play mode, 83tg's avatar)
| Test | Result |
|---|---|
| The carry, standing, crouched and behind high cover | the AK held by its middle at the side; crouched beside the left knee, about level; the holstered Uzi on the same thigh clear of it; nothing clipping (screenshots) |
| Crouch walk with the AK in hand | the legs clear; the gun 0.17 over the floor; the right forearm resting on the chest (0.04) |
| M9 reload with the AK carried | the one-handed clip played (full weight from 0.15 to 1.95 s); the AK moved at most 0.075 against the hips; the spent magazine dropped |
| Low cover squat, blind fire both sides | from the enemy's side only the hand and pistol show over the top, about 20° up; the head stays hidden; the carried AK never in the head or torso (225 frames) |
| Aiming over low cover, ducking back | both work on the new squat; the shins 0.22 under the floor while ducking, 0.07 at rest |
| Dive on a flat floor | 0.78 s in the air, 18.6 studs, 1.4 high; 20.2 to rest; gets up and walks |
| Dive in bullet time (0.6) | the same arc, slower: 18.8 studs in 1.32 s |
| Imported clips | all 24 match the export |

**Decided**
- The crouch walk's legs sinking into the floor (to-do 4.20) stays as it is: JordanSaa called the amount negligible (2026-11-11).

**Not done**
- Publishing the 6 new clips and the 18 re-made ones again (83tg). Publish the re-made carries before the place: `LoadoutService` now hangs the carried gun by its middle, which the old published carry clips weren't made for.
- Ducking back into low cover puts the shins 0.22 under the floor (0.07 at rest). Blender's boxes show no deeper dip than the squat's, so it comes from the blend's timing (to-do 4.28).

## 2026-11-10: Two-handed blind fire behind high cover
Session 7, late on 2026-11-10 (this PC, Studio signed in as 83tg). It did to-do 4.26, the first open polish item; the to-do's first items (saving the place, committing, publishing) wait on JordanSaa and 83tg.
- Four new clips (106 clips now, not published yet). Two scripts and the test harness changed in the Team Create place.
- Details and numbers: [[Animation and MP3 Systems - Progress and To Do]] (session 7).

**Fixed: rifles and other long guns blind fired from high cover** (`mp_hands.blind_fire_two`, `TWO_FIRE`; to-do 4.26)
- The high blind fire clips were made with a pistol. With a long gun the arm guard kept it out of the wall by swinging the arm about 50° round mid-wall; at the end working right the support arm went 0.44 into the wall's corner, and working left and on the runs the support hand couldn't reach the gun.
- `BlindFireHighTwoLeft/Right` (still) and `BlindFireHighMoveTwoLeft/Right` (on the run) hold it in both hands across the body: still, pointing toward the edge worked and turned round it (41° working right, 17° working left, where the chest turns to the corner); on the run, ahead along the wall.
- Found by a search in Blender with every long gun in the place and the support hand placed as AimLayer places it, at a wall's end 0.5 to 0.9 past the root and mid-wall, and checked in `register()` the same way. The blends were simulated with Roblox's blending against the same switches with the old clips.

**Changed: the game** (Team Create place)
- `AnimationController`: behind high cover with a two-handed gun, blind fire plays the two-handed clips. Where they can't load (live servers, until they're published) it plays the one-handed ones, as before. Reversals between the runs still dip into the hold (their names start `BlindFireHighMove`).
- `AnimationConfig`: the four slots (113 slots now), no published ids yet.
- `TestHarness` (Studio only, and the repo's copy): names clips by their published ids too.

**Tested** (Studio play mode, 83tg's avatar, the HighWall)
| Test | Result |
|---|---|
| AK-47, FAL and M107: raise and fire mid-wall, slide to each end and hold, reverse, lower | nothing in the wall (0.05, the guard's slack, for 2 physics frames on a reversal); the support hand on the gun throughout; nothing in the head (the M107's 1.09-tall box up to 0.23, its scope under the chin) |
| The muzzle at the ends | 1.9 past either end |
| Output log | clean |

**Not done**
- Publishing the four clips (83tg): until then live servers play the one-handed clips with long guns, as before.

## 2026-11-10: Blind fire while sliding along high cover, and bullet time slows its activator
Later in session 6 (this PC, Studio signed in as 83tg). It did to-do 4.25, and checked bullet time against [[Last Stand and Bullet Time]] after a play test where the player moved freely in their own bullet time.
- Two new clips (102 clips now). Four scripts changed in the Team Create place.
- Details and numbers: [[Animation and MP3 Systems - Progress and To Do]] (session 6, parts 8 and 9).

**Added: blind fire on the high cover run** (`mp_hands.blind_fire_move`, `RUN_FIRE`; to-do 4.25)
- `BlindFireHighMoveLeft/Right`, made on the high cover run that goes that way. The gun arm points straight out ahead along the wall, about shoulder height, the barrel level, the head looking along it. Going right the arm is on the open side; going left it's on the wall side, the chest turned a little so the gun shoulder leads, the gun in front of the chest.
- Found by a search in Blender and checked like the low ones, with one more rule: the gun arm and gun clear of the head (the first left pose put the forearm 0.6 into it). On the default R15, over the run's cycle: nothing in the wall, the barrel within 8° of the way the body runs. The self-check in `register()` now covers both heights, and the forearm, hand and gun out of the head.

**Changed: the game** (Team Create place)
- `AnimationController`: blind fire while sliding plays the run's own clip in high cover too. The two high runs never cross-fade with each other: Roblox flips a slide's velocity in one physics frame, and cross-faded, a reversal swept the gun up to a stud into the wall (in Blender, with Roblox's blending). The old clip dips into the hold first, as the low run going right does with any other (`DIP_ANY`, `dipFor`). The dip now checks every blind fire clip still showing, not only the first it finds.
- `AnimationConfig`: the two slots (109 slots now).

**Checked: bullet time works as [[Last Stand and Bullet Time]] says**
- Whoever triggers it keeps full speed. That's the stated rule ("the activator keeps full speed unless someone else's bullet time sees them"), so moving freely in your own bullet time is expected. Everyone they can see slows to 0.3 (walking at 4.8 instead of 16), and aims at 0.35 if their own level is lower.
- Max Payne 3 differs: there the user is slowed too, less than their victims, and the slow-down chains through the victims' sight ([[Max Payne 3 Mechanics Reference]]).

**Changed: bullet time slows the player who triggers it, to 0.6** (`BulletTimeRules`, `BulletTimeService`; to-do 4.27, decided by JordanSaa the same day)
- `ACTIVATOR_SCALE` 0.6: less than the 0.3 of everyone they slow, as in Max Payne 3. A self-check keeps it between the two. Everything that reads `TimeScale` follows (walking, sprinting, fire rate, reloads, dives, vaults, the clips); the aim isn't slowed.
- Not in a Last Stand: its bubble keeps the downed player at full speed, and a bullet time started before the killing blow would otherwise slow them through the stand.

**Tested** (Studio play mode, 83tg's avatar, the HighWall and the TargetOpen dummy)
| Test | Result |
|---|---|
| High cover, sliding both ways while firing: M9, AK-47, dual M9 and Uzi | nothing in the wall; the barrel 0.99 to 1.00 along the wall the way the body runs; the new clips' arm and gun at most 0.02 into the head's box (0.09 mid-blend) |
| Reversals while firing | the velocity flips in one physics frame; the old clip dips into the hold and the new one comes up; nothing in the wall |
| Starting and stopping a slide, also from the other side | cross-fades; nothing in the wall |
| Bullet time, the player triggering it (full meter) | 5 s, the meter drained; the dummy at 0.3; the player at full speed |
| … after the change, triggered mid-sprint | the player at 0.6: sprinting 14.4, walking 9.6, back to 1 after 5 s; no movement-check strike |
| … a Last Stand during it | 0.6 until the killing blow, then 1 through the stand; the gunman at 0.3 |
| Bullet time, a dummy triggering it on the player | the player at 0.3, walking at 4.8, aim penalty 0.35; over after 5 s |
| … the player counter-activating at the same level | the aim penalty cleared; both at 0.3 while in sight of each other; both back to 1 behind the pillar |
| Output log | clean |

**Not fixed**
- Bullet time doesn't chain through the victims' sight, as Max Payne 3's does.
- 4.26 (rifles in high cover blind fire) is open. The AK-47 rests on the wall (0.05) in the still clips, held off by the arm guard, and is clear while sliding.

## 2026-11-10: Carried guns over vaults, and vaults on the run
Session 6 went on into 2026-11-10 (this PC, Studio signed in as 83tg). It did to-do 4.23, found and fixed running vaults being refused, and re-measured 4.24, 4.5 and 4.15. Two scripts changed in the Team Create place.
- Details and numbers: [[Animation and MP3 Systems - Progress and To Do]] (session 6, parts 5 to 7).

**Fixed: the arm guard checks where the body will be drawn** (`AimLayer`; to-do 4.23)
- The carried AK went 0.29 to 0.33 into the wall's top edge at every vault's take-off. The guard runs before the physics step and cleared the arm for where the body stood, then physics moved the body on by its velocity (0.3 at take-off speed) before the frame was drawn.
- It now tests against where the body will be: the root's velocity times the larger of the physics step and the render step (a vault places the root by the render step).
- The AK now rests on the top edge (0.05, the guard's slack) through standing, running and sprinting vaults. A vault carry clip was tried in Blender and dropped: no one pose blends cleanly from the four carries a vault can start from.

**Fixed: running vaults refused by the server** (`VaultRules`)
- A vault started at a run was refused (`NoVault`) after 3 frames, and the body dropped onto the top of the wall. The server checks from its own copy of the character, which lagged about 0.25 s: still 6.9 from the wall and not yet moving.
- `SERVER_SLACK` 2.5 → 7.5 (a sprint's lag). The client never vaults from further than `REACH` (3.6); the server still checks the obstacle's height, depth, far side and landing room.

**Tested** (Studio play mode, 83tg's avatar, the LowWall and the HighWall, AK carried)
| Test | Result |
|---|---|
| Standing, running (16), sprinting (24) vaults | accepted; the AK 0.05 on the top edge |
| Vault out of low cover | the AK clear when drawn; 0.20 for one frame after physics in the take-off turn (4.15) |
| Low cover blind fire slides (regression) | nothing in the wall |
| High cover, stepping out and back, both ends (4.24) | no upper arm in the wall (it went 0.43 in with the old pose); forearm 0.09, everything else ≤ 0.08 |
| Output log | clean |

**Not fixed**
- The vault's free left hand stops 0.07 to 0.11 short of the top (4.5); a sprint vault pressed late touches the face with the stride for one frame (4.5); vaulting out of low cover still puts a foot 0.64 in the wall for 1 to 2 frames (4.15).

## 2026-11-09: Blind fire while sliding along low cover
Session 6 ran on this PC (Studio signed in as 83tg), 2026-11-09, with Claude Code driving Blender headless and Studio. It did to-do 4.19, which JordanSaa decided the same day (keep the slide, make new clips), and found two faults on the way (4.25, 4.26).
- Blind firing while sliding along low cover played the still clips, whose waist twist is made for hips facing out from the wall. On the run the hips face the way it goes, so the chest turned the wrong way and the gun swung 2.7 out from the wall, pointing back along it.
- Two new clips (100 clips now). Two scripts changed in the Team Create place.
- Details and numbers: [[Animation and MP3 Systems - Progress and To Do]] (session 6).

**Added: blind fire on the run** (`mp_hands.blind_fire_move`, `RUN_FIRE`)
- `BlindFireLowMoveLeft/Right`, made on the low cover run that goes that way. The chest comes partly out of the run's fold and leans the gun shoulder up, the arm goes straight up, and the gun points across the wall as high as the still clip holds it. The head stays ducked under the raised arm, looking down ahead along the wall.
  - Going left the gun arm is on the wall side: the chest turns toward the wall.
  - Going right it is on the open side: the chest rolls onto its left side, gun shoulder on top, facing out.
- Found by a search in Blender, scored on the run's whole cycle and on the blends into the clips. On the default R15: the gun 0.37 to 0.38 over a 3.6 top, the head's box no higher than the still clip's (3.31 over the floor), nothing in the wall, the gap held; dual pistols, the carried AK and a rifle out of the wall too. A self-check in `register()` stops the export otherwise.

**Changed: the game** (Team Create place)
- `AnimationController`:
  - The body layer records which way the body runs along cover each frame. Hidden in low cover and sliding, blind fire plays the run's own clip, picked the same frame as the run, so the two blend in step.
  - The run going right never cross-fades with another blind fire clip (`DIP_CLIP`): the clip being left goes down into the cover hold at `DIP_FADE` (50 per second), then the new one comes up.
- `AnimationConfig`: the two slots (107 slots now).

**Why the dip**
- Roblox blends tracks joint by joint, weight-normalised, the short way round (measured in Studio).
- Going right, the chest is turned about 150° from the still clip's, so the gun arm is too: the shoulder ended 170° from the still clip's. Near a half turn the way round flipped with the firing judder, and the gun swung round to point back along the wall for about 0.1 s at the start and end of a slide; on a reversal the head and the carried AK went into the wall. No pose keeps the gun pointing across through that blend, so the game doesn't cross-fade it. Going left the cross-fade is clean.

**Tested** (Studio play mode, 83tg's avatar, the LowWall)
| Test | Result |
|---|---|
| Sliding both ways while firing (held, and real shots) | the gun 0.52 to 0.72 over the top, pointing across; the head 0.32 to 0.45 under it; nothing in the wall; the gap unchanged |
| Starting to fire mid-slide | the gun comes up muzzle first, across in 0.12 to 0.25 s |
| Starting, stopping and five reversals while firing | nothing in the wall; the gun never points back along the wall; the head under the top |
| Dual pistols, a rifle (FAL) | the Uzi rests 0.05 on the face, the rifle 0.05 on the top (the arm guard's slack) |
| Output log | clean |

**Not fixed**
- **New, 4.25:** blind firing while sliding along high cover has 4.19's fault: the still clip turns the gun back along the wall.
- **New, 4.26:** with a rifle, high cover blind fire puts it 1.9 into the wall (the clips were made with a pistol), the support hand 0.49.
- The holstered Uzi still goes 0.35 under the floor on the low run (4.20).

## 2026-11-08: Popping up and ducking back in low cover turn the body round
Session 5 ran on this PC (Studio signed in as 83tg), 2026-11-08, with Claude Code driving Blender headless and Studio. It did to-do 4.14, ran 4.19's first test, and found two new faults on the way (the cover slide's feet, fixed, and 4.20).
- Side-on, the low cover idle faces out from the wall and the aim faces over it. Popping up and ducking back used to turn the body about 166° in the body layer's 0.2 s blend, and the feet swept through the wall's base.
- Four new clips take the turn (98 clips now). Three scripts changed in the Team Create place.
- Details and numbers: [[Animation and MP3 Systems - Progress and To Do]] (session 5).

**Added: the turn clips** (`mp_stances.cover_turn`)
- `CoverPopUpLeft/Right` (0.25 s, as long as `CoverPeek`) and `CoverDuckLeft/Right` (0.3 s). Sampled at 60 per second, not 30: they turn the body half round in a quarter second.
- **The turn:** toward the edge being worked, so the head that was looking along the wall leads it. Working right the body goes from facing out (-180°) through facing the edge (-90°) to the aim (14°), working left through 90°.
- **Popping up:** the body rises, leaves the wall and only then turns (turning in place, the side-on torso went 0.47 into the wall). The hips sway 0.6 out from the wall halfway round. The foot on the outside of the turn steps first.
- **Ducking back:** the body turns and folds over first, and goes down once the feet are round. Left to `AimLayer`'s height ease, the hips dropped halfway in 0.06 s with the feet still stepping: the knees folded forward over them and the shins went 0.3 into the floor.
- **The game's height ease is built in:** the game changes the hip height at once, and `AimLayer` holds the body where it was and eases it to the new height (10 per second). The clips plant the feet where that hold leaves the floor, so they stay on it.
- **Knees:** they turn with the feet, from the way they bend in the pose the clip starts on to the way they bend in the one it ends on, so each clip starts and ends on its neighbours' legs. Where a knee, or a gun holstered on the left thigh, would reach past the wall's face, the knee turns out from the wall, no further than it needs.
- **`CoverAim`:** the back heel is up (22°). Flatter, the shin leant over the foot and its box went 0.12 into the floor.

**Changed: the game** (Team Create place)
- `AnimationController`:
  - Low cover to `CoverPeek` plays `CoverPopUp<side>`, bound to the stance. `CoverPeek` or `CoverAim` back to low cover plays `CoverDuck<side>`. They play in real time, as the height ease does (bullet time doesn't slow them), and take the body over at 25 per second (`TURN_FADE`).
  - For the first 0.15 s of a pop-up (`POP_AIM`) the gun stays in the low cover hold. Raised at once it went through the wall's top; at 0.1 s it still went 0.5 into the wall's face working left, where the turn takes the gun shoulder past the wall.
  - Other players' characters use the right-hand clips, as their cover idles already do.
- `AnimationConfig`: the four slots (105 slots now).
- `AimLayer`: the foot guard (the body lifts so no foot is under the floor) now runs in every cover stance, not only while a height change eases. Sliding along low cover, the idle blends into the run a quarter turn round, and the feet went 0.36 under the floor.

**Tested** (Studio play mode, 83tg's avatar, the LowWall)
| Test | Result |
|---|---|
| Pop up and duck back, working right and left | the clips play on the stance changes. A shin 0.08 under the floor for one frame at most (0.22 with the clips' first version); feet 0.05; no leg in the wall |
| The gun coming up while popping up | working left, the gun 0.05 in the wall's face for a few frames (0.59 with `POP_AIM` at 0.1); aiming over the top, the forearm rests on it (0.05), as before |
| Sliding along low cover, start and stop | feet 0.05 under the floor (0.36 before the guard ran in cover); shins, thighs and holstered gun still go 0.33 under (4.20) |
| Blind fire while sliding along low cover (4.19, first test) | nothing in the wall, but on the run the gun is 2.7 out from the wall pointing back along it |
| Camera | largest step 0.08 |
| Output log | clean (client and server) |

**Not fixed**
- **New, 4.20:** the crouch walk and the low cover run fold the trailing leg so low that the knee is 0.19 above the floor: the shin's box goes 0.44 to 0.47 under it, the thigh's 0.26, a holstered gun's 0.34 (default R15; 0.33 in game). Tried in Blender: the push-off heel, the knees turned out, shorter strides, the feet further forward: no better than 0.35. Hips 0.2 to 0.3 higher with short strides: 0.16 to 0.3, the head 0.2 to 0.33 higher.
- At the start of ducking back working right, the holstered gun is 0.14 in the wall for 2 frames while the clip blends in over the aim. The right upper arm rests on the wall's top edge (0.08) as the aim lowers.
- **4.19, tested:** blind firing while sliding along low cover turns the chest the wrong way (the clip twists the waist for the idle's hips, which face out; the run's face along the wall). Needs a call: stop the slide while blind firing, or blind fire clips made on the run.

## 2026-11-07: Side-on cover, as Max Payne 3 does it
Session 4 ran on this PC (Studio signed in as 83tg), 2026-11-07 from 19:26 (UK time), with Claude Code driving Blender headless and Studio. Studio had updated itself at 19:18 and dropped Claude Code's Studio connection, so the session drove Studio's own `StudioMCP.exe` directly (see "How to resume" in [[Animation and MP3 Systems - Progress and To Do]]).
- The three open decisions in the to-do were made: the game's code stays out of git, the test harness goes into the repo, and cover goes side-on, high and low, like Max Payne 3.
- 24 cover clips were remade in Blender and one added (94 clips now). Five scripts changed in the Team Create place, two of them only in comments.
- Everything was measured in Studio play mode, frame by frame, on 83tg's avatar (a slim R15: torso 1.4 studs wide where the default is 1.94, root 3.13 above the floor).
- Details, numbers and what's left: [[Animation and MP3 Systems - Progress and To Do]] (session 4).

**What Max Payne 3 does** (frames from the Steam trailers, studied at 2 to 4 fps; nothing stored in the repo)
- *Design and Tech Video 2*, 2:53–2:54: Max runs to a tall cabinet and puts his **back flat against it**, facing out, SMG low in the right hand, the left hand up by his face, head turned toward the edge.
- Same video, 2:56–2:57: behind a low counter he **crouches with his back against it**, knees up, gun up by his shoulder, head turned to the edge. Popping up, he turns round to face over it.
- *Multiplayer* trailer, 1:35–1:36: players stand with their **back to a wall at its edge**, pistol low, head turned along the wall. 1:43: a rifle held **upright beside the face**.
- The official screenshot `ss_4ae054ce…` (see [[Reference Images]]): back to the wall beside a window, the pistol low in both hands, head turned to the window.
- So "side-on" here is Max's version: back and inner shoulder on the wall, the body turned toward the edge being worked, the head looking along the wall to it. Moving along the wall, the body runs side-on, facing the way it goes.

**Changed: the cover clips** (`mp_stances.py`, `mp_hands.py`, `mp_arms.py`)
- **How they fit the game:** the game keeps the root part facing the wall, and keeps the gap the body's reach toward the wall needs (`CoverController.bodyReach`). So the clips turn the body round inside the root part and lean it back until the head, torso and upper arms reach 1.1 toward the wall: the gap comes out at 1.15 and the back rests on the wall. No gameplay code depends on which way the body faces.
- **High cover idle** (`CoverHighLeft/Right`): turned 150° from facing the wall, so the back and inner shoulder are on it, knees soft, feet out from the wall, the head turned along the wall to the edge.
- **Low cover idle** (`CoverLowLeft/Right`): a deep squat on the balls of the feet, back against the wall, folded over the knees. The head is aimed along the wall to the edge with a look-at, since a neck turn on a folded body rolls the head instead. Head top 2.80 above the floor on the default R15, so it's under even the lowest (3-stud) cover. The old pose's was 3.22, and 3.49 in game.
- **Moving along cover** (`Cover…Move…`): side-on, facing the way it goes. High is a hunched jog at 9.6 studs/s; low is a crouched run at 8 studs/s, folded at the waist to keep the head under 3 studs. Folding at the hips put the trailing shin through the floor.
- **Corners** (`CoverCorner…`): from the idle, a side-on stride round the corner, and back to the idle.
- **Wall ends:** the root stops 0.9 short of an end (`EDGE_MARGIN`), and an R15's shoulders reach further than that along the wall. So the idles sit back along the wall, away from the edge: 0.35 (high) and 0.75 (low). The runs sit back so the head leads the root by no more than 0.8 (high) and 1 (low).
- **Holds while hidden:**
  - High: `CoverHoldHighOne` (the pistol low in front of the belly, muzzle down, as in the screenshot), `CoverHoldHighTwo` (the rifle upright across the chest, muzzle up and to the left, its top 4.5 above the floor, under the 5.2 wall) and `CoverHoldHighDual` (both pistols up in front of the chest).
  - Low: `CoverHoldLowOne` and `CoverHoldLowDual` (the gun up beside the face), and `CoverHoldLowTwoLeft/Right` (the rifle upright past the face, leaning away from the edge the head looks to).
  - The guns are placed in a body part's frame and aimed in the body's facing frame, so one clip fits both sides.
- **Blind fire:**
  - **Low** (`BlindFireLowLeft/Right`, now keys the waist and neck): the hips stay against the wall and the chest twists 105° to put the gun shoulder to it. The arm goes straight up, and the gun goes over the top, the head ducked and facing away.
    - With the back to the wall the arm can't reach over: folded to keep the head down, the shoulders are 2 studs out from the wall, and upright the head is above it.
    - The hand stays in front of the wall's face. With the hand over the wall, the forearm cut 1.2 into the top edge of the 2-stud-thick LowWall.
  - **High** (`BlindFireHigh…`, now keys the waist and neck): the gun arm out along the wall and the gun turned round the edge, the head looking along the wall, not round it.
    - Working right, the gun arm is on the side away from the edge (back to the wall), so the chest leans out and toward the edge and the arm reaches across.
- **Carried rifle:** `CarryTwoHandedCover` now hangs the rifle muzzle down in front of the left thigh, off the wall on either side. The new `CarryTwoHandedCoverLow` holds it by the knee, muzzle forward and down, away from the wall. `CarryTwoHandedLow` is now only for crouching and getting up.

**Changed: the game** (Team Create place)
- `AimLayer`:
  - The head no longer looks at the aim while hidden in cover. The aim is past the wall, behind the turned head, and would wring the neck round. It eases on and off at 8 per second (`gaze`).
  - The momentum lean is worked out in the hips' frame. In the root part's frame it went the wrong way once the body turned round, and it was 45 to 50° off on strafes too.
- `AnimationController.carryFor`: low cover uses `CarryTwoHandedCoverLow`.
- `AnimationConfig`: the new slot, and the cover comments.
- `CoverController`, `CoverRules`: comments only (no more "hunched").

**Found in the place** (done after the 2026-11-03 notes, without notes or commits; found reading the code)
- `AimLayer.guardArm` keeps each arm, its gun and the carried gun out of walls (to-do 4.2 and 4.7).
- The dive landing is held and eased like a crouch, so the root no longer falls 2.4 and bounces (`DodgeGround` left `FALLS`; 4.3). The foot guard now lifts up to 1.2.
- `VaultRules.LEG_CLEARANCE` is 0.3 (4.4).
- `AnimationController.watchReloads` runs the reload markers on other players' guns (4.13). A reload cut short puts the gun back to rest, and every clip is loaded at spawn so the first vault isn't unstretched.
- `CoverController.bodyReach` counts the upper arms below the cover's top. The high-cover step out is capped at what lands on the spot by the next frame.
- `ServerStorage.Tools.TestHarness`: a 733-line play-test harness. `ServerStorage.Tools.AnimationImporter` was rewritten as a module.
- A large block, `Workspace.Part` (4 × 18 × 18 at x 32, z 47), stands between the spawn and the arena.

**Added: repo**
- `Tools/TestHarness.luau`: the place's harness (to-do decision 2). How to install and use it is in the file's header and in [[Test Arena]].
- `Assets/Blender/Animation/studio_import.luau` now matches the place's `AnimationImporter`.
- 94 clips in `Exports/keyframes.json` and in `MaximumPain_Animations.blend`. Only the 24 cover clips changed, plus the new one; the other 69 are byte-identical.

**Decisions**
- The game's code stays out of git: the repo is public (JordanSaa's call, to-do 1).
- Cover is side-on as Max Payne 3 has it: back and inner shoulder to the wall, turned to the edge (to-do 3). Moving is side-on, facing the way it goes.
- The body is turned inside the root part, not the root part itself, so cover detection, the gap, edges, peeking, the server's checks and the virtual muzzle all stay as they were.
- The wall ends are handled in the clips (sitting back from the edge), not by widening `EDGE_MARGIN`. A wider margin would change where peeking and blind fire work.

**Tested** (Studio play mode, 83tg's avatar)
| Test | Result |
|---|---|
| Low cover, settled | head top 2.77, 0.83 under the 3.6 wall (3.49 before); root 1.21 off the wall; nothing in the wall or the floor |
| Low cover at the wall's ends | head 0.47 inside the end; the edge-side upper arm 0.33 past it (0.73 before the idle sat back) |
| Low cover, the run stopping at an end | head 0.21 past the end while the run blends out (0.64 before) |
| High cover at the wall's ends | head 0.39 inside; arm 0.29, legs 0.15, holstered Uzi 0.47 past (head 0.84 and arm 0.96 past before the idle sat back) |
| Blind fire over the LowWall | head 0.34 under the top, gun 0.11 over it (0.39 on the default R15); nothing in the wall; gap held at 1.21 |
| Blind fire round the HighWall's ends | working left: gun 1.07 past the end, round the corner; working right: just past the corner, the body leaning out |
| Popping up and out, ducking back | right clips; aiming over the wall the forearm only rests on the top (0.05); ducking back into high cover the gun is 0.22 in the wall for 3 frames |
| Corner swings round CrateA | nothing in the crate |
| Vault out of low cover | flies clear; see Not fixed |
| Camera | largest step 0.08 |
| Output log | clean |

**Not fixed** (in the to-do as 4.14 to 4.19)
- Popping up and ducking back in low cover turn the body round in a 0.2 s blend. A foot goes up to 0.43 into the wall's base, and the gun arm 1.2 into the top for the first frame. A turn clip for each would fix it.
- Vaulting out of low cover: for one frame a foot is 0.74 inside the wall as the body turns.
- At an inside corner the root turns 90° in one frame, and the run's body (up to 1.8 off the root) swings with it. Sliding round CrateA into the next crate, it went 1.1 into CrateA for about 3 frames.
- Blind fire working right reaches only just past the corner.
- Not tested: two players, other avatars in game, firing while sliding along low cover.

## 2026-11-04: Polish pass: height changes, arms against walls, the dive landing, vaults, others' reloads
Session 4 ran on JackT6785's PC, with Claude Code driving Studio. (It ran in parallel with the 2026-11-07 session below it in the list, which also called itself session 4; the two were merged on 2026-11-08 and this entry put back on 2026-11-09, after the merge had dropped it.) It worked through the to-do list in order and measured every change in Studio play mode on JackT6785's avatar.
- **Measured what is drawn.** A new test harness (`Tools/TestHarness.luau`, in the repo and the place) records each frame at the end of the render step, which is what the player sees, as well as after physics. Session 3 logged only after physics, so it couldn't see the first fault below. Clearances and depths are exact box-against-box results.
- **Low frame rate.** Studio in the background draws about 15 frames a second while physics runs at 60, so render-step code (camera, stances, movers, clip weights) runs in 66 ms steps. Several faults below only showed at that rate, but each would also hit players on slow machines, so each was fixed rather than put down to the test.
- 9 scripts changed and one was added, all in the Team Create place. The notes and the harness changed in the repo.
- Every measurement and the code details are in [[Animation and MP3 Systems - Progress and To Do]] (session 4).

**Fixed: height changes drawn a frame early** (`CharacterController`, `CameraController`, `ProceduralLayer`)
- **The whole body was drawn a stance's height out for one frame** on every crouch, stand, cover entry or exit, pop-up and get-up: crouching, the feet were 1.80 into the floor; standing, 1.89 above it.
  - Cause: the root moved at once (on the key press or in the render step), but the aim layer's hold only came before the next physics step, after that frame was drawn.
  - Fix: the hip height and the root change together just before physics. `moveRoot` is the first procedural layer, run right before the aim layer holds the body. The humanoid keeps its old hip height until then: it checks its floor between the render step and physics, and told the new height first it lost the floor and fell.
  - Result: no frame is drawn out of place, and the humanoid stays in Running.
- **The camera jumped on every height change:** 0.87 crouching, 0.88 standing, 0.87 popping up from low cover at 15 fps (about 0.3 at 60).
  - Cause: the camera watched `HipHeight` itself and heard of the root's move separately. Part of one eased away before the other arrived.
  - Fix: `CameraController.absorbHeight(rise, drop)` receives both at once from `moveRoot`, between two camera frames.
  - Result: the largest step is 0.22 (the ease itself).

**Fixed: the dive's landing** (`CharacterController`, `AimLayer`; to-do 4.3)
- **The body fell the last 2.4 studs onto the floor at up to 31 studs/s and bounced.** The camera dropped 1.38 in one frame.
  - Cause: in the flight the hip height is the standing one, so the humanoid caught the root at standing height. Then DodgeGround dropped the hips 2.2 with nothing moving the root.
  - Fix: DodgeGround left `AIRBORNE` and `FALLS`. The landing puts the root on the floor at once (measured from the floor) and the aim layer eases the body down, like a crouch.
  - Result: no fall, no bounce, the humanoid stays in Running, and the camera step is 0.35. No forearm or hand went more than 0.05 under the floor (session 3's 0.30 forearm dip didn't occur).

**Fixed: arms and guns in walls** (`AimLayer`, `AnimationController`, `CoverController`; to-do 4.2)
- **Popping up from low cover** the gun went 0.73 into the wall; **ducking back** 0.56.
- **Holding aim in high cover away from an edge** played the aim clip anyway (the pop-out is refused there) and raised the gun 0.67 into the wall. The arms now keep the cover hold, as the camera already did.
- **Behind high cover the leading arm was in the wall at rest.** The body turns toward the side worked: at the east end the right upper arm was 0.55 in, the hand 0.45 and the M9 0.11. On the right side the carried AK's upper arm was 0.32 in.
- **Stepping out of high cover** the M9 went 1.00 into the wall's corner and the forearm 0.85.
- Fixes:
  - **Arm guard** in the aim layer: after everything else has posed the arms, any arm whose boxes (upper arm, forearm, hand, gun) overlap a wall is turned at the shoulder by the smallest angle that clears it. There are three ways out: *lift* (toward upright: an aimed gun comes up as from a high ready, shrinking to nothing as the body rises), *swing* (straight out of what it went into: a hanging arm, the carried gun) and *yaw* (flared out about the vertical: the bent hold arm, whose elbow and gun move opposite ways under the other turns). A turn is at most 60°, or 30° with the upper arm in the wall. A way, once taken, is kept while it works, so the arm doesn't flick.
  - **High cover keeps room for the shoulders:** the gap is the body's reach including the upper arms (below the cover's top and not while firing, so blind fire and aiming over low cover don't push the body back). On JackT6785's avatar that's 1.52 to 1.78 instead of 1.15.
  - **No aim clip while hidden in cover** (`AnimationController.ready`).
- Result: popping up and ducking back ≤ 0.05 (the box slack); high cover at rest, nothing in the wall; stepping out, clear, and stepping back a 0.1 s brush (M9 0.20). Low cover's gap is unchanged (2.52).
- **The step out of high cover overshot back and forth** (0.5 studs each frame at 15 fps, 0.33 at 30): it walked at full speed until within 0.2 of the spot. It now walks no faster than reaches the spot by the next frame, and bullet time slows it like any walk.

**Fixed: vaults** (`VaultController`, `AnimationController`, `VaultRules`; to-do 4.4, part of 4.5)
- **The path wasn't followed between frames.** Between two placements of the root, gravity sagged it up to 0.47 below the path over the top, and the velocity carried on from the last frame threw it 0.7 above the path at take-off. Both shrink at 60 fps but not to nothing.
  - Fix: gravity is cancelled for the vault (a `VectorForce` the character's weight), and physics is aimed at where the path will be by the next frame. The root runs along the path's chords at any frame rate. The landing cap isn't needed any more.
- **The clip lagged the path at take-off,** so the legs still hung when they reached the obstacle. Three causes:
  - A track reads a length of 0 until its animation has loaded, so the first vault of a life (and the first reload or draw) played its first frames unstretched. Every clip is now loaded when the character is set up.
  - A stopped track keeps its old time (the last vault's end), but `Play()` starts it from 0. The chase used the old time and left the clip frozen on its first frame for a frame.
  - The root was placed a frame ahead of the clip. It now starts exactly at the start, and the clip chases the place the root is aimed at.
- **The margin:** in slow motion the far edge was cleared by nothing (−0.05). `LEG_CLEARANCE` 0.2 → 0.3 lifts the arc 0.1 for longer-legged avatars; a standard avatar still flies 2.1 above the top.
- Result: from 2.5 back, +0.19 over the LowWall with no contact (was −0.12 to −0.56 at take-off); from 2.09 back, the near face is touched by 0.02 (was 0.23); out of low cover +0.26; no Fall clip, no bounce, the feet at 0.00 after landing.

**Fixed: other players' reloads** (`AnimationController`; to-do 4.13)
- Reload markers fired only on the reloading player's client, and gun parts moved there don't replicate, so others saw the clip but no magazine or bolt move. Each client now runs the markers itself on everyone else's reload tracks, found by their animation id.
- **A reload cut short left the magazine hidden** until the next reload, for the owner too. A reload track that stops now puts the gun back at rest.
- Tested on one client: a reload played on the gunman by another script moved its AK's magazine and bolt, and one stopped after MagOut brought the magazine back. The owner's own reload is unchanged (M9 12 → 15 rounds). Seeing it from a second player needs the two-client test, with published animation ids (see Not done).

**Fixed: a big drop at a low frame rate** (`AimLayer`)
- Dropping into a Last Stand (2.2) at 15 fps sank the feet 0.47: the clips' weights change once a drawn frame while the body's hold eases every physics step, so the straight legs sank further than the foot guard's 0.6 lift. `MAX_FOOT_LIFT` 0.6 → 1.2. Result: −0.05.

**Changed**
- **High cover:** the character stands 1.5 to 1.8 studs off the wall (its reach with the upper arms) instead of 1.15.
- **Arms** are turned at the shoulder to stay out of walls, held and carried guns included.
- **The dive's landing** is eased onto the floor instead of falling the last 2.4 studs.
- **Hidden in cover**, holding aim where you can't pop out keeps the gun in the cover hold.
- **Vaults** fly 0.1 higher for avatars taller than standard.

**Added**
- **Code:**
  - `CharacterController.moveRoot` (a procedural layer).
  - `CameraController.absorbHeight`.
  - `AimLayer`'s arm guard (`guardArm`, `GUARD_LIMIT` 60°, `GUARD_SHOULDER_LIMIT` 30°, `GUARD_SLACK` 0.05).
  - `AnimationController`'s `wireMarkers`, `restGun` and `watchReloads`.
  - `CoverController`'s `stepToward`.
- **Tools:** `ServerStorage.Tools.TestHarness`, also `Tools/TestHarness.luau` in the repo. It records play tests and reports floor and wall clearances, penetrations, camera steps, clips and the stance timeline, and it can walk the character and point a debug camera. Install steps are in its header.

**Removed**
- `CameraController.absorbRise` and its own `HipHeight` watching (replaced by `absorbHeight`).
- The vault's landing speed cap (the path's chords can't overshoot).

**Decisions**
- **Low cover pose: keep the hunched pose facing the wall** (JackT6785, 2026-11-04; to-do 3). Replaced on 2026-11-07 by side-on cover (see that entry).
- The two-client test waits: the Studio connection can't reach the test windows, so it has to be run by hand.
- What is drawn is the measure. Tests are checked at the end of the render step, and every timing fix has to hold at a low frame rate.

**Tested** (Studio play mode, JackT6785's avatar, drawn at about 15 fps; before → after)
| Test | Result |
|---|---|
| Crouch and stand | first drawn frame: feet −1.80 / +1.89 → in place; camera step 0.87 → 0.22; humanoid stays Running |
| Low cover pop-up and back | gun 0.73 / 0.56 into the wall → 0.05; camera 0.87 → 0.22; gap 2.52 (unchanged) |
| High cover, aim held mid-wall | gun 0.67 into the wall → stays in the cover hold |
| High cover at rest | right arm 0.55 (east end), AK's arm 0.32 (right side) → nothing in the wall; gap 1.78 / 1.52 |
| High cover step out and back | M9 1.00, forearm 0.85 → clear out; 0.1 s brush back (0.20); no overshoot |
| Dive landing | fell 2.4 at 31 studs/s and bounced, camera −1.38 → put on the floor, eased; camera 0.35; hands ≥ −0.02 |
| Vault from standing (2.5 / 2.09 back) | legs −0.12…−0.56 at take-off → +0.19 crossing, no contact / 0.02 |
| Vault out of low cover | +0.26 over the top; no Fall clip; feet 0.00 after |
| Vault in bullet time (0.3) | 1.52 s in the air; tightest −0.05 at the far edge → `LEG_CLEARANCE` 0.3 |
| Last Stand (survived) | drop: feet −0.47 → −0.05, camera 0.12; wakeup and stand ≥ −0.05, camera ≤ 0.14; painkillers 3 → 2 |
| Dive get-up, first reload of a life | feet ≥ −0.05; the reload stretched from its first frame (1.6 s clip known) |
| Others' reloads (one client) | magazine and bolt moved by a reload this client didn't start; cut short, the magazine came back |
| Output log | clean |

**Scripts changed** (in the Team Create place; not in git)
| Script | Change |
|---|---|
| `CharacterController` | `moveRoot`: hip height and root change together before physics; DodgeGround out of `AIRBORNE` |
| `CameraController` | `absorbHeight` replaces `absorbRise` and the `HipHeight` watching |
| `AimLayer` | arm guard; DodgeGround out of `FALLS`; `MAX_FOOT_LIFT` 1.2 |
| `AnimationController` | no aim clip in hidden cover; every clip preloaded; the vault clip's chase; markers for everyone else's reloads; guns back at rest when a reload stops |
| `CoverController` | upper arms in the reach (below the top, not while firing); `stepToward` |
| `VaultController` | gravity cancelled; the root placed then aimed at the next frame's place; landing momentum from the path |
| `VaultRules` | `LEG_CLEARANCE` 0.3; self-check tolerant of rounding |
| `ProceduralLayer`, `ClientMain` | comments: the root move is the first procedural layer |
| `ServerStorage.Tools.TestHarness` | new (test tool, never sent to players) |

**Repo:** `Tools/TestHarness.luau` and these notes, `48ee647` (pushed; merged in `85d5b61`).

**Not done**
- **Saving the place** after these changes (File > Save to Roblox).
- **The two-client test.** A finding for it: Studio's temporary clip ids (`KeyframeSequenceProvider`) differ from one process to another (the server's and a client's id for the same clip didn't match). So in a Studio two-player test, one player can't see the other's clips or reload markers. With published ids, as in live servers, they match.
- Polish still open: 4.5 (the hand on the top, a vault from idle), 4.6, 4.8 (not tried with the M107), 4.9, 4.10, 4.11, 4.12, and what this pass found: arms against walls when hugging a wall in the open, the carried AK brushing the top in a vault, a 0.2 s high-cover brush after stepping back. Details in the to-do (now 4.21 to 4.24).

## 2026-11-02: Play tests, the fixes they needed, and the Blender export
Session 3 ran on JackT6785's PC, with Claude Code driving Studio: 2026-11-02 20:58 to 22:20, then 2026-11-03 01:51 to 02:00 (UK time).
- Every play test left on the to-do list was run in Studio play mode on JackT6785's R15 avatar, and measured frame by frame: each body part's box, the root, the camera and each clip's weight.
- Every fault found was fixed and measured again.
- 13 scripts changed, all in the Team Create place. The Blender export and the notes changed in the repo.
- The per-gun reload table, every measurement and the code details are in [[Animation and MP3 Systems - Progress and To Do]] (session 3).

**Fixed: vaults** (`AnimationController`, `VaultRules`, `VaultController`, `CameraController`)
- **The legs went into the top of the obstacle:** 0.19 into the LowWall, 0.31 into a crate.
  - Cause: when the leading foot reached the near face, the Vault clip had only blended in to 0.78. The standing clips' straight legs still pulled the feet down.
  - Fix: the Vault clip blends in at 30 per second (`VAULT_FADE`) instead of the body layer's 10, so it is at 0.99 by the near face. The arc also rises with the avatar's legs (see Changed).
  - Result:
    - The lowest point over the top is +0.23 over the LowWall and +0.16 over a crate.
    - Out of low cover the left hand rests on the top (0.00).
    - In slow motion the tightest point is +0.06, at the front edge.
- **Every landing played the Fall clip** for about 0.2 s (weight 0.16).
  - Cause: a finished vault handed the humanoid back in Freefall, which plays Fall until it finds the floor.
  - Fix: `VaultController.release(landed)` puts it straight into Running. Only a vault cut short falls.
- **Landings bounced 0.2** once the arc was higher.
  - Cause: the speed handed to physics in the last frames carried the root below the landing, so the feet hit the floor and the body sprang up.
  - Fix: on the way down the vault caps that speed, so one physics step ends at the landing height.
- **The camera jumped 2 to 4 studs in a tenth of a second:** 1.17 in one frame at take-off, and −1.35 then +2.15 out of low cover.
  - Cause: the view followed the hop rigidly.
  - Fix: new `CameraController.setVerticalLag(share)`. While vaulting (`CAMERA_LAG` 0.5), the view takes half of each rise and fall at once and eases into the rest. An earlier try fed each step of the path to the camera; landings juddered, so it was dropped.
  - Result: largest step 0.6 to 0.8 (0.22 in bullet time).

**Fixed: height changes** (`CameraController`, `CharacterController`, `AimLayer`)
- **The camera popped when the hips moved without the root jumping:** out of low cover into a vault (above), and +1.68 on a dive's landing.
  - Cause: the camera only held its height back when `CharacterController` reported moving the root.
  - Fix: the camera watches the hip height itself every frame, whoever changed it. It holds 75% of each change (`CROUCH_CAMERA_KEEP`) and eases it out at 10 per second. `absorbRise` now only reports the root jumping.
- **Stances the server forces moved the body by physics.** Dropping into a Last Stand was a 2.2-stud free fall, with the feet 0.74 under the floor and a 1.77 camera pop. A timed get-up rose over 8 frames.
  - Cause: for a Last Stand, a wakeup and a timed get-up, the server's HipHeight reaches the client before the stance does. The client saw no change and never moved the root.
  - Fix: `CharacterController` compares with the hip height it last put the root at (`appliedHip`). It moves the root to the new height over the floor in the same frame, or only the rest of the way if physics already moved it.
  - Result: the drop is instant, the feet are at −0.05 and the largest camera step is 0.20.
- **A dive's launch pushed the feet 0.39 into the floor** for four frames.
  - Cause: the aim layer held the body at the run-up's lower height while the launch carried the root up.
  - Fix: `DodgeAir` and `Dead` count as real moves of the root in `AimLayer`; its `FALLS` now matches `CharacterController`'s `AIRBORNE`.
  - Result: +0.21.
- **The feet dipped into the floor while a height change eased out:** 0.11 crouching, 0.14 to 0.30 standing up, 0.33 into a Last Stand (to-do 4.1).
  - Cause: the clips bend and straighten the legs at their own pace, not the body's.
  - Fix: a foot guard in `AimLayer`. For 1 s after a height change, the body is lifted just enough that neither foot's box is more than 0.05 under the floor beneath it (one ray per foot, at most 0.6).
  - Result: within 0.05 in every case.

**Fixed: guns** (`WeaponEffects`, `AnimationController`, `WeaponController`, `AimLayer`, `ProceduralLayer`, `HitReactions`)
- **Slides and bolts stayed racked back after reloads** (FAL, M4, Desert Eagle).
  - Cause: the marker that sends them home fired on time, but the part's resting pose had been lost.
    - Resting poses were kept in a weak-keyed table (`__mode = "k"`) keyed by the guns' Motor6Ds.
    - The engine can drop an instance's Lua handle while the instance still exists, so entries vanish at random. This was reproduced: a key vanished after one garbage collection while the motor was still in the gun.
  - Fix: the resting pose is stored on the motor (`RestC0` attribute) and read through `WeaponEffects.restPose`, shared by the reload markers and the firing kick.
- **The same pattern was removed everywhere:** 10 tables in six controllers. Each is now a plain table, emptied when its instance leaves the game:
  - `WeaponEffects`: the kick's resting poses. If an entry was lost while a part was kicked back, the next shot took the kicked pose as the rest.
  - `WeaponEffects`: the muzzle effects. Each lost entry added another shadow-casting light and three particle emitters to the muzzle. They're now found by name, and the flash counter is the muzzle's `Flashes` attribute.
  - `WeaponController`: each gun's spray, bloom and predicted ammo, which restarted when lost.
  - `AimLayer`: each body's state. A lost entry reset a height change mid-move.
  - `ProceduralLayer`: the joints' base poses.
  - `HitReactions`: the flinch springs, the joint cache, and the hit log that the death push and the kill cam read.
  - Kept on purpose: `AimLayer`'s gun-box cache, where a lost entry only costs a rebuild.
- **A pistol reload moved the carried rifle's parts too.** A Desert Eagle reload dropped a spent magazine from the M4 in the left hand and moved its bolt.
  - Fix: reload markers move only the gun in the right hand, or both pistols for `ReloadDual`.
- **Result:**
  - All 13 guns and the dual reload play their clip once at full weight, with no restart.
  - Each clip is stretched to its gun's reload time, from 0.81× speed (Desert Eagle, Uzi, dual) to 1.15× (MP5).
  - Every part comes back to rest, and the ammo is right after each reload.

**Fixed: dropped guns** (`LoadoutService`)
- **For the player who dropped it, the gun hung in the air** where it left the hand.
  - Cause: the gun was still part of that player's physics (their client owns it). The server moved it in the same frame as it released it, and that move never reached them.
  - Fix: the gun is anchored and released at once, then laid down 0.1 s later (`SETTLE_DELAY`). Its `DroppedAt` time doubles as a token, so a late lay-down can't move a gun that was picked up or dropped again.
- **For everyone else, guns floated about 0.45 above the floor.**
  - Cause: `GetBoundingBox` turns with the gun, so for a gun on its side the box's "height" was a width.
  - Fix: `bottomOf` measures the real lowest point. `layDown` rolls the gun onto its side and rests it 0.03 above the highest floor under its middle and both ends.
- **Result** (server and client agree):
  - Open floor: 0.03 above the floor.
  - Against the gun table: on the floor, 0.21 short of it.
  - A swap at the rack: on the table top.

**Fixed: cover** (`CoverRules`, `CoverController`)
- **Corner swings behind low cover had stopped working** (tested on CrateA).
  - Cause: `CoverRules.outerCorner` looked for the wall's end face from the high-cover distance (1.15). Low cover keeps 2.2 to 2.8 since session 2, so its probes started in front of the wall and found nothing.
  - Fix: it now takes the character's real distance from the wall, and returns the swing's middle point as well as its target.
  - Result: holding D went round two corners of the crate in a row, with nothing inside it.
- **Ducking back from aiming over low cover lunged at the wall:** the root moved 0.57 toward it and the forearm went 0.83 into it.
  - Cause: the distance from the wall was re-measured on the upright aiming pose while it blended out.
  - Fix: `CoverController` remembers the body's deepest reach for each cover stance while in cover. It eases that back (0.5 studs/s) only when settled (0.4 s after a stance change), still, and not firing (1.5 s after a shot).
  - Result: the gap held at 2.54 through popping up and back. After a slide the body eases back to the wall (head 0.07 to 0.13 off it; it stayed 0.2 out before).

**Fixed: the Blender export** (`mp_lib.py`)
- **It crashed on Blender 5.** `mp_lib.bake` used `action.fcurves`, which Blender 5.0 removed; F-curves now sit in the action's layers, strips and channel bags. The new `_fcurves(action)` reads either layout, so older Blender versions still work.
- **Every export rewrote `keyframes.json`.** `clip_data` walked a Python set, whose order changes every run; the tracks are now sorted. Two exports are byte-identical, and the regenerated clips equal the committed ones, so Studio didn't need a re-import.

**Changed**
- **The vault's arc depends on the avatar:** `VaultRules.apexAbove(rootHeight)` = max(2.1, 0.6 × the root's standing height + 0.2). A standard avatar still flies 2.1 above the top, JackT6785's 2.23 and a tall Rthro 2.54.
- **Vault landing:** a finished vault lands straight into running, and the camera eases over the hop.
- **Reload markers** move only the gun being reloaded.
- **Dropped guns** lie on their side on the highest floor under them, about 2 studs ahead of the feet. `dropFront` checks for the gun's length ahead at shin height: the gun stops short of anything in the way, or lies across the feet when there's less than 0.6 of room.
- **Low cover:** the distance from the wall is the deepest reach of the stance since taking cover. It relaxes only when the character is settled, still and not firing.

**Added**
- **Code:**
  - `CameraController.setVerticalLag`.
  - `WeaponEffects.restPose`.
  - `VaultRules.apexAbove`, `LEG_TUCK` 0.6 and `LEG_CLEARANCE` 0.2, with self-checks.
  - A `gap` argument for `CoverRules.outerCorner`, and its returned `apex`.
  - `AimLayer`'s foot guard (`footDip`, `FOOT_SLACK` 0.05, `MAX_FOOT_LIFT` 0.6).
  - `LoadoutService.bottomOf`, `layDown` and `dropFront`.
  - `CharacterController`'s `appliedHip`.
  - `CoverController`'s `REACH_SETTLE` 0.4, `REACH_RELAX` 0.5 and `FIRED_HOLD` 1.5.
- **Attributes,** set by each client on its own copy:
  - `RestC0` on gun motors (the part's resting pose).
  - `Flashes` on muzzles (the flash counter).
- **Repo:**
  - `MaximumPain_Animations.blend`: the rig and all 93 clips as actions (1.95 MB).
  - FBX copies of every clip in `Exports/FBX` (93 files, 14.6 MB). They're kept out of git: `L.export(fbx=True)` rebuilds them in about 12 s.
- **Notes:** [[Euphoria-style Reactions and Ragdolls]], [[Max Payne 3 Kill Cam]].

**Removed**
- Ten weak-keyed tables (above).
- The "cover-to-cover moves" lines from this changelog's 2026-10-31 entry and from [[Cover System]], as the to-do asked.
- Python bytecode from git (`__pycache__/` is now ignored).

**Decisions**
- State that must survive is kept on the instance (as attributes) or in plain tables emptied when the instance leaves. It never goes in weak-keyed tables keyed by instances; only caches may stay weak.
- The camera handles every hip height change itself, instead of relying on each script that changes it.
- The server lays a dropped gun down 0.1 s after the drop, not in the drop frame.
- The FBX copies aren't committed, since they're rebuilt in seconds; the `.blend` is.
- The low-cover pose stays hunched until JackT6785 and JordanSaa decide (to-do 3).
- The commits stay local until JackT6785 pushes them, as it's JordanSaa's public repo.
- Publishing the animations is left to JordanSaa, because an experience only plays animations its owner owns. (Corrected 2026-11-10: the place's owner on Roblox is 83tg; JordanSaa is the GitHub name.)

**Tested** (Studio play mode, JackT6785's avatar; before → after)
| Test | Result |
|---|---|
| Vault over the LowWall from standing | lowest point −0.19 → +0.23; Fall clip 0.16 → 0; camera step 1.17 → 0.62 |
| Vault over a crate | −0.31 → +0.16 |
| Vault out of low cover | camera −1.35/+2.15 → 0.83; the hand rests on the top (0.00) |
| Vault landing | bounce 0.20 → 0 |
| Vault in bullet time (0.3) | 1.40 s in the air; +0.06 at the front edge; camera 0.22 |
| Dive launch / landing | feet −0.39 → +0.21 / camera +1.68 → 0.56 |
| Last Stand drop and wakeup | free fall, feet −0.74, camera +1.77 → instant, feet −0.05, camera 0.20 |
| Crouch and stand | feet −0.11 / −0.14 to −0.30 → −0.05 |
| Get-up forced after 8 s | rose by physics over 8 frames → at once |
| Turning while lying (8 angles) | lowest point +0.04 to +0.06; guns +0.38 |
| Reloads: 13 guns and dual | 3 guns left racked, and the carried rifle dropped a magazine too → all correct |
| Pickup (F) ×14, painkiller (H) | worked: torso 82 → 100, painkillers 3 → 2 |
| Drop (G) | hung (the dropper) / floated 0.45 (everyone else) → 0.03 above the floor |
| Low cover: slide and ends | 8 studs/s; stops 0.74 to 0.85 from the ends |
| Low cover: corner swings | never swung → two corners in a row |
| Low cover: pop up and back | lunge 0.57 → gap steady at 2.54 |
| High cover: blind fire and pop out | right arm only; shots round the corner; the carried AK ≥ 1.29 off the wall |
| Network (the server's view) | stance, hip height, the root's drop and the Vault clip's pacing replicate |
| Output log | clean |

**Scripts changed** (in the Team Create place; not in git)
| Script | Change |
|---|---|
| `CameraController` | follows every hip height change; `setVerticalLag` |
| `CharacterController` | `appliedHip`; moves the root over the floor, including for forced stances |
| `AimLayer` | DodgeAir and Dead in `FALLS`; foot guard; plain `bodies` table |
| `AnimationController` | `VAULT_FADE`; resting poses from `WeaponEffects`; markers on the reloaded gun only |
| `VaultController` | lands in Running; caps the landing speed; turns the camera lag on and off |
| `VaultRules` | `apexAbove`, `LEG_TUCK`, `LEG_CLEARANCE`, self-checks |
| `WeaponEffects` | `restPose`; muzzle effects found by name; `Flashes` |
| `WeaponController` | plain `gunStates` table |
| `ProceduralLayer` | plain `bases` and `applied` tables |
| `HitReactions` | plain `springs`, `hits` and `joints` tables |
| `LoadoutService` | `bottomOf`, `layDown`, the delayed lay-down, `dropFront` |
| `CoverRules` | `outerCorner` takes the gap and returns the apex |
| `CoverController` | reach remembered per cover stance; corner swing from the real gap |

**Repo:** committed on JackT6785's PC on 2026-11-02 and 03: `3634cce` (stop tracking bytecode), `7f86ec1` (the Blender export on Blender 5, deterministic, and the `.blend`), `a608dc7` (notes).

**Not done**
- Saving the place in Studio after these changes (File > Save to Roblox).
- A two-player test (Studio's Clients and Servers). Only the server's view was checked.
- Publishing the 93 animations: JordanSaa has to do it, as the place's owner. (Corrected 2026-11-10: the place's owner on Roblox is 83tg; JordanSaa is the GitHub name. The 102 clips were published as 83tg that day.)
- The low-cover pose decision.
- 12 polish items, listed in the to-do with ideas for each.

## 2026-11-01 (later): Animation fixes, carried guns, low cover and the vault (in progress)
Full detail, measurements and next steps: [[Animation and MP3 Systems - Progress and To Do]].

**Changed**
- **One-off clips** (landings, getting up, corners, reloads, draws) hold their last frame while fading instead of flashing their first frame.
- **Stance height changes** (crouch, low cover, getting up, Last Stand) move the root at once; the body and camera ease over. The body no longer sinks up to a stud into the floor, and crouching no longer plays the fall clip.
- **Carried two-handed gun:** new crouched and high-cover carries, plus a floor guard. It no longer goes through the floor when crouching, in cover, diving or lying.
- **Low cover:** guns held low (pistol, dual, rifle per side); blind fire per side over the top; the character keeps the distance its hunched body needs, which stops it sliding along the wall.
- **Corner swings** start and end on the cover idle. **Lying poses** float 0.10 instead of 0.18.
- **Vault:** a higher, level arc over the obstacle and a speed-vault clip paced by the way over, so the legs clear the top.

**Not finished:** the to-do lists the remaining play tests (Last Stand, vault from low cover, two clients), a low-cover pose decision, and publishing. The place must be saved in Studio; nothing is committed.

## 2026-11-01: Bullet time levels, vaulting, hit reactions, ragdoll, kill cam, aim layer and 86 animations (in progress)
Full detail and the next steps: [[Animation and MP3 Systems - Progress and To Do]].

**Changed**
- **Bullet time** rebuilt: 5 s meter in 3 levels; slows players in the activator's direct line of sight; lower-level victims get a mouse-sensitivity penalty; counter-activation at an equal or higher level clears it; Last Stand needs at least one level.
- **Vaulting** over low obstacles (Space), with free aim and firing throughout.
- **Euphoria-style hit flinches** (visual only, movement untouched), **physics ragdoll** on death, and a local **multi-shot kill cam**.
- **Aim layer**: guns point exactly where each player aims from any pose (≤0.03° barrel error), with chest blading, head look, recoil kicks, momentum lean, a run arm pump, the left hand kept on every rifle's handguard, and smooth height changes between stances. Players report their aim to the server (`AimUpdate`), so everyone sees it.
- **86 animations** made in Blender and imported: locomotion, holds, aims, cover (idle, shuffle, corners, holds, blind fire, aiming out), shoot-dodge (run-up, flight, landing, floor), getting up, Last Stand (fall, stand, wakeup), vault, landing roll, draws, pickup, painkiller, drop, and seven reloads with markers.
- **Fixes:** R15 arm IK no longer bends elbows backward; the low-ready holds no longer cross the belly; corner swings turn the body smoothly instead of snapping 90°; flinches slow down in bullet time.

**Not finished:** one-off clips flash their first frame when they end (fix planned first), low-cover hold clips, blind fire over low cover, and several mechanics still to test in play. See the to-do list.

## 2026-10-31: Loadouts, stances, cover, shoot-dodge and Last Stand
**Changed**
- **Loadouts:** two one-handed guns (keys 1, 2) and one two-handed gun (3). **Dual wielding** on 4; drawing both one-handed guns **drops the two-handed gun** on the floor. The two-handed gun is never holstered: it rides in the left hand while a one-handed gun is out, as in Max Payne 3. See [[Loadout and Dual Wielding]].
- **Guns are now Models, not Tools** (a character can only hold one Tool). They hang from Motor6Ds (`RightGrip`, `LeftGrip`, `Holster`) that animations can move.
- **Dropping and picking up:** G drops, F picks up or swaps; guns keep their ammo. Death drops what was in the hands. The Uzi is now one-handed.
- **Reloads** move ammo only when the server's timer finishes, so interruptions lose and duplicate nothing. Dual reloads take the longer time ×1.5. Switching guns takes a short draw time.
- **Movement state machine** (`StanceRules`): one stance at a time (standing, sprinting, crouching, four cover stances, three dive stances, getting up, Last Stand, dead), with what each allows and which stances follow. The client predicts and the server confirms, rejects or forces. See [[Movement State Machine]].
- **Sprint** is now a stance: firing ends it (0.2 s before the gun can fire), it can't start in cover, and reloads carry on.
- **Free crouch** on C, with a headroom check under low ceilings.
- **Cover** on E: high and low cover, sliding along walls, stopping at ends, inside corners, swinging round outside corners, popping out to aim, blind fire, and the shoulder camera following the side. See [[Cover System]].
- **Shoot-dodge** on Left Alt or V: a 0.2 s run-up, dives in any direction, a long low flight, wall stops and slides, a floor slide, lying down aiming, getting up. See [[Shoot-Dodge]].
- **Last Stand:** a killing blow on a player with a painkiller and a loaded gun drops them into localized bullet time with the camera dragged onto the killer; killing or downing the killer in 4 s costs a painkiller and all adrenaline, followed by a 3 s defenseless wakeup. See [[Last Stand and Bullet Time]].
- **Bullet time** exists as a local bubble (`TimeScale` on characters), and the HUD's slim bar is now the **adrenaline** meter.
- **Accuracy modifiers** for walking, sprinting, crouching, jumping, diving, blind fire, peeking, aiming from cover and dual wielding.
- **Shots leave from a server-placed muzzle** and are blocked by anything solid in the gun's path; the reticle shows a cross when blocked.
- **Aiming is tracked by the server** (0.15 s settle time) instead of a flag on each shot; aiming slows walking to 70%.
- **Server checks** for every stance request, dive, cover claim, hold, drop and pickup, plus a movement-speed check that puts speeders back.
- **Animation preparation:** every animation has an empty slot in `AnimationConfig`; `AnimationController` will play them, stretching reloads to the server's timers. See [[Animation Hooks]].
- **HUD:** three fixed gun rows, pickup and cover prompts, short messages, a stance tag, the Last Stand countdown, a bullet-time label, the dual-wield warning, a blocked reticle.
- **Code layout:** new shared modules `StanceRules`, `CoverRules`, `DodgeRules`, `ShotRules`, `LoadoutRules`, `LastStandRules`, `AnimationConfig`; new server modules `StanceService`, `LoadoutService`, `LastStandService`, `BulletTimeService`; `CharacterServer` replaces `LimbServer`; `WeaponServer` rewritten; new client controllers `Keybinds`, `CoverController`, `DodgeController`, `LastStandController`, `AnimationController`, `WeaponEffects`; `CharacterController`, `WeaponController`, `CameraController` and `Hud` rewritten or extended. New remotes `StanceRequest`, `StanceResult`, `WeaponAction`, `LastStandEvent`. See [[Architecture]].
- **Test arena** north of the spawn: cover walls, a pillar, crates, an inside corner, a dive lane, a ledge, a crouch tunnel, a table with every gun, target dummies and a gunman that shoots back (press T). See [[Test Arena]].

**Decisions**
- The sawn-off stays one-handed (as in Max Payne 3 and the previous build), even though it is a shotgun. One line in `WeaponConfig` changes it.
- Dodge on Left Alt or V, cover on E, pick up on F, drop on G, crouch on C. Space stays jump. Shift stays sprint.
- During a Last Stand the downed player can't be hurt; only the window and line of sight decide. The killer's way out is to hide.
- High cover can only be aimed or blind fired from an end, as in Max Payne 3 (lean out at a pillar).
- No slow motion during dives: Max Payne 3's multiplayer isn't confirmed to have it, and slowing a whole server isn't possible.
- This place has no Roblox PlayerModule, so the client reads WASD and the left stick directly.

**Tested in Studio play mode** (details in [[Test Arena]])
- Crouch, the tunnel's headroom check, sprint and the trigger ending it.
- Dual wield and the drop, pickups and swaps, interrupted and full reloads, dual reloads, dropping with G.
- High and low cover, ends, pop-out and back, inside corner, circling the pillar, aimed shots and blind fire from cover, blocked blind fire.
- Forward, sideways and backward dives, a head-on dive into a wall, getting up.
- Last Stand: start, camera lock, bullet time on the killer, success with its costs, the wakeup, failure by timeout, instant death without painkillers.
- Arm injuries ending dual wielding; the server pulling back a faked speed hack. No errors in the output.

**Not done or not tested**
- No animations (as requested); the body sinks for crouches and guns hang from the hands. No sounds.
- Not tested with two real players or under lag; no touch controls.
- The angled wall, the ledge dive and Last Stand's line-of-sight failure weren't tried in play. Studio's Script Analysis wasn't checked.
- Player-triggered bullet time from the adrenaline meter, vaulting and rolling on the floor aren't built.

## 2026-10-31: HUD restyled to match the Max Payne 3 reference
**Changed**
- **Health display:** the boxy body figure is replaced by a 3D human figure, matching your AK screenshots. It is Roblox's "Man" body, seen from behind in see-through grey. Each limb fills red from its lowest part up (feet first), and a limb in the red is red all over.
- **Painkiller count:** now a black number in a white square on the figure's back.
- **Slim bar:** a white bar beside the figure, a placeholder for the future bullet-time meter.
- **Status text:** red text with no box.
- **Gun list:** restyled to match the figure. No black tiles or white outlines; the guns are see-through grey shapes and the gun in hand is bright white. Ammo is written like Max Payne 3's "30 120": magazine in bold white, spare rounds in grey.
- **Keybinds:** unchanged, as asked.
- `ReplicatedStorage.Assets.UI.HealthFigure` added. `WeaponController` now sends the HUD numbers instead of a ready-made ammo string.

**Tested**
- Previewed in edit mode, then checked in play mode with no errors.
- The equipped AK row read "0 | 26 | 30" after a burst.
- With the left leg half damaged, the foot showed red, the shin half red and the thigh grey. The right arm in the red was fully red, and its two-handed guns faded in the list.

**Not done**
- The figure is chunkier than Max's slim one; a custom figure would need modelling.
- The bullet-time bar doesn't move yet.

## 2026-10-31: Weapon overhaul, camera, limb health and HUD
**Changed**
- **Ammo:** every gun now spawns with a full magazine plus **one spare magazine** (was several spare magazines).
- **Recoil:** CS2-style. Server-side spread grows while firing and settles after a pause. A fixed spray pattern per gun moves the camera, and each shot adds a sharp jerk.
- **Aiming:** right mouse button. The camera zooms in and spread tightens. The Barrett M107 gets a heavy second zoom into a scope overlay.
- **Tracers:** the thin instant line is replaced by a two-beam glowing streak that travels at the gun's bullet speed.
- **Muzzle flash:** the glowing ball is replaced by a real light that briefly lights the surroundings, plus flame, spark and smoke particles.
- **Impacts:** sparks and dust on surfaces, blood on bodies.
- **Camera:** locked to third person over the shoulder, with no first-person view. Q swaps shoulders. The character always faces where the camera points.
- **Limb health:** head, torso, both arms and both legs each have their own health. Limping, crawling, one-arm and disarmed rules apply, and the head or torso in the red kills.
- **Painkillers (H)** heal every limb. Players start with 3.
- **Shoot-dodge hooks:** the `ShootDodgeScale` attribute (1, 0.4 or 0) is ready for the dive when it's built.
- **Sprint** on Shift, blocked by limping or aiming.
- **HUD:** keybinds bottom left; weapon slots with white outline icons and ammo bottom right; body figure with painkiller count and status tag. Roblox's own hotbar and health bar are off.
- **Weapon switching:** keys 1–0 and the mouse wheel, since the Roblox hotbar is gone.
- **Code layout:** split into modules. Server: `WeaponServer`, `LimbServer`, `LimbService`. Shared: `WeaponConfig`, `WeaponMath`, `LimbRules`. Client: `ClientMain` starting `CameraController`, `CharacterController`, `WeaponController` and `Hud`. The old `WeaponClient` was removed.
- `StarterPlayer.EnableMouseLockOption` turned off, so Roblox's shift-lock doesn't fight the camera or the sprint key.

**Decisions**
- Hits stay instant (hitscan), as the networking notes recommend for the first prototype. The tracer only shows the bullet's travel.
- Recoil lives on the client camera; spread stays on the server. A no-recoil cheat is possible, but a no-spread cheat isn't.
- The client tells the server whether it is aiming. This is cheatable for now and logged as a follow-up.
- Weapon icons are drawn from untextured copies of the real gun models, so no images had to be uploaded.
- The "one magazine, no reserve" line in [[Max Payne 3 HUD and Combat UI Reference]] was replaced by this milestone's rule: one spare magazine.

**Tested in Studio play mode**
- No errors in the output log.
- Camera: locked third person on the right shoulder; Q moved it to the left shoulder and back.
- Aim zoom: 70 to 52 for normal guns. The sniper reached its overlay at 0.45 s, and switching guns mid-aim blended smoothly both ways.
- Firing: the MP5 fired at its rate. The muzzle light lit up during the burst and switched off after. The camera climbed 3.7° and recovered within 1.5 s.
- Spread on the server: AK hip 0.2° growing to 4°; aimed 0.3° growing to 1.8°.
- Tracers travelled at the configured speed (AK 2,000 studs/s) with a 7-stud streak.
- Reload used the single spare magazine (MP5 21 rounds → 30 / 21).
- Sprint: walk speed 24, back to 16 on release.
- Every limb rule, painkiller use and cooldown, gun dropping and equip blocking, real shots hitting the right limbs on a dummy, and torso death with a clean respawn. Details in [[Limb Health]].

**Not done or not tested**
- No animations (as requested), sounds, ammo pickups or touch controls.
- The shoot-dodge itself isn't built; only its hooks exist.
- Not yet tested with two real players or under network lag. Not tested on phones or consoles.
- Studio's Script Analysis (strict type warnings) wasn't checked. Only runtime errors were watched.

## 2026-10-31: First working guns
- Made the 13 guns in `ServerStorage.WeaponKit` usable: server-checked hitscan shots, ammo and reloads, fire-rate limits, spread that grows while firing, slide kick, muzzle flash and tracers, an ammo readout, and a Studio-only test loadout.
- Tested: fire rate, spam and bad-data rejection, walls blocking shots, shotgun pellets, headshots, reload cancelling, respawn.
- Superseded the same day by the overhaul above.
