import ast
import os

import matplotlib.pyplot as plt
import numpy as np


def load_data(directory):
    """
    Load and process data from files in the given directory.
    If there are multiple files, compute the average of corresponding data points.
    """
    data = []
    files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.txt')]

    for file in files:
        with open(file, 'r') as f:
            # Safely evaluate the Python-style list in the file
            file_data = ast.literal_eval(f.read().strip())
            data.append(np.array(file_data))

    # If multiple files, compute the average
    if len(data) > 1:
        data = np.mean(data, axis=0).astype(int)
    else:
        data = data[0]

    return data.tolist()

# Load data from directories
subscribers_1 = load_data('data/1')
subscribers_2 = load_data('data/2')
subscribers_3 = load_data('data/3')

# Extracting data for plotting
sizes = [entry[1] for entry in subscribers_1]
freq_1 = [entry[3] for entry in subscribers_1]
freq_2 = [entry[3] for entry in subscribers_2]
freq_3 = [entry[3] for entry in subscribers_3]

bandwidth_1 = [entry[2] / 1e6 for entry in subscribers_1]  # Convert to Mbps
bandwidth_2 = [entry[2] / 1e6 for entry in subscribers_2]  # Convert to Mbps
bandwidth_3 = [entry[2] / 1e6 for entry in subscribers_3]  # Convert to Mbps

# Plotting
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))

# Frequency plot
ax1.set_title("Frequency and Bandwidth vs Size")
ax1.loglog(sizes, freq_1, 'o-', label="1 - Subscriber")
ax1.loglog(sizes, freq_2, 's-', label="2 - Subscribers")
ax1.loglog(sizes, freq_3, '^-', label="3 - Subscribers")
ax1.set_ylabel("Frequency (Hz)")
ax1.grid(True, which="both", linestyle="--", linewidth=0.5)
ax1.legend()
ax1.set_xticks([])  # Remove x-axis labels for top plot

# Bandwidth plot
ax2.loglog(sizes, bandwidth_1, 'o-', label="1 - Subscriber")
ax2.loglog(sizes, bandwidth_2, 's-', label="2 - Subscribers")
ax2.loglog(sizes, bandwidth_3, '^-', label="3 - Subscribers")
ax2.set_xlabel("Size (KB)")
ax2.set_ylabel("Bandwidth (Mbps)")
ax2.grid(True, which="both", linestyle="--", linewidth=0.5)
ax2.legend()

# Add overall x-axis ticks
for ax in [ax1, ax2]:
    ax.set_xticks(sizes)
    ax.set_xticklabels([f"{size // 1024}KB" for size in sizes], rotation=45)

plt.tight_layout()
plt.show()
