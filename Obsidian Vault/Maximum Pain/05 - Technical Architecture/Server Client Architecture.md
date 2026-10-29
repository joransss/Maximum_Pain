# Server Client Architecture

## Principle
The client handles responsive input and presentation; the server validates gameplay and owns authoritative results.

## Client Responsibilities
- Read input
- Control local camera
- Play local cosmetic effects
- Display HUD
- Send requests to the server

## Server Responsibilities
- Validate weapon ownership and ammunition
- Enforce fire rate and reload state
- Validate ability cooldowns and duration
- Calculate or verify hits
- Apply damage
- Own health, eliminations, scores and match state
- Save persistent progression

## Never Trust Client Claims
Do not let the client choose arbitrary damage, target health, score, cooldown duration or match outcome. Treat every RemoteEvent payload as untrusted input.

## Network Review Checklist
- [ ] Validate argument types and ranges
- [ ] Rate-limit remote requests
- [ ] Verify player is alive and eligible
- [ ] Verify equipped weapon and ammo
- [ ] Reject impossible origin / range / fire cadence
- [ ] Clean up state on death and disconnect
