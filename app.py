# flake8: noqa
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

# Cosine similarity using TF-IDF Vectorizer
def cosine_similarity_tfidf(text1, text2):
    vectorizer = TfidfVectorizer().fit([text1, text2])
    vectors = vectorizer.transform([text1, text2])
    return cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

def handle_null_values(text1, text2):
    """Handle null/None values in text comparison."""
    if pd.isna(text1) and pd.isna(text2):
        return 1.0  # Both empty means they're identical
    elif pd.isna(text1) or pd.isna(text2):
        return 0.0  # One empty means no similarity
    return None  # Both non-null, proceed with normal comparison

# Semantic similarity using Sentence-BERT (better for contextual similarity)
def semantic_similarity_bert(text1, text2):
    """Calculate semantic similarity with null value handling."""
    # First check for null values
    null_result = handle_null_values(text1, text2)
    if null_result is not None:
        return null_result

    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    embeddings = model.encode([str(text1), str(text2)])
    return np.dot(embeddings[0], embeddings[1]) / (np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1]))

# Streamlit application
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

    # Display a graph for the overall similarity (we will calculate it on a row-wise basis soon)
    st.subheader("Overall Similarity Comparison")
    fig, ax = plt.subplots()
    
    # Progress Bar initialization for this block
    progress_bar = st.progress(0)  
    num_tests = len(test_data)  # Total number of tests
    
    for idx, (test_name, types) in enumerate(test_data.items()):
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

                    # Calculate semantic similarity using sentence transformer
                    action_similarity = semantic_similarity_bert(action_a, action_b)
                    verification_similarity = semantic_similarity_bert(verification_a, verification_b)

                    # Average of action and verification similarity as row-wise similarity
                    row_similarity = (action_similarity + verification_similarity) / 2
                    similarity_scores.append(row_similarity)

            avg_similarity = np.mean(similarity_scores) if similarity_scores else 0
            
            # Gradients, mapping similarity score to color intensity (greener for higher similarity)
            color_intensity = min(1, max(0, avg_similarity))  # Map to range 0-1
            bar_color = plt.cm.viridis(color_intensity)  # Apply "viridis" colormap for a green-to-yellow gradient
            
            # Draw the bar with gradient color
            ax.barh(test_name, avg_similarity, color=bar_color)
        
        # Update progress bar after each test is processed
        progress = (idx + 1) / num_tests
        progress_bar.progress(progress)

    plt.xlabel("Average Similarity")
    plt.ylabel("Test Name")
    plt.title("Similarity Comparison by Test Name")
    st.pyplot(fig)

    st.markdown('---')

    selected_test = st.selectbox("Select a Test Name to Compare", list(test_data.keys()))
    if selected_test:
        available_types = list(test_data[selected_test].keys())
        type_a = available_types[0]
        type_b = available_types[1]

        if st.button("Compare"):
            if type_a in test_data[selected_test] and type_b in test_data[selected_test]:
                # Retrieve DataFrames for display
                df_a = test_data[selected_test][type_a]
                df_b = test_data[selected_test][type_b]

                # Row-wise comparison of Jaccard distance and cosine similarity
                row_similarities = []
                num_rows = len(df_a)

                # Add a progress bar for the row-wise comparison
                row_progress_bar = st.progress(0)

                for i, row_a in df_a.iterrows():
                    action_a = row_a["Actions"]
                    verification_a = row_a["Verifications"]
                    if i < len(df_b):
                        row_b = df_b.iloc[i]
                        action_b = row_b["Actions"]
                        verification_b = row_b["Verifications"]

                        # Calculate semantic similarity using sentence transformer
                        action_similarity = semantic_similarity_bert(action_a, action_b)
                        verification_similarity = semantic_similarity_bert(verification_a, verification_b)

                        # Average of action and verification similarity as row-wise similarity
                        row_similarity = (action_similarity + verification_similarity) / 2
                        row_similarities.append(row_similarity)

                    # Update progress bar
                    progress = (i + 1) / num_rows
                    row_progress_bar.progress(progress)

                st.subheader(f"Results for {selected_test}")
                st.write(f"Average Similarity between Type '{type_a}' and Type '{type_b}': **{np.mean(row_similarities):.4f}**")

                st.write(f"**Type '{type_a}' Table Data:**")
                st.dataframe(df_a, hide_index=True)

                st.write(f"**Type '{type_b}' Table Data:**")
                st.dataframe(df_b, hide_index=True)

            else:
                st.error(f"One or both types ('{type_a}', '{type_b}') are missing for the selected test.")
