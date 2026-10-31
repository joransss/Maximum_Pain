# Changelog

Every change to the game, newest first. Each entry says what changed, the decisions behind it, what was tested, and what was left out.
System details: [[Architecture]] · [[Movement State Machine]] · [[Loadout and Dual Wielding]] · [[Cover System]] · [[Shoot-Dodge]] · [[Last Stand and Bullet Time]] · [[Animation Hooks]] · [[Test Arena]] · [[Weapons and Recoil]] · [[Limb Health]] · [[HUD Layout]]

## 2026-10-31: Loadouts, stances, cover, shoot-dodge and Last Stand
**Changed**
- **Loadouts:** two one-handed guns (keys 1, 2) and one two-handed gun (3). **Dual wielding** on 4; drawing both one-handed guns **drops the two-handed gun** on the floor. The two-handed gun is never holstered: it rides in the left hand while a one-handed gun is out, as in Max Payne 3. See [[Loadout and Dual Wielding]].
- **Guns are now Models, not Tools** (a character can only hold one Tool). They hang from Motor6Ds (`RightGrip`, `LeftGrip`, `Holster`) that animations can move.
- **Dropping and picking up:** G drops, F picks up or swaps; guns keep their ammo. Death drops what was in the hands. The Uzi is now one-handed.
- **Reloads** move ammo only when the server's timer finishes, so interruptions lose and duplicate nothing. Dual reloads take the longer time ×1.5. Switching guns takes a short draw time.
- **Movement state machine** (`StanceRules`): one stance at a time (standing, sprinting, crouching, four cover stances, three dive stances, getting up, Last Stand, dead), with what each allows and which stances follow. The client predicts and the server confirms, rejects or forces. See [[Movement State Machine]].
- **Sprint** is now a stance: firing ends it (0.2 s before the gun can fire), it can't start in cover, and reloads carry on.
- **Free crouch** on C, with a headroom check under low ceilings.
- **Cover** on E: high and low cover, sliding along walls, stopping at ends, inside corners, swinging round outside corners, popping out to aim, blind fire, and the shoulder camera following the side. See [[Cover System]].
- **Shoot-dodge** on Left Alt or V: a 0.2 s run-up, dives in any direction, a long low flight, wall stops and slides, a floor slide, lying down aiming, getting up. See [[Shoot-Dodge]].
- **Last Stand:** a killing blow on a player with a painkiller and a loaded gun drops them into localized bullet time with the camera dragged onto the killer; killing or downing the killer in 4 s costs a painkiller and all adrenaline, followed by a 3 s defenseless wakeup. See [[Last Stand and Bullet Time]].
- **Bullet time** exists as a local bubble (`TimeScale` on characters), and the HUD's slim bar is now the **adrenaline** meter.
- **Accuracy modifiers** for walking, sprinting, crouching, jumping, diving, blind fire, peeking, aiming from cover and dual wielding.
- **Shots leave from a server-placed muzzle** and are blocked by anything solid in the gun's path; the reticle shows a cross when blocked.
- **Aiming is tracked by the server** (0.15 s settle time) instead of a flag on each shot; aiming slows walking to 70%.
- **Server checks** for every stance request, dive, cover claim, hold, drop and pickup, plus a movement-speed check that puts speeders back.
- **Animation preparation:** every animation has an empty slot in `AnimationConfig`; `AnimationController` will play them, stretching reloads to the server's timers. See [[Animation Hooks]].
- **HUD:** three fixed gun rows, pickup and cover prompts, short messages, a stance tag, the Last Stand countdown, a bullet-time label, the dual-wield warning, a blocked reticle.
- **Code layout:** new shared modules `StanceRules`, `CoverRules`, `DodgeRules`, `ShotRules`, `LoadoutRules`, `LastStandRules`, `AnimationConfig`; new server modules `StanceService`, `LoadoutService`, `LastStandService`, `BulletTimeService`; `CharacterServer` replaces `LimbServer`; `WeaponServer` rewritten; new client controllers `Keybinds`, `CoverController`, `DodgeController`, `LastStandController`, `AnimationController`, `WeaponEffects`; `CharacterController`, `WeaponController`, `CameraController` and `Hud` rewritten or extended. New remotes `StanceRequest`, `StanceResult`, `WeaponAction`, `LastStandEvent`. See [[Architecture]].
- **Test arena** north of the spawn: cover walls, a pillar, crates, an inside corner, a dive lane, a ledge, a crouch tunnel, a table with every gun, target dummies and a gunman that shoots back (press T). See [[Test Arena]].

