FROM nginx:alpine

# Install certbot
RUN apk add --no-cache certbot certbot-nginx

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create directories for certbot
RUN mkdir -p /var/www/certbot /var/www/static

# Copy entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
