# dashboard/streamlit_app.py
import streamlit as st
import pandas as pd
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(page_title="🎫 Client Success Triage", layout="wide")
st.title("🎫 Client Success Ticket Triage System")
st.markdown("AI-powered classification of support tickets by **priority** and **category**.")

# Configuration
API_URL = "https://client-success-triage-system.onrender.com"
API_KEY = "your-secret-api-key-here-keep-it-safe"

# Test API connection
def test_api():
    try:
        health = requests.get("http://localhost:8000/health", timeout=5)
        return health.status_code == 200
    except Exception as e:
        logger.error(f"API connection failed: {e}")
        return False

if not test_api():
    st.error("❌ Cannot connect to FastAPI backend. Make sure it's running:")
    st.code("python -m uvicorn app.main:app --reload")
else:
    st.success("✅ Connected to FastAPI backend")

# Upload CSV
uploaded_file = st.file_uploader("📤 Upload your tickets (CSV)", type="csv")
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.info(f"Loaded **{len(df)} tickets** from uploaded file.")

        # Normalize column names
        df.columns = [col.strip().lower() for col in df.columns]

        # Validate required columns
        if "subject" not in df.columns or "description" not in df.columns:
            st.error("❌ CSV must contain 'subject' and 'description' columns.")
            st.write("📋 Your columns:", list(df.columns))
            st.stop()

        # Ensure subject/description are strings
        df["subject"] = df["subject"].astype(str).fillna("")
        df["description"] = df["description"].astype(str).fillna("")

        # Show preview
        with st.expander("🔍 Data Preview", expanded=False):
            st.dataframe(df.head(10))

        # Classify first 25
        if st.button("🧠 Classify First 25 Tickets"):
            df = df.head(25).copy()

            # Add prediction columns
            df["predicted_priority"] = ""
            df["predicted_category"] = ""
            df["priority_confidence"] = 0.0
            df["category_confidence"] = 0.0
            df["error"] = ""

            st.subheader("📊 Classification Progress")
            progress_bar = st.progress(0)
            status_text = st.empty()

            for idx, row in df.iterrows():
                subject = row["subject"]
                description = row["description"]
                status_text.text(f"Classifying: {subject[:50]}...")

                try:
                    response = requests.post(
                        API_URL,
                        json={"subject": subject, "description": description},
                        headers={"X-API-Key": API_KEY},
                        timeout=30
                    )
                    if response.status_code == 200:
                        result = response.json()
                        df.at[idx, "predicted_priority"] = result["priority"]
                        df.at[idx, "predicted_category"] = result["category"]
                        df.at[idx, "priority_confidence"] = round(result["priority_confidence"], 4)
                        df.at[idx, "category_confidence"] = round(result["category_confidence"], 4)
                    else:
                        error_msg = response.json().get("detail", "Unknown error")
                        df.at[idx, "predicted_priority"] = "ERROR"
                        df.at[idx, "predicted_category"] = "ERROR"
                        df.at[idx, "error"] = f"HTTP {response.status_code}: {error_msg}"
                except Exception as e:
                    df.at[idx, "predicted_priority"] = "ERROR"
                    df.at[idx, "predicted_category"] = "ERROR"
                    df.at[idx, "error"] = str(e)

                progress_bar.progress((idx + 1) / len(df))

            st.success("✅ Classification complete!")
            st.session_state['classified_df'] = df

    except Exception as e:
        st.error(f"❌ Failed to read CSV file: {e}")

# Display results if available
if 'classified_df' in st.session_state:
    df = st.session_state['classified_df']

    st.subheader("📋 Classification Results")
    # Show only relevant columns
    display_df = df[[
        "subject", "description",
        "predicted_priority", "priority_confidence",
        "predicted_category", "category_confidence", "error"
    ]]
    st.dataframe(display_df, use_container_width=True)

    # Charts
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📊 Predicted Priority Distribution")
        st.bar_chart(df["predicted_priority"].value_counts())
    with col2:
        st.markdown("### 📊 Predicted Category Distribution")
        st.bar_chart(df["predicted_category"].value_counts())

    # Export
    csv = df.to_csv(index=False).encode()
    st.download_button(
        label="📥 Download Results as CSV",
        data=csv,
        file_name="classified_tickets_with_predictions.csv",
        mime="text/csv"
    )