import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json

st.set_page_config(page_title="Industries - GitHub Peru", page_icon="🏭", layout="wide")

def load_ind_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(current_dir))
    
    eco_file = os.path.join(base_dir, "data", "metrics", "ecosystem_metrics.json")
    repos_file = os.path.join(base_dir, "data", "processed", "repositories.csv")
    class_file = os.path.join(base_dir, "data", "processed", "classifications.csv")
    
    with open(eco_file, 'r') as f:
        eco = json.load(f)
    
    r_df = pd.read_csv(repos_file)
    c_df = pd.read_csv(class_file)
    merged = r_df.merge(c_df[['repo_id', 'industry_name']], left_on='id', right_on='repo_id', how='left')
    
    return eco, merged

eco, merged_df = load_ind_data()

st.title("Industry Analysis")
st.markdown("### Structural Distribution & Technical Specialization")

ind_dist = pd.DataFrame(eco["industry_distribution"])

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("Industry Volume")
    fig = px.bar(
        ind_dist, 
        x="count", 
        y="industry", 
        orientation='h',
        color="count", 
        color_continuous_scale="Blues",
        template="plotly_white"
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Distribution Breakdown")
    fig = px.pie(
        ind_dist, 
        values="count", 
        names="industry", 
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Tealgrn,
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Industry-Language Correlation Heatmap")
st.markdown("Analysis of technological preference across different economic sectors.")

# Prepare heatmap data
top_inds = ind_dist.nlargest(8, "count")["industry"].tolist()
top_langs = merged_df["language"].value_counts().nlargest(10).index.tolist()

heatmap_df = merged_df[
    (merged_df["industry_name"].isin(top_inds)) & 
    (merged_df["language"].isin(top_langs))
]
heatmap_pivot = heatmap_df.pivot_table(
    index='industry_name', 
    columns='language', 
    values='id', 
    aggfunc='count', 
    fill_value=0
)

fig_heat = px.imshow(
    heatmap_pivot,
    labels=dict(x="Programming Language", y="Industry", color="Repo Count"),
    x=heatmap_pivot.columns,
    y=heatmap_pivot.index,
    color_continuous_scale="Viridis",
    aspect="auto",
    template="plotly_white",
    text_auto=True
)
st.plotly_chart(fig_heat, use_container_width=True)
