# VPS Setup Guide

Step-by-step guide for deploying The Sorting Hat on an Ubuntu VPS.

## Prerequisites

- Ubuntu 22.04+ VPS with root access
- Domain `2524.info` pointing to the VPS IP
- SSH access configured

## 1. Install Docker & Docker Compose

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Add deploy user to docker group
sudo usermod -aG docker $USER

# Verify
docker --version
docker compose version
```

## 2. Create Deploy User

```bash
sudo adduser deploy
sudo usermod -aG docker deploy

# Set up SSH key auth
sudo mkdir -p /home/deploy/.ssh
sudo cp ~/.ssh/authorized_keys /home/deploy/.ssh/
sudo chown -R deploy:deploy /home/deploy/.ssh
sudo chmod 700 /home/deploy/.ssh
sudo chmod 600 /home/deploy/.ssh/authorized_keys
```

## 3. Clone the Repository

```bash
su - deploy
git clone https://github.com/joemc3/sorting-hat.git ~/sorting-hat
cd ~/sorting-hat
```

## 4. Configure Environment

```bash
# Root .env (API config)
cp .env.example .env
# Edit .env — set POSTGRES_PASSWORD, LLM keys

# Supabase .env (if using full Supabase stack)
cp deploy/supabase/.env.example deploy/supabase/.env
# Edit deploy/supabase/.env — set JWT_SECRET, POSTGRES_PASSWORD, keys
```

## 5. Start the Stack

### Option A: Simple (Postgres + App + Traefik)

```bash
# Create the network first
docker network create app_network

# Start the application stack
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Start Traefik
cd deploy/traefik
docker compose up -d
```

### Option B: Full Supabase (Postgres + Auth + Studio + App + Traefik)

```bash
# Start Supabase infrastructure
cd deploy/supabase
docker compose up -d

# Create app network
docker network create app_network

# Start the application (connect to Supabase's Postgres)
cd ~/sorting-hat
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Start Traefik
cd deploy/traefik
docker compose up -d
```

## 6. Verify SSL

```bash
# Check Traefik is running
docker compose -f deploy/traefik/docker-compose.yml logs

# Test HTTPS
curl -I https://2524.info

# Check certificate
echo | openssl s_client -connect 2524.info:443 2>/dev/null | openssl x509 -noout -subject -dates
```

## 7. Verify the Full Stack

```bash
# Check all containers are running
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps

# Check API health
curl https://2524.info/api/v1/health

# Check logs
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs api
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs web
```

## 8. Firewall (UFW)

Docker bypasses UFW by default. Since Traefik is the only service binding to host ports (80/443), and application containers don't publish ports in production, this is handled architecturally.

```bash
# Basic UFW setup
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

For additional Docker+UFW hardening, see: https://github.com/chaifeng/ufw-docker

## Updating

CI builds and pushes new Docker images to GHCR on every push to `main`. To update the VPS:

```bash
cd ~/sorting-hat
docker compose -f docker-compose.yml -f docker-compose.prod.yml pull
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Alembic migrations run automatically on API container startup.

## Troubleshooting

### Containers won't start
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs
```

### Database connection issues
```bash
# Check Postgres is healthy
docker compose ps db
docker compose logs db
```

### SSL certificate not provisioning
```bash
# Check Traefik logs for ACME errors
docker compose -f deploy/traefik/docker-compose.yml logs traefik
# Ensure DNS A record points to VPS IP
dig 2524.info
```
