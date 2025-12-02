#!/bin/sh
# Fix permissions for instance directory and database file
if [ -f /app/instance/restaurant.db ]; then
    chmod 666 /app/instance/restaurant.db 2>/dev/null || true
fi
chmod 777 /app/instance 2>/dev/null || true

# Execute the main command
exec "$@"
