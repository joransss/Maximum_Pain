# Max Payne 3 HUD and Combat UI Reference

## Purpose
Use this as a visual and functional reference for the **Maximum Pain** HUD. This is a study reference only; recreate the underlying principles with an original interface rather than copying Max Payne 3's protected visual design or assets.

## Multiplayer HUD screenshot

![Max Payne 3 multiplayer gameplay HUD showing match score, timer, player labels, and ammunition indicators](https://m.media-amazon.com/images/M/MV5BNmEyMjkyZmEtMDM4ZC00MDgxLTg4N2MtZWJlM2JiM2I3YjZhXkEyXkFqcGdeQXRyYW5zY29kZS13b3JrZmxvdw%40%40._V1_FMjpg_UX1000_.jpg)

Source: [Max Payne 3 multiplayer screenshot hosted on IMDb](https://www.imdb.com/video/embed/vi4014849305/). Image is remotely hosted and may require an internet connection.

## Annotated HUD reference

The [Max Payne 3 Xbox 360 manual, Heads Up Display section](https://www.gamesdatabase.org/Media/SYSTEM/Microsoft_Xbox_360/Manual/formated/Max_Payne_3_-_2012_-_Rockstar_Games.pdf) labels the main single-player HUD elements:

- **Health meter:** represented by a character silhouette that fills red as damage is sustained; painkiller stock is shown within the silhouette. (Maximum Pain calls these **medicine**.)
- **Bullet-time meter:** communicates the remaining slow-motion resource.
- **Weapon wheel:** communicates weapon selection and loadout changes, including the trade-off when switching to dual wielding.
- **Ammo count:** clearly shows ammunition for the equipped weapon.
- **Reticle:** communicates the shot direction.
- **Context prompts:** show when an interaction is available.
- **Damage indicator:** communicates the direction of incoming damage.

The manual also describes multiplayer HUD elements including score, round timer, minimap, match updates, and an adrenaline meter. These are useful reference categories, not requirements to copy wholesale.

## Visual style: black and white boxes (multiplayer)

Seen in your Kill UI screenshot (`Pasted image 20261030022940.png`, kept on your PC; shown in [[Reference Images]]).

- **Flat boxes:** solid rectangles with square corners. No gradients, rounded corners, borders or glow. Each value gets its own box, and boxes sit in a row with thin gaps, like tiles.
- **Type:** heavy, bold sans-serif in white. Labels are uppercase ("KILL"); the event text in the score bar is slanted ("KILL +1"). Numbers are as big as the labels.
- **Colour:** almost only black, white and one grey. **Red is the only accent and always means the enemy:** the enemy team's score and the victim's name.
- **Score bar (top centre):** `KILL +1` (white on black) · `33` your team's score (white on black) · `4:44` round timer (black on light grey, the one inverted box) · `32` enemy score (red on black). The event tile appears at the left end when you score.
- **Kill pop-up (in the world, over the body):** a short vertical stack: `KILL` in white with no box, the points (`50`) in white in a black box, then the victim's name in red with a dark outline, and a thin black underline. It floats over the victim instead of sitting in a fixed screen spot.
- **Kill feed (left edge):** no boxes, just text with a dark shadow. The killer's line is white (two names joined by a grey "+", likely killer and assist ❓); the victim is red underneath.
- **Single-player HUD (your AK screenshots):** same restraint but no boxes. A white body outline (fills red with damage, painkiller count on the chest), a thin white bullet-time bar, and the ammo count (magazine large and bold white, reserve smaller and grey), all grouped in the bottom-right corner.

**Take for Maximum Pain:** high contrast, flat square shapes, very few colours, one accent colour reserved for "enemy", and short uppercase labels. Build our own version (own font, proportions and layout); don't trace this one.

## Design observations for Maximum Pain

1. Keep combat-critical information readable without covering the central target area.
2. Distinguish current magazine ammunition from reserve ammunition. **Maximum Pain starts each weapon with a full magazine plus one spare magazine** (decided 2026-10-31; see [[Weapons and Recoil]]). Compatible ammo scavenged from a ground weapon should update the reserve or magazine according to the game's final ammo model.
3. Make health, bullet-time resource, weapon identity, magazine count, and interaction prompts legible during shoot-dodges and fast camera motion.
4. Use subtle, contextual damage-direction feedback that does not obscure the reticle.
5. In multiplayer, show only match information that players need to make immediate decisions; avoid clutter around the reticle.
6. Test visibility at different resolutions, aspect ratios, and Roblox UI scale settings.

## Suggested Maximum Pain HUD checklist

- [ ] Original black-and-white boxed style: flat square boxes, bold white type, red only for enemies
- [ ] Health state and damage feedback
- [ ] Bullet-time resource and active-state indicator
- [ ] Current weapon identity and fire mode where relevant
- [ ] Magazine ammunition and reserve ammunition shown separately
- [ ] Reticle and hit-confirmation feedback
- [ ] Contextual pickup / interaction prompt
- [ ] Round timer and score where the mode needs them
- [ ] Incoming-damage direction indicator
- [ ] UI remains readable while diving, rotating, and under camera effects

## Use and rights

The screenshot and manual belong to their respective rights holders and are linked for internal visual analysis only. Do not import the screenshot into the shipped game, trace the interface pixel-for-pixel, or treat it as a licensed production asset. Create original UI artwork and layout for Maximum Pain.
