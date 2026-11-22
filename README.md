# RetailPulse — E-commerce Analytics Platform

**A personal data engineering and analytics project built with Python, DuckDB and Streamlit.**

## About the Project

I built RetailPulse to explore how raw e-commerce data can be transformed into meaningful business insights using data engineering and analytics tools.

The project takes customer, product, order and website activity data, processes it through a Python and DuckDB pipeline, and presents the results through an interactive Streamlit dashboard.

My main focus was to build a complete workflow — from generating raw data and processing it to analysing business metrics and presenting the results.

## What I Developed

I worked on the following components:

- **Data Generation:** Created a reproducible synthetic e-commerce dataset containing customers, products, orders, order items and website events.
- **Data Processing:** Built a Python pipeline using DuckDB to load, clean and transform the raw datasets.
- **Data Validation:** Added handling for duplicate records, invalid values and missing information.
- **Sales Analytics:** Calculated daily revenue, order counts, units sold and average order value.
- **Customer Analytics:** Generated customer-level purchase summaries and lifetime revenue.
- **Event Analytics:** Analysed product views, add-to-cart activities and purchase events.
- **Dashboard Development:** Built an interactive dashboard using Streamlit to present the analytics results.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Pipeline development |
| DuckDB | Data processing and analytical queries |
| Pandas | Data handling |
| Streamlit | Interactive dashboard |
| Docker | Containerisation |
| Git & GitHub | Version control |

## Project Results

I tested the pipeline using the generated sample dataset.

**Local execution results:**

| Metric | Result |
|---|---:|
| Processed orders | 1,363 |
| Total revenue | £1,010,607.49 |
| Average order value | £741.46 |
| Automated tests | 3/3 passed |

All three automated tests passed, covering order processing, output generation and revenue validation.

These figures are from the synthetic development dataset and are not real customer or business transactions.

## Dashboard

The Streamlit dashboard currently provides:

- Overall revenue and order metrics
- Average order value
- Daily revenue trends
- Customer-level summaries
- Event funnel analytics

## Running the Project Locally

Clone the repository:

```bash
git clone YOUR_REPOSITORY_URL
cd retailpulse
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Generate the sample dataset:

```bash
python src/generate_data.py
```

Run the analytics pipeline:

```bash
python src/pipeline.py
```

Run automated tests:

```bash
python -m unittest discover -s tests -v
```

Launch the dashboard:

```bash
streamlit run src/dashboard.py
```

## Project Structure

```text
retailpulse/
│
├── data/
│   ├── raw/
│   └── output/
│
├── src/
│   ├── generate_data.py
│   ├── pipeline.py
│   └── dashboard.py
│
├── tests/
│   └── test_pipeline.py
│
├── Dockerfile
├── requirements.txt
├── .gitignore
└── README.md
```

## Future Improvements

There are several areas I would like to explore next:

- Improve pipeline performance for larger datasets.
- Add more advanced customer segmentation.
- Introduce marketing channel attribution.
- Add more detailed product and category analytics.
- Implement automated data quality checks.
- Deploy the dashboard for public access.

## About My Work

I developed this project as part of my ongoing learning and practical work in data engineering, analytics and Python-based application development.

I am continuing to improve the pipeline, explore better data processing techniques and expand the analytical features.

**This project is a work in progress, and I plan to build on it further.**