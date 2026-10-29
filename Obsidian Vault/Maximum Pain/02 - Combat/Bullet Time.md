# Bullet Time

## Design Goal
A short, tactical slow-motion ability inspired by cinematic third-person shooters. It must affect local combat rather than slowing the whole Roblox server simulation.

## Multiplayer Model: Line-of-Sight Chain
The reference design uses a line-of-sight effect that can spread through connected sightlines. For this game, implement the rule explicitly and test it:
1. The server validates activation, charge, cooldown, alive state and duration.
2. Find eligible opponents within a defined radius and raycast from the activator to check clear line of sight.
3. Build a bounded visibility graph: a visible affected player may connect the effect to another eligible player they can see. Cap chain depth/radius and recalculate periodically to control performance.
4. Apply the slow to affected opponents' movement and weapon handling. The activator gets the designed handling advantage, not global immunity to all combat rules.
5. Recalculate sightlines; cover or sufficient distance can break a connection. End the effect when the timer expires, the resource runs out, or the user dies/round ends.

**Important:** Do not change global `Workspace` time or assume the server simulation itself can be slowed safely. Keep authoritative damage, ammo, fire cadence and hit validation on the server. Client-side camera, colour grading, sound and motion effects are presentation only.

## Prototype Defaults to Test
- Duration: 3 seconds
- Resource: meter gained from combat; activation requires a full or minimum threshold
- Cooldown: start after the effect ends; tune with playtests
- Slow amount: begin around 50% movement/handling speed for affected opponents, then balance
- Chain: only opponents connected by visible sightlines; cap graph radius and number of hops
- Telegraph: distinctive audio/visual cue so opponents know they are affected

These are starting values for testing, not final balance values.

## Implementation Tasks
- [ ] Define target eligibility, range and team rules
- [ ] Server validates activation and resource/cooldown
- [ ] Implement line-of-sight raycasts and bounded chain search
- [ ] Separate movement slowdown from weapon fire/reload slowdown
- [ ] Keep damage and hit validation server-authoritative
- [ ] Add client presentation and cleanup
- [ ] Handle cover, death, respawn, disconnect and round reset
- [ ] Measure server cost with maximum intended player count

## Exploit and Fairness Checks
- [ ] Client cannot choose arbitrary targets or slowdown values
- [ ] Repeated remote calls cannot bypass cooldown
- [ ] Walls block sightlines consistently
- [ ] Clients cannot claim damage based on locally slowed visuals
- [ ] No effect remains after death or round reset
- [ ] High latency does not make the effect unpredictable

## Test Scenarios
- Activator sees B; B sees C; verify whether the chain reaches C according to the defined graph rule.
- A player behind solid cover is not connected through that wall.
- A player exits the radius or breaks line of sight and is removed according to the chosen grace period.
- Two opposing activations overlap; precedence and refresh rules are deterministic.
- A full server can use the ability without frame-rate or remote-event spikes.

## Open Decisions
- Does the chain include teammates, opponents only, or both?
- Is line of sight checked from head, torso, or camera/aim point?
- Is there a short grace period after sightline breaks?
- Does the activator retain normal reload speed, firing speed, or both?
