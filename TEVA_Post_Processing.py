# Import libraries
import numpy as np
import pandas as pd
import ast
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
        # don't include the first 14 columns
        item = dnfs.iloc[i].iloc[14:]
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
        # don't include the first 14 columns
        cc_values = ccs.iloc[i].iloc[14:]
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



def stacked_features(ccs, unique_features, cc_features, all_features_flat):
    cc_len = np.arange(1, max(ccs['order']) + 1 , 1)
    cc_col_names = ['Feature']

    feature_counts = []
    for i in range(len(unique_features)):
        feature_counts.append(np.count_nonzero(all_features_flat==unique_features[i]))

    for j in range(len(cc_len)):
        cc_col_names.append('Order ' + str(j+1))

    cc_col_names.append('Total')
    feature_order = pd.DataFrame(columns=cc_col_names)
    feature_order['Feature'] = unique_features
    feature_order['Total'] = feature_counts

    # List subset by length
    for k in range(len(cc_len)):
        # subset cc_features by order
        subset = [sublist for sublist in cc_features if len(sublist) == cc_len[k]]
        subset = np.array(flatten(subset))

        for i in range(len(unique_features)):
            feature_order.loc[i, 'Order ' + str(k+1)] = np.count_nonzero(subset==unique_features[i])

    feature_order.sort_values(by=['Total'], ascending=False, inplace=True)
    # feature_order.drop(columns=['Total'], inplace=True)
    stack_plot_feature = dict(feature_order)
    stack_names_feature = cc_col_names[1:-1]

    return stack_plot_feature, stack_names_feature



def stacked_ccs(dnfs, unique_ccs, all_ccs, all_ccs_flat):
    dnf_len = np.arange(1, max(dnfs['order']) + 1 , 1)
    dnf_col_names = ['CC']

    cc_counts = []
    for i in range(len(unique_ccs)):
        cc_counts.append(np.count_nonzero(all_ccs_flat==unique_ccs[i]))

    for j in range(len(dnf_len)):
        dnf_col_names.append('Order ' + str(j+1))

    dnf_col_names.append('Total')
    cc_order = pd.DataFrame(columns=dnf_col_names)
    cc_order['CC'] = unique_ccs
    cc_order['Total'] = cc_counts

    # List subset by length
    for k in range(len(dnf_len)):
        # subset by order
        subset = [sublist for sublist in all_ccs if len(sublist) == dnf_len[k]]
        subset = np.array(flatten(subset))

        for i in range(len(unique_ccs)):
            cc_order.loc[i, 'Order ' + str(k+1)] = np.count_nonzero(subset==unique_ccs[i])

    cc_order.sort_values(by=['Total'], ascending=False, inplace=True)
    # cc_order.drop(columns=['Total'], inplace=True)
    stack_plot_cc = dict(cc_order)
    stack_names_cc = dnf_col_names[1:-1]
    
    return stack_plot_cc, stack_names_cc


def feature_ranges_by_cc(ccs):
    '''
    Parse the feature value ranges and write them to a list of lists.
    '''

    a = ccs.drop(columns=['Unnamed: 0', 'class', 'mask', 'fitness', 'order', 'age', 'cov', 'ppv',
       'min_feat_sensitivity', 'max_feat_sensitivity', 'tp', 'tn', 'fp', 'fn'])
    
    main_list = []
    for i in range(0, len(a)):
        b = a.iloc[i].dropna().to_list()

        value_list = []
        for j in range(0, len(b)):
                value_list.append(ast.literal_eval(b[j]))
        
        main_list.append(value_list)
    
    return main_list



def feature_ranges_by_feature(ccs):
    '''
    Parse feature ranges by feature.
    '''

    a = ccs.drop(columns=['Unnamed: 0', 'class', 'mask', 'fitness', 'order', 'age', 'cov', 'ppv',
        'min_feat_sensitivity', 'max_feat_sensitivity', 'tp', 'tn', 'fp', 'fn'])
    a.dropna(axis=1, how='all', inplace=True)

    cols = a.columns.to_list()

    main_list = []
    for i in range(0, len(cols)):
        b = a[cols[i]].dropna().to_list()
        value_list = []
        for j in range(0, len(b)):
            value_list.append(ast.literal_eval(b[j]))
        
        main_list.append(value_list)

    return main_list



def confusion_matrix(ccs, cc_num):
    '''
    Given ccs output file and a selected cc, plot a confusion matrix.
    Normalized by total count.
    '''

    return np.array([[ccs.iloc[cc_num]['tp'], ccs.iloc[cc_num]['fn']], [ccs.iloc[cc_num]['fp'], ccs.iloc[cc_num]['tn']]]) #/ sum(ccs.iloc[0]['tp' : 'fn'])