#!/bin/zsh

ip_address=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null)

# Check if IP address was found
if [ -z "$ip_address" ]; then
  echo "No IP address found on en0 or en1."
  exit 1
else
  echo "IP Address: $ip_address"
fi

# Run Django server with the IP address
echo "Starting Django server on $ip_address:8000"
python manage.py runserver "$ip_address:8000" 