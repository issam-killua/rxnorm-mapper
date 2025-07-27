import argparse
import sys
import os
import streamlit as st
import pandas as pd
from config import Config
from data_processor import DataProcessor
from mapping_engine import MappingEngine
from csv_exporter import CSVExporter
from dashboard import Dashboard

def main():
    parser = argparse.ArgumentParser(description='Moroccan Medical Products to RxNorm Mapper')
    parser.add_argument('--mode', choices=['process', 'dashboard'], default='process',
                        help='Run mode: process data or show dashboard')
    parser.add_argument('--input-file', default=Config.INPUT_FILE,
                        help='Input Excel file path')
    parser.add_argument('--batch-size', type=int, default=Config.BATCH_SIZE,
                        help='Batch size for processing')
    parser.add_argument('--start-index', type=int, default=0,
                        help='Starting index for processing')
    parser.add_argument('--max-products', type=int,
                        help='Maximum number of products to process')
    
    args = parser.parse_args()
    
    if args.mode == 'process':
        run_processing(args)
    elif args.mode == 'dashboard':
        run_dashboard()

def run_processing(args):
    """Run the main processing pipeline"""
    
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
    
    # Initialize mapping engine
    print("Initializing mapping engine...")
    mapping_engine = MappingEngine(Config.OPENAI_API_KEY)
    
    # Process products
    print("Starting product mapping...")
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
    """Run the Streamlit dashboard"""
    
    # MOVE PAGE CONFIG TO THE VERY BEGINNING
    st.set_page_config(
        page_title="RxNorm Mapping Dashboard",
        page_icon="💊",
        layout="wide"
    )
    
    st.title("🏥 RxNorm Mapping Dashboard")
    st.markdown("Monitor and analyze Moroccan medical products mapping to RxNorm standards")
    
    # Remove the Dashboard class initialization that was causing the error
    # dashboard = Dashboard()  # REMOVE THIS LINE
    
    # File upload for results
    uploaded_file = st.file_uploader("Upload mapping results CSV", type=['csv'])
    
    if uploaded_file:
        # Load results
        results_df = pd.read_csv(uploaded_file)
        
        # Convert to results format for statistics
        results = []
        for _, row in results_df.iterrows():
            result = {
                'final_status': row.get('final_status', ''),
                'needs_review': row.get('needs_review', False),
                'ai_mapping': {
                    'confidence_score': row.get('ai_confidence_score', 0)
                },
                'timestamp': pd.to_datetime(row.get('timestamp', ''), errors='coerce')
            }
            results.append(result)
        
        # Calculate statistics
        total = len(results)
        successful = len([r for r in results if r['final_status'] == 'success'])
        failed = total - successful
        needs_review = len([r for r in results if r['needs_review']])
        
        stats = {
            'total_processed': total,
            'successful_mappings': successful,
            'failed_mappings': failed,
            'needs_manual_review': needs_review,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'review_rate': (needs_review / total * 100) if total > 0 else 0
        }
        
        # Display statistics directly
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Processed", stats.get('total_processed', 0))
        
        with col2:
            st.metric("Successful Mappings", stats.get('successful_mappings', 0))
        
        with col3:
            st.metric("Failed Mappings", stats.get('failed_mappings', 0))
        
        with col4:
            st.metric("Need Review", stats.get('needs_manual_review', 0))
        
        # Create charts directly
        col1, col2 = st.columns(2)
        
        with col1:
            import plotly.graph_objects as go
            fig1 = go.Figure(data=[
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
            
            fig1.update_layout(
                title="Mapping Results Overview",
                xaxis_title="Status",
                yaxis_title="Number of Products"
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            import plotly.express as px
            confidence_scores = []
            for result in results:
                ai_mapping = result.get('ai_mapping', {})
                if ai_mapping and ai_mapping.get('confidence_score'):
                    confidence_scores.append(ai_mapping['confidence_score'])
            
            if confidence_scores:
                fig2 = px.histogram(
                    x=confidence_scores,
                    nbins=10,
                    title="AI Confidence Score Distribution",
                    labels={'x': 'Confidence Score (1-10)', 'y': 'Number of Products'}
                )
                st.plotly_chart(fig2, use_container_width=True)
        
        # Detailed results table
        st.subheader("Detailed Results")
        st.dataframe(results_df, use_container_width=True)
    
    else:
        st.info("Please upload a mapping results CSV file to view the dashboard")

if __name__ == "__main__":
    main()
