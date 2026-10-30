# RemoteEvents

## Remote Inventory
All live in `ReplicatedStorage.Remotes`. Client → server remotes pass through a per-player rate limit in `CombatMain` before any handler runs.

| Remote | Direction | Payload | Validation | Rate limit |
|---|---|---|---|---|
| `FireWeapon` | Client → Server | origin, direction | Finite vectors; alive; weapon equipped; not reloading; origin ≤ 10 studs from head and not behind a wall; cadence (bullet-time scaled); ammo | 15/s |
| `ReloadWeapon` | Client → Server | — | Alive; weapon equipped; not reloading; magazine not full; reserve > 0 | 4/s |
| `RequestDodge` | Client → Server | direction | Finite, horizontal, non-zero; alive; no active combat state; 1.5 s cooldown | 4/s |
| `RequestGetUp` | Client → Server | — | Alive; state is Diving or Prone | 4/s |
| `RequestBulletTime` | Client → Server | — (toggle) | Alive; not a victim; not in Last Stand; cooldown; meter ≥ cost; someone in view | 4/s |
| `UseMedicine` | Client → Server | — | Alive; not downed; has medicine; not full health; 1 s cooldown | 4/s |
| `SetAiming` | Client → Server | aiming (boolean) | Boolean; alive with a weapon equipped to start aiming; sets `Aiming` and walk speed | 10/s |
| `AimDirection` (UnreliableRemoteEvent) | Client → Server | unit look vector, at most 10 Hz | Finite and unit length; presentation only (sets `AimDir` for remote poses), never used for shots | 20/s |
| `RequestStance` | Client → Server | "Stand" / "Sprint" / "Crouch" / "Cover", optional direction | String; CharacterStates rules; cover = server raycast + height check; stand/sprint need overhead clearance | 8/s |
| `ShotEffects` | Server → Client | shooter, origin, velocity, range | Server-accepted shots only, sent to other players | — |
| `ImpactEffects` (UnreliableRemoteEvent) | Server → Client | flesh?, position, normal, surface | Server bullet hit points only; drawn as bullet holes or blood | — |
| `CombatFeedback` | Server → Client | `{ kind, ... }`: Hit, Downed, Kill, Pickup, Healed, LastStand, Recovered, Message | Server-computed events and score | — |
| `MatchStateChanged` | Server → Client | Phase / result | Server-originated state only | Planned |
| `RequestCosmeticAction` | Client → Server | Equip / open case | Ownership, balance, policy eligibility | Planned |

Pickups use server-side `ProximityPrompt`s (no remote).

## Rules
- Use clear names and narrow responsibilities.
- Do not pass arbitrary Instance references unless necessary and validated.
- Keep payloads small.
- Add rate limits.
- Never trust a client to award currency, damage, eliminations or case rewards.
- Case outcome and inventory grant must be decided atomically on the server.
- Document every new remote here.

## Change Log
| Date | Remote | Change | Reason |
|---|---|---|---|
| 2026-10-30 | FireWeapon, ReloadWeapon, RequestDodge, RequestGetUp, RequestBulletTime, UseMedicine, ShotEffects, CombatFeedback | Added | Combat sandbox (see [[Implementation Log]]) |
| 2026-10-30 | RequestAbility | Split into RequestDodge / RequestGetUp / RequestBulletTime | Narrow responsibilities, per-remote rate limits |
| 2026-10-30 | SetAiming, AimDirection | Added | Server-owned aiming (spread/move penalty) and replicated aim poses |
| 2026-10-30 | RequestStance | Added | Server-owned sprint, crouch and cover |
| 2026-10-30 | ImpactEffects | Added (Server → Client, unreliable) | Bullet holes and blood at server hit points |
