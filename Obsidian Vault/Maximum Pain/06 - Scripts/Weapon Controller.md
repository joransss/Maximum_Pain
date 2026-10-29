# Weapon Controller

## Purpose
Handle local weapon input and presentation while requesting validated shots from the server.

## Likely Location
`StarterPlayerScripts` or a client-side controller ModuleScript, depending on architecture.

## Client Responsibilities
- Read fire and reload input
- Show immediate cosmetic muzzle flash and recoil
- Send a shot request with minimal necessary information
- Display ammo and reload state from validated game state

## Server Responsibilities
See [[Gunplay]] and [[Server Client Architecture]].

## Implementation Tasks
- [ ] Define weapon configuration
- [ ] Bind fire input
- [ ] Add local firing presentation
- [ ] Request shot from server
- [ ] Receive validated ammo / reload state
- [ ] Handle unequip and death
- [ ] Test remote spam and latency

## Code
```lua
-- Add implementation after the architecture is decided.
```