**Decisions**
- The sawn-off stays one-handed (as in Max Payne 3 and the previous build), even though it is a shotgun. One line in `WeaponConfig` changes it.
- Dodge on Left Alt or V, cover on E, pick up on F, drop on G, crouch on C. Space stays jump. Shift stays sprint.
- During a Last Stand the downed player can't be hurt; only the window and line of sight decide. The killer's way out is to hide.
- High cover can only be aimed or blind fired from an end, as in Max Payne 3 (lean out at a pillar).
- No slow motion during dives: Max Payne 3's multiplayer isn't confirmed to have it, and slowing a whole server isn't possible.
- This place has no Roblox PlayerModule, so the client reads WASD and the left stick directly.

**Tested in Studio play mode** (details in [[Test Arena]])
- Crouch, the tunnel's headroom check, sprint and the trigger ending it.
- Dual wield and the drop, pickups and swaps, interrupted and full reloads, dual reloads, dropping with G.
- High and low cover, ends, pop-out and back, inside corner, circling the pillar, aimed shots and blind fire from cover, blocked blind fire.
- Forward, sideways and backward dives, a head-on dive into a wall, getting up.
- Last Stand: start, camera lock, bullet time on the killer, success with its costs, the wakeup, failure by timeout, instant death without painkillers.
- Arm injuries ending dual wielding; the server pulling back a faked speed hack. No errors in the output.

**Not done or not tested**
- No animations (as requested); the body sinks for crouches and guns hang from the hands. No sounds.
- Not tested with two real players or under lag; no touch controls.
- The angled wall, the ledge dive and Last Stand's line-of-sight failure weren't tried in play. Studio's Script Analysis wasn't checked.
- Player-triggered bullet time from the adrenaline meter, vaulting, cover-to-cover moves and rolling on the floor aren't built.

## 2026-10-31: HUD restyled to match the Max Payne 3 reference
**Changed**
- **Health display:** the boxy body figure is replaced by a 3D human figure, matching your AK screenshots. It is Roblox's "Man" body, seen from behind in see-through grey. Each limb fills red from its lowest part up (feet first), and a limb in the red is red all over.
- **Painkiller count:** now a black number in a white square on the figure's back.
- **Slim bar:** a white bar beside the figure, a placeholder for the future bullet-time meter.
- **Status text:** red text with no box.
- **Gun list:** restyled to match the figure. No black tiles or white outlines; the guns are see-through grey shapes and the gun in hand is bright white. Ammo is written like Max Payne 3's "30 120": magazine in bold white, spare rounds in grey.
- **Keybinds:** unchanged, as asked.
- `ReplicatedStorage.Assets.UI.HealthFigure` added. `WeaponController` now sends the HUD numbers instead of a ready-made ammo string.

**Tested**
- Previewed in edit mode, then checked in play mode with no errors.
- The equipped AK row read "0 | 26 | 30" after a burst.
- With the left leg half damaged, the foot showed red, the shin half red and the thigh grey. The right arm in the red was fully red, and its two-handed guns faded in the list.

**Not done**
- The figure is chunkier than Max's slim one; a custom figure would need modelling.
- The bullet-time bar doesn't move yet.

