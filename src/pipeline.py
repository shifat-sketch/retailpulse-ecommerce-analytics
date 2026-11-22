
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "output"
OUT.mkdir(parents=True, exist_ok=True)


def export_csv(con, query, filename):
    path = (OUT / filename).as_posix().replace("'", "''")
    con.execute(
        f"COPY ({query}) TO '{path}' (HEADER, DELIMITER ',')"
    )


def run_pipeline():
    required = [
        "customers.csv",
        "products.csv",
        "orders.csv",
        "order_items.csv",
        "events.csv"
    ]

    missing = [f for f in required if not (RAW / f).exists()]
    if missing:
        raise FileNotFoundError("Missing files: " + ", ".join(missing))

    con = duckdb.connect(str(OUT / "retailpulse.duckdb"))

    try:
        # Load raw datasets
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

        # Clean and deduplicate paid orders
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

        # Build order-level facts
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

        # 1. Daily sales
        export_csv(con, """
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
        """, "daily_sales.csv")

        # 2. Customer summary
        export_csv(con, """
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
        """, "customer_summary.csv")

        # 3. Event funnel
        export_csv(con, """
            WITH clean_events AS (
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
            ),
            view_count AS (
                SELECT COUNT(DISTINCT customer_id) AS viewers
                FROM clean_events
                WHERE event_type = 'product_view'
            )
            SELECT
                event_type,
                COUNT(*) AS event_count,
                COUNT(DISTINCT customer_id) AS unique_customers,
                ROUND(
                    100.0 * COUNT(DISTINCT customer_id) /
                    NULLIF((SELECT viewers FROM view_count), 0),
                    2
                ) AS customer_rate_from_viewers_pct
            FROM clean_events
            GROUP BY event_type
            ORDER BY CASE event_type
                WHEN 'product_view' THEN 1
                WHEN 'add_to_cart' THEN 2
                WHEN 'purchase' THEN 3
            END
        """, "funnel_summary.csv")

        # 4. Product performance
        export_csv(con, """
            SELECT
                p.product_id,
                p.category,
                COUNT(DISTINCT o.order_id) AS orders,
                SUM(try_cast(i.quantity AS INTEGER)) AS units_sold,
                ROUND(
                    SUM(
                        try_cast(i.quantity AS INTEGER) *
                        try_cast(i.unit_price AS DOUBLE)
                    ), 2
                ) AS revenue
            FROM valid_orders o
            JOIN items_raw i USING (order_id)
            JOIN products p USING (product_id)
            WHERE try_cast(i.quantity AS INTEGER) > 0
              AND try_cast(i.unit_price AS DOUBLE) >= 0
            GROUP BY p.product_id, p.category
            ORDER BY revenue DESC
        """, "product_summary.csv")

        # 5. Category performance
        export_csv(con, """
            SELECT
                p.category,
                COUNT(DISTINCT o.order_id) AS orders,
                SUM(try_cast(i.quantity AS INTEGER)) AS units_sold,
                ROUND(
                    SUM(
                        try_cast(i.quantity AS INTEGER) *
                        try_cast(i.unit_price AS DOUBLE)
                    ), 2
                ) AS revenue
            FROM valid_orders o
            JOIN items_raw i USING (order_id)
            JOIN products p USING (product_id)
            WHERE try_cast(i.quantity AS INTEGER) > 0
              AND try_cast(i.unit_price AS DOUBLE) >= 0
            GROUP BY p.category
            ORDER BY revenue DESC
        """, "category_summary.csv")

        # 6. Customer retention segments
        export_csv(con, """
            WITH customer_orders AS (
                SELECT
                    c.customer_id,
                    COUNT(DISTINCT f.order_id) AS order_count,
                    COALESCE(SUM(f.revenue), 0) AS revenue
                FROM customers c
                LEFT JOIN order_facts f USING (customer_id)
                GROUP BY c.customer_id
            ),
            segments AS (
                SELECT *,
                    CASE
                        WHEN order_count = 0 THEN 'No purchase'
                        WHEN order_count = 1 THEN 'One-time customer'
                        ELSE 'Repeat customer'
                    END AS customer_segment
                FROM customer_orders
            )
            SELECT
                customer_segment,
                COUNT(*) AS customer_count,
                SUM(order_count) AS total_orders,
                ROUND(SUM(revenue), 2) AS total_revenue,
                ROUND(AVG(order_count), 2) AS average_orders_per_customer
            FROM segments
            GROUP BY customer_segment
            ORDER BY customer_segment
        """, "retention_summary.csv")

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
