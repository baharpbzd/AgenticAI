import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from typing import List, Dict
import random

# --- Data Management ---
def load_or_create_data():
    try:
        with open('diabetes_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'glucose_readings': [],
            'medications': [],
            'meals': [],
            'exercise': []
        }

def save_data(data):
    with open('diabetes_data.json', 'w') as f:
        json.dump(data, f)

# --- AI Components ---
class DiabetesAI:
    def analyze_glucose_pattern(self, readings: List[Dict]) -> Dict:
        if not readings:
            return {"risk_level": "unknown", "recommendations": ["Not enough data for analysis"]}
        
        values = [r['value'] for r in readings[-10:]]  # Last 10 readings
        mean = np.mean(values)
        std = np.std(values)
        
        risk_level = "low"
        if mean > 180:
            risk_level = "high"
        elif mean > 140:
            risk_level = "moderate"
            
        recommendations = []
        if mean > 180:
            recommendations.append("Your blood sugar is running high. Consider reviewing your meal plan.")
        if std > 40:
            recommendations.append("Your blood sugar shows high variability. Try to maintain consistent meal times.")
        if mean < 70:
            recommendations.append("Your blood sugar is running low. Consider adjusting your medication.")
            
        if not recommendations:
            recommendations.append("Your blood sugar control looks good! Keep up the good work.")
            
        return {
            "risk_level": risk_level,
            "mean": round(mean, 1),
            "std": round(std, 1),
            "recommendations": recommendations
        }

# --- Main Application ---
def main():
    st.set_page_config(page_title="Diabetes Management System", layout="wide")
    
    # Initialize session state
    if 'data' not in st.session_state:
        st.session_state.data = load_or_create_data()
    if 'ai' not in st.session_state:
        st.session_state.ai = DiabetesAI()

    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Dashboard", "Log Glucose", "Medications", "Meals", "Exercise", "Analytics"]
    )
    
    # Header
    st.title("Diabetes Management System")
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Log Glucose":
        show_glucose_logging()
    elif page == "Medications":
        show_medications()
    elif page == "Meals":
        show_meals()
    elif page == "Exercise":
        show_exercise()
    elif page == "Analytics":
        show_analytics()

