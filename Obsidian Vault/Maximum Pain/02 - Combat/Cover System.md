# Cover System

## Goal
Allow players to use walls, crates, vehicles and other level geometry to break sightlines and create tactical repositioning opportunities.

## Initial Scope
- Cover is primarily environmental; avoid a complex snap-to-cover system in the first prototype.
- Solid cover blocks bullets and Bullet Time line-of-sight raycasts.
- Add optional contextual lean/peek only after core aiming and hit detection are stable.
- Keep flank routes and multiple approaches so cover does not create unbreakable camping positions.

## Implementation Tasks
- [ ] Define collision groups for characters, bullets, and cover raycasts
- [ ] Ensure cover blocks line-of-sight and projectile/hitscan checks consistently
- [ ] Build each test map with flank routes and safe spawn exits
- [ ] Test crouching/standing and camera clipping around cover
- [ ] If adding lean/peek, clamp movement and validate shot origin server-side

## Acceptance Criteria
- Bullets cannot pass through solid cover due to client-side visuals
- Bullet Time visibility checks use the same intended cover rules
- Players cannot hide inside geometry or exploit gaps
- No cover position completely dominates the map

## Implemented (2026-10-30)
Contextual snap-to-cover was built on request (see [[Implementation Log]]).
- **Enter:** V within 3.5 studs of a wall in the camera direction. The server raycasts and classifies by height above the floor: **high** ≥5.6 studs (standing; R15 head top 5.4), **low** ≥2.4 (crouched; posture via `HipHeight`, so hitboxes match). Shorter walls are not cover.
- **In cover:** face the wall at 1.1 studs; A/D slide along it (client-driven, server speed-guarded); endpoints stop you. Holding the direction 0.35 s rounds **inner and outer corners**, and the server re-validates the new wall.
- **Peek / fire:** aiming at a high-cover edge steps out 1.6 studs; aiming in low cover pops up. Blind fire is allowed (spread ×2). Peeking uses aimed accuracy. The muzzle must be reachable from the head (direct, or raised over low cover); shots from inside a wall are refused.
- **Reload** works in cover. **Leave:** V, pull back (S), dive, or the wall is no longer behind you (server check, 0.5 s grace).
- Cover blocks bullets and bullet-time line of sight through the normal raycasts. No invulnerability.
- Not yet: cover-to-cover moves, a HUD prompt when cover is available, vaulting.

## Update — back-to-wall cover (2026-10-30, supersedes the cover description above)
- **Posture:** back to the wall, facing away from it (Max Payne 3 style). The character eases onto the wall and turns smoothly; no snap.
- **Movement:** A/D slide along the wall; the ends of the wall stop you. **No corner wrapping** (removed: too snappy).
- **Peek and shoot:** aim at a high-cover edge → lean 1.6 studs out and turn to the target; aim in low cover → pop up and turn to the target. Aimed accuracy applies only while the head is actually clear of the wall (server check).
- **Blind fire:** fire without peeking → gun held over low cover or around a high-cover edge, body stays in cover, spread ×8.
- Leave cover: V, pull back (S), or dive.
