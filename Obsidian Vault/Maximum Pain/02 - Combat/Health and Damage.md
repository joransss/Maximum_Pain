# Health and Damage

## Authority
The server is authoritative for health, damage, eliminations and respawn eligibility.

## Rules to Define
- Maximum health:
- Damage sources:
- Friendly fire:
- Damage falloff:
- Headshot rules:
- Spawn protection:
- Death and assist rules:

## Damage Flow
1. Client sends a fire request with limited shot information.
2. Server validates weapon, ammo, cadence and shot plausibility.
3. Server performs or verifies the hit calculation.
4. Server applies damage once.
5. Server updates elimination and score state.
6. Clients receive appropriate UI and cosmetic feedback.

## Test Cases
- [ ] Damage cannot be applied twice from one shot
- [ ] Client cannot choose arbitrary damage values
- [ ] Dead players cannot continue dealing damage
- [ ] Respawn restores the intended health state
- [ ] Round reset clears temporary combat state

## Implemented rules (2026-10-30)
- Max health 100; **no regeneration** (empty `Health` script in StarterCharacterScripts).
- **Medicine** (formerly "painkillers"): heals 40, 1 s cooldown, carry max 5, start with 0; **picked up automatically** by walking within 3.5 studs (map spawns refill after 30 s; death drops). Use with Q.
- Damage sources: server-simulated bullets only (9mm: 20 body, ×2 head). Accessories don't absorb shots.
- Low-health screen treatment at ≤ 25%. Last Stand: see [[Last Stand]].
- One elimination and one score award per life (`Eliminated` guard). Friendly fire / teams: not defined yet (everyone is an enemy).
