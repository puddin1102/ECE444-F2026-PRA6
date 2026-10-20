# Verification record

## Automated

- Local suite: 28 passed; 93% Python statement coverage.
- Black formatting check: passed.
- Flake8: passed.
- GitHub Actions on initial push: passed. [Run](https://github.com/puddin1102/ECE444-F2026-PRA6/actions/runs/39367105685).

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
- Vercel deployment verification is pending account reconnection and database environment setup.

Do not treat local tests as proof of a successful live deployment. Update this record after testing the live URL.
