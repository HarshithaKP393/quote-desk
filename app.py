from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash, abort

import db
from logic import best_quote, rfq_status

app = Flask(__name__)
app.secret_key = "dev-only-change-me"   # needed for flash messages
db.init_db()


@app.route("/")
def index():
    today = date.today()
    rows = []
    for r in db.list_rfqs():
        needed_by = date.fromisoformat(r["needed_by"])
        quotes = db.get_quotes(r["id"])
        rows.append({
            "rfq": r,
            "needed_by": needed_by,
            "n_quotes": len(quotes),
            "status": rfq_status(quotes, needed_by, today),
            "best": best_quote(quotes, needed_by, today),
        })
    return render_template("index.html", rows=rows)


@app.route("/rfqs", methods=["POST"])
def create_rfq():
    try:
        part_number = request.form["part_number"].strip()
        description = request.form["description"].strip()
        quantity = int(request.form["quantity"])
        needed_by = date.fromisoformat(request.form["needed_by"])
        if not part_number or not description or quantity <= 0:
            raise ValueError
    except (ValueError, KeyError):
        flash("Please fill all RFQ fields correctly (quantity must be > 0).")
        return redirect(url_for("index"))
    rid = db.create_rfq(part_number, description, quantity, needed_by)
    return redirect(url_for("rfq_detail", rfq_id=rid))


@app.route("/rfqs/<int:rfq_id>")
def rfq_detail(rfq_id):
    rfq = db.get_rfq(rfq_id)
    if rfq is None:
        abort(404)
    today = date.today()
    needed_by = date.fromisoformat(rfq["needed_by"])
    quotes = db.get_quotes(rfq_id)
    best = best_quote(quotes, needed_by, today)
    return render_template(
        "rfq.html", rfq=rfq, needed_by=needed_by, quotes=quotes, best=best,
        status=rfq_status(quotes, needed_by, today), today=today,
    )


@app.route("/rfqs/<int:rfq_id>/quotes", methods=["POST"])
def add_quote(rfq_id):
    if db.get_rfq(rfq_id) is None:
        abort(404)
    try:
        supplier = request.form["supplier"].strip()
        price = float(request.form["unit_price"])
        lead = int(request.form["lead_time_days"])
        valid_until = date.fromisoformat(request.form["valid_until"])
        if not supplier or price < 0 or lead < 0:
            raise ValueError
    except (ValueError, KeyError):
        flash("Please fill all quote fields correctly.")
        return redirect(url_for("rfq_detail", rfq_id=rfq_id))
    db.add_quote(rfq_id, supplier, price, lead, valid_until)
    return redirect(url_for("rfq_detail", rfq_id=rfq_id))


if __name__ == "__main__":
    app.run(debug=True)