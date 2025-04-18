#!/usr/bin/env python

import os

def create_trace_file(filename, bandwidth_mbps):
    """
    Create a trace file for MahiMahi with constant bandwidth
    
    Args:
        filename: Output filename
        bandwidth_mbps: Bandwidth in Mbps
    """
    # Convert Mbps to bytes per millisecond (needed by MahiMahi)
    # 1 Mbps = 1,000,000 bits per second = 125,000 bytes per second
    # For millisecond granularity: 125,000 / 1000 = 125 bytes per millisecond
    bytes_per_ms = int(bandwidth_mbps * 125)
    
    # Create a file with constant bandwidth (same value repeated)
    # MahiMahi expects one number per line, each representing bytes available in 1ms
    with open(filename, 'w') as f:
        # Write the same bandwidth value for 60 seconds (60,000 ms)
        for _ in range(60000):
            f.write("{0}\n".format(bytes_per_ms))
    
    print("Created trace file '{0}' with constant {1} Mbps".format(filename, bandwidth_mbps))

def main():
    # Create traces directory if it doesn't exist
    if not os.path.exists('traces'):
        os.makedirs('traces')
    
    # Create 50 Mbps trace file
    create_trace_file('traces/50mbps.trace', 50)
    
    # Create 1 Mbps trace file
    create_trace_file('traces/1mbps.trace', 1)
    
    print("Trace files created successfully!")

if __name__ == "__main__":
    main()
