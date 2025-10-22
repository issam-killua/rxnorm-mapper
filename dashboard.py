import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy import stats
import seaborn as sns


def create_dashboard():
    """Enhanced RxNorm Mapping Dashboard with improved statistical analysis"""
    st.set_page_config(page_title="RxNorm Mapping Dashboard", layout="wide")
    st.title("💊 RxNorm Mapping Dashboard")

    tabs = st.tabs(["📈 Results Analysis", "📊 Method Comparison", "📋 Statistical Tests", "📑 Dataset Comparison", "🛠️ File Diagnostics"])

    # Sidebar uploaders
    with st.sidebar:
        st.header("📂 Data Upload")
        uploaded_file = st.file_uploader("Upload a single results CSV", type=['csv'])
        st.divider()
        st.header("🔍 Compare Two Methods")
        col1, col2 = st.columns(2)
        with col1:
            direct_file = st.file_uploader("Direct (Mistral) CSV", type=['csv'], key="direct")
        with col2:
            openai_file = st.file_uploader("OpenAI CSV", type=['csv'], key="openai")

    # File Diagnostics Tab
    with tabs[4]:
        st.subheader("📋 File Diagnostics")
        st.write("Use this tab to diagnose issues with your CSV files")
        
        file_to_check = st.file_uploader("Upload a CSV file to diagnose", type=['csv'], key="diagnostics")
        
        if file_to_check:
            st.write("### File Preview")
            
            # Try to read the first few lines directly
            file_to_check.seek(0)
            raw_data = file_to_check.read(2000).decode('utf-8')
            st.text_area("Raw file content (first 2000 bytes):", raw_data, height=200)
            
            # Try different parsing options
            file_to_check.seek(0)
            try:
                # Try with different delimiters
                st.write("### Parsing Attempts")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("Default parsing:")
                    try:
                        file_to_check.seek(0)
                        df = pd.read_csv(file_to_check)
                        st.write(f"Success! Found {len(df)} rows and {len(df.columns)} columns")
                        st.dataframe(df.head(3))
                    except Exception as e:
                        st.error(f"Default parsing failed: {str(e)}")
                
                file_to_check.seek(0)
                with col2:
                    st.write("Semicolon delimiter parsing:")
                    try:
                        df = pd.read_csv(file_to_check, sep=';')
                        st.write(f"Success! Found {len(df)} rows and {len(df.columns)} columns")
                        st.dataframe(df.head(3))
                    except Exception as e:
                        st.error(f"Semicolon parsing failed: {str(e)}")
                
                file_to_check.seek(0)
                st.write("Tab delimiter parsing:")
                try:
                    df = pd.read_csv(file_to_check, sep='\t')
                    st.write(f"Success! Found {len(df)} rows and {len(df.columns)} columns")
                    st.dataframe(df.head(3))
                except Exception as e:
                    st.error(f"Tab parsing failed: {str(e)}")
            
            except Exception as e:
                st.error(f"Diagnostic error: {str(e)}")
        else:
            st.info("Upload a CSV file to diagnose potential issues")

    # Tab 1 - Single Results
    with tabs[0]:
        if uploaded_file:
            try:
                # Create a copy of the file in memory
                file_data = uploaded_file.getvalue()
                
                # Use StringIO to create a file-like object
                import io
                file_obj = io.StringIO(file_data.decode('utf-8'))
                
                # Read the CSV
                df = pd.read_csv(file_obj)
                
                if len(df) > 0:
                    display_single_results(df)
                else:
                    st.error("The uploaded file is empty. Please upload a valid CSV file.")
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
                st.info("Please make sure the uploaded file is a valid CSV file with mapping results.")
                st.info("Try using the File Diagnostics tab to check your file format.")
        else:
            st.info("Upload a results CSV to start the analysis.")

    # Tab 2 - Method Comparison
    with tabs[1]:
        if direct_file and openai_file:
            try:
                # Create copies of the files in memory
                direct_data = direct_file.getvalue()
                openai_data = openai_file.getvalue()
                
                # Use StringIO to create file-like objects
                import io
                direct_obj = io.StringIO(direct_data.decode('utf-8'))
                openai_obj = io.StringIO(openai_data.decode('utf-8'))
                
                # Read the CSVs
                direct_df = pd.read_csv(direct_obj)
                openai_df = pd.read_csv(openai_obj)
                
                if len(direct_df) > 0 and len(openai_df) > 0:
                    display_comparison(direct_df, openai_df)
                else:
                    st.error("One or both of the uploaded files are empty. Please upload valid CSV files.")
            except Exception as e:
                st.error(f"Error reading files: {str(e)}")
                st.info("Please make sure the uploaded files are valid CSV files with mapping results.")
                st.info("Try using the File Diagnostics tab to check your file format.")
        else:
            st.info("Please upload both Direct and OpenAI result files to compare.")

    # Tab 3 - Statistical Tests
    with tabs[2]:
        if direct_file and openai_file:
            try:
                # Create copies of the files in memory
                direct_data = direct_file.getvalue()
                openai_data = openai_file.getvalue()
                
                # Use StringIO to create file-like objects
                import io
                direct_obj = io.StringIO(direct_data.decode('utf-8'))
                openai_obj = io.StringIO(openai_data.decode('utf-8'))
                
                # Read the CSVs
                direct_df = pd.read_csv(direct_obj)
                openai_df = pd.read_csv(openai_obj)
                
                if len(direct_df) > 0 and len(openai_df) > 0:
                    display_statistical_analysis(direct_df, openai_df)
                else:
                    st.error("One or both of the uploaded files are empty. Please upload valid CSV files.")
            except Exception as e:
                st.error(f"Error reading files: {str(e)}")
                st.info("Please make sure the uploaded files are valid CSV files with mapping results.")
                st.info("Try using the File Diagnostics tab to check your file format.")
        else:
            st.info("Please upload both Direct and OpenAI result files for statistical analysis.")
            
    # Tab 4 - Dataset Comparison
    with tabs[3]:
        if direct_file and openai_file:
            try:
                # Create copies of the files in memory
                direct_data = direct_file.getvalue()
                openai_data = openai_file.getvalue()
                
                # Use StringIO to create file-like objects
                import io
                direct_obj = io.StringIO(direct_data.decode('utf-8'))
                openai_obj = io.StringIO(openai_data.decode('utf-8'))
                
                # Read the CSVs
                direct_df = pd.read_csv(direct_obj)
                openai_df = pd.read_csv(openai_obj)
                
                if len(direct_df) > 0 and len(openai_df) > 0:
                    display_dataset_comparison(direct_df, openai_df)
                else:
                    st.error("One or both of the uploaded files are empty. Please upload valid CSV files.")
            except Exception as e:
                st.error(f"Error reading files: {str(e)}")
                st.info("Please make sure the uploaded files are valid CSV files with mapping results.")
                st.info("Try using the File Diagnostics tab to check your file format.")
        else:
            st.info("Please upload both Direct and OpenAI result files for dataset comparison.")


