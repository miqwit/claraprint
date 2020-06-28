import matplotlib

import matplotlib.pyplot as plt
import numpy as np

# Got from experiment es_multiple_fp_generated
# Config:
# configs_to_run = [
#     Config(algo="chords_chordino", duration=120, letters_to_use=1, range_words=[range(2, 8)], num_sources=[1]),
#     Config(algo="chords_crema", duration=120, letters_to_use=1, range_words=[range(2, 8)], num_sources=[1]),
#     Config(algo="melody_melodia", duration=120, letters_to_use=3, range_words=[range(2, 8)], num_sources=[1]),
#     Config(algo="melody_piptrack", duration=120, letters_to_use=3, range_words=[range(2, 8)], num_sources=[1]),
# ]
labels = ['Ingestion time', 'Query time']
chord_chordino_means = [4.94, 4.14]
chord_crema_means = [5.22, 4.72]
melody_melodia_means = [6.52, 11.37]
melody_piptrack_means = [8.08, 19.70]


# x = np.arange(len(labels))  # the label locations
x = np.array([0, .5])
width = 0.10  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - 1.5*width, chord_chordino_means, width, label='ch')
rects2 = ax.bar(x - width/2, chord_crema_means, width, label='cr')
rects3 = ax.bar(x + width/2, melody_melodia_means, width, label='me')
rects4 = ax.bar(x + 1.5*width, melody_piptrack_means, width, label='mp')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Time (ms)')
ax.set_title('Ingestion and Query Times')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

def autolabel(rects):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 1),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')


autolabel(rects1)
autolabel(rects2)
autolabel(rects3)
autolabel(rects4)

fig.tight_layout()

plt.show()
plt.savefig("graph_compare_algos_times.png")
