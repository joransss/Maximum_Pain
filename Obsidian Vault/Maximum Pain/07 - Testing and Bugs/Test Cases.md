# Test Cases

## Combat
- [x] Fire with ammo — 2026-10-30, Studio solo
- [ ] Attempt to fire with no ammo
- [ ] Reload full magazine
- [ ] Reload while firing
- [ ] Die during reload
- [x] Repeated fire requests are rate-limited — 2026-10-30, Studio solo
- [x] Invalid remote payload is rejected — 2026-10-30, Studio solo
- [ ] Solid cover blocks weapon hits

## Movement and Abilities
- [x] Sprint start/stop — 2026-10-30, Studio solo
- [x] Dive on flat ground — 2026-10-30, Studio solo
- [ ] Dive near walls and ledges — walls pass (2026-10-30); ledges not tested; diving out of cover works
- [ ] Prone shooting only becomes available in the intended state — prone + aim pose and firing work solo (2026-10-30)
- [ ] Activate Bullet Time at zero charge
- [ ] Bullet Time affects only eligible sightline-connected players
- [ ] Cover blocks Bullet Time raycasts — uses the same line-of-sight raycast as the dummy (wall blocks it); not tested with a second player
- [ ] Chain depth/radius caps prevent server spikes
- [ ] Two overlapping Bullet Time activations resolve deterministically
- [x] Spam ability remote — 2026-10-30, Studio solo
- [ ] Die while ability is active
- [ ] Respawn after ability use
- [ ] Last Stand succeeds/fails correctly at timeout and simultaneous lethal damage — timeout passes (2026-10-30); success and simultaneous damage need two clients
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

## Stances and cover (2026-10-30, Studio solo, R6)
- [x] Crouch blocked from standing under an overhang
- [x] High cover: snap, slide, endpoint, inner and outer corners
- [x] Peek at a high-cover edge; shot accepted; shot into the wall face refused
- [x] Low cover: crouched, pop-up on aim, fire over the wall
- [x] Reload animation phases end when the server moves ammo
- [x] Movement guard pulls back a client-side speed hack
- [ ] Two clients see each other's stances and poses
- [ ] Slopes, stairs, ledges and corners under latency

## Back-to-wall cover and impacts (2026-10-30, Studio solo, R6, screenshots)
- [x] Back-to-wall in high and low cover; smooth entry
- [x] Peek at a high-cover edge and over low cover; aimed shots tight (5 holes within 0.1 studs at ~12 studs)
- [x] Blind fire from cover scatters (avg 3.8 studs, max 11.9 studs off)
- [x] Bullet holes on surfaces; blood on the dummy
- [ ] Other players see peeks, blind fire and impacts

## R15 migration and animation suite (2026-10-30, Studio solo, R15, screenshots)
- [x] Imported clip poses a Studio R15 rig identically to Blender (within 0.001 stud)
- [x] Standard body applied after avatar load (scale 1, HipHeight 2.192, default head); no avatar animation tracks
- [x] Barrel on the aim point: aimed 0.0°, hip 0.5°, aiming while prone 1.1°
- [x] Shoot-dodge sequence plays in order: DiveWindup → DiveAir → Land → Prone → Recover → Idle
- [x] Run plays at ~1.0× for 16 studs/s; walk → run blend while accelerating
- [x] Crouch: planted foot on the ground; crouched head top 3.96 (under the 4.0 low walls)
- [x] Reload clip at 1.0× for the 1.6 s server reload; a shot plays RecoilHip
- [x] No warnings or errors in Output
- [ ] Two clients see each other's clips (needs published clip IDs)
- [ ] Cover, sprint, strafes and turn-in-place checked on screen
- [ ] Bullet-time slow-motion playback
- [ ] FBX files import into Studio's Animation Editor
