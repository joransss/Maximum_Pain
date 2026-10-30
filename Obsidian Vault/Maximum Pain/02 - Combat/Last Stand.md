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

## Implemented rules (2026-10-30)
- **Trigger:** lethal damage while carrying ≥ 1 medicine; once per life.
- 4 s window at 1 HP, knocked prone; the player can aim and fire. Banner and countdown shown to the downed player; the attacker sees "DOWNED".
- **Success:** killing the player who downed you consumes 1 medicine, restores 30 HP and awards +100 LAST STAND.
- **Failure:** timeout eliminates, with credit to the original attacker. **Any** damage while downed eliminates, with credit to whoever dealt it.
- Server owns the timer (session token), charge use and outcome. Toggle with `GameConfig.LastStand.Enabled`.
- Verified: entry and timeout. Not verified: comeback kill with two players, simultaneous lethal damage.
