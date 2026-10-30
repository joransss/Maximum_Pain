# Max Payne 3 Animation Reference

Benchmark for how Maximum Pain's animations should **feel**. Study reference only: build original animations, don't copy Max Payne 3's characters, content or assets. Clip list and pipeline: [[Animation System]]. Screenshots of a single-player rifle fight: [[Reference Images]] (Max Payne 3 Combat).

Compiled 2026-10-30 from Rockstar's official trailers on the [Steam store page](https://store.steampowered.com/app/204100/Max_Payne_3/) (frames viewed at 5 fps; none stored in the repo) and the written sources below. Timestamps let you find each moment.

## Sources
| Source | What it shows |
|---|---|
| Steam trailer "Max Payne 3 Multiplayer" | Real multiplayer footage: hit reactions on the move (0:14–0:16, 0:44–0:48), running and firing on the move (2:24–2:31) |
| Steam trailer "Design and Tech Video 2" (Targeting and Weapons, then Tactical Movement from ~2:25) | Sideways shoot-dodge and shooting from the ground (2:30–2:36), low cover and staggering enemies (2:55–3:02) |
| Steam trailer "Design and Tech Video 3" (Visual Effects and Cinematics) | Close-up hit reactions (2:14–2:16) |
| [MCV: art director Rob Nelson on Euphoria](https://mcvuk.com/development-news/max-payne-3-dev-explains-euphoria-engine-tweaks/) | Shoot-dodge is "physics and an animation pose library running together"; hit reactions made "more connected"; individual shots react and people fall realistically |
| [WhatCulture: Euphoria for the masses](https://whatculture.com/gaming/max-payne-3-euphoria-for-the-masses) | Max "collides with walls, slides along floors, and even moves 360 degrees while lying on the floor" |
| [Reviewed: review](https://reviewed.com/content/max-payne-3-review) | Prone until a direction is pressed; turn and roll a full 360° while aiming on the ground; getting up is a plain stand-up (exposed); hitting a wall ends the dive |
| [Engadget: learning to shootdodge](https://www.engadget.com/2012-03-01-learning-how-to-shootdodge-with-max-payne-3.html) | Max "remains an open target on the ground" after a dive |

## Animation by animation
| Animation | Max Payne 3 (reference) | Maximum Pain now | Change |
|---|---|---|---|
| **Getting hit** | Each shot jolts the torso away from the hit and flings the arms. The body **keeps its momentum** (a target kept running along a beam through several hits), the knees buckle and it sinks into a crouch. Seen from the victim: one hand to the wound, hunched, stumbling sideways. | Nothing (blood puff only). | **Top priority.** Per-hit flinch layered on top of whatever clip is playing, a short stagger, and a crouch when health is low. |
| **Death** | Progressive collapse after the last hits, with physics: the body falls with its momentum. | Roblox default (body falls apart). | Ragdoll that keeps the body's momentum and the last hit's direction. |
| **Dive, in the air (sideways)** | Body fully horizontal, **legs straight and together**, trailing slightly up; gun arm reaching out at the target, head down the arm. In the single-player clip it's slow motion, ~2.5 s airborne. | `DiveAir_L/R`: legs scissored with bent knees, two-handed aim; real time, 0.65 s. | Straighten and close the legs; extend the gun arm further. |
| **Dive hits a wall** | The body collides physically and the dive ends there. | Slides along the wall with the pose unchanged. | Impact reaction (crumple) when the dive is stopped by a wall. |
| **On the ground** | On his back, head lifted, one arm up at the target; **turns and rolls 360°** to keep aiming; stays down until a direction is pressed. | Arms aim from the ground, but the body stays on the side it landed on. | Let the lying body roll and turn toward the aim. |
| **Getting up** | A plain stand-up that leaves you exposed. | 0.5 s push-up or roll. | Fine as is; could be shorter. |
| **Running with a pistol** | Upright, slight lean, gun held **low** in one hand, the other arm pumping. | `Run` + `Hip`: gun held forward at the waist the whole time. | Carry the gun low while running; raise it only when firing. |
| **Firing on the move** | The gun arm extends one-handed at the target **without breaking stride**. | `RecoilHip` from the waist pose. | Extend the arm to fire while running. |
| **Run → aim** | About 0.4 s from a sprint to a shouldered aim. | ~0.12 s blend plus the chest turn. | Matches. |
| **Recoil while aiming** | The body barely moves; the muzzle flash carries the shot. | `RecoilAim` kicks the gun 14°. | Reduce the kick (about 5–6°). |
| **Low cover** | Kneels behind cover, pops up to fire over it, **ducks with the head well below the edge**, gun tucked to the chest. | Back to the wall, crouched; pops up when aiming. | Duck lower and tuck the gun when not firing. |
| **Leaning out at a pillar** | Leans out sideways to fire. | Leans 1.6 studs out at cover edges. | Matches. |
| **Reload, melee** | Not covered by these clips. | `Reload` clip; no melee. | Still need reference. |

## Takeaways
1. Max Payne 3's weight comes mostly from **physics reactions** (hits, deaths, collisions), not the keyframes.
2. Reactions **add on top of movement** rather than stopping it.
3. Players stay dangerous on the ground: they aim and roll in any direction.
4. When not firing, the pistol is carried low and one-handed.
