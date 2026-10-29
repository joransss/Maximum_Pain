# Game Modes

## Prototype Recommendation: Free-for-All
**Why:** Simplest way to prototype and test combat without team balancing.

### Rules
- Players spawn at approved spawn points.
- Each elimination grants one point.
- Match ends when the timer expires or a score limit is reached.
- Highest score wins; ties use a documented rule.

### Required Systems
- [[Round Manager]]
- [[Teams and Spawning]]
- [[Kill Feed and Scoreboard]]
- [[Health and Damage]]

## Later: Team Deathmatch
- Two teams
- Team score increments on eliminations
- Friendly-fire policy clearly defined
- Spawns avoid direct enemy line of sight

## Later: Objective Chain Mode
See [[Objective Chain Mode]]. Round outcomes change the next objective, such as capture, defend, recover or extract.

## Later: High-Value Target Mode
See [[High Value Target Mode]]. One or two players become targets while others hunt them. Keep target durability and location information fair.

## Mode Acceptance Criteria
- Match starts and ends reliably
- Players joining late are handled intentionally
- Deaths and eliminations count exactly once
- Round reset clears temporary state
- Objectives and target markers cannot be exploited through client requests
