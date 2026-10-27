@echo off
cd /d %~dp0backend
call venv_torch\Scripts\activate
set KMP_DUPLICATE_LIB_OK=TRUE
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
