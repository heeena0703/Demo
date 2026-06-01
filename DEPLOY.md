Quick deploy guide

This repo contains a Flask app. The following steps show how to deploy to Render (simple) or AWS Elastic Beanstalk (alternative).

Render (recommended for quick deploy)

1. Create a new Web Service on Render.
2. Connect your GitHub repo and select the repository.
3. Build command: pip install -r requirements.txt
4. Start command: gunicorn app:app
5. Add environment variables in the Render dashboard:
   - SECRET_KEY
   - DB_HOST, DB_USER, DB_PASSWORD, DB_NAME (or set USE_SQLITE=true to use sqlite fallback)
6. Deploy. Render will install dependencies, run migrations (none), and start the Gunicorn server.

Notes:

- The project includes a Procfile for Heroku-style hosts. The `web: gunicorn app:app --bind 0.0.0.0:$PORT` command is set.
- If using SQLite on the host, ensure the instance's filesystem is writable (many PaaS treat the filesystem as ephemeral).

AWS Elastic Beanstalk (alternative)

1. Install and configure the EB CLI and AWS credentials.
2. Create a new Python application and environment.
3. Deploy the repository. Set environment vars in the Elastic Beanstalk console.
4. The EB environment will run `gunicorn app:app` if you set the Procfile or set the startup command.

Security

- Replace `SECRET_KEY` with a secure random string in production.
- Do not commit production DB credentials to the repo; use environment variables.

Troubleshooting

- If a package fails to install on the host, check build logs and add any missing system dependencies.
- If the app can't connect to MySQL, use the sqlite fallback by setting `USE_SQLITE=true` or provide correct DB credentials.

If you'd like, I can:

- Create a deploy-ready GitHub Actions workflow to push to Render or EB automatically.
- Create small start/stop ps1 scripts for local convenience.
