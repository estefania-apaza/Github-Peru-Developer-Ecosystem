import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Repositories - GitHub Peru", page_icon="📂", layout="wide")

def load_repo_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(current_dir))
    repos_file = os.path.join(base_dir, "data", "processed", "repositories.csv")
    class_file = os.path.join(base_dir, "data", "processed", "classifications.csv")
    
    r_df = pd.read_csv(repos_file)
    c_df = pd.read_csv(class_file)
    return r_df.merge(c_df[['repo_id', 'industry_name', 'confidence']], left_on='id', right_on='repo_id', how='left')

df = load_repo_data()
st.title("📂 Repository Browser")

query = st.text_input("Search (Name or Description)")
cols = ["name", "description", "language", "stargazers_count", "industry_name", "confidence"]

filtered = df.copy()
if query:
    filtered = filtered[filtered["name"].str.contains(query, case=False, na=False) | 
                        filtered["description"].str.contains(query, case=False, na=False)]

st.dataframe(filtered[cols], use_container_width=True)

st.subheader("Stars vs Forks Analysis")
fig = px.scatter(filtered, x="stargazers_count", y="forks_count", size="stargazers_count", 
                 color="language", hover_name="name", log_x=True, log_y=True)
st.plotly_chart(fig, use_container_width=True)
