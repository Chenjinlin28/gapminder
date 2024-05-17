import streamlit as st
import pandas as pd
import os
import plotly.express as px

st.title('Gapminder')
st.write("Unlocking Lifetimes: Visualizing Progress in Longevity and Poverty Eradication")

# Function to load data
@st.cache_data
def load_data():
    # Get the current working directory
    base_dir = os.path.dirname(__file__)
    
    # Construct full paths to the CSV files
    lex_path = os.path.join(base_dir, 'lex.csv')
    pop_path = os.path.join(base_dir, 'pop.csv')
    gnp_path = os.path.join(base_dir, 'ny_gnp_pcap_pp_cd.csv')
    
    # Debug: Print paths to ensure they are correct
    st.write(f"Lex path: {lex_path}")
    st.write(f"Pop path: {pop_path}")
    st.write(f"GNP path: {gnp_path}")
    
    # Load the CSV files
    lex = pd.read_csv(lex_path)
    pop = pd.read_csv(pop_path)
    gnp = pd.read_csv(gnp_path)
    
    return lex, pop, gnp

# Function to convert string values to numeric
def convert_to_numeric(value):
    if isinstance(value, str):
        value = value.strip()
        if 'B' in value:
            return float(value.replace('B', '')) * 1_000_000_000
        elif 'M' in value:
            return float(value.replace('M', '')) * 1_000_000
        elif 'k' in value:
            return float(value.replace('k', '')) * 1_000
        else:
            return float(value)
    return value

# Function to preprocess data
@st.cache_data
def preprocess_data(lex, pop, gnp):
    # Perform forward filling on numeric columns only
    lex.iloc[:, 1:] = lex.iloc[:, 1:].ffill(axis=1)
    gnp.iloc[:, 1:] = gnp.iloc[:, 1:].ffill(axis=1)
    pop.iloc[:, 1:] = pop.iloc[:, 1:].ffill(axis=1)

    # Replace NaN values with 0 in the entire DataFrames
    lex.fillna(0, inplace=True)
    gnp.fillna(0, inplace=True)
    pop.fillna(0, inplace=True)

    # Apply the conversion function to all columns except 'country'
    for col in pop.columns[1:]:
        pop[col] = pop[col].apply(convert_to_numeric)
    for col in gnp.columns[1:]:
        gnp[col] = gnp[col].apply(convert_to_numeric)
    for col in lex.columns[1:]:
        lex[col] = lex[col].apply(convert_to_numeric)

    # Transform the lex DataFrame to tidy format
    lex_tidy = lex.melt(id_vars=["country"], var_name="year", value_name="life_expectancy")

    # Transform the pop DataFrame to tidy format
    pop_tidy = pop.melt(id_vars=["country"], var_name="year", value_name="population")

    # Transform the gnp DataFrame to tidy format
    gnp_tidy = gnp.melt(id_vars=["country"], var_name="year", value_name="GNI_per_capita")

    # Merge the DataFrames on 'country' and 'year'
    merged_df = pd.merge(lex_tidy, pop_tidy, on=["country", "year"])
    merged_df = pd.merge(merged_df, gnp_tidy, on=["country", "year"])
    
    return merged_df

# Load data
lex, pop, gnp = load_data()

# Preprocess data
merged_df = preprocess_data(lex, pop, gnp)

# Display the head of the merged DataFrame
if merged_df is not None:
    st.write(merged_df.head())
else:
    st.write("Data could not be loaded or processed.")

# Interactive widgets
year = st.slider('Select Year', min_value=int(merged_df['year'].min()), max_value=int(merged_df['year'].max()), value=int(merged_df['year'].min()))
selected_countries = st.multiselect('Select Countries', options=merged_df['country'].unique(), default=merged_df['country'].unique())

# Filter data based on user input
filtered_df = merged_df[(merged_df['year'] == str(year)) & (merged_df['country'].isin(selected_countries))]

# Debug: Print the filtered DataFrame to ensure it's correct
st.write("Filtered DataFrame:")
st.write(filtered_df)

# Create bubble chart
fig = px.scatter(
    filtered_df,
    x='GNI_per_capita',
    y='life_expectancy',
    size='population',
    color='country',
    log_x=True,
    size_max=60,
    range_x=[1, 1e6],  # Adjust this range as necessary
    labels={'GNI_per_capita': 'GNI per capita (log scale)', 'life_expectancy': 'Life Expectancy'},
    title=f'Gapminder Data for {year}'
)

# Display the chart
st.plotly_chart(fig)
