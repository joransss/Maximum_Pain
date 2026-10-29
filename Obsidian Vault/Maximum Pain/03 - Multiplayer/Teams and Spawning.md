# Teams and Spawning

## Prototype
Use Free-for-All spawn points first unless Team Deathmatch is the first mode.

## Spawn Requirements
- Spawn at valid points
- Avoid direct line of sight to enemies where possible
- Avoid spawning inside geometry
- Clear temporary death state and set health correctly
- Apply spawn protection only if designed and tested
- Ensure spawn protection ends reliably

## Test Cases
- [ ] Every spawn point is reachable and safe
- [ ] Players do not spawn outside the map
- [ ] Spawn selection handles occupied points
- [ ] Respawn works after repeated deaths
- [ ] Team assignments remain valid if using teams
