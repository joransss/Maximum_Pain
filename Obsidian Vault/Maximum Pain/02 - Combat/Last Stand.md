# Last Stand Recovery

## Design Goal
Create a rare, dramatic chance to reverse a lethal encounter without making eliminations feel unreliable.

## Proposed Rule
When a player receives lethal damage, they may enter a brief Last Stand state if they have a recovery charge. During this state, they can attempt to eliminate the attacker. If successful within the window, they survive with a small amount of health; otherwise, they are eliminated when the window ends.

## Constraints
- One charge per life or a long cooldown; test both options.
- The state must be clearly telegraphed to both players.
- Do not grant invulnerability indefinitely. Define exactly which damage can end the state.
- Server controls the state, timer, charge consumption and final outcome.
- Exclude from competitive modes if it makes trades or kill confirmation too inconsistent.

## Tasks
- [ ] Define trigger and eligible damage sources
- [ ] Create clear downed/Last Stand animation and UI
- [ ] Implement short server-owned timer and attacker attribution
- [ ] Decide whether a successful counter restores health or only prevents death
- [ ] Prevent duplicate eliminations and score awards
- [ ] Test latency, simultaneous lethal damage and round-end interactions
