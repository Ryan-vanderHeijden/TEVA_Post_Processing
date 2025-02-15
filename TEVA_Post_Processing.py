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



def CC_feature_heatmap(unique_features, cc_features):
    '''
    This function goes through the CC features and builds a "correlation" - style matrix
    that shows how many times each feature appears in a CC with each other feature.
        
            unique_features     list of unique features
            cc_features         list of lists (ccs and their features)

        Returns:
            2d matrix
    '''

    matrix = np.zeros((len(unique_features), len(unique_features)))

    # select the first feature
    for i in range(0, len(unique_features)):
        # select the second feature
        for j in range(0, len(unique_features)):
            # pass if same feature is selected
            if unique_features[i] == unique_features[j]:
                pass
            else:
                # loop through cc_features
                for k in range(0, len(cc_features)):
                    # pass for all order 1 CCs
                    if len(cc_features[k]) == 1:
                        pass
                    else:
                        # check if first feature is in the cc
                        if unique_features[i] in cc_features[k]:
                            # check if second feature is in the cc
                            if unique_features[j] in cc_features[k]:
                                matrix[i,j] += 1
    
    # set the upper triangle to be nan. k=0 sets the main diagonal to nan as well
    matrix[np.triu_indices_from(matrix, k=0)] = np.nan
    
    return matrix