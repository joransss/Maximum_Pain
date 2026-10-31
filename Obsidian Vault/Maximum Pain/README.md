# Maximum Pain — Reference Vault

**Maximum Pain** is an original Roblox PvP third-person shooter in the style of **Max Payne 3** multiplayer: cinematic gunplay, shoot-dodge, bullet time, physical (Euphoria-style) reactions.

The project restarted from scratch on 2026-10-30. Notes on the systems built since then are in `01 - Game Systems`; everything else here is reference material.

## Game systems (current build)
- [[Architecture]]: how the code is split, the remotes, the character attributes, and who decides what.
- [[Movement State Machine]]: every stance (standing, sprint, crouch, cover, shoot-dodge, getting up, Last Stand, dead), what each allows, prediction and server checks.
- [[Loadout and Dual Wielding]]: two one-handed guns and one two-handed gun, dual wielding and its drop penalty, pickups, switching, reloads.
- [[Weapons and Recoil]]: weapon balancing, where shots come from, accuracy modifiers, CS2-style recoil and spread, aiming and the sniper scope, tracers and muzzle flash.
- [[Cover System]]: high and low cover, corners, popping out, blind fire, the cover camera.
- [[Shoot-Dodge]]: the dive in any direction, from run-up to getting up.
- [[Last Stand and Bullet Time]]: Last Stand, localized bullet time and the adrenaline meter.
- [[Limb Health]]: per-limb health, the limping, crawling, one-arm and disarmed rules, painkillers.
- [[HUD Layout]]: blueprint of the HUD (Max Payne 3 style health figure and gun list, boxed keybinds and prompts).
- [[Animation Hooks]]: the animation slots and rules, ready for when animations are made.
- [[Test Arena]]: the test area, its dummies, and what was tested.
- [[Changelog]]: every change to the game, newest first.

## Max Payne 3 (primary reference)
- [[Max Payne 3 Mechanics Reference]] — every mechanic found: single player and multiplayer.
- [[Max Payne 3 Gunplay - Accuracy and Recoil]] — first-shot accuracy, spread while firing fast, recoil and how it recovers.
- [[Max Payne 3 Animation Reference]] — movement, dives, cover, hits and deaths, frame by frame from official footage.
- [[Max Payne 3 HUD and Combat UI Reference]]

## Other references
- [[Reference Games]] — other games and Roblox games worth studying.
- [[Reference Videos]] — video sources, with timestamps.
- [[Reference Images]] — image sources.
- [[Reference Index]] — Roblox documentation, tools and research.

## Rules for references
- Study the design; build original content. Don't copy Max Payne 3's characters, names, story, maps, UI art, audio or assets.
- The GitHub repo is public. Images are **linked**, not stored. Screenshots you paste into Obsidian stay on your PC (`.gitignore`).
- Write down the source and timestamp for every observation, and say whether it was seen in footage or only read about.
