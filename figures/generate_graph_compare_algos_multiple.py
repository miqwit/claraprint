import matplotlib

import matplotlib.pyplot as plt
import numpy as np

# Got from experiment es_cross_sources
# Config:
# configs_to_run = [
# Config(algos=["chords_chordino", "melody_melodia"], range_words=[range(2, 8)], search_func=es_search_shingle),
# Config(algos=["chords_chordino", "melody_piptrack"], range_words=[range(2, 8)], search_func=es_search_shingle),
# Config(algos=["chords_crema", "melody_melodia"], range_words=[range(2, 8)], search_func=es_search_shingle),
# Config(algos=["chords_crema", "melody_piptrack"], range_words=[range(2, 8)], search_func=es_search_shingle),
# Config(algos=["chords_chordino", "chords_crema"], range_words=[range(2, 8)], search_func=es_search_shingle),
# Config(algos=["melody_melodia", "melody_piptrack"], range_words=[range(2, 8)], search_func=es_search_shingle),
# ]
labels = ['MT10', 'MT1']
ch_me_means = [0.91, 0.78]
ch_mp_means = [0.88, 0.76]
cr_me_means = [0.86, 0.72]
cr_mp_means = [0.84, 0.68]
ch_cr_means = [0.91, 0.82]
me_mp_means = [0.83, 0.62]

# x = np.arange(len(labels))  # the label locations
x = np.array([0, .5])
width = 0.05  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - 2.5*width, ch_cr_means, width, label='ch-cr')
rects2 = ax.bar(x - 1.5*width, ch_me_means, width, label='ch-me')
rects3 = ax.bar(x - width/2, ch_mp_means, width, label='ch-mp')
rects4 = ax.bar(x + width/2, cr_me_means, width, label='cr-me')
rects5 = ax.bar(x + 1.5*width, cr_mp_means, width, label='cr-mp')
rects6 = ax.bar(x + 2.5*width, me_mp_means, width, label='me-mp')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Score')
ax.set_title('MT10 and MT1 for MIR algorithm combination')
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
autolabel(rects5)
autolabel(rects6)

fig.tight_layout()

plt.show()
plt.savefig("graph_compare_algos_multiple.png")
