#!/usr/bin/env python3
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__) or '.')

from server.app import app

if __name__ == "__main__":
    print("Starting VideoSplit Flask server on port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
