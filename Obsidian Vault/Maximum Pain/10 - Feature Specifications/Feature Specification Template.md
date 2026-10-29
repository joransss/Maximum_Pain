# Feature Specification Template

> Copy this note for each major feature. Keep values marked **TBD** until tested.

## Status
- Design: Draft / Reviewed
- Implementation: Not started / In progress / Implemented
- Verification: Not tested / Passing / Failing
- Owner: Claude Code / Human review
- Dependencies: TBD

## Purpose
What problem does this feature solve and what player experience should it create?

## Player-facing behaviour
- Inputs:
- Preconditions:
- Success result:
- Failure result:
- Feedback:
- Interactions with other mechanics:

## Rules and tuning
| Parameter | Initial value | Status / rationale |
|---|---|---|
| Cooldown | TBD | Needs playtest |
| Duration | TBD | Needs playtest |
| Resource cost | TBD | Needs playtest |

## Technical design
- Client responsibilities:
- Server responsibilities:
- State transitions:
- Remotes / payloads:
- Replication requirements:
- Data required:
- Animation / audio / VFX:

## Exploit and failure cases
- Invalid input:
- Spam:
- Death / respawn during action:
- Disconnect during action:
- Latency / replication delay:
- Collision / obstruction:
- Interaction with another active state:

## Acceptance criteria
- [ ] Normal use works.
- [ ] Invalid use is rejected server-side.
- [ ] State resets correctly after death/respawn.
- [ ] Tested with at least two clients.
- [ ] No relevant errors in Output.
- [ ] Performance impact reviewed.
- [ ] Documentation updated.

## References and decisions
- References:
- Decisions:
- Open questions:
