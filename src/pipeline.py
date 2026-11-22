
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "output"
OUT.mkdir(parents=True, exist_ok=True)


def run_pipeline():
    required = [
        "customers.csv", "products.csv", "orders.csv",
        "order_items.csv", "events.csv"
    ]

    missing = [f for f in required if not (RAW / f).exists()]
    if missing:
        raise FileNotFoundError("Missing files: " + ", ".join(missing))

    con = duckdb.connect(str(OUT / "retailpulse.duckdb"))

    try:
        for table, filename in [
            ("customers", "customers.csv"),
            ("products", "products.csv"),
            ("orders_raw", "orders.csv"),
            ("items_raw", "order_items.csv"),
            ("events_raw", "events.csv"),
        ]:
            path = (RAW / filename).as_posix().replace("'", "''")
            con.execute(
                f"CREATE OR REPLACE TABLE {table} AS "
                f"SELECT * FROM read_csv_auto('{path}', header=true)"
            )

        con.execute("""
            CREATE OR REPLACE TABLE valid_orders AS
            SELECT * EXCLUDE (rn)
            FROM (
                SELECT *,
                    row_number() OVER (
                        PARTITION BY order_id ORDER BY order_ts
                    ) AS rn
                FROM orders_raw
                WHERE order_id IS NOT NULL
                  AND customer_id IS NOT NULL
                  AND try_cast(order_ts AS TIMESTAMPTZ) IS NOT NULL
                  AND status = 'paid'
            )
            WHERE rn = 1
        """)

        con.execute("""
            CREATE OR REPLACE TABLE order_facts AS
            SELECT
                o.order_id,
                o.customer_id,
                CAST(o.order_ts AS TIMESTAMPTZ) AS order_ts,
                CAST(CAST(o.order_ts AS TIMESTAMPTZ) AS DATE) AS order_day,
                o.channel,
                SUM(
                    try_cast(i.quantity AS INTEGER) *
                    try_cast(i.unit_price AS DOUBLE)
                ) AS revenue,
                SUM(try_cast(i.quantity AS INTEGER)) AS units
            FROM valid_orders o
            JOIN items_raw i USING (order_id)
            JOIN products p USING (product_id)
            WHERE try_cast(i.quantity AS INTEGER) > 0
              AND try_cast(i.unit_price AS DOUBLE) >= 0
            GROUP BY ALL
        """)

        con.execute("""
            COPY (
                SELECT
                    order_day AS "day",
                    COUNT(DISTINCT order_id) AS orders,
                    ROUND(SUM(revenue), 2) AS revenue,
                    SUM(units) AS units_sold,
                    ROUND(
                        SUM(revenue) /
                        NULLIF(COUNT(DISTINCT order_id), 0), 2
                    ) AS average_order_value
                FROM order_facts
                GROUP BY order_day
                ORDER BY order_day
            )
            TO '""" + (OUT / "daily_sales.csv").as_posix() + """'
            (HEADER, DELIMITER ',')
        """)

        con.execute("""
            COPY (
                SELECT
                    c.customer_id,
                    c.country,
                    COUNT(DISTINCT f.order_id) AS orders,
                    ROUND(COALESCE(SUM(f.revenue), 0), 2)
                        AS lifetime_revenue,
                    CAST(MAX(f.order_ts) AS DATE) AS last_order_date
                FROM customers c
                LEFT JOIN order_facts f USING (customer_id)
                GROUP BY c.customer_id, c.country
                ORDER BY lifetime_revenue DESC
            )
            TO '""" + (OUT / "customer_summary.csv").as_posix() + """'
            (HEADER, DELIMITER ',')
        """)

        con.execute("""
            COPY (
                SELECT
                    event_type,
                    COUNT(*) AS event_count,
                    COUNT(DISTINCT customer_id) AS unique_customers
                FROM (
                    SELECT * EXCLUDE (rn)
                    FROM (
                        SELECT *,
                            row_number() OVER (
                                PARTITION BY event_id ORDER BY event_ts
                            ) AS rn
                        FROM events_raw
                        WHERE event_id IS NOT NULL
                          AND customer_id IS NOT NULL
                          AND try_cast(event_ts AS TIMESTAMPTZ) IS NOT NULL
                          AND event_type IN (
                              'product_view', 'add_to_cart', 'purchase'
                          )
                    )
                    WHERE rn = 1
                )
                GROUP BY event_type
                ORDER BY event_type
            )
            TO '""" + (OUT / "funnel_summary.csv").as_posix() + """'
            (HEADER, DELIMITER ',')
        """)

        count, revenue = con.execute("""
            SELECT COUNT(*), COALESCE(SUM(revenue), 0)
            FROM order_facts
        """).fetchone()

        return {
            "orders": count,
            "revenue": round(revenue, 2)
        }

    finally:
        con.close()


if __name__ == "__main__":
    print(run_pipeline())
