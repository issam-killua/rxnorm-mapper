import argparse
import sys
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import Config
from data_processor import DataProcessor
from mapping_engine import MappingEngine
from batch_processor import BatchMappingEngine  # New import
from csv_exporter import CSVExporter

def main():
    parser = argparse.ArgumentParser(description='Moroccan Medical Products to RxNorm Mapper')
    parser.add_argument('--mode', choices=['process', 'batch', 'dashboard'], default='process',
                        help='Run mode: process data individually, batch process, or show dashboard')
    parser.add_argument('--input-file', default=Config.INPUT_FILE,
                        help='Input Excel file path')
    parser.add_argument('--batch-size', type=int, default=Config.BATCH_SIZE,
                        help='Batch size for individual processing (ignored in batch mode)')
    parser.add_argument('--start-index', type=int, default=0,
                        help='Starting index for individual processing (ignored in batch mode)')
    parser.add_argument('--max-products', type=int,
                        help='Maximum number of products to process')
    
    args = parser.parse_args()
    
    if args.mode == 'process':
        run_individual_processing(args)  # Your existing method
    elif args.mode == 'batch':
        run_batch_processing(args)       # New batch API method
    elif args.mode == 'dashboard':
        run_dashboard()

def run_batch_processing(args):
    """Run the batch API processing pipeline"""
    
    # Check OpenAI API key
    if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY == 'your_openai_api_key_here':
        print("Error: OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key in the .env file")
        sys.exit(1)
    
    # Load data
    print("Loading data...")
    data_processor = DataProcessor(args.input_file)
    products_df = data_processor.load_data()
    
    if args.max_products:
        products_df = products_df.head(args.max_products)
        print(f"Limited to {args.max_products} products")
    
    # Initialize batch mapping engine
    print("Initializing batch mapping engine...")
    batch_engine = BatchMappingEngine(Config.OPENAI_API_KEY)
    
    try:
        # Process all products with Batch API
        print("🚀 Starting Batch API processing...")
        print(f"This will process {len(products_df)} products in a single batch")
        print("Note: Batch processing can take up to 24 hours but is much more cost-effective")
        
        # Confirm with user for large batches
        if len(products_df) > 100:
            confirm = input(f"\nYou're about to process {len(products_df)} products. Continue? (y/N): ")
            if confirm.lower() != 'y':
                print("Processing cancelled")
                return
        
        results = batch_engine.process_with_batch_api(products_df)
        
        # Export results
        print("Exporting results...")
        exporter = CSVExporter()
        csv_file = exporter.export_results(results)
        
        # Final statistics
        final_stats = batch_engine.get_statistics()
        print("\n" + "="*60)
        print("FINAL BATCH PROCESSING STATISTICS")
        print("="*60)
        print(f"Total Products Processed: {final_stats['total_processed']}")
        print(f"Successful Mappings: {final_stats['successful_mappings']}")
        print(f"Failed Mappings: {final_stats['failed_mappings']}")
        print(f"Need Manual Review: {final_stats['needs_manual_review']}")
        print(f"Success Rate: {final_stats['success_rate']:.2f}%")
        print(f"Review Rate: {final_stats['review_rate']:.2f}%")
        print(f"\nResults exported to: {csv_file}")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\nProcessing interrupted by user")
    except Exception as e:
        print(f"Error in batch processing: {e}")
        print("You can try individual processing mode with --mode process")

def run_individual_processing(args):
    """Run the original individual processing pipeline"""
    
    # Check OpenAI API key
    if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY == 'your_openai_api_key_here':
        print("Error: OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key in the .env file")
        sys.exit(1)
    
    # Load data
    print("Loading data...")
    data_processor = DataProcessor(args.input_file)
    products_df = data_processor.load_data()
    
    if args.max_products:
        products_df = products_df.head(args.max_products)
        print(f"Limited to {args.max_products} products")
    
    # Initialize mapping engine (your existing one)
    print("Initializing mapping engine...")
    mapping_engine = MappingEngine(Config.OPENAI_API_KEY)
    
    # Process products
    print("Starting individual product mapping...")
    current_idx = args.start_index
    
    while current_idx < len(products_df):
        try:
            batch_results = mapping_engine.process_batch(
                products_df, 
                current_idx, 
                args.batch_size
            )
            current_idx += args.batch_size
            
            # Show progress
            stats = mapping_engine.get_statistics()
            print(f"\nProgress Update:")
            print(f"Processed: {stats['total_processed']}/{len(products_df)}")
            print(f"Success Rate: {stats['success_rate']:.1f}%")
            print(f"Review Rate: {stats['review_rate']:.1f}%")
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\nProcessing interrupted by user")
            break
        except Exception as e:
            print(f"Error in batch processing: {e}")
            current_idx += args.batch_size
            continue
    
    # Export results
    print("Exporting results...")
    exporter = CSVExporter()
    csv_file = exporter.export_results(mapping_engine.results)
    
    # Final statistics
    final_stats = mapping_engine.get_statistics()
    print("\n" + "="*60)
    print("FINAL PROCESSING STATISTICS")
    print("="*60)
    print(f"Total Products Processed: {final_stats['total_processed']}")
    print(f"Successful Mappings: {final_stats['successful_mappings']}")
    print(f"Failed Mappings: {final_stats['failed_mappings']}")
    print(f"Need Manual Review: {final_stats['needs_manual_review']}")
    print(f"Success Rate: {final_stats['success_rate']:.2f}%")
    print(f"Review Rate: {final_stats['review_rate']:.2f}%")
    print(f"\nResults exported to: {csv_file}")
    print("="*60)

