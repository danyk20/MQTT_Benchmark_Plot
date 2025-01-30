import ast
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

from config import description, expected_payload, required_throughput

data_folder = 'data' if len(sys.argv) == 1 else sys.argv[1]


def format_subscriber(subscribers_number: str) -> str:
    if '00' in subscribers_number:
        return subscribers_number[:-2] + "x100"
    else:
        return subscribers_number


def average_agg_files(data_dir: str) -> None:
    """
    Averages .agg files in a directory and its subdirectories.

    Args:
        data_dir: The root directory to search for .agg files.

    Returns:
        None. Saves the averaged results to .txt files with the same name as the original .agg files.
    """

    for root, _, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.agg'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    data = np.array([eval(line) for line in f.readlines()])

                # Calculate the average along the first axis (across files)
                avg_data = np.mean(data, axis=0)

                # Save the averaged data to a .txt file
                output_file = file_path.replace('.agg', '.txt')
                with open(output_file, 'w') as f:
                    result = []
                    for row in avg_data:
                        result.append(str(row.tolist()))
                    f.write("[" + ','.join(result) + "]")


def load_data(directory) -> list:
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


average_agg_files(data_folder)

qos = [int(name) for name in os.listdir(data_folder) if os.path.isdir(os.path.join(data_folder, name))]
dataset = dict()
subscribers = [[] for _ in range(len(qos))]
for selected_qos in qos:
    subscribers[selected_qos] = [name for name in os.listdir(os.path.join(data_folder, str(selected_qos))) if
                   os.path.isdir(os.path.join(data_folder, str(selected_qos), name))]
    dataset[selected_qos] = dict()
    for subscriber in subscribers[selected_qos]:
        dataset[selected_qos][subscriber] = load_data(os.path.join(data_folder, str(selected_qos), subscriber))

    subscribers[selected_qos] = list(map(str, sorted(list(map(int, subscribers[selected_qos])))))

# Extracting data for plotting
frequency = dict()
bandwidth = dict()
for selected_qos in qos:
    frequency[selected_qos] = dict()
    bandwidth[selected_qos] = dict()
    for subscriber in subscribers[selected_qos]:
        frequency[selected_qos][subscriber] = [entry[3] for entry in dataset[selected_qos][subscriber]]
        bandwidth[selected_qos][subscriber] = [entry[2] / 1e6 for entry in dataset[selected_qos][subscriber]]
sizes = [entry[1] for entry in dataset[qos[0]][subscribers[selected_qos][0]]]

# Plotting
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))

# Frequency plot
ax1.set_title("Frequency and Bandwidth vs Size")
for selected_qos in qos:
    for subscriber in subscribers[selected_qos]:
        mark = 'o-' if selected_qos == '0' else 'v-'
        ax1.loglog(sizes, frequency[selected_qos][subscriber], mark,
                   label=format_subscriber(subscriber) + " - Subscribers; QoS - " + str(selected_qos))

if expected_payload > 0:
    ax1.axvline(x=expected_payload * 1024, color='red', linestyle='--')
    ax1.annotate('requirement', xy=(expected_payload * 1024, ax1.get_ylim()[0]),
                 xytext=(80 * 1024, ax1.get_ylim()[0] * 2),
                 arrowprops=dict(facecolor='red', arrowstyle='->'),
                 fontsize=12, color='red')

ax1.set_ylabel("Frequency (Hz)")
ax1.grid(True, which="both", linestyle="--", linewidth=0.5)
ax1.legend()
ax1.set_xticks([])  # Remove x-axis labels for top plot

# Bandwidth plot

for selected_qos in qos:
    for subscriber in subscribers[selected_qos]:
        mark = 'o-' if selected_qos == '0' else 'v-'
        ax2.loglog(sizes, bandwidth[selected_qos][subscriber], mark,
                   label=format_subscriber(subscriber) + " - Subscriber; QoS - " + str(selected_qos))
if expected_payload > 0:
    ax2.axvline(x=expected_payload * 1024, color='red', linestyle='--')
    ax2.annotate('requirement', xy=(expected_payload * 1024, ax2.get_ylim()[0]),
                 xytext=(80 * 1024, ax2.get_ylim()[0] * 2),
                 arrowprops=dict(facecolor='red', arrowstyle='->'),
                 fontsize=12, color='red')

ax2.axhline(y=required_throughput, color='g', linestyle='--', label=f'Requirement {required_throughput} MB/s')
ax2.set_xlabel("Size (KB)")
ax2.set_ylabel("Bandwidth (MBps)")
ax2.grid(True, which="both", linestyle="--", linewidth=0.5)
ax2.legend()

# Add overall x-axis ticks
for ax in [ax1, ax2]:
    ax.set_xticks(sizes)
    ax.set_xticklabels([f"{size // 1024}KB" for size in sizes], rotation=45)

# Adding a description box
fig.text(0.5, 0.02, description, ha='center', fontsize=12, bbox=dict(facecolor='white', alpha=0.8))

plt.tight_layout(rect=(0.0, 0.05, 1.0, 1.0))
plt.show()
