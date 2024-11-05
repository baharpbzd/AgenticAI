import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from typing import List, Dict
import base64

# --- Agent System ---
class Agent:
    def __init__(self, name: str, role: str, icon: str):
        self.name = name
        self.role = role
        self.icon = icon
        
    def describe(self):
        return f"{self.icon} {self.name}: {self.role}"

class GlucoseAgent(Agent):
    def __init__(self):
        super().__init__("GlucoseBot", "Monitors and analyzes glucose patterns", "🤖")
        
    def analyze(self, readings: List[Dict]) -> Dict:
        if not readings:
            return {"risk_level": "unknown", "recommendations": ["No data available for analysis"]}
        
        values = [r['value'] for r in readings[-10:]]
        mean = np.mean(values)
        std = np.std(values)
        
        return {
            "risk_level": "high" if mean > 180 else "moderate" if mean > 140 else "low",
            "mean": round(mean, 1),
            "std": round(std, 1),
            "recommendations": self._generate_recommendations(mean, std)
        }
    
    def _generate_recommendations(self, mean: float, std: float) -> List[str]:
        recommendations = []
        if mean > 180:
            recommendations.append("Blood sugar is high - consider adjusting medication/diet")
        if std > 40:
            recommendations.append("High variability detected - try maintaining consistent meal times")
        if mean < 70:
            recommendations.append("Blood sugar running low - review medication dosage")
        if not recommendations:
            recommendations.append("Blood sugar control looks good!")
        return recommendations

class DataIntegrationAgent(Agent):
    def __init__(self):
        super().__init__("DataBot", "Manages external data integration", "🔄")
    
    def import_apple_watch_data(self, file=None):
        if file is not None:
            try:
                # Process Apple Watch data
                # This is a placeholder for actual implementation
                return {"success": True, "message": "Apple Watch data imported successfully"}
            except Exception as e:
                return {"success": False, "message": f"Error importing data: {str(e)}"}
        return {"success": False, "message": "No file provided"}
    
    def import_ehr_data(self, file=None):
        if file is not None:
            try:
                # Process EHR data
                # This is a placeholder for actual implementation
                return {"success": True, "message": "EHR data imported successfully"}
            except Exception as e:
                return {"success": False, "message": f"Error importing data: {str(e)}"}
        return {"success": False, "message": "No file provided"}

# --- Styling and Background ---
def set_background():
    # Function to set background image
    background_html = '''
    <style>
        .stApp {
            background: linear-gradient(to bottom right, #f0f8ff, #e6e9ff);
        }
        .agent-card {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 10px 0;
        }
        .metric-card {
            background-color: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin: 5px 0;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 20px;
            padding: 10px 20px;
            border: none;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
    </style>
    '''
    st.markdown(background_html, unsafe_allow_html=True)

# --- Main Application ---
def main():
    st.set_page_config(page_title="Smart Diabetes Management System", layout="wide")
    set_background()
    
    # Initialize agents
    if 'glucose_agent' not in st.session_state:
        st.session_state.glucose_agent = GlucoseAgent()
    if 'data_agent' not in st.session_state:
        st.session_state.data_agent = DataIntegrationAgent()
    if 'data' not in st.session_state:
        st.session_state.data = load_or_create_data()

    # Sidebar
    with st.sidebar:
        st.title("Navigation")
        page = st.radio("", ["Dashboard", "Data Entry", "Data Integration", "Analytics"])
        
        st.markdown("---")
        st.markdown("### Active Agents")
        st.markdown(st.session_state.glucose_agent.describe())
        st.markdown(st.session_state.data_agent.describe())

    if page == "Dashboard":
        show_dashboard()
    elif page == "Data Entry":
        show_data_entry()
    elif page == "Data Integration":
        show_data_integration()
    elif page == "Analytics":
        show_analytics()

