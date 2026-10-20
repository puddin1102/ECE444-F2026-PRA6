# PRA6 explanation and demo guide

## What you built

Flask handles HTTP requests. Routes in `project/app.py` authenticate the admin and read or write posts using SQLAlchemy. Jinja renders the HTML templates. Bootstrap and the stylesheet format the pages. JavaScript calls the deletion endpoint and refreshes the page. Locally, posts live in SQLite; the deployed app connects to Postgres through `DATABASE_URL`. Vercel runs the Flask app, while the database service stores the posts independently of Vercel instances.

## Explain TDD in your own words

1. **Red:** Write a test describing the desired behavior and run it before the behavior exists. A failure demonstrates that the test detects the missing feature.
2. **Green:** Add enough implementation to satisfy the test.
3. **Refactor:** Improve structure while preserving behavior, then rerun all tests.

This repository first defined blog tests, ran them (17 failed, 1 database test passed), implemented the blog (18 passed), then defined search and access tests (10 failed) before implementing those features (28 passed total). Logs are saved under `docs/`; the commit history preserves those stages. The `login_required` decorator replaces repeated login checks; base and partial templates remove duplicated HTML.

## How the tests work

`tests/conftest.py` defines pytest fixtures. `app(tmp_path)` creates a new Flask application with test configuration and a unique temporary SQLite file. It creates tables before yielding the app, then removes the session, drops test tables and disposes the engine afterwards. `client` returns Flask's test client, which sends requests without a real web server. `logged_in` logs that client in before a test. Each test is isolated; no deployed data is reset.

`assert` checks the expected result. A status code alone is often too weak: a deletion test should check that the actual row disappeared. Authorization tests must also check that a denied operation left the row intact.

| Test/group | What to explain |
| --- | --- |
| `test_index`, `test_empty_db` | Home responds with 200 and the correct empty message. |
| `test_database` | SQLAlchemy created a real SQLite test file and the `post` table. |
| `test_login_page`, `test_login_logout` | Login renders; valid credentials set the session; logout clears authentication. Redirect following lets the test inspect the resulting flash message. |
| `test_invalid_login` | Parameterized wrong username, wrong password, and empty credentials; none gets an authenticated session. |
| `test_messages` | A logged-in user creates a database row. Titles are escaped, while permitted body formatting survives. |
| `test_post_requires_login` | Anonymous posting returns 401 and inserts nothing. |
| `test_reject_invalid_post` | Missing/blank fields and a title over 200 characters produce 400 and no insert. |
| `test_newest_post_first` | Two posts appear in descending ID order. |
| `test_delete_message` | An existing post is deleted and JSON reports success. |
| `test_delete_nonexistent_message` | A missing row produces 404 instead of falsely reporting success. |
| `test_html_sanitized` | Basic bold formatting survives, while script tags and event handlers cannot run. |
| `test_search_page_without_query` | A search page loads before input; it does not dump all posts. |
| `test_search_title_and_body_case_insensitive` | Student-designed cases match titles or body text, ignore case and trim spaces, while excluding unrelated posts. |
| `test_search_no_matches`, wildcard and escaping tests | No-result feedback, literal `%` handling, and safe rendering of a query containing HTML. |
| `test_anonymous_delete_denied_and_post_preserved` | Student-designed access test: a 401 JSON response plus proof that the database row survives. |
| `test_logout_revokes_delete_access` | Logging out prevents deletion using the previously authenticated client. |
| `test_anonymous_missing_post_still_requires_login` | Authentication happens before looking up a post, even when the ID does not exist. |

The tests combine unit-style checks with route/database integration tests. They do not by themselves prove that the live Postgres connection, Vercel runtime, or browser JavaScript works; demonstrate those separately.

## Components the TA may ask about

- **GET vs POST:** GET reads pages/query strings; POST carries submitted form data. The tutorial uses GET for deletion; discuss why a production app should use a CSRF-protected POST or DELETE instead.
- **Flask factory:** `create_app(config)` builds the app after choosing its configuration. This prevents SQLAlchemy from binding test requests to a previously initialized production database.
- **SQLAlchemy model:** `Post` has a primary-key ID, required title and required body. `db.session.add()` stages an object; `commit()` persists it. Selecting/deleting models avoids concatenating untrusted input into SQL.
- **Sessions and secret:** Flask signs its session cookie using `SECRET_KEY`. Signing prevents undetected changes; it does not encrypt the contents. Never put passwords in the session. A stable secret lets sessions survive different server instances.
- **Decorator:** `@login_required` checks `session['logged_in']` before a route runs. `@wraps` preserves the function name so Flask can register distinct endpoints.
- **Search:** It reads `query`, trims spaces, and applies case-insensitive substring conditions to both title and body. `autoescape=True` treats `%` and `_` literally rather than as SQL wildcard instructions.
- **HTML:** Jinja escapes a title/query. Body content passes through an allowlist sanitizer before the template marks it safe.
- **JavaScript:** The Delete button triggers `fetch`; the JSON result and HTTP status determine success. A network/authentication failure shows a visible message and re-enables the button.
- **Deployment:** Vercel runs application code; Render stores persistent Postgres data. An external URL is required because Vercel is outside Render's private network. `.env` and Vercel variables keep secrets out of Git.
- **Coverage:** The saved run measures 93% of Python statements. Coverage shows what executed, not whether every important behavior is correct; assertions and edge cases matter more than the percentage.

## Five-minute demo

1. Open your GitHub repo, show the project files and actual red/green commits.
2. Run `python -m pytest`; pick one search test and one unauthorized-deletion test and explain their arrange/action/assert steps.
3. Open the live Vercel URL. Log in using the deployment credentials, then add “PRA6 demo” with body “Testing Flask and Postgres.”
4. Search `pra6`, then `POSTGRES`. Explain title/body and case-insensitive matches. Search an unrelated word to show the empty result.
5. Refresh or open another browser session to show the stored post is persistent.
6. Log out. Request `/delete/ID` for that post and explain the 401 response. Show the post still exists.
7. Log in again and delete the demo post using the button. Refresh to show the row is gone.
8. Submit the GitHub URL on Quercus and ensure the TA records your evaluation before the PRA ends.

Practice these explanations yourself. The handout explicitly makes understanding and testing your own responsibility even when you use AI assistance.
