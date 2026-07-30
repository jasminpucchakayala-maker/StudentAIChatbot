import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import config

def format_response_time(seconds: float) -> str:
    """Format decimal seconds into millisecond reading or seconds."""
    if seconds < 1.0:
        return f"{int(seconds * 1000)} ms"
    return f"{seconds:.2f} s"

def calculate_analytics_metrics(df: pd.DataFrame) -> dict:
    """
    Extract aggregate KPI indicators from the history DataFrame.
    """
    metrics = {
        "total_questions": 0,
        "questions_today": 0,
        "total_sessions": 0,
        "avg_confidence": 0.0,
        "avg_response_time": 0.0,
        "most_common_category": "None",
        "unknown_percentage": 0.0
    }
    
    if df.empty:
        return metrics
        
    metrics["total_questions"] = len(df)
    metrics["total_sessions"] = df["SessionID"].nunique()
    
    # Calculate questions asked today
    today_str = date.today().isoformat()
    questions_today_df = df[df["Timestamp"].dt.date == date.today()]
    metrics["questions_today"] = len(questions_today_df)
    
    # Averages
    metrics["avg_confidence"] = float(df["Confidence"].mean())
    metrics["avg_response_time"] = float(df["ResponseTimeSec"].mean())
    
    # Most common topic category (excluding standard greetings/conversations if possible)
    academic_df = df[~df["IntentMatched"].isin(["greeting", "goodbye", "thanks", "identity", "help"])]
    if not academic_df.empty:
        metrics["most_common_category"] = str(academic_df["IntentMatched"].mode().iloc[0]).capitalize()
    elif not df["IntentMatched"].empty:
        metrics["most_common_category"] = str(df["IntentMatched"].mode().iloc[0]).capitalize()
        
    # Unknown queries rate
    unknowns = len(df[df["IntentMatched"] == "unknown"])
    metrics["unknown_percentage"] = float((unknowns / len(df)) * 100.0)
    
    return metrics

def generate_intent_bar_chart(df: pd.DataFrame):
    """Generate a Plotly bar chart indicating most queried category tags."""
    if df.empty:
        return None
        
    # Exclude standard chat filler tags to focus on college topics
    academic_df = df[~df["IntentMatched"].isin(["greeting", "goodbye", "thanks", "identity"])]
    if academic_df.empty:
        academic_df = df
        
    category_counts = academic_df["IntentMatched"].value_counts().reset_index()
    category_counts.columns = ["Category", "Count"]
    
    # Sort for plot
    category_counts = category_counts.sort_values(by="Count", ascending=True)
    
    fig = px.bar(
        category_counts,
        y="Category",
        x="Count",
        orientation='h',
        title="Queries by Topic Category",
        labels={"Count": "Number of Questions", "Category": "Category"},
        color="Count",
        color_continuous_scale="Blues"
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="#ADB5BD",
        title_font_size=16,
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.08)'),
        yaxis=dict(showgrid=False),
        margin=dict(l=20, r=20, t=40, b=20),
        coloraxis_showscale=False,
        height=320
    )
    return fig

def generate_confidence_pie_chart(df: pd.DataFrame):
    """Generate circular Plotly pie chart splitting queries by match confidence tiers."""
    if df.empty:
        return None
        
    def get_tier(conf):
        if conf >= config.MATCH_THRESHOLD:
            return "High Confidence (>= 55%)"
        elif conf >= config.SUGGESTION_THRESHOLD:
            return "Medium Confidence (35-55%)"
        else:
            return "Low Confidence (< 35%)"
            
    df_tiers = df.copy()
    df_tiers["ConfidenceTier"] = df_tiers["Confidence"].apply(get_tier)
    tier_counts = df_tiers["ConfidenceTier"].value_counts().reset_index()
    tier_counts.columns = ["Status", "Count"]
    
    colors = {
        "High Confidence (>= 55%)": "#0EA5E9",
        "Medium Confidence (35-55%)": "#F59E0B",
        "Low Confidence (< 35%)": "#EF4444"
    }
    
    fig = px.pie(
        tier_counts,
        names="Status",
        values="Count",
        title="Intent Recognition Accuracy Distribution",
        color="Status",
        color_discrete_map=colors,
        hole=0.4
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="#ADB5BD",
        title_font_size=16,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        height=320
    )
    return fig

def generate_response_time_line_chart(df: pd.DataFrame):
    """Generate line chart demonstrating average response speed over time."""
    if df.empty:
        return None
        
    df_time = df.copy()
    # Group by minute/hour depending on counts
    df_time = df_time.sort_values(by="Timestamp")
    df_time["Time_Bucket"] = df_time["Timestamp"].dt.strftime("%H:%M")
    
    trend_df = df_time.groupby("Time_Bucket")["ResponseTimeSec"].mean().reset_index()
    trend_df.columns = ["Time", "AvgResponseSec"]
    
    fig = px.line(
        trend_df,
        x="Time",
        y="AvgResponseSec",
        title="Average System Response Time Trend",
        labels={"AvgResponseSec": "Time (seconds)", "Time": "Time of Day (HH:MM)"},
        markers=True
    )
    
    fig.update_traces(line_color="#06B6D4", marker=dict(size=8, color="#0891B2"))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="#ADB5BD",
        title_font_size=16,
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.08)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.08)'),
        margin=dict(l=20, r=20, t=40, b=20),
        height=320
    )
    return fig