def display_single_results(df):
    """Display analysis for one results file"""
    total = len(df)
    
    # Create a success column if it doesn't exist
    if 'rxnorm_found' in df.columns:
        df['success'] = df['rxnorm_found'].astype(str).str.lower().isin(['true'])
    elif 'final_status' in df.columns:
        df['success'] = df['final_status'].astype(str).str.lower() == 'success'
    else:
        # Create a default success column if neither exists
        st.warning("Could not find rxnorm_found or final_status column in CSV. Using best guess.")
        df['success'] = False  # Default to false
    
    success_count = df['success'].sum()
    success_rate = (success_count / total * 100) if total else 0

    st.header("📊 Results Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Products", total)
    col2.metric("Successful Mappings", success_count)
    col3.metric("Success Rate", f"{success_rate:.1f}%")

    # Pie chart for success/fail
    fig = px.pie(
        names=['Successful', 'Failed'],
        values=[success_count, total - success_count],
        color=['Successful', 'Failed'],
        color_discrete_map={'Successful': '#2ecc71', 'Failed': '#e74c3c'},
        title="Mapping Results"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Success rate by form if available
    if 'original_form' in df.columns:
        st.subheader("Form-wise Success Rate")
        try:
            form_stats = df.groupby('original_form')['success'].agg(['count', 'sum']).reset_index()
            form_stats['success_rate'] = (form_stats['sum'] / form_stats['count'] * 100)
            form_stats = form_stats.sort_values('count', ascending=False).head(10)

            bar = px.bar(
                form_stats, x='original_form', y='success_rate', text='count',
                color='success_rate', color_continuous_scale='RdYlGn',
                title="Success Rate by Form"
            )
            st.plotly_chart(bar, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating form statistics: {str(e)}")

    # TTY distribution if available
    if 'rxnorm_tty' in df.columns:
        st.subheader("RxNorm Term Types (TTY)")
        try:
            successful_df = df[df['success'] == True]
            if len(successful_df) > 0:
                tty_counts = successful_df['rxnorm_tty'].value_counts().reset_index()
                tty_counts.columns = ['Term Type', 'Count']
                
                tty_fig = px.bar(
                    tty_counts, 
                    x='Term Type', 
                    y='Count',
                    color='Count',
                    title="Distribution of RxNorm Term Types"
                )
                st.plotly_chart(tty_fig, use_container_width=True)
            else:
                st.info("No successful mappings with TTY information found.")
        except Exception as e:
            st.error(f"Error generating TTY statistics: {str(e)}")

    st.subheader("Raw Data Preview")
    st.dataframe(df.head(100), use_container_width=True)

def display_comparison(direct_df, openai_df):
    """Compare Direct (Mistral) and OpenAI methods"""
    
    """Compare Direct (Mistral) and OpenAI methods"""
    # Check if the 'rxnorm_found' column exists in direct_df
    if 'rxnorm_found' in direct_df.columns:
        direct_df['success'] = direct_df['rxnorm_found'].astype(str).str.lower().isin(['true'])
    elif 'final_status' in direct_df.columns:
        direct_df['success'] = direct_df['final_status'].astype(str).str.lower() == 'success'
    else:
        # Create a default success column if neither exists
        st.warning("Could not find rxnorm_found or final_status column in Direct CSV. Using best guess.")
        direct_df['success'] = False  # Default to false
    
    # Check if the 'rxnorm_found' column exists in openai_df
    if 'rxnorm_found' in openai_df.columns:
        openai_df['success'] = openai_df['rxnorm_found'].astype(str).str.lower().isin(['true'])
    elif 'final_status' in openai_df.columns:
        openai_df['success'] = openai_df['final_status'].astype(str).str.lower() == 'success'
    else:
        # Create a default success column if neither exists
        st.warning("Could not find rxnorm_found or final_status column in OpenAI CSV. Using best guess.")
        openai_df['success'] = False  # Default to false
    
    # Now that we have a 'success' column in both dataframes, proceed with comparison
    direct_total = len(direct_df)
    openai_total = len(openai_df)
    
    direct_success = direct_df['success'].sum()
    openai_success = openai_df['success'].sum()
    
    direct_rate = (direct_success / direct_total * 100) if direct_total else 0
    openai_rate = (openai_success / openai_total * 100) if openai_total else 0

    # Dataset size and success metrics
    st.header("📊 Dataset Overview")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Direct (Mistral)")
        st.metric("Total Products", direct_total)
        st.metric("Successful Mappings", direct_success)
        st.metric("Success Rate", f"{direct_rate:.1f}%")
    
    with col2:
        st.subheader("OpenAI")
        st.metric("Total Products", openai_total)
        st.metric("Successful Mappings", openai_success)
        st.metric("Success Rate", f"{openai_rate:.1f}%")
    
    # Dataset size comparison
    st.subheader("Dataset Size Comparison")
    dataset_size_data = {
        'Method': ['Direct (Mistral)', 'OpenAI'],
        'Products Processed': [direct_total, openai_total]
    }
    
    fig = px.bar(
        dataset_size_data,
        x='Method',
        y='Products Processed',
        color='Method',
        color_discrete_map={'Direct (Mistral)': '#3498db', 'OpenAI': '#f39c12'},
        text_auto=True,
        title="Number of Products Processed by Each Method"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Success rate comparison
    st.subheader("Success Rate Comparison")
    comp_df = pd.DataFrame({
        'Method': ['Direct (Mistral)', 'OpenAI'],
        'Success Rate (%)': [direct_rate, openai_rate],
        'Successful Mappings': [direct_success, openai_success],
        'Total Products': [direct_total, openai_total]
    })
    
    fig = px.bar(
        comp_df, 
        x='Method', 
        y='Success Rate (%)', 
        color='Method',
        color_discrete_map={'Direct (Mistral)': '#3498db', 'OpenAI': '#f39c12'},
        text_auto=True,
        title="Success Rate Comparison"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Combined success metrics
    st.subheader("Success Metrics")
    success_data = pd.DataFrame({
        'Method': ['Direct (Mistral)', 'OpenAI'],
        'Total Processed': [direct_total, openai_total],
        'Successful': [direct_success, openai_success],
        'Failed': [direct_total - direct_success, openai_total - openai_success],
        'Success Rate (%)': [direct_rate, openai_rate]
    })
    
    fig = px.bar(
        success_data,
        x='Method',
        y=['Successful', 'Failed'],
        color_discrete_map={'Successful': '#2ecc71', 'Failed': '#e74c3c'},
        barmode='stack',
        title="Success vs. Failure Count",
        text_auto=True
    )
    fig.update_layout(legend_title_text="Result")
    st.plotly_chart(fig, use_container_width=True)

    # Common product comparison
    if {'original_code'} <= set(direct_df.columns) & set(openai_df.columns):
        merged = pd.merge(
            direct_df[['original_code', 'success']],
            openai_df[['original_code', 'success']],
            on='original_code', suffixes=('_direct', '_openai')
        )
        
        total_common = len(merged)
        both_success = ((merged['success_direct']) & (merged['success_openai'])).sum()
        both_fail = ((~merged['success_direct']) & (~merged['success_openai'])).sum()
        direct_only = ((merged['success_direct']) & (~merged['success_openai'])).sum()
        openai_only = ((~merged['success_direct']) & (merged['success_openai'])).sum()

        # Common product metrics
        st.header("🔄 Common Product Analysis")
        st.write(f"Found {total_common} products processed by both methods")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Both Successful", both_success, f"{both_success/total_common*100:.1f}%")
        col2.metric("Both Failed", both_fail, f"{both_fail/total_common*100:.1f}%")
        col3.metric("Direct Only", direct_only, f"{direct_only/total_common*100:.1f}%")
        col4.metric("OpenAI Only", openai_only, f"{openai_only/total_common*100:.1f}%")
        
        # Pie chart for common products
        pie_df = pd.DataFrame({
            'Category': ['Both Successful', 'Both Failed', 'Direct Only', 'OpenAI Only'],
            'Count': [both_success, both_fail, direct_only, openai_only],
            'Percentage': [
                both_success/total_common*100, 
                both_fail/total_common*100,
                direct_only/total_common*100,
                openai_only/total_common*100
            ]
        })
        
        pie = px.pie(
            pie_df, 
            values='Count', 
            names='Category', 
            title=f"Common Product Outcomes ({total_common} products)",
            hover_data=['Percentage'],
            color='Category',
            color_discrete_map={
                'Both Successful': '#2ecc71',
                'Both Failed': '#e74c3c',
                'Direct Only': '#3498db',
                'OpenAI Only': '#f39c12'
            }
        )
        st.plotly_chart(pie, use_container_width=True)
        
        # Display contingency table
        st.subheader("📋 Contingency Table")
        contingency_df = pd.DataFrame({
            'OpenAI Success': [both_success, direct_only],
            'OpenAI Failure': [openai_only, both_fail]
        }, index=['Direct Success', 'Direct Failure'])
        st.dataframe(contingency_df)
        
        # Unique coverage visualization
        st.subheader("Unique Contributions")
        unique_data = pd.DataFrame({
            'Method': ['Direct Only', 'OpenAI Only', 'Both Methods'],
            'Successful Products': [direct_only, openai_only, both_success]
        })
        
        fig = px.bar(
            unique_data,
            x='Method',
            y='Successful Products',
            color='Method',
            color_discrete_map={
                'Direct Only': '#3498db', 
                'OpenAI Only': '#f39c12',
                'Both Methods': '#2ecc71'
            },
            text_auto=True,
            title="Unique Successful Mappings by Method"
        )
        st.plotly_chart(fig, use_container_width=True)

def display_statistical_analysis(direct_df, openai_df):
    """Perform detailed statistical analysis between the two methods"""
    st.header("📊 Statistical Analysis")
    
    # Prepare data - add 'success' column if it doesn't exist
    # Check if the 'rxnorm_found' column exists in direct_df
    if 'rxnorm_found' in direct_df.columns:
        direct_df['success'] = direct_df['rxnorm_found'].astype(str).str.lower().isin(['true'])
    elif 'final_status' in direct_df.columns:
        direct_df['success'] = direct_df['final_status'].astype(str).str.lower() == 'success'
    else:
        # Create a default success column if neither exists
        st.warning("Could not find rxnorm_found or final_status column in Direct CSV. Using best guess.")
        direct_df['success'] = False  # Default to false
    
    # Check if the 'rxnorm_found' column exists in openai_df
    if 'rxnorm_found' in openai_df.columns:
        openai_df['success'] = openai_df['rxnorm_found'].astype(str).str.lower().isin(['true'])
    elif 'final_status' in openai_df.columns:
        openai_df['success'] = openai_df['final_status'].astype(str).str.lower() == 'success'
    else:
        # Create a default success column if neither exists
        st.warning("Could not find rxnorm_found or final_status column in OpenAI CSV. Using best guess.")
        openai_df['success'] = False  # Default to false
    
    # Find common products
    if {'original_code'} <= set(direct_df.columns) & set(openai_df.columns):
        try:
            merged = pd.merge(
                direct_df[['original_code', 'success']],
                openai_df[['original_code', 'success']],
                on='original_code', suffixes=('_direct', '_openai')
            )
            
            total_common = len(merged)
            both_success = ((merged['success_direct']) & (merged['success_openai'])).sum()
            both_fail = ((~merged['success_direct']) & (~merged['success_openai'])).sum()
            direct_only = ((merged['success_direct']) & (~merged['success_openai'])).sum()
            openai_only = ((~merged['success_direct']) & (merged['success_openai'])).sum()
            
            st.subheader("McNemar's Test")
            st.write("""
            McNemar's test is used to determine if there is a significant difference between two methods
            on the same sample. It's particularly useful for assessing whether one mapping approach 
            systematically outperforms the other.
            """)
            
            # Display contingency table
            contingency = np.array([[both_success, direct_only], [openai_only, both_fail]])
            st.write("Contingency Table:")
            st.write(pd.DataFrame(
                contingency, 
                columns=['OpenAI Success', 'OpenAI Failure'],
                index=['Direct Success', 'Direct Failure']
            ))
            
            # Perform McNemar's test
            try:
                # We care about the discordant pairs (direct_only and openai_only)
                chi2 = (abs(direct_only - openai_only) - 1)**2 / (direct_only + openai_only) if (direct_only + openai_only) > 0 else 0
                p_value = stats.chi2.sf(chi2, 1)
                
                col1, col2 = st.columns(2)
                col1.metric("McNemar's Chi2", f"{chi2:.3f}")
                col2.metric("p-value", f"{p_value:.4f}")
                
                alpha = 0.05
                if p_value < alpha:
                    if direct_only > openai_only:
                        st.success(f"Direct method statistically outperforms OpenAI (p={p_value:.4f})")
                    else:
                        st.success(f"OpenAI statistically outperforms Direct method (p={p_value:.4f})")
                else:
                    st.info(f"No statistically significant difference between methods (p={p_value:.4f})")
            except Exception as e:
                st.warning(f"Could not perform McNemar's test - {str(e)}")
            
            # Concordance analysis
            st.subheader("Concordance Analysis")
            
            total_agreement = (both_success + both_fail) / total_common * 100
            st.metric("Overall Agreement", f"{total_agreement:.1f}%", 
                     help="Percentage of products where both methods arrived at the same result (success or failure)")
            
            # Calculate Cohen's Kappa
            try:
                observed_agreement = (both_success + both_fail) / total_common
                expected_agreement = (
                    ((both_success + direct_only) * (both_success + openai_only)) + 
                    ((openai_only + both_fail) * (direct_only + both_fail))
                ) / (total_common * total_common)
                
                kappa = (observed_agreement - expected_agreement) / (1 - expected_agreement)
                
                # Interpret kappa
                if kappa < 0:
                    kappa_interpretation = "Poor agreement (worse than random)"
                elif kappa < 0.2:
                    kappa_interpretation = "Slight agreement"
                elif kappa < 0.4:
                    kappa_interpretation = "Fair agreement"
                elif kappa < 0.6:
                    kappa_interpretation = "Moderate agreement"
                elif kappa < 0.8:
                    kappa_interpretation = "Substantial agreement"
                else:
                    kappa_interpretation = "Almost perfect agreement"
                    
                st.metric("Cohen's Kappa", f"{kappa:.3f}", kappa_interpretation, 
                         help="Measures agreement beyond what would be expected by chance alone")
            except Exception as e:
                st.warning(f"Could not calculate Cohen's Kappa - {str(e)}")
            
            # Analyze by form if available
            if 'original_form' in direct_df.columns and 'original_form' in openai_df.columns:
                st.subheader("Statistical Analysis by Form")
                
                try:
                    # Get success rates for common forms
                    direct_df['form_success'] = direct_df['success'].astype(int)
                    openai_df['form_success'] = openai_df['success'].astype(int)
                    
                    direct_by_form = direct_df.groupby('original_form')['form_success'].agg(['count', 'sum', 'mean'])
                    openai_by_form = openai_df.groupby('original_form')['form_success'].agg(['count', 'sum', 'mean'])
                    
                    # Merge and find forms with enough data for comparison
                    forms_merged = pd.merge(
                        direct_by_form, openai_by_form,
                        left_index=True, right_index=True,
                        suffixes=('_direct', '_openai')
                    )
                    
                    forms_merged = forms_merged[forms_merged['count_direct'] >= 5]
                    forms_merged = forms_merged[forms_merged['count_openai'] >= 5]
                    
                    # Calculate proportions test (z-test) for each form
                    results = []
                    for form, row in forms_merged.iterrows():
                        direct_success = row['sum_direct']
                        direct_total = row['count_direct']
                        openai_success = row['sum_openai']
                        openai_total = row['count_openai']
                        
                        if direct_total > 0 and openai_total > 0:
                            direct_rate = direct_success / direct_total
                            openai_rate = openai_success / openai_total
                            diff = openai_rate - direct_rate
                            
                            # Calculate standard error and z-score
                            pooled_prop = (direct_success + openai_success) / (direct_total + openai_total)
                            se = np.sqrt(pooled_prop * (1 - pooled_prop) * (1/direct_total + 1/openai_total))
                            
                            if se > 0:
                                z = diff / se
                                p = 2 * (1 - stats.norm.cdf(abs(z)))
                                
                                results.append({
                                    'Form': form,
                                    'Direct Rate': direct_rate * 100,
                                    'OpenAI Rate': openai_rate * 100,
                                    'Difference': diff * 100,
                                    'Z-Score': z,
                                    'P-Value': p,
                                    'Significant': p < 0.05,
                                    'Better Method': 'OpenAI' if diff > 0 else 'Direct' if diff < 0 else 'Tie',
                                    'Sample Size': direct_total + openai_total
                                })
                    
                    if results:
                        results_df = pd.DataFrame(results)
                        results_df = results_df.sort_values('P-Value')
                        
                        # Filter to significant findings
                        sig_results = results_df[results_df['Significant']]
                        if not sig_results.empty:
                            st.write(f"Forms with statistically significant performance differences:")
                            
                            # Format the table
                            display_df = sig_results.copy()
                            display_df['Direct Rate'] = display_df['Direct Rate'].round(1).astype(str) + '%'
                            display_df['OpenAI Rate'] = display_df['OpenAI Rate'].round(1).astype(str) + '%'
                            display_df['Difference'] = display_df['Difference'].round(1).astype(str) + '%'
                            display_df['P-Value'] = display_df['P-Value'].round(4)
                            
                            st.dataframe(
                                display_df[['Form', 'Direct Rate', 'OpenAI Rate', 'Difference', 'P-Value', 'Better Method', 'Sample Size']], 
                                use_container_width=True
                            )
                        else:
                            st.info("No pharmaceutical forms show statistically significant differences between methods.")
                    else:
                        st.warning("Insufficient data for statistical comparison by form")
                except Exception as e:
                    st.error(f"Error in form analysis: {str(e)}")
                    
            # Decision tree: When to use which method
            st.subheader("📋 Decision Guide: When to Use Each Method")
            
            try:
                if direct_only > 10 and openai_only > 10:
                    # If we have enough data to make recommendations
                    st.write("Based on the analysis, here's a guide for choosing between Direct (Mistral) and OpenAI methods:")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### Use Direct (Mistral) Method When:")
                        direct_better_conditions = []
                        
                        # Overall performance recommendations
                        if direct_only > openai_only and p_value < 0.05:
                            direct_better_conditions.append("- **Higher overall success rate** across all products")
                        
                        # Processing scale considerations
                        direct_better_conditions.append("- **Processing large datasets** is a priority (proven to handle 5,900+ products)")
                        
                        # Speed considerations
                        direct_better_conditions.append("- **Processing speed** is important (typically faster)")
                        
                        # Form-specific recommendations
                        if 'original_form' in direct_df.columns and 'original_form' in openai_df.columns:
                            try:
                                form_results = pd.DataFrame(results)
                                direct_better_forms = form_results[
                                    (form_results['Better Method'] == 'Direct') & 
                                    (form_results['Significant']) & 
                                    (form_results['Sample Size'] >= 10)
                                ]
                                
                                if len(direct_better_forms) > 0:
                                    direct_better_conditions.append("- **Product forms:** " + 
                                                                ", ".join(direct_better_forms['Form'].head(5)))
                            except:
                                pass
                        
                        # Add default if no conditions
                        if not direct_better_conditions:
                            direct_better_conditions.append("- Batch processing of large datasets")
                            direct_better_conditions.append("- Simpler pharmaceutical products")
                        
                        for condition in direct_better_conditions:
                            st.markdown(condition)
                    
                    with col2:
                        st.markdown("#### Use OpenAI Method When:")
                        openai_better_conditions = []
                        
                        # Overall performance recommendations
                        if openai_only > direct_only and p_value < 0.05:
                            openai_better_conditions.append("- **Higher overall success rate** across all products")
                        
                        # Complex product considerations
                        openai_better_conditions.append("- **Complex products** with multiple ingredients")
                        openai_better_conditions.append("- **Unusual formulations** that need context interpretation")
                        
                        # Form-specific recommendations
                        if 'original_form' in direct_df.columns and 'original_form' in openai_df.columns:
                            try:
                                form_results = pd.DataFrame(results)
                                openai_better_forms = form_results[
                                    (form_results['Better Method'] == 'OpenAI') & 
                                    (form_results['Significant']) & 
                                    (form_results['Sample Size'] >= 10)
                                ]
                                
                                if len(openai_better_forms) > 0:
                                    openai_better_conditions.append("- **Product forms:** " + 
                                                                ", ".join(openai_better_forms['Form'].head(5)))
                            except:
                                pass
                        
                        # Add default if no conditions
                        if not openai_better_conditions:
                            openai_better_conditions.append("- Products requiring deep contextual understanding")
                            openai_better_conditions.append("- When highest possible success rate is critical")
                        
                        for condition in openai_better_conditions:
                            st.markdown(condition)
                    
                    # Hybrid approach recommendation
                    st.markdown("#### 🔄 Consider a Hybrid Approach")
                    st.markdown("""
                    For optimal results, consider using both methods strategically:
                    1. Start with the Direct (Mistral) method for all products
                    2. For failed mappings, use OpenAI as a fallback
                    3. For specific forms where one method significantly outperforms, use that method first
                    """)
                else:
                    st.info("Process more products with both methods to get method selection recommendations")
            except Exception as e:
                st.error(f"Error generating decision guide: {str(e)}")
        except Exception as e:
            st.error(f"Error performing statistical analysis: {str(e)}")
            st.info("Make sure your CSV files have compatible structures and contain an 'original_code' column.")
    else:
        st.warning("Cannot perform statistical analysis - missing the 'original_code' column in one or both datasets.")

def display_dataset_comparison(direct_df, openai_df):
    """Compare the datasets processed by each method"""
    st.header("📊 Dataset Comparison")
    
    direct_total = len(direct_df)
    openai_total = len(openai_df)
    
    # Overview metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Direct Dataset Size", direct_total)
    with col2:
        st.metric("OpenAI Dataset Size", openai_total)
    
    # Size comparison visualization
    st.subheader("Dataset Size Comparison")
    fig = px.bar(
        x=['Direct (Mistral)', 'OpenAI'],
        y=[direct_total, openai_total],
        color=['Direct (Mistral)', 'OpenAI'],
        color_discrete_map={'Direct (Mistral)': '#3498db', 'OpenAI': '#f39c12'},
        labels={'x': 'Method', 'y': 'Number of Products'},
        text_auto=True,
        title="Total Products Processed by Each Method"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Common vs Unique products
    if {'original_code'} <= set(direct_df.columns) & set(openai_df.columns):
        common_products = set(direct_df['original_code']) & set(openai_df['original_code'])
        direct_only_products = set(direct_df['original_code']) - set(openai_df['original_code'])
        openai_only_products = set(openai_df['original_code']) - set(direct_df['original_code'])
        
        st.subheader("Dataset Overlap Analysis")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Common Products", len(common_products))
        col2.metric("Direct-only Products", len(direct_only_products))
        col3.metric("OpenAI-only Products", len(openai_only_products))
        
        # Venn diagram-like visualization
        overlap_data = pd.DataFrame([
            {'Category': 'Direct Only', 'Count': len(direct_only_products)},
            {'Category': 'Common', 'Count': len(common_products)},
            {'Category': 'OpenAI Only', 'Count': len(openai_only_products)}
        ])
        
        fig = px.bar(
            overlap_data,
            x='Category',
            y='Count',
            color='Category',
            color_discrete_map={
                'Direct Only': '#3498db',
                'Common': '#2ecc71',
                'OpenAI Only': '#f39c12'
            },
            text_auto=True,
            title="Product Distribution Between Methods"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Pie chart visualization
        pie_data = pd.DataFrame([
            {'Category': 'Common', 'Count': len(common_products)},
            {'Category': 'Direct Only', 'Count': len(direct_only_products)},
            {'Category': 'OpenAI Only', 'Count': len(openai_only_products)}
        ])
        
        fig = px.pie(
            pie_data,
            values='Count',
            names='Category',
            color='Category',
            color_discrete_map={
                'Direct Only': '#3498db',
                'Common': '#2ecc71',
                'OpenAI Only': '#f39c12'
            },
            title="Dataset Overlap"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Form distribution comparison
    if 'original_form' in direct_df.columns and 'original_form' in openai_df.columns:
        st.subheader("Pharmaceutical Form Distribution")
        
        direct_forms = direct_df['original_form'].value_counts().reset_index()
        direct_forms.columns = ['Form', 'Count']
        direct_forms['Method'] = 'Direct (Mistral)'
        direct_forms = direct_forms.sort_values('Count', ascending=False).head(10)
        
        openai_forms = openai_df['original_form'].value_counts().reset_index()
        openai_forms.columns = ['Form', 'Count']
        openai_forms['Method'] = 'OpenAI'
        openai_forms = openai_forms.sort_values('Count', ascending=False).head(10)
        
        # Combine and visualize top forms
        top_forms = pd.concat([direct_forms, openai_forms])
        
        fig = px.bar(
            top_forms,
            x='Form',
            y='Count',
            color='Method',
            color_discrete_map={
                'Direct (Mistral)': '#3498db', 
                'OpenAI': '#f39c12'
            },
            barmode='group',
            text_auto=True,
            title="Top Pharmaceutical Forms by Method"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Common forms comparison
        st.subheader("Common Forms Success Rate Comparison")
        
        # Get success rates for common forms
        direct_form_success = direct_df.groupby('original_form')['success'].agg(['count', 'sum']).reset_index()
        direct_form_success['success_rate'] = direct_form_success['sum'] / direct_form_success['count'] * 100
        direct_form_success = direct_form_success.rename(
            columns={'count': 'direct_count', 'sum': 'direct_success', 'success_rate': 'direct_rate'})
        
        openai_form_success = openai_df.groupby('original_form')['success'].agg(['count', 'sum']).reset_index()
        openai_form_success['success_rate'] = openai_form_success['sum'] / openai_form_success['count'] * 100
        openai_form_success = openai_form_success.rename(
            columns={'count': 'openai_count', 'sum': 'openai_success', 'success_rate': 'openai_rate'})
        
        # Find common forms
        common_forms = pd.merge(
            direct_form_success[['original_form', 'direct_count', 'direct_rate']],
            openai_form_success[['original_form', 'openai_count', 'openai_rate']],
            on='original_form'
        )
        
        # Filter to forms with enough data
        common_forms = common_forms[(common_forms['direct_count'] >= 5) & (common_forms['openai_count'] >= 5)]
        common_forms['rate_diff'] = common_forms['openai_rate'] - common_forms['direct_rate']
        common_forms['total_count'] = common_forms['direct_count'] + common_forms['openai_count']
        common_forms = common_forms.sort_values('total_count', ascending=False).head(10)
        
        if not common_forms.empty:
            # Create comparison chart
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=common_forms['original_form'],
                y=common_forms['direct_rate'],
                name='Direct (Mistral)',
                marker_color='#3498db',
                text=common_forms['direct_count'],
                textposition='auto'
            ))
            
            fig.add_trace(go.Bar(
                x=common_forms['original_form'],
                y=common_forms['openai_rate'],
                name='OpenAI',
                marker_color='#f39c12',
                text=common_forms['openai_count'],
                textposition='auto'
            ))
            
            fig.update_layout(
                barmode='group',
                title="Success Rate Comparison for Common Forms (numbers show sample size)",
                xaxis_title="Pharmaceutical Form",
                yaxis_title="Success Rate (%)",
                legend_title="Method"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show forms with biggest differences
            st.subheader("Forms with Largest Success Rate Differences")
            
            common_forms_sorted = common_forms.sort_values('rate_diff', ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("OpenAI performs better:")
                better_openai = common_forms_sorted[common_forms_sorted['rate_diff'] > 0].head(5)
                if not better_openai.empty:
                    better_openai_display = better_openai.copy()
                    better_openai_display['direct_rate'] = better_openai_display['direct_rate'].round(1).astype(str) + '%'
                    better_openai_display['openai_rate'] = better_openai_display['openai_rate'].round(1).astype(str) + '%'
                    better_openai_display['rate_diff'] = better_openai_display['rate_diff'].round(1).astype(str) + '%'
                    
                    st.dataframe(better_openai_display[['original_form', 'direct_rate', 'openai_rate', 'rate_diff', 'total_count']])
                else:
                    st.write("No forms where OpenAI performs better")
            
            with col2:
                st.write("Direct performs better:")
                better_direct = common_forms_sorted[common_forms_sorted['rate_diff'] < 0].tail(5).sort_values('rate_diff')
                if not better_direct.empty:
                    better_direct_display = better_direct.copy()
                    better_direct_display['direct_rate'] = better_direct_display['direct_rate'].round(1).astype(str) + '%'
                    better_direct_display['openai_rate'] = better_direct_display['openai_rate'].round(1).astype(str) + '%'
                    better_direct_display['rate_diff'] = better_direct_display['rate_diff'].round(1).astype(str) + '%'
                    
                    st.dataframe(better_direct_display[['original_form', 'direct_rate', 'openai_rate', 'rate_diff', 'total_count']])
                else:
                    st.write("No forms where Direct performs better")
        else:
            st.info("Insufficient data to compare common pharmaceutical forms")

if __name__ == "__main__":
    create_dashboard()