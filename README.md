# Hospital Management System

Staff profile registration and authentication for receptionists and doctors.
Receptionists can also save patient entries with name, age, contact number,
address, and appointment reason for future appointment workflows.

## Local setup

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
uvicorn hospital_management.main:app --reload
```

Open `http://127.0.0.1:8000`. SQLite data is stored in
`hospital_management.db` by default. Set `DATABASE_URL` to use another
SQLAlchemy-compatible database.

## Current workflows

- `POST /api/profiles` creates receptionist and doctor profiles.
- `POST /api/auth/login` authenticates saved staff profiles.
- `POST /api/patients` saves patient entries captured at reception.

## Tests

```powershell
pytest
```
