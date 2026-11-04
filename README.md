🌱 AIML FARMER

AI-Powered Smart Agriculture & Precision Irrigation Platform

AIML FARMER is an intelligent agriculture platform designed to help farmers make smarter irrigation decisions using Artificial Intelligence, Machine Learning, soil moisture analysis, crop water requirements and weather-based insights.

The platform combines machine learning predictions with agricultural parameters to support efficient water management and sustainable farming practices.

🚀 Key Features

- 24-Hour Soil Moisture Prediction: Predict future soil moisture conditions using a trained machine learning model.
- Weather Intelligence: Analyze weather-related parameters for agricultural decision-making.
- AI Irrigation Advisory: Generate intelligent irrigation recommendations based on soil, crop and weather conditions.
- Soil Moisture Analysis: Monitor and analyze soil moisture information.
- Water Requirement Calculator: Estimate irrigation water requirements for agricultural fields.
- Irrigation Decision Lab: Evaluate irrigation-related parameters and decisions.
- Field Management: Register and manage agricultural fields.
- Crop & Soil Configuration: Configure crop details and soil characteristics.
- Reports & History: Save and review generated agricultural reports.

🧠 Machine Learning

The platform uses machine learning models to analyze soil moisture patterns and generate predictions.

Model evaluation metrics on the held-out test dataset:

Metric| Result
R² Score| 96.28%
MAE| 2.48
RMSE| 3.96

🛠️ Technology Stack

Frontend

- Python
- Streamlit
- Pandas

Backend

- Python
- FastAPI
- REST APIs

Machine Learning

- Scikit-learn
- Random Forest Regressor
- HistGradientBoosting Regressor

Database

- SQLite

Development Tools

- Visual Studio Code
- Git & GitHub

📂 Project Structure

AIML-FARMER/
│
├── app.py
├── dashboard.py
├── api_client.py
│
├── pages/
│   ├── 24_hour_prediction.py
│   ├── Ai_advisory.py
│   ├── Crop_soil_configuration.py
│   ├── Field_management.py
│   ├── Irrigation_decision.py
│   ├── Report_history.py
│   ├── Soil_moisture.py
│   ├── Water_calculator.py
│   └── Weather_intelligence.py
│
├── backend/
│   ├── main.py
│   └── schemes.py
│
├── services/
│   ├── database.py
│   ├── irrigation_engine.py
│   └── advisory_engine.py
│
├── model/
│   ├── train_model.py
│   ├── soil_moisture_model.pkl
│   └── model_metadata.pkl
│
├── assets/
├── data/
├── requirements.txt
└── README.md

⚙️ Installation & Setup

1. Clone the Repository

git clone YOUR_GITHUB_REPOSITORY_URL

2. Navigate to Project Directory

cd AIML-FARMER

3. Create Virtual Environment

python -m venv venv

4. Activate Virtual Environment

Windows:

venv\Scripts\activate

5. Install Dependencies

pip install -r requirements.txt

6. Start Backend Server

python -m uvicorn backend.main:app --reload

Backend API:

http://127.0.0.1:8000

API Documentation:

http://127.0.0.1:8000/docs

7. Start Frontend

Open another terminal and run:

streamlit run app.py

The application will open in your browser.

🌍 Project Vision

AIML FARMER aims to promote data-driven agriculture by combining machine learning, intelligent irrigation recommendations and agricultural analytics.

Our goal is to support better water utilization, informed farming decisions and sustainable agricultural practices.

⚠️ Disclaimer

The irrigation recommendations are advisory estimates and should be evaluated alongside actual field conditions, local weather information and agricultural expertise.

👨‍💻 Project

AIML FARMER — Smart Agriculture Intelligence Platform

Built with Python, Machine Learning and Streamlit.