def show_dashboard():
    # Layout with columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Blood Glucose Trends")
        if st.session_state.data['glucose_readings']:
            df = pd.DataFrame(st.session_state.data['glucose_readings'])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            fig = px.line(df, x='timestamp', y='value', 
                         title='Blood Glucose History',
                         labels={'value': 'Blood Glucose (mg/dL)', 'timestamp': 'Time'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No glucose readings available. Start logging to see trends!")

    with col2:
        st.subheader("AI Analysis")
        analysis = st.session_state.ai.analyze_glucose_pattern(st.session_state.data['glucose_readings'])
        
        # Risk level indicator
        risk_colors = {"low": "green", "moderate": "yellow", "high": "red"}
        st.markdown(f"""
            <div style='padding: 10px; border-radius: 5px; background-color: {risk_colors.get(analysis["risk_level"], "gray")}'>
                <h3 style='color: white; margin: 0;'>Risk Level: {analysis["risk_level"].upper()}</h3>
            </div>
        """, unsafe_allow_html=True)
        
        # Recommendations
        st.subheader("Recommendations")
        for rec in analysis["recommendations"]:
            st.write("•", rec)
    
    # Recent activities
    st.subheader("Recent Activities")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Latest Glucose Readings")
        if st.session_state.data['glucose_readings']:
            for reading in st.session_state.data['glucose_readings'][-3:]:
                st.write(f"🔵 {reading['value']} mg/dL at {reading['timestamp']}")
    
    with col2:
        st.markdown("### Today's Medications")
        if st.session_state.data['medications']:
            for med in st.session_state.data['medications'][-3:]:
                st.write(f"💊 {med['name']} - {med['dosage']}")
    
    with col3:
        st.markdown("### Recent Meals")
        if st.session_state.data['meals']:
            for meal in st.session_state.data['meals'][-3:]:
                st.write(f"🍽️ {meal['description']}")

def show_glucose_logging():
    st.subheader("Log Blood Glucose Reading")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        reading = st.number_input("Blood Glucose (mg/dL)", 0, 500, 120)
        notes = st.text_area("Notes", "")
        
        if st.button("Save Reading"):
            new_reading = {
                "timestamp": datetime.now().isoformat(),
                "value": reading,
                "notes": notes
            }
            st.session_state.data['glucose_readings'].append(new_reading)
            save_data(st.session_state.data)
            st.success("Reading saved successfully!")
    
    with col2:
        if st.session_state.data['glucose_readings']:
            df = pd.DataFrame(st.session_state.data['glucose_readings'][-10:])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            fig = px.line(df, x='timestamp', y='value',
                         title='Recent Readings',
                         labels={'value': 'Blood Glucose (mg/dL)', 'timestamp': 'Time'})
            st.plotly_chart(fig)

def show_medications():
    st.subheader("Medication Tracking")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        med_name = st.text_input("Medication Name")
        dosage = st.text_input("Dosage")
        time = st.time_input("Time")
        
        if st.button("Add Medication"):
            new_med = {
                "name": med_name,
                "dosage": dosage,
                "time": time.strftime("%H:%M")
            }
            st.session_state.data['medications'].append(new_med)
            save_data(st.session_state.data)
            st.success("Medication added successfully!")
    
    with col2:
        if st.session_state.data['medications']:
            st.write("Current Medications:")
            for med in st.session_state.data['medications']:
                st.write(f"💊 {med['name']} - {med['dosage']} at {med['time']}")

def show_meals():
    st.subheader("Meal Logging")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
        description = st.text_area("Description")
        carbs = st.number_input("Carbohydrates (g)", 0, 200, 0)
        
        if st.button("Log Meal"):
            new_meal = {
                "timestamp": datetime.now().isoformat(),
                "type": meal_type,
                "description": description,
                "carbs": carbs
            }
            st.session_state.data['meals'].append(new_meal)
            save_data(st.session_state.data)
            st.success("Meal logged successfully!")
    
    with col2:
        if st.session_state.data['meals']:
            st.write("Recent Meals:")
            for meal in st.session_state.data['meals'][-5:]:
                st.write(f"🍽️ {meal['type']}: {meal['description']} ({meal['carbs']}g carbs)")

def show_exercise():
    st.subheader("Exercise Tracking")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        activity = st.text_input("Activity Type")
        duration = st.number_input("Duration (minutes)", 0, 300, 30)
        intensity = st.selectbox("Intensity", ["Low", "Moderate", "High"])
        
        if st.button("Log Exercise"):
            new_exercise = {
                "timestamp": datetime.now().isoformat(),
                "activity": activity,
                "duration": duration,
                "intensity": intensity
            }
            st.session_state.data['exercise'].append(new_exercise)
            save_data(st.session_state.data)
            st.success("Exercise logged successfully!")
    
    with col2:
        if st.session_state.data['exercise']:
            st.write("Recent Exercise:")
            for ex in st.session_state.data['exercise'][-5:]:
                st.write(f"🏃 {ex['activity']} - {ex['duration']} min ({ex['intensity']} intensity)")

def show_analytics():
    st.subheader("Analytics Dashboard")
    
    if not st.session_state.data['glucose_readings']:
        st.warning("No data available for analysis. Please log some readings first.")
        return
    
    # Convert readings to DataFrame
    df = pd.DataFrame(st.session_state.data['glucose_readings'])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Time range selector
    time_range = st.selectbox(
        "Select Time Range",
        ["Last 7 Days", "Last 30 Days", "All Time"]
    )
    
    if time_range == "Last 7 Days":
        df = df[df['timestamp'] >= datetime.now() - timedelta(days=7)]
    elif time_range == "Last 30 Days":
        df = df[df['timestamp'] >= datetime.now() - timedelta(days=30)]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Glucose distribution
        fig = px.histogram(df, x='value',
                          title='Blood Glucose Distribution',
                          labels={'value': 'Blood Glucose (mg/dL)', 'count': 'Frequency'})
        st.plotly_chart(fig)
    
    with col2:
        # Time of day analysis
        df['hour'] = df['timestamp'].dt.hour
        hourly_avg = df.groupby('hour')['value'].mean().reset_index()
        fig = px.line(hourly_avg, x='hour', y='value',
                     title='Average Blood Glucose by Hour',
                     labels={'value': 'Blood Glucose (mg/dL)', 'hour': 'Hour of Day'})
        st.plotly_chart(fig)
    
    # Statistics
    st.subheader("Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Average Glucose", f"{df['value'].mean():.1f} mg/dL")
    with col2:
        st.metric("Standard Deviation", f"{df['value'].std():.1f} mg/dL")
    with col3:
        st.metric("Minimum", f"{df['value'].min():.1f} mg/dL")
    with col4:
        st.metric("Maximum", f"{df['value'].max():.1f} mg/dL")

if __name__ == "__main__":
    main()
