# CarConnect â€” Dealership Reviews

**Project name:** Best Cars / fullstack_developer_capstone
**Repository owner:** Huynguyen736
**Course:** IBM Full Stack Software Developer Capstone

A Django + React application for browsing car dealerships, filtering by state,
reading sentiment-tagged reviews and posting authenticated reviews.

## Attribution

Adapted from [Willie Conway's project](https://github.com/Willie-Conway/Full-Stack-Developer-Capstone),
based on the [IBM starter](https://github.com/ibm-developer-skills-network/xrwvm-fullstack_developer_capstone).
Original history and the Apache-2.0 license are retained. See [NOTICE](NOTICE).
The old `Screenshots/` folder is inherited reference material. Evidence generated
from this fork belongs in `submission/` and the named output files at the root.

## Features and architecture

- React routes: `/`, `/dealers`, `/login`, `/register`, `/dealer/1`, `/postreview/1`.
- Static About and Contact pages served at `/about/` and `/contact/`.
- Five-field registration; Django sessions; CSRF tokens on every write.
- Dealer filtering, car makes/models, persistent reviews and root admin.
- Reviewer identity derived from the authenticated user on the server.
- Positive/negative/neutral sentiment using an explicitly local lexicon baseline.
- 50 educational sample dealers and 50 initial reviews, seeded idempotently.
- A single-origin deployment; React is built into the Django container.

This adaptation stores dealers and reviews in Django SQLite instead of depending
on the original external Express/MongoDB and sentiment service URLs. The original
`server/database` and `djangoapp/microservices` directories remain as reference;
they are not required for this deployment. The sentiment baseline is not a
trained language model and has the usual limitations of word-based scoring.

## Run locally

Requires Python 3.12+ and Node.js 22.

```bash
python -m venv .venv
# Activate .venv for your operating system
pip install -r server/requirements.txt
cd server/frontend
npm ci
npm run build
cd ..
python manage.py migrate
python manage.py seed_demo
python manage.py collectstatic --noinput
python manage.py createsuperuser --username root
python manage.py runserver 127.0.0.1:8000
```

Open `http://127.0.0.1:8000/`. Register a user using the website.
Admin: `http://127.0.0.1:8000/admin/`. Passwords and the local database are not committed.

## Verify

```bash
ruff check server/djangoapp server/djangoproj
cd server
python manage.py test djangoapp -v 2
python manage.py makemigrations --check --dry-run
cd frontend
CI=true npm test -- --watchAll=false --runInBand
CI=true npm run build
```

## API

| Method | Path | Result |
| --- | --- | --- |
| GET | `/djangoapp/session` | Session identity + csrfToken |
| POST | `/djangoapp/register` | Register userName, firstName, lastName, email, password |
| POST | `/djangoapp/login` | Login with userName and password |
| POST | `/djangoapp/logout/` | Logout current session |
| GET | `/djangoapp/get_dealers/` | All dealers |
| GET | `/djangoapp/get_dealers/Kansas` | Dealers in Kansas |
| GET | `/djangoapp/dealer/1` | Dealer details |
| GET | `/djangoapp/reviews/dealer/1` | Reviews newest first |
| GET | `/djangoapp/get_cars` | All car makes and models |
| POST | `/djangoapp/add_review` | Authenticated review creation |
| GET | `/djangoapp/analyze/Fantastic%20services` | Sentiment analysis |
| GET | `/djangoapp/health` | Database readiness |

First fetch session with a cookie jar; send `X-CSRFToken` and the same cookies on
writes. Refresh session after login because Django rotates the token.
`scripts/capture_api.py` executes real curl commands and saves the rubric output
files. Set CAPSTONE_USERNAME and CAPSTONE_PASSWORD privately before running it.

## Container and Skills Network deployment

The `server/Dockerfile` uses a Node build stage and a Python runtime stage.
The entrypoint migrates existing schema, seeds missing sample data and collects
static assets before starting Gunicorn on port 8000. Migrations are committed
and checked in CI; they are not generated during container startup.

Inside the authenticated Skills Network Cloud IDE:

```bash
git clone https://github.com/Huynguyen736/xrwvm-fullstack_developer_capstone.git
cd xrwvm-fullstack_developer_capstone/server
bash deploy-lab.sh
kubectl port-forward deployment.apps/dealership 8000:8000 --address 0.0.0.0
```

Open port 8000 using Skills Network Toolbox. The lab URL and namespace in the
script are specific to this user's current lab. Set the matching host if the lab
changes. Deployment secrets are generated inside the lab and never committed.
SQLite lives in an `emptyDir` volume: it survives container restarts in the same
Pod but not Pod replacement or lab reset. This is a temporary course deployment;
use a persistent volume or PostgreSQL for a long-lived application.

## Submission

See `submission/README.md` for the task-by-task index and verification status.
The final grader, not this repository, determines the awarded points.
