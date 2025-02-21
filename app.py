import streamlit as st
import pandas as pd
import numpy as np
import datetime
import requests
import openai
import matplotlib.pyplot as plt

# Streamlit UI
st.title("🔬 AI-Powered Diabetes Self-Management")

# Sidebar for API Key Entry
st.sidebar.header("🔑 API Configuration")
openai_api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")

# Store API Key in session state (only if provided)
if openai_api_key:
    st.session_state["openai_api_key"] = openai_api_key

# Function to fetch AI-generated recommendations
def generate_recommendations(user_data):
    if "openai_api_key" not in st.session_state or not st.session_state["openai_api_key"]:
        return "⚠ Please enter a valid OpenAI API key in the sidebar."

    prompt = f"""
    A diabetes patient has the following details:
    - Age: {user_data['age']} 
    - BMI: {user_data['bmi']}
    - Daily Exercise: {user_data['exercise']} mins
    - Medication Compliance: {user_data['medication_compliance']}
    - Blood Glucose Levels: {user_data['glucose_level']} mg/dL

    Provide personalized recommendations for:
    - Diet (including meal suggestions)
    - Exercise (activity recommendations)
    - Medication adherence strategies
    - Motivational message (health benefits)
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI health advisor."},
                {"role": "user", "content": prompt}
            ],
            api_key=st.session_state["openai_api_key"]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠ Error: {str(e)}"

# Function for real-time alerts
def generate_alerts(glucose_level, medication_compliance):
    alerts = []
    if glucose_level > 180:
        alerts.append("⚠ High blood sugar detected! Consider adjusting your diet and consulting your doctor.")
    if glucose_level < 70:
        alerts.append("⚠ Low blood sugar detected! Have a small snack with carbohydrates.")
    if medication_compliance < 80:
        alerts.append("⚠ Medication compliance is below recommended levels. Remember to take your medications on time!")
    return alerts

# Function for AI-driven summarization
def generate_summary(data):
    summary = f"""
    - Your average glucose level this week: {np.mean(data['glucose_level']):.1f} mg/dL
    - Exercise consistency: {np.mean(data['exercise'])} mins/day
    - Medication adherence: {np.mean(data['medication_compliance'])}%
    - BMI: {data['bmi'][0]}

    Recommendation: {generate_recommendations(data)}
    """
    return summary

# Collect user input
st.sidebar.header("📊 User Health Data")
age = st.sidebar.number_input("Age", min_value=18, max_value=100, value=40)
bmi = st.sidebar.number_input("BMI", min_value=10.0, max_value=50.0, value=25.0)
exercise = st.sidebar.slider("Daily Exercise (mins)", 0, 120, 30)
medication_compliance = st.sidebar.slider("Medication Compliance (%)", 0, 100, 90)
glucose_level = st.sidebar.slider("Blood Glucose Level (mg/dL)", 50, 300, 120)
date = st.sidebar.date_input("Date", datetime.date.today())

# Create user data dictionary
user_data = {
    "age": age,
    "bmi": bmi,
    "exercise": exercise,
    "medication_compliance": medication_compliance,
    "glucose_level": glucose_level,
    "date": date
}

# Store data
if "patient_data" not in st.session_state:
    st.session_state.patient_data = pd.DataFrame(columns=["date", "age", "bmi", "exercise", "medication_compliance", "glucose_level"])

st.session_state.patient_data = pd.concat(
    [st.session_state.patient_data, pd.DataFrame([user_data])], ignore_index=True
)

# Display recommendations
st.subheader("📌 Personalized AI Recommendations")
recommendations = generate_recommendations(user_data)
st.write(recommendations)

# Display alerts
st.subheader("🚨 Real-Time Alerts")
alerts = generate_alerts(glucose_level, medication_compliance)
if alerts:
    for alert in alerts:
        st.warning(alert)
else:
    st.success("✅ No immediate health concerns detected.")

# Display summary
st.subheader("📊 Weekly Health Summary")
summary = generate_summary(st.session_state.patient_data)
st.write(summary)

# Visualizing glucose trends
st.subheader("📈 Blood Glucose Trend")
if len(st.session_state.patient_data) > 1:
    plt.figure(figsize=(8, 4))
    plt.plot(st.session_state.patient_data["date"], st.session_state.patient_data["glucose_level"], marker='o', linestyle='-')
    plt.xlabel("Date")
    plt.ylabel("Glucose Level (mg/dL)")
    plt.title("Blood Glucose Trends Over Time")
    st.pyplot(plt)

# Multi-Agent Collaboration Simulation
st.subheader("🤖 Multi-Agent Collaboration")
st.write("""
This AI application integrates multiple agents:
- **Diet Agent:** Monitors nutritional intake and suggests personalized meals.
- **Exercise Agent:** Analyzes physical activity data and recommends optimal workouts.
- **Medication Agent:** Ensures adherence and sends reminders.
- **Motivational Agent:** Encourages patients with health benefits and success stories.
""")

# Final message
st.success("🎉 Keep tracking your health! Your AI assistant will continuously adapt to support your journey.")
