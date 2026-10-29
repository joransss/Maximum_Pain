# Networking and Security — Reference Notes

Sources:
- https://create.roblox.com/docs/scripting/events/remote
- https://create.roblox.com/docs/scripting/security/client-server-boundary

## Rules
- Server owns authoritative gameplay state: damage, ammo, reload, cooldowns, score, currency, objectives and match result.
- Client owns presentation and input capture, then sends requests.
- Validate every client request: type, structure, range, permissions, player state, timing and rate.
- Do not accept arbitrary Instances, paths, module names or client-provided damage values as authority.
- Treat the server as a gatekeeper, not a blind relay.
- Avoid synchronous RemoteFunction calls where a RemoteEvent or replicated state is sufficient.
- Keep remote names and payload schemas documented in the architecture notes.

## Security test examples
- Send malformed payloads and unexpected types.
- Attempt to fire while dead, reloading, unarmed or out of ammo.
- Spam ability activation and weapon fire.
- Attempt to damage teammates or players through static walls.
- Attempt to award score or currency from a client request.
