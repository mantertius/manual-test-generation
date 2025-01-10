# flake8: noqa
import datetime
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

def extract_test_data_from_html(file_path):
    """Extract test data including test name, type, and table contents from the HTML file."""
    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    test_data = {}
    containers = soup.find_all("div", class_="container")  # Find all containers

    for container in containers:
        # Get the test name from the <h1> tag
        test_name = container.find("h1").text.strip()

        # Get all boxes for this test
        boxes = container.find_all("div", class_="box")
        for box in boxes:
            # Get the test type from the <p> tag inside .type-test
            test_type = box.find("div", class_="type-test").find("p").text.strip()

            # Extract table data
            rows = box.find_all("tr")
            table_data = []
            for row in rows[1:]:  # Skip the header
                cols = row.find_all("td")
                if cols:
                    table_data.append([col.text.strip() for col in cols])

            # Convert table data to a DataFrame
            if table_data:
                df = pd.DataFrame(table_data, columns=["#", "Actions", "Verifications"])

            # Organize data by test name and type
            if test_name not in test_data:
                test_data[test_name] = {}
            test_data[test_name][test_type] = df

    return test_data

def handle_null_values(text1, text2):
    """Handle null/None values in text comparison."""
    if pd.isna(text1) and pd.isna(text2):
        return 1.0  # Both empty means they're identical
    elif pd.isna(text1) or pd.isna(text2):
        return 0.0  # One empty means no similarity
    return None  # Both non-null, proceed with normal comparison

# Cosine similarity using TF-IDF Vectorizer
def cosine_similarity_tfidf(text1, text2):
    vectorizer = TfidfVectorizer().fit([text1, text2])
    vectors = vectorizer.transform([text1, text2])
    return cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

# Semantic similarity using Sentence-BERT
def semantic_similarity_bert(text1, text2):
    """Calculate semantic similarity with null value handling."""
    # First check for null values
    null_result = handle_null_values(text1, text2)
    if null_result is not None:
        return null_result

    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    embeddings = model.encode([str(text1), str(text2)])
    return np.dot(embeddings[0], embeddings[1]) / (np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1]))

def perform_comparison(df_a, df_b, progress_placeholder):
    """Perform row-wise comparison with progress tracking."""
    row_similarities = []
    # Use the shorter DataFrame length to avoid index errors
    total_rows = min(len(df_a), len(df_b))

    # Create a progress bar
    progress_bar = progress_placeholder.progress(0)

    # Only compare up to the length of the shorter DataFrame
    for i in range(total_rows):
        row_a = df_a.iloc[i]
        row_b = df_b.iloc[i]

        action_a = row_a["Actions"]
        verification_a = row_a["Verifications"]
        action_b = row_b["Actions"]
        verification_b = row_b["Verifications"]

        # Calculate semantic similarity using sentence transformer
        action_similarity = semantic_similarity_bert(action_a, action_b)
        verification_similarity = semantic_similarity_bert(verification_a, verification_b)

        # Average of action and verification similarity as row-wise similarity
        row_similarity = (action_similarity + verification_similarity) / 2
        row_similarities.append(row_similarity)

        # Update progress
        progress = (i + 1) / total_rows
        progress_bar.progress(progress)

    # Clean up progress bar after completion
    progress_placeholder.empty()

    return row_similarities, total_rows


# Streamlit application
# st.info("This app compares the similarity between two types of tests based on their actions and verifications. Upload the 'tables.html' file to get started.")
# st.snow()
st.set_page_config(
    page_title="Test Similarity Comparison",
    page_icon="🧪"
    ,
)
st.title("Semantic and Cosine Similarity Comparison by Test Name and Type")
uploaded_file = st.file_uploader("Upload the 'tables.html' file", type=["html"])

