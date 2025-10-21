import argparse
import sys
import os
import pandas as pd
import time
from typing import Dict, List
from datetime import datetime
from config import Config
from data_processor import DataProcessor
from mapping_engine import MappingEngine
from batch_processor import BatchMappingEngine
from hybrid_mapping_engine import HybridMappingEngine
from direct_rxnorm_mapper import DirectRxNormMapper
from csv_exporter import CSVExporter

def main():
    parser = argparse.ArgumentParser(description='Moroccan Medical Products to RxNorm Mapper')
    parser.add_argument('--mode', choices=['process', 'batch', 'direct', 'hybrid', 'dashboard'], default='direct',
                        help='Run mode: process (OpenAI individual), batch (OpenAI batch), direct (RxNorm direct), hybrid (with fallback), or dashboard')
    parser.add_argument('--input-file', default=Config.INPUT_FILE,
                        help='Input Excel file path')
    parser.add_argument('--batch-size', type=int, default=Config.BATCH_SIZE,
                        help='Batch size for processing')
    parser.add_argument('--start-index', type=int, default=0,
                        help='Starting index for processing')
    parser.add_argument('--max-products', type=int,
                        help='Maximum number of products to process')
    parser.add_argument('--workers', type=int, default=Config.MAX_WORKERS,
                        help='Number of parallel workers')
    parser.add_argument('--output', default=None,
                        help='Custom output file name')
    
    args = parser.parse_args()
    
    if args.mode == 'process':
        run_individual_processing(args)
    elif args.mode == 'batch':
        run_batch_processing(args)
    elif args.mode == 'direct':
        run_direct_processing(args)
    elif args.mode == 'hybrid':
        run_hybrid_processing(args)
    elif args.mode == 'dashboard':
        print("Dashboard mode requires Streamlit. Use 'streamlit run main.py -- --mode dashboard'")
        sys.exit(1)

