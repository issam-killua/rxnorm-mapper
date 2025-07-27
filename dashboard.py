import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List

class Dashboard:
    def __init__(self):
        self.setup_page()
    
    def setup_page(self):
        st.set_page_config(
            page_title="RxNorm Mapping Dashboard",
            page_icon="💊",
            layout="wide"
        )
    
    def display_statistics(self, stats: Dict):
        """Display key statistics"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Processed", stats.get('total_processed', 0))
        
        with col2:
            st.metric("Successful Mappings", stats.get('successful_mappings', 0))
        
        with col3:
            st.metric("Failed Mappings", stats.get('failed_mappings', 0))
        
        with col4:
            st.metric("Need Review", stats.get('needs_manual_review', 0))
    
    def create_success_rate_chart(self, stats: Dict):
        """Create success rate visualization"""
        fig = go.Figure(data=[
            go.Bar(
                x=['Successful', 'Failed', 'Need Review'],
                y=[
                    stats.get('successful_mappings', 0),
                    stats.get('failed_mappings', 0),
                    stats.get('needs_manual_review', 0)
                ],
                marker_color=['green', 'red', 'orange']
            )
        ])
        
        fig.update_layout(
            title="Mapping Results Overview",
            xaxis_title="Status",
            yaxis_title="Number of Products"
        )
        
        return fig
    
    def create_confidence_distribution(self, results: List[Dict]):
        """Create confidence score distribution chart"""
        confidence_scores = []
        for result in results:
            ai_mapping = result.get('ai_mapping', {})
            if ai_mapping and ai_mapping.get('confidence_score'):
                confidence_scores.append(ai_mapping['confidence_score'])
        
        if confidence_scores:
            fig = px.histogram(
                x=confidence_scores,
                nbins=10,
                title="AI Confidence Score Distribution",
                labels={'x': 'Confidence Score (1-10)', 'y': 'Number of Products'}
            )
            return fig
        
        return None
