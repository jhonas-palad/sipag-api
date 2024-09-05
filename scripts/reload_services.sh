#!/bin/bash

# Reload supervisor
echo "Reloading Supervisor..."
sudo supervisorctl reload

# Reload NGINX
echo "Reloading NGINX..."
sudo systemctl reload nginx

echo "Services have been reloaded successfully."
