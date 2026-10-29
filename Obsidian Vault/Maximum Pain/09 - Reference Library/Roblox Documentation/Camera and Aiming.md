# Camera and Aiming — Reference Notes

Primary source: https://create.roblox.com/docs/workspace/camera

## Design requirements
- Third-person over-the-shoulder camera with a configurable shoulder offset.
- Camera should keep targets visible during normal movement and aiming.
- Camera collision must prevent clipping through walls where practical.
- Aiming should tighten camera framing without making movement unresponsive.
- Crosshair represents the intended aim ray; server hit validation must account for the camera and character muzzle not being at the same position.
- Camera shake and recoil are feedback, not substitutes for accurate aim logic.

## Acceptance checks
- Player can orbit the camera without unintended character rotation.
- Aiming changes framing consistently.
- Close walls do not hide the player or cause extreme camera snapping.
- Crosshair placement and hit ray agree sufficiently for fair play.
- Test on low frame rate and different aspect ratios.
