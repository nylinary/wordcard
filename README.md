# For renewals (add to cron):
docker compose run --rm certbot renew

# For renewals (add to cron):
docker compose run --rm certbot renew
docker compose restart frontend-proxy

# To apply new volumes
docker compose up -d --force-recreate frontend-proxy