#!/bin/bash
set -e
if [ ! -s seed.db ]; then python3 create_db.py; fi
cp seed.db state.db
echo "State reset to seed."
