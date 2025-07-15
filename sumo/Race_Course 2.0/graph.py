import pandas as pd
import matplotlib.pyplot as plt

# === Step A: Load and plot averaged junction data ===

file = 'junction_data_race_course.csv'
data = pd.read_csv(file)

# Drop the 'Time' column
junction_data = data.drop(columns=['Time'])

# Resample per 1 minutes (assuming 60 Hz data; 60*60 = 3600 rows per 1 minutes)
samples_per_5min = 300
minute_data = junction_data.groupby(junction_data.index // samples_per_5min).mean()

# Create subplots
num_junctions = minute_data.shape[1]
fig, axs = plt.subplots(num_junctions, 1, figsize=(15, 3 * num_junctions), sharex=True)

for i, col in enumerate(minute_data.columns):
    axs[i].plot(minute_data.index, minute_data[col], color='darkorange', linewidth=0.8)
    axs[i].set_title(col)
    axs[i].set_ylabel("Avg Count")
    axs[i].grid(True)

axs[-1].set_xlabel("Time (1-minute bins)")
fig.suptitle("Per-Minute Average Traffic Count per Junction", fontsize=18)
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('avg_counts_per_junction.png')
plt.close()
print("A done")

# === Step B: Detect jams and store occurrences ===

df = pd.read_csv(file)

thresholds = {
    "FP_A": 40, "FP_B": 3, "FP_C": 5, "FP_D": 15, "KR_Circle": 20,
    "KG_Road": 15, "District_Office": 10, "Anand_Rao_Jnc": 6,
    "Race_Course_Jnc": 10, "Palace_Road_Jnc": 20
}
junctions = {j: (f"{j}_QueuePct", f"{j}_Speed") for j in thresholds}

jam_times = []
jam_places = []

for idx, row in df.iterrows():
    for junction, (queue_col, speed_col) in junctions.items():
        if row[speed_col] < 0.1 and row[queue_col] > thresholds[junction]:
            jam_times.append(row['Time'])
            jam_places.append(junction)
print("B done")

# === Step C: Plot jam time histogram (multi-day support) ===

max_time = int(df['Time'].max())
y = [1] * len(jam_times)

plt.hist(jam_times, bins=range(0, max_time + 1, 7200))
plt.scatter(jam_times, [i * 50 for i in y], color='r', s=2)
plt.xlabel("Time of Day (Hours)")
plt.ylabel("Number of Jams")
plt.ylim(0, 90)

xticks = range(0, max_time + 1, 7200)
plt.xticks(xticks, [f"{i // 3600}" for i in xticks])
plt.title("Distribution of Jam Occurrences Throughout the Day")
plt.savefig("jam_distribution.png")
plt.close()
print("C done")

# === Step D: Save jam status per junction ===

def check_jam(row, junction, threshold):
    return int(row[f"{junction}_QueuePct"] > threshold and row[f"{junction}_Speed"] < 0.1)

jam_data = pd.DataFrame()
jam_data['Time'] = df['Time']

for junction in thresholds:
    jam_data[f"{junction}_Count"] = df[f"{junction}_Count"]
    jam_data[f"{junction}_Jam"] = df.apply(lambda row: check_jam(row, junction, thresholds[junction]), axis=1)

jam_data.to_csv('race_course_jam_stats.csv', index=False)
print("D done")

# === Step E: Plot counts and jam status per 5 minutes ===

df = pd.read_csv('race_course_jam_stats.csv')
df['FiveMinute'] = df['Time'] // 300
df_resampled = df.groupby('FiveMinute').sum()

junctions = list(thresholds.keys())
fig, axes = plt.subplots(len(junctions), 2, figsize=(15, len(junctions)*3))

for i, junction in enumerate(junctions):
    axes[i, 0].plot(df_resampled.index, df_resampled[f"{junction}_Count"], color='blue')
    axes[i, 0].set_title(f'{junction} Count')
    axes[i, 0].set_xlabel('Time (5-min bins)')
    axes[i, 0].set_ylabel('Count')

    axes[i, 1].plot(df_resampled.index, df_resampled[f"{junction}_Jam"], color='red')
    axes[i, 1].set_title(f'{junction} Jam Status')
    axes[i, 1].set_xlabel('Time (5-min bins)')
    axes[i, 1].set_ylabel('Jam')
    axes[i, 1].set_ylim(-0.1, 1.1)

plt.tight_layout()
plt.savefig("counts_and_jams_per_five_minutes.png")
plt.close()
print("E done")

# === Step F: Add and Plot Score Per Junction (per 5 minutes, with threshold line) ===

df_original = pd.read_csv(file)
df_original['FiveMinute'] = df_original['Time'] // 300

for junction in thresholds:
    queue_col = f"{junction}_QueuePct"
    speed_col = f"{junction}_Speed"
    score_col = f"{junction}_Score"
    df_original[score_col] = (df_original[queue_col] * df_original[speed_col]).abs()

score_per_five_min = df_original.groupby('FiveMinute').mean()

fig, axs = plt.subplots(len(junctions), 1, figsize=(15, len(junctions) * 2.5), sharex=True)

for i, junction in enumerate(junctions):
    score_col = f"{junction}_Score"
    axs[i].plot(score_per_five_min.index, score_per_five_min[score_col], color='purple')
    axs[i].axhline(y=thresholds[junction] * 0.1, color='gray', linestyle='--', linewidth=1.0)
    axs[i].set_title(f"{junction} Score (|QueuePct × Speed|)")
    axs[i].set_ylabel("Score")
    axs[i].grid(True)

axs[-1].set_xlabel("Time (5-min bins)")
fig.suptitle("Junction Scores Over Time (with Threshold Lines)", fontsize=16)
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("junction_scores_per_five_minutes.png")
plt.close()
print("F done")
