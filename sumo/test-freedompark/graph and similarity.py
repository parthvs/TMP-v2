import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import euclidean, cityblock
from scipy.stats import pearsonr, spearmanr
from fastdtw import fastdtw
from pandas.plotting import table

# === Read merged (real) data ===
merged_data = pd.read_csv(r"C:\Users\USER\projects\TMPv2\sumo\test-freedompark\merged_right_lane_counts.csv")
merged_data = merged_data.dropna(axis=1, how='all')  # drop empty columns

if 'Unnamed: 8' in merged_data.columns:
    merged_data = merged_data.drop(columns=['Unnamed: 8'])

merged_data['Time'] = pd.to_datetime(merged_data['Time'], format='%H:%M:%S', errors='coerce')
merged_data = merged_data.dropna(subset=['Time'])
merged_data.set_index('Time', inplace=True)

# === Read junction (simulated) data ===
junction_data = pd.read_csv(r"C:\Users\USER\projects\TMPv2\sumo\test-freedompark\junction_data_high.csv")
junction_data['Time'] = pd.to_datetime(junction_data['Time'], unit='s')

# === Resample Data ===
# Resample merged data to 5-minute intervals
merged_5min = merged_data.resample('5min').sum()

# Resample junction data to 5-minute intervals
junction_5min = junction_data.resample('5min', on='Time').sum()

# === Similarity Metrics Calculation ===
def compare_time_series(junction_data, merged_data):
    results = {}

    for junction_col in junction_data.columns:  # Loop over each junction's data
        file_comparison = []

        for i in range(1, 6):  # Loop over file_1 to file_5 in merged_data
            file_col = f"file_{i}"

            # Extract values from both time series
            junction_values = junction_data[junction_col].values
            file_values = merged_data[file_col].values

            # Calculate metrics for each file
            comparison_metrics = {
                "File": file_col,
                "Cosine Similarity": round(cosine_similarity([junction_values], [file_values])[0][0], 2),
                "Manhattan Distance": round(cityblock(junction_values, file_values), 2),
                "Euclidean Distance": round(euclidean(junction_values, file_values), 2),
                "Pearson Correlation": round(pearsonr(junction_values, file_values)[0], 2),
                "Spearman Correlation": round(spearmanr(junction_values, file_values)[0], 2),
                "RMSE": round(np.sqrt(np.mean((junction_values - file_values) ** 2)), 2),
                "MAE": round(np.mean(np.abs(junction_values - file_values)), 2),
                "DTW Distance": round(fastdtw(junction_values, file_values)[0], 2)
            }
            file_comparison.append(comparison_metrics)

        # Store the results for the current junction column
        results[junction_col] = pd.DataFrame(file_comparison)

    return results

# Calculate similarity scores for each junction and file pair
similarities = compare_time_series(junction_5min, merged_5min)

# === Plotting ===
# Plot each junction and file pair
merged_cols = [col for col in merged_5min.columns if 'file_' in col]
junction_cols = [col for col in junction_5min.columns if col != 'Time']

# Determine the number of rows needed for plots
num_rows = max(len(merged_cols), len(junction_cols))

fig, axes = plt.subplots(num_rows, 2, figsize=(14, num_rows * 3))
fig.suptitle("KR Circle Merged Data vs Junction Data (per 5 Minutes)", fontsize=16)

# Ensure axes is always 2D
if num_rows == 1:
    axes = [axes]

for i in range(num_rows):
    # Plot merged data (left)
    if i < len(merged_cols):
        axes[i][0].plot(merged_5min[merged_cols[i]], label=merged_cols[i], color="black")
        axes[i][0].set_title(f"KR Circle Merged: {merged_cols[i]}")
    else:
        axes[i][0].axis('off')

    # Plot junction data (right)
    if i < len(junction_cols):
        axes[i][1].plot(junction_5min[junction_cols[i]], label=junction_cols[i], color="blue")
        axes[i][1].set_title(f"Junction: {junction_cols[i]}")
    else:
        axes[i][1].axis('off')

    for j in range(2):
        axes[i][j].set_xlabel("Time")
        axes[i][j].set_ylabel("Vehicle Count")
        axes[i][j].legend()
        axes[i][j].grid(True)
        axes[i][j].set_xticklabels([])  # Remove x-axis tick labels

plt.tight_layout(rect=[0, 0, 1, 0.96])

# === Combining All Similarity Tables into One Image ===
# Create a single figure for all tables
fig_table = plt.figure(figsize=(16, 12))  # Adjusted figure size for better readability

# Start the initial y-position for the first table
y_pos = 1

# Loop through each junction and its similarity metrics table
for junction, df in similarities.items():
    # Create a new subplot for each table
    ax_table = fig_table.add_axes([0.05, y_pos, 0.9, 0.15])  # Adjusted height for better table spacing
    ax_table.axis('off')

    # Title for the table
    ax_table.set_title(f"Similarity Metrics for {junction}", fontsize=16)

    # Create a table from the DataFrame and plot it with larger font size for both the values and the header
    table(ax_table, df, loc='center', colWidths=[0.1] * len(df.columns), fontsize=14, rowColours=["lightblue"]*len(df))

    # Update the y-position for the next table
    y_pos -= 0.175  # Adjust spacing between tables (make sure it fits in the image)

# Save the combined table image with improved readability
table_image_path = "all_similarity_tables_large.png"
fig_table.savefig(table_image_path, bbox_inches='tight')
print(f"Combined table image saved at {table_image_path}")

# Optionally, save the final graph as an image
fig.savefig("merged_vs_junction_plots.png")
print("Plot saved as 'merged_vs_junction_plots.png'")
