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
