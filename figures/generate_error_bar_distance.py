# [29.856      62.96       55.93239235]
# [3.3        3.7        1.48612532]
# [ 81.4        255.2        238.73586943]
# x = np.array()

import matplotlib.pyplot as plt
import numpy as np

MEANS_IDX = 0
MINS_IDX = 1
MAXES_IDX = 2
STD_IDX = 3

# levenshtein
# ch, cr, me, mp
lev_chord = np.array([[29.856, 26.357, 71.939, 105.469],
                      [3.3, 1.7, 17.2, 50.],
                      [81.4, 64., 350.9, 191.8],
                      [12.7801277, 11.40262474, 51.63729833, 27.97021164]])

# levenshtein melody
# me, mp
# lev_melody = np.array([[57.939, 27.995],
#              [16.9, 1.4],
#              [207.9, 113.8],
#              [29.04833522, 15.117919]])

# common_words
# ch, cr, me, mp
cw_chord = np.array([[62.96, 47.91, 116.099, 202.712],
                      [3.7, 1., 23.1, 68.9],
                      [255.2, 141., 377.7, 438.2],
                      [37.7507139, 26.43120315, 60.59834073, 59.97658923]])

# common_words melody
# me, mp
# cw_melody = np.array([[100.643, 45.912],
#              [21.8, 0.6],
#              [300.3, 207.6],
#              [45.0805396, 30.82822499]])

# create stacked errorbars:
plt.figure()

# fig, (ax1, ax2) = plt.subplots(1, 2)
# fig.suptitle('Horizontally stacked subplots')

fig = plt.figure()

ax1 = fig.add_subplot(121)
ax1.set_title('Levenshtein Distance')
ax1.set_xticks([0, 1, 2, 3])
ax1.set_xticklabels(['ch', 'cr', 'me', 'mp'])
ax1.set_xlim(-1, lev_chord.shape[1])
ax1.errorbar(np.arange(lev_chord.shape[1]), lev_chord[MEANS_IDX], lev_chord[STD_IDX], fmt='ok', lw=3)
ax1.errorbar(np.arange(lev_chord.shape[1]), lev_chord[MEANS_IDX], [lev_chord[MEANS_IDX] - lev_chord[MINS_IDX], lev_chord[MAXES_IDX] - lev_chord[MEANS_IDX]],
             fmt='.k', ecolor='gray', lw=1)

# ax2 = fig.add_subplot(222)
# ax2.set_title('Distance', loc='left', position=(-.15, 1.))  # small trick to make a row title
# ax2.set_xticks([0, 1])
# ax2.set_xticklabels(['me', 'mp'])
# ax2.set_xlim(-1, lev_melody.shape[1])
# ax2.errorbar(np.arange(lev_melody.shape[1]), lev_melody[MEANS_IDX], lev_melody[STD_IDX], fmt='ok', lw=3)
# ax2.errorbar(np.arange(lev_melody.shape[1]), lev_melody[MEANS_IDX], [lev_melody[MEANS_IDX] - lev_chord[MINS_IDX], lev_chord[MAXES_IDX] - lev_chord[MEANS_IDX]],
#              fmt='.k', ecolor='gray', lw=1)

ax3 = fig.add_subplot(122)
ax3.set_title('Common Words Distance')
ax3.set_xticks([0, 1, 2, 3])
ax3.set_xticklabels(['ch', 'cr', 'me', 'mp'])
ax3.set_xlim(-1, cw_chord.shape[1])
ax3.errorbar(np.arange(cw_chord.shape[1]), cw_chord[MEANS_IDX], cw_chord[STD_IDX], fmt='ok', lw=3)
ax3.errorbar(np.arange(cw_chord.shape[1]), cw_chord[MEANS_IDX], [cw_chord[MEANS_IDX] - lev_chord[MINS_IDX], lev_chord[MAXES_IDX] - lev_chord[MEANS_IDX]],
             fmt='.k', ecolor='gray', lw=1)

# ax4 = fig.add_subplot(224)
# ax4.set_title('Distance', loc='left', position=(-.15, 1.))  # small trick to make a row title
# ax4.set_xticks([0, 1])
# ax4.set_xticklabels(['me', 'mp'])
# ax4.set_xlim(-1, cw_melody.shape[1])
# ax4.errorbar(np.arange(cw_melody.shape[1]), cw_melody[MEANS_IDX], cw_melody[STD_IDX], fmt='ok', lw=3)
# ax4.errorbar(np.arange(cw_melody.shape[1]), cw_melody[MEANS_IDX], [cw_melody[MEANS_IDX] - lev_chord[MINS_IDX], lev_chord[MAXES_IDX] - lev_chord[MEANS_IDX]],
#              fmt='.k', ecolor='gray', lw=1)

# Will leave some space to the main title
fig.tight_layout(rect=[0, 0.03, 1, 0.95])
fig.suptitle('Average distances within cliques', fontsize=16)


plt.savefig("error_bar_distance.png")
