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
| Vaulting | the vault's path (14 along the ground) | — | 1.3 | 1.1 | fire, aim, reload, switch |
| GettingUp | — | 1.2 | — | — | nothing (defenseless) |
| LastStand | — | 2.2 | 1 | 1 | fire, aim |
| Dead | — | — | — | — | nothing |

Speeds are studs per second for a healthy character; limping and crawling scale them down ([[Limb Health]]). Aiming while standing or crouched slows walking to 70%. Bullet time multiplies everything by the character's `TimeScale`.

Walking adds up to +35% spread at full walking speed (standing or crouched). Jumping or falling (not diving) doubles spread. Dual wielding adds ×1.35 spread and ×1.25 recoil. All of these multiply each gun's own spread and aiming ([[Weapons and Recoil]]).

## Transitions
| From | Can change to |
|---|---|
| Standing, Sprinting, Crouching | each other, CoverHigh, CoverLow, DodgePrep, Vaulting, LastStand, Dead |
| CoverHigh, CoverLow | each other (the wall's height changes), CoverPeek, Standing, Crouching, Vaulting (only low cover passes the height check), LastStand, Dead |
| Vaulting | Standing (Crouching under a low ceiling), LastStand, Dead |
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
| Vaulting → Standing | when the client lands (0.45 to 0.75 s at full speed); the server rises on its own 0.3 s after the vault's time if the landing message is lost |

All timers stretch under bullet time, so nothing can get stuck: every stance either has an exit the player controls or a timer that forces one.

## Height
Each stance's hip drop sets the humanoid's `HipHeight` (crouch, low cover, prone, getting up, Last Stand).
- **On the ground:** the root part moves to the new height over the floor at once, instead of falling or springing there over several frames. The free fall used to sink the body up to a stud into the floor and play the Fall clip.
- **When:** since 2026-11-04 the hip height and the root change together just before physics (`CharacterController.moveRoot`, the first procedural layer), right before the aim layer holds the body. Moved on the key press, the root took the body with it and a frame was drawn a stance's height out (the feet 1.8 into the floor on a crouch). The humanoid keeps its old hip height until then: it checks its floor between the render step and physics, and told the new height early it lost the floor and fell.
- **Easing:** the clips blend over a fifth of a second. Meanwhile the aim layer holds the body where it was and eases it to the new height, lifting it (up to 1.2) wherever the legs' blend would put a foot through the floor. The camera hears of the root's move and the new drop together (`absorbHeight`), holds its view and eases too.
- **In the air:** in DodgeAir, Vaulting and Dead the root isn't moved, because the launch, the vault's path or the ragdoll take it there for real. The body goes with the root. A dive's landing (DodgeGround) is moved and eased like a crouch since 2026-11-04; it used to fall the last 2.4 studs and bounce.
- **Server-forced stances:** when the server forces a stance (Last Stand, a wakeup, a timed get-up), its new hip height reaches the client before the stance does. The client therefore compares with the height it last put the root at, not with the humanoid's current value, so these move the root at once too (since 2026-11-02).

## Actions (upper body)
Reloading and switching guns run alongside the stance, in the character attributes `Action` and `ActionEnds`. A stance that doesn't allow reloading (diving, getting up, Last Stand, dead) cancels a reload. No ammo moves until a reload finishes, so nothing is lost or duplicated.

## Prediction and the server
1. A key press changes the client's stance at once and sends a request (`StanceRequest`).
2. The server checks it against the same rules, plus its own geometry checks. If it agrees, it sets the `Stance` attribute and says nothing more.
3. If it disagrees it sends **Rejected** with its own stance and a reason, which the HUD shows (for example NO ROOM TO STAND). The client takes the server's stance.
4. When the server changes a stance on its own (Last Stand, death, cover that stopped being valid, a dive held too long) it sends **Forced** and the client follows.
5. Safety net: if the two disagree for 0.75 s, the client takes the server's stance.
6. The server's copy of a moving character lags the client (about 0.25 s in Studio), so its checks of where the character is reach further than the client's: a vault's obstacle is looked for `VaultRules.SERVER_SLACK` (7.5) further. With 2.5, running vaults were refused (2026-11-10).

## Sprint
- Hold Shift while moving forward (within about 60° of where the camera looks). Sprint speed 24.
- Stops when Shift is released, when aiming, when movement stops or turns sideways, when a leg is in the red, or when stamina runs out.
- **Stamina** (since 2026-11-20, numbers in `VitalsRules`): a full bar sprints for 6 s with a Medium loadout, 7.8 s Light, 4.2 s Heavy (the class the guns carried make right now: [[Loadout and Dual Wielding#Weight]]). It starts filling 1 s after a sprint ends and fills in 4 s, whatever the class. A sprint that runs it dry ends, and Shift must be pressed again; once dry, a sprint can start again when it is a quarter full. Only sprinting uses it, not dives or vaults. When the class changes mid-sprint, the share left stays the same and drains at the new class's pace.
- **Who decides:** the server keeps the real count (`StanceService`): it ends a sprint that runs dry (Forced, "Tired") and refuses one started before the quarter (Rejected, "Tired"). The client predicts the same count so the stop is instant, and takes the server's (the `Stamina` attribute, in tenths) when it is clearly lower; a forced stop empties its count, while a refusal (the server a moment behind near the quarter) holds it just under the quarter, and the sprint starts once both agree if Shift is still held. Walking can't stand in for a sprint: the server's movement check holds walking to 16 × 1.1 studs a second (below). The HUD shows a slim bar under the figure while it isn't full ([[HUD Layout]]).
- **No sprinting under Bulletproof** (since 2026-11-21, the skill: [[Menus, Loadout, Progression and Shop - To Do#6. Skills (Max Payne 3's Bursts, renamed)]]): while it runs the server refuses a sprint (Rejected, "NoSprint") and ends one under way (Forced, "NoSprint"); the character carries `NoSprint` for the client, which neither starts one nor keeps one going meanwhile.
- **Aiming in** takes the class's share of the usual time (since 2026-11-20): the camera's zoom and the sniper scope's push, and the server's 0.15 s aim settle ([[Weapons and Recoil]]): Light ×0.85, Medium ×1, Heavy ×1.2. Letting go is the same for everyone. Walk speed and dive distance are the same for every class.
- **Firing:** pulling the trigger ends the sprint, and the gun can fire 0.2 s later (the server enforces the same delay). Shift must be pressed again to sprint.
- **Cover:** a sprint can't start in cover; leave cover first. Running into cover from a sprint is allowed.
- **Reloading** carries on while sprinting, and **switching guns** is allowed.
- Spread ×2, which only matters in the 0.2 s after a sprint.

## Free crouch
- C toggles it. The hips drop 1.8 studs (head top about 3.5 studs above the floor). Speed 8.8, spread ×0.8, recoil ×0.85, no jumping.
- **Headroom check:** standing up (or sprinting out of a crouch) is refused under anything lower than standing height, and the HUD shows NO ROOM TO STAND. Tested under the arena's 4-stud crouch tunnel.
- Separate from low cover: a free crouch moves anywhere; low cover is attached to a wall.
- The crouch clips (CrouchIdle, CrouchWalk in four directions) fold the legs to match the hip drop. The camera only follows a quarter of the drop, so it can still see over low cover.

## Movement check (anti-cheat)
Roblox lets each player's own computer move their character, so the server can only check afterwards. Until 2026-11-20 it compared each 0.5 s with the stance's top speed ×1.35 plus 6 studs/s, which let a client walk faster than a sprint without spending stamina (the review that day). Since then (`StanceService.checkSpeed`):
- Each stance is held to its own speed with the legs' state, as the client sets it: the walk speed for `MoveState` (`LimbRules.WALK_SPEED`: 16, limping 11, crawling 4) times the stance's share, 70% of that while aiming (standing or crouched); a sprint's 24 only while sprinting, and for a second after the server ends a sprint itself (Tired, a hit: the client runs on until it hears; a stop the client asks for needs no grace); a vault's 14 while vaulting; a dive's 31 while diving, and for a second after a dive or a vault starts or ends (lying after a dive gets nothing more); cover's 10 for stepping out and swinging round corners. Bullet time scales them all, and when it slows a character the old scale counts for a second.
- A bank of distance fills at 1.1 times that speed, up to a second of it (of walking at least) plus 4 studs, and each frame's move across the ground is taken from it. Late position updates arrive in a burst that what built up while they were late pays for; a client a moment ahead of the server (up from the floor and walking before the server hears) is covered too. A new character is checked from its spawn point at once.
- Overdrawn, the character is put back where it last moved legally, and kept there while it keeps trying, with a warning in the output at most every 5 s (the stance, the speed allowed, the last step and where).
- Self-checks warn (they don't stop the game) if walking's limit (16 × 1.1) reaches a sprint's speed, or `StanceRules.WALK_SPEED` stops matching `LimbRules`'. Height and walls aren't checked: climbing, flying or teleporting upwards, and a blink of up to the bank (about 20 studs) in one step, through a wall too, are for a later pass.
- Server code that moves a character itself (a teleport) calls `StanceService.moved(character)` first: the check trusts where it is for 0.5 s, then starts afresh. Without it a move over the bank is undone.
- Tested 2026-11-20: a client forcing its walk speed to 26 without sprinting was put back 7 times in 9 s and averaged 17.6 studs/s; forcing 16 while limping averaged 12.4. Walking, sprinting, limping, crouching, a dive, a vault, cover, bullet time and getting up after 8 s on the floor never tripped it.
- Tested 2026-11-21 (after the second review): a client pushed to 24 to 26 while asking to sprint and to stop every 0.9 s averaged 16.7; aimed but pushed to 17, it was held to 12.3; a 60-stud jump right after respawning kept only the usual allowance. Under Studio's "Bad Connection (3G)" network (150 to 180 ms each way, jitter, 0.5% loss), walking, sprinting, stopping, crouching, a dive and sprinting into bullet time never tripped it.
