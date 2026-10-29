# Progression and Cosmetics

## Scope
Long-term system; implement only after the core match loop and combat are stable.

## Design constraints
- Cosmetic rewards should not create pay-to-win advantages.
- Server validates unlocks, inventory changes, purchases and currency.
- Persistent data must handle retries, failed writes, duplicate requests and schema changes.
- Never trust client-provided price, reward amount or ownership.
- Avoid implementing paid cases or monetisation until platform policy, age-appropriate design, disclosure and local legal requirements have been reviewed.

## Acceptance criteria
- [ ] Ownership is server-confirmed.
- [ ] Invalid or repeated purchase requests cannot duplicate rewards.
- [ ] Save failures are handled and logged.
- [ ] Cosmetic changes do not affect hitboxes or combat stats.
