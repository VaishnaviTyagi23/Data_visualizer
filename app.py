import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Set the page config
st.set_page_config(page_title='Data Visualizer', layout='wide', page_icon='📊')

# Title and description
st.title('📊 Data Visualizer')
st.write(
    "Upload your CSV file or select one from the predefined folder to visualize the data using various plot types. You can also filter and analyze the data with correlation heatmaps and moving averages.")

# Sidebar for file upload and selection
st.sidebar.header("Upload or Select a CSV File")

# Option to upload a CSV file
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

# Specify the folder where your CSV files are located
working_dir = os.path.dirname(os.path.abspath(__file__))
folder_path = f"{working_dir}/data"  # Update this to your folder path

# List all files in the folder
files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# Dropdown to select a file from the folder
selected_file = st.sidebar.selectbox('Or select a file from the folder', files)

# Load data based on user input
df = None
if uploaded_file:
    df = pd.read_csv(uploaded_file)
elif selected_file:
    file_path = os.path.join(folder_path, selected_file)
    df = pd.read_csv(file_path)

if df is not None:
    columns = df.columns.tolist()

    st.subheader("Data Preview")
    st.dataframe(df.head())

    # Filter Section
    st.subheader("Filter Data")
    with st.expander("Select columns and values to filter"):
        selected_columns = st.multiselect('Columns to Filter', columns, help="Choose columns to apply filters")
        filtered_df = df[selected_columns] if selected_columns else df

        for column in selected_columns:
            unique_values = df[column].unique()
            selected_values = st.multiselect(f'Values for {column}', unique_values,
                                             help=f"Choose specific values for {column}")
            filtered_df = filtered_df[filtered_df[column].isin(selected_values)]

    # Plotting Section
    st.subheader("Create a Plot")
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        x_axis = st.selectbox('X-axis', options=columns, help="Select the column for the X-axis")
        y_axis = st.selectbox('Y-axis', options=columns, help="Select the column for the Y-axis")

    with col2:
        plot_list = ['Line Plot', 'Bar Chart', 'Scatter Plot', 'Distribution Plot', 'Count Plot']
        plot_type = st.selectbox('Plot Type', options=plot_list, help="Choose the type of plot to generate")

    with col3:
        width = st.slider('Width', min_value=5, max_value=15, value=10, help="Adjust the plot width")
        height = st.slider('Height', min_value=3, max_value=10, value=6, help="Adjust the plot height")

    if st.button('Generate Plot'):
        fig, ax = plt.subplots(figsize=(width, height))

        if plot_type == 'Line Plot':
            sns.lineplot(x=filtered_df[x_axis], y=filtered_df[y_axis], ax=ax)
        elif plot_type == 'Bar Chart':
            sns.barplot(x=filtered_df[x_axis], y=filtered_df[y_axis], ax=ax)
        elif plot_type == 'Scatter Plot':
            sns.scatterplot(x=filtered_df[x_axis], y=filtered_df[y_axis], ax=ax)
        elif plot_type == 'Distribution Plot':
            sns.histplot(filtered_df[x_axis], kde=True, ax=ax)
        elif plot_type == 'Count Plot':
            sns.countplot(x=filtered_df[x_axis], ax=ax)

        st.pyplot(fig)

    # Correlation Heatmap
    st.subheader("Additional Analysis")
    if st.checkbox('Show Correlation Heatmap'):
        st.write("Correlation heatmap shows the relationship between different variables in the dataset.")
        corr = df.corr()
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
        st.pyplot(fig)

    # Moving average for trend analysis
    if st.checkbox('Show Moving Average'):
        window_size = st.slider('Window Size', min_value=2, max_value=30, value=5,
                                help="Select the window size for the moving average")
        df[f'{y_axis}_moving_avg'] = df[y_axis].rolling(window=window_size).mean()
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.lineplot(x=df[x_axis], y=df[f'{y_axis}_moving_avg'], ax=ax, label=f'{y_axis} Moving Average')
        st.pyplot(fig)

    # Download Section
    st.subheader("Download Options")
    if not filtered_df.empty:
        csv = filtered_df.to_csv(index=False)
        st.download_button('Download Filtered Data', csv, f'filtered_data_{selected_file}.csv', 'text/csv',
                           help="Download the filtered dataset as a CSV file")

    if st.button('Download Plot'):
        fig.savefig(f'{plot_type}_{x_axis}_vs_{y_axis}.png')
        st.success('Plot downloaded successfully!')

else:
    st.warning("Please upload a file or select one from the folder.")
