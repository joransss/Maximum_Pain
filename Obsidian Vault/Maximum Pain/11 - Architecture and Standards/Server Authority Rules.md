# Server Authority Rules

## Must be server-authoritative
- Damage and health changes caused by combat
- Ammo consumption and reload completion
- Weapon fire cadence and cooldowns
- Ability eligibility and resource spending
- Score, kill feed source events and match results
- Objective ownership and objective rewards
- Progression, currency, unlocks and purchases
- Respawn eligibility and match state

## Client may own
- Input capture and local camera
- Local crosshair and immediate cosmetic feedback
- Non-authoritative animation presentation, reconciled with replicated state
- UI layout and visual effects that do not determine outcomes

## Remote validation order
1. Confirm expected types and finite numeric values.
2. Confirm player and character state.
3. Confirm permission, equipment and range.
4. Confirm cooldown/rate limits.
5. Validate aim/target against server world state.
6. Apply server-owned rules.
7. Replicate the accepted result, not the raw client claim.

See [[Networking and Security — Reference Notes]].

## Implemented checks (2026-10-30)
Stance requests (sprint/crouch/cover) are validated by `CharacterStates` rules, server raycasts (cover), and server Blockcast (stand-up clearance). Posture and speed are server-set. A movement guard pulls back sustained over-speed. Shots require a muzzle reachable from the head. See [[RemoteEvents]] and [[Implementation Log]].
