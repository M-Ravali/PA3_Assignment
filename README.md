# Pantheon Congestion Control Evaluation

This repository contains the implementation, analysis, and results of Programming Assignment 3 for Computer Networks (Spring 2025). The project evaluates the performance of different congestion control algorithms using the Pantheon framework and MahiMahi network emulator.

## Overview

This project compares three congestion control protocols (BBR, Cubic, and Vegas) under two different network conditions:
1. High bandwidth, low latency (50 Mbps, 10 ms RTT)
2. Low bandwidth, high latency (1 Mbps, 200 ms RTT)

The evaluation measures throughput, latency, and packet loss for each protocol to identify their strengths and weaknesses in diverse network environments.

## Requirements

- Linux operating system (tested on Ubuntu 18.04)
- Python 2.7 (for Pantheon)
- Python packages: matplotlib, numpy, pandas
- Git
- Build essentials

## Installation and Setup

### 1. Install System Dependencies

```bash
# Update package lists
sudo apt update && sudo apt upgrade -y

# Install basic dependencies
sudo apt install -y build-essential dkms linux-headers-$(uname -r)
sudo apt install -y build-essential zlib1g-dev libncurses5-dev \
libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget

# Install Python 2.7 (if not already installed)
cd /tmp
wget https://www.python.org/ftp/python/2.7.18/Python-2.7.18.tgz
tar -xf Python-2.7.18.tgz
cd Python-2.7.18
./configure --prefix=/opt/python2.7
make -j$(nproc)
sudo make install
sudo ln -s /opt/python2.7/bin/python2.7 /usr/bin/python

# Verify Python installation
python --version

# Install pip for Python 2.7
curl https://bootstrap.pypa.io/pip/2.7/get-pip.py -o get-pip.py
python get-pip.py

# Update PATH
export PATH=$PATH:~/.local/bin
echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
source ~/.bashrc

# Verify pip installation
pip2 --version

# Install required Python packages
pip2 install --user pyyaml==5.1.2
```

### 2. Clone Pantheon Repository

```bash
git clone https://github.com/StanfordSNR/pantheon.git
cd pantheon
```

### 3. Install MahiMahi

```bash
# Clone MahiMahi inside Pantheon's third_party directory
mkdir -p third_party
cd third_party
git clone https://github.com/ravinet/mahimahi.git
cd mahimahi

# Install MahiMahi dependencies
sudo apt install -y libxcb-xinerama0 libpangocairo-1.0-0
sudo apt install -y libprotobuf-dev protobuf-compiler libssl-dev libhttp-parser-dev libalglibdev libcap-dev libnl-3-dev libnl-genl-3-dev libnl-route-3-dev
sudo apt install -y apache2
sudo apt install -y apache2-dev
sudo apt install -y libxcb-present0 libxcb-present-dev
sudo apt install -y libpango1.0-dev libcairo2-dev libgtk2.0-dev libx11-dev

# Build and install MahiMahi
./autogen.sh
./configure
make
sudo make install

# Enable IP forwarding
sudo sysctl -w net.ipv4.ip_forward=1
```

### 4. Clone This Repository

```bash
git clone https://github.com/[your-username]/pantheon-evaluation.git
cd pantheon-evaluation
```

### 5. Set Up Project Structure

```bash
# Create necessary directories
mkdir -p scripts
mkdir -p traces
mkdir -p graphs

# Copy the scripts from the repository
cp scripts/analyze_results.py ~/pantheon/scripts/
cp scripts/generate_traces.py ~/pantheon/scripts/

# Make scripts executable
chmod +x ~/pantheon/scripts/analyze_results.py
chmod +x ~/pantheon/scripts/generate_traces.py
```

## Running Experiments

### 1. Generate Trace Files

```bash
cd ~/pantheon
python scripts/generate_traces.py
```

### 2. Install Congestion Control Schemes

```bash
cd ~/pantheon
python src/wrappers/cubic.py deps
python src/wrappers/bbr.py deps
python src/wrappers/vegas.py deps

# Set up the schemes
python src/experiments/setup.py --install-deps --schemes "cubic bbr vegas"
python src/experiments/setup.py --setup --schemes "cubic bbr vegas"
```

### 3. Run Experiments

#### High Bandwidth, Low Latency Scenario (50 Mbps, 10 ms RTT)

