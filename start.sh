#!/bin/bash
python server/app.py &
FLASK_PID=$!
sleep 2
NODE_ENV=development tsx server/index.ts
kill $FLASK_PID 2>/dev/null
