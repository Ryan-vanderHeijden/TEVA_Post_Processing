#%% Import Packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ast
# from scipy.stats import gaussian_kde
# from bokeh.models import ColumnDataSource, FixedTicker, PrintfTickFormatter
# from bokeh.plotting import figure, show

plt.rcParams['font.sans-serif'] = 'Times New Roman'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10

#%% Import Data
clust = 2
data = pd.read_csv('/Users/ryanvan/Library/CloudStorage/OneDrive-UniversityofVermont/Documents/_UVM/Research/CIROH/TEVA/BFI Data/BFI_observations.csv')
ccs = pd.read_excel('/Users/ryanvan/Library/CloudStorage/OneDrive-UniversityofVermont/Documents/_UVM/Research/CIROH/TEVA/BFI Data/BFI_test_CC.xlsx', sheet_name=clust)
dnfs = pd.read_excel('/Users/ryanvan/Library/CloudStorage/OneDrive-UniversityofVermont/Documents/_UVM/Research/CIROH/TEVA/BFI Data/BFI_test_dnf.xlsx', sheet_name=clust)

#%% Test
'''
For each dnf, build a dictionary containing the list of it's ccs.
'''
all_dnfs = []
for j in range(0, len(dnfs)):
    cc_list = dnfs.iloc[j].iloc[8:]
    cc_list = cc_list[cc_list != 0].keys().to_list()
    cc_list = list(map(lambda i: i[3:], cc_list))
    all_dnfs.append(cc_list)

'''
For each cc, build a dictionary containing the features as keys
and feature ranges as values.
'''
all_ccs = []
for j in range(0, len(ccs)):
    cc_values = ccs.iloc[j].iloc[8:]
    cc_values.fillna(value = 0, method=None, inplace=True)
    cc_values = dict(cc_values[cc_values != 0])
    all_ccs.append(cc_values)

'''
Now we have a list of all DNFs and their CCs, and a list
of all CCs and their features.
'''

#%% Test Ridgeline Plot
# pick a CC to plot
kde_color = '#da3907'
cc = int(48)  # 48, 70, 108, 110, 127
var = list(all_ccs[cc].keys())

#%% KDE
fig, ax = plt.subplots(figsize=(3, 1.25*len(var)), nrows=len(var), ncols=1, sharex=False, sharey=False, dpi=300, layout='constrained')
fig.suptitle('CC Number {}'.format(cc))
for i in range(0, len(var)):
    kde = data[str(var[i])]
    plot = kde.plot.kde(ax=ax[i], style=['k'], linewidth=0.7)
    x_plot = plot.get_children()[0]._x
    y_plot = plot.get_children()[0]._y
    
    # ax[i].fill_between(x,y,color=cmap(colors[i]), alpha=0.8)
    ax[i].fill_between(x_plot,y_plot,color='gainsboro', alpha=0.7)

    # plot feature range
    ax[i].fill_between(x_plot,y_plot,
                       where = (x_plot > ast.literal_eval(ccs[var[i]][cc])[0]) & (x_plot < ast.literal_eval(ccs[var[i]][cc])[1]),
                       facecolor='cornflowerblue',
                       alpha=0.7)

    ax[i].annotate(all_ccs[cc][var[i]], [0.05, 0.85], xycoords='axes fraction')

    # set axes properties
    ax[i].set_ylim(0, max(y_plot)*1.1)
    ax[i].set_xlim(0, max(x_plot))
    ax[i].set_ylabel('')
    ax[i].set_yticklabels('')
    ax[i].set_yticks([])
    ax[i].set_ylabel(var[i])

# %%
