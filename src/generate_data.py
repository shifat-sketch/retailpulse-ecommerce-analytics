from pathlib import Path
import csv, random
from datetime import datetime, timedelta, timezone

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)
random.seed(42)

def save(name, header, rows):
    with (RAW / name).open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)

def main():
    customers = [[f"C{i:04}", random.choice(["UK","US","DE","BD"]), (datetime(2025,1,1)+timedelta(days=random.randrange(300))).date().isoformat()] for i in range(1,301)]
    products = [[f"P{i:03}", random.choice(["Electronics","Home","Fashion","Sports"]), round(random.uniform(8,350),2)] for i in range(1,61)]
    save("customers.csv", ["customer_id","country","signup_date"], customers)
    save("products.csv", ["product_id","category","list_price"], products)
    start = datetime(2025,1,1,tzinfo=timezone.utc)
    orders, items = [], []
    for i in range(1,1801):
        customer = random.choice(customers)[0]
        ts = start + timedelta(days=random.randrange(300), minutes=random.randrange(1440))
        orders.append([f"O{i:05}",customer,ts.isoformat(),random.choice(["organic","paid_search","email","social","referral"]),random.choice(["paid","paid","paid","refunded"])])
        for _ in range(random.randint(1,4)):
            product = random.choice(products); qty = random.randint(1,3)
            items.append([f"O{i:05}",product[0],qty,round(float(product[2])*random.uniform(.85,1.05),2)])
    save("orders.csv",["order_id","customer_id","order_ts","channel","status"],orders)
    save("order_items.csv",["order_id","product_id","quantity","unit_price"],items)
    events=[]
    for i in range(1,9001):
        ts=start+timedelta(days=random.randrange(300),minutes=random.randrange(1440))
        events.append([f"E{i:06}",random.choice(customers)[0],ts.isoformat(),random.choices(["product_view","add_to_cart","purchase"],[.72,.20,.08])[0]])
    save("events.csv",["event_id","customer_id","event_ts","event_type"],events)
    print("Sample data generated:", RAW)

if __name__ == "__main__": main()
