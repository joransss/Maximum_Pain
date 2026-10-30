# Combat Architecture and Implementation Plan

> [!summary] Locked direction
> **Rig changed to R15 on 2026-10-30** (user decision; standard body for all players, Blender-authored clips — see [[Animation System]]). R6 references below are historical.
>
> Maximum Pain is an R15 multiplayer third-person shooter focused on Max Payne-inspired cinematic combat. Use directional shoot-dodge, hybrid bullet time (personal presentation with limited shared gameplay effects), and a full weapon arsenal. Treat these as current design decisions unless playtesting reveals a strong reason to revise them.

## Design pillars

1. **Responsive gunplay** — fast target acquisition, readable recoil, distinct weapon handling and clear hit feedback.
2. **Signature movement** — a directional shoot-dodge that permits airborne firing and has a defined recovery window.
3. **Cinematic bullet time** — dramatic local presentation and a bounded, server-controlled gameplay benefit without globally slowing the simulation.
4. **Multiplayer fairness** — the server validates damage, ammunition, fire rate, ability use and competitive state transitions.
5. **One standard R15 body** — everyone shares the default R15 body and scale (own clothes and accessories), so authored poses, weapon attachments, hit reactions, movement and hitboxes are consistent. (Was "R6-first" until 2026-10-30.) Feel benchmark: [[Max Payne 3 Animation Reference]].

## Combat architecture

### Client responsibilities

- Read input and send requests to the server.
- Present camera movement, local recoil, crosshair, muzzle flash, sound, UI and responsive animation.
- Optionally predict non-authoritative presentation, while reconciling with server-confirmed results.
- Never decide authoritative damage, ammunition, cooldowns or eliminations.

### Server responsibilities

- Validate and execute weapon fire, ammo consumption, reload completion, damage and eliminations.
- Validate dodge eligibility, direction, movement limits and cooldowns.
- Own bullet-time resource, activation duration and shared effects.
- Validate state transitions and clean up actions on death, respawn, character removal and disconnect.
- Rate-limit remote requests and reject malformed, stale or implausible payloads.

### Proposed module boundaries

| Module | Responsibility | Suggested location |
|---|---|---|
| `CombatController` | Client input and combat-state presentation | `StarterPlayerScripts` |
| `CameraController` | Shoulder camera, aiming, recoil, FOV and cinematic effects | `StarterPlayerScripts` |
| `MovementController` | Sprint, dodge input and client movement presentation | `StarterPlayerScripts` |
| `WeaponController` | Weapon input, local feedback, reload and switching requests | `StarterPlayerScripts` |
| `CombatHUD` | Health, ammo, crosshair and bullet-time meter | `StarterGui` / client controller |
| `WeaponConfig` | Shared, non-secret weapon tuning data | `ReplicatedStorage` |
| `CombatService` | Server-side combat orchestration and validation | `ServerScriptService` |
| `WeaponService` | Ammo, fire rate, raycasts, reloads and damage | `ServerScriptService` |
| `DodgeService` | Eligibility, movement bounds, cooldown and replication | `ServerScriptService` |
| `BulletTimeService` | Resource, activation and shared gameplay rules | `ServerScriptService` |
| `CombatEffects` | Reusable local/replicated visual effects | Shared assets plus client controller |

These are proposed boundaries, not a requirement to create every module immediately. Inspect existing project scripts and extend them rather than duplicating systems.

## Combat state machine

Use a central state controller to prevent incompatible actions from running concurrently. Suggested states:

- `Idle`
- `Aiming`
- `Firing`
- `Reloading`
- `Sprinting`
- `ShootDodging`
- `Recovery`
- `InCover` (only if the cover feature is retained)
- `Dead`

Bullet time is an ability layer that may overlap with aiming, firing or dodging according to explicit rules; it should not be a competing movement state by default.

Rules:

- Death overrides all active combat states.
- Reloading blocks firing unless a later design explicitly supports interruption.
- Shoot-dodge temporarily controls movement and has a defined end and recovery.
- Every timed action must clean up after death, respawn, character removal and disconnect.
- Server validation is required for competitive state transitions.
- UI and animation should reflect authoritative state without excessive remote traffic.

