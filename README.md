# RetailPulse — E-commerce Analytics Project

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?logo=streamlit)](https://retailpulse-ecommerce-analytics-fdwhk7xqcqt4xc2y29zee4.streamlit.app/)

**Live Dashboard:** [Explore RetailPulse](https://retailpulse-ecommerce-analytics-fdwhk7xqcqt4xc2y29zee4.streamlit.app/)

## Why I Started This Project

I wanted to challenge myself by building a practical data analytics project from scratch rather than just following tutorials or working with isolated examples.

I started exploring how e-commerce businesses collect data, how that data can be processed, and how useful business insights can be generated from it.

That idea led me to build **RetailPulse**, a small end-to-end e-commerce analytics platform where I could experiment with Python, SQL, DuckDB, Pandas and Streamlit.

This project is part of my journey to strengthen my practical skills in data analytics, data engineering and business intelligence.

## What I Tried to Build

My goal was to create a simple but functional analytics workflow:

- Generate sample e-commerce data for customers, products, orders and customer activities.
- Process and analyse the data using Python and DuckDB.
- Calculate revenue, order performance and customer-level summaries.
- Explore customer activity through an event funnel.
- Present the results in an interactive dashboard using Streamlit.

I wanted to understand how all these individual components could work together in a real-world-style project.

## Technologies I Used

While building this project, I worked with:

- **Python** — data generation and processing.
- **Pandas** — data manipulation and analysis.
- **DuckDB** — SQL-based analytical queries.
- **Streamlit** — interactive dashboard development.
- **Git & GitHub** — version control and project management.

## A Look at the Results

After generating the sample data and running the pipeline, the dashboard currently displays:

| Metric | Result |
|---|---:|
| Total Revenue | £1,010,607.49 |
| Total Orders | 1,363 |
| Average Order Value | £741.46 |

*These figures are based on synthetic data generated for this project, not actual commercial transactions.*

The dashboard also includes daily revenue trends, top customer summaries and an event funnel.

## How I Structured the Project

```text
retailpulse/
├── data/
│   ├── raw/
│   └── output/
├── src/
│   ├── generate_data.py
│   ├── pipeline.py
│   └── dashboard.py
├── tests/
│   └── test_pipeline.py
├── requirements.txt
├── Dockerfile
└── README.md
```

I separated the data generation, processing and dashboard components so that each part has its own responsibility.

## Running the Project Locally

If you want to explore the project on your own machine:

**1. Clone the repository**

```bash
git clone https://github.com/shifat-sketch/retailpulse-ecommerce-analytics.git
cd retailpulse-ecommerce-analytics
```

**2. Install the dependencies**

```bash
pip install -r requirements.txt
```

**3. Generate the sample data**

```bash
python src/generate_data.py
```

**4. Run the data pipeline**

```bash
python src/pipeline.py
```

**5. Start the dashboard**

```bash
streamlit run src/dashboard.py
```

You can then open `http://localhost:8501` in your browser.

## Testing

I also added basic automated tests to check whether the pipeline generates the expected output files and produces valid results.

Run the tests using:

```bash
python -m unittest discover -s tests -v
```

## What's Next?

This is an ongoing learning project, and there are several things I would like to explore next:

- Product and category performance analysis.
- Monthly and seasonal revenue trends.
- Customer retention and repeat purchase analysis.
- Conversion rate and funnel optimisation.
- More interactive dashboard filters.
- Improved data quality checks and testing.

I plan to keep improving the project as I learn more and experiment with additional analytics techniques.

## A Little About Me

I'm Shifat Ahamed, with a background in Computer Science and an interest in Artificial Intelligence, Machine Learning and Data Analytics.

I enjoy learning by building things, experimenting with technologies and turning ideas into practical projects.

If you have any suggestions or feedback, I'd genuinely appreciate it.

**GitHub Repository:** [RetailPulse on GitHub](https://github.com/shifat-sketch/retailpulse-ecommerce-analytics)

**Live Demo:** [Try the RetailPulse Dashboard](https://retailpulse-ecommerce-analytics-fdwhk7xqcqt4xc2y29zee4.streamlit.app/)
