import matplotlib.pyplot as plt
import numpy as np

# Data
constraint_satisfaction = {
    7: 233,
    5: 220,
    8: 109,
    9: 33,
    6: 315,
    4: 53,
    3: 4,
    10: 19,
    11: 10,
    12: 3,
    13: 1,
}
entropy_based = {
    5: 287,
    6: 323,
    4: 81,
    9: 27,
    7: 177,
    8: 74,
    3: 5,
    10: 18,
    13: 1,
    11: 4,
    12: 3,
}
baseline = {
    11: 172,
    17: 24,
    16: 52,
    13: 130,
    9: 100,
    8: 40,
    20: 3,
    12: 152,
    14: 88,
    10: 115,
    7: 24,
    15: 64,
    6: 9,
    18: 13,
    19: 10,
    21: 1,
    4: 1,
    5: 2,
}

# Combine all possible numbers of tries
all_tries = sorted(
    set(constraint_satisfaction.keys())
    | set(entropy_based.keys())
    | set(baseline.keys())
)

# Prepare data for plotting
constraint_counts = [constraint_satisfaction.get(x, 0) for x in all_tries]
entropy_counts = [entropy_based.get(x, 0) for x in all_tries]
baseline_counts = [baseline.get(x, 0) for x in all_tries]

# Set up bar positions
x = np.arange(len(all_tries))  # the label locations
width = 0.25  # the width of the bars

# Create the plot
fig, ax = plt.subplots(figsize=(12, 6))

rects1 = ax.bar(
    x - width,
    constraint_counts,
    width,
    label="Constraint Satisfaction Method",
    color="blue",
)
rects2 = ax.bar(x, entropy_counts, width, label="Entropy-based Method", color="green")
rects3 = ax.bar(x + width, baseline_counts, width, label="Baseline Method", color="red")

# Add labels, title, and custom x-axis tick labels
ax.set_xlabel("Number of Tries")
ax.set_ylabel("Number of Games")
ax.set_title("Performance of Different AI Models on Dordle")
ax.set_xticks(x)
ax.set_xticklabels(all_tries)
ax.legend()

# Optimize layout
fig.tight_layout()

# Display the plot
plt.show()
