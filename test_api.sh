#!/bin/bash

# Start the server in the background
python3 main.py &
SERVER_PID=$!

# Wait for the server to start
sleep 3

# Make the API request
data='{"title":"Test Note","content":"Sample content for testing","user_id":"user123","folder_id":"folder123","source_type":"file"}'
curl -X POST "http://localhost:8001/process-note" -H "Content-Type: application/json" -d "$data"

# Kill the server process
kill $SERVER_PID 