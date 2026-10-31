# Last Stand and Bullet Time

Max Payne 3's Last Stand, for multiplayer: a killing blow gives the victim one slow-motion chance to shoot their killer. Also the localized bullet time it uses, and the adrenaline meter. Built 2026-10-31.
Related: [[Limb Health]] · [[Movement State Machine]] · [[Max Payne 3 Mechanics Reference]] · [[HUD Layout]]

## When it happens
On a killing blow (head or torso in the red), a player gets a Last Stand only if **all** of these are true:
- at least one **painkiller**;
- a **loaded gun** (rounds in the magazine) their arms can fire, in any slot;
- not both arms in the red;
- a killer to shoot at: another character that is still up;
- not already getting up from a Last Stand, and no Last Stand in the last 10 s.

Otherwise they die at once. Test dummies never get one.

## What happens
1. **The fall (0.6 s):** the stance becomes LastStand and the body drops (hips 2.2 studs lower until there is an animation). The camera is **dragged onto the killer** and the mouse is ignored. A loaded gun goes into the hand at once and any reload is cancelled. The killer gets a red outline only the downed player sees.
2. **Bullet time:** everyone within 80 studs of the downed player slows to 0.3 speed (walking, fire rate, reloads, dives, tracers). The downed player doesn't. Their screen loses most of its colour and blurs slightly.
3. **The window (4 s):** the player aims and fires. The camera keeps being dragged along as the killer moves, on top of the player's own aim. A white bar under LAST STAND counts down.
4. **Survive:** the killer dies or goes down (dead, or in a Last Stand of their own). The player pays **one painkiller** and **all their adrenaline**, and comes back with head and torso at 35% of their maximum (other limbs stay as they were).
5. **Fail:** the window runs out, or the killer stays **completely out of sight** for 0.75 s (checked from the downed player's head to the killer's head and torso). The player dies.
6. **Wakeup (3 s):** the player gets up **defenseless**: no moving, firing, reloading or anything else. They can be hurt and killed normally, with no second Last Stand. The HUD tag reads DEFENSELESS.

During the window the downed player can't be hurt; the window alone decides. The killer's teammates can't finish them off, so the killer's way out is to break line of sight.

## Bullet time (localized)
Roblox has no world time scale, so bullet time is a bubble. `BulletTimeService` gives every character near the bubble's owner a `TimeScale` below 1, and each system reads it:
| Where | What slows |
|---|---|
| Client | walk speed, dive timings, tracer speed, animation speed (once there are animations), the BULLET TIME label and the colour grade |
| Server | fire rate, reloads, draw times, dive and get-up timers, the movement check's speed limit, walk speed of non-player characters |

Overlapping bubbles use the lowest scale. Gravity isn't slowed, so jumps and falls run at normal speed.

## Adrenaline
The slim white bar beside the HUD figure is now the adrenaline meter (0 to 1). Every point of damage dealt adds 0.004 and every kill adds 0.25. A survived Last Stand empties it. **Spending it on player-triggered bullet time isn't built yet.**

## Tested (2026-10-31)
- Torso at 30; the gunman's hit put it in the red. Last Stand started within 0.2 s. During the fall the camera pointed 0.7° off the gunman, and the gunman was slowed to 0.3.
- One M9 headshot downed the gunman. The player got up with torso 35, painkillers 3 → 2, adrenaline 0.6 → 0, defenseless for 3 s, then back to Standing.
- When the shots came too late, the window ran out and the player died.
- With no painkillers, a killing blow was instant death.

## Not done
- The line-of-sight failure (the killer hides) wasn't tested in play. It ends the stand the same way as the timer running out.
- No slow-motion sound.
- No Last Stand animations (see [[Animation Hooks]]).
