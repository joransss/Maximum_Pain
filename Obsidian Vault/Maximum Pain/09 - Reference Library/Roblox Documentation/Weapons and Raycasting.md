# Weapons and Raycasting — Reference Notes

Primary source: https://create.roblox.com/docs/workspace/raycasting

## Intended approach
Use server-validated hitscan for the first weapon prototype. The client may provide input and aim intent, but must not be trusted to decide damage or bypass walls.

## Server validation checklist
- Character exists and is alive.
- Weapon is equipped and the player is allowed to fire.
- Server ammo is greater than zero.
- Fire rate and reload state are valid.
- Shot origin is plausibly close to the character/weapon.
- Aim direction and hit claims have valid types and reasonable values.
- Raycast and obstruction checks reject shooting through static cover.
- Target is a valid opposing player and not already dead.
- Damage amount comes from server-owned weapon configuration.
- Requests are rate-limited and malformed input is rejected.

## Acceptance checks
- Walls block hits.
- Client cannot choose arbitrary damage or target health.
- Empty magazine cannot fire.
- Rapid remote spam does not exceed weapon fire rate.
- Respawn and weapon switching cannot retain invalid combat state.
