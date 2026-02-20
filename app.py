import streamlit as st

st.set_page_config(
    page_title="AI Research Methodology Recommender",
    page_icon="🧠",
    layout="wide"
)

# ------------------ Styling ------------------
st.markdown("""
<style>
body {
    background-color: #0f172a;
}
.title {
    text-align:center;
    font-size:40px;
    font-weight:700;
}
.subtitle {
    text-align:center;
    color:#94a3b8;
    margin-bottom:40px;
}
.card {
    background: rgba(255,255,255,0.05);
    padding:25px;
    border-radius:16px;
    border:1px solid rgba(255,255,255,0.1);
}
.result-card {
    background: rgba(30,41,59,0.7);
    padding:25px;
    border-radius:16px;
    margin-top:20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🧠 AI Research Methodology Recommender</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Offline Intelligent Study Design Advisor</div>', unsafe_allow_html=True)

# ------------------ Layout ------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    domain = st.selectbox(
        "📚 Research Domain",
        ["Education", "Healthcare", "AI/ML", "Social Sciences", "Business", "Engineering", "Other"]
    )

    objective = st.text_area(
        "📝 Research Objective",
        height=200,
        placeholder="Example: To evaluate whether AI tutoring improves math performance among engineering students."
    )

    generate = st.button("🚀 Recommend Methodology")

    st.markdown('</div>', unsafe_allow_html=True)

def recommend_method(objective_text):
    text = objective_text.lower()

    if "impact" in text or "effect" in text or "improve" in text:
        return "Experimental Study / Randomized Controlled Trial (RCT)"
    elif "explore" in text or "understand" in text or "experience" in text:
        return "Qualitative Study (Interviews / Focus Groups)"
    elif "relationship" in text or "correlation" in text:
        return "Correlational Study"
    elif "predict" in text or "model" in text:
        return "Predictive Modeling / Simulation Study"
    else:
        return "Survey-Based Cross-Sectional Study"

def build_framework(method):
    return f"""
### 1️⃣ Recommended Study Design
**{method}**

### 2️⃣ Justification
This design aligns with the research objective based on its analytical intent.

### 3️⃣ Data Collection
- Structured questionnaires
- Experimental measurements
- Interviews (if qualitative)
- Observational datasets

### 4️⃣ Sampling Strategy
- Random Sampling (if experimental)
- Stratified Sampling (if survey-based)
- Purposive Sampling (if qualitative)

### 5️⃣ Statistical Analysis
- T-test / ANOVA (for experimental)
- Regression Analysis (for correlation/prediction)
- Thematic Analysis (for qualitative)

### 6️⃣ Limitations
- Sampling bias
- Measurement errors
- External validity constraints

### 7️⃣ Ethical Considerations
- Informed consent
- Data privacy
- Institutional approval (if required)
"""

with col2:
    if generate and objective:
        method = recommend_method(objective)
        framework = build_framework(method)

        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown("## 📊 Recommended Research Framework")
        st.markdown(framework)
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("Built for Academic Projects & Research Planning 🚀")