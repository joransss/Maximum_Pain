# Max Payne 3 Kill Cam

Research behind the game's kill cam, and what was built. Written 2026-11-02.
Related: [[Euphoria-style Reactions and Ragdolls]] · [[Max Payne 3 Mechanics Reference]] · [[Max Payne 3 HUD and Combat UI Reference]] · [[Architecture]]

## What Max Payne 3 did (read in 2012 previews and reviews, not checked against footage)
- **Single player:** the earlier games' bullet-time camera became a "final kill" cam. It triggers on the last enemy in an area and follows the bullet in, and the player can slow the bullet down. ([PAX East preview](https://thegamefanatics.com/pax-east-max-payne-3-aims), [GamesRadar](https://www.gamesradar.com/max-payne-3-multiplayer-guide/4))
- **Multiplayer:** each death shows a comic-panel image of the killer and the victim, with a target indicator showing where the fatal shots hit; one preview called the indicator the real innovation. ([VideoGamer preview](https://www.videogamer.com/?p=143171))
- **Presentation:** the comic-panel framing is part of the game's cinematics; its panel generator works on in-game footage in real time, so cinematics flow into play without loading screens. ([Gaming Nexus](https://www.gamingnexus.com/FullNews/Max-Payne-3-shows-off-its-fancy-visual-effects-and-cinematics/Item25914.aspx))

These are pre-release and launch articles. None of the sources showed the released game's multiplayer death panel, so its exact layout still needs checking in footage, with timestamps, before it's copied more closely.

## What Maximum Pain built (`KillCamController`)
It is local to the player who died; the server and everyone else carry on as normal. It runs in about three seconds and ends as they respawn:
1. **Bullet:** the camera rides the killing bullet from the killer's gun to the body.
2. **Impact:** a close, side-on look at the body taking the hit in slow motion, with the hits marked red.
3. **Panel:** a low, slow turn round the falling body, beside a panel of the killer as they fired, their gun, and a small figure marking where the fatal shots hit (Max Payne 3's indicator).

The real body falls in real time (it is a ragdoll, see [[Euphoria-style Reactions and Ragdolls]]). So the camera records every part of it each frame and plays the recording back, slowed, on a local copy, with the real body hidden. The killing shot and the shooter come from `HitReactions.recentHits`; a Last Stand's killer takes priority. In Studio, a `DebugKillCamSlow` number on the player stretches the whole sequence for inspection; raise `Players.RespawnTime` to match.

## Not done
- Checking the panel's layout against Max Payne 3 multiplayer footage.
- A kill cam for the killer, or for spectators.
