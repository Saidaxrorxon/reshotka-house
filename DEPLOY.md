# Deploying Reshetki House to a VPS

This is a copy-paste runbook for putting the site on a fresh Ubuntu 22.04+
VPS behind Nginx + Gunicorn, with systemd keeping Gunicorn running and
Let's Encrypt for HTTPS. Any 1 vCPU / 1GB RAM box is plenty for this site.

Run the steps below **on the server** unless noted otherwise. `<APP_DIR>` is
wherever you clone the repo, e.g. `/home/deploy/reshotka-house`.

## 0. Before you start
- Point the domain's DNS **A record** (`reshetkihouse.uz` and
  `www.reshetkihouse.uz`) at the server's public IP. DNS propagation can
  take a while, so do this first.
- Have SSH access to the server as a non-root user with `sudo`.

## 1. System packages

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip nginx certbot python3-certbot-nginx git
```

## 2. Get the code

```bash
git clone <YOUR_REPO_URL> <APP_DIR>
cd <APP_DIR>
```

## 3. Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install django pillow gunicorn
```

(Or `pip install pipenv && pipenv install --deploy` if you prefer to keep
using the `Pipfile`/`Pipfile.lock` as the source of truth.)

## 4. Configure environment variables

```bash
cp .env.example .env
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Paste the generated key into `.env` as `SECRET_KEY=...`. **Do not reuse the
key that's committed in `config/settings.py`'s fallback — treat it as
already leaked.** Double-check `DEBUG=False` and `ALLOWED_HOSTS` match your
real domain(s).

## 5. Django setup

```bash
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py createsuperuser
```

## 6. Gunicorn as a systemd service

```bash
sudo cp deploy/gunicorn.service /etc/systemd/system/reshotka-house.service
sudo nano /etc/systemd/system/reshotka-house.service   # replace <DEPLOY_USER> and <APP_DIR>
sudo systemctl daemon-reload
sudo systemctl enable --now reshotka-house
sudo systemctl status reshotka-house   # should be "active (running)"
```

## 7. Nginx

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/reshotka-house
sudo nano /etc/nginx/sites-available/reshotka-house   # replace every <APP_DIR>
sudo ln -s /etc/nginx/sites-available/reshotka-house /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

At this point `http://reshetkihouse.uz` should load the site.

## 8. HTTPS

```bash
sudo certbot --nginx -d reshetkihouse.uz -d www.reshetkihouse.uz
```

Certbot edits the Nginx config to add the HTTPS server block and redirect
HTTP → HTTPS, and sets up auto-renewal.

## 9. Firewall (if not already configured)

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

## Deploying updates later

```bash
cd <APP_DIR>
git pull
source .venv/bin/activate
pip install django pillow gunicorn   # or: pipenv install --deploy
python manage.py collectstatic --noinput
python manage.py migrate
sudo systemctl restart reshotka-house
```

## Notes
- The SQLite database (`db.sqlite3`) lives on the server's disk — back it
  up periodically (e.g. a cron job copying it off-box). It's gitignored, so
  it's never overwritten by `git pull`.
- Uploaded images (`portfolio/`, `works/`, `catalog_cards/`) also live on
  local disk. Back these up too if that matters to you — there's no cloud
  storage configured.
