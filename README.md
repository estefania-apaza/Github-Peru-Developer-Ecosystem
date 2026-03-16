# 🇵🇪 GitHub Peru Analytics: Developer Ecosystem Dashboard

> Analyzing the Peruvian developer landscape through data engineering and AI.

### 🐣 The Antigravity Easter Egg
Before anything else, we follow the Python tradition:
![Antigravity Screenshot](demo/antigravity_screenshot.png)

## 🚀 Key Findings
Based on the analysis of **503 Peruvian developers** and **1,200 repositories**:
1. **Language Landscape**: **JavaScript** remains the king of the ecosystem (16.4%), with **TypeScript** (15.5%) showing rapid professional adoption.
2. **Industry Dominance**: As expected, **Information and Communication** (58%) is the primary industry, but **Education** (12.6%) and **Arts/Recreation** (8%) show significant open-source contributions.
3. **Maturity**: The average Peruvian developer account in this dataset is **9 years old** (~3,284 days), indicating a deeply experienced core community.
4. **Community Value**: The ecosystem has amassed over **68,000 stars**, reflecting high external recognition for local projects.
5. **Impact Hub**: Lima dominates the geographic distribution, acting as the primary hub for the country's technical innovation.

## 📊 Data Collection
- **Sample Size**: 503 Users, 1,200 Repositories.
- **Source**: GitHub Search API (Location: Peru, Lima, Arequipa, etc.).
- **Rate Limiting**: Implemented using `tenacity` with exponential backoff and `GitHubClient` to monitor `X-RateLimit-Remaining` headers.
- **Full Context**: READMEs were extracted for all 1,200 repositories to nourish the AI Classification Agent.

## ✨ Dashboard Features
1. **Main Dashboard**: Real-time ecosystem KPIs (Total Devs, Repos, Stars) and Growth Timeline.
2. **Developer Explorer**: Filterable table with 20+ metrics (h-index, impact score, consistency) and CSV Export.
3. **Repository Browser**: Industry-specific filtering and "Stars vs Forks" correlation analysis.
4. **Industry Analytics**: Deep dive into CIIU categorization and language distribution per sector.
5. **Language Analytics**: Heatmaps correlating technical stacks with industry focus.
6. **AI Agent Transparency**: Details on how the autonomous categorization was performed.

## ⚙️ Installation & Usage
1. **Clone & Setup**:
   ```bash
   git clone <repo-url>
   pip install -r requirements.txt
   ```
2. **Configuration**: Create a `.env` file from the example:
   ```env
   GITHUB_TOKEN=your_token
   OPENAI_API_KEY=your_key
   ```
3. **Run Pipeline**:
   ```bash
   python scripts/extract_data.py
   python scripts/classify_repos.py
   python scripts/calculate_metrics.py
   ```
4. **Launch Application**:
   ```bash
   streamlit run app/main.py
   ```

## 🧠 AI Agent Documentation
We implemented a **Classification Agent** using OpenAI's Function Calling (`gpt-4o-mini`).
- **Autonomy**: The agent decides whether it needs more context (README) before finalizing a classification.
- **Tools**: `get_readme`, `get_languages`, `classify_industry`.
- **Reasoning**: Every classification includes a `reasoning` field documenting the agent's logic.

## ⚠️ Limitations
1. **Location Bias**: Only users with explicit location "Peru" or major cities in their profile were captured.
2. **Stars Threshold**: Data collection favors historically popular repositories, potentially missing emerging trends.
3. **Classification Accuracy**: While GPT-4 is highly accurate, some generic libraries ("Utils", "Template") may default to Information/Communication industry.

## 👤 Author Information
- **Name**: [Your Name]
- **Course**: Prompt Engineering - Assignment 2
- **Date**: March 2026
- **Video Link**: [Found in demo/video_link.md](demo/video_link.md)
