import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy import stats
import seaborn as sns
import re


def create_dashboard():
    """Enhanced RxNorm Mapping Dashboard with hierarchy-aware comparison and improved error handling"""
    st.set_page_config(page_title="RxNorm Mapping Dashboard", layout="wide")
    st.title("💊 RxNorm Mapping Dashboard")

    tabs = st.tabs(["📈 Results Analysis", "📊 Method Comparison", "📋 Statistical Tests", 
                   "📑 Dataset Comparison", "🔍 Matched Products Analysis", 
                   "🧩 Hierarchy Analysis", "🛠️ File Diagnostics"])

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
    with tabs[6]:
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
                        st.write("### Column Names:")
                        st.write(", ".join(df.columns.tolist()))
                    except Exception as e:
                        st.error(f"Default parsing failed: {str(e)}")
                
                file_to_check.seek(0)
                with col2:
                    st.write("Semicolon delimiter parsing:")
                    try:
                        df = pd.read_csv(file_to_check, sep=';')
                        st.write(f"Success! Found {len(df)} rows and {len(df.columns)} columns")
                        st.dataframe(df.head(3))
                        st.write("### Column Names:")
                        st.write(", ".join(df.columns.tolist()))
                    except Exception as e:
                        st.error(f"Semicolon parsing failed: {str(e)}")
                
                file_to_check.seek(0)
                st.write("Tab delimiter parsing:")
                try:
                    df = pd.read_csv(file_to_check, sep='\t')
                    st.write(f"Success! Found {len(df)} rows and {len(df.columns)} columns")
                    st.dataframe(df.head(3))
                    st.write("### Column Names:")
                    st.write(", ".join(df.columns.tolist()))
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
                st.error(f"Error in dataset comparison: {str(e)}")
                st.info("Please make sure the uploaded files are valid CSV files with mapping results.")
                st.info("Try using the File Diagnostics tab to check your file format.")
        else:
            st.info("Please upload both Direct and OpenAI result files to compare datasets.")

    # Tab 5 - Matched Products Analysis
    with tabs[4]:
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
                    display_matched_products_analysis(direct_df, openai_df)
                else:
                    st.error("One or both of the uploaded files are empty. Please upload valid CSV files.")
            except Exception as e:
                st.error(f"Error in matched products analysis: {str(e)}")
                st.info("Please make sure the uploaded files are valid CSV files with mapping results.")
                st.info("Try using the File Diagnostics tab to check your file format.")
        else:
            st.info("Please upload both Direct and OpenAI result files to analyze matched products.")

    # Tab 6 - RxNorm Hierarchy Analysis (NEW)
    with tabs[5]:
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
                    display_hierarchy_analysis(direct_df, openai_df)
                else:
                    st.error("One or both of the uploaded files are empty. Please upload valid CSV files.")
            except Exception as e:
                st.error(f"Error in hierarchy analysis: {str(e)}")
                st.info("Please make sure the uploaded files are valid CSV files with mapping results.")
                st.info("Try using the File Diagnostics tab to check your file format.")
        else:
            st.info("Please upload both Direct and OpenAI result files for hierarchy analysis.")

def standardize_column_names(df):
    """Standardize column names across different datasets"""
    # Create a copy to avoid modifying the original dataframe
    standardized_df = df.copy()
    
    # Create a mapping of possible column name variations to standard names
    column_mapping = {
        # Success indicators
        'final_status': 'final_status',
        'rxnorm_found': 'rxnorm_found',
        'is_success': 'success',
        'success': 'success',
        
        # RxNorm information
        'rxcui': 'rxnorm_rxcui',
        'rxnorm_rxcui': 'rxnorm_rxcui',
        'rx_cui': 'rxnorm_rxcui',
        'rxnorm_cui': 'rxnorm_rxcui',
        'cui': 'rxnorm_rxcui',
        
        'name': 'rxnorm_name',
        'rxname': 'rxnorm_name',
        'rxnorm_name': 'rxnorm_name',
        'rx_name': 'rxnorm_name',
        
        'tty': 'rxnorm_tty',
        'rxnorm_tty': 'rxnorm_tty',
        'term_type': 'rxnorm_tty',
        'rx_tty': 'rxnorm_tty',
        
        # Product information
        'product_name': 'original_product_name',
        'original_product_name': 'original_product_name',
        'med_name': 'original_product_name',
        
        'form': 'original_form',
        'original_form': 'original_form',
        'med_form': 'original_form',
        'dosage_form': 'original_form',
        
        'code': 'original_code',
        'original_code': 'original_code',
        'product_code': 'original_code',
        'med_code': 'original_code',
        
        'dci': 'original_dci',
        'original_dci': 'original_dci',
        'ingredient': 'original_dci',
    }
    
    # Check each column and standardize if needed
    for col in standardized_df.columns:
        col_lower = col.lower()
        for variant, standard in column_mapping.items():
            if col_lower == variant.lower():
                standardized_df.rename(columns={col: standard}, inplace=True)
                break
    
    # Add success flag if not present
    if 'success' not in standardized_df.columns:
        if 'final_status' in standardized_df.columns:
            standardized_df['success'] = standardized_df['final_status'].str.lower() == 'success'
        elif 'rxnorm_found' in standardized_df.columns:
            standardized_df['success'] = standardized_df['rxnorm_found'].astype(bool)
    
    return standardized_df

