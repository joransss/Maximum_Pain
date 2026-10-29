# Objective Chain Mode

## Concept
A multi-round team mode where the outcome of one round changes the next objective. This captures the feeling of an evolving conflict without copying any specific game's narrative or map sequence.

## Example Match Flow
1. Round 1: attack or defend a weapons cache.
2. Round 2: the winner must escort or secure the cache while the opposing team attempts to recover it.
3. Round 3: both teams fight for control of a final extraction point.

## Rules
- Keep objectives simple and legible: capture, defend, escort, recover.
- The round manager owns objective state, score and phase changes.
- Teams should have a comeback path; early wins must not make later rounds automatic.
- Start with two objective types and a single map before adding a full chain.

## Tasks
- [ ] Define objective state machine
- [ ] Add clear UI for current objective and win conditions
- [ ] Handle ties, timeouts, disconnects and round resets
- [ ] Playtest attacker/defender balance and spawn safety
