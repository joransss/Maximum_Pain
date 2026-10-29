# Shoot Dodge

## Design Goal
A fast directional dive that helps players cross exposed space or break an opponent's aim, with a meaningful recovery cost.

## Proposed Rules
- Triggered by a dedicated input.
- Direction derives from movement input, with a documented fallback when no direction is pressed.
- Has a cooldown and/or recovery window.
- Prevents repeated activation while active.
- Animation and movement should agree on the dive direction.
- Server validates ability state and timing.
- Optional later feature: allow aiming/firing while prone after the dive, with slower movement and a clear exposure risk.

## State Machine
**Ready → Diving → Prone/Recovery → Ready**

Possible cancellation states: death, character removal, round reset.

## Implementation Tasks
- [ ] Define input and direction rules
- [ ] Create animation placeholder
- [ ] Implement movement impulse or controlled trajectory
- [ ] Prevent repeated activation
- [ ] Define weapon firing restrictions during dive
- [ ] Prototype prone aiming/firing only after normal dive works
- [ ] Add cooldown feedback
- [ ] Test stairs, walls, slopes and ledges
- [ ] Test latency and exploit attempts

## Balance Questions
- Can the player change direction mid-dive?
- How long is recovery?
- Does the dive reduce incoming damage? If yes, by how much and for how long?
- Can players dive through narrow gaps or into unintended areas?
- Does prone shooting reward good timing without becoming a safe camping stance?
