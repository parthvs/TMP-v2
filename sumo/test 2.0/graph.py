import csv
import matplotlib.pyplot as plt

# Read the CSV file manually
with open('data1.csv', 'r') as file:
    reader = csv.reader(file, delimiter=',')  # Adjust delimiter if needed
    headers = next(reader)  # Get column names
    data = list(reader)  # Read the rest of the data

# Convert data to floats (except first column, which is time)
time = [float(row[0]) for row in data]
features = {headers[i]: [float(row[i]) if row[i] else 0 for row in data] for i in range(1, len(headers))}

# Create subplots
fig, axes = plt.subplots(len(features), 1, figsize=(16, len(features) * 2.5), sharex=True)

# Ensure axes is always iterable
if len(features) == 1:
    axes = [axes]

# Plot each feature
for ax, (feature, values) in zip(axes, features.items()):
    ax.plot(time, values)
    ax.set_title(feature)
    ax.set_ylabel(feature)
    ax.grid(True)

# Set x-axis label on the last subplot
axes[-1].set_xlabel(headers[0])

plt.tight_layout()
plt.savefig("all_features_graph.png")
plt.show()