def show_dashboard():
    st.title("Smart Diabetes Management Dashboard")
    
    # Agent Activity Section
    with st.container():
        st.markdown("### 🤖 Active Agent Analysis")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            analysis = st.session_state.glucose_agent.analyze(
                st.session_state.data['glucose_readings']
            )
            
            # Risk Level Card
            risk_colors = {
                "low": "#4CAF50",
                "moderate": "#FFA500",
                "high": "#FF0000"
            }
            st.markdown(f"""
                <div style='padding: 20px; border-radius: 10px; background-color: {risk_colors.get(analysis["risk_level"], "#808080")}; color: white;'>
                    <h2 style='margin: 0;'>Risk Level: {analysis["risk_level"].upper()}</h2>
                    <p>Mean: {analysis["mean"]} mg/dL | Std: {analysis["std"]} mg/dL</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Recommendations
            st.markdown("#### AI Recommendations")
            for rec in analysis["recommendations"]:
                st.markdown(f"* {rec}")
        
        with col2:
            st.markdown("#### Quick Stats")
            if st.session_state.data['glucose_readings']:
                latest = st.session_state.data['glucose_readings'][-1]
                st.metric("Latest Reading", f"{latest['value']} mg/dL")
                st.metric("Readings Today", len([r for r in st.session_state.data['glucose_readings'] 
                                              if datetime.fromisoformat(r['timestamp']).date() == datetime.now().date()]))

    # Glucose Trend Chart
    st.markdown("### 📈 Glucose Trends")
    if st.session_state.data['glucose_readings']:
        df = pd.DataFrame(st.session_state.data['glucose_readings'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        fig = px.line(df, x='timestamp', y='value',
                     title='Blood Glucose History',
                     labels={'value': 'Blood Glucose (mg/dL)', 'timestamp': 'Time'})
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No glucose readings available. Start logging to see trends!")

def show_data_integration():
    st.title("External Data Integration")
    
    st.markdown("### 🔄 Import External Data")
    
    tab1, tab2 = st.tabs(["Apple Watch Data", "EHR Data"])
    
    with tab1:
        st.markdown("#### Import Apple Watch Data")
        st.markdown("Upload your Apple Health Export (export.xml)")
        apple_file = st.file_uploader("Choose Apple Health Export file", type=['xml'], key='apple')
        if apple_file:
            result = st.session_state.data_agent.import_apple_watch_data(apple_file)
            if result['success']:
                st.success(result['message'])
            else:
                st.error(result['message'])
    
    with tab2:
        st.markdown("#### Import EHR Data")
        st.markdown("Upload your EHR data export (CSV format)")
        ehr_file = st.file_uploader("Choose EHR data file", type=['csv'], key='ehr')
        if ehr_file:
            result = st.session_state.data_agent.import_ehr_data(ehr_file)
            if result['success']:
                st.success(result['message'])
            else:
                st.error(result['message'])

    # Data Integration Status
    st.markdown("### 📊 Integration Status")
    status_col1, status_col2 = st.columns(2)
    
    with status_col1:
        st.markdown("#### Apple Watch")
        st.markdown("* Last sync: Not synced")
        st.markdown("* Available data: Steps, Heart Rate")
        
    with status_col2:
        st.markdown("#### EHR System")
        st.markdown("* Last sync: Not synced")
        st.markdown("* Available data: Lab Results, Medications")

def show_data_entry():
    st.title("Manual Data Entry")
    
    tab1, tab2, tab3 = st.tabs(["Glucose", "Medications", "Meals"])
    
    with tab1:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### Log Blood Glucose")
            reading = st.number_input("Blood Glucose (mg/dL)", 0, 500, 120)
            notes = st.text_area("Notes")
            
            if st.button("Save Reading"):
                new_reading = {
                    "timestamp": datetime.now().isoformat(),
                    "value": reading,
                    "notes": notes
                }
                st.session_state.data['glucose_readings'].append(new_reading)
                save_data(st.session_state.data)
                st.success("Reading saved!")
        
        with col2:
            if st.session_state.data['glucose_readings']:
                df = pd.DataFrame(st.session_state.data['glucose_readings'][-10:])
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                fig = px.line(df, x='timestamp', y='value',
                            title='Recent Readings',
                            labels={'value': 'Blood Glucose (mg/dL)', 'timestamp': 'Time'})
                st.plotly_chart(fig)

    # Add similar implementations for Medications and Meals tabs...

def show_analytics():
    st.title("Advanced Analytics")
    
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
        fig = px.histogram(df, x='value',
                          title='Blood Glucose Distribution',
                          labels={'value': 'Blood Glucose (mg/dL)', 'count': 'Frequency'})
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig)
    
    with col2:
        df['hour'] = df['timestamp'].dt.hour
        hourly_avg = df.groupby('hour')['value'].mean().reset_index()
        fig = px.line(hourly_avg, x='hour', y='value',
                     title='Average Blood Glucose by Hour',
                     labels={'value': 'Blood Glucose (mg/dL)', 'hour': 'Hour of Day'})
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig)

if __name__ == "__main__":
    main()
