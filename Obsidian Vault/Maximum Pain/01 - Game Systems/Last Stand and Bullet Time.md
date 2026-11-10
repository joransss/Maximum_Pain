# Last Stand and Bullet Time

Max Payne 3's Last Stand, for multiplayer: a killing blow gives the victim one slow-motion chance to shoot their killer. Also the localized bullet time it uses, and the adrenaline meter. Built 2026-10-31.
Related: [[Limb Health]] · [[Movement State Machine]] · [[Max Payne 3 Mechanics Reference]] · [[HUD Layout]]

## When it happens
On a killing blow (head or torso in the red), a player gets a Last Stand only if **all** of these are true:
- at least one **painkiller**;
- a **loaded gun** (rounds in the magazine) their arms can fire, in any slot;
- not both arms in the red;
- a killer to shoot at: another character that is still up;
- not already getting up from a Last Stand, and no Last Stand in the last 10 s;
- at least **one level of bullet time** in the adrenaline meter (a third of it).

Otherwise they die at once. Test dummies never get one.

## What happens
1. **The fall (0.6 s):**
   - The stance becomes LastStand and the LastStandFall clip plays.
   - The hips drop 2.2 studs. The root drops with them at once, the body eases down, and the feet stay on the floor. Since 2026-11-02 this works although the server forces this stance; before that the body free-fell and the feet went through the floor.
   - The camera is **dragged onto the killer** and the mouse is ignored.
   - A loaded gun goes into the hand at once and any reload is cancelled.
   - The killer gets a red outline only the downed player sees.
2. **Bullet time:** everyone within 80 studs of the downed player slows to 0.3 speed (walking, fire rate, reloads, dives, tracers). The downed player doesn't. Their screen loses most of its colour and blurs slightly.
3. **The window (4 s):** the player aims and fires. The camera keeps being dragged along as the killer moves, on top of the player's own aim. A white bar under LAST STAND counts down.
4. **Survive:** the killer dies or goes down (dead, or in a Last Stand of their own). The player pays **one painkiller** and **all their adrenaline**, and comes back with head and torso at 35% of their maximum (other limbs stay as they were).
5. **Fail:** the window runs out, or the killer stays **completely out of sight** for 0.75 s (checked from the downed player's head to the killer's head and torso). The player dies.
6. **Wakeup (3 s, the LastStandWakeup clip):** the player gets up **defenseless**: no moving, firing, reloading or anything else. They can be hurt and killed normally, with no second Last Stand. The HUD tag reads DEFENSELESS. During the window the body sits on the floor aiming (the LastStand clip, with the aim layer pointing the gun).

During the window the downed player can't be hurt; the window alone decides. The killer's teammates can't finish them off, so the killer's way out is to break line of sight.

## Bullet time (localized)
Roblox has no world time scale, so every character carries a `TimeScale` attribute (1, or lower while slowed) and each system reads it:
| Where | What slows |
|---|---|
| Client | walk speed, dive timings, the vault's path, tracer speed, animations (locomotion follows the slowed velocity; everything else plays at `TimeScale`), hit flinches, the BULLET TIME label and the colour grade |
| Server | fire rate, reloads, draw times, dive and get-up timers, the movement check's speed limit, walk speed of non-player characters |

Two things slow characters, and the lowest scale wins:
- **Last Stand bubbles:** everyone within 80 studs of the downed player, at 0.3.
- **Player-triggered bullet time** (`BulletTimeRules`), on **X** (middle mouse button, gamepad Select):
  - It spends every full level of the meter. There are three levels in a full meter, worth 5 s in all, so one level lasts 1.67 s.
  - Everyone the activator can see is slowed to 0.3 until the time runs out or the sight breaks. "See" means on the activator's screen, with a clear ray from their eye to the target's head, chest or hips; walls block it, glass and other characters don't. It's checked 10 times a second.
  - A slowed player whose own active level is lower than the activator's also turns their aim at 0.35 speed, until they activate a level at least as high.
  - The activator is slowed too, to 0.6 (`BulletTimeRules.ACTIVATOR_SCALE`): less than everyone they slow, as Max Payne 3 slows the user less than their victims. Someone else's bullet time seeing them slows them to 0.3. In a Last Stand they keep full speed, even while their own bullet time runs. (Until 2026-11-10 the activator kept full speed.)

Gravity isn't slowed, so jumps and falls run at normal speed. Studio test hook: a `DebugBulletTime` attribute set to true on any character activates its bullet time (with `Adrenaline` 1 and, for a dummy, an `Aim` attribute pointing at the target).

## Adrenaline
The slim white bar beside the HUD figure is the adrenaline meter (0 to 1). Every point of damage dealt adds 0.004 and every kill adds 0.25. Bullet time spends it, and a survived Last Stand empties it.

## Tested (2026-10-31)
- Torso at 30; the gunman's hit put it in the red. Last Stand started within 0.2 s. During the fall the camera pointed 0.7° off the gunman, and the gunman was slowed to 0.3.
- One M9 headshot downed the gunman. The player got up with torso 35, painkillers 3 → 2, adrenaline 0.6 → 0, defenseless for 3 s, then back to Standing.
- When the shots came too late, the window ran out and the player died.
- With no painkillers, a killing blow was instant death.

## Tested (2026-11-02)
- **The stand:** the hostile gunman's killing blow started it. Four server-checked shots after the 0.6 s fall downed the gunman, and the player survived.
- **The drop:** the root dropped 2.2 at once, the feet stayed within 0.05 of the floor and the camera moved smoothly (largest step 0.20). Before the session's fixes the body fell freely, the feet went 0.74 into the floor and the view popped 1.77.
- **The wakeup:** the root rose at once.
- **Bullet time** (a dummy's, on the player): a vault took 1.40 s in the air at 0.3 (0.45 s normally); crouching and standing stayed smooth.
- **Still open:** the wake-up clip plants the right hand while it holds the pistol, and the pistol's box touches the floor (0.2). See [[Animation and MP3 Systems - Progress and To Do]].

## Tested (2026-11-10)
Checked after a play test where the player moved freely in their own bullet time (83tg's avatar, the TargetOpen dummy about 20 studs away). It worked as this note then said, the activator at full speed. JordanSaa decided the same day to slow the activator to 0.6, and it was retested:
- **The player triggering it** with a full meter (X): level 3 for 5 s, the meter drained to 0, the dummy in view at 0.3. Before the change the player stayed at 1 (16 studs/s). After it, 0.6: sprinting at 14.4, walking at 9.6, back to 1 after 5 s. Triggered mid-sprint, the server's movement check stayed quiet. The player's screen shows the BULLET TIME label and the drained colour.
- **The dummy triggering it on the player:** the player at 0.3, walking at 4.8, `AimPenalty` 0.35; back to 1 after 5 s.
- **A counter-activation** at the same level: the penalty cleared at once; both stayed at 0.3 while they could see each other, and both went back to 1 with the pillar between them.
- **A Last Stand during the player's own bullet time:** at 0.6 until the gunman's killing blow, then 1 for the whole stand while their own bullet time ran on; the gunman at 0.3 in the stand's bubble.

## Not done
- Max Payne 3's slow-down also chains through the victims' sight ([[Max Payne 3 Mechanics Reference]]); here it doesn't.
- The line-of-sight failure (the killer hides) wasn't tested in play. It ends the stand the same way as the timer running out.
- No slow-motion sound.