def run_direct_processing(args):
    """Run the optimized direct RxNorm mapping pipeline"""
    start_time = time.time()
    
    # Check Mistral API key (optional but helpful for form translation)
    if not Config.MISTRAL_API_KEY:
        print("Note: MISTRAL_API_KEY not found. Form translations will use basic mapping only.")
        print("Add MISTRAL_API_KEY to your .env file for better form translations.")
    
    # Load data
    print("Loading data...")
    data_processor = DataProcessor(args.input_file)
    products_df = data_processor.load_data()
    
    if args.max_products:
        products_df = products_df.head(args.max_products)
        print(f"Limited to {args.max_products} products")
    
    if args.start_index > 0:
        if args.start_index >= len(products_df):
            print(f"Error: Start index {args.start_index} is beyond dataset size ({len(products_df)})")
            return
        products_df = products_df.iloc[args.start_index:]
        print(f"Starting from index {args.start_index}, {len(products_df)} products remaining")
    
    # Initialize direct RxNorm mapper
    print("Initializing direct RxNorm mapper...")
    direct_mapper = DirectRxNormMapper(Config.MISTRAL_API_KEY)
    
    # Process products using the new optimized method
    print(f"Starting direct RxNorm mapping of {len(products_df)} products...")
    print(f"Batch size: {args.batch_size}, Workers: {args.workers}")
    
    # Use the new process_dataframe method
    results = direct_mapper.process_dataframe(products_df, args.batch_size)
    
    # Export results
    print("Exporting results...")
    exporter = CSVExporter()
    
    # Generate output filename with timestamp if not specified
    if args.output:
        output_filename = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"direct_rxnorm_mapping_{timestamp}.csv"
    
    csv_file = exporter.export_results(results, filename_prefix=output_filename.split('.')[0])
    
    # Calculate final statistics
    total = len(results)
    successful = sum(1 for r in results if r.get('final_status') == 'success')
    failed = total - successful
    success_rate = (successful / total * 100) if total > 0 else 0
    
    total_time = time.time() - start_time
    products_per_second = total / total_time if total_time > 0 else 0
    
    print("\n" + "="*60)
    print("DIRECT MAPPING STATISTICS")
    print("="*60)
    print(f"Total Products Processed: {total}")
    print(f"Successful Mappings: {successful} ({success_rate:.2f}%)")
    print(f"Failed Mappings: {failed}")
    print(f"Total Processing Time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
    print(f"Processing Speed: {products_per_second:.2f} products per second")
    print(f"Results exported to: {csv_file}")
    print("="*60)

def run_hybrid_processing(args):
    """Run the hybrid processing pipeline (Direct RxNorm with OpenAI fallback)"""
    start_time = time.time()
    
    # Check Mistral API key
    if not Config.MISTRAL_API_KEY:
        print("Note: MISTRAL_API_KEY not found. Form translations will use basic mapping only.")
        print("Add MISTRAL_API_KEY to your .env file for better form translations.")
    
    # Check OpenAI API key for fallback
    if not Config.OPENAI_API_KEY:
        print("Warning: OPENAI_API_KEY not found. Fallback to OpenAI will not be available.")
        print("Add OPENAI_API_KEY to your .env file for OpenAI fallback.")
        print("Continuing with direct RxNorm mapping only...")
    
    # Load data
    print("Loading data...")
    data_processor = DataProcessor(args.input_file)
    products_df = data_processor.load_data()
    
    if args.max_products:
        products_df = products_df.head(args.max_products)
        print(f"Limited to {args.max_products} products")
    
    if args.start_index > 0:
        if args.start_index >= len(products_df):
            print(f"Error: Start index {args.start_index} is beyond dataset size ({len(products_df)})")
            return
        products_df = products_df.iloc[args.start_index:]
        print(f"Starting from index {args.start_index}, {len(products_df)} products remaining")
    
    # Initialize hybrid mapping engine
    print("Initializing hybrid mapping engine...")
    hybrid_engine = HybridMappingEngine(
        openai_api_key=Config.OPENAI_API_KEY,
        mistral_api_key=Config.MISTRAL_API_KEY
    )
    
    # Process products with hybrid approach
    print(f"Starting hybrid mapping of {len(products_df)} products...")
    print(f"Batch size: {args.batch_size}, Workers: {args.workers}")
    
    if Config.OPENAI_API_KEY:
        results = hybrid_engine.process_with_fallback(
            products_df, 
            batch_size=args.batch_size,
            max_workers=args.workers
        )
    else:
        results = hybrid_engine.process_dataframe_direct(
            products_df,
            batch_size=args.batch_size,
            max_workers=args.workers
        )
    
    # Export results
    print("Exporting results...")
    exporter = CSVExporter()
    
    # Generate output filename with timestamp if not specified
    if args.output:
        output_filename = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"hybrid_rxnorm_mapping_{timestamp}.csv"
    
    csv_file = exporter.export_results(results, filename_prefix=output_filename.split('.')[0])
    
    # Final statistics are already printed by the hybrid mapping engine
    print(f"Results exported to: {csv_file}")

def run_individual_processing(args):
    """Run the original individual processing pipeline with OpenAI"""
    
    # Check OpenAI API key
    if not Config.OPENAI_API_KEY:
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
    
    if args.start_index > 0:
        products_df = products_df.iloc[args.start_index:]
        print(f"Starting from index {args.start_index}")
    
    # Initialize mapping engine (original OpenAI approach)
    print("Initializing mapping engine...")
    mapping_engine = MappingEngine(Config.OPENAI_API_KEY)
    
    # Process products
    print("Starting individual OpenAI processing...")
    start_time = time.time()
    current_idx = 0
    total_products = len(products_df)
    
    while current_idx < total_products:
        end_idx = min(current_idx + args.batch_size, total_products)
        batch_size = end_idx - current_idx
        
        try:
            print(f"Processing batch {current_idx//args.batch_size + 1}: products {current_idx}-{end_idx-1}")
            batch_results = mapping_engine.process_batch(
                products_df, 
                current_idx, 
                batch_size
            )
            current_idx = end_idx
            
            # Show progress
            elapsed = time.time() - start_time
            products_per_second = current_idx / elapsed if elapsed > 0 else 0
            estimated_remaining = (total_products - current_idx) / products_per_second if products_per_second > 0 else 0
            
            stats = mapping_engine.get_statistics()
            print(f"\nProgress: {current_idx}/{total_products} ({current_idx/total_products*100:.1f}%)")
            print(f"Success Rate: {stats['success_rate']:.1f}%")
            print(f"Review Rate: {stats['review_rate']:.1f}%")
            print(f"Processing speed: {products_per_second:.2f} products/second")
            print(f"Estimated time remaining: {estimated_remaining/60:.1f} minutes")
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\nProcessing interrupted by user")
            break
        except Exception as e:
            print(f"Error in batch processing: {e}")
            current_idx = end_idx
            continue
    
    # Export results
    print("Exporting results...")
    exporter = CSVExporter()
    
    # Generate output filename with timestamp if not specified
    if args.output:
        output_filename = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"openai_mapping_{timestamp}.csv"
    
    csv_file = exporter.export_results(mapping_engine.results, filename_prefix=output_filename.split('.')[0])
    
    # Final statistics
    final_stats = mapping_engine.get_statistics()
    total_time = time.time() - start_time
    
    print("\n" + "="*60)
    print("OPENAI INDIVIDUAL PROCESSING STATISTICS")
    print("="*60)
    print(f"Total Products Processed: {final_stats['total_processed']}")
    print(f"Successful Mappings: {final_stats['successful_mappings']}")
    print(f"Failed Mappings: {final_stats['failed_mappings']}")
    print(f"Need Manual Review: {final_stats['needs_manual_review']}")
    print(f"Success Rate: {final_stats['success_rate']:.2f}%")
    print(f"Review Rate: {final_stats['review_rate']:.2f}%")
    print(f"Total Processing Time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
    
    products_per_second = final_stats['total_processed'] / total_time if total_time > 0 else 0
    print(f"Processing Speed: {products_per_second:.2f} products per second")
    print(f"Results exported to: {csv_file}")
    print("="*60)

def run_batch_processing(args):
    """Run the OpenAI Batch API processing pipeline"""
    
    # Check OpenAI API key
    if not Config.OPENAI_API_KEY:
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
    
    if args.start_index > 0:
        products_df = products_df.iloc[args.start_index:]
        print(f"Starting from index {args.start_index}")
    
    # Initialize batch mapping engine
    print("Initializing OpenAI Batch API engine...")
    batch_engine = BatchMappingEngine(Config.OPENAI_API_KEY)
    
    try:
        # Process all products with Batch API
        print("🚀 Starting OpenAI Batch API processing...")
        print(f"This will process {len(products_df)} products in a single batch")
        print("Note: Batch processing can take up to 24 hours but is much more cost-effective")
        
        # Confirm with user for large batches
        if len(products_df) > 100:
            confirm = input(f"\nYou're about to process {len(products_df)} products with OpenAI Batch API. Continue? (y/N): ")
            if confirm.lower() != 'y':
                print("Processing cancelled")
                return
        
        start_time = time.time()
        results = batch_engine.process_with_batch_api(products_df)
        total_time = time.time() - start_time
        
        # Export results
        print("Exporting results...")
        exporter = CSVExporter()
        
        # Generate output filename with timestamp if not specified
        if args.output:
            output_filename = args.output
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"openai_batch_mapping_{timestamp}.csv"
        
        csv_file = exporter.export_results(results, filename_prefix=output_filename.split('.')[0])
        
        # Final statistics
        final_stats = batch_engine.get_statistics()
        
        print("\n" + "="*60)
        print("OPENAI BATCH PROCESSING STATISTICS")
        print("="*60)
        print(f"Total Products Processed: {final_stats['total_processed']}")
        print(f"Successful Mappings: {final_stats['successful_mappings']}")
        print(f"Failed Mappings: {final_stats['failed_mappings']}")
        print(f"Need Manual Review: {final_stats['needs_manual_review']}")
        print(f"Success Rate: {final_stats['success_rate']:.2f}%")
        print(f"Review Rate: {final_stats['review_rate']:.2f}%")
        print(f"Total Processing Time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
        
        products_per_second = final_stats['total_processed'] / total_time if total_time > 0 else 0
        print(f"Processing Speed: {products_per_second:.2f} products per second")
        print(f"Results exported to: {csv_file}")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\nProcessing interrupted by user")
    except Exception as e:
        print(f"Error in batch processing: {e}")
        print("You can try individual processing mode with --mode process")

if __name__ == "__main__":
    main()