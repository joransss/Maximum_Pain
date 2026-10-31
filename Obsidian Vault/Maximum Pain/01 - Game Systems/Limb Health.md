# Limb Health

Health tracked per body part, the "in the red" rules, Max Payne 3 style painkillers, and the hooks the future shoot-dodge will use. Built 2026-10-31.
Related: [[Weapons and Recoil]] · [[HUD Layout]] · [[Changelog]] · [[Max Payne 3 Mechanics Reference]]

## Health matrix
| Limb | Max health | In the red at or below | Body parts that count |
|---|---|---|---|
| Head | 50 | 12.5 | Head, plus hats and hair |
| Torso | 100 | 25 | UpperTorso, LowerTorso, HumanoidRootPart (R6: Torso), and anything unrecognised |
| Left arm, right arm | 60 each | 15 | Upper arm, lower arm, hand. A gun in someone's hand counts as their right arm. |
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
| One arm in the red | **ONE ARM** | A held two-handed gun (rifles, SMGs, Mossberg 500, SPAS-15, Barrett M107) drops to the floor. Only pistols and the sawn-off can be equipped. |
| Both arms in the red | **DISARMED** | Whatever gun is held drops. Nothing can be equipped. |
| Head or torso in the red | Dead | Instant death. |

Leg and arm statuses combine (the HUD shows, for example, "LIMPING / ONE ARM").

### How the arm rules are enforced
- The server drops the held gun the moment an arm goes into the red. The gun lands in front of the player with touch-to-pick-up turned off.
- The client won't equip a gun the arms can't hold, and the HUD fades those slots.
- If a client forces one into its hands anyway, the server moves it straight back to the backpack. The server also refuses to fire it.

## Painkillers
- **H** (gamepad D-pad up) takes one.
- Each painkiller restores 60% of every limb's maximum, capped at full. That always lifts a limb out of the red, so it clears every status.
- Players start each life with 3. The count shows in a white square on the HUD figure's back (see [[HUD Layout]]).
- 1 s cooldown. A painkiller is refused when nothing is hurt or the player is dead.

## Hooks for the shoot-dodge (not built yet)
The server keeps these attributes on each character. The future shoot-dodge should read them instead of re-deriving the rules:
- `ShootDodgeScale`: **1** normal, **0.4** limping, **0** crawling. Multiply dive distance and speed by it; **0 means the dive is blocked**.
- `MoveState`: `Normal`, `Limping` or `Crawling`.
- `ArmState`: `Normal`, `OneArm` or `Disarmed`.

## Where the code lives
| Piece | Place in Studio | Job |
|---|---|---|
| `LimbRules` | ReplicatedStorage.Modules | All the numbers and rules above, shared by server and client. Checks itself when it loads. |
| `LimbService` | ServerScriptService | Applies damage, then the effects: death, dropped guns, status attributes. Also handles painkillers. |
| `LimbServer` | ServerScriptService | Sets up each new character, answers painkiller requests, blocks equipping guns the arms can't hold. |
| `CharacterController` | StarterPlayerScripts.Controllers | Sprint, walk speed and jumping from the leg rules, and the painkiller key. |

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

## Known limits
- Walk speed is applied on the player's own machine, as with all Roblox movement, so a speed cheat would ignore limping.
- No pickup system yet. Dropped guns despawn after 30 s, and healing doesn't give them back.
- Death is instant. Max Payne 3's Last Stand isn't built.
