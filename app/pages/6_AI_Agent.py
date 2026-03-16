import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="AI Agent - GitHub Peru", page_icon="🤖", layout="wide")

st.title("Autonomous AI Agent")

st.info("The agent has autonomously processed 1,200 repositories using GPT-4o-mini and Function Calling.")

st.markdown("""
### Agent Architecture & Workflow
The **Classification Agent** operates as an autonomous entity that determines the industry focus of a software project.

#### 1. Decision Logic
- **Analyze Metadata**: The agent begins with the repo name, topics, and description.
- **Context Retrieval (Tool Usage)**: If the metadata is insufficient, it uses the `get_repo_readme` tool to fetch documentation.
- **Categorization**: Maps the project to one of the 21 CIIU industry categories.

#### 2. Agent Tools
- **`get_readme`**: Decodes and returns the repository's README.md file.
- **`get_languages`**: Fetches the detailed breakdown of code bytes per language.
- **`classify_industry`**: Evaluates all collected context to output a JSON classification.

#### 3. Agent Autonomy
Unlike a static script, the agent can loop its reasoning. It decides **if** and **when** it needs more data before committing to a classification, handling ambiguous projects (like "Utils" or "Base") with deep inspection.
""")

st.divider()

current_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(os.path.dirname(current_dir))
class_file = os.path.join(base_dir, "data", "processed", "classifications.csv")
if os.path.exists(class_file):
    c_df = pd.read_csv(class_file)
    st.subheader("Live Agent Reasoning Examples")
    sample = c_df.sample(3)
    for _, row in sample.iterrows():
        with st.expander(f"Repo: {row['repo_name']}"):
            st.write(f"**Industry:** {row['industry_name']} (Code: {row['industry_code']})")
            st.write(f"**Confidence:** {row['confidence'].upper()}")
            st.info(f"**Agent Reasoning:** {row['reasoning']}")
