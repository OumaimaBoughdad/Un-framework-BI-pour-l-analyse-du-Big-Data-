import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import glob
import os

st.set_page_config(page_title="Scientific Articles Analysis", layout="wide", page_icon="📊")

# Custom CSS
st.markdown("""
<style>
    .main {background-color: #f5f7fa;}
    .stMetric {background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);}
    h1 {color: #1f77b4; font-weight: 700;}
    h2 {color: #2c3e50; font-weight: 600;}
    h3 {color: #34495e; font-weight: 500;}
</style>
""", unsafe_allow_html=True)

OUTPUT_DIR = "/root/bigdata-bi-project/phase3_spark/output"

@st.cache_data
def load_csv(filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    if os.path.isdir(filepath):
        csv_files = glob.glob(os.path.join(filepath, "*.csv"))
        if csv_files:
            return pd.read_csv(csv_files[0])
    elif os.path.exists(filepath):
        return pd.read_csv(filepath)
    return pd.DataFrame()

st.title("📊 Scientific Articles Analysis Dashboard")
st.markdown("### Big Data BI Project - Phase 3: Apache Spark Analytics")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.markdown("# 📊")
    st.title("Navigation")
    page = st.radio("📊 Select Analysis", [
        "🏠 Overview",
        "📈 Publication Trends",
        "👥 Authors & Collaborations",
        "🏛️ Affiliations",
        "🔑 Keywords Analysis",
        "🚀 Emerging Trends"
    ], label_visibility="collapsed")
    

if page == "🏠 Overview":
    st.header("📊 Dataset Overview")
    
    # Load summary stats
    summary = load_csv("summary_stats.csv")
    by_source = load_csv("by_source.csv")
    
    if not summary.empty:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📚 Total Articles", f"{int(summary['total_articles'].iloc[0]):,}")
        with col2:
            st.metric("🔗 Unique DOIs", f"{int(summary['unique_dois'].iloc[0]):,}")
        with col3:
            st.metric("📖 Journals", f"{int(summary['unique_journals'].iloc[0]):,}")
        with col4:
            year_range = f"{int(summary['earliest_year'].iloc[0])} - {int(summary['latest_year'].iloc[0])}"
            st.metric("📅 Year Range", year_range)
    
    st.markdown("")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📊 Distribution by Source")
        if not by_source.empty:
            fig = px.pie(by_source, names='source', values='count',
                        color_discrete_sequence=px.colors.qualitative.Set3,
                        hole=0.4)
            fig.update_traces(textposition='inside', textinfo='percent+label',
                            textfont_size=14, marker=dict(line=dict(color='white', width=2)))
            fig.update_layout(height=400, showlegend=True, 
                            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Articles by Source")
        if not by_source.empty:
            fig = go.Figure(data=[
                go.Bar(x=by_source['source'], y=by_source['count'],
                      marker_color=['#1f77b4', '#ff7f0e', '#2ca02c'],
                      text=by_source['count'], textposition='outside')
            ])
            fig.update_layout(
                height=400, showlegend=False,
                xaxis_title="Source", yaxis_title="Number of Articles",
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='lightgray')
            )
            st.plotly_chart(fig, use_container_width=True)

elif page == "📈 Publication Trends":
    st.header("📈 Publications Evolution Over Time")
    
    data = load_csv("publications_by_year.csv")
    if not data.empty:
        data = data.sort_values('year')
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=data['year'], y=data['count'],
                mode='lines+markers',
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=10, color='#1f77b4', line=dict(color='white', width=2)),
                fill='tozeroy', fillcolor='rgba(31, 119, 180, 0.2)',
                name='Publications'
            ))
            fig.update_layout(
                title="Publication Trend Analysis",
                xaxis_title="Year", yaxis_title="Number of Publications",
                height=500, hovermode='x unified',
                plot_bgcolor='white', paper_bgcolor='white',
                xaxis=dict(showgrid=True, gridcolor='lightgray'),
                yaxis=dict(showgrid=True, gridcolor='lightgray')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Statistics")
            total = data['count'].sum()
            avg = data['count'].mean()
            max_year = data.loc[data['count'].idxmax(), 'year']
            max_count = data['count'].max()
            
            st.metric("Total Publications", f"{int(total):,}")
            st.metric("Average per Year", f"{int(avg):,}")
            st.metric("Peak Year", f"{int(max_year)}")
            st.metric("Peak Count", f"{int(max_count):,}")
            
            st.markdown("")
            st.dataframe(data, use_container_width=True, height=300)

elif page == "👥 Authors & Collaborations":
    st.header("👥 Authors & Collaboration Analysis")
    
    tab1, tab2 = st.tabs(["📊 Top Authors", "🔗 Collaboration Network"])
    
    with tab1:
        authors = load_csv("top_authors.csv")
        if not authors.empty:
            limit = st.slider("Number of authors to display", 10, 50, 20)
            top_authors = authors.head(limit)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = px.bar(top_authors.head(15), x='publications', y='author',
                           orientation='h', color='publications',
                           color_continuous_scale='Blues',
                           labels={'publications': 'Publications', 'author': 'Author'})
                fig.update_layout(height=600, showlegend=False,
                                title="Top 15 Most Productive Authors",
                                yaxis={'categoryorder':'total ascending'})
                fig.update_traces(texttemplate='%{x}', textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("📈 Productivity Stats")
                st.metric("Total Authors", f"{len(authors):,}")
                st.metric("Max Publications", f"{int(authors['publications'].max())}")
                st.metric("Avg Publications", f"{authors['publications'].mean():.1f}")
                
                st.markdown("")
                st.dataframe(top_authors, use_container_width=True, height=400)
    
    with tab2:
        network = load_csv("coauthor_network.csv")
        if not network.empty:
            st.subheader("🔗 Top Collaborations")
            top_collab = network.head(20)
            
            fig = px.bar(top_collab, x='collaborations', y=top_collab.index,
                        orientation='h', color='collaborations',
                        color_continuous_scale='Viridis',
                        labels={'collaborations': 'Joint Publications', 'y': 'Collaboration Pair'})
            fig.update_layout(height=600, showlegend=False,
                            yaxis={'categoryorder':'total ascending'})
            fig.update_traces(texttemplate='%{x}', textposition='outside',
                            hovertemplate='<b>%{customdata[0]} ↔ %{customdata[1]}</b><br>Collaborations: %{x}<extra></extra>',
                            customdata=top_collab[['author1', 'author2']].values)
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(network.head(50), use_container_width=True)

elif page == "🏛️ Affiliations":
    st.header("🏛️ Affiliations & Institutions Analysis")
    
    affiliations = load_csv("top_affiliations.csv")
    quartiles = load_csv("quartile_distribution.csv")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if not affiliations.empty:
            st.subheader("🏛️ Top Institutions")
            top_aff = affiliations.head(20)
            
            fig = px.bar(top_aff, x='count', y='affiliation',
                       orientation='h', color='count',
                       color_continuous_scale='Teal',
                       labels={'count': 'Articles', 'affiliation': 'Institution'})
            fig.update_layout(height=700, showlegend=False,
                            yaxis={'categoryorder':'total ascending'})
            fig.update_traces(texttemplate='%{x}', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if not quartiles.empty and 'quartile_assigned' in quartiles.columns:
            st.subheader("📊 Quartile Distribution")
            fig = px.pie(quartiles, names='quartile_assigned', values='count',
                        color_discrete_sequence=px.colors.sequential.RdBu,
                        hole=0.4)
            fig.update_traces(textposition='inside', textinfo='percent+label',
                            textfont_size=14)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("")
            st.dataframe(affiliations, use_container_width=True, height=400)

elif page == "🔑 Keywords Analysis":
    st.header("🔑 Keywords & Topics Analysis")
    
    keywords = load_csv("keywords_by_year.csv")
    if not keywords.empty:
        years = sorted(keywords['year'].unique())
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_year = st.selectbox("📅 Select Year", years, index=len(years)-1)
        with col2:
            top_n = st.slider("Top N Keywords", 10, 50, 20)
        
        year_data = keywords[keywords['year'] == selected_year].nlargest(top_n, 'frequency')
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.bar(year_data.head(15), x='frequency', y='keyword',
                       orientation='h', color='frequency',
                       color_continuous_scale='Sunset',
                       labels={'frequency': 'Frequency', 'keyword': 'Keyword'})
            fig.update_layout(height=600, showlegend=False,
                            title=f"Top Keywords in {selected_year}",
                            yaxis={'categoryorder':'total ascending'})
            fig.update_traces(texttemplate='%{x}', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Year Statistics")
            if len(year_data) > 0:
                st.metric("Total Keywords", len(year_data))
                st.metric("Total Occurrences", int(year_data['frequency'].sum()))
                st.metric("Most Frequent", year_data.iloc[0]['keyword'])
            else:
                st.warning("No data for selected year")
            
            st.markdown("")
            st.dataframe(year_data, use_container_width=True, height=400)
        
        st.markdown("---")
        st.subheader("📈 Keyword Trends Over Time")
        
        top_keywords = keywords.groupby('keyword')['frequency'].sum().nlargest(10).index
        trend_data = keywords[keywords['keyword'].isin(top_keywords)]
        
        fig = px.line(trend_data, x='year', y='frequency', color='keyword',
                     markers=True, line_shape='spline',
                     labels={'frequency': 'Frequency', 'year': 'Year', 'keyword': 'Keyword'})
        fig.update_layout(height=500, hovermode='x unified',
                        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5))
        st.plotly_chart(fig, use_container_width=True)

elif page == "🚀 Emerging Trends":
    st.header("🚀 Emerging Trends & Weak Signals Detection")
    
    weak_signals = load_csv("weak_signals.csv")
    if not weak_signals.empty:
        st.subheader("🔍 Weak Signal Detection (2023+)")
        st.markdown("Tracking emerging research areas and technologies in recent publications")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=weak_signals['occurrences'],
                y=weak_signals['term'],
                orientation='h',
                marker=dict(
                    color=weak_signals['occurrences'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Occurrences")
                ),
                text=weak_signals['occurrences'],
                textposition='outside'
            ))
            fig.update_layout(
                height=600,
                title="Emerging Terms Detection",
                xaxis_title="Number of Occurrences",
                yaxis_title="Emerging Term",
                yaxis={'categoryorder':'total ascending'},
                plot_bgcolor='white'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Signal Strength")
            total = weak_signals['occurrences'].sum()
            st.metric("Total Detections", int(total))
            st.metric("Strongest Signal", weak_signals.iloc[0]['term'])
            st.metric("Signal Count", weak_signals.iloc[0]['occurrences'])
            
            st.markdown("")
            st.info("💡 These terms represent cutting-edge research areas detected in publications from 2023 onwards.")
            
            st.dataframe(weak_signals, use_container_width=True)
        
        st.markdown("---")
        st.subheader("🎯 Trend Insights")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**🤖 AI/ML Trends**")
            ai_terms = weak_signals[weak_signals['term'].str.contains('learning|ai|gpt|llm', case=False)]
            st.metric("AI-related signals", len(ai_terms))
        with col2:
            st.markdown("**⚛️ Quantum Computing**")
            quantum_terms = weak_signals[weak_signals['term'].str.contains('quantum', case=False)]
            st.metric("Quantum signals", len(quantum_terms))
        with col3:
            st.markdown("**🔬 Other Emerging**")
            other = len(weak_signals) - len(ai_terms) - len(quantum_terms)
            st.metric("Other signals", other)

st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>Big Data BI Project - Phase 3 | Apache Spark + Flask + Streamlit</div>", unsafe_allow_html=True)
