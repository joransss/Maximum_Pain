# Bug Tracker

Create a separate note for any bug that takes more than a quick fix.

## Open Bugs
Minor, from the R15 migration (2026-10-30, [[Implementation Log]]):
- **Foot slip while running:** contact points slide ~1.7 studs/s (median) at 16 studs/s in game, with spikes at touchdown. Clips are foot-planted in Blender; residual comes from playback-speed smoothing. Fix: in-engine foot IK.
- **Support hand off the gun when aiming from the ground:** straight-arm ground aim can't bring both hands together on an R15 body.
- **Reload support hand 0.12 studs short** at one phase (out of reach in the clip).
- **R6 avatars get no animation:** if Game Settings allows Player Choice, an R6 player has no clips or aim layer. Set Avatar Type to R15.

## Bug Template
Copy this section for each issue.

### BUG — [Short title]
- **Status:** Open
- **Severity:** Medium
- **System:** [[Gunplay]]
- **Date:**

**Expected behaviour:**

**Actual behaviour:**

**Steps to reproduce:**
1. 
2. 
3. 

**Exact Output error:**
```text
Paste the full error here.
```

**Root cause:**

**Fix:**

**Regression test:**
- [ ] Original issue is fixed
- [ ] Related behaviour still works
