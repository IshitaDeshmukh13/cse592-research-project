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
    7: 196,
    6: 325,
    4: 94,
    9: 15,
    8: 74,
    10: 4,
    3: 5,
}
csp_entropy_combo = {
    5: 267,
    6: 286,
    10: 24,
    9: 44,
    8: 104,
    4: 64,
    7: 196,
    11: 7,
    12: 5,
    3: 3,
}
left_right_word_balanced_1 = {
    4: 85,
    6: 320,
    8: 73,
    5: 281,
    10: 16,
    7: 188,
    9: 29,
    11: 5,
    3: 1,
    12: 1,
    13: 1,
}
left_right_word_balanced_2 = {
    7: 199,
    5: 272,
    9: 39,
    8: 107,
    6: 269,
    4: 71,
    11: 7,
    12: 3,
    10: 31,
    13: 1,
    3: 1,
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
    | set(csp_entropy_combo.keys())
    | set(left_right_word_balanced_1.keys())
    | set(left_right_word_balanced_2.keys())
    | set(baseline.keys())
)

# Prepare data for plotting
constraint_counts = [constraint_satisfaction.get(x, 0) for x in all_tries]
entropy_counts = [entropy_based.get(x, 0) for x in all_tries]
csp_entropy_combo_counts = [csp_entropy_combo.get(x, 0) for x in all_tries]
left_right_balanced_1_counts = [
    left_right_word_balanced_1.get(x, 0) for x in all_tries
]
left_right_balanced_2_counts = [
    left_right_word_balanced_2.get(x, 0) for x in all_tries
]
baseline_counts = [baseline.get(x, 0) for x in all_tries]

# Set up bar positions
x = np.arange(len(all_tries))  # the label locations
num_datasets = 6
total_width = 0.8
width = total_width / num_datasets  # the width of the bars

# Positions of bars
positions = [
    x - total_width / 2 + width / 2 + i * width for i in range(num_datasets)
]

# Create the plot
fig, ax = plt.subplots(figsize=(12, 6))

rects1 = ax.bar(
    positions[0],
    constraint_counts,
    width,
    label="Constraint Satisfaction Method (1)",
    color="blue",
)
rects2 = ax.bar(
    positions[1],
    entropy_counts,
    width,
    label="Entropy-based Method (2)",
    color="green",
)
rects3 = ax.bar(
    positions[2],
    csp_entropy_combo_counts,
    width,
    label="CSP Entropy Combo Method (3)",
    color="orange",
)
rects4 = ax.bar(
    positions[3],
    left_right_balanced_1_counts,
    width,
    label="Left-Right Word Balanced 1 (4)",
    color="purple",
)
rects5 = ax.bar(
    positions[4],
    left_right_balanced_2_counts,
    width,
    label="Left-Right Word Balanced 2 (5)",
    color="brown",
)
rects6 = ax.bar(
    positions[5],
    baseline_counts,
    width,
    label="Baseline Method",
    color="red",
)

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
