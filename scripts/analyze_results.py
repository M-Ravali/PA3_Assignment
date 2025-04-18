import json
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import glob
import re

# Set matplotlib style for better looking graphs
plt.style.use('ggplot')
plt.rcParams.update({'font.size': 12})

# Create output directories for saving graphs
if not os.path.exists('graphs'):
    os.makedirs('graphs')

# 1. Load performance data
def load_perf_data(filename):
    with open(filename, 'r') as f:
        return json.load(f)

# Load the performance data for both scenarios
high_bw_data = load_perf_data('results_50mbps_10ms/pantheon_perf.json')
low_bw_data = load_perf_data('results_1mbps_200ms/pantheon_perf.json')

# 2. Load time-series data for more detailed analysis
def parse_throughput_logs(log_dir):
    """Parse throughput logs from Pantheon experiments"""
    data = {}
    
    # Find all throughput log files
    log_files = glob.glob(os.path.join(log_dir, "*throughput.log"))
    
    for log_file in log_files:
        # Extract scheme name from filename
        scheme = re.search(r'([a-z]+)_throughput\.log', os.path.basename(log_file)).group(1)
        
        # Read the log file
        df = pd.read_csv(log_file, sep=' ', header=None, 
                         names=['timestamp', 'throughput'])
        
        # Convert timestamp to seconds from start
        if len(df) > 0:
            start_time = df['timestamp'].iloc[0]
            df['time'] = df['timestamp'] - start_time
            data[scheme] = df
    
    return data

def parse_delay_logs(log_dir):
    """Parse delay logs from Pantheon experiments"""
    data = {}
    
    # Find all delay log files
    log_files = glob.glob(os.path.join(log_dir, "*delay.log"))
    
    for log_file in log_files:
        # Extract scheme name from filename
        scheme = re.search(r'([a-z]+)_delay\.log', os.path.basename(log_file)).group(1)
        
        # Read the log file
        df = pd.read_csv(log_file, sep=' ', header=None, 
                         names=['timestamp', 'delay'])
        
        # Convert timestamp to seconds from start
        if len(df) > 0:
            start_time = df['timestamp'].iloc[0]
            df['time'] = df['timestamp'] - start_time
            data[scheme] = df
    
    return data

def parse_loss_logs(log_dir):
    """Parse loss logs from Pantheon experiments"""
    data = {}
    
    # Find all loss log files
    log_files = glob.glob(os.path.join(log_dir, "*loss.log"))
    
    for log_file in log_files:
        # Extract scheme name from filename
        scheme = re.search(r'([a-z]+)_loss\.log', os.path.basename(log_file)).group(1)
        
        # Read the log file
        try:
            df = pd.read_csv(log_file, sep=' ', header=None, 
                             names=['timestamp', 'loss'])
            
            # Convert timestamp to seconds from start
            if len(df) > 0:
                start_time = df['timestamp'].iloc[0]
                df['time'] = df['timestamp'] - start_time
                data[scheme] = df
        except:
            print("Couldn't parse %s" % log_file)
    
    return data

# Try to parse time-series data if available
try:
    high_bw_throughput = parse_throughput_logs('results_50mbps_10ms')
    high_bw_delay = parse_delay_logs('results_50mbps_10ms')
    high_bw_loss = parse_loss_logs('results_50mbps_10ms')
    
    low_bw_throughput = parse_throughput_logs('results_1mbps_200ms')
    low_bw_delay = parse_delay_logs('results_1mbps_200ms')
    low_bw_loss = parse_loss_logs('results_1mbps_200ms')
    
    have_timeseries = True
except Exception as e:
    print("Unable to parse time-series logs: %s" % str(e))
    have_timeseries = False

# If we don't have time-series data, we'll use the performance data summary only
# 3. Extract metrics for each protocol from summary data
def extract_metrics(data):
    metrics = {}
    for protocol in data:
        run_data = data[protocol]['1']['all']
        metrics[protocol] = {
            'throughput': run_data['tput'],
            'delay': run_data['delay'],
            'loss': run_data['loss']
        }
    return metrics

high_bw_metrics = extract_metrics(high_bw_data)
low_bw_metrics = extract_metrics(low_bw_data)

# 4. Create the required plots
# 4.1. Plot time-series throughput for each CC scheme (if available)
if have_timeseries:
    # High bandwidth scenario
    plt.figure(figsize=(12, 6))
    for scheme, data in high_bw_throughput.items():
        plt.plot(data['time'], data['throughput'], label=scheme.upper())
    
    plt.xlabel('Time (s)')
    plt.ylabel('Throughput (Mbps)')
    plt.title('Throughput over Time (50 Mbps, 10 ms RTT)')
    plt.legend()
    plt.grid(True)
    plt.savefig('graphs/high_bw_throughput_timeseries.png', dpi=300)
    
    # Low bandwidth scenario
    plt.figure(figsize=(12, 6))
    for scheme, data in low_bw_throughput.items():
        plt.plot(data['time'], data['throughput'], label=scheme.upper())
    
    plt.xlabel('Time (s)')
    plt.ylabel('Throughput (Mbps)')
    plt.title('Throughput over Time (1 Mbps, 200 ms RTT)')
    plt.legend()
    plt.grid(True)
    plt.savefig('graphs/low_bw_throughput_timeseries.png', dpi=300)

