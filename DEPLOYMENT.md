# Deploy WeatherBot with a stable public URL

This project now includes a Docker-based setup to run everything behind Nginx, so you can expose a single URL for recruiters.

## What this gives you
- Rasa server (API enabled)
- Action server
- Web UI served via Flask
- Nginx front-end proxy that:
  - serves the web UI at /
  - proxies API calls at /api to the Rasa server

The web client auto-detects environment:
- Local dev (start_bot.bat): calls http://localhost:5005
- Deployed (Docker/Nginx): calls relative /api

## 1) Prerequisites
- Docker installed (Docker Desktop for Windows or Docker Engine on a Linux VM)
- Docker Compose plugin available (`docker compose` command)
- Your WeatherAPI key

## 2) One-time setup
1. Create a `.env` file next to `docker-compose.yml`:
   
   Copy `.env.example` to `.env` and fill your key:
   
   WEATHERAPI_KEY=your_real_api_key

2. Ensure you have a trained model in `models/`.
   - If empty, train one inside the Rasa container:
     
     docker compose run --rm rasa train

   This will produce a model file under `models/` that the server will load on start.

## 3) Run
- Start all services:
  
  docker compose up -d --build

- Open your browser at:
  
  http://<server-ip>/

- The chat UI should load. Messages will be sent to /api/webhooks/rest/webhook via Nginx.

## 4) Custom domain (recommended for your resume)
- Point a domain or subdomain (e.g., bot.yourdomain.com) to your server’s public IP with an A record.
- Easiest HTTPS: put the domain behind Cloudflare (Proxied orange cloud). You’ll immediately get HTTPS without changing this repo’s Nginx config.
  - In Cloudflare DNS, set the record to Proxied.
  - Within a few minutes, https://bot.yourdomain.com should serve your bot over TLS.
- Alternative: terminate TLS on the server (e.g., with Caddy or certbot+Nginx). This repo’s Nginx is HTTP-only to keep things simple.

## 5) Update and restart
- Pull latest changes and rebuild:
  
  docker compose pull
  docker compose up -d --build

## 6) Logs and troubleshooting
- Service logs:
  
  docker compose logs -f rasa
  docker compose logs -f actions
  docker compose logs -f web
  docker compose logs -f nginx

- Common issues:
  - 404 on /api: ensure Nginx is up and `nginx` service depends_on includes `rasa`.
  - Model not loaded: run `docker compose run --rm rasa train` to create a model.
  - Weather key errors: verify `.env` has `WEATHERAPI_KEY` and containers were restarted.

## Alternative: Stable URL from your own computer (no VM)
If you don’t want a server:
- Use Cloudflare Tunnel or ngrok with a reserved domain.
  - Cloudflare Tunnel (free): install `cloudflared`, authenticate, and run a tunnel pointing to `http://localhost:8080`. It gives you a stable subdomain.
  - ngrok (paid for reserved domains): `ngrok http 8080` with an authtoken and a reserved subdomain gives a consistent link.
- Keep your PC on and `start_bot.bat` running; share the Cloudflare/ngrok URL.

## Quick success criteria
- http://<server-ip>/ loads the chat UI
- A message returns a bot response
- If using a domain, https://bot.yourdomain.com shows the same

That’s it—add the URL to your resume and you’re good to go.
