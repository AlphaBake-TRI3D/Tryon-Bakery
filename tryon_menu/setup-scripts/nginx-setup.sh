#!/bin/bash

# Prompt for server name
SERVER_NAME="${1}"

# Install Nginx
sudo apt install nginx -y

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Prepare the Nginx server block configuration
CONFIG="map \$http_upgrade \$connection_upgrade {
    default upgrade;
    '' close;
}

server {
    listen 80;
    server_name ${SERVER_NAME};

    # Configuration for the main application
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection \$connection_upgrade;
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        client_max_body_size 100M;
    }

    # Configuration for the /extract_embeddings endpoint
    location /training {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_read_timeout 3000s;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection \$connection_upgrade;
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        client_max_body_size 100M;
    }
}"

# Write the configuration to the Nginx available sites
echo "$CONFIG" | sudo tee /etc/nginx/sites-available/myapp

# Enable the new site
sudo ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/

# Restart Nginx to apply changes
sudo systemctl restart nginx

echo "Nginx has been configured and restarted."