## Combat diving — detailed specification

### Core design rule

Combat diving is a **free-angle, committed movement action**. The player can dive in any horizontal direction, not just the four cardinal directions or the character's facing direction. Colliding with a wall, prop or other solid object must **not cancel the dive state or snap the player back to standing**. The dive continues for its authored duration; the movement controller resolves the collision while keeping the dive active.

This is not a permission to pass through solid geometry. Unless level design explicitly introduces a breakable/penetrable obstacle mechanic, the character must remain blocked by walls. On contact, remove the component of movement pushing into the surface and preserve the tangential component, allowing the character to slide along it. This prevents collision from cancelling the move while avoiding wall-clipping and exploit-friendly noclip.

### Direction selection — any angle

1. Read the current movement input vector and the camera's horizontal forward/right vectors.
2. Convert input into world space: `direction = cameraRight * input.X + cameraForward * input.Y`.
3. Flatten the vector to the horizontal plane and normalize it. This allows any angle across the full 360-degree horizontal plane, including diagonals and backwards/sideways dives.
4. If there is no meaningful movement input, use the player's current horizontal movement direction; if that is also near zero, use the camera's horizontal forward direction.
5. Send the desired direction to the server. The server checks that it is finite, approximately horizontal and non-zero after fallback; it clamps/normalizes it rather than trusting a client-provided speed or impulse.
6. Orient the dive animation and torso/weapon presentation to the selected direction. The camera may keep looking toward the aim target, so movement direction and firing direction are independent.

Do not quantize the direction to four or eight directions. Animation can blend between directional poses or use a best-fit directional dive animation, but movement must retain the full vector.

### Movement and collision handling

Prefer a dedicated dive movement controller over repeatedly applying uncontrolled impulses. The server validates and owns the action timing and bounds; the client may predict the initial pose and camera response for responsiveness.

- Enter `Diving` once eligibility is accepted. Start the dive timer and animation independently of collision contacts.
- Drive the character toward a configured horizontal velocity/trajectory for the dive window. Tune the trajectory with the R6 rig and actual map scale.
- Detect/block solid geometry through the normal character collision system or a controlled sweep/raycast ahead of the root. Do not disable all character collisions for the dive.
- On a collision, keep the dive timer and animation running. Remove only velocity into the collision normal, preserve tangential velocity and continue the remaining trajectory where space permits.
- If fully blocked by a flat wall, the character can remain pressed against it for the remainder of the dive, but the action does not terminate early. Do not teleport through the wall or repeatedly force the root into it.
- Keep collision handling stable around corners, doorframes, stairs, ledges and low ceilings. Avoid repeated raycast jitter by using a small contact tolerance and consistent surface-normal handling.
- At the end of the dive window, transition to `DiveRecovery` and restore normal movement control. Collision alone must never trigger this transition.
- Death, respawn or character removal may cancel the action. Ordinary world collisions may not.

If the project later decides that diving should smash through specific props, implement that as an explicit tagged-object mechanic with server validation; do not generalize it to every collidable object.

### Shooting during the dive

- Allow aiming and firing while diving, subject to normal server-owned weapon, ammo, fire-rate, reload and line-of-fire checks.
- Keep aim direction separate from dive direction. A player may dive left while shooting forward, or dive backwards while aiming at a pursuing enemy.
- Do not let the dive animation or camera roll alter the authoritative shot origin/direction calculation.
- If reloading is not intended to be interruptible, block the dive while reloading. If the design chooses to interrupt reloads, cancel the reload on the server and preserve ammo rules; decide this once and test it consistently.
- Ensure muzzle-to-target obstruction is checked so the player cannot shoot through the wall they are sliding against.

### Initial tuning hypothesis

| Parameter | Prototype value | Notes |
|---|---:|---|
| Dive duration | 0.65 s | Collision does not shorten this duration |
| Recovery | 0.35 s | No new dive during recovery |
| Cooldown | 1.5 s | Server enforced from a clearly defined start/end point |
| Horizontal speed target | 45 studs/s | Starting point; tune with actual collision response |
| Vertical lift | 12 studs/s | Optional arc; avoid excessive launch over cover |
| Collision behaviour | Slide along surface | Preserve action; never clip through ordinary geometry |