## 2026-10-31: Weapon overhaul, camera, limb health and HUD
**Changed**
- **Ammo:** every gun now spawns with a full magazine plus **one spare magazine** (was several spare magazines).
- **Recoil:** CS2-style. Server-side spread grows while firing and settles after a pause. A fixed spray pattern per gun moves the camera, and each shot adds a sharp jerk.
- **Aiming:** right mouse button. The camera zooms in and spread tightens. The Barrett M107 gets a heavy second zoom into a scope overlay.
- **Tracers:** the thin instant line is replaced by a two-beam glowing streak that travels at the gun's bullet speed.
- **Muzzle flash:** the glowing ball is replaced by a real light that briefly lights the surroundings, plus flame, spark and smoke particles.
- **Impacts:** sparks and dust on surfaces, blood on bodies.
- **Camera:** locked to third person over the shoulder, with no first-person view. Q swaps shoulders. The character always faces where the camera points.
- **Limb health:** head, torso, both arms and both legs each have their own health. Limping, crawling, one-arm and disarmed rules apply, and the head or torso in the red kills.
- **Painkillers (H)** heal every limb. Players start with 3.
- **Shoot-dodge hooks:** the `ShootDodgeScale` attribute (1, 0.4 or 0) is ready for the dive when it's built.
- **Sprint** on Shift, blocked by limping or aiming.
- **HUD:** keybinds bottom left; weapon slots with white outline icons and ammo bottom right; body figure with painkiller count and status tag. Roblox's own hotbar and health bar are off.
- **Weapon switching:** keys 1–0 and the mouse wheel, since the Roblox hotbar is gone.
- **Code layout:** split into modules. Server: `WeaponServer`, `LimbServer`, `LimbService`. Shared: `WeaponConfig`, `WeaponMath`, `LimbRules`. Client: `ClientMain` starting `CameraController`, `CharacterController`, `WeaponController` and `Hud`. The old `WeaponClient` was removed.
- `StarterPlayer.EnableMouseLockOption` turned off, so Roblox's shift-lock doesn't fight the camera or the sprint key.

**Decisions**
- Hits stay instant (hitscan), as the networking notes recommend for the first prototype. The tracer only shows the bullet's travel.
- Recoil lives on the client camera; spread stays on the server. A no-recoil cheat is possible, but a no-spread cheat isn't.
- The client tells the server whether it is aiming. This is cheatable for now and logged as a follow-up.
- Weapon icons are drawn from untextured copies of the real gun models, so no images had to be uploaded.
- The "one magazine, no reserve" line in [[Max Payne 3 HUD and Combat UI Reference]] was replaced by this milestone's rule: one spare magazine.

**Tested in Studio play mode**
- No errors in the output log.
- Camera: locked third person on the right shoulder; Q moved it to the left shoulder and back.
- Aim zoom: 70 to 52 for normal guns. The sniper reached its overlay at 0.45 s, and switching guns mid-aim blended smoothly both ways.
- Firing: the MP5 fired at its rate. The muzzle light lit up during the burst and switched off after. The camera climbed 3.7° and recovered within 1.5 s.
- Spread on the server: AK hip 0.2° growing to 4°; aimed 0.3° growing to 1.8°.
- Tracers travelled at the configured speed (AK 2,000 studs/s) with a 7-stud streak.
- Reload used the single spare magazine (MP5 21 rounds → 30 / 21).
- Sprint: walk speed 24, back to 16 on release.
- Every limb rule, painkiller use and cooldown, gun dropping and equip blocking, real shots hitting the right limbs on a dummy, and torso death with a clean respawn. Details in [[Limb Health]].

**Not done or not tested**
- No animations (as requested), sounds, ammo pickups or touch controls.
- The shoot-dodge itself isn't built; only its hooks exist.
- Not yet tested with two real players or under network lag. Not tested on phones or consoles.
- Studio's Script Analysis (strict type warnings) wasn't checked. Only runtime errors were watched.

## 2026-10-31: First working guns
- Made the 13 guns in `ServerStorage.WeaponKit` usable: server-checked hitscan shots, ammo and reloads, fire-rate limits, spread that grows while firing, slide kick, muzzle flash and tracers, an ammo readout, and a Studio-only test loadout.
- Tested: fire rate, spam and bad-data rejection, walls blocking shots, shotgun pellets, headshots, reload cancelling, respawn.
- Superseded the same day by the overhaul above.
