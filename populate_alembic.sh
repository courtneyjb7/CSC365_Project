#!/bin/bash
echo "alembic downgrade base"
alembic downgrade base
echo "alembic upgrade head"
alembic upgrade head
echo "Populating tables..." 
py src/fake_data.py
