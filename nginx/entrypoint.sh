#!/bin/sh
set -e

# Function to obtain SSL certificate
obtain_ssl_cert() {
    echo "Obtaining SSL certificate for $DOMAIN..."
    
    certbot certonly --webroot \
        --webroot-path=/var/www/certbot \
        --email "$ADMIN_EMAIL" \
        --agree-tos \
        --no-eff-email \
        -d "$DOMAIN"
    
    echo "SSL certificate obtained successfully!"
}

# Function to renew SSL certificates
renew_ssl_certs() {
    echo "Renewing SSL certificates..."
    certbot renew --quiet
    nginx -s reload
}

# Check if certificate exists
DOMAIN="${DOMAIN:-disipl.uz}"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@disipl.uz}"

if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    obtain_ssl_cert
fi

# Start nginx
nginx -g 'daemon off;'

# Schedule certificate renewal (every 12 hours)
while true; do
    sleep 43200
    renew_ssl_certs
done &
