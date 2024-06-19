from dotenv import dotenv_values
from flask import Flask, jsonify, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.sql import func

db = SQLAlchemy()
admin = Admin(url="/")


class Ticker(db.Model):
    __tablename__ = "ticker"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    beta = db.Column(db.Float)

    def __repr__(self) -> str:
        return self.name


class Price(db.Model):
    __tablename__ = "price"
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, server_default=func.now())
    ticker_id = db.Column(db.Integer, db.ForeignKey("ticker.id"), nullable=False)
    ticker = db.relationship("Ticker", backref="price")

    def __repr__(self) -> str:
        return self.date


class ReadOnlyView(ModelView):
    can_create = False
    can_delete = False
    can_edit = False


class PriceView(ReadOnlyView):
    form_columns = ["price", "ticker"]
    column_list = ("ticker", "price", "date")


# Add admin views
admin.add_view(ReadOnlyView(Ticker, db.session))
admin.add_view(PriceView(Price, db.session))

# Create Flask app
app = Flask(__name__)
env_values = dotenv_values("/var/www/api/.env")
app.config["SQLALCHEMY_DATABASE_URI"] = env_values["DB_URI"]
app.config["SECRET_KEY"] = env_values["DB_SECRET"]

db.init_app(app)
admin.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()


# Define routes


@app.route("/api/prices", methods=["POST"])
def get_prices():
    req = request.get_json()
    if "ticker" not in req:
        return "Missing 'ticker' field in the request", 400

    if "limit" in req:
        limit = req["limit"]
    else:
        limit = 1

    with db.engine.connect() as con:
        result = con.execute(
            text(
                """
                SELECT price FROM price
                JOIN ticker ON price.ticker_id = ticker.id
                WHERE ticker.name = :ticker
                ORDER BY price.date DESC
                LIMIT :limit;
                """
            ),
            {"ticker": req["ticker"], "limit": limit},
        )
    return jsonify({"prices": [r.price for r in result]})


@app.route("/api/beta", methods=["POST"])
def get_beta():
    req = request.get_json()
    if "ticker" not in req:
        return "Missing 'ticker' field in the request", 400

    with db.engine.connect() as con:
        result = con.execute(
            text(
                """
                SELECT beta FROM ticker
                WHERE name = :ticker;
                """
            ),
            {"ticker": req["ticker"]},
        )
    return jsonify({"beta": next(result).beta})
