# Completion plan — 2026-11-08

Goal: implement and verify the 28-task dealership rubric in Huynguyen736's fork.

Design: retain the upstream Django/React application and Apache-2.0 attribution. Serve the React production build and static About/Contact pages from Django on one origin. Persist dealers/reviews in Django SQLite for a self-contained deployment; retain original Express service as reference, clearly document this adaptation. Session authentication with CSRF protection, server-side review ownership, deterministic local sentiment analysis. Real evidence only; inherited screenshots are reference material, never represented as this fork's runs.

1. Import Willie-Conway history without replacing fork history; preserve license and provenance.
2. Backend lane: implement models, seed data, auth and dealer/review/car/sentiment APIs with regression tests. Own server/djangoapp only.
3. Frontend lane: repair React routing, forms, state filtering and review flows; complete About/Contact. Own server/frontend only.
4. Integration lane: settings, static/build serving, environment-based deployment configuration, GitHub Actions and documentation.
5. Run backend tests, lint, production frontend build, browser verification and actual cURL commands. Capture fresh local screenshots with URL bar.
6. Commit and push to authorized origin; observe real GitHub Actions result and save actual logs.
7. Deploy to user's chosen available hosting account; verify live application and capture deployment screenshots. If account access is unavailable, explicitly retain these tasks as blocked rather than fabricate evidence.
8. Produce a task-by-task submission index with actual URLs, command outputs and images.

Success: all 28 tasks have real verifiable artifacts; no fake CI logs, copied evidence or invented deployment URL. Public URL and hosting credentials are external prerequisites.
