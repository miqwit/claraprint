# libraries
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Data
df = pd.DataFrame({
    'x': range(1, 5),
    'ch@MT10': np.array([0.91, 0.94, 0.97, 0.98]),
    'cr@MT10': np.array([0.87, 0.92, 0.94, 0.97]),
    'me@MT10': np.array([0.80, 0.83, 0.87, 0.91]),
    'mp@MT10': np.array([0.63, 0.64, 0.67, 0.73]),
    'ch@MT1': np.array([0.84, 0.87, 0.91, 0.95]),
    'cr@MT1': np.array([0.72, 0.77, 0.81, 0.85]),
    'me@MT1': np.array([0.57, 0.64, 0.69, 0.73]),
    'mp@MT1': np.array([0.43, 0.40, 0.44, 0.53])
})

plt.figure()
fig = plt.figure()

ax1 = fig.add_subplot(211)
# ax1.set_title('title1')
ax1.set_xticks([1, 2, 3, 4])
# ax1.set_xticklabels([1, 2, 3, 4])
# ax1.set_xlim(-1, lev_chord.shape[1])
ax1.plot('x', 'ch@MT10', data=df, marker='s', color='tab:blue')
ax1.plot('x', 'cr@MT10', data=df, marker='p', color='tab:orange')
ax1.plot('x', 'me@MT10', data=df, marker='v', color='tab:red')
ax1.plot('x', 'mp@MT10', data=df, marker='^', color='tab:purple')
ax1.legend()

ax3 = fig.add_subplot(212)
# ax3.set_title('Common Words Distance')
ax3.set_xticks([1, 2, 3, 4])
# ax3.set_xticklabels(['1', '2', '3', '4'])
# ax3.set_xlim(-1, cw_chord.shape[1])
ax3.plot('x', 'ch@MT1', data=df, marker='s', linestyle='--', color='tab:blue')
ax3.plot('x', 'cr@MT1', data=df, marker='p', linestyle='--', color='tab:orange')
ax3.plot('x', 'me@MT1', data=df, marker='v', linestyle='--', color='tab:red')
ax3.plot('x', 'mp@MT1', data=df, marker='^', linestyle='--', color='tab:purple')
ax3.legend()

# fig.tight_layout(rect=[0, 0.03, 1, 0.95])
fig.suptitle('Similarity Matching for Multi Sources Claraprints', fontsize=16)

plt.savefig("multiple_source_line.png")
