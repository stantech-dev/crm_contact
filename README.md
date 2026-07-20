# CRM (Dealbook CLI)

A simple command-line CRM for tracking leads — add, update, search, and export
contacts, built with Python and SQLite.

## Setup

Clone the repo and initialize the database (creates an empty `dealbook.db`
with the correct schema, no sample data included):

```bash
git clone https://github.com/stantech-dev/crm.git
cd crm
python init_db.py
```

## Usage

Run the CLI:

```bash
python crm.py
```

## Features

- Add new leads
- Update lead status
- Search leads by name or contact
- Export leads to CSV

## Notes

- `dealbook.db` and any exported `.csv` files are excluded from version
  control (see `.gitignore`) since they contain local/personal data.
- Run `init_db.py` once after cloning to create a fresh, empty database.
