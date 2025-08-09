# Project-Driver
## Quickstart

```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt

# create .env from example and update secrets
copy .env.example .env

# run
uvicorn app.main:app --reload

# try health (if you add it)
curl http://127.0.0.1:8000/ping
