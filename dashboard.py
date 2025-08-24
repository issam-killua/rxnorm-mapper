import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List
import json

def create_enhanced_dashboard():
    """Create an enhanced RxNorm mapping dashboard"""
    
    # Page configuration
    st.set_page_config(
        page_title="RxNorm Mapping Dashboard",
        page_icon="💊",
        layout="wide"
    )
    
    # Header
    st.title("🏥 RxNorm Mapping Dashboard")
    st.markdown("Monitor and analyze Moroccan medical products mapping to RxNorm standards")
    
    # Batch processing info
    st.info("💡 **Tip**: Use `--mode batch` for processing large datasets efficiently with OpenAI Batch API (50% cost reduction)")
    
    # File upload
    uploaded_file = st.file_uploader("Upload mapping results CSV", type=['csv'])
    
    if uploaded_file:
        # Load and process the CSV
        results_df = pd.read_csv(uploaded_file)
        
        # Process the data
        results, stats = process_uploaded_data(results_df)
        
        # Display dashboard sections
        display_key_metrics(stats)
        display_charts(stats, results)
        display_insights(stats, results_df)
        display_detailed_results(results_df)
        
    else:
        # Show example/empty state
        st.info("Please upload a mapping results CSV file to view the dashboard")
        display_example_dashboard()

def process_uploaded_data(results_df):
    """Process uploaded CSV data for dashboard display"""
    
    # Convert DataFrame to results format for statistics
    results = []
    for _, row in results_df.iterrows():
        result = {
            'final_status': row.get('final_status', ''),
            'needs_review': row.get('needs_review', False),
            'ai_mapping': {
                'confidence_score': row.get('ai_confidence_score', 0),
                'primary_rxnorm_concept': row.get('ai_primary_concept', ''),
                'reasoning': row.get('ai_reasoning', '')
            },
            'rxnorm_validation': {
                'found': row.get('rxnorm_found', False),
                'rxcui': row.get('rxnorm_rxcui', ''),
                'name': row.get('rxnorm_name', '')
            },
            'original_data': {
                'product_name': row.get('original_product_name', ''),
                'active_ingredient': row.get('original_dci', ''),
                'dosage': row.get('original_dosage', ''),
                'form': row.get('original_form', '')
            },
            'timestamp': pd.to_datetime(row.get('timestamp', ''), errors='coerce')
        }
        results.append(result)
    
    # Calculate statistics
    total = len(results)
    successful = len([r for r in results if r['final_status'] == 'success'])
    failed = total - successful
    needs_review = len([r for r in results if r['needs_review']])
    
    # Calculate confidence stats
    confidence_scores = [r['ai_mapping']['confidence_score'] for r in results 
                        if r['ai_mapping']['confidence_score'] > 0]
    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
    
    stats = {
        'total_processed': total,
        'successful_mappings': successful,
        'failed_mappings': failed,
        'needs_manual_review': needs_review,
        'success_rate': (successful / total * 100) if total > 0 else 0,
        'review_rate': (needs_review / total * 100) if total > 0 else 0,
        'avg_confidence': avg_confidence,
        'high_confidence': len([s for s in confidence_scores if s >= 8]),
        'processing_time': results[0]['timestamp'] if results and results[0]['timestamp'] else None
    }
    
    return results, stats

def display_key_metrics(stats):
    """Display key performance metrics"""
    
    st.subheader("📊 Key Performance Metrics")
    
    # Main metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Processed", stats.get('total_processed', 0))
    
    with col2:
        st.metric(
            "Successful Mappings", 
            stats.get('successful_mappings', 0),
            f"{stats.get('success_rate', 0):.1f}%"
        )
    
    with col3:
        st.metric("Failed Mappings", stats.get('failed_mappings', 0))
    
    with col4:
        st.metric("Need Review", stats.get('needs_manual_review', 0))
    
    with col5:
        st.metric(
            "Avg Confidence", 
            f"{stats.get('avg_confidence', 0):.1f}/10",
            f"{stats.get('high_confidence', 0)} high confidence"
        )
    
    # Additional metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        success_rate = stats.get('success_rate', 0)
        color = "green" if success_rate >= 80 else "orange" if success_rate >= 60 else "red"
        st.metric("Success Rate", f"{success_rate:.1f}%")
    
    with col2:
        review_rate = stats.get('review_rate', 0)
        st.metric("Review Rate", f"{review_rate:.1f}%")
    
    with col3:
        if stats.get('processing_time'):
            st.metric("Last Processing", stats['processing_time'].strftime("%Y-%m-%d %H:%M"))
        else:
            st.metric("Processing Time", "N/A")
    
    with col4:
        # Cost estimation (rough)
        total = stats.get('total_processed', 0)
        estimated_cost = total * 0.003  # Rough estimate
        st.metric("Est. Cost", f"${estimated_cost:.2f}")