```bash
cd ~/pantheon
python src/experiments/test.py local \
  --schemes "vegas cubic bbr" \
  --run-times 1 \
  --runtime 60 \
  --data-dir results_50mbps_10ms \
  --uplink-trace traces/50mbps.trace \
  --downlink-trace traces/50mbps.trace \
  --prepend-mm-cmds "mm-delay 5"
```

#### Low Bandwidth, High Latency Scenario (1 Mbps, 200 ms RTT)

```bash
cd ~/pantheon
python src/experiments/test.py local \
  --schemes "vegas cubic bbr" \
  --run-times 1 \
  --runtime 60 \
  --data-dir results_1mbps_200ms \
  --uplink-trace traces/1mbps.trace \
  --downlink-trace traces/1mbps.trace \
  --prepend-mm-cmds "mm-delay 100"
```

## Data Analysis

### Analyze Results and Generate Graphs

```bash
cd ~/pantheon
python scripts/analyze_results.py
```

This script will:
1. Load performance data from both experiments
2. Generate time-series plots for throughput and loss
3. Create comparison graphs for RTT, throughput vs. RTT, and loss rates
4. Save all graphs to the `graphs` directory
5. Print summary statistics for analysis

## Results

The analysis compares the three congestion control algorithms based on:

1. **Throughput Performance**: Examining how efficiently each algorithm utilizes available bandwidth
2. **Loss Patterns**: Analyzing packet loss behavior under different network conditions
3. **RTT Values**: Measuring latency impact and queue buildup
4. **Combined Performance**: Evaluating the throughput vs. latency trade-off

Key findings include:
- Cubic achieves highest throughput but causes significant latency and loss
- Vegas provides the best balance between throughput and latency
- BBR maintains low loss rates but shows unexpectedly low throughput in our tests

## File Structure

```
.
├── README.md
├── scripts/
│   ├── analyze_results.py   # Script for data analysis and visualization
│   └── generate_traces.py   # Script for generating trace files
├── traces/
│   ├── 1mbps.trace          # Low bandwidth trace file
│   └── 50mbps.trace         # High bandwidth trace file
├── results_50mbps_10ms/     # Results from high-bandwidth experiment
│   ├── pantheon_metadata.json
│   ├── pantheon_perf.json
│   └── logs/                # Detailed log files
├── results_1mbps_200ms/     # Results from low-bandwidth experiment
│   ├── pantheon_metadata.json
│   ├── pantheon_perf.json
│   └── logs/                # Detailed log files
└── graphs/                  # Generated visualizations
    ├── high_bw_throughput_timeseries.png
    ├── low_bw_throughput_timeseries.png
    ├── high_bw_loss_timeseries.png
    ├── low_bw_loss_timeseries.png
    ├── avg_rtt_comparison.png
    ├── loss_rate_comparison.png
    └── rtt_vs_throughput.png
```

## Troubleshooting

### Common Issues

1. **Pantheon Installation**:
   - If you encounter errors with specific congestion control schemes, try installing them individually.
   - Some schemes might require additional dependencies not covered in the basic setup.

2. **MahiMahi Issues**:
   - If MahiMahi commands fail with permission errors, make sure you have run `sudo sysctl -w net.ipv4.ip_forward=1`
   - If experiencing "mm-delay: command not found", verify MahiMahi installation with `which mm-delay`

3. **Python Version Conflicts**:
   - Pantheon requires Python 2.7. If you have multiple Python versions, ensure you're using the correct one.
   - Use `python --version` to verify before running scripts.

4. **Analysis Script Errors**:
   - If matplotlib throws errors, install it with `pip2 install --user matplotlib`
   - For pandas errors, install with `pip2 install --user pandas`

### Verifying Experiment Success

To verify that your experiments ran successfully:

1. Check that result directories contain JSON files:
   ```bash
   ls -la results_50mbps_10ms/
   ls -la results_1mbps_200ms/
   ```

2. Examine performance JSON files:
   ```bash
   cat results_50mbps_10ms/pantheon_perf.json
   cat results_1mbps_200ms/pantheon_perf.json
   ```

3. Look for log files with data:
   ```bash
   ls -la results_50mbps_10ms/logs/
   ls -la results_1mbps_200ms/logs/
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Pantheon framework from Stanford University
- MahiMahi network emulation toolkit from MIT
- Assignment guidelines from Computer Networks course, Spring 2025
