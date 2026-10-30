# Max Payne 3 Gunplay — Accuracy and Recoil

How Max Payne 3 makes rapid fire less accurate and lets recoil build. Compiled 2026-10-30.
**Confidence:** ✅ official source or seen in official footage · 📰 2012 guides or reviews · ❓ unconfirmed.
Related: [[Max Payne 3 Mechanics Reference]] · [[Max Payne 3 HUD and Combat UI Reference]]

## What's confirmed
1. **The first shot is the accurate one.** In MP, the laser sight attachment "increases first shot accuracy". That only means something if the shots after the first are less accurate. 📰 ([mp3multiplayer: loadouts](https://mp3multiplayer.wordpress.com/2012/06/18/loadouts/))
2. **Recoil costs accuracy.** The compensator attachment "reduces recoil, increasing accuracy". 📰 (same source)
3. **Recoil builds and recovers over time.** A 2012 patch (fan transcription) improved the Mini-30's "recoil recovery speed". In Rockstar's own patch notes, accuracy is a per-weapon tuning value: DE .50 "accuracy … slightly increased". ✅/❓ ([Rockstar](https://www.rockstargames.com/newswire/article/75o9411317315k/max-payne-3-multiplayer-latest-weapon-tuning-updates.html))
4. **The reticle can show the spread.** The weapon-specific reticle option draws a crosshair or circle sized to "the bullet spread/blast radius of your particular weapon". The default is a dot that turns red on a target, with an "x" for a kill. ✅ ([NVIDIA tweak guide](https://www.nvidia.com/en-gb/geforce/news/max-payne-3-tweak-guide))
5. **Spread depends on the weapon:** semi-automatic rifles (Mini 30), slow, short-range pistols (608 Bull), and SMGs with an "insanely fast fire rate" (Micro 9mm). Suppressors increase damage drop-off; barrel upgrades reduce it. 📰
6. **Low camera recoil:** one review says the guns barely kick the camera, but a laser-sighted gun had "substantially more recoil". Read together: little camera shake, with most of the cost going into spread and visible gun kick. 📰❓ ([Reviewed](https://reviewed.com/content/max-payne-3-review))

## What the footage shows
| Source | Moment | What you see |
|---|---|---|
| Design & Tech Video 2 ("Targeting and Weapons", Steam) | 1:02–1:04 | Dual Micro SMGs fired continuously while running: circle reticles around the aim point. Muzzle flash and arm kick on every shot. ✅ |
| Design & Tech Video 2 | 0:20–0:30 | Over-the-shoulder rifle fire in an office: a small "+" reticle with a circle; bullet holes spread across the wall behind the target. ✅ |
| Your screenshots (XboxViewTV gameplay video, ~1:18–1:19; kept on your PC) | AK, 30 → 25 rounds | The first rounds show a red reticle with a hit marker and blood on the target. Later frames show a larger white ringed crosshair. The target keeps reacting to each hit while moving. Suggests spread grows while firing, but the reticle could also just be off target. ❓ |
| Multiplayer trailer (Steam) | 0:44–0:48 | Sustained rifle fire at a moving target on a rooftop beam; hits land while the target keeps running, then he collapses. ✅ |

The frames were studied at 5–10 fps. None is stored in the repo; use the timestamps on the [Steam page](https://store.steampowered.com/app/204100/Max_Payne_3/).

## Not confirmed
- The exact numbers: how much spread grows per shot, the cap, and the recovery rate.
- Whether recoil follows a set pattern (as in Counter-Strike) or is random.
- How much moving, crouching, cover and dives change accuracy, beyond the general hints above.

To pin these down, record a short clip of each weapon fired in bursts at a wall and compare the bullet-hole spread from shot 1 to shot 10.

## Same idea in other games (for tuning)
- **Counter-Strike 2:** recoil (a learnable climb pattern) and inaccuracy (random spread from movement) are separate systems. The first shot lands where the crosshair is. ([refrag.gg: spray science](https://refrag.gg/blog/spray-science-how-does-weapon-recoil-function-in-cs2) · [csdb.gg recoil patterns](https://csdb.gg/recoil-patterns/))
- **"Bloom":** the reticle grows with sustained fire and shrinks when you stop. ([Destinypedia](https://www.destinypedia.com/Reticule_bloom) · [Giant Bomb: expanding crosshair](https://www.giantbomb.com/expanding-crosshair/3015-134/))
- **Roblox:** recoil is usually a spring kicked on each shot, kept separate from hit detection (e.g. FastCast). ([spring recoil thread](https://devforum.roblox.com/t/help-with-gun-recoil-system/2166799) · [FastCast](https://devforum.roblox.com/t/making-a-combat-game-with-ranged-weapons-fastcast-may-be-the-module-for-you/133474))

## Takeaway for Maximum Pain
- The first shot is accurate.
- Each quick follow-up shot adds spread and visible gun or arm kick, up to a cap per weapon.
- Spread recovers when you stop firing; recovery speed is a tuning value per weapon.
- Attachments trade on this: laser for first-shot accuracy, compensator for recoil.
- Show spread on the reticle (optional, like Max Payne 3's weapon-specific reticle) and keep camera shake small.
