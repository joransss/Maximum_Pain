# RemoteEvents

## Remote Inventory
| Remote | Direction | Purpose | Validation |
|---|---|---|---|
| `FireWeapon` | Client → Server | Request a shot | Weapon, ammo, cadence, origin and direction |
| `ReloadWeapon` | Client → Server | Request reload | Equipped weapon, ammo state, reload state |
| `RequestAbility` | Client → Server | Request dive, Bullet Time or tactical ability | Ability unlocked, alive, cooldown/resource |
| `MatchStateChanged` | Server → Client | Publish phase / result state | Server-originated state only |
| `CombatEvent` | Server → Client | Publish validated hit/kill/callout data | Server computes the event and score |
| `RequestCosmeticAction` | Client → Server | Request equip/open case action | Ownership, balance, policy eligibility, valid case |

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
| | | | |
