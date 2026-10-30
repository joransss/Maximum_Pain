# Max Payne 3 Animation Reference

How Max Payne 3 animates, from Rockstar's official trailers on the [Steam page](https://store.steampowered.com/app/204100/Max_Payne_3/) (frames studied at 5 fps; none stored in the repo) and the sources below. Compiled 2026-10-30. Use it as the benchmark for **feel**; build original animations.
Related: [[Max Payne 3 Mechanics Reference]] · [[Max Payne 3 Gunplay - Accuracy and Recoil]]

## How it works (Euphoria)
- Max Payne 3 runs on Rockstar's RAGE engine with NaturalMotion's **Euphoria**: physics, simulated muscles and authored animation blended together. ✅
- Shoot-dodge is "physics and an animation pose library running together"; the body behaves "realistically depending on his environment". ✅ (Rob Nelson, art director, [MCV](https://mcvuk.com/development-news/max-payne-3-dev-explains-euphoria-engine-tweaks/))
- Hit reactions were made to feel "more connected"; each shot reacts and bodies "fall realistically". ✅ (same)
- The animation comes from hundreds of hours of motion capture, with Max played by James McCaffrey. It won "Best Animation" in 2012.
- **Lesson:** the weight comes from physical reactions laid **on top of** movement, not from keyframes alone.

## Animation by animation
Official images: `https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/204100/<file>`. The **Steam #** column gives the file name.

| Animation | What Max Payne 3 does | Footage | Steam # |
|---|---|---|---|
| **Getting hit** | Each shot jolts the torso away from the hit and flings the arms. The body **keeps its momentum**: a target kept running along a beam through several hits, then his knees buckled into a crouch and he fell. A wide-legged, hunched stagger sideways. From the victim's view: a hand to the wound, hunched. | MP trailer 0:14–0:16, 0:44–0:48; D&T Video 2 2:57–3:00; D&T Video 3 2:14–2:16 | 8 (`ss_351fd2a6…`) |
| **Death** | A gradual collapse driven by physics; the body falls with its momentum. In the bullet cam, Max can keep firing into the falling body. | MP trailer 0:47–0:48 | 15 (`ss_8e2bb13d…`) |
| **Shoot-dodge (in the air)** | Body flat with legs straight and together, trailing up; the gun arm reaches out at the target, head down the arm. ~2.5 s in the SP slow motion. | D&T Video 2 2:30–2:34 | 1 (`ss_84fc2ba2…`), 9 (`ss_4729803d…`) |
| **Dive hits a wall** | The body collides and the dive ends there. | (from sources) | — |
| **On the ground** | On his back with the head up, one arm raised at the target; turns and rolls 360° to keep aiming; stays down until moving. | D&T Video 2 2:34–2:36 | — |
| **Getting up** | A plain stand-up that leaves you exposed. | (Reviewed) | — |
| **Running with a pistol** | Upright, slight lean, pistol low in one hand, other arm pumping; heavy feel. | MP trailer 2:24–2:31 | 2 (`ss_b442d79f…`) |
| **Firing on the move** | The gun arm extends one-handed at the target without breaking stride. | MP trailer 2:29–2:31 | 4 (`ss_6e329c5e…`) |
| **Two-handed weapon carry** | Rifle held low in two hands while moving; under the arm while firing a pistol. | — | 10 (`ss_a0106421…`) |
| **Dual wield** | Both arms extended, each gun aimed at the target; fires on the move. | D&T Video 2 1:02–1:04 | 11 (`ss_f528ddad…`), 5 (`ss_649a56ef…`) |
| **Aim** | Rifle shouldered, head down on the gun, camera tight over the shoulder; about 0.4 s from a sprint to aiming. | Your screenshots; MP trailer 0:40–0:42 | 14 (`ss_e35354a1…`) |
| **Recoil** | Big muzzle flash; the aiming body barely moves; one-handed pistols kick at the wrist and elbow. | D&T Video 2 1:02–1:04 | 4 |
| **Cover** | Shoulder or back to the wall with the gun low. In low cover: kneel, pop up to fire, duck with the head well below the edge. At a pillar: lean out. | D&T Video 2 2:55–3:02 | 3 (`ss_4ae054ce…`), 6 (`ss_4fc1bd43…`) |
| **Melee** | Close-quarters strikes and kicks. | — | 13 (`ss_23bf1fb7…`) |

Other screenshots: 7 (`ss_6a624879…`) close SMG handling · 12 (`ss_0bcd7e1f…`) multiplayer character and crew · 16 (`ss_482c837e…`) character.

## Sources
[MCV interview](https://mcvuk.com/development-news/max-payne-3-dev-explains-euphoria-engine-tweaks/) · [WhatCulture: Euphoria](https://whatculture.com/gaming/max-payne-3-euphoria-for-the-masses) · [Reviewed review](https://reviewed.com/content/max-payne-3-review) · [Engadget: shootdodge](https://www.engadget.com/2012-03-01-learning-how-to-shootdodge-with-max-payne-3.html) · [Wikipedia](https://en.wikipedia.org/wiki/Max_Payne_3) · Steam trailers: "Max Payne 3 Multiplayer", "Design and Tech Video 2" (Targeting and Weapons, then Tactical Movement from ~2:25), "Design and Tech Video 3" (Visual Effects and Cinematics).
