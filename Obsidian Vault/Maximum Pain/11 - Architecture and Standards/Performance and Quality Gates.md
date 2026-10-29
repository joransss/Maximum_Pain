# Performance and Quality Gates

## Before a milestone is complete
- No unexplained errors or warnings in Studio Output.
- Test normal play and failure/interruption cases.
- Use at least two clients for multiplayer mechanics.
- Confirm cleanup on death, respawn and disconnect.
- Check remote traffic frequency and avoid per-frame remotes unless justified.
- Avoid excessive unanchored physics, unnecessary high-frequency raycasts and unbounded effect creation.
- Profile before optimising; record the test conditions and observations.

## Performance goals
Set measurable targets after the baseline is running on representative devices. Do not claim a frame-rate target without testing it.
