# Cinematic Kill Camera

## Goal
Occasionally highlight a round-ending elimination with a short replay-like camera presentation.

## Recommended Scope
Start with a brief kill-cam presentation, not a full replay recorder. On the final elimination, the server sends validated killer/victim/weapon metadata and clients present a short camera transition using existing character positions or a simple authored camera angle.

## Rules
- Keep it short (about 2–3 seconds as a starting point) and allow players to skip it.
- Never delay respawns or round transitions for ordinary kills.
- Avoid showing information the player should not know, such as hidden enemy positions.
- Do not trust the client to award kills or decide match results.
- If actual replay playback is added later, record compact server-validated events and test network/replication limits.

## Tasks
- [ ] Trigger only on final elimination or selected highlights
- [ ] Add skip input and settings toggle
- [ ] Return camera control reliably after death/respawn
- [ ] Test disconnects and round transitions during the camera sequence
