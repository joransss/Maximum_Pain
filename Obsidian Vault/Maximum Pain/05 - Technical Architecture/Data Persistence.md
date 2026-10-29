# Data Persistence

## Build Later
Persistent progression is not needed to prove the first combat prototype.

## Potential Data
- Settings
- Cosmetic unlocks
- Lifetime stats
- Progression level

## Requirements
- Server-only data access
- Handle load and save failures
- Use protected calls and sensible retry/backoff policies
- Avoid saving every frame or every small change
- Validate and version stored data
- Consider player leaving and server shutdown
- Do not store sensitive personal data

## Test Cases
- [ ] New player receives defaults
- [ ] Existing data loads correctly
- [ ] Failed load is handled safely
- [ ] Save works after a match
- [ ] Disconnect and shutdown paths are handled
