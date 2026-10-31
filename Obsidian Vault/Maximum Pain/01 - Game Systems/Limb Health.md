# Limb Health

Health tracked per body part, the "in the red" rules, Max Payne 3 style painkillers, and what injuries do to the shoot-dodge, guns and Last Stand. Built 2026-10-31, updated the same day for loadouts, the shoot-dodge and Last Stand.
Related: [[Weapons and Recoil]] · [[Loadout and Dual Wielding]] · [[Last Stand and Bullet Time]] · [[Shoot-Dodge]] · [[HUD Layout]] · [[Changelog]] · [[Max Payne 3 Mechanics Reference]]

## Health matrix
| Limb | Max health | In the red at or below | Body parts that count |
|---|---|---|---|
| Head | 50 | 12.5 | Head, plus hats and hair |
| Torso | 100 | 25 | UpperTorso, LowerTorso, HumanoidRootPart (R6: Torso), and anything unrecognised |
| Left arm, right arm | 60 each | 15 | Upper arm, lower arm, hand. Guns can't be hit: shots pass through them to the body. |
| Left leg, right leg | 70 each | 17.5 | Upper leg, lower leg, foot |

- A limb is **in the red** at or below 25% of its maximum (`RED_FRACTION`).
- Headshots do ×2 damage.
- A hit only damages the limb it lands on. A shotgun blast spreads its pellets over several limbs.
- Health does not regenerate. Only painkillers restore it.

## State rules
| Condition | Status (HUD tag) | Effect |
|---|---|---|
| Nothing in the red | Normal | Walk 16, sprint 24 (hold Shift; not while aiming). |
| One leg in the red | **LIMPING** | Walk 11, no sprint. Shoot-dodge scale 0.4 (heavily handicapped). |
| Both legs in the red | **CRAWLING** | Walk 4 (dragging), no sprint, no jumping. Shoot-dodge scale 0 (no dive). |
| One arm in the red | **ONE ARM** | A two-handed gun in use (rifles, the MP5, shotguns except the sawn-off, the M107) drops to the floor, and dual wielding ends. Only one-handed guns can be drawn. A carried two-handed gun stays carried. |
| Both arms in the red | **DISARMED** | Everything in the hands drops, including the carried two-handed gun. Nothing can be drawn or picked up. |
| Head or torso in the red | Last Stand or dead | A [[Last Stand and Bullet Time\|Last Stand]] if the player has a painkiller and a loaded gun their arms can fire; otherwise instant death. |

Leg and arm statuses combine (the HUD shows, for example, "LIMPING / ONE ARM").

### How the arm rules are enforced
- The server applies the arm rules from `LoadoutRules` the moment an arm goes into or out of the red ([[Loadout and Dual Wielding]]). Dropped guns land in front of the player as pickups.
- Hold requests the arms can't manage are refused by the server, the client doesn't send them, and the HUD fades those slots.
- The server also refuses to fire a gun the arms can't hold.

## Painkillers
- **H** (gamepad D-pad up) takes one.
- Each painkiller restores 60% of every limb's maximum, capped at full. That always lifts a limb out of the red, so it clears every status.
- Players start each life with 3. The count shows in a white square on the HUD figure's back (see [[HUD Layout]]).
- 1 s cooldown. A painkiller is refused when nothing is hurt, the player is dead, or the stance doesn't allow it (sprinting is fine; diving, getting up and Last Stand are not).
- A painkiller is also the price of surviving a Last Stand, and having one is what makes a Last Stand possible.

## Hooks the other systems read
The server keeps these attributes on each character:
- `ShootDodgeScale`: **1** normal, **0.4** limping, **0** crawling. The [[Shoot-Dodge]] multiplies dive speed and distance by it; **0 blocks the dive**.
- `MoveState`: `Normal`, `Limping` or `Crawling`. Sets walk speed; limping or crawling stops a sprint.
- `ArmState`: `Normal`, `OneArm` or `Disarmed`. Drives the loadout rules and Last Stand eligibility.

## Where the code lives
| Piece | Place in Studio | Job |
|---|---|---|
| `LimbRules` | ReplicatedStorage.Modules | All the numbers and rules above, shared by server and client. Checks itself when it loads. |
| `LimbService` | ServerScriptService | Applies damage (with who dealt it), then the effects: status attributes, the arm rules through `LoadoutService`, and killing blows through `LastStandService`. Ignores damage during a Last Stand. Also handles painkillers. |
| `CharacterServer` | ServerScriptService | Sets up each new character (stance, limbs, loadout) and answers painkiller requests. Replaced `LimbServer` on 2026-10-31. |
| `CharacterController` | StarterPlayerScripts.Controllers | The client's stance machine: walk speed and jumping from the leg rules and the stance, sprint, crouch and the painkiller key. |

Character attributes: `HeadHealth`, `TorsoHealth`, `LeftArmHealth`, `RightArmHealth`, `LeftLegHealth`, `RightLegHealth`, `Painkillers`, `MoveState`, `ArmState`, `ShootDodgeScale`.
Characters without these attributes (for example plain NPCs) take ordinary Humanoid damage instead.

## Verified in play (2026-10-31)
- Right leg in the red: LIMPING, walk speed 11 even with Shift held, dive scale 0.4.
- Both legs: CRAWLING, walk speed 4, jumping off, dive scale 0.
- A painkiller healed both legs back to normal; a second press within 0.3 s was refused.
- Right arm in the red while holding the M4: the M4 dropped to the floor. Keys and a forced equip of the AK were both blocked; the M9 still equipped.
- Both arms: the M9 dropped, nothing could be equipped, and all slots faded.
- A painkiller restored the arms, and rifles equipped again.
- Real aimed shots at a test dummy hit the right limbs: two FAL hits on a leg put it in the red, two on an arm took it to 0, and one headshot killed it.
- Torso in the red killed the player. The respawn came back with full health, 3 painkillers and the full loadout.
- Later the same day, with the loadout system: the right arm in the red ended dual wielding, and a painkiller restored it. A killing blow with painkillers and a loaded gun started a Last Stand; with no painkillers it killed at once.

## Known limits
- Walk speed is applied on the player's own machine, as with all Roblox movement. The server's movement check ([[Movement State Machine]]) catches big speed cheats, but its slack means a limping cheater could still walk at normal speed.
- Dropped guns lie on the floor for 45 s and can be picked up again; healing doesn't bring them back.
