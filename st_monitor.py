import psutil
import time
import pandas as pd
import streamlit as st

# Initialize data storage
metrics_data = {
    "Time": [],
    "CPU (%)": [],
    "Memory (%)": [],
    "Disk (%)": [],
    "Network (MB)": []
}

# Streamlit app setup
st.title("Enhanced Dynamic Resource Monitor")
st.markdown("Real-time tracking of system performance with advanced features.")
st.sidebar.header("Settings")

# Sidebar settings
refresh_rate = st.sidebar.slider("Refresh Interval (seconds)", min_value=0.5, max_value=5.0, value=1.0)
time_window = st.sidebar.slider("Time Window (seconds)", min_value=10, max_value=300, value=60)

# Thresholds for alerts
cpu_threshold = st.sidebar.slider("CPU Usage Alert (%)", min_value=50, max_value=100, value=90)
memory_threshold = st.sidebar.slider("Memory Usage Alert (%)", min_value=50, max_value=100, value=90)

# Add export button
if st.sidebar.button("Download Metrics Data"):
    csv = pd.DataFrame(metrics_data).to_csv(index=False)
    st.sidebar.download_button(label="Download Metrics", data=csv, file_name="metrics_data.csv", mime="text/csv")

# Display placeholders for charts and metrics
st.subheader("Resource Usage Over Time")
cpu_chart = st.line_chart()
memory_chart = st.line_chart()
disk_chart = st.line_chart()
network_chart = st.line_chart()

st.subheader("Current Metrics")
metrics_placeholder = st.empty()

st.subheader("Top Processes by CPU Usage")
processes_placeholder = st.empty()

st.subheader("Idle Time Tracker")
idle_placeholder = st.empty()

# Function to get system metrics
def get_system_metrics():
    network_bytes = psutil.net_io_counters()
    return {
        "cpu": psutil.cpu_percent(interval=0),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "network": (network_bytes.bytes_sent + network_bytes.bytes_recv) / (1024 ** 2),  # Convert to MB
        "idle": psutil.cpu_times().idle / (psutil.cpu_times().idle + psutil.cpu_times().user + psutil.cpu_times().system)
    }

# Function to get top processes
def get_top_processes():
    processes = [(p.info['name'], p.info['cpu_percent']) for p in psutil.process_iter(['name', 'cpu_percent'])]
    return pd.DataFrame(processes, columns=["Process", "CPU (%)"]).sort_values(by="CPU (%)", ascending=False).head(10)

# Function to get CPU temperature (if available)
def get_cpu_temperature():
    try:
        from psutil._psplatform import sensors_temperatures
        temps = sensors_temperatures()
        if "coretemp" in temps:
            return temps["coretemp"][0].current
        return None
    except ImportError:
        return None

# Monitoring loop
def monitor_resources():
    start_time = time.time()
    while True:
        # Collect metrics
        metrics = get_system_metrics()
        current_time = round(time.time() - start_time, 2)

        # Append metrics data
        metrics_data["Time"].append(current_time)
        metrics_data["CPU (%)"].append(metrics["cpu"])
        metrics_data["Memory (%)"].append(metrics["memory"])
        metrics_data["Disk (%)"].append(metrics["disk"])
        metrics_data["Network (MB)"].append(metrics["network"])

        # Trim data to fit the time window
        for key in metrics_data:
            if len(metrics_data[key]) > time_window:
                metrics_data[key] = metrics_data[key][-time_window:]

        # Update charts
        metrics_df = pd.DataFrame(metrics_data)
        cpu_chart.line_chart(metrics_df[["Time", "CPU (%)"]].set_index("Time"))
        memory_chart.line_chart(metrics_df[["Time", "Memory (%)"]].set_index("Time"))
        disk_chart.line_chart(metrics_df[["Time", "Disk (%)"]].set_index("Time"))
        network_chart.line_chart(metrics_df[["Time", "Network (MB)"]].set_index("Time"))

        # Update current metrics display
        alert_style = lambda value, threshold: f"**:red[{value}%]**" if value > threshold else f"**{value}%**"
        metrics_placeholder.markdown(f"""
            - **CPU Usage**: {alert_style(metrics['cpu'], cpu_threshold)}  
            - **Memory Usage**: {alert_style(metrics['memory'], memory_threshold)}  
            - **Disk Usage**: **{metrics['disk']}%**  
            - **Network Activity**: **{metrics['network']:.2f} MB**  
            - **CPU Temperature**: **{get_cpu_temperature() or 'N/A'}°C**
        """)

        # Update top processes
        processes_placeholder.table(get_top_processes())

        # Update idle time tracker
        idle_placeholder.markdown(f"**System Idle Time**: **{metrics['idle'] * 100:.2f}%**")

        time.sleep(refresh_rate)

# Run the app
if __name__ == "__main__":
    monitor_resources()
