#!/usr/bin/env python3
"""
Script to initialize the PostgreSQL database tables.
Run this once before starting the application.
"""

from database import init_db

if __name__ == "__main__":
    print("Initializing database tables...")
    success = init_db()
    if success:
        print("All tables created successfully!")
    else:
        print("Failed to initialize database. Check your DATABASE_URL.")
