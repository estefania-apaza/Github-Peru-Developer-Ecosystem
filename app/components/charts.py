import plotly.express as px
import pandas as pd

def create_impact_bar_chart(df: pd.DataFrame):
    fig = px.bar(
        df, 
        x="impact_score", 
        y="login", 
        orientation='h',
        color="impact_score",
        color_continuous_scale="Viridis",
        template="plotly_white"
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    return fig

def create_industry_pie_chart(df: pd.DataFrame):
    fig = px.pie(
        df, 
        values="count", 
        names="industry", 
        hole=0.5,
        template="plotly_white"
    )
    return fig

def create_stars_forks_scatter(df: pd.DataFrame):
    fig = px.scatter(
        df, 
        x="stargazers_count", 
        y="forks_count", 
        size="stargazers_count", 
        color="language", 
        log_x=True, 
        log_y=True,
        template="plotly_white"
    )
    return fig