import psutil
import time
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import threading
import streamlit as st

def get_system_metrics():
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory().percent,
        "disk":psutil.disk_usage('/').percent,
        "network": psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv  
    }

def live_dashboard():
    cpu_data, memory_data, disk_data, network_data, time_data = [], [], [], [], []
    start_time = time.time()
    
    # Create a plot with subplots
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, subplot_titles=("CPU Usage (%)", "Memory Usage (%)", "Disk Usage (%)", "Network Activity (bytes)"))
    
    # Initialize plots
    cpu_trace = go.Scatter(y=[], mode="lines", name="CPU")
    memory_trace = go.Scatter(y=[], mode="lines", name="Memory")
    disk_trace = go.Scatter(y=[], mode="lines", name="Disk")
    network_trace = go.Scatter(y=[], mode="lines", name="Network")
    
    fig.add_trace(cpu_trace, row=1, col=1)
    fig.add_trace(memory_trace, row=2, col=1)
    fig.add_trace(disk_trace, row=3, col=1)
    fig.add_trace(network_trace, row=4, col=1)
    
    # Update figure dynamically
    while True:
        metrics = get_system_metrics()
        current_time = time.time() - start_time
        
        # Update data arrays
        cpu_data.append(metrics['cpu'])
        memory_data.append(metrics['memory'])
        disk_data.append(metrics['disk'])
        network_data.append(metrics['network'])
        time_data.append(current_time)
        
        # Update traces
        fig.data[0].y = cpu_data
        fig.data[0].x = time_data
        fig.data[1].y = memory_data
        fig.data[1].x = time_data
        fig.data[2].y = disk_data
        fig.data[2].x = time_data
        fig.data[3].y = network_data
        fig.data[3].x = time_data
        
        #Re-render the plot
        fig.update_layout(height=800, title="Dynamic Resource Monitor")
        fig.show(renderer="browser")
        
        time.sleep(1)
        
if __name__ == "__main__":
    dashboard_thread = threading.Thread(target=live_dashboard, daemon=True)
    dashboard_thread.start()
    
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("Exiting...")
            break