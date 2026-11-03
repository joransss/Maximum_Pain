# Euphoria-style Reactions and Ragdolls

Research behind the game's hit flinches and deaths, and how they are built. Written 2026-11-02.
Related: [[Max Payne 3 Animation Reference]] · [[Max Payne 3 Mechanics Reference]] · [[Max Payne 3 Kill Cam]] · [[Architecture]] · [[Limb Health]]

## What Euphoria is (read, not seen)
- NaturalMotion's Euphoria is middleware that makes characters move by combining physics, simulated muscles and motor control, and behaviours, instead of playing fixed animations. Rockstar used it in GTA IV, Red Dead Redemption and Max Payne 3. ([Wikipedia: Euphoria](https://en.wikipedia.org/wiki/Euphoria_(software)))
- Max Payne 3 ran Euphoria together with Rockstar's RAGE engine, as confirmed by Game Informer in July 2009. (cited by Wikipedia, above)
- Rob Nelson, the art director, said the team refined the hit reactions so shots feel more connected than in Red Dead Redemption. He described Euphoria as a set of tunable behaviours, and physics blended with a library of animated poses, using the shoot-dodge as his example. ([MCV, citing GameSpot](https://mcvuk.com/development-news/max-payne-3-dev-explains-euphoria-engine-tweaks/))
- Press coverage of the game's technology described RAGE carrying much of the work alongside the physics. ([TechRadar](https://www.techradar.com/news/gaming/the-technology-of-max-payne-3-1082751))

All of this is 2009–2012 press and developer talk, read rather than checked against footage. The frame-by-frame observations of hits and deaths are in [[Max Payne 3 Animation Reference]].

## What Roblox offers (read)
- **Avatar joint upgrade:** a character's Motor6D joints can be replaced by three constraints:
  - a BallSocketConstraint, which keeps the parts together and limits each joint to a cone;
  - an AnimationConstraint, which drives the part (kinematic, or with forces and torques when `IsKinematic` is false, so physics can act on it);
  - and, between some parts, a NoCollisionConstraint.
  ([DevForum beta](https://devforum.roblox.com/t/studio-beta-avatar-joint-upgrade-enabling-physically-simulated-characters/3266099), [launch post](https://devforum.roblox.com/t/avatar-joint-upgrade-for-physically-simulated-character-movement-is-now-live/4298561))
- **Which characters get the upgrade:** only characters spawned through the player flow or built from a HumanoidDescription; models already placed in the world aren't changed, and R6 isn't supported. Developers on those threads recommend keeping the Root and Waist joints kinematic to avoid wobble while running, and switching off breaking joints on death to get a ragdoll. (same threads)

## How Maximum Pain does it
| Effect | Where | How |
|---|---|---|
| Flinches | `HitReactions` (every client, every character) | Each hit kicks springs on the joints near the wound. The kick turns each joint the way the bullet pushes about it (the lever from the joint to the wound, crossed with the bullet's direction). The springs rebound and settle in about a quarter of a second, within per-joint limits. A chest hit snaps the head back like whiplash; a leg hit buckles the knee. Only joint rotations change, so movement, aim and hit boxes are untouched. Flinches slow down in bullet time. |
| Deaths | `RagdollRules`, `RagdollService`, `RagdollController` | No death animation: the body becomes an active ragdoll. Every AnimationConstraint stops following the animation and becomes a muscle pulling toward a collapse pose (knees buckling, body folding over), with a strength that fades over about a second, so the body crumples before it goes limp. The ball sockets keep the limbs within human limits. The body keeps its momentum, and the killing shot pushes the part it hit. A player's own client simulates their body; the server does it for dummies. |
| Death push and kill cam | `HitReactions.recentHits` | An 8-second log of hits on each character, read by the death push and by the [[Max Payne 3 Kill Cam]]. Until 2026-11-02 the log could vanish at random (a weak-keyed table). |

Only upgraded joints ragdoll; an old Motor6D rig stays rigid.

## Ideas not built yet (not from the sources)
- Staggering or catching a fall instead of only flinching, which Euphoria's balance behaviours are known for.
- Reactions to falls and impacts while alive, not only to shots.
- Ragdolls for Motor6D rigs, by adding ball sockets at death.
