# Import libraries
import numpy as np
import pandas as pd
import matplotlib.tri as tri

# Define post-processing functions
def flatten(xss):
    '''
    Flattens a list of lists.
    '''

    return np.array([x for xs in xss for x in xs])


def parse_dnf(dnfs):
    '''
    Creates a list of the ccs composing each dnf.
    '''

    all_ccs = []
    for i in range(0, len(dnfs['mask'])):
        item = dnfs.iloc[i].iloc[12:]
        item_ccs = item[item==1].index.values.tolist()
        item_ccs = list(map(lambda j: j[3:], item_ccs))
        all_ccs.append(item_ccs)
    return all_ccs


def parse_cc(ccs):
    '''
    Creates a list of the features composing each cc.
    '''

    cc_features = []
    for i in range(0, len(ccs)):
        cc_values = ccs.iloc[i].iloc[12:]
        cc_values.fillna(value = 0, method=None, inplace=True)
        cc_values = dict(cc_values[cc_values != 0])
        cc_features.append(list(cc_values.keys()))
    return cc_features


def fitness_contours(n_grid, dnfs, ccs):
    '''
    Interpolate fitness values within plot domain using linear triangular interpolator.
    
        n_grid      number of grid points
        dnfs        TEVA dnf output excel file
        ccs         TEVA cc output excel file

    Returns:
        x           x coordinates of mesh
        y           y coordinates of mesh
        z           interpolated fitness masked array

    Can be passed into the Bokeh contour renderer. Example:
                # fitness contours
                # x, y, z = fitness_contours(1000, dnfs, ccs)
    '''

    x = np.linspace(0, 1, n_grid)
    y = np.linspace(0, 1, n_grid)
    xplot, yplot = np.meshgrid(x, y)
    triangles = tri.Triangulation(pd.concat([dnfs['cov'],ccs['cov']]),
                                  pd.concat([dnfs['ppv'], ccs['ppv']]))
    fitness = pd.concat([dnfs['fitness'], ccs['fitness']])
    interpolator = tri.LinearTriInterpolator(triangles, fitness)
    z = interpolator(xplot, yplot)

    return (x, y, z, fitness)