if uploaded_file:
    # Save uploaded file temporarily
    temp_path = Path("uploaded_tables.html")
    temp_path.write_bytes(uploaded_file.read())

    # Explanation and Formula before overall similarity computation
    st.subheader("How is the Overall Similarity Calculated?")
    explanation = """
### Similarity Score Calculation

The similarity score you see in the graph is calculated through these steps:

1. **Row-by-Row Comparison**:
   - For each row, we compare both the 'Actions' and 'Verifications' columns between the two test types
   - We use BERT (Bidirectional Encoder Representations from Transformers) to understand the semantic meaning of the text

2. **Handling Missing Values**:
   - If both cells are empty (null): Score = 1.0 (100% similar)
   - If one cell is empty and the other isn't: Score = 0.0 (0% similar)
   - If neither cell is empty: Calculate semantic similarity

3. **Individual Row Score**:
   - Action Similarity: Calculated using BERT (0.0 to 1.0)
   - Verification Similarity: Calculated using BERT (0.0 to 1.0)
   - Row Score = (Action Similarity + Verification Similarity) / 2

4. **Final Score**:
   - Average of all row scores
   - Displayed as a value between 0.0 (completely different) and 1.0 (identical)

The color intensity in the graph represents this final score:
- Darker/more intense colors = Higher similarity
- Lighter colors = Lower similarity
"""

    st.markdown(explanation)
    # Extract test data
    test_data = extract_test_data_from_html(temp_path)

    if st.button("Generate Overall Similarity Comparison"):
        # Display a graph for the overall similarity
        st.subheader("Overall Similarity Comparison")
        fig, ax = plt.subplots()

        # Create placeholders for loading indicators
        spinner_placeholder = st.empty()
        progress_placeholder = st.empty()
        #calculate elapsed time
        start = datetime.datetime.now()
        with spinner_placeholder.container():
            # Progress Bar initialization for this block
            progress_bar = progress_placeholder.progress(0)
            num_tests = len(test_data)  # Total number of tests
            overall_similarity_scores : list[float] = []

            for idx, (test_name, types) in enumerate(test_data.items()):
                with st.spinner(f"Processing test '{test_name}'..."):
                    if len(types) == 2:
                        type_a = list(types.keys())[0]
                        type_b = list(types.keys())[1]

                        # Perform semantic comparison for Actions and Verifications
                        type_a_df = types[type_a]
                        type_b_df = types[type_b]

                        similarity_scores = []
                        for i, row_a in type_a_df.iterrows():
                            action_a = row_a["Actions"]
                            verification_a = row_a["Verifications"]
                            if i < len(type_b_df):
                                row_b = type_b_df.iloc[i]
                                action_b = row_b["Actions"]
                                verification_b = row_b["Verifications"]

                                # Calculate semantic similarity
                                action_similarity = semantic_similarity_bert(action_a, action_b)
                                verification_similarity = semantic_similarity_bert(verification_a, verification_b)

                                # Average of action and verification similarity
                                row_similarity = (action_similarity + verification_similarity) / 2
                                similarity_scores.append(row_similarity)

                        avg_similarity = np.mean(similarity_scores) if similarity_scores else 0
                        overall_similarity_scores.append(avg_similarity)

                        # Gradients for color intensity
                        color_intensity = avg_similarity  # Use the average similarity directly for color intensity
                        bar_color = plt.cm.viridis(color_intensity)  # Use viridis colormap for gradient colors

                        # Draw the bar with gradient color
                        ax.barh(test_name, avg_similarity, color=bar_color)
                        ax.text(avg_similarity, test_name, f"{avg_similarity:.4f}", va='center', ha='right', color='black')

                    # Update progress bar
                    progress = (idx + 1) / num_tests
                    progress_bar.progress(progress)

            # Clear the loading indicators
            spinner_placeholder.success("✅ Overall comparison completed!")
            progress_placeholder.markdown('')

        with st.container():
            # Calculate elapsed time
            end = datetime.datetime.now()
            elapsed_time = end - start
            formatted_elapsed_time = elapsed_time.total_seconds()
            st.write(f"⏱️ Elapsed Time: {formatted_elapsed_time} seconds")
            plt.xlabel("Average Similarity")
            plt.ylabel("Test Name")
            plt.title("Similarity Comparison by Test Name")
            st.pyplot(fig)

            # Display overall metrics
            a,b,c,d = st.columns(4)
            a.metric(
                label="Total Tests 📊",
                value=f"{num_tests}"
            )
            b.metric(
                label="Average Similarity 📈",
                value=f"{np.mean(overall_similarity_scores):.4f}",
            )
            c.metric(
                label="Minimum Similarity 📉",
                value=f"{min(overall_similarity_scores):.4f}",
            )
            d.metric(
                label="Maximum Similarity 🏆",
                value=f"{max(overall_similarity_scores):.4f}",
            )

    st.markdown('---')

    selected_test = st.selectbox("Select a Test Name to Compare", list(test_data.keys()))
    if selected_test:
        available_types = list(test_data[selected_test].keys())
        type_a = available_types[0]
        type_b = available_types[1]

        if st.button("Compare"):
            if type_a in test_data[selected_test] and type_b in test_data[selected_test]:
                # Create placeholders for loading indicators
                spinner_placeholder = st.empty()
                progress_placeholder = st.empty()
                spinner_container = spinner_placeholder.container()

                spinner_container.write("🔄 Performing comparison analysis...")

                # Retrieve DataFrames for display
                df_a = test_data[selected_test][type_a]
                df_b = test_data[selected_test][type_b]

                # Perform comparison with progress tracking
                with spinner_placeholder.container():
                    with st.spinner("Calculating similarities..."):
                        row_similarities, compared_rows = perform_comparison(df_a, df_b, progress_placeholder)

                # Calculate average similarity
                avg_similarity = np.mean(row_similarities) if row_similarities else 0

                # Clear the loading message
                spinner_placeholder.success("✅ Comparison analysis completed!")

                    # Display results
                with st.container():
                    st.write(f"### Comparison Results for Test '{selected_test}'")
                    # Create columns for the metrics
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric(
                            label="Average Similarity",
                            value=f"{avg_similarity:.4f}"
                        )
                    with col2:
                        st.metric(
                            label="Minimum Similarity",
                            value=f"{min(row_similarities):.4f}" if row_similarities else "N/A"
                        )
                    with col3:
                        st.metric(
                            label="Maximum Similarity",
                            value=f"{max(row_similarities):.4f}" if row_similarities else "N/A"
                        )
                    with col4:
                        st.metric(
                            label="Rows Compared",
                            value=f"{compared_rows}"
                        )

                    # Display detailed results
                    with st.expander("View Detailed Results", expanded=False):
                        # Display length difference warning if applicable
                        if len(df_a) != len(df_b):
                            st.warning(f"⚠️ The two test types have different numbers of rows: {type_a}: {len(df_a)} rows, {type_b}: {len(df_b)} rows. Only the first {compared_rows} rows were compared.")

                        # Create copies of original DataFrames
                        df_a_display = df_a.copy()
                        df_b_display = df_b.copy()

                        # Initialize similarity columns with 'N/A'
                        df_a_display.loc[:, 'Similarity'] = 'N/A'
                        df_b_display.loc[:, 'Similarity'] = 'N/A'

                        # Update similarity values for compared rows
                        for i, similarity in enumerate(row_similarities):
                            if i < len(df_a_display):
                                df_a_display.at[df_a_display.index[i], 'Similarity'] = f"{similarity:.4f}"
                            if i < len(df_b_display):
                                df_b_display.at[df_b_display.index[i], 'Similarity'] = f"{similarity:.4f}"

                        st.write(f"**Type '{type_a}' Table Data:**")
                        st.dataframe(df_a_display, hide_index=True)

                        st.write(f"**Type '{type_b}' Table Data:**")
                        st.dataframe(df_b_display, hide_index=True)

            else:
                st.error(f"One or both types ('{type_a}', '{type_b}') are missing for the selected test.")