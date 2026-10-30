# Camera System

## Goals
- Third-person view with clear character visibility
- Responsive aim mode
- Camera collision with walls
- Readable reticle and target alignment
- Controlled camera feedback during firing and abilities

## Settings to Prototype
- Shoulder offset:
- Field of view:
- Aim sensitivity:
- Aim zoom:
- Camera smoothing:
- Reticle style:

## Test Cases
- [ ] Camera does not clip excessively through walls
- [ ] Aim direction matches server-validated shot direction
- [ ] Camera behaves correctly during dive and respawn
- [ ] Mouse and gamepad input are considered — mouse tested; gamepad bound (left/right trigger, left stick) but untested
- [ ] UI remains readable at different resolutions

## Implemented settings (2026-10-30)
- **Shoulder offset:** (1.75, 0.6, 0); while aiming (1.3, 0.45, 0); centered while diving/prone.
- **Field of view:** 70; aiming ×0.72 (~50); bullet-time activator 62.
- **Aim sensitivity:** ×0.7 while aiming; bullet-time victims ×0.3.
- **Zoom range:** 6–14 studs. **Smoothing:** offset lerp ~0.1 s.
- **Reticle:** single round precision dot (mouse locked to centre).
- Recoil kicks the camera and returns to the original aim.
- **Update (2026-10-30):** the shoulder offset is computed in camera space (camera stays over the right shoulder even when the body faces the camera in cover); body turns are smoothed (~50 ms).
