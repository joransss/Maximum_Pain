# Destructible Environments

## Goal
Add cinematic impact through a small number of authored breakable props.

## First Version
- Breakable glass panes
- Wooden cover that degrades or breaks after a damage threshold
- Small debris and sparks as client-side visual effects
- No fully destructible buildings or free-form physics destruction in the first release

## Technical Rules
- Server owns damage thresholds and whether a prop is destroyed.
- Replicate a compact state change; clients can render debris locally.
- Use object pooling or simple replacement states rather than spawning unlimited debris.
- Decide whether broken cover stays broken for the rest of the round or resets between rounds.
- Keep bullet obstruction and Bullet Time line-of-sight results consistent with the prop's current state.

## Tasks
- [ ] Create a reusable breakable-prop definition
- [ ] Validate damage and destruction on server
- [ ] Add intact/broken visual states
- [ ] Cap debris count and lifetime
- [ ] Test multiple clients seeing the same gameplay state
- [ ] Test reset behavior between rounds
