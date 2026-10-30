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

## Design observations for Maximum Pain

1. Keep combat-critical information readable without covering the central target area.
2. Distinguish current magazine ammunition from reserve ammunition. **Maximum Pain starts each weapon with one magazine and no reserve ammo**; compatible ammo scavenged from a ground weapon should update the reserve or magazine according to the game's final ammo model.
3. Make health, bullet-time resource, weapon identity, magazine count, and interaction prompts legible during shoot-dodges and fast camera motion.
4. Use subtle, contextual damage-direction feedback that does not obscure the reticle.
5. In multiplayer, show only match information that players need to make immediate decisions; avoid clutter around the reticle.
6. Test visibility at different resolutions, aspect ratios, and Roblox UI scale settings.

## Suggested Maximum Pain HUD checklist

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

## Implemented HUD (2026-10-30)
Original layout in `StarterGui.CombatHUD`:
- **Bottom right:** weapon panel (live 3D weapon view, name, magazine / reserve, reload state), vertical bullet-time meter, health silhouette that fills red from the feet, medicine bottles.
- **Centre:** precision dot reticle (2026-10-30), hit marker (amber on headshot), red kill X, score pop-ups to the right (KILL / HEADSHOT / SHOOT-DODGE / BULLET TIME / LAST STAND).
- **Top right:** score and kills.
- **Other:** Last Stand banner with countdown, context messages, screen grading for bullet time and low health.
Not yet: damage-direction indicator, round timer.
