import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json

st.set_page_config(page_title="GitHub Peru Analytics", page_icon="🇵🇪", layout="wide")

# Custom CSS for premium look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_all_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(current_dir)
    processed_dir = os.path.join(base_dir, "data", "processed")
    metrics_dir = os.path.join(base_dir, "data", "metrics")
    
    users_df = pd.read_csv(os.path.join(processed_dir, "users.csv"))
    repos_df = pd.read_csv(os.path.join(processed_dir, "repositories.csv"))
    class_df = pd.read_csv(os.path.join(processed_dir, "classifications.csv"))
    user_metrics_df = pd.read_csv(os.path.join(metrics_dir, "user_metrics.csv"))
    
    with open(os.path.join(metrics_dir, "ecosystem_metrics.json"), 'r') as f:
        eco_metrics = json.load(f)
            
    return users_df, repos_df, class_df, user_metrics_df, eco_metrics

users_df, repos_df, classifications_df, user_metrics_df, eco_metrics = load_all_data()

st.title("Peru Developer Ecosystem")
st.markdown("""
### Strategic Overview & Performance Insights
Welcome to the **GitHub Peru Analytics** dashboard. This application provides a comprehensive analysis of the 
software development landscape in Peru, utilizing data extracted from the GitHub API and processed through 
AI-driven industrial classification (GPT-4) and advanced technical metrics.
""")

if eco_metrics:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Developers", f"{eco_metrics.get('total_developers', 0):,}")
    with col2:
        st.metric("Total Repositories", f"{eco_metrics.get('total_repositories', 0):,}")
    with col3:
        st.metric("Total Stars", f"{eco_metrics.get('total_stars', 0):,}")
    with col4:
        active_pct = eco_metrics.get("active_developer_pct", 0)
        st.metric("Active Developers", f"{active_pct:.1f}%")
    
    colA, colB = st.columns(2)
    with colA:
        st.metric("Avg Repos per User", f"{eco_metrics.get('avg_repos_per_user', 0):.2f}")
    with colB:
        st.metric("Avg Account Age", f"{eco_metrics.get('avg_account_age_days', 0):.0f} Days")

st.divider()

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Developer Impact Ranking")
    top_devs = user_metrics_df.nlargest(10, "impact_score")[["login", "impact_score", "primary_language_1"]]
    fig = px.bar(
        top_devs, 
        x="impact_score", 
        y="login", 
        orientation='h',
        color="impact_score",
        color_continuous_scale="Viridis",
        text="primary_language_1",
        template="plotly_white"
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Industry Landscape")
    ind_dist = pd.DataFrame(eco_metrics["industry_distribution"])
    fig = px.pie(
        ind_dist, 
        values="count", 
        names="industry", 
        hole=0.5,
        color_discrete_sequence=px.colors.sequential.RdBu,
        template="plotly_white"
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

st.divider()

col3, col4 = st.columns(2)

with col3:
    st.subheader("Most Starred Repositories")
    top_repos = repos_df.nlargest(10, "stargazers_count")[["name", "stargazers_count", "language"]]
    fig_repos = px.bar(
        top_repos, 
        x="stargazers_count", 
        y="name", 
        orientation='h', 
        color="stargazers_count",
        color_continuous_scale="Plotly3",
        template="plotly_white"
    )
    fig_repos.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_repos, use_container_width=True)

with col4:
    st.subheader("Ecosystem Growth Profile")
    user_metrics_df['join_year'] = 2024 - (user_metrics_df['account_age_days'] / 365)
    growth_df = user_metrics_df.groupby(user_metrics_df['join_year'].astype(int)).size().reset_index(name='count')
    fig_growth = px.area(
        growth_df, 
        x="join_year", 
        y="count", 
        markers=True, 
        color_discrete_sequence=['#ff4b4b'],
        template="plotly_white"
    )
    st.plotly_chart(fig_growth, use_container_width=True)