These are prototype values, not final balance. Keep them in `DodgeConfig`. Test every direction at full and diagonal input, with and without movement input, while firing, and against walls/corners/props under latency. Acceptance criteria: a wall collision can stop forward progress, but never ends the dive animation/state early; the character never crosses an ordinary solid wall.

## Bullet time — line-of-sight targeting specification

### Core design rule

Bullet time is a **selective, line-of-sight effect**, not a global time stop. When activated, it may affect only eligible combatants the activating player can currently see with a clear line of sight. A target behind a wall, around a corner, or fully occluded by solid world geometry must not be slowed just because it is nearby. Do not slow every player, all NPCs, the whole server, or global physics.

Keep three concepts separate:

1. **Activator presentation:** the activating player's camera, colour treatment, audio mix and HUD can enter a cinematic bullet-time presentation locally.
2. **Visible target effects:** only characters passing the line-of-sight test receive the gameplay slow effect, and only while they remain eligible and visible.
3. **Unaffected world:** the activator, unseen characters, unrelated physics objects and global simulation remain at normal time unless a future, separately specified mechanic explicitly says otherwise.

### Target acquisition and line-of-sight rules

The server must be authoritative for which targets receive gameplay effects. The client can show immediate local activation feedback, but cannot submit a trusted list of targets to slow.

1. On activation, validate the player's alive state, resource, cooldown and allowed combat state.
2. Build candidate targets within a configured maximum range. Candidates are other living combatants/NPCs; exclude the activator, dead characters, allies if team rules require it, and entities that are not eligible for bullet time.
3. For each candidate, test that it is within the activator's allowed view cone and has a clear raycast path from an appropriate origin near the camera/character to a target point on the character (for example, upper torso). The exact view-cone rule is a design choice: use the camera's look direction if aiming should define vision, or the character's facing direction if not.
4. Use `RaycastParams` to exclude the activator's own character and non-blocking visual effects. Solid map geometry must block line of sight. Define transparent/see-through objects intentionally rather than assuming all transparent parts are non-occluding.
5. Only targets that pass both range and line-of-sight checks enter the affected set. A target that is visible at activation but then moves behind cover should stop being affected after the next server visibility update. A newly visible target may join while the ability remains active if the design enables continuous acquisition; recommended default: yes, acquire and release targets continuously during the active window.
6. Recheck visibility at a controlled interval rather than every render frame. Start around 10 checks per second for the prototype, then profile server cost and tune. Use per-target checks with a hard maximum candidate count and range cap.
7. Replicate the resulting affected target IDs/state to relevant clients so the target and nearby observers can render coherent effects. Treat this replicated state as presentation; server logic remains authoritative.

**Occlusion rule:** if a wall blocks the ray, that target is not affected even if their character is partially visible around an edge. For a later refinement, test multiple body points (head/upper torso/lower torso) and count the target visible if at least one permitted point has an unobstructed ray. Start with one upper-torso point for simpler, predictable behaviour.

### What “slowed” means in Roblox

Roblox does not provide a safe per-character global time-scale switch that automatically slows every subsystem. Do not attempt to change global physics speed. Implement a controlled gameplay modifier for affected characters instead:

- Reduce eligible targets' movement speed while affected, then restore the exact pre-effect baseline when they leave the affected set or bullet time ends.
- If jumping, acceleration or other movement parameters are changed, store and restore their baselines safely. Avoid overwriting changes made by another buff/debuff while bullet time is active; use a modifier/composition layer rather than blindly resetting hardcoded values.
- For NPCs, slow decision/update cadence and movement through the NPC controller where feasible.
- For player characters, decide explicitly which inputs/abilities are slowed. A practical first prototype is reduced movement speed and reduced NPC response cadence, while **weapon firing rate, projectile/hitscan resolution and server simulation remain authoritative and do not run at a different global clock**. If player weapon cadence is to be slowed, do so as a server-validated per-character modifier, not by changing the global server clock.
- Cosmetic animation playback speed may be adjusted locally for the affected target, but do not confuse a slowed animation with a gameplay slow. A character must not appear slowed while still moving and acting at full speed unless that is an intentional visual-only effect.
- Keep the activator's own movement and firing at normal simulation speed by default; the ability's power comes from slowing visible opponents, not from making the whole game slow.

