# Verification record

## Automated

- Local suite: 30 passed; 95% Python statement coverage.
- Black formatting check: passed.
- Flake8: passed.
- GitHub Actions on initial and final implementation pushes: passed. [Run](https://github.com/puddin1102/ECE444-F2026-PRA6/actions/runs/39368317277).

## Local browser

Verified in a clean browser session:

- Home page and empty state render.
- Login with the local demo credentials succeeds.
- A post with `<strong>Flask</strong>` in its body is saved and rendered with formatting.
- Searching uppercase `POSTGRES` matches lowercase/mixed-case body content.
- The JavaScript Delete button removes the test post and refreshes the search results to “No matching entries.”

## Cloud setup

- GitHub repository created as private: https://github.com/puddin1102/ECE444-F2026-PRA6.
- Render Postgres `ece444-pra6-db` created using the Free plan and reported Available.
- Render reports an expiration date of November 18, 2026. Ensure the database remains available for grading.
- Vercel production deployment is READY at https://ece444-pra6.vercel.app/.

Live HTTP verification is recorded in `live-smoke-test.txt`: login, invalid credentials, protected posting, persistent Postgres data across separate cookie sessions, case-insensitive search, protected deletion, logout, authenticated deletion, and static asset delivery. Test-created data was removed after verification.
