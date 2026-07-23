@echo off
cd /d d:\_Projects\math_agent\backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 > _run.log 2>&1
