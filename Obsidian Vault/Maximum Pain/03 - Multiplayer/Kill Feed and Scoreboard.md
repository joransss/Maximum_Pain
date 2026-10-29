# Kill Feed and Scoreboard

## Scoreboard Fields
- Player display name
- Eliminations
- Deaths
- Assists, if supported
- Ping indicator only if useful and reliable
- Team, if using team modes

## Kill Feed
- Show validated eliminations
- Use a short display duration
- Avoid displaying untrusted client-submitted kill claims
- Handle players leaving the server

## Test Cases
- [ ] Scores update once per elimination
- [ ] Death does not count as an elimination
- [ ] Disconnects do not leave stale entries
- [ ] Round reset clears or archives scores as intended