A strong initial multiplayer rule is: **visible enemies are slowed; the activator and all occluded entities are not.** If the game has teams, decide whether friendly players are excluded; recommended default is to affect opponents only.

### Duration, resource and refresh behaviour

- The server owns the meter, activation start/end time, cooldown and active target set.
- Consume the activation cost only after the request is accepted. Drain resource on the server while active and end the effect immediately when duration/resource expires, the activator dies, or the character is removed.
- Recommended first prototype: maximum meter 100, activation cost 25, drain 15/s, maximum continuous activation 3 seconds. Values are provisional.
- Do not allow repeated activation requests to stack multiple slow modifiers. One activation should produce one active session and one modifier per target.
- When a target exits line of sight, restore its baseline promptly even if the activator's bullet time continues. When it re-enters line of sight during the same session, reapply once without stacking.
- On session end, death, respawn, disconnect or target removal, clear every effect and replicated state. Use a session/token ID or equivalent guard so an old delayed cleanup cannot cancel a newer session.
- If multiple players can activate bullet time simultaneously, define stacking explicitly. Recommended prototype rule: do not stack slow multipliers; apply the strongest permitted slow or use a priority/refresh rule, with deterministic server logic.

### Presentation and fairness

- The activator receives the strongest cinematic presentation: subtle FOV change, restrained colour grading, low-pass/filtered audio and meter feedback. Do not obscure enemies or reduce visibility.
- Affected targets can receive a modest local visual/audio cue, but do not make the cue reveal the activator's position through walls.
- Other players should see coherent target animation and movement effects only for entities actually affected. Avoid a global screen tint that suggests everyone is slowed.
- Add clear UI for activation, remaining resource and expiry. Give opponents enough responsiveness to understand that they are under an ability effect.
- Keep the ability bounded and test it in PvP. It must not bypass server fire-rate, damage, ammo or hit validation.

### Initial bullet-time tuning hypothesis

| Parameter | Prototype value | Notes |
|---|---:|---|
| Meter maximum | 100 | Server-owned |
| Activation cost | 25 | Charge only on accepted activation |
| Drain | 15 points/s | Server-owned |
| Maximum active window | 3 s | Hard cap for initial balance |
| Target range | 80 studs | Starting point; test arena scale |
| Visibility update | 10 Hz | Profile and cap candidate count |
| Target movement multiplier | 0.5× | Prototype only; restore baseline on release |
| Target acquisition | Continuous while active | Only if currently visible and eligible |

The numbers above are hypotheses. Keep them in `BulletTimeConfig`; test against different camera angles, cover, transparent geometry, multiple targets and simultaneous activations. Do not call this finished until line-of-sight acquisition/release and cleanup pass the acceptance tests below.

## Full weapon arsenal

Use one shared weapon framework and data-driven configuration. Start with three archetypes and expand only after their handling feels distinct.

| Archetype | Role | Design considerations |
|---|---|---|
| Pistol | Responsive baseline | Accurate semi-auto, quick handling; establishes core firing feel |
| Shotgun | Close-range burst | Multiple server-validated pellet rays, spread and slower reload |
| Assault rifle | Mid-range sustained fire | Automatic fire, manageable recoil and clear accuracy trade-offs |
| SMG | Mobile close-range pressure | Higher rate of fire, more recoil and movement compatibility |
| Precision rifle | Deliberate long-range shots | Slower follow-up shots and careful balance during dodge/bullet time |
| Dual pistols | Signature cinematic variant | Dedicated two-weapon animation/attachment setup and explicit ammo policy |

Recommended configuration fields:

- `Damage`
- `FireRate`
- `MagazineSize`
- `ReserveAmmo`
- `ReloadTime`
- `Range`
- `Spread`
- `Recoil`
- `Automatic`
- `PelletCount` (where relevant)
- `AimSpeed` or another clearly defined handling modifier

Use server-owned ammunition and fire-rate timing. Dual wielding requires dedicated attachment points, firing cadence and reload rules; do not assume duplicating the single-pistol model will make the animation work.

