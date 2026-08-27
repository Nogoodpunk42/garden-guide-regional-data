# Vegetable evidence correction 03

Reviewed: August 27, 2026

## Outcome

Celery and parsnip are eligible home-garden recommendations throughout New Jersey. South Jersey
pack version 2 replaces the prior commercial-production citations with Rutgers NJAES FS129.
North/Central Jersey pack version 3 carries direct override reviews for both crops so the corrected
evidence does not depend on the order in which a user installs the South and North/Central updates.

The North/Central pack now covers 49 plant identities and 50 unique recommendation records.

## Primary evidence

Rutgers NJAES Fact Sheet FS129, *Planning a Vegetable Garden*:

- https://njaes.rutgers.edu/fs129/

The New Jersey home vegetable planting guide lists celery as a transplant for May and June. It
lists parsnip as a seeded crop for April. These rows establish both home-garden scope and statewide
New Jersey planting windows.

## Decisions

| Plant | Status | Action | Months | Evidence |
|---|---|---|---|---|
| Celery | `recommended` | Use transplants | May, June | Rutgers NJAES FS129 |
| Parsnip | `recommended` | Direct sow fresh seed | April | Rutgers NJAES FS129 |

The prior commercial-production sources remain useful technical references, but they are no longer
used as the catalog's primary evidence for these homeowner recommendations.

## Release gates

- Both corrected South Jersey reviews must cite Rutgers NJAES FS129.
- North/Central must contain exactly two direct override reviews: celery and parsnip.
- Both overrides must be `recommended` and cite Rutgers NJAES FS129.
- Celery must retain the May–June transplant window.
- Parsnip must use the April direct-sow window.
- The North/Central pack must resolve to 49 identities and 50 unique recommendation keys.
- Manifest checksums, byte counts, pack versions, and detached signature must verify in CI.
