# Quote Desk

A small web app for comparing supplier quotes against a request for quotation (RFQ).

When a part is needed, you raise an RFQ and collect quotes from several suppliers. Quote Desk shows every RFQ with a status and highlights the **best quote**: the cheapest quote that is still valid **and** can arrive before the "needed by" date.

Built with Python, Flask and SQLite.

## Features

- Create an RFQ: part number, description, quantity, needed-by date
- Add supplier quotes to an RFQ: supplier, unit price (INR), lead time (days), valid-until date
- List all RFQs with a status:
  - **Open**: no quotes yet
  - **Quoted**: at least one quote is still valid
  - **Expired**: the needed-by date has passed, or every quote is past its valid-until date
- Highlight the best quote per RFQ (shown on the list page and on the RFQ page)
- Data is saved in a SQLite file and survives restarts
- Automated tests for the best-quote and status logic

## How to run

Requires Python 3.10+.

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install flask pytest

# 3. Start the app
python app.py
```

Open http://127.0.0.1:5000 in your browser. The database file `quotedesk.db` is created automatically on first run.

## How to run the tests

```bash
pytest
```

## Project structure

```
quote-desk/
├── app.py            Flask routes (web layer)
├── db.py             SQLite access (storage layer)
├── logic.py          Business rules: validity, arrival, best quote, status
├── test_logic.py     Tests for logic.py
├── templates/
│   ├── base.html     Shared layout and styles
│   ├── index.html    RFQ list and "new RFQ" form
│   └── rfq.html      One RFQ: quotes table and "add quote" form
└── quotedesk.db      Created at runtime (not committed)
```

The rules in `logic.py` are plain functions with no web or database code, so they can be tested on their own and changed safely.

## Assumptions

The brief left some details open, so I made these choices:

1. **A quote is valid through its "valid until" date.** It is expired from the day after.
2. **We order today.** A quote arrives on `today + lead time`, and it is in time if that date is on or before "needed by". Arriving exactly on the needed-by date counts as in time.
3. **An RFQ past its needed-by date is Expired**, even if it has no quotes.
4. **Ties on price** go to the quote with the shorter lead time.
5. **An RFQ can be Quoted with no best quote**, for example when every valid quote would arrive late. The UI says "No quote can meet the date" instead of leaving it blank.
6. **All prices are in INR.** There is no currency field.
7. **"Today" is the server's current date.** In the code it is passed into the logic functions as a parameter, so tests are deterministic.

## Design decisions

- **SQLite:** one file, no server to install, persists across restarts, and still gives real tables, foreign keys and constraints. That is enough for a single-user tool. For many concurrent users I would move to PostgreSQL.
- **Status is computed, not stored.** Status depends on today's date, so a stored value would go stale when a quote expires overnight. Computing it on each request is always correct.
- **Money stored as integer paise.** Floats cannot represent some decimal values exactly; integers can. The conversion happens at the edges (on save and on load).
- **Dates stored as ISO text (`YYYY-MM-DD`)**, since SQLite has no date type and ISO strings sort correctly.
- **Parameterised SQL queries** (`?` placeholders) everywhere, to avoid SQL injection.
- **Database constraints** (`NOT NULL`, `CHECK`, foreign key with cascade delete) act as a second line of defence behind the form validation.
- **POST, then redirect** after form submissions, so refreshing the page does not resubmit the form.

## What I would do next with one more day

- Edit and delete for RFQs and quotes
- Tests for the Flask routes and the database layer, not just the logic
- Use `Decimal` (or integer paise) inside `logic.py` too; it currently compares float rupees, which is fine for 2-decimal prices but not ideal
- A visible label for *why* a quote is not the best (expired, arrives late, or costlier), instead of the combined note
- Show total cost (unit price × quantity) per quote
- Warn when adding a quote to an RFQ that is already expired
- Replace the development secret key with one from an environment variable, and add a deployed link
- Simple authentication if more than one person will use it

## What I left out, and why

- **Logins and users:** not requested, and not needed to show the core logic.
- **Multiple currencies:** the brief says to assume INR; adding conversion would add complexity without testing the main idea.
- **Editing and deleting:** not required; I chose to get the core rules correct and tested first.
- **A front-end framework:** plain server-rendered HTML is enough for this size and keeps the code easy to follow.
- **Database migrations:** the schema is created with `CREATE TABLE IF NOT EXISTS`. If the schema changes during development, delete `quotedesk.db` and restart.

## A note on AI use

I used AI assistance while building this, working through it step by step, and I reviewed each part so I can explain and modify it.
