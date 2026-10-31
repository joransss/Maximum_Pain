# Weapons and Recoil

How the guns work in the current build, where to tune them, and how the CS2-style recoil is put together. Built 2026-10-31.
Related: [[Limb Health]] · [[HUD Layout]] · [[Changelog]] · [[Max Payne 3 Gunplay - Accuracy and Recoil]] · [[Weapons and Raycasting]]

## Where the code lives
| Piece | Place in Studio | Job |
|---|---|---|
| `WeaponConfig` | ReplicatedStorage.Modules | Every gun's numbers. **The only file to edit when tuning.** It checks itself when it loads (for example, `MaxSpread` below `BaseSpread` stops the game with a clear error). |
| `WeaponMath` | ReplicatedStorage.Modules | Spread, bloom and spray-pattern maths. Shared by server and client so both always agree. |
| `WeaponServer` | ServerScriptService | Decides every shot: fire rate, ammo, reloads, spread, hits and limb damage. Hands out the Studio test loadout. |
| `WeaponController` | StarterPlayerScripts.Controllers | Trigger, aim, reload and weapon-switch keys; recoil; muzzle flash, tracers and impacts. |
| `CameraController` | StarterPlayerScripts.Controllers | Over-the-shoulder camera, aim zoom, sniper scope and recoil kick. |
| Remotes | ReplicatedStorage.Remotes | `FireWeapon` (aim point + whether aiming), `ReloadWeapon`, `WeaponFired` (server to everyone: where each pellet landed and whether it hit a body). |

## Ground rules
- **The server decides.** The client only sends where it is aiming and whether it is aiming down the sights. Damage, ammo, fire rate, spread and hits are all worked out on the server.
- **Hitscan.** Each shot is an instant ray from the muzzle toward the crosshair's target. The tracer is only the picture of that shot.
- **Ammo: one spare magazine.** Every gun spawns with a full magazine plus one spare. When both are spent the gun is empty. There are no ammo pickups yet.
- **Test loadout.** In Studio every player gets all 13 guns. Published servers give nothing until real loadouts exist.

## Weapon balancing
All numbers are first-pass placeholders, tuned by feel. Damage is per bullet (per pellet for shotguns). Headshots do ×2.

### Handling
| Gun | Fire | Hands | RPM | Damage | Mag (+1 spare) | Reload | Range | Bullet speed |
|---|---|---|---|---|---|---|---|---|
| M9 | Semi | One | 400 | 22 | 15 | 1.6 s | 300 | 1100 |
| Glock 18 | Auto | One | 1100 | 14 | 17 | 1.6 s | 250 | 1100 |
| Desert Eagle | Semi | One | 200 | 50 | 7 | 2.0 s | 400 | 1300 |
| S&W 500 | Semi | One | 120 | 65 | 5 | 3.0 s | 350 | 1400 |
| MP5 | Auto | Two | 800 | 16 | 30 | 2.2 s | 300 | 1300 |
| Uzi | Auto | Two | 950 | 14 | 32 | 2.0 s | 220 | 1200 |
| Mossberg 500 | Semi | Two | 70 | 8 × 12 | 6 | 3.0 s | 120 | 1000 |
| SPAS-15 | Semi | Two | 240 | 8 × 10 | 6 | 2.6 s | 120 | 1000 |
| Sawn-off | Semi | One | 300 | 10 × 13 | 2 | 2.4 s | 60 | 900 |
| AK-47 | Auto | Two | 600 | 26 | 30 | 2.5 s | 500 | 2000 |
| FN FAL | Semi | Two | 400 | 34 | 20 | 2.7 s | 600 | 2200 |
| M4 | Auto | Two | 750 | 22 | 30 | 2.3 s | 500 | 2300 |
| Barrett M107 | Semi | Two | 90 | 95 | 10 | 3.5 s | 1500 | 2600 |

Range and bullet speed are in studs and studs per second. "Hands" matters for [[Limb Health]]: with one arm in the red, only one-handed guns can be used.

### Spread and recoil (degrees)
| Gun | Hip spread | + per shot | Max | Recovery /s | Aim × | Climb /shot | Sway |
|---|---|---|---|---|---|---|---|
| M9 | 0.6 | 0.8 | 4 | 8 | 0.5 | 0.9 | 0.3 |
| Glock 18 | 0.9 | 0.6 | 6 | 9 | 0.6 | 0.55 | 0.6 |
| Desert Eagle | 0.5 | 2.5 | 6 | 6 | 0.5 | 3 | 0.8 |
| S&W 500 | 0.5 | 3 | 7 | 5 | 0.5 | 4 | 1 |
| MP5 | 0.9 | 0.4 | 5 | 10 | 0.5 | 0.45 | 0.35 |
| Uzi | 1.3 | 0.5 | 6.5 | 10 | 0.6 | 0.55 | 0.6 |
| Mossberg 500 | 4.5 | 1 | 6 | 6 | 0.75 | 3.5 | 0.6 |
| SPAS-15 | 5 | 1.5 | 8 | 6 | 0.75 | 2.2 | 0.6 |
| Sawn-off | 7 | 1 | 9 | 6 | 0.85 | 4.5 | 1 |
| AK-47 | 0.7 | 0.6 | 5 | 7 | 0.4 | 0.75 | 0.7 |
| FN FAL | 0.5 | 1.2 | 5 | 7 | 0.4 | 1.6 | 0.5 |
| M4 | 0.6 | 0.45 | 4 | 8 | 0.4 | 0.55 | 0.45 |
| Barrett M107 | 2.5 | 4 | 8 | 4 | 0.02 | 6 | 1 |

