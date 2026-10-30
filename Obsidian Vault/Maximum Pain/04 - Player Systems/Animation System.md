# Animation System

## Required Animations
- Idle / locomotion
- Sprint
- Aim / weapon hold
- Fire and reload
- Jump / fall / land
- Shoot-dodge
- Hit reaction
- Death

## Notes
- Use original or properly licensed animations.
- Decide which animations are local presentation and which must replicate.
- Keep animation state aligned with gameplay state.
- Avoid animations that obscure enemy visibility or aim feedback.

## Integration
- [[Player Movement]]
- [[Camera System]]
- [[Gunplay]]
- [[Shoot Dodge]]

## Implemented: procedural combat poses (2026-10-30)
`StarterPlayerScripts.PoseController` writes `Motor6D.Transform` after the default animations each frame, for every character on each client (R6 and R15). It is driven by replicated state, so other players see the same poses:
| State | Pose |
|---|---|
| Weapon out (hip) | Gun arm points at the aim, one-handed |
| Aiming (right mouse) | Both hands on the gun, head follows the aim |
| Diving / prone | Arms stretched ahead of the head, legs together |
| Aiming while diving / prone / Last Stand | Arms on the aim from the lying body |
| Firing | Gun arm kicks up ~12° and recovers in 0.15 s |
- Inputs: `Aiming` / `CombatState` / `AimDir` attributes (server-set) for others; local input for your own character.
- Blends over ~0.15 s; the default Animate script still drives locomotion.
- **Still needed (authored R6 animations):** reload, hit reaction, landing roll, get-up, death.

### Added poses (2026-10-30)
| State | Pose |
|---|---|
| Reload | Gun in front of the chest; support hand: to the gun → fetch magazine → insert → rack (phases in `WeaponConfig.ReloadPose`, timed by the server) |
| Dive run-up | Torso leans into the dive direction |
| Get-up | Hands push toward the ground while the humanoid stands up |
| Sprint | Forward lean, gun carried low across the body |
| Crouch / low cover | Low lunge (R6 has no knees), stride while moving, slight lean |
| Cover (not firing) | Gun up at the chest, two hands; firing switches to blind-fire hip aim |
Priority order: [[Combat State Machine]].

### Cover poses (updated 2026-10-30)
| State | Pose |
|---|---|
| In cover, idle | Back to the wall, gun up beside the head, two hands |
| Peeking (aiming at an edge / over low cover) | Body leans out or pops up, turns to the target, two-handed aim |
| Blind fire | Body stays in cover; gun arm held over low cover or around a high-cover edge toward the target |
Verified on screen 2026-10-30 (hip, aim, sprint, crouch, high cover, peek, blind fire, low cover, pop-up).
