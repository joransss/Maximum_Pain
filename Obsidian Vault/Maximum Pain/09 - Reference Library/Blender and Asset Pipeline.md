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

## Asset register
| Asset | Creator/source | Licence/permission | Source file | Roblox asset ID | Tested |
|---|---|---|---|---|---|
| Gunshot "Gun Live Ammunition 601 (SFX)", 9mm Beretta | Pro Sound Effects via Roblox Creator Store | Roblox-licensed SFX library | — | 9114714021 | Library sound to try |
| Reload "Machine Gun 16 (SFX)" | Pro Sound Effects via Roblox Creator Store | Roblox-licensed SFX library | — | 9116345318 | Library sound to try |
