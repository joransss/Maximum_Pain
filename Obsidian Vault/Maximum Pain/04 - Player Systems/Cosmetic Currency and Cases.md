# Cosmetic Currency and Cases

## Goal
Reward playing and winning with an earnable currency, then let players spend it on cosmetic cases. If Robux can buy the currency, cases are paid random items under Roblox policy and require extra safeguards.

## Economy Principles
- Currency earns through participation, wins, eliminations and objectives.
- Reward participation so new players are not locked out of progression.
- Cosmetics do not change damage, recoil, movement, ability recharge or other competitive stats.
- Keep cosmetics non-tradable at launch.
- Show every possible case outcome and its actual numerical probability before opening a case if any part of the purchase path uses Robux-purchased currency.
- Check Roblox policy restrictions for each player; provide a compliant alternative, such as direct cosmetic purchase, where required.

## Example Starting Rewards (balance through testing)
| Action | Currency |
|---|---:|
| Complete match | 100 |
| Win | +150 |
| Elimination | 10 |
| Objective contribution | 25 |
| Daily challenge | 200–500 |

Example case prices to test: Standard 500, Armoury 2,000, Elite 5,000 currency. These are prototypes, not final values.

## Implementation Tasks
- [ ] Server awards currency from validated match events
- [ ] Persist balances and owned cosmetics safely
- [ ] Prevent duplicate reward grants and negative balances
- [ ] Case UI lists all possible outcomes and numerical odds where required
- [ ] Add duplicate handling (small currency refund or fragments)
- [ ] Add direct-purchase alternative for players restricted from paid random items
- [ ] Check current Roblox policy and player policy flags before enabling paid random cases
- [ ] Do not implement Robux packs until the free economy is balanced

## Monetisation Caution
Buying currency with Robux and then spending it on random cosmetic cases still counts as paid random items. Follow current Roblox Creator Hub policy: https://create.roblox.com/docs/production/monetization/paid-random-items
