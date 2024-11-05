import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from typing import List, Dict

# --- Styling and Configuration ---
def set_page_config():
    st.set_page_config(
        page_title="Diabetes Management System",
        page_icon="🏥",
        layout="wide"
    )
    
    # Custom CSS for styling
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            background-color: #f8f9fa;
        }
        
        .main {
            background-color: #FFFFFF;
        }
        
        .stButton > button {
            background-color: #007AFF;
            color: white;
            border-radius: 5px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 500;
        }
        
        div[data-testid="stMetricValue"] {
            font-size: 24px;
            font-weight: bold;
        }
        
        .agent-card {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
        }
        
        .metric-container {
            background-color: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        /* Device connection styling */
        .device-status {
            padding: 10px;
            border-radius: 5px;
            margin: 5px 0;
        }
        
        .device-connected {
            background-color: #e7f5e7;
            color: #2e7d32;
        }
        
        .device-disconnected {
            background-color: #ffebee;
            color: #c62828;
        }
        </style>
    """, unsafe_allow_html=True)

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

# --- Device Connection Management ---
def show_device_connection():
    st.title("Device Connections")
    
    # Apple Watch Connection
    st.header("Apple Watch")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### Connection Steps")
        st.markdown("""
        1. Open the Apple Health app on your iPhone
        2. Go to Settings → Privacy → Apps
        3. Enable sharing with Diabetes Manager
        4. Click Connect below
        """)
    
    with col2:
        connection_status = False  # This would be dynamic in production
        if connection_status:
            st.markdown("""
                <div class="device-status device-connected">
                    ✅ Connected
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="device-status device-disconnected">
                    ❌ Not Connected
                </div>
            """, unsafe_allow_html=True)
        
        st.button("Connect Apple Watch")
    
    # Data Sync Status
    st.header("Data Sync Status")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Last Sync", "Never")
    with col2:
        st.metric("Steps Today", "0")
    with col3:
        st.metric("Heart Rate", "-- bpm")
    
    # Available Data Types
    st.header("Available Data")
    st.markdown("""
    - ⌚ Heart Rate Monitoring
    - 👣 Step Counter
    - 🏃‍♂️ Exercise Minutes
    - 🔄 Blood Glucose (requires compatible sensor)
    """)

# --- Main Application Pages ---
def show_dashboard():
    st.title("Dashboard")
    
    # Quick Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Latest Glucose",
            "120 mg/dL",
            "↑ 5%"
        )
    with col2:
        st.metric(
            "Daily Average",
            "118 mg/dL",
            "↓ 2%"
        )
    with col3:
        st.metric(
            "Readings Today",
            "4",
            None
        )
    
    # Glucose Chart
    st.header("Glucose Trends")
    if st.session_state.data['glucose_readings']:
        df = pd.DataFrame(st.session_state.data['glucose_readings'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        fig = px.line(
            df, 
            x='timestamp', 
            y='value',
            labels={'value': 'Blood Glucose (mg/dL)', 'timestamp': 'Time'}
        )
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(t=20, l=40, r=20, b=40)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No glucose readings available. Start logging to see trends!")
    
    # Recent Logs
    st.header("Recent Activity")
    if st.session_state.data['glucose_readings']:
        for reading in reversed(st.session_state.data['glucose_readings'][-5:]):
            st.markdown(f"""
            <div class="metric-container">
                🔵 {reading['value']} mg/dL at {datetime.fromisoformat(reading['timestamp']).strftime('%I:%M %p')}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent activity to display")

def show_data_entry():
    st.title("Log Data")
    
    tab1, tab2, tab3 = st.tabs(["Glucose", "Medications", "Meals"])
    
    with tab1:
        col1, col2 = st.columns([1, 2])
        
        with col1:
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
                st.success("Reading saved successfully!")
        
        with col2:
            if st.session_state.data['glucose_readings']:
                df = pd.DataFrame(st.session_state.data['glucose_readings'][-10:])
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                fig = px.line(df, x='timestamp', y='value',
                            labels={'value': 'Blood Glucose (mg/dL)', 'timestamp': 'Time'})
                fig.update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    margin=dict(t=20, l=40, r=20, b=40)
                )
                st.plotly_chart(fig)

def show_analytics():
    st.title("Analytics")
    
    if not st.session_state.data['glucose_readings']:
        st.warning("No data available for analysis. Please log some readings first.")
        return
    
    # Time range selector
    time_range = st.selectbox(
        "Select Time Range",
        ["Last 7 Days", "Last 30 Days", "All Time"]
    )
    
    df = pd.DataFrame(st.session_state.data['glucose_readings'])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    if time_range == "Last 7 Days":
        df = df[df['timestamp'] >= datetime.now() - timedelta(days=7)]
    elif time_range == "Last 30 Days":
        df = df[df['timestamp'] >= datetime.now() - timedelta(days=30)]
    
    # Statistics
    st.header("Statistics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Average", f"{df['value'].mean():.1f}")
    with col2:
        st.metric("Std Dev", f"{df['value'].std():.1f}")
    with col3:
        st.metric("Minimum", f"{df['value'].min():.1f}")
    with col4:
        st.metric("Maximum", f"{df['value'].max():.1f}")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.histogram(
            df, 
            x='value',
            title='Glucose Distribution',
            labels={'value': 'Blood Glucose (mg/dL)', 'count': 'Frequency'}
        )
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        st.plotly_chart(fig)
    
    with col2:
        df['hour'] = df['timestamp'].dt.hour
        hourly_avg = df.groupby('hour')['value'].mean().reset_index()
        fig = px.line(
            hourly_avg,
            x='hour',
            y='value',
            title='Average by Hour',
            labels={'value': 'Blood Glucose (mg/dL)', 'hour': 'Hour of Day'}
        )
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        st.plotly_chart(fig)

def main():
    set_page_config()
    
    if 'data' not in st.session_state:
        st.session_state.data = load_or_create_data()
    
    # Sidebar navigation
    with st.sidebar:
        st.title("Diabetes Manager")
        st.markdown("---")
        
        pages = {
            "📊 Dashboard": show_dashboard,
            "📱 Device Connections": show_device_connection,
            "📝 Log Data": show_data_entry,
            "📈 Analytics": show_analytics
        }
        
        page = st.radio("Navigation", list(pages.keys()))
        
        st.markdown("---")
        st.markdown("### System Status")
        device_status = "🔴 Disconnected"  # This would be dynamic
        st.markdown(f"Apple Watch: {device_status}")
        last_sync = "Never"  # This would be dynamic
        st.markdown(f"Last Sync: {last_sync}")
    
    # Display selected page
    pages[page]()

if __name__ == "__main__":
    main()