def display_single_results(df):
    """Display analysis for a single results file"""
    
    # Standardize column names
    df = standardize_column_names(df)
    
    st.subheader("📊 Results Overview")
    
    # Add success flag if not present
    if 'success' not in df.columns:
        st.warning("Could not determine success status from file columns. Using default success rate of 0%.")
        df['success'] = False
    
    # Success rate
    success_count = df['success'].sum()
    total_count = len(df)
    success_rate = success_count / total_count * 100 if total_count > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Products", total_count)
    col2.metric("Successful Mappings", success_count)
    col3.metric("Success Rate", f"{success_rate:.1f}%")
    
    # Success rate visualization
    success_data = pd.DataFrame({
        'Status': ['Success', 'Failed'],
        'Count': [success_count, total_count - success_count]
    })
    
    fig = px.pie(
        success_data, 
        values='Count', 
        names='Status',
        color='Status',
        color_discrete_map={'Success': '#2ecc71', 'Failed': '#e74c3c'},
        title="Mapping Success Rate"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Analyze TTY distribution if available
    if 'rxnorm_tty' in df.columns:
        st.subheader("📋 RxNorm Term Type (TTY) Analysis")
        
        try:
            # Filter to successful mappings
            successful_df = df[df['success'] == True]
            
            if len(successful_df) > 0 and 'rxnorm_tty' in successful_df.columns and successful_df['rxnorm_tty'].notna().any():
                # Count TTYs
                tty_counts = successful_df['rxnorm_tty'].value_counts().reset_index()
                tty_counts.columns = ['Term Type', 'Count']
                
                # Add descriptions for common TTYs
                tty_descriptions = {
                    'SCD': 'Semantic Clinical Drug (generic)',
                    'SBD': 'Semantic Branded Drug',
                    'GPCK': 'Generic Pack',
                    'BPCK': 'Brand Name Pack',
                    'IN': 'Ingredient',
                    'PIN': 'Precise Ingredient',
                    'MIN': 'Multiple Ingredients',
                    'BN': 'Brand Name',
                    'SCDC': 'Semantic Clinical Drug Component',
                    'SCDF': 'Semantic Clinical Drug Form',
                    'SCDG': 'Semantic Clinical Drug Group',
                    'DF': 'Dose Form',
                    'SBDC': 'Semantic Branded Drug Component',
                    'SBDF': 'Semantic Branded Drug Form',
                    'SBDG': 'Semantic Branded Drug Group'
                }
                
                # Add descriptions to the dataframe
                tty_counts['Description'] = tty_counts['Term Type'].map(tty_descriptions)
                
                # Display TTY distribution
                fig = px.bar(
                    tty_counts,
                    x='Term Type',
                    y='Count',
                    title="RxNorm Term Type Distribution",
                    text_auto=True,
                    hover_data=['Description']
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Display TTY descriptions
                with st.expander("RxNorm Term Type (TTY) Descriptions"):
                    desc_df = pd.DataFrame(list(tty_descriptions.items()), columns=['TTY', 'Description'])
                    st.dataframe(desc_df)
            else:
                st.info("No Term Type (TTY) data available for successful mappings.")
        except Exception as e:
            st.error(f"Error analyzing TTY distribution: {str(e)}")
    
    # Analyze forms if available
    if 'original_form' in df.columns:
        st.subheader("📋 Pharmaceutical Form Analysis")
        
        try:
            if df['original_form'].notna().any():
                # Top forms
                top_forms = df['original_form'].value_counts().reset_index()
                top_forms.columns = ['Form', 'Count']
                top_forms = top_forms.head(10)
                
                fig = px.bar(
                    top_forms,
                    x='Form',
                    y='Count',
                    title="Top 10 Pharmaceutical Forms",
                    text_auto=True
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Success rate by form
                form_success = df.groupby('original_form')['success'].agg(['count', 'sum']).reset_index()
                form_success['success_rate'] = form_success['sum'] / form_success['count'] * 100
                form_success = form_success.sort_values('count', ascending=False).head(10)
                
                fig = px.bar(
                    form_success,
                    x='original_form',
                    y='success_rate',
                    title="Success Rate by Pharmaceutical Form (Top 10 by Frequency)",
                    labels={'original_form': 'Form', 'success_rate': 'Success Rate (%)'},
                    text=form_success['count'],
                    color='success_rate',
                    color_continuous_scale='RdYlGn'
                )
                fig.update_traces(textposition='auto')
                fig.update_layout(
                    yaxis_range=[0, 100],
                    coloraxis_showscale=False
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No pharmaceutical form data available for analysis.")
        except Exception as e:
            st.error(f"Error analyzing forms: {str(e)}")
    
    # View raw results
    with st.expander("🔍 View Raw Results"):
        st.dataframe(df)

def display_comparison(direct_df, openai_df):
    """Display comparison between Direct and OpenAI mapping results"""
    
    # Standardize column names
    direct_df = standardize_column_names(direct_df)
    openai_df = standardize_column_names(openai_df)
    
    st.subheader("📊 Method Comparison")
    
    # Check if success column is available
    if 'success' not in direct_df.columns:
        st.warning("Could not determine success status for Direct dataset. Using default success rate of 0%.")
        direct_df['success'] = False
    
    if 'success' not in openai_df.columns:
        st.warning("Could not determine success status for OpenAI dataset. Using default success rate of 0%.")
        openai_df['success'] = False
    
    # Calculate overall stats
    direct_success = direct_df['success'].sum()
    direct_total = len(direct_df)
    direct_rate = direct_success / direct_total * 100 if direct_total > 0 else 0
    
    openai_success = openai_df['success'].sum()
    openai_total = len(openai_df)
    openai_rate = openai_success / openai_total * 100 if openai_total > 0 else 0
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Direct Method")
        st.metric("Total Products", direct_total)
        st.metric("Successful Mappings", direct_success)
        st.metric("Success Rate", f"{direct_rate:.1f}%")
    
    with col2:
        st.subheader("OpenAI Method")
        st.metric("Total Products", openai_total)
        st.metric("Successful Mappings", openai_success)
        st.metric("Success Rate", f"{openai_rate:.1f}%")
    
    with col3:
        st.subheader("Difference")
        st.metric("Dataset Size Difference", openai_total - direct_total)
        st.metric("Success Count Difference", openai_success - direct_success)
        st.metric("Success Rate Difference", f"{openai_rate - direct_rate:.1f}%")
    
    # Visualization
    comparison_data = pd.DataFrame({
        'Method': ['Direct', 'OpenAI'],
        'Success Rate': [direct_rate, openai_rate]
    })
    
    fig = px.bar(
        comparison_data,
        x='Method',
        y='Success Rate',
        color='Method',
        color_discrete_map={'Direct': '#3498db', 'OpenAI': '#f39c12'},
        title="Success Rate Comparison",
        text_auto=True,
        labels={'Method': 'Mapping Method', 'Success Rate': 'Success Rate (%)'}
    )
    
    fig.update_traces(textposition='outside')
    fig.update_layout(yaxis_range=[0, 100])
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Success/Failure visualization
    success_data = pd.DataFrame({
        'Status': ['Success', 'Failed'],
        'Direct': [direct_success, direct_total - direct_success],
        'OpenAI': [openai_success, openai_total - openai_success]
    })
    
    success_data_melted = pd.melt(
        success_data,
        id_vars='Status',
        var_name='Method',
        value_name='Count'
    )
    
    fig = px.bar(
        success_data_melted,
        x='Method',
        y='Count',
        color='Status',
        barmode='stack',
        color_discrete_map={'Success': '#2ecc71', 'Failed': '#e74c3c'},
        title="Success vs. Failure Count by Method",
        text_auto=True
    )
    
    fig.update_traces(textposition='auto')
    st.plotly_chart(fig, use_container_width=True)

    # TTY Distribution Comparison if available
    try:
        if ('rxnorm_tty' in direct_df.columns and 'rxnorm_tty' in openai_df.columns and
            direct_df['rxnorm_tty'].notna().any() and openai_df['rxnorm_tty'].notna().any()):
            
            st.subheader("RxNorm Term Type (TTY) Comparison")
            
            # Filter to successful mappings
            direct_success_df = direct_df[direct_df['success'] == True]
            openai_success_df = openai_df[openai_df['success'] == True]
            
            if len(direct_success_df) > 0 and len(openai_success_df) > 0:
                # Count TTYs for Direct
                direct_tty_counts = direct_success_df['rxnorm_tty'].value_counts().reset_index()
                direct_tty_counts.columns = ['Term Type', 'Count']
                direct_tty_counts['Method'] = 'Direct'
                
                # Count TTYs for OpenAI
                openai_tty_counts = openai_success_df['rxnorm_tty'].value_counts().reset_index()
                openai_tty_counts.columns = ['Term Type', 'Count']
                openai_tty_counts['Method'] = 'OpenAI'
                
                # Combine and visualize
                all_tty_counts = pd.concat([direct_tty_counts, openai_tty_counts])
                
                fig = px.bar(
                    all_tty_counts,
                    x='Term Type',
                    y='Count',
                    color='Method',
                    barmode='group',
                    color_discrete_map={'Direct': '#3498db', 'OpenAI': '#f39c12'},
                    title="RxNorm Term Type Distribution by Method",
                    text_auto=True
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Insufficient successful mappings with TTY data for comparison.")
    except Exception as e:
        st.error(f"Error comparing TTY distributions: {str(e)}")

def display_statistical_analysis(direct_df, openai_df):
    """Display statistical analysis of the results"""
    
    # Standardize column names
    direct_df = standardize_column_names(direct_df)
    openai_df = standardize_column_names(openai_df)
    
    st.subheader("📊 Statistical Analysis")
    
    # Check if success column is available
    if 'success' not in direct_df.columns:
        st.warning("Could not determine success status for Direct dataset. Using default success rate of 0%.")
        direct_df['success'] = False
    
    if 'success' not in openai_df.columns:
        st.warning("Could not determine success status for OpenAI dataset. Using default success rate of 0%.")
        openai_df['success'] = False
    
    # Convert to numeric
    direct_df['success_int'] = direct_df['success'].astype(int)
    openai_df['success_int'] = openai_df['success'].astype(int)
    
    # Chi-square test for independence
    st.write("### Chi-Square Test for Independence")
    st.write("Tests whether the success rates are significantly different between the two methods.")
    
    # Create contingency table
    contingency = pd.DataFrame({
        'Success': [direct_df['success_int'].sum(), openai_df['success_int'].sum()],
        'Failure': [len(direct_df) - direct_df['success_int'].sum(), len(openai_df) - openai_df['success_int'].sum()]
    }, index=['Direct', 'OpenAI'])
    
    st.write("Contingency Table:")
    st.dataframe(contingency)
    
    # Perform chi-square test
    chi2, p, dof, expected = stats.chi2_contingency(contingency)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Chi-Square Value", f"{chi2:.3f}")
    col2.metric("p-value", f"{p:.5f}")
    col3.metric("Degrees of Freedom", dof)
    
    # Interpretation
    alpha = 0.05
    if p < alpha:
        st.success(f"The difference between the methods is statistically significant (p < {alpha}).")
    else:
        st.info(f"The difference between the methods is not statistically significant (p > {alpha}).")
    
    st.write("### Expected Frequencies")
    st.write("These are the expected frequencies if there was no relationship between method and success rate:")
    expected_df = pd.DataFrame(expected, columns=['Success', 'Failure'], index=['Direct', 'OpenAI'])
    st.dataframe(expected_df)
    
    # Effect size - Cramer's V
    st.write("### Effect Size - Cramer's V")
    n = contingency.sum().sum()
    cramers_v = np.sqrt(chi2 / (n * (min(contingency.shape) - 1)))
    
    st.metric("Cramer's V", f"{cramers_v:.3f}")
    
    # Interpretation of Cramer's V
    if cramers_v < 0.1:
        effect_size = "negligible"
    elif cramers_v < 0.3:
        effect_size = "small"
    elif cramers_v < 0.5:
        effect_size = "medium"
    else:
        effect_size = "large"
    
    st.write(f"The effect size is {effect_size}.")
    
    # Confidence Intervals for Success Proportions
    st.write("### Confidence Intervals for Success Proportions")
    
    direct_prop = direct_df['success_int'].mean()
    direct_se = np.sqrt((direct_prop * (1 - direct_prop)) / len(direct_df))
    direct_ci_lower = max(0, direct_prop - 1.96 * direct_se)
    direct_ci_upper = min(1, direct_prop + 1.96 * direct_se)
    
    openai_prop = openai_df['success_int'].mean()
    openai_se = np.sqrt((openai_prop * (1 - openai_prop)) / len(openai_df))
    openai_ci_lower = max(0, openai_prop - 1.96 * openai_se)
    openai_ci_upper = min(1, openai_prop + 1.96 * openai_se)
    
    ci_data = pd.DataFrame({
        'Method': ['Direct', 'OpenAI'],
        'Success Rate': [direct_prop * 100, openai_prop * 100],
        'Lower 95% CI': [direct_ci_lower * 100, openai_ci_lower * 100],
        'Upper 95% CI': [direct_ci_upper * 100, openai_ci_upper * 100]
    })
    
    st.dataframe(ci_data)
    
    # Visualize confidence intervals
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=ci_data['Method'],
        y=ci_data['Success Rate'],
        error_y=dict(
            type='data',
            symmetric=False,
            array=ci_data['Upper 95% CI'] - ci_data['Success Rate'],
            arrayminus=ci_data['Success Rate'] - ci_data['Lower 95% CI']
        ),
        mode='markers',
        marker=dict(
            color=['#3498db', '#f39c12'],
            size=12
        ),
        name='Success Rate with 95% CI'
    ))
    
    fig.update_layout(
        title='Success Rate with 95% Confidence Intervals',
        xaxis_title='Method',
        yaxis_title='Success Rate (%)',
        yaxis_range=[0, 100]
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Overlap interpretation
    if (direct_ci_lower <= openai_ci_upper and direct_ci_upper >= openai_ci_lower):
        st.info("The 95% confidence intervals overlap, which suggests the difference might not be statistically significant at the 5% level.")
    else:
        st.success("The 95% confidence intervals do not overlap, which suggests the difference is statistically significant at the 5% level.")

def display_dataset_comparison(direct_df, openai_df):
    """Display dataset comparison analysis"""
    
    # Standardize column names
    direct_df = standardize_column_names(direct_df)
    openai_df = standardize_column_names(openai_df)
    
    st.subheader("📊 Dataset Comparison")
    
    # Find common identifiers between datasets
    common_identifiers = ['original_code', 'original_product_name', 'original_dci']
    identifier_found = False
    
    for id_col in common_identifiers:
        if id_col in direct_df.columns and id_col in openai_df.columns:
            identifier_found = True
            
            direct_products = set(direct_df[id_col].astype(str))
            openai_products = set(openai_df[id_col].astype(str))
            
            common_products = direct_products.intersection(openai_products)
            direct_only_products = direct_products - common_products
            openai_only_products = openai_products - common_products
            
            st.write(f"### Product Overlap Analysis (based on {id_col})")
            
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
            try:
                if 'original_form' in direct_df.columns and 'original_form' in openai_df.columns:
                    st.subheader("Pharmaceutical Form Distribution")
                    
                    if direct_df['original_form'].notna().any() and openai_df['original_form'].notna().any():
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
                    else:
                        st.info("Pharmaceutical form data is not available or is empty in one or both datasets.")
                
                    # Check for success column
                    if 'success' not in direct_df.columns:
                        st.warning("Could not determine success status for Direct dataset. Skipping common forms comparison.")
                    elif 'success' not in openai_df.columns:
                        st.warning("Could not determine success status for OpenAI dataset. Skipping common forms comparison.")
                    else:
                        # Common forms success rate comparison
                        st.subheader("Common Forms Success Rate Comparison")
                        
                        try:
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
                                st.info("Insufficient data to compare common pharmaceutical forms. Need at least 5 products per form in both datasets.")
                        except Exception as e:
                            st.error(f"Error comparing common forms: {str(e)}")
            except Exception as e:
                st.error(f"Error analyzing pharmaceutical forms: {str(e)}")
            
            # We've found a valid identifier and completed the analysis, so break the loop
            break
    
    if not identifier_found:
        # Provide column information to help the user
        st.error("No common identifier found between datasets. Please ensure both datasets have matching identifier columns.")
        st.write("### Available Columns")
        col1, col2 = st.columns(2)
        with col1:
            st.write("Direct Dataset Columns:")
            st.write(", ".join(direct_df.columns.tolist()))
        with col2:
            st.write("OpenAI Dataset Columns:")
            st.write(", ".join(openai_df.columns.tolist()))
        
        st.info("The dashboard looks for common identifier columns like 'original_code', 'original_product_name', or 'original_dci'. Make sure at least one of these columns exists in both datasets with matching values.")

def display_matched_products_analysis(direct_df, openai_df):
    """Display analysis of matched products between Direct and OpenAI datasets"""
    
    # Standardize column names
    direct_df = standardize_column_names(direct_df)
    openai_df = standardize_column_names(openai_df)
    
    st.subheader("🔍 Matched Products Comparison")
    
    # Identify product identifiers to match datasets
    common_identifiers = ['original_code', 'original_product_name', 'original_dci']
    identifier_found = False
    
    for id_col in common_identifiers:
        if id_col in direct_df.columns and id_col in openai_df.columns:
            identifier_found = True
            
            # Check if success column is available
            if 'success' not in direct_df.columns:
                st.warning("Could not determine success status for Direct dataset. Using default success rate of 0%.")
                direct_df['success'] = False
            
            if 'success' not in openai_df.columns:
                st.warning("Could not determine success status for OpenAI dataset. Using default success rate of 0%.")
                openai_df['success'] = False
            
            try:
                # Match datasets using string identifiers to avoid type issues
                direct_df['id'] = direct_df[id_col].astype(str)
                openai_df['id'] = openai_df[id_col].astype(str)
                
                # Find common products
                common_ids = set(direct_df['id']).intersection(set(openai_df['id']))
                
                # Create matched dataframes
                direct_matched = direct_df[direct_df['id'].isin(common_ids)]
                openai_matched = openai_df[openai_df['id'].isin(common_ids)]
                
                # Count products
                st.write(f"Found {len(common_ids)} matched products using {id_col} as identifier")
                
                # Display metrics for matched products only
                st.subheader("Performance Comparison on Matched Products Only")
                
                # Calculate stats for matched products
                direct_success = direct_matched['success'].sum()
                direct_total = len(direct_matched)
                direct_rate = direct_success / direct_total * 100 if direct_total > 0 else 0
                
                openai_success = openai_matched['success'].sum()
                openai_total = len(openai_matched)
                openai_rate = openai_success / openai_total * 100 if openai_total > 0 else 0
                
                # Display metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.subheader("Direct Method")
                    st.metric("Total Matched Products", direct_total)
                    st.metric("Successful Mappings", direct_success)
                    st.metric("Success Rate", f"{direct_rate:.1f}%")
                
                with col2:
                    st.subheader("OpenAI Method")
                    st.metric("Total Matched Products", openai_total)
                    st.metric("Successful Mappings", openai_success)
                    st.metric("Success Rate", f"{openai_rate:.1f}%")
                
                with col3:
                    st.subheader("Difference")
                    st.metric("Success Count Difference", openai_success - direct_success)
                    st.metric("Success Rate Difference", f"{openai_rate - direct_rate:.1f}%")
                
                # Create a comparative bar chart
                comparison_data = pd.DataFrame({
                    'Method': ['Direct (Matched)', 'OpenAI (Matched)'],
                    'Success Rate': [direct_rate, openai_rate]
                })
                
                fig = px.bar(
                    comparison_data,
                    x='Method',
                    y='Success Rate',
                    color='Method',
                    color_discrete_map={
                        'Direct (Matched)': '#3498db', 
                        'OpenAI (Matched)': '#f39c12'
                    },
                    title="Success Rate Comparison (Matched Products Only)",
                    text_auto=True
                )
                
                fig.update_traces(textposition='outside')
                fig.update_layout(yaxis_range=[0, 100])
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Product-by-product analysis
                st.subheader("Product-by-Product Comparison")
                
                # Prepare data for comparison (avoid using index to prevent Float64Index issues)
                direct_matched = direct_matched.copy()
                openai_matched = openai_matched.copy()
                
                # Create a combined dataset of matched products with success status for both methods
                matched_comparison = pd.DataFrame({
                    'id': list(common_ids),
                    'direct_success': [False] * len(common_ids),
                    'openai_success': [False] * len(common_ids)
                })
                
                # Fill in success values from each dataset
                for idx, product_id in enumerate(matched_comparison['id']):
                    direct_product = direct_matched[direct_matched['id'] == product_id]
                    if not direct_product.empty:
                        matched_comparison.loc[idx, 'direct_success'] = direct_product['success'].iloc[0]
                    
                    openai_product = openai_matched[openai_matched['id'] == product_id]
                    if not openai_product.empty:
                        matched_comparison.loc[idx, 'openai_success'] = openai_product['success'].iloc[0]
                
                # Add additional product information if available
                if id_col in direct_matched.columns:
                    matched_comparison['product_id'] = matched_comparison['id'].apply(
                        lambda pid: direct_matched[direct_matched['id'] == pid][id_col].iloc[0] 
                        if not direct_matched[direct_matched['id'] == pid].empty else "")
                
                if 'original_product_name' in direct_matched.columns:
                    matched_comparison['product_name'] = matched_comparison['id'].apply(
                        lambda pid: direct_matched[direct_matched['id'] == pid]['original_product_name'].iloc[0] 
                        if not direct_matched[direct_matched['id'] == pid].empty else "")
                
                if 'original_form' in direct_matched.columns:
                    matched_comparison['form'] = matched_comparison['id'].apply(
                        lambda pid: direct_matched[direct_matched['id'] == pid]['original_form'].iloc[0] 
                        if not direct_matched[direct_matched['id'] == pid].empty else "")
                
                # Calculate agreement between methods
                matched_comparison['agreement'] = matched_comparison['direct_success'] == matched_comparison['openai_success']
                matched_comparison['both_success'] = matched_comparison['direct_success'] & matched_comparison['openai_success']
                matched_comparison['both_failed'] = ~matched_comparison['direct_success'] & ~matched_comparison['openai_success']
                matched_comparison['direct_only_success'] = matched_comparison['direct_success'] & ~matched_comparison['openai_success']
                matched_comparison['openai_only_success'] = ~matched_comparison['direct_success'] & matched_comparison['openai_success']
                
                # Calculate agreement statistics
                agreement_count = matched_comparison['agreement'].sum()
                agreement_rate = agreement_count / len(matched_comparison) * 100
                both_success_count = matched_comparison['both_success'].sum()
                both_success_rate = both_success_count / len(matched_comparison) * 100
                both_failed_count = matched_comparison['both_failed'].sum()
                both_failed_rate = both_failed_count / len(matched_comparison) * 100
                direct_only_count = matched_comparison['direct_only_success'].sum()
                direct_only_rate = direct_only_count / len(matched_comparison) * 100
                openai_only_count = matched_comparison['openai_only_success'].sum()
                openai_only_rate = openai_only_count / len(matched_comparison) * 100
                
                # Display agreement statistics
                st.write(f"### Agreement Statistics")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Overall Agreement Rate", f"{agreement_rate:.1f}%")
                    st.metric("Both Methods Successful", f"{both_success_count} ({both_success_rate:.1f}%)")
                    st.metric("Both Methods Failed", f"{both_failed_count} ({both_failed_rate:.1f}%)")
                
                with col2:
                    st.metric("Direct Only Successful", f"{direct_only_count} ({direct_only_rate:.1f}%)")
                    st.metric("OpenAI Only Successful", f"{openai_only_count} ({openai_only_rate:.1f}%)")
                    st.metric("Total Unique Successful Products", both_success_count + direct_only_count + openai_only_count)
                
                # Visualize agreement categories
                agreement_data = pd.DataFrame([
                    {'Category': 'Both Successful', 'Count': both_success_count},
                    {'Category': 'Both Failed', 'Count': both_failed_count},
                    {'Category': 'Direct Only', 'Count': direct_only_count},
                    {'Category': 'OpenAI Only', 'Count': openai_only_count}
                ])
                
                fig = px.pie(
                    agreement_data,
                    values='Count',
                    names='Category',
                    color='Category',
                    color_discrete_map={
                        'Both Successful': '#2ecc71',
                        'Both Failed': '#e74c3c',
                        'Direct Only': '#3498db',
                        'OpenAI Only': '#f39c12'
                    },
                    title="Agreement Analysis between Methods"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Calculate combined success rate
                hybrid_success_count = both_success_count + direct_only_count + openai_only_count
                hybrid_success_rate = hybrid_success_count / len(matched_comparison) * 100
                
                # Compare success rates including potential hybrid approach
                comparative_rates = pd.DataFrame({
                    'Method': ['Direct', 'OpenAI', 'Hybrid (Combined)'],
                    'Success Rate': [direct_rate, openai_rate, hybrid_success_rate]
                })
                
                fig = px.bar(
                    comparative_rates,
                    x='Method',
                    y='Success Rate',
                    color='Method',
                    color_discrete_map={
                        'Direct': '#3498db', 
                        'OpenAI': '#f39c12',
                        'Hybrid (Combined)': '#2ecc71'
                    },
                    title="Success Rate Comparison Including Hybrid Approach",
                    text_auto=True
                )
                
                fig.update_traces(textposition='outside')
                fig.update_layout(yaxis_range=[0, 100])
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Analysis by pharmaceutical form (if available)
                try:
                    if 'form' in matched_comparison.columns and matched_comparison['form'].notna().any():
                        st.subheader("Form-Based Analysis")
                        
                        # Calculate form-specific statistics
                        form_stats = matched_comparison.groupby('form').agg({
                            'direct_success': 'mean',
                            'openai_success': 'mean',
                            'both_success': 'mean',
                            'direct_only_success': 'mean',
                            'openai_only_success': 'mean',
                            'id': 'count'
                        }).reset_index()
                        
                        form_stats = form_stats.rename(columns={'id': 'count'})
                        form_stats['direct_success'] *= 100
                        form_stats['openai_success'] *= 100
                        form_stats['both_success'] *= 100
                        form_stats['direct_only_success'] *= 100
                        form_stats['openai_only_success'] *= 100
                        
                        # Calculate hybrid success rate
                        form_stats['hybrid_success'] = form_stats['both_success'] + form_stats['direct_only_success'] + form_stats['openai_only_success']
                        
                        # Filter to forms with sufficient sample size
                        min_samples = 5
                        significant_forms = form_stats[form_stats['count'] >= min_samples].sort_values('count', ascending=False).head(10)
                        
                        if not significant_forms.empty:
                            # Display top forms by sample size
                            st.write(f"### Top Forms by Sample Size (minimum {min_samples} samples)")
                            
                            # Melt data for plotting
                            plot_data = significant_forms.melt(
                                id_vars=['form', 'count'],
                                value_vars=['direct_success', 'openai_success', 'hybrid_success'],
                                var_name='Method',
                                value_name='Success Rate'
                            )
                            
                            # Rename method values for display
                            plot_data['Method'] = plot_data['Method'].map({
                                'direct_success': 'Direct',
                                'openai_success': 'OpenAI',
                                'hybrid_success': 'Hybrid'
                            })
                            
                            fig = px.bar(
                                plot_data,
                                x='form',
                                y='Success Rate',
                                color='Method',
                                color_discrete_map={
                                    'Direct': '#3498db', 
                                    'OpenAI': '#f39c12',
                                    'Hybrid': '#2ecc71'
                                },
                                barmode='group',
                                text_auto='.1f',
                                title="Success Rate by Pharmaceutical Form",
                                hover_data=['count']
                            )
                            
                            fig.update_layout(
                                xaxis_title="Pharmaceutical Form",
                                yaxis_title="Success Rate (%)",
                                yaxis_range=[0, 100]
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Show forms with biggest method differences
                            st.write("### Forms with Largest Method Differences")
                            
                            significant_forms['method_diff'] = significant_forms['openai_success'] - significant_forms['direct_success']
                            significant_forms = significant_forms.sort_values('count', ascending=False)
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write("OpenAI performs better:")
                                better_openai = significant_forms[significant_forms['method_diff'] > 0].sort_values('method_diff', ascending=False).head(5)
                                if not better_openai.empty:
                                    better_openai_display = better_openai.copy()
                                    better_openai_display['direct_success'] = better_openai_display['direct_success'].round(1).astype(str) + '%'
                                    better_openai_display['openai_success'] = better_openai_display['openai_success'].round(1).astype(str) + '%'
                                    better_openai_display['method_diff'] = better_openai_display['method_diff'].round(1).astype(str) + '%'
                                    
                                    st.dataframe(better_openai_display[['form', 'direct_success', 'openai_success', 'method_diff', 'count']])
                                else:
                                    st.write("No forms where OpenAI performs better")
                            
                            with col2:
                                st.write("Direct performs better:")
                                better_direct = significant_forms[significant_forms['method_diff'] < 0].sort_values('method_diff').head(5)
                                if not better_direct.empty:
                                    better_direct_display = better_direct.copy()
                                    better_direct_display['direct_success'] = better_direct_display['direct_success'].round(1).astype(str) + '%'
                                    better_direct_display['openai_success'] = better_direct_display['openai_success'].round(1).astype(str) + '%'
                                    better_direct_display['method_diff'] = better_direct_display['method_diff'].round(1).astype(str) + '%'
                                    
                                    st.dataframe(better_direct_display[['form', 'direct_success', 'openai_success', 'method_diff', 'count']])
                                else:
                                    st.write("No forms where Direct performs better")
                        else:
                            st.info(f"No forms with at least {min_samples} samples found")
                except Exception as e:
                    st.error(f"Error in form-based analysis: {str(e)}")
                
                # Browse detailed product results
                st.subheader("Browse Detailed Product Results")
                
                # Prepare comparison table
                browse_comparison = matched_comparison.copy()
                
                # Add columns for both RxNorm results if available
                try:
                    if 'rxnorm_name' in direct_matched.columns and 'rxnorm_name' in openai_matched.columns:
                        # Add direct RxNorm info
                        browse_comparison['direct_rxnorm_name'] = browse_comparison['id'].apply(
                            lambda pid: direct_matched[direct_matched['id'] == pid]['rxnorm_name'].iloc[0]
                            if not direct_matched[direct_matched['id'] == pid].empty and 
                               direct_matched[direct_matched['id'] == pid]['success'].iloc[0] else "")
                        
                        browse_comparison['direct_rxnorm_rxcui'] = browse_comparison['id'].apply(
                            lambda pid: direct_matched[direct_matched['id'] == pid]['rxnorm_rxcui'].iloc[0]
                            if not direct_matched[direct_matched['id'] == pid].empty and 
                               direct_matched[direct_matched['id'] == pid]['success'].iloc[0] else "")
                        
                        # Add openai RxNorm info
                        browse_comparison['openai_rxnorm_name'] = browse_comparison['id'].apply(
                            lambda pid: openai_matched[openai_matched['id'] == pid]['rxnorm_name'].iloc[0]
                            if not openai_matched[openai_matched['id'] == pid].empty and 
                               openai_matched[openai_matched['id'] == pid]['success'].iloc[0] else "")
                        
                        browse_comparison['openai_rxnorm_rxcui'] = browse_comparison['id'].apply(
                            lambda pid: openai_matched[openai_matched['id'] == pid]['rxnorm_rxcui'].iloc[0]
                            if not openai_matched[openai_matched['id'] == pid].empty and 
                               openai_matched[openai_matched['id'] == pid]['success'].iloc[0] else "")
                except Exception as e:
                    st.warning(f"Could not add RxNorm information: {str(e)}")
                
                # Add TTY columns if available
                try:
                    if 'rxnorm_tty' in direct_matched.columns and 'rxnorm_tty' in openai_matched.columns:
                        # Add direct TTY
                        browse_comparison['direct_rxnorm_tty'] = browse_comparison['id'].apply(
                            lambda pid: direct_matched[direct_matched['id'] == pid]['rxnorm_tty'].iloc[0]
                            if not direct_matched[direct_matched['id'] == pid].empty and 
                               direct_matched[direct_matched['id'] == pid]['success'].iloc[0] else "")
                        
                        # Add openai TTY
                        browse_comparison['openai_rxnorm_tty'] = browse_comparison['id'].apply(
                            lambda pid: openai_matched[openai_matched['id'] == pid]['rxnorm_tty'].iloc[0]
                            if not openai_matched[openai_matched['id'] == pid].empty and 
                               openai_matched[openai_matched['id'] == pid]['success'].iloc[0] else "")
                except Exception as e:
                    st.warning(f"Could not add TTY information: {str(e)}")
                
                # Filter options
                filter_options = ["All Products", 
                                "Both Methods Successful", 
                                "Both Methods Failed",
                                "Direct Only Successful", 
                                "OpenAI Only Successful",
                                "Methods Disagree"]
                
                filter_selection = st.selectbox("Filter products by category:", filter_options)
                
                # Apply filter
                if filter_selection == "Both Methods Successful":
                    filtered_data = browse_comparison[browse_comparison['both_success']]
                elif filter_selection == "Both Methods Failed":
                    filtered_data = browse_comparison[browse_comparison['both_failed']]
                elif filter_selection == "Direct Only Successful":
                    filtered_data = browse_comparison[browse_comparison['direct_only_success']]
                elif filter_selection == "OpenAI Only Successful":
                    filtered_data = browse_comparison[browse_comparison['openai_only_success']]
                elif filter_selection == "Methods Disagree":
                    filtered_data = browse_comparison[~browse_comparison['agreement']]
                else:
                    filtered_data = browse_comparison
                
                # Search by product name if available
                if 'product_name' in filtered_data.columns:
                    search_term = st.text_input("Search by product name:")
                    if search_term:
                        filtered_data = filtered_data[filtered_data['product_name'].str.contains(search_term, case=False, na=False)]
                
                # Show total
                st.write(f"Showing {len(filtered_data)} products")
                
                # Display detailed results
                cols_to_display = []
                
                # Add available columns to display
                if 'product_name' in filtered_data.columns:
                    cols_to_display.append('product_name')
                
                if 'form' in filtered_data.columns:
                    cols_to_display.append('form')
                
                cols_to_display.extend(['direct_success', 'openai_success'])
                
                if 'direct_rxnorm_name' in filtered_data.columns and 'openai_rxnorm_name' in filtered_data.columns:
                    cols_to_display.extend(['direct_rxnorm_name', 'openai_rxnorm_name'])
                
                if 'direct_rxnorm_tty' in filtered_data.columns and 'openai_rxnorm_tty' in filtered_data.columns:
                    cols_to_display.extend(['direct_rxnorm_tty', 'openai_rxnorm_tty'])
                
                # Ensure we have columns to display
                if not cols_to_display:
                    cols_to_display = filtered_data.columns.tolist()
                
                st.dataframe(filtered_data[cols_to_display])
                
                # Export button
                if st.button("Export Detailed Comparison"):
                    csv = filtered_data.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="matched_products_comparison.csv",
                        mime="text/csv"
                    )
            except Exception as e:
                st.error(f"Error in product comparison: {str(e)}")
                st.info("Try using the File Diagnostics tab to check your file format and column names.")
            
            # Found a valid identifier, so break the loop
            break
    
    if not identifier_found:
        # Provide column information to help the user
        st.error("No common identifier found between datasets. Please ensure both datasets have matching identifier columns.")
        st.write("### Available Columns")
        col1, col2 = st.columns(2)
        with col1:
            st.write("Direct Dataset Columns:")
            st.write(", ".join(direct_df.columns.tolist()))
        with col2:
            st.write("OpenAI Dataset Columns:")
            st.write(", ".join(openai_df.columns.tolist()))
        
        st.info("The dashboard looks for common identifier columns like 'original_code', 'original_product_name', or 'original_dci'. Make sure at least one of these columns exists in both datasets with matching values.")

def display_hierarchy_analysis(direct_df, openai_df):
    """Display RxNorm hierarchy-based analysis"""
    
    # Standardize column names
    direct_df = standardize_column_names(direct_df)
    openai_df = standardize_column_names(openai_df)
    
    st.subheader("🧩 RxNorm Hierarchy Analysis")
    st.markdown("""
    This tab analyzes differences in RxNorm mappings accounting for hierarchy differences 
    between generic and branded drug concepts, different term types, and ingredient relationships.
    """)
    
    # Check if required columns are present
    required_cols = ['success', 'rxnorm_rxcui', 'rxnorm_name', 'rxnorm_tty']
    missing_cols = {}
    
    for df_name, df in [("Direct", direct_df), ("OpenAI", openai_df)]:
        # Add success flag if not present
        if 'success' not in df.columns:
            if 'final_status' in df.columns:
                df['success'] = df['final_status'].str.lower() == 'success'
            elif 'rxnorm_found' in df.columns:
                df['success'] = df['rxnorm_found'].astype(bool)
            else:
                missing_cols[df_name] = ['success']
        
        # Check other required columns
        for col in required_cols[1:]:
            if col not in df.columns:
                if df_name in missing_cols:
                    missing_cols[df_name].append(col)
                else:
                    missing_cols[df_name] = [col]
    
    # Display warnings for missing columns
    if missing_cols:
        st.warning("Some required columns are missing from your datasets:")
        for df_name, cols in missing_cols.items():
            st.write(f"**{df_name}**: Missing {', '.join(cols)}")
        
        st.info("This analysis requires 'success', 'rxnorm_rxcui', 'rxnorm_name', and 'rxnorm_tty' columns. Please ensure your CSV files contain these columns.")
        
        # Show available columns
        st.write("### Available Columns")
        col1, col2 = st.columns(2)
        with col1:
            st.write("Direct Dataset Columns:")
            st.write(", ".join(direct_df.columns.tolist()))
        with col2:
            st.write("OpenAI Dataset Columns:")
            st.write(", ".join(openai_df.columns.tolist()))
        
        return
    
    # Find common identifiers between datasets
    common_identifiers = ['original_code', 'original_product_name', 'original_dci']
    identifier_found = False
    
    for id_col in common_identifiers:
        if id_col in direct_df.columns and id_col in openai_df.columns:
            identifier_found = True
            
            try:
                # Add unique ID column as string to avoid float/int issues
                direct_df['id'] = direct_df[id_col].astype(str)
                openai_df['id'] = openai_df[id_col].astype(str)
                
                # Find common products
                common_ids = set(direct_df['id']).intersection(set(openai_df['id']))
                st.write(f"Found {len(common_ids)} matched products using {id_col} as identifier")
                
                # Create matched dataframes
                direct_matched = direct_df[direct_df['id'].isin(common_ids)].copy()
                openai_matched = openai_df[openai_df['id'].isin(common_ids)].copy()
                
                # Filter to successful mappings
                direct_success = direct_matched[direct_matched['success']]
                openai_success = openai_matched[openai_matched['success']]
                
                # Check if we have successful mappings in both datasets
                if len(direct_success) == 0 or len(openai_success) == 0:
                    st.warning("Insufficient successful mappings in one or both datasets.")
                    st.info(f"Direct successful mappings: {len(direct_success)}")
                    st.info(f"OpenAI successful mappings: {len(openai_success)}")
                    return
                
                # Create a mapping from ID to RxNorm info
                direct_mapping = {}
                for _, row in direct_success.iterrows():
                    # Convert values to strings to avoid data type issues
                    rxcui = str(row['rxnorm_rxcui']) if not pd.isna(row['rxnorm_rxcui']) else ""
                    name = str(row['rxnorm_name']) if not pd.isna(row['rxnorm_name']) else ""
                    tty = str(row['rxnorm_tty']) if not pd.isna(row['rxnorm_tty']) else ""
                    direct_mapping[row['id']] = (rxcui, name, tty)
                
                openai_mapping = {}
                for _, row in openai_success.iterrows():
                    # Convert values to strings to avoid data type issues
                    rxcui = str(row['rxnorm_rxcui']) if not pd.isna(row['rxnorm_rxcui']) else ""
                    name = str(row['rxnorm_name']) if not pd.isna(row['rxnorm_name']) else ""
                    tty = str(row['rxnorm_tty']) if not pd.isna(row['rxnorm_tty']) else ""
                    openai_mapping[row['id']] = (rxcui, name, tty)
                
                # Find products successful in both methods
                both_success_ids = set(direct_mapping.keys()).intersection(set(openai_mapping.keys()))
                
                st.write(f"Found {len(both_success_ids)} products successfully mapped by both methods")
                
                # Create a comparison dataframe
                comparison_data = []
                
                for product_id in both_success_ids:
                    # Get RxNorm info for each method
                    direct_rxcui, direct_name, direct_tty = direct_mapping[product_id]
                    openai_rxcui, openai_name, openai_tty = openai_mapping[product_id]
                    
                    # Get product info
                    product_info = direct_matched[direct_matched['id'] == product_id].iloc[0]
                    product_name = product_info['original_product_name'] if 'original_product_name' in product_info else product_id
                    
                    # Extract active ingredient from name (simplistic approach)
                    direct_ingredients = extract_ingredient(direct_name)
                    openai_ingredients = extract_ingredient(openai_name)
                    
                    # Determine if mappings are same, hierarchy-related, or different
                    same_rxcui = direct_rxcui == openai_rxcui
                    same_ingredients = bool(set(direct_ingredients).intersection(set(openai_ingredients))) if direct_ingredients and openai_ingredients else False
                    
                    # Categorize the relationship
                    if same_rxcui:
                        relationship = "Exact Match"
                    elif same_ingredients and direct_tty != openai_tty:
                        relationship = "Hierarchy Difference"
                    else:
                        relationship = "Different Mapping"
                    
                    comparison_data.append({
                        'Product ID': product_id,
                        'Product Name': product_name,
                        'Direct RxCUI': direct_rxcui,
                        'Direct Name': direct_name,
                        'Direct TTY': direct_tty,
                        'OpenAI RxCUI': openai_rxcui,
                        'OpenAI Name': openai_name,
                        'OpenAI TTY': openai_tty,
                        'Relationship': relationship
                    })
                
                # Create a comparison dataframe
                comparison_df = pd.DataFrame(comparison_data)
                
                # Display hierarchy relationship statistics
                if not comparison_df.empty:
                    st.subheader("Hierarchy Relationship Analysis")
                    
                    relationship_counts = comparison_df['Relationship'].value_counts().reset_index()
                    relationship_counts.columns = ['Relationship', 'Count']
                    relationship_counts['Percentage'] = relationship_counts['Count'] / len(comparison_df) * 100
                    
                    # Display counts
                    st.write("### Mapping Relationship Types")
                    col1, col2, col3 = st.columns(3)
                    
                    exact_count = relationship_counts[relationship_counts['Relationship'] == 'Exact Match']['Count'].sum() if 'Exact Match' in relationship_counts['Relationship'].values else 0
                    hierarchy_count = relationship_counts[relationship_counts['Relationship'] == 'Hierarchy Difference']['Count'].sum() if 'Hierarchy Difference' in relationship_counts['Relationship'].values else 0
                    different_count = relationship_counts[relationship_counts['Relationship'] == 'Different Mapping']['Count'].sum() if 'Different Mapping' in relationship_counts['Relationship'].values else 0
                    
                    col1.metric("Exact Match", exact_count, f"{exact_count/len(comparison_df)*100:.1f}%")
                    col2.metric("Hierarchy Difference", hierarchy_count, f"{hierarchy_count/len(comparison_df)*100:.1f}%")
                    col3.metric("Different Mapping", different_count, f"{different_count/len(comparison_df)*100:.1f}%")
                    
                    # Create pie chart
                    fig = px.pie(
                        relationship_counts,
                        values='Count',
                        names='Relationship',
                        title="Mapping Relationship Distribution",
                        color='Relationship',
                        color_discrete_map={
                            'Exact Match': '#2ecc71',
                            'Hierarchy Difference': '#f39c12',
                            'Different Mapping': '#e74c3c'
                        },
                        hover_data=['Percentage']
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # TTY comparison for hierarchy differences
                    hierarchy_diff = comparison_df[comparison_df['Relationship'] == 'Hierarchy Difference']
                    
                    if not hierarchy_diff.empty:
                        st.write("### Hierarchy Relationship Analysis")
                        
                        # Create TTY pair counts
                        hierarchy_diff['TTY Pair'] = hierarchy_diff['Direct TTY'] + ' → ' + hierarchy_diff['OpenAI TTY']
                        tty_pairs = hierarchy_diff['TTY Pair'].value_counts().reset_index()
                        tty_pairs.columns = ['TTY Pair', 'Count']
                        tty_pairs['Percentage'] = tty_pairs['Count'] / len(hierarchy_diff) * 100
                        tty_pairs = tty_pairs.sort_values('Count', ascending=False)
                        
                        # Display TTY pair distribution
                        fig = px.bar(
                            tty_pairs,
                            x='TTY Pair',
                            y='Count',
                            title="Hierarchy Relationship Types",
                            text_auto=True
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # TTY descriptions
                        st.markdown("""
                        ### Common RxNorm TTY Types
                        - **SCD**: Semantic Clinical Drug (generic)
                        - **SBD**: Semantic Branded Drug
                        - **GPCK**: Generic Pack
                        - **BPCK**: Brand Name Pack
                        - **IN**: Ingredient
                        - **BN**: Brand Name
                        """)
                    
                    # Browse examples
                    st.subheader("Browse Hierarchy Examples")
                    
                    # Filter options
                    filter_options = ["All Mappings", "Exact Match", "Hierarchy Difference", "Different Mapping"]
                    filter_selection = st.selectbox("Filter by relationship type:", filter_options)
                    
                    if filter_selection != "All Mappings":
                        filtered_data = comparison_df[comparison_df['Relationship'] == filter_selection]
                    else:
                        filtered_data = comparison_df
                    
                    # Search by product name if available
                    search_term = st.text_input("Search by product name:")
                    if search_term:
                        filtered_data = filtered_data[filtered_data['Product Name'].str.contains(search_term, case=False, na=False)]
                    
                    # Show total
                    st.write(f"Showing {len(filtered_data)} products")
                    
                    # Display detailed results
                    if not filtered_data.empty:
                        st.dataframe(filtered_data)
                        
                        # Export button
                        if st.button("Export Hierarchy Analysis"):
                            csv = filtered_data.to_csv(index=False)
                            st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name="hierarchy_analysis.csv",
                                mime="text/csv"
                            )
                    
                    # Show specific examples
                    if len(filtered_data) > 0:
                        st.subheader("Example Mappings")
                        
                        # Get up to 3 examples of each relationship type
                        examples = []
                        for relationship in ['Exact Match', 'Hierarchy Difference', 'Different Mapping']:
                            relationship_examples = comparison_df[comparison_df['Relationship'] == relationship].head(3)
                            if not relationship_examples.empty:
                                examples.append(relationship_examples)
                        
                        if examples:
                            examples_df = pd.concat(examples)
                            
                            # Create expandable sections for each example
                            for i, row in examples_df.iterrows():
                                with st.expander(f"{row['Relationship']}: {row['Product Name']}"):
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.markdown("**Direct Mapping**")
                                        st.write(f"**RxCUI:** {row['Direct RxCUI']}")
                                        st.write(f"**Name:** {row['Direct Name']}")
                                        st.write(f"**TTY:** {row['Direct TTY']}")
                                    
                                    with col2:
                                        st.markdown("**OpenAI Mapping**")
                                        st.write(f"**RxCUI:** {row['OpenAI RxCUI']}")
                                        st.write(f"**Name:** {row['OpenAI Name']}")
                                        st.write(f"**TTY:** {row['OpenAI TTY']}")
                                    
                                    # Add explanations for hierarchy differences
                                    if row['Relationship'] == 'Hierarchy Difference':
                                        st.markdown("---")
                                        st.markdown("**Explanation**")
                                        
                                        direct_ingredients = extract_ingredient(row['Direct Name'])
                                        openai_ingredients = extract_ingredient(row['OpenAI Name'])
                                        
                                        st.write(f"Both mappings refer to the same medication but at different hierarchy levels:")
                                        
                                        # Generic vs branded
                                        if row['Direct TTY'] in ['SCD', 'SCDC', 'SCDF'] and row['OpenAI TTY'] in ['SBD', 'SBDC', 'SBDF']:
                                            st.write("Direct mapped to a generic concept while OpenAI mapped to a brand-name concept")
                                        elif row['Direct TTY'] in ['SBD', 'SBDC', 'SBDF'] and row['OpenAI TTY'] in ['SCD', 'SCDC', 'SCDF']:
                                            st.write("Direct mapped to a brand-name concept while OpenAI mapped to a generic concept")
                                        
                                        # Ingredient vs drug
                                        if row['Direct TTY'] in ['IN', 'MIN', 'PIN'] and row['OpenAI TTY'] in ['SCD', 'SBD', 'SCDF', 'SBDF']:
                                            st.write("Direct mapped to an ingredient concept while OpenAI mapped to a drug product concept")
                                        elif row['OpenAI TTY'] in ['IN', 'MIN', 'PIN'] and row['Direct TTY'] in ['SCD', 'SBD', 'SCDF', 'SBDF']:
                                            st.write("OpenAI mapped to an ingredient concept while Direct mapped to a drug product concept")
                        else:
                            st.info("No example mappings to display.")
                else:
                    st.warning("No products were successfully mapped by both methods. Cannot perform hierarchy analysis.")
            except Exception as e:
                st.error(f"Error in hierarchy analysis: {str(e)}")
            
            # Found a valid identifier and completed the analysis, so break the loop
            break
    
    if not identifier_found:
        # Provide column information to help the user
        st.error("No common identifier found between datasets. Please ensure both datasets have matching identifier columns.")
        st.write("### Available Columns")
        col1, col2 = st.columns(2)
        with col1:
            st.write("Direct Dataset Columns:")
            st.write(", ".join(direct_df.columns.tolist()))
        with col2:
            st.write("OpenAI Dataset Columns:")
            st.write(", ".join(openai_df.columns.tolist()))
        
        st.info("The dashboard looks for common identifier columns like 'original_code', 'original_product_name', or 'original_dci'. Make sure at least one of these columns exists in both datasets with matching values.")

def extract_ingredient(rxnorm_name):
    """Extract potential ingredients from RxNorm concept name"""
    if not rxnorm_name or not isinstance(rxnorm_name, str):
        return []
    
    # Simplistic approach: split by spaces and take words that start with uppercase
    words = rxnorm_name.split()
    potential_ingredients = [word for word in words if word and len(word) > 0 and word[0].isupper() and word.lower() not in 
                          ['oral', 'injection', 'tablet', 'capsule', 'solution', 'pack', 'extended', 'release']]
    
    # Also try to extract ingredients based on common patterns
    # For example: "100 MG acetaminophen / 5 MG oxycodone Oral Tablet" -> ["acetaminophen", "oxycodone"]
    ingredients = []
    pattern = r'\b([A-Z][a-z]+(?:\s[a-z]+)?)\b'
    matches = re.findall(pattern, rxnorm_name)
    ingredients.extend(matches)
    
    # Clean and combine
    all_ingredients = list(set(potential_ingredients + ingredients))
    return [ingredient.strip() for ingredient in all_ingredients if len(ingredient.strip()) > 2]

if __name__ == "__main__":
    create_dashboard()