## Loadout packages, weapon drops and PvP-only scope

### Two mutually exclusive loadout packages

The core inventory is intentionally constrained to one of two packages:

- **Heavy + pistol (`HeavyAndPistol`):** exactly one heavy weapon, such as a shotgun, assault rifle, SMG or precision weapon, plus one pistol.
- **Dual pistols (`DualPistols`):** a paired pistol setup with **no heavy weapon**. Treat the pair as one package with its own firing/reload configuration, not two independent slots.

The server owns the inventory and enforces the package invariant after every spawn, equip, switch, pickup and drop. A player must not be able to combine dual pistols with a heavy weapon by rapidly switching, sending stale requests or racing two pickups. A heavy pickup while dual-wielding replaces the package and transitions to the heavy-plus-pistol package only when a compatible sidearm is available; otherwise use a clearly defined temporary pistol-only fallback or reject the pickup. A second heavy weapon replaces the current heavy weapon or is rejected. It never creates another slot.

### Drops from defeated players

When a player is eliminated, create world pickups for their actual carried weapons at a safe position near the elimination point:

- `HeavyAndPistol` creates a heavy-weapon pickup and a pistol pickup.
- `DualPistols` creates one paired-pistol pickup, not two separate pistols that could bypass the package rule.

Recommended prototype rules:

- Preserve the dropped weapons' remaining ammo; ammo and weapon identity are server-owned.
- The pickup prompt clearly indicates weapon type and whether taking it replaces an existing weapon/package.
- The server validates range, current pickup existence, line of sight/obstruction if required, loadout compatibility and replacement choice.
- Claiming a pickup is atomic: only one player can acquire it, and the weapon cannot simultaneously exist in the old inventory and the world.
- Give each elimination a unique drop ID/idempotency guard so duplicate death events cannot duplicate weapons.
- Unclaimed drops expire after an initial 30–45 seconds, then are destroyed. Profile this with the number of players and pickups expected per arena.
- Respawn uses the selected game-mode spawn package; it does not restore the weapons dropped on the previous life unless a future mode explicitly says so.
- If a player dies while carrying a looted weapon, drop their current package again under the same rules, with safeguards against duplicate drops and excessive world pickups.

Suggested server-side inventory fields: `LoadoutType`, `PrimaryWeaponId`, `SidearmWeaponId`, `DualPistolWeaponId`, server-owned ammo state, `EquippedSlot`, and `InventoryRevision`. Increment the revision after each successful inventory mutation and reject stale requests. Every mutation should preserve these invariants: a weapon has one owner/location; ammo is finite and non-negative; dual pistols and a heavy weapon never coexist; and an elimination creates its drops at most once.

### Explicitly PvP-only

**There is no PvE.** Do not build hostile NPCs, enemy bots or AI combatants as part of the core game. Target acquisition, damage, bullet-time visibility checks, kill credit, elimination statistics and weapon drops apply to eligible player characters only. Environmental props can obstruct bullets, block movement or provide cover, but are not combat targets. Training dummies or bots would require a deliberate design-scope change.

### Acceptance tests

- [ ] Both package types can be selected and are represented correctly on the HUD.
- [ ] No server-approved state can contain both a heavy weapon and dual pistols.
- [ ] Defeated players drop the correct package exactly once.
- [ ] Concurrent pickup requests cannot duplicate a weapon or ammo.
- [ ] Pickup replacement follows the package rules and never creates a hidden extra slot.
- [ ] Respawn follows the configured spawn package and does not restore dropped weapons unexpectedly.
- [ ] Bullet time and combat target selection never affect NPCs because no NPC combatants exist in scope.

## Networking contract

### Client-to-server requests

| Remote | Suggested payload | Server checks |
|---|---|---|
| `FireWeapon` | Weapon ID, aim direction, shot sequence | Equipped weapon, finite direction, ammo, fire interval, range and plausible origin |
| `ReloadWeapon` | Weapon ID | Equipped weapon, ammo state, current state and reload eligibility |
| `RequestDodge` | Desired direction | Alive state, cooldown, state eligibility and movement bounds |
| `RequestBulletTime` | Activation request | Resource, cooldown, alive state and ability rules |
| `SwitchWeapon` | Requested slot/weapon ID | Ownership, valid slot and switching restrictions |

