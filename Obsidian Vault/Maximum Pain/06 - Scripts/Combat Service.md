# Combat Service

## Purpose
Server-side validation and application of weapon damage.

## Responsibilities
- Validate shot requests
- Verify player and weapon state
- Enforce fire rate and ammunition
- Calculate / verify hit result
- Apply damage once
- Notify match scoring when an elimination occurs

## Security Checklist
- [ ] Never accept client-provided damage as authoritative
- [ ] Validate types, finite numbers and vector magnitude
- [ ] Enforce range and cadence
- [ ] Verify character is alive
- [ ] Avoid duplicate hit processing
- [ ] Rate-limit malformed requests

## Code
```lua
-- Add implementation after weapon protocol is defined.
```
