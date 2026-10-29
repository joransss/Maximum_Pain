# Round Manager

## Responsibilities
- Track lobby, countdown, active match and results phases
- Spawn eligible players
- Track time and score limit
- End the round once
- Publish match state to clients
- Reset temporary state before the next round

## State Machine
**Intermission → Countdown → In Progress → Results → Intermission**

## Rules
- Server owns phase transitions and final score.
- Round-ending conditions must be idempotent: they should not run twice.
- Handle player disconnects and low player counts.
- Decide how late joiners are treated.
- Reset cooldowns, ammo, temporary effects and score correctly.

## Test Cases
- [ ] Match starts with the required player count
- [ ] Timer ending the match triggers results once
- [ ] Score limit ending the match triggers results once
- [ ] Disconnect during combat does not break the round
- [ ] New round starts with clean state
