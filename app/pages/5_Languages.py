import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json

st.set_page_config(page_title="Languages - GitHub Peru", page_icon="💻", layout="wide")

def load_lang_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(current_dir))
    eco_file = os.path.join(base_dir, "data", "metrics", "ecosystem_metrics.json")
    user_file = os.path.join(base_dir, "data", "metrics", "user_metrics.csv")
    with open(eco_file, 'r') as f:
        eco = json.load(f)
    users = pd.read_csv(user_file)
    return eco, users

eco, users = load_lang_data()
st.title("Technical Stack Analytics")
st.markdown("### Language Popularity & Developer Expertise")

lang_dist = pd.DataFrame(eco["most_popular_languages"])

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("Dominant Programming Languages")
    fig = px.bar(
        lang_dist, 
        x="count", 
        y="language", 
        orientation='h',
        color="count", 
        color_continuous_scale="Plasma",
        template="plotly_white",
        text_auto=True
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Language Market Share")
    fig_pie = px.pie(
        lang_dist, 
        values="count", 
        names="language", 
        template="plotly_white",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig_pie, use_container_width=True)

st.divider()

st.subheader("Leading Developers by Technical Stack")
sel_lang = st.selectbox("Filter Expertise by Language", options=lang_dist["language"].tolist())
top_devs = users[users["primary_language_1"] == sel_lang].nlargest(10, "impact_score")

if not top_devs.empty:
    st.table(top_devs[["login", "name", "total_stars_received", "impact_score"]])
else:
    st.info(f"Not enough data to rank developers for {sel_lang} yet.")