The M107 also has `ScopeFov = 10`, which is what makes it zoom into a scope.

### What each field does
| Field | Meaning |
|---|---|
| `FireMode` | `Semi` fires once per click; `Auto` fires while the trigger is held. |
| `OneHanded` | Pistols and the sawn-off. Still usable with one arm in the red. |
| `RPM` | Fastest fire rate. The server enforces it. |
| `Damage`, `Pellets` | Damage per bullet, and bullets per shot (shotguns). |
| `Range` | How far a shot reaches, in studs. |
| `BulletSpeed` | How fast the tracer travels, in studs per second. |
| `MagSize` | Rounds per magazine. The spare magazine is the same size. |
| `ReloadTime` | Seconds. Switching guns cancels a reload. |
| `BaseSpread` | Spread of the first shot from the hip. |
| `SpreadPerShot` | Spread ("bloom") each quick follow-up shot adds. Must be above 0. |
| `MaxSpread` | Spread never goes above this. |
| `SpreadRecovery` | Bloom removed per second once the player stops firing. |
| `AimSpreadScale` | Whole spread is multiplied by this while aiming. |
| `RecoilClimb` | How far the camera climbs per shot of a spray. |
| `RecoilSway` | How far a long spray drifts side to side. |
| `ScopeFov` | Scoped guns only: field of view when fully zoomed in. |

## CS2-style recoil: how it works
Like Counter-Strike 2, recoil and inaccuracy are two separate systems.

### 1. Spread (server, random)
- The first shot uses `BaseSpread`, so it lands where the crosshair points (Max Payne 3's "first shot is the accurate one").
- Each quick follow-up shot adds `SpreadPerShot`, up to `MaxSpread`.
- Nothing recovers while the trigger is held at full rate. Spread only starts to shrink once the pause between shots is longer than the gun's normal shot interval. It then drops by `SpreadRecovery` degrees per second. Holding the trigger keeps building spread; tapping or short bursts let it settle.
- Aiming multiplies the whole cone by `AimSpreadScale`.
- The server picks each bullet's random direction inside that cone, so spread can't be cheated away.

### 2. Spray pattern (client camera, fixed per gun)
- Each shot of a spray moves the camera along a set path. It climbs `RecoilClimb` per shot for the first 8 shots, then a quarter of that per shot. From about the 4th shot it also drifts side to side, up to `RecoilSway` × 6 degrees.
- The side-to-side curve is fixed per gun (seeded from the gun's name), so a gun always sprays the same way and players can learn to pull against it.
- "Heat" counts the shots in the current spray. It recovers at the same pace as bloom, so the camera drifts back to where the player aimed once they stop firing.
- On top of the pattern, every shot gives a sharp jerk: 60% of `RecoilClimb` upward plus a small random sideways twitch. It settles in about 0.1 s.
- Bullets go where the centre of the screen points, so the pattern really moves the shots. Pulling the mouse down against the climb keeps a spray on target.

### Measured in play (2026-10-31)
- AK-47 from the hip, 10-shot burst: 0.2° on the first shot, growing to about 4°.
- The same burst while aiming: 0.3°, growing to 1.8°.
- M4 spray pattern: about 4.7° up after 10 shots, then swaying about ±2.7°.
- MP5, 0.6 s burst: the camera climbed 3.7° and was back to 0° 1.5 s after release.

## Aiming and the sniper scope
- **Aim:** right mouse button (gamepad L2), held. The camera moves in close to the shoulder and the field of view narrows from 70 to 52. Spread is multiplied by `AimSpreadScale`. Sprinting stops while aiming.
- **Sniper scope (M107):** after the normal aim zoom, a second, slower and heavier push takes the view to 10. At 85% of that push the scope overlay appears with a quick fade from black. From the hip the overlay appears about 0.45 s after pressing aim. Letting go zooms out quickly. Turning speed scales with zoom, so scoped aiming stays steady.
- Switching guns while aiming blends smoothly in both directions; it never snaps.

## Tracers, muzzle flash and impacts
- **Tracers:** each bullet is a 7-stud glowing streak made of two beams: a wide warm glow around a thin hot core. It travels from the barrel at the gun's `BulletSpeed` (measured: 2,000 studs/s for the AK). Every client draws every shot. Because damage is hitscan, the hit lands slightly before the tracer arrives (under 0.1 s at normal ranges).
- **Muzzle flash:** a real `PointLight` (brightness 6, range 14, shadows on) switched on for 0.05 s per shot, so each shot briefly lights the room. Flame, spark and smoke particles burst at the muzzle. All textures are Roblox built-ins, so nothing had to be uploaded.
- **Gun kick:** the slide, bolt or pump snaps back on every shot.
- **Impacts:** sparks and dust on surfaces, a dark red burst on bodies (the server tells clients which pellets hit a body).

## Known limits and next steps
- No ammo pickups yet. Dropped guns lie on the floor for 30 s, then despawn.
- Recoil runs on the player's own camera, so a cheat could remove it. Spread can't be removed, because the server applies it.
- "Aiming" is a flag the client sends with each shot, so a cheat could always claim it for tighter spread. Later, aiming should cost something the server can check.
- No sounds yet. Two Roblox library sounds to try are listed in [[Blender and Asset Pipeline]].
- No animations, by design for this milestone.