def run_dashboard():
    """Run the enhanced Streamlit dashboard"""
    
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
        results, stats = process_dashboard_data(results_df)
        
        # Display enhanced dashboard sections
        display_dashboard_metrics(stats)
        display_dashboard_charts(stats, results)
        display_dashboard_insights(stats, results_df)
        display_dashboard_results(results_df)
        
    else:
        st.info("Please upload a mapping results CSV file to view the dashboard")
        display_example_dashboard()

def process_dashboard_data(results_df):
    """Process uploaded CSV data for dashboard display"""
    
    results = []
    for _, row in results_df.iterrows():
        result = {
            'final_status': row.get('final_status', ''),
            'needs_review': row.get('needs_review', False),
            'ai_mapping': {
                'confidence_score': row.get('ai_confidence_score', 0),
                'primary_rxnorm_concept': row.get('ai_primary_concept', ''),
            },
            'rxnorm_validation': {
                'found': row.get('rxnorm_found', False),
            },
            'timestamp': pd.to_datetime(row.get('timestamp', ''), errors='coerce')
        }
        results.append(result)
    
    # Calculate statistics
    total = len(results)
    successful = len([r for r in results if r['final_status'] == 'success'])
    failed = total - successful
    needs_review = len([r for r in results if r['needs_review']])
    
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
    }
    
    return results, stats

def display_dashboard_metrics(stats):
    """Display key performance metrics"""
    
    st.subheader("📊 Key Performance Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Processed", stats.get('total_processed', 0))
    
    with col2:
        st.metric(
            "Successful", 
            stats.get('successful_mappings', 0),
            f"{stats.get('success_rate', 0):.1f}%"
        )
    
    with col3:
        st.metric("Failed", stats.get('failed_mappings', 0))
    
    with col4:
        st.metric("Need Review", stats.get('needs_manual_review', 0))
    
    with col5:
        st.metric(
            "Avg Confidence", 
            f"{stats.get('avg_confidence', 0):.1f}/10"
        )

def display_dashboard_charts(stats, results):
    """Display visualization charts"""
    
    st.subheader("📈 Analytics & Visualizations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Success Rate Chart
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
            height=400
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Confidence Distribution
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
                labels={'x': 'Confidence Score (1-10)', 'y': 'Number of Products'}
            )
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)

def display_dashboard_insights(stats, results_df):
    """Display insights"""
    
    st.subheader("🧠 Insights & Recommendations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        success_rate = stats.get('success_rate', 0)
        if success_rate >= 90:
            st.success(f"🌟 Excellent success rate: {success_rate:.1f}%")
        elif success_rate >= 75:
            st.info(f"✅ Good success rate: {success_rate:.1f}%")
        else:
            st.warning(f"⚠️ Success rate needs improvement: {success_rate:.1f}%")
    
    with col2:
        avg_confidence = stats.get('avg_confidence', 0)
        if avg_confidence >= 8:
            st.success(f"🎯 High confidence: {avg_confidence:.1f}/10")
        else:
            st.info(f"📊 Average confidence: {avg_confidence:.1f}/10")
    
    with col3:
        review_rate = stats.get('review_rate', 0)
        if review_rate <= 15:
            st.success(f"✨ Low review rate: {review_rate:.1f}%")
        else:
            st.warning(f"📋 High review rate: {review_rate:.1f}%")

def display_dashboard_results(results_df):
    """Display detailed results table"""
    
    st.subheader("📋 Detailed Results")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox("Filter by Status", ['All', 'success', 'failed'])
    
    with col2:
        confidence_filter = st.slider("Min Confidence", 0, 10, 0)
    
    with col3:
        search_term = st.text_input("Search Products")
    
    # Apply filters
    filtered_df = results_df.copy()
    
    if status_filter != 'All':
        filtered_df = filtered_df[filtered_df['final_status'] == status_filter]
    
    if confidence_filter > 0:
        filtered_df = filtered_df[filtered_df['ai_confidence_score'] >= confidence_filter]
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['original_product_name'].str.contains(search_term, case=False, na=False)
        ]
    
    st.write(f"Showing {len(filtered_df)} of {len(results_df)} results")
    
    # Display key columns
    display_columns = [
        'original_product_name', 'original_dci', 'ai_primary_concept', 
        'ai_confidence_score', 'rxnorm_found', 'rxnorm_name', 'final_status'
    ]
    
    available_columns = [col for col in display_columns if col in filtered_df.columns]
    st.dataframe(filtered_df[available_columns], use_container_width=True, height=400)

def display_example_dashboard():
    """Show example when no file uploaded"""
    st.subheader("📊 Example Dashboard")
    st.info("Upload your CSV to see your actual results here!")
    
    example_data = {'Status': ['Successful', 'Failed'], 'Count': [87, 13]}
    fig = px.bar(example_data, x='Status', y='Count', title="Example Results")
    st.plotly_chart(fig)

if __name__ == "__main__":
    main()