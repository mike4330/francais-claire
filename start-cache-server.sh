#!/bin/bash

echo "🚀 Starting French Listening App Redis Cache Server..."
echo "📍 Port: 8080"
echo "📊 Redis: localhost:6379"
echo ""

# Check if Redis is running
if ! pgrep -x "redis-server" > /dev/null; then
    echo "⚠️  Redis server not running. Starting Redis..."
    sudo systemctl start redis-server
    sleep 2
fi

# Check Redis connection
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis server is running"
else
    echo "❌ Redis server not responding"
    exit 1
fi

echo "🔥 Starting WebSocket cache server..."
echo "📝 Logs will appear below..."
echo "🛑 Press Ctrl+C to stop"
echo ""

# Start the cache server
node redis-cache-server.js 