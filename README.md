This is a final project repo for QMSS-G5063-2026 (Data Visualization, Spring 2026) 
Group member: Xiang Fan (xf2300), Zhicheng Jiang (zj2433), Jiahao Huang (jh5140), Yehua Huang (yh3932)

# YC at 20: Three Waves Before AI

An interactive data visualization exploring how AI compares to past Y Combinator investment waves
(Enterprise SaaS, Fintech, Developer Tools) across scale, penetration, and geography.

## Live Demo

> Add the Streamlit Community Cloud URL here after deployment.

## Run Locally

Prerequisites: Anaconda or Miniconda with a Python 3.10+ environment.

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd group-project

# 2. Activate your environment and install dependencies
conda activate hw
pip install -r requirements.txt

# 3. Generate the cleaned dataset (one-time step)
python prep_data.py

# 4. Launch the app
streamlit run app.py
```

The app opens at http://localhost:8501.

## Data

Source: YC Companies dataset by DataHive AI on HuggingFace
https://huggingface.co/datasets/datahiveai/ycombinator-companies

- 5,080 companies, Y Combinator batches 2011-2025
- Fields used: batch, tags, city, country, industry
- Raw CSV: data/yc-companies.csv (included in repo, 9.4 MB)
- Cleaned parquet: data/companies_clean.parquet (generated locally by prep_data.py, not tracked in git)

## Project Structure

```
group-project/
|-- app.py                    # Main entry point (single-page scroll)
|-- utils.py                  # Shared data, colors, CSS, aggregation functions
|-- prep_data.py              # CSV -> Parquet cleaning pipeline
|-- pages_internal/
|   |-- tab_scale.py          # Section 01: Scale analysis
|   |-- tab_penetration.py    # Section 02: Penetration analysis
|   |-- tab_geography.py      # Section 03: Geography analysis
|   +-- page3_answer.py       # Conclusion + methodology
|-- data/
|   +-- yc-companies.csv      # Raw data
|-- .streamlit/
|   +-- config.toml           # Theme configuration
+-- requirements.txt
```

## Dependencies

See requirements.txt. Key packages: streamlit, pandas, plotly, networkx, folium.
