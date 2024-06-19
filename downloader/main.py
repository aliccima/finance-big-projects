from urllib.parse import urlparse

import psycopg2
import yfinance as yf
from dotenv import dotenv_values
from psycopg2.extras import execute_values

RF = "^IRX"  # risk free rate
RM = "NQ=F"  # market return

TICKERS = [
    "AAPL",
    "AMZN",
    "GOOGL",
    "MSFT",
    "TSLA",
    "META",
    "NVDA",
    "NFLX",
    "V",
    "JNJ",
    RF,
    RM,
]


def update_tickers(cursor):
    for tk in TICKERS:
        if tk in [RF, RM]:
            cursor.execute(
                """
                SELECT id FROM ticker
                WHERE ticker.name = %s
                """,
                (tk,),
            )
        else:
            ticker = yf.Ticker(tk)
            beta = ticker.info["beta"]

            cursor.execute(
                """
                INSERT INTO ticker (name, beta)
                VALUES (%s, %s)
                ON CONFLICT (name)
                DO UPDATE SET beta=%s
                RETURNING id;
                """,
                (tk, beta, beta),
            )

        id = cursor.fetchone()[0]
        price = yf.download(tk, period="1d")["Adj Close"].item()
        cursor.execute(
            """
            INSERT INTO price (price, ticker_id)
            VALUES (%s, %s);
            """,
            (price, id),
        )


# Create entries for whole year
def populate_year(cursor):
    for tk in TICKERS:
        cursor.execute(
            """
            SELECT id FROM ticker
            WHERE ticker.name = %s
            """,
            (tk,),
        )
        id = cursor.fetchone()[0]
        prices = yf.download(tk, period="1y")["Adj Close"]
        prices = [(str(price[0].date()), price[1]) for price in prices.items()]
        execute_values(
            cursor,
            """
            INSERT INTO price (date, price, ticker_id)
            VALUES %s;
            """,
            prices,
            template=f"(%s, %s, {id})",
        )


def main():
    env_values = dotenv_values("/var/www/api/.env")
    url = urlparse(env_values["DB_URI"])

    with psycopg2.connect(
        user=url.username,
        password=url.password,
        database=url.path[1:],
        host=url.hostname,
        port=url.port,
    ) as conn:
        with conn.cursor() as cur:
            # Update betas and prices
            update_tickers(cur)
            # populate_year(cur)


if __name__ == "__main__":
    main()
