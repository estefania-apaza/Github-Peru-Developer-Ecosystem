import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Developers - GitHub Peru", page_icon="👤", layout="wide")

def load_dev_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(current_dir))
    metrics_file = os.path.join(base_dir, "data", "metrics", "user_metrics.csv")
    return pd.read_csv(metrics_file)

df = load_dev_data()
st.title("Developer Explorer")

col1, col2, col3 = st.columns(3)
with col1:
    min_stars = st.slider("Minimum Total Stars", 0, 5000, 0)
with col2:
    langs = [str(l) for l in df["primary_language_1"].unique() if pd.notna(l)]
    lang_filter = st.multiselect("Filter by Language", options=langs)
with col3:
    active_only = st.checkbox("Show Active only")

filtered = df.copy()
if min_stars > 0:
    filtered = filtered[filtered["total_stars_received"] >= min_stars]
if lang_filter:
    filtered = filtered[filtered["primary_language_1"].isin(lang_filter)]
if active_only:
    filtered = filtered[filtered["is_active"] == True]

display_cols = [
    "login", "name", 
    "total_repos", "total_stars_received", "total_forks_received", "avg_stars_per_repo", "account_age_days", "repos_per_year",
    "followers", "following", "follower_ratio", "h_index", "impact_score",
    "primary_language_1", "language_diversity", "industries_served", "has_readme_pct", "has_license_pct",
    "total_open_issues", "days_since_last_push", "is_active", "contribution_consistency"
]
safe_cols = [c for c in display_cols if c in filtered.columns]

st.dataframe(filtered[safe_cols], use_container_width=True)

csv = filtered[safe_cols].to_csv(index=False).encode('utf-8')
st.download_button(label="📥 Download Results (CSV)", data=csv, file_name='peru_devs.csv', mime='text/csv')
