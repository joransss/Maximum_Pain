# Multiplayer Match Loop

## Intended flow
1. Waiting for enough players.
2. Pre-match countdown.
3. Spawn players and initialise match state.
4. Active match: objectives, eliminations, scoring and timers.
5. End condition reached.
6. Results screen and rewards calculated by server.
7. Return to intermission and reset match-specific state.

## Match configuration
- Minimum players: TBD.
- Match duration: TBD.
- Score limit / objective rules: mode-specific.
- Team assignment and spawn protection: TBD.
- Disconnect and late-join behaviour: TBD.

## Required safeguards
- Server owns match state and score.
- Players cannot award themselves points.
- Spawns should avoid immediate line-of-sight kills where practical.
- Reset round state without wiping persistent progression.
- Test team balance, simultaneous end conditions and player disconnects.
