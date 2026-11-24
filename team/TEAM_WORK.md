# Reddit Forum - Team Work Split

The runnable project lives inside `team/`, so the repository root stays clean.

| Member | Weightage | Owns |
| --- | ---: | --- |
| Sameer Alam | 35% | Django project setup, home feed, shared layout, styling, InsForge deployment/schema coordination |
| Kshitiz Kumar | 16.25% | User accounts, registration, login, profiles and password flows |
| Aaditya Verma | 16.25% | Communities: creation, membership and community pages |
| Saksham Yadav | 16.25% | Posts: text/link/image posts and post detail pages |
| Aditya Kumar | 16.25% | Comments, voting, direct messages and conversations |

## Run locally

```bash
cd team/sameer_alam/project
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

The app uses InsForge directly. User accounts, forum records and media are not stored in SQLite. Keep backend keys in local environment configuration, never in committed source files.
