# Movement State Machine

Every character is in exactly one **stance**. The stance decides speed, crouch height, accuracy, what the character can do and which stances come next. One table (`StanceRules`) holds all of it, shared by server and client, so scripts never disagree and animations never compete. Built 2026-10-31.
Related: [[Architecture]] · [[Cover System]] · [[Shoot-Dodge]] · [[Last Stand and Bullet Time]] · [[Animation Hooks]]

## Stances
| Stance | Speed | Hips drop | Spread × | Recoil × | Can |
|---|---|---|---|---|---|
| Standing | 16 | — | 1 | 1 | everything on foot |
| Sprinting | 24 | — | 2 | 1 | reload, switch, move, jump, crouch, take cover, dive, pick up, painkiller. **No firing or aiming.** |
| Crouching | 8.8 | 1.8 | 0.8 | 0.85 | fire, aim, reload, switch, move, sprint, take cover, dive, pick up, painkiller |
| CoverHigh | 9.6 along the wall | — | 2.5 (blind fire) | 1.3 | blind fire, aim (pops out at an edge), reload, switch, move, leave, painkiller |
| CoverLow | 8 along the wall | 1.8 | 2.5 (blind fire) | 1.3 | as high cover |
| CoverPeek | — | — | 1.5 | 1 | fire, aim, reload, switch, leave, painkiller (0.25 s, then CoverAim) |
| CoverAim | — | — | 0.85 | 0.8 | fire, aim, reload, switch, leave, painkiller |
| DodgePrep | run-up | 0.6 | 1.3 | 1 | aim (0.2 s, then DodgeAir) |
| DodgeAir | flight | — | 1.3 | 1.2 | fire, aim |
| DodgeGround | — | 2.2 | 0.9 | 1 | fire, aim, reload, switch, painkiller |
| GettingUp | — | 1.2 | — | — | nothing (defenseless) |
| LastStand | — | 2.2 | 1 | 1 | fire, aim |
| Dead | — | — | — | — | nothing |

Speeds are studs per second for a healthy character; limping and crawling scale them down ([[Limb Health]]). Aiming while standing or crouched slows walking to 70%. Bullet time multiplies everything by the character's `TimeScale`.

Walking adds up to +35% spread at full walking speed (standing or crouched). Jumping or falling (not diving) doubles spread. Dual wielding adds ×1.35 spread and ×1.25 recoil. All of these multiply each gun's own spread and aiming ([[Weapons and Recoil]]).

## Transitions
| From | Can change to |
|---|---|
| Standing, Sprinting, Crouching | each other, CoverHigh, CoverLow, DodgePrep, LastStand, Dead |
| CoverHigh, CoverLow | each other (the wall's height changes), CoverPeek, Standing, Crouching, LastStand, Dead |
| CoverPeek | CoverAim, CoverHigh, CoverLow, Standing, Crouching, LastStand, Dead |
| CoverAim | CoverHigh, CoverLow, Standing, Crouching, LastStand, Dead |
| DodgePrep | DodgeAir, Standing, LastStand, Dead |
| DodgeAir | DodgeGround, LastStand, Dead |
| DodgeGround | GettingUp, LastStand, Dead |
| GettingUp | Standing, Crouching, LastStand, Dead |
| LastStand | GettingUp (survived), Dead |
| Dead | nothing (a respawn starts in Standing) |

`StanceRules` checks itself when it loads: every exit leads to a real stance, Dead has no exits, sprinting can't fire, and cover can't go straight to sprinting.

## Timed steps
The server times these, and the client times the same steps itself so nothing waits on the network.
| Step | Time |
|---|---|
| DodgePrep → DodgeAir | 0.2 s |
| CoverPeek → CoverAim | 0.25 s |
| GettingUp → Standing (Crouching if there is no headroom) | 0.6 s after a dive, 3 s after a Last Stand |
| DodgeAir → DodgeGround | when the client lands; forced after 2.5 s |
| DodgeGround → GettingUp | when a movement key is pressed; forced after 8 s |

All timers stretch under bullet time, so nothing can get stuck: every stance either has an exit the player controls or a timer that forces one.

## Actions (upper body)
Reloading and switching guns run alongside the stance, in the character attributes `Action` and `ActionEnds`. A stance that doesn't allow reloading (diving, getting up, Last Stand, dead) cancels a reload. No ammo moves until a reload finishes, so nothing is lost or duplicated.

## Prediction and the server
1. A key press changes the client's stance at once and sends a request (`StanceRequest`).
2. The server checks it against the same rules, plus its own geometry checks. If it agrees, it sets the `Stance` attribute and says nothing more.
3. If it disagrees it sends **Rejected** with its own stance and a reason, which the HUD shows (for example NO ROOM TO STAND). The client takes the server's stance.
4. When the server changes a stance on its own (Last Stand, death, cover that stopped being valid, a dive held too long) it sends **Forced** and the client follows.
5. Safety net: if the two disagree for 0.75 s, the client takes the server's stance.

## Sprint
- Hold Shift while moving forward (within about 60° of where the camera looks). Sprint speed 24.
- Stops when Shift is released, when aiming, when movement stops or turns sideways, or when a leg is in the red.
- **Firing:** pulling the trigger ends the sprint, and the gun can fire 0.2 s later (the server enforces the same delay). Shift must be pressed again to sprint.
- **Cover:** a sprint can't start in cover; leave cover first. Running into cover from a sprint is allowed.
- **Reloading** carries on while sprinting, and **switching guns** is allowed.
- Spread ×2, which only matters in the 0.2 s after a sprint.

## Free crouch
- C toggles it. The hips drop 1.8 studs (head top about 3.5 studs above the floor). Speed 8.8, spread ×0.8, recoil ×0.85, no jumping.
- **Headroom check:** standing up (or sprinting out of a crouch) is refused under anything lower than standing height, and the HUD shows NO ROOM TO STAND. Tested under the arena's 4-stud crouch tunnel.
- Separate from low cover: a free crouch moves anywhere; low cover is attached to a wall.
- Until there is a crouch animation, the body sinks into the floor by the hip drop. The camera only follows a quarter of the drop, so it can still see over low cover.

## Movement check (anti-cheat)
Roblox lets each player's own computer move their character, so the server can only check afterwards. Every 0.5 s it compares how far each character moved with the top speed its stance allows (×1.35, plus 6 studs/s for lag). Two windows too fast in a row and the character is put back where it last moved legally, with a warning in the output. Tested: a faked run at 200 studs/s was pulled back.
