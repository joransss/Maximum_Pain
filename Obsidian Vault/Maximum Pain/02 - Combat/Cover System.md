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
