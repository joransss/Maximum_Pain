# Test Cases

## Combat
- [ ] Fire with ammo
- [ ] Attempt to fire with no ammo
- [ ] Reload full magazine
- [ ] Reload while firing
- [ ] Die during reload
- [ ] Repeated fire requests are rate-limited
- [ ] Invalid remote payload is rejected
- [ ] Solid cover blocks weapon hits

## Movement and Abilities
- [ ] Sprint start/stop
- [ ] Dive on flat ground
- [ ] Dive near walls and ledges
- [ ] Prone shooting only becomes available in the intended state
- [ ] Activate Bullet Time at zero charge
- [ ] Bullet Time affects only eligible sightline-connected players
- [ ] Cover blocks Bullet Time raycasts
- [ ] Chain depth/radius caps prevent server spikes
- [ ] Two overlapping Bullet Time activations resolve deterministically
- [ ] Spam ability remote
- [ ] Die while ability is active
- [ ] Respawn after ability use
- [ ] Last Stand succeeds/fails correctly at timeout and simultaneous lethal damage
- [ ] Dual-wield shots obey ammo and fire cadence

## Environment and Camera
- [ ] Breakable prop state matches on all clients
- [ ] Destruction does not spawn unlimited debris
- [ ] Broken cover updates bullet and sightline checks
- [ ] Kill camera can be skipped
- [ ] Camera control returns after death, respawn, disconnect or round transition

## Multiplayer and Modes
- [ ] Two clients damage one another
- [ ] Scores increment exactly once
- [ ] Objective updates and round transitions are server-authoritative
- [ ] High-value target assignment and scoring are consistent
- [ ] Disconnect during a round
- [ ] Round ends on timer
- [ ] Round ends on score limit
- [ ] Reset clears temporary state

## Progression and Monetisation
- [ ] Currency is granted once for validated match events
- [ ] Client cannot alter currency balance
- [ ] Case cannot be opened with insufficient funds
- [ ] Case reward and currency deduction are atomic
- [ ] Owned cosmetics persist correctly
- [ ] Paid-random-item odds and policy restrictions are implemented before Robux-funded cases launch

## Performance
- [ ] Test at intended player count
- [ ] Check server and client frame rate
- [ ] Check remote traffic
- [ ] Check effects cleanup
- [ ] Test line-of-sight graph cost in dense fights
