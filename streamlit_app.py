# streamlit_app.py

import streamlit as st
import os
from src.greenwashing_detector.main import run_greenwashing_crew

st.set_page_config(page_title="Greenwashing Detector", layout="centered")

st.title("🌍 Greenwashing Detector")
st.markdown("Upload a company’s sustainability report (PDF) to detect potential greenwashing.")

uploaded_file = st.file_uploader("Upload Sustainability Report (PDF)", type="pdf")

if uploaded_file:
    with st.spinner("Analyzing report..."):
        file_path = os.path.join("uploaded_reports", uploaded_file.name)
        os.makedirs("uploaded_reports", exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

        result = run_greenwashing_crew(file_path)
        st.success("Analysis complete!")

        st.markdown("### 📝 Greenwashing Report")
        st.markdown(result)