### Server-to-client notifications

- `ShotEffects` — confirmed shot data needed for presentation.
- `CombatFeedback` — confirmed hit/elimination feedback.
- `DodgeEffects` — validated dodge event for other clients to animate.
- `BulletTimeEffects` — activation cues and relevant shared effects.

Keep payloads small, validate types and ranges, and rate-limit requests. Never accept client-reported damage or a client assertion that a target was hit. The server should perform or independently validate the hitscan raycast and apply damage. Start with current server positions; consider historical hitbox rewinding only if latency testing demonstrates a need and the design can support it safely.

## Camera and presentation

- Use an over-the-shoulder camera with a stable aiming point.
- Keep camera ray direction and muzzle direction conceptually separate: aim toward the camera target, then validate the muzzle-to-target path to reduce shooting through cover.
- Add recoil through camera and weapon/arm presentation without making aim unpredictably uncontrollable.
- Smooth FOV transitions and shoulder offsets; avoid excessive shake that hides targets.
- Camera collision must prevent clipping through walls, including during dives.
- Make hit feedback, kill feedback and shared bullet-time cues visible but brief.

## Implementation roadmap

### Milestone 1 — R15 foundation (was R6)

- [x] Confirm the character, scale and collision assumptions — *R15 standard body, 2026-10-30: HipHeight 2.19, standing head top 5.4, crouch drop 1.3 (head top ~3.8–4.0), lying root ~0.6 up*
- [ ] Implement third-person camera and reliable aim direction.
- [ ] Create central combat-state controller and cleanup rules.

### Milestone 2 — One complete weapon

- [ ] Implement server-validated hitscan firing.
- [ ] Add server-owned ammo, reload and weapon switching.
- [ ] Add recoil, muzzle flash, sound and hit feedback.
- [ ] Test with two Studio clients.

### Milestone 3 — Shoot-dodge

- [ ] Implement full 360-degree horizontal direction from camera-relative input, with sensible neutral-input fallback.
- [ ] Keep dive state/timer running through wall and prop collisions; slide along surfaces without clipping through geometry.
- [ ] Add dive animation and independent airborne aiming/firing — *R15 clips (windup / air / land / prone / recover, 4 directions) and aim layer implemented 2026-10-30, solo-tested; two clients pending*
- [ ] Test corners, doorframes, stairs, ledges, cooldowns, replication and interruption cleanup.

### Milestone 4 — Bullet time

- [ ] Add server-owned resource, duration and activation limits.
- [ ] Implement authoritative range + view-cone + raycast line-of-sight target selection.
- [ ] Recheck visibility during the active window; release targets immediately when occluded and avoid stacking modifiers.
- [ ] Implement personal cinematic effects and coherent cues for affected targets only.
- [ ] Confirm unseen targets, the activator and global server physics are not slowed.

### Milestone 5 — Arsenal expansion

- [ ] Add shotgun and automatic rifle using the shared framework.
- [ ] Add weapon-specific spread, recoil and reload behaviour.
- [ ] Add SMG, precision weapon and dual pistols after the baseline works.

### Milestone 6 — Production polish

- [ ] Add hit reactions, death presentation and optional ragdolls — *biggest gap against Max Payne 3 footage: reactions layer on top of movement, deaths keep momentum ([[Max Payne 3 Animation Reference]])*
- [ ] Profile effect and remote-event costs.
- [ ] Test latency, exploit resistance, balance and state cleanup.

## Acceptance tests

- [ ] Firing cannot exceed the configured rate or consume negative ammo.
- [ ] Client cannot award itself damage, ammo or eliminations.
- [ ] Shooting while diving works only when allowed and is server validated.
- [ ] Dodge cannot exceed configured movement bounds or bypass cooldown.
- [ ] Diving accepts any horizontal angle; diagonal, backward and sideways inputs are not quantized.
- [ ] Wall/prop collision does not cancel a dive early, and the character never clips through ordinary solid geometry.
- [ ] Bullet time affects only eligible targets with clear server-verified line of sight; targets behind walls/corners are unaffected.
- [ ] Targets leaving line of sight are restored promptly; re-entry does not stack modifiers.
- [ ] Death/respawn during reload, dive or bullet time leaves no stuck state or un-restored movement modifier.
- [ ] Bullet time does not globally slow server physics or affect the activator/unseen entities.
- [ ] Other clients see coherent dodge, shot and activation effects.
- [ ] Camera does not become trapped inside walls during aiming or diving.
- [ ] Shotgun pellet rays and all weapon hit checks are range-limited and server validated.
- [ ] Two-player Studio tests show acceptable feedback and no obvious replication desynchronisation.

## Official Roblox references

- [Camera](https://create.roblox.com/docs/workspace/camera)
- [Raycasting](https://create.roblox.com/docs/workspace/raycasting)
- [Remote events](https://create.roblox.com/docs/scripting/events/remote)
- [Client-server boundary](https://create.roblox.com/docs/scripting/security/client-server-boundary)
- [Security tactics](https://create.roblox.com/docs/scripting/security/security-tactics)
- [Network ownership](https://create.roblox.com/docs/physics/network-ownership)
- [Server authority](https://create.roblox.com/docs/projects/server-authority)
- [Animation editor](https://create.roblox.com/docs/animation/editor)
- [Humanoid](https://create.roblox.com/docs/reference/engine/classes/Humanoid)
- [[Technical Architecture Overview]]
- [[Combat State Machine]]
- [[Shoot-Dodge]]
- [[Bullet Time]]
- [[Weapon System]]
- [[Weapons and Recoil]]
- [[Server Authority Rules]]

## Design decision summary

**Locked direction:** R15 (was R6 until 2026-10-30); cinematic Max Payne-inspired combat; directional shoot-dodge; hybrid personal bullet-time presentation with limited shared gameplay effects; full arsenal. Prototype one pistol and one arena before expanding. Tune the sample values through multiplayer playtests rather than treating them as final requirements.

## Design updates — 2026-10-30 (supersede conflicting text above)

Decided by the project owner and implemented in Studio (see [[Implementation Log]]):

1. **Bullet time is asymmetric, and the activator is slowed too.** Time slows only if an enemy is in view of the activator or the activator is in view of an enemy. If nobody is in view, it does not trigger. The activator keeps free aim, but their movement, fire rate and bullet speed slow (×0.6). Everyone caught in view gets a total slowdown: movement, aim, fire rate and bullet speed (×0.3). Whoever activates first keeps activator status. This replaces "keep the activator's movement and firing at normal speed" and "the activator is not slowed". Per-character modifiers only; the global clock and physics still never slow.
2. **Dive landing: stay prone until input.** After the dive window the player stays prone (and can aim and fire) until a movement key is pressed, which triggers the get-up recovery. This replaces "at the end of the dive window, transition to DiveRecovery and restore normal movement control".
3. **Studio-only test dummy.** A non-attacking test dummy exists for sandbox testing of damage, HUD and bullet-time line of sight. It is a Studio-only exception to the PvP-only rule: live servers delete it, and it is never a combatant in shipped gameplay.
4. **Medicine** replaces "painkillers". Players drop all carried medicine and weapons on death.
5. **Shoot-dodge in bullet time runs in slow motion** (same distance, slower; velocities ×s, gravity ×s², durations ÷s).
6. **Aiming (ADS)** is a server-owned state that tightens spread and slows movement; recoil adds server-side bloom.
7. **Medicine is collected automatically** by walking over it.
8. **Sprint, crouch and cover are server-owned stances** with one shared rule set (`CharacterStates`). Crouch and low cover lower the real body (`HipHeight`) so server hitboxes match. Cover faces the wall, slides along it, rounds corners and peeks by stepping out at edges.
9. **Movement guard:** the server pulls back characters whose sustained speed exceeds their state's allowance.
10. **Cover is back-to-wall** (Max Payne 3 style) with peek-and-shoot at edges / over low cover and blind fire (spread ×8) otherwise; corner wrapping was removed.
11. **Impact effects** (bullet holes, blood) are drawn at the server's real hit points so they show the true spread.
