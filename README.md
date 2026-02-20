🧠 AI Research Methodology Recommender (Offline Version)

An intelligent Streamlit-based tool that recommends appropriate research study designs based on a user-defined research objective.

This version runs fully offline with no API or external AI services required.

🚀 Features

📚 Select research domain

📝 Input research objective

🧠 Intelligent keyword-based study design detection

📊 Structured research framework output

🎨 Clean modern UI

🔌 Fully offline (No API key required)

🏗 How It Works

The system analyzes keywords in the research objective such as:

Keywords	Recommended Design
impact, effect, improve	Experimental / RCT
explore, understand	Qualitative Study
relationship, correlation	Correlational Study
predict, model	Predictive Modeling
(default)	Survey-Based Study

It then generates:

Recommended Study Design

Justification

Data Collection Plan

Sampling Strategy

Statistical Analysis

Limitations

Ethical Considerations

🛠 Installation

Clone the repository:

git clone https://github.com/yourusername/research-methodology-ai.git
cd research-methodology-ai

Install dependencies:

pip install -r requirements.txt
▶️ Run the App
streamlit run app.py

The app will open at:

http://localhost:8501
🎯 Use Cases