def display_charts(stats, results):
    """Display visualization charts"""
    
    st.subheader("📈 Analytics & Visualizations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Success Rate Overview Chart
        fig1 = go.Figure(data=[
            go.Bar(
                x=['Successful', 'Failed', 'Need Review'],
                y=[
                    stats.get('successful_mappings', 0),
                    stats.get('failed_mappings', 0),
                    stats.get('needs_manual_review', 0)
                ],
                marker_color=['#2E8B57', '#DC143C', '#FF8C00'],
                text=[
                    stats.get('successful_mappings', 0),
                    stats.get('failed_mappings', 0),
                    stats.get('needs_manual_review', 0)
                ],
                textposition='auto'
            )
        ])
        
        fig1.update_layout(
            title="Mapping Results Overview",
            xaxis_title="Status",
            yaxis_title="Number of Products",
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Confidence Score Distribution
        confidence_scores = []
        for result in results:
            ai_mapping = result.get('ai_mapping', {})
            if ai_mapping and ai_mapping.get('confidence_score', 0) > 0:
                confidence_scores.append(ai_mapping['confidence_score'])
        
        if confidence_scores:
            fig2 = px.histogram(
                x=confidence_scores,
                nbins=10,
                title="AI Confidence Score Distribution",
                labels={'x': 'Confidence Score (1-10)', 'y': 'Number of Products'},
                color_discrete_sequence=['#1f77b4']
            )
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No confidence score data available")
    
    # Additional charts row
    col1, col2 = st.columns(2)
    
    with col1:
        # Success Rate Pie Chart
        fig3 = go.Figure(data=[go.Pie(
            labels=['Successful', 'Failed', 'Need Review'],
            values=[
                stats.get('successful_mappings', 0),
                stats.get('failed_mappings', 0),
                stats.get('needs_manual_review', 0)
            ],
            marker_colors=['#2E8B57', '#DC143C', '#FF8C00'],
            hole=0.4
        )])
        fig3.update_layout(
            title="Processing Results Distribution",
            height=400
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        # RxNorm Validation Success
        rxnorm_found = len([r for r in results if r.get('rxnorm_validation', {}).get('found', False)])
        rxnorm_not_found = len(results) - rxnorm_found
        
        fig4 = go.Figure(data=[go.Bar(
            x=['RxNorm Found', 'RxNorm Not Found'],
            y=[rxnorm_found, rxnorm_not_found],
            marker_color=['#32CD32', '#FF6347'],
            text=[rxnorm_found, rxnorm_not_found],
            textposition='auto'
        )])
        fig4.update_layout(
            title="RxNorm Validation Results",
            xaxis_title="Validation Status",
            yaxis_title="Number of Products",
            height=400
        )
        st.plotly_chart(fig4, use_container_width=True)

def display_insights(stats, results_df):
    """Display insights and recommendations"""
    
    st.subheader("🧠 Insights & Recommendations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🎯 Performance Insights")
        success_rate = stats.get('success_rate', 0)
        if success_rate >= 90:
            st.success("🌟 Excellent success rate! Your mapping is performing very well.")
        elif success_rate >= 75:
            st.info("✅ Good success rate. Consider reviewing failed mappings for improvements.")
        else:
            st.warning("⚠️ Success rate could be improved. Review prompt engineering and data quality.")
        
        avg_confidence = stats.get('avg_confidence', 0)
        if avg_confidence >= 8:
            st.success(f"🎯 High average confidence ({avg_confidence:.1f}/10)")
        elif avg_confidence >= 6:
            st.info(f"👍 Moderate confidence ({avg_confidence:.1f}/10)")
        else:
            st.warning(f"⚡ Low confidence ({avg_confidence:.1f}/10) - consider improving prompts")
    
    with col2:
        st.markdown("### 🔍 Data Quality")
        
        # Check for missing original data
        missing_names = results_df['original_product_name'].isna().sum()
        missing_dci = results_df['original_dci'].isna().sum()
        
        if missing_names == 0 and missing_dci == 0:
            st.success("✅ Complete original data extraction")
        else:
            st.warning(f"⚠️ Missing data: {missing_names} names, {missing_dci} ingredients")
        
        # Check AI mapping quality
        ai_mappings = results_df['ai_primary_concept'].notna().sum()
        st.metric("AI Mappings Generated", f"{ai_mappings}/{len(results_df)}")
    
    with col3:
        st.markdown("### 💡 Recommendations")
        
        review_rate = stats.get('review_rate', 0)
        if review_rate > 30:
            st.warning("📋 High review rate - consider improving confidence thresholds")
        elif review_rate > 15:
            st.info("📝 Moderate review rate - some manual validation needed")
        else:
            st.success("✨ Low review rate - high automation achieved")
        
        # Cost optimization
        total_processed = stats.get('total_processed', 0)
        if total_processed > 1000:
            st.info("💰 For large batches, batch API provides 50% cost savings")

def display_detailed_results(results_df):
    """Display detailed results table with filtering"""
    
    st.subheader("📋 Detailed Results")
    
    # Filtering options
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            options=['All', 'success', 'failed', 'ai_failed', 'error'],
            index=0
        )
    
    with col2:
        confidence_filter = st.slider(
            "Min Confidence Score",
            min_value=0,
            max_value=10,
            value=0
        )
    
    with col3:
        rxnorm_filter = st.selectbox(
            "RxNorm Validation",
            options=['All', 'Found', 'Not Found'],
            index=0
        )
    
    with col4:
        search_term = st.text_input("Search Product Names", placeholder="Enter search term...")
    
    # Apply filters
    filtered_df = results_df.copy()
    
    if status_filter != 'All':
        filtered_df = filtered_df[filtered_df['final_status'] == status_filter]
    
    if confidence_filter > 0:
        filtered_df = filtered_df[filtered_df['ai_confidence_score'] >= confidence_filter]
    
    if rxnorm_filter == 'Found':
        filtered_df = filtered_df[filtered_df['rxnorm_found'] == True]
    elif rxnorm_filter == 'Not Found':
        filtered_df = filtered_df[filtered_df['rxnorm_found'] == False]
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['original_product_name'].str.contains(search_term, case=False, na=False)
        ]
    
    st.write(f"Showing {len(filtered_df)} of {len(results_df)} results")
    
    # Display the filtered results
    if len(filtered_df) > 0:
        # Select key columns for display
        display_columns = [
            'original_product_name', 'original_dci', 'original_dosage', 'original_form',
            'ai_primary_concept', 'ai_confidence_score', 
            'rxnorm_found', 'rxnorm_name', 'rxnorm_rxcui',
            'final_status', 'needs_review'
        ]
        
        # Ensure columns exist in the dataframe
        available_columns = [col for col in display_columns if col in filtered_df.columns]
        
        st.dataframe(
            filtered_df[available_columns],
            use_container_width=True,
            height=400
        )
        
        # Download filtered results
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Results",
            data=csv,
            file_name=f"filtered_results_{status_filter}_{len(filtered_df)}_products.csv",
            mime="text/csv"
        )
    else:
        st.warning("No results match your current filters.")

def display_example_dashboard():
    """Display example dashboard when no file is uploaded"""
    
    st.subheader("📊 Example Dashboard")
    st.info("Upload your mapping results CSV to see your actual data here")
    
    # Show example metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Processed", "1,500", "↑ 12%")
    with col2:
        st.metric("Success Rate", "87.3%", "↑ 2.1%")
    with col3:
        st.metric("Avg Confidence", "8.2/10", "↑ 0.3")
    with col4:
        st.metric("Need Review", "127", "↓ 5%")
    
    # Show example chart
    example_data = {
        'Status': ['Successful', 'Failed', 'Need Review'],
        'Count': [1310, 63, 127]
    }
    fig = px.bar(example_data, x='Status', y='Count', 
                 title="Example: Mapping Results Overview",
                 color='Status',
                 color_discrete_map={'Successful': '#2E8B57', 'Failed': '#DC143C', 'Need Review': '#FF8C00'})
    st.plotly_chart(fig, use_container_width=True)

# Main execution
if __name__ == "__main__":
    create_enhanced_dashboard()