# 4.2. Plot time-series losses for each CC scheme (if available)
if have_timeseries:
    # High bandwidth scenario
    plt.figure(figsize=(12, 6))
    for scheme, data in high_bw_loss.items():
        plt.plot(data['time'], data['loss'], label=scheme.upper())
    
    plt.xlabel('Time (s)')
    plt.ylabel('Loss Rate')
    plt.title('Loss Rate over Time (50 Mbps, 10 ms RTT)')
    plt.legend()
    plt.grid(True)
    plt.savefig('graphs/high_bw_loss_timeseries.png', dpi=300)
    
    # Low bandwidth scenario
    plt.figure(figsize=(12, 6))
    for scheme, data in low_bw_loss.items():
        plt.plot(data['time'], data['loss'], label=scheme.upper())
    
    plt.xlabel('Time (s)')
    plt.ylabel('Loss Rate')
    plt.title('Loss Rate over Time (1 Mbps, 200 ms RTT)')
    plt.legend()
    plt.grid(True)
    plt.savefig('graphs/low_bw_loss_timeseries.png', dpi=300)

# 4.3. Compare average RTT across test scenarios
plt.figure(figsize=(10, 6))
protocols = list(high_bw_metrics.keys())
x = np.arange(len(protocols))
width = 0.35

# Plot average RTT for high bandwidth scenario
high_bw_rtt = [high_bw_metrics[p]['delay'] for p in protocols]
plt.bar(x - width/2, high_bw_rtt, width, label='50 Mbps, 10 ms RTT')

# Plot average RTT for low bandwidth scenario
low_bw_rtt = [low_bw_metrics[p]['delay'] for p in protocols]
plt.bar(x + width/2, low_bw_rtt, width, label='1 Mbps, 200 ms RTT')

plt.xlabel('Protocol')
plt.ylabel('Average RTT (ms)')
plt.title('Average RTT Comparison')
plt.xticks(x, [p.upper() for p in protocols])
plt.legend()
plt.grid(True)
plt.savefig('graphs/avg_rtt_comparison.png', dpi=300)

# 4.4. Plot RTT vs Throughput graph (as specified in the assignment)
plt.figure(figsize=(10, 6))
protocols = list(high_bw_metrics.keys())
colors = {'cubic': 'blue', 'bbr': 'green', 'vegas': 'red'}
markers = {'cubic': 'o', 'bbr': 's', 'vegas': '^'}

for protocol in protocols:
    # Plot high bandwidth point
    plt.scatter(1/high_bw_metrics[protocol]['delay'], high_bw_metrics[protocol]['throughput'], 
               color=colors.get(protocol, 'black'), marker=markers.get(protocol, 'o'), s=100,
               label="%s (50Mbps, 10ms)" % protocol.upper())
    
    # Plot low bandwidth point
    plt.scatter(1/low_bw_metrics[protocol]['delay'], low_bw_metrics[protocol]['throughput'], 
               color=colors.get(protocol, 'black'), marker=markers.get(protocol, 'o'), s=100, alpha=0.5,
               label="%s (1Mbps, 200ms)" % protocol.upper())

plt.xlabel('1/RTT (higher RTT closer to origin)')
plt.ylabel('Throughput (Mbps)')
plt.title('RTT vs Throughput for Different CC Algorithms')
plt.legend()
plt.grid(True)
plt.savefig('graphs/rtt_vs_throughput.png', dpi=300)

# 4.5. Compare loss rates across protocols
plt.figure(figsize=(10, 6))
protocols = list(high_bw_metrics.keys())
x = np.arange(len(protocols))
width = 0.35

# Plot loss rates for high bandwidth scenario
high_bw_loss_rates = [high_bw_metrics[p]['loss'] for p in protocols]
plt.bar(x - width/2, high_bw_loss_rates, width, label='50 Mbps, 10 ms RTT')

# Plot loss rates for low bandwidth scenario
low_bw_loss_rates = [low_bw_metrics[p]['loss'] for p in protocols]
plt.bar(x + width/2, low_bw_loss_rates, width, label='1 Mbps, 200 ms RTT')

plt.xlabel('Protocol')
plt.ylabel('Loss Rate')
plt.title('Loss Rate Comparison')
plt.xticks(x, [p.upper() for p in protocols])
plt.legend()
plt.grid(True)
plt.savefig('graphs/loss_rate_comparison.png', dpi=300)

# Print summary statistics for analysis
print("="*50)
print("SUMMARY STATISTICS FOR ANALYSIS")
print("="*50)

print("\nHigh Bandwidth, Low Latency (50 Mbps, 10 ms RTT):")
for protocol, metrics in high_bw_metrics.items():
    print("%s: Throughput = %.4f Mbps, RTT = %.2f ms, Loss = %.4f" % 
          (protocol.upper(), metrics['throughput'], metrics['delay'], metrics['loss']))

print("\nLow Bandwidth, High Latency (1 Mbps, 200 ms RTT):")
for protocol, metrics in low_bw_metrics.items():
    print("%s: Throughput = %.4f Mbps, RTT = %.2f ms, Loss = %.4f" % 
          (protocol.upper(), metrics['throughput'], metrics['delay'], metrics['loss']))

print("\nAnalysis complete! All graphs saved to the 'graphs' directory.")
