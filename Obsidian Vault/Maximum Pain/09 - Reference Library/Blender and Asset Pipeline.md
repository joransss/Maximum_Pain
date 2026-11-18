# Blender and Asset Pipeline

## Primary references
- [Blender Manual](https://docs.blender.org/manual/en/latest/) — modelling, materials, UVs, rigging and animation.
- [Roblox model export requirements](https://create.roblox.com/docs/art/modeling/export-requirements) — check current export constraints before importing.
- [Roblox animation documentation](https://create.roblox.com/docs/animation) — animation workflow and publishing.
- [Roblox Animation Editor](https://create.roblox.com/docs/animation/editor) — editing and testing animation in Studio.

## Suggested pipeline
1. **Blockout:** create simple, readable proportions before detailed modelling.
2. **Model:** keep topology and object complexity appropriate for the asset's screen size and gameplay importance.
3. **Materials and UVs:** use consistent material naming and test appearance under Roblox lighting.
4. **Rigging:** use a compatible rig and confirm deformation at shoulders, elbows, wrists and weapon grips.
5. **Export:** follow the current Roblox export requirements; keep a source `.blend` file and a separate export copy.
6. **Import:** check scale, orientation, pivots, materials, animation and collision behaviour in Roblox Studio.
7. **Optimise:** remove unnecessary geometry and materials; use simple collision geometry where possible.
8. **Track rights:** record creator, source URL, licence/permission and modifications for every third-party asset.

## Asset checklist
- [ ] Scale and orientation are correct
- [ ] Pivot/origin is appropriate for placement or animation
- [ ] Materials and textures import correctly
- [ ] Rig and animation behave correctly, if applicable
- [ ] Collision is appropriate and does not obstruct gameplay
- [ ] Performance is acceptable in a multiplayer test
- [ ] Source files are retained
- [ ] Licence and attribution requirements are recorded

## Maximum Pain priorities
Prioritise weapon silhouettes, first-/third-person weapon handling, character locomotion and readable environment props. Prototype with greybox assets before spending time on polished art. Visual detail must not compromise aiming clarity, hit readability or performance.

## UI art for the menus
Built 2026-11-18 for the menu plan's section 3 ([[Menus, Loadout, Progression and Shop - To Do#3. Blender for the UI]]). Everything is in `Assets/Blender/UI/`.
- **Run it** from the repo's root with Blender 5.2 or newer (on JordanSaa's PC Blender is `D:\blender.exe`, not on PATH):
  `blender -b --factory-startup --python-exit-code 1 --python Assets/Blender/UI/ui_lib.py -- [logo] [overlays] [weapons] [--rebuild]`
  With no group named it does all three (the weapons only when the guns' FBX files are there). A full run takes about 40 s.
- **What it makes:** each image goes to `Exports/<name>.png` and into `Exports/manifest.json` with its size and SHA-256.

| Image | Size | What it is | Where it's used |
|---|---|---|---|
| `UI_Logo_Full` | 1024 × 147 | MAXIMUM PAIN on one line: Oswald Bold, extruded, worn off-white paint over steel (chips, fine scratches, worn edges), lit flat-on | The main menu, 104 px high at 1080p |
| `UI_Logo_Compact` | 628 × 320 | The same on two lines | Not yet |
| `UI_Overlay_Grain` | 256 × 256 | Film grain: white and black specks, a tile with no seams | Tiled over the menu, jumping 18 times a second |
| `UI_Overlay_Vignette` | 1024 × 576 | Black edges fading to clear; stretched, it follows any shape of screen | Over the menu |
| `UI_Overlay_Bokeh1`, `2` | 512 × 512 | Out-of-focus lights, warm and cool: discs a little brighter at the rim | Drifting over the menu |
| `UI_Overlay_LightLeak` | 512 × 512 | A warm glow from one corner | The menu's top right, swelling and fading |
| `UI_Icon_<gun>` | 512 × 160 | A gun side-on, muzzle right, white | Not made yet (below) |

- **The `.blend` files are scenes to look at and adjust** (`UI_Logo.blend` so far). Every object in a scene's `UI_Render` collection is rendered one by one through `UI_Camera`, lit by the `UI_Rig` lights (key, fill and rim, sized to each object), framed to fit. An object's custom property `ui_frame` (width, height in pixels) or `ui_height` (its height on a 1080p screen: it is rendered at twice that, never wider than 1024) says how, so an object added to `UI_Render` by hand is rendered too. `--rebuild` builds a `.blend` afresh from the script, losing changes made by hand.
- **The same files every time:** Cycles on the CPU with a fixed seed and no denoiser, Standard colour (no tone curve), and each PNG saved again with nothing but its pixels, since Cycles writes its render times into every file. Two runs on 2026-11-18 gave byte-identical files, so git only sees real changes.
- **The font:** the logo uses Oswald Bold, the HUD's font, which ships with Roblox (SIL Open Font License 1.1). `ui_lib.py` finds it in Roblox's install folders (`%LOCALAPPDATA%\Roblox\Versions\*\content\fonts`), or set `UI_FONT` to a copy of `Oswald-Bold.ttf`. The font file isn't kept in the repo: its licence would have to go with it.
- **Weapon icons:** `ui_lib.py weapons` imports every gun in `Assets/Blender/Weapons/Exports/FBX` (the weapon pipeline's export, one file per weapon id), drops the helper points (`*_Att`), turns each gun side-on with the muzzle to the right (found from its Muzzle point), gives it one white material and renders it into 512 × 160 as `UI_Icon_<last part of the id>` (`UI_Icon_AK47`). The game draws the grey version by tinting the white one (`ImageColor3`), so each gun is one upload. It worked on the M9 work file; the real FBX files aren't on this PC (2026-11-18), so the 13 icons aren't made. `--weapons-from DIR` takes them from elsewhere.
- **Uploading:** the images must be uploaded by 83tg, the place's owner. Through the Studio MCP: serve `Exports/` on the PC (for example with Blender's own Python, `D:\5.2\python\bin\python.exe -I -m http.server 8766 --bind 127.0.0.1 --directory Assets/Blender/UI/Exports`) and give `upload_image` the URLs; or by hand with Studio's Asset Manager (Bulk Import). Put each new id in `Exports/ui_ids.json` (with the image's SHA-256 from the manifest, so it's clear which upload matches which file) and in the game's `UiAssets` module. A changed image is a new upload with a new id.
- **Checking an upload:** `ContentProvider:PreloadAsync` run from the Studio MCP reported Failure for images that showed fine; look at the menu in a screenshot instead.

## Asset register
| Asset | Creator/source | Licence/permission | Source file | Roblox asset ID | Tested |
|---|---|---|---|---|---|
| Gunshot "Gun Live Ammunition 601 (SFX)", 9mm Beretta | Pro Sound Effects via Roblox Creator Store | Roblox-licensed SFX library | — | 9114714021 | Library sound to try |
| Reload "Machine Gun 16 (SFX)" | Pro Sound Effects via Roblox Creator Store | Roblox-licensed SFX library | — | 9116345318 | Library sound to try |
| `UI_Logo_Full` (image) | Ours: `ui_lib.py`, set in Oswald Bold | Ours; Oswald: SIL Open Font License 1.1 | `Assets/Blender/UI/UI_Logo.blend` | 96790464909769 | In the main menu, 2026-11-18 |
| `UI_Logo_Compact` (image) | Ours: `ui_lib.py`, set in Oswald Bold | Ours; Oswald: SIL Open Font License 1.1 | `Assets/Blender/UI/UI_Logo.blend` | 136813098305884 | Uploaded, not used yet |
| `UI_Overlay_Grain` (image) | Ours: `ui_lib.py` | Ours | `Assets/Blender/UI/ui_lib.py` | 100309540894530 | In the main menu, 2026-11-18 |
| `UI_Overlay_Vignette` (image) | Ours: `ui_lib.py` | Ours | `Assets/Blender/UI/ui_lib.py` | 72666939925737 | In the main menu, 2026-11-18 |
| `UI_Overlay_Bokeh1` (image) | Ours: `ui_lib.py` | Ours | `Assets/Blender/UI/ui_lib.py` | 87414498407667 | In the main menu, 2026-11-18 |
| `UI_Overlay_Bokeh2` (image) | Ours: `ui_lib.py` | Ours | `Assets/Blender/UI/ui_lib.py` | 71815412009345 | In the main menu, 2026-11-18 |
| `UI_Overlay_LightLeak` (image) | Ours: `ui_lib.py` | Ours | `Assets/Blender/UI/ui_lib.py` | 72722730202860 | In the main menu, 2026-11-18 |
