import matplotlib.pyplot as plt

from manual_input import display_data, info


def prepare_combined_plot_data(all_broker_data):
    """
    Prepares broker performance data for plotting, organizing it by broker and QoS.

    Args:
        all_broker_data (dict): Data for multiple brokers. Keys are broker names,
                                 values are dictionaries mapping (publisher, qos)
                                 tuples to (bytes_per_second, messages_per_second) tuples.

    Returns:
        dict: Transformed data for plotting. Includes a list of all publishers
              and, for each broker, lists of publishers, BPS, and MPS per QoS type.
    """
    all_publishers = sorted(list(set(
        p[0] for broker_data in all_broker_data.values() for p in broker_data.keys()
    )))

    combined_data = {
        'publishers': all_publishers,
    }

    for broker_name, broker_data in all_broker_data.items():
        combined_data[broker_name] = {}

        qos_types = sorted(list(set(k[1] for k in broker_data.keys())))

        for qos_type in qos_types:
            bps_list = []
            mps_list = []
            publishers_list = []

            for pub in all_publishers:
                if (pub, qos_type) in broker_data:
                    bps, mps = broker_data[(pub, qos_type)]
                    publishers_list.append(pub)
                    bps_list.append(bps)
                    mps_list.append(mps)

            combined_data[broker_name][f'publishers_{qos_type}'] = publishers_list
            combined_data[broker_name][f'bps_{qos_type}'] = bps_list
            combined_data[broker_name][f'mps_{qos_type}'] = mps_list

    return combined_data


def plot_mqtt_performance(data, info_label):
    """
    Generates a two-subplot comparison plot for MQTT broker performance,
    displaying Bytes per Second (B/s) and Messages per Second (msg/s).

    Args:
        data (dict): Original data containing broker information.
        info_label (str): Additional information to display at the bottom of the plot.
    """

    combined_plot_data = prepare_combined_plot_data(data)
    fig, axs = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle('MQTT Broker Performance Comparison', fontsize=16)

    plot_metric(axs[0], combined_plot_data, display_data.keys(),
                metric_prefix='bps', title='Bytes per Second (B/s)',
                y_label='Bytes per Second (B/s)', requirement_val=1782579,
                requirement_label='Requirement 1782579 B/s')

    plot_metric(axs[1], combined_plot_data, display_data.keys(),
                metric_prefix='mps', title='Messages per Second (msg/s)',
                y_label='Messages per Second (msg/s)', requirement_val=96,
                requirement_label='Requirement 96 msg/s')

    axs[0].legend()
    axs[0].grid(True)
    axs[1].legend()
    axs[1].grid(True)

    if info_label:
        fig.text(0.5, 0.02, info_label, ha='center', fontsize=10,
                 bbox=dict(facecolor='white', alpha=0.8))

    plt.tight_layout(rect=(0.0, 0.05, 1.0, 1.0))
    plt.show()

def plot_metric(ax, combined_plot_data, legends, metric_prefix, title, y_label, requirement_val, requirement_label):
    """
    Helper function to plot a specific metric (B/s or msg/s) on a given axes.

    Args:
        ax (matplotlib.axes.Axes): The ax object to plot on.
        combined_plot_data (dict): Processed data for plotting.
        legends (list): Data labels for legend.
        metric_prefix (str): Prefix for the metric keys (e.g., 'bps', 'mps').
        title (str): Title for the subplot.
        y_label (str): Label for the y-axis.
        requirement_val (int/float): The value for the horizontal requirement line.
        requirement_label (str): Label for the requirement line.
    """
    markers = ['o', 's', 'x', '^', 'v', '<', '>', 'p', '*', 'h', '+', 'D']
    styles = ['-', '--', ':', '-.']
    for i, legend_name in enumerate(legends):
        broker_plot_data = combined_plot_data[legend_name]
        marker = markers[i % len(markers)]

        qos_types_for_broker = sorted(list(set(k.split('_')[1] for k in broker_plot_data.keys()
                                                if k.startswith(f'{metric_prefix}_'))))

        for j, qos_type in enumerate(qos_types_for_broker):
            line_style = styles[j % len(styles)]

            ax.plot(broker_plot_data[f'publishers_{qos_type}'],
                    broker_plot_data[f'{metric_prefix}_{qos_type}'],
                    marker=marker, linestyle=line_style, label=f'{legend_name} {qos_type}')

    ax.axhline(y=requirement_val, color='r', linestyle='--', label=requirement_label)
    ax.set_title(title)
    ax.set_xlabel('Number of Publishers')
    ax.set_ylabel(y_label)



plot_mqtt_performance(display_data, info)