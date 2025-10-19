import argparse
import sys
import os
import pandas as pd
from config import Config
from data_processor import DataProcessor
from mapping_engine import MappingEngine
from batch_processor import BatchMappingEngine
from hybrid_mapping_engine import HybridMappingEngine
from csv_exporter import CSVExporter

def main():
    parser = argparse.ArgumentParser(description='Moroccan Medical Products to RxNorm Mapper')
    parser.add_argument('--mode', choices=['process', 'batch', 'hybrid', 'mistral', 'dashboard'], default='process',
                        help='Run mode: process data individually, batch process, hybrid, mistral-only, or show dashboard')
    parser.add_argument('--input-file', default=Config.INPUT_FILE,
                        help='Input Excel file path')
    parser.add_argument('--batch-size', type=int, default=Config.BATCH_SIZE,
                        help='Batch size for individual processing')
    parser.add_argument('--start-index', type=int, default=0,
                        help='Starting index for individual processing')
    parser.add_argument('--max-products', type=int,
                        help='Maximum number of products to process')
    
    args = parser.parse_args()
    
    if args.mode == 'process':
        run_individual_processing(args)
    elif args.mode == 'batch':
        run_batch_processing(args)
    elif args.mode == 'hybrid':
        run_hybrid_processing(args)
    elif args.mode == 'mistral':
        run_mistral_only_processing(args)
    elif args.mode == 'dashboard':
        print("Dashboard mode is not implemented in this version. Please install and configure Streamlit.")
        sys.exit(1)

def run_mistral_only_processing(args):
    """Run the Mistral-only processing pipeline (no OpenAI fallback)"""
    
    # Check Mistral API key
    if not Config.MISTRAL_API_KEY or Config.MISTRAL_API_KEY == 'your_mistral_api_key_here':
        print("Error: MISTRAL_API_KEY not found in environment variables")
        print("Please set your Mistral API key in the .env file")
        sys.exit(1)
    
    # Load data
    print("Loading data...")
    data_processor = DataProcessor(args.input_file)
    products_df = data_processor.load_data()
    
    if args.max_products:
        products_df = products_df.head(args.max_products)
        print(f"Limited to {args.max_products} products")
    
    # Initialize hybrid mapping engine (with Mistral only)
    print("Initializing Mistral-only mapping engine...")
    hybrid_engine = HybridMappingEngine(mistral_api_key=Config.MISTRAL_API_KEY)  # No OpenAI key
    
    # Process products
    print("Starting Mistral-only product mapping...")
    current_idx = args.start_index
    
    while current_idx < len(products_df):
        try:
            batch_results = hybrid_engine.process_batch_mistral_only(
                products_df, 
                current_idx, 
                args.batch_size
            )
            current_idx += args.batch_size
            
            # Show progress
            stats = hybrid_engine.get_statistics()
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
    csv_file = exporter.export_results(hybrid_engine.results, filename_prefix="mistral_rxnorm_mapping")
    
    # Final statistics
    final_stats = hybrid_engine.get_statistics()
    print("\n" + "="*60)
    print("FINAL MISTRAL-ONLY PROCESSING STATISTICS")
    print("="*60)
    print(f"Total Products Processed: {final_stats['total_processed']}")
    print(f"Successful Mappings: {final_stats['successful_mappings']}")
    print(f"Failed Mappings: {final_stats['failed_mappings']}")
    print(f"Need Manual Review: {final_stats['needs_manual_review']}")
    print(f"Success Rate: {final_stats['success_rate']:.2f}%")
    print(f"Review Rate: {final_stats['review_rate']:.2f}%")
    print(f"\nResults exported to: {csv_file}")
    print("="*60)

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

def run_hybrid_processing(args):
    """Run the hybrid processing pipeline (Mistral + OpenAI fallback)"""
    
    # Check OpenAI API key
    if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY == 'your_openai_api_key_here':
        print("Error: OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key in the .env file")
        sys.exit(1)
        
    # Check Mistral API key
    if not Config.MISTRAL_API_KEY or Config.MISTRAL_API_KEY == 'your_mistral_api_key_here':
        print("Error: MISTRAL_API_KEY not found in environment variables")
        print("Please set your Mistral API key in the .env file")
        sys.exit(1)
    
    # Load data
    print("Loading data...")
    data_processor = DataProcessor(args.input_file)
    products_df = data_processor.load_data()
    
    if args.max_products:
        products_df = products_df.head(args.max_products)
        print(f"Limited to {args.max_products} products")
    
    # Initialize hybrid mapping engine
    print("Initializing hybrid mapping engine...")
    hybrid_engine = HybridMappingEngine(Config.OPENAI_API_KEY, Config.MISTRAL_API_KEY)
    
    # Process products
    print("Starting hybrid product mapping...")
    current_idx = args.start_index
    
    while current_idx < len(products_df):
        try:
            batch_results = hybrid_engine.process_batch(
                products_df, 
                current_idx, 
                args.batch_size
            )
            current_idx += args.batch_size
            
            # Show progress
            stats = hybrid_engine.get_statistics()
            print(f"\nProgress Update:")
            print(f"Processed: {stats['total_processed']}/{len(products_df)}")
            print(f"Success Rate: {stats['success_rate']:.1f}%")
            print(f"Direct Mapping Rate: {stats.get('direct_mapping_rate', 0):.1f}%")
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
    csv_file = exporter.export_results(hybrid_engine.results, filename_prefix="hybrid_rxnorm_mapping")
    
    # Final statistics
    final_stats = hybrid_engine.get_statistics()
    print("\n" + "="*60)
    print("FINAL HYBRID PROCESSING STATISTICS")
    print("="*60)
    print(f"Total Products Processed: {final_stats['total_processed']}")
    print(f"Successful Mappings: {final_stats['successful_mappings']}")
    print(f"Failed Mappings: {final_stats['failed_mappings']}")
    print(f"Need Manual Review: {final_stats['needs_manual_review']}")
    print(f"Success Rate: {final_stats['success_rate']:.2f}%")
    print(f"Direct Mapping Rate: {final_stats.get('direct_mapping_rate', 0):.2f}%")
    openai_rate = 100 - final_stats.get('direct_mapping_rate', 0)
    print(f"OpenAI Fallback Rate: {openai_rate:.2f}%")
    print(f"Review Rate: {final_stats['review_rate']:.2f}%")
    print(f"\nResults exported to: {csv_file}")
    print("="*60)

if __name__ == "__main__":
    main()

