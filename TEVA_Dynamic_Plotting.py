
# Import libraries
import numpy as np
import pandas as pd
import holoviews as hv
import panel as pn
from bokeh.plotting import figure
from bokeh.models import LinearColorMapper
from bokeh.palettes import Viridis256
from bokeh.models import HoverTool, CDSView, GroupFilter, NumeralTickFormatter, LinearColorMapper, ColorBar, IndexFilter, Label, LabelSet, ColumnDataSource
from bokeh.transform import linear_cmap
import TEVA_Post_Processing as post




# Dynamic / Interactive Plots
def feature_plotter(selected_cc, data, cc_features, feature_values_by_cc):
    '''
    Generates flexible region that contains KDE plots of the features associated with a selected CC.
    Also plots the feature ranges associaated with the selected CC.

    KDE plot for continuous data.
    Bar plot for categorical data (work in progress)
    '''

    fig = []
    for i in range(len(cc_features[selected_cc])):
        # check if continuous or categorical
        '''
        This is not very robust: it just checks if the column dtpye is float or not, and
        assumes that float is continuous and anything else is categorical.
        '''
        if data[cc_features[selected_cc][i]].dtype == 'float64':
            # KDE plot
            kde_plot = data[cc_features[selected_cc][i]].dropna().hvplot.kde(height=200, width=300, hover=False).opts(color='lightgray')

            # VSpan glyph to show feature range        
            feat_range_plot = hv.VSpan(feature_values_by_cc[selected_cc][i][0], feature_values_by_cc[selected_cc][i][1]).opts(color='red', alpha=0.3)
            
            # Combine plots and add to fig list, set options
            fig.append(kde_plot * feat_range_plot)
            fig[i].opts(shared_axes=False, toolbar=None)
        
        else:
            # bar plot
            # prepare data for bar
            a = data[cc_features[selected_cc][i]].value_counts()
            a.sort_index(inplace=True)
            a = pd.DataFrame(a)

            # bar color by feature range
            b = feature_values_by_cc[selected_cc][i]
            c = a.index.tolist()
            bar_colors = []
            for j in range(len(a)):
                if c[j] in b:
                    bar_colors.append('lightcoral')
                else:
                    bar_colors.append('lightgray')
            a['bar_color'] = bar_colors

            bar_plot = a.hvplot.bar(x=cc_features[selected_cc][i], y='count', height=200, width=300, hover=False, color='bar_color').opts(alpha=0.7)

            # Combine plots and add to fig list, set options
            fig.append(bar_plot)# * feat_range_plot)
            fig[i].opts(shared_axes=False, toolbar=None)

    return pn.FlexBox(objects=fig)





def confusion_matrix_plotter(selected_cc, ccs):
    '''
    Plots a confusion matrix based on the selected CC.
    '''

    conf = post.confusion_matrix(ccs, selected_cc)
    conf_percent = np.round((conf / sum(ccs.iloc[0]['tp' : 'fn'])) * 100, 1)
    conf_data = {
        'image': [conf_percent],
        'x': [0],
        'y': [0],
        'dw': [2],
        'dh': [2]
    }

    conf_color_mapper = LinearColorMapper(palette=Viridis256, low=0, high=100)

    conf_mat_fig = figure(title='Confusion Matrix',
                        width=400,
                        height=300,
                        x_axis_label='Observation',
                        y_axis_label='Prediction',
                        x_range=['Positive', 'Negative'],
                        y_range=['Positive', 'Negative'])

    conf_mat_fig.image(source=conf_data, x='x', y='y', dw='dw', dh='dh', color_mapper=conf_color_mapper)
    conf_mat_fig.add_tools(HoverTool(tooltips=[('Value', '@image')]))
    color_bar = ColorBar(color_mapper=conf_color_mapper, label_standoff=12, major_tick_line_color='black', title='Percent')
    conf_mat_fig.add_layout(color_bar, 'right')

    label_source = ColumnDataSource(data=dict(
    x=[0.5, 1.5, 0.5, 1.5],
    y=[0.5, 0.5, 1.5, 1.5],
    names=conf.flatten().astype(str)
    ))
    labels = LabelSet(x='x', y='y', text='names', x_offset=0, y_offset=0, text_font_size='12pt', text_color='black', background_fill_color='white', source=label_source)
    conf_mat_fig.add_layout(labels)

    return conf_mat_fig





def cc_plotter(min_sens, max_sens, fitness, x_fit, y_fit, z_fit, contour_colors, cc_plot_data, cc_len, cc_plot_source, cc_colors, ccs, dnf_len, dnf_plot_data, dnf_plot_source, dnf_colors, dnfs):
    '''
    Plots the main figure (PPV vs. COV) that dynamically updates based on the selected sensitivity range.
    '''
    
    h = 600
    w = 800

    dnf_TOOLS = [
        ('DNF #', '@DNF'),
        ('Order', '@Order'),
        ('PPV', '@y_values'),
        ('COV', '@x_values'),
        ('CCs', '@CCs')]

    cc_TOOLS = [
        ('CC #', '@CC'),
        ('Order', '@Order'),
        ('PPV', '@y_values'),
        ('COV', '@x_values'),
        ('Min Sens.', '@min_sens'),
        ('Max Sens.', '@max_sens'),
        ('Features', '@Features')]
    
    # Figure
    p = figure(width = w, height = h,
            y_range=(0,1.05),
            x_range=(0,1.05),
            x_axis_label='Observation Coverage',
            y_axis_label='Positive Predictive Value',
            hidpi=True,
            tools='crosshair, pan, tap, wheel_zoom, zoom_in, zoom_out, box_zoom, undo, redo, reset, save, lasso_select, help')

    # Fitness Contours
    cont_levels = np.linspace(min(fitness), max(fitness), 10)
    contour_renderer = p.contour(x_fit, y_fit, z_fit,
                                levels=cont_levels,
                                line_color='gray',
                                fill_color=contour_colors,
                                line_dash='dashed')
    
    #### CCs
    # filter by sensitivity
    filter_idx = cc_plot_data[(cc_plot_data['min_sens'] >= min_sens) & (cc_plot_data['max_sens'] <= max_sens)].index.to_list()
    sens_filtered_CCs = IndexFilter(filter_idx)

    # CCs by order
    all_cc_plots = []
    for i in range(0, len(cc_len)):
        # Filter by order
        order_filtered_CCs = GroupFilter(column_name='Order', group=len(cc_len) - i)
        # Plot
        cc_plot = p.scatter('x_values', 'y_values', source=cc_plot_source,
                            view=CDSView(filter=sens_filtered_CCs & order_filtered_CCs),
                            size=12,
                            marker='square',
                            line_color='white',
                            fill_color=linear_cmap('Order', cc_colors, low=min(ccs['order']), high=max(ccs['order'])),
                            hover_color='black',
                            legend_label='CC Order {}'.format(len(cc_len) - i),
                            fill_alpha=1)
        all_cc_plots.append(cc_plot)
        
    
    #### DNFs        
    # filter by sensitivity
    filter_dnf_idx = []
    for i in range(len(dnf_plot_data['CCs'])):
        if set(list(map(int, dnf_plot_data['CCs'][i]))).issubset(filter_idx) == True:
            filter_dnf_idx.append(i)
        else:
            pass
    sens_filtered_DNFs = IndexFilter(filter_dnf_idx)
    
    # DNFs by order
    all_dnf_plots = []
    for i in range(0, len(dnf_len)):
        # filter by order
        order_filtered_DNFs = GroupFilter(column_name='Order', group=len(dnf_len) - i)
        # plot
        dnf_plot = p.scatter('x_values', 'y_values', source=dnf_plot_source,
                             view=CDSView(filter=sens_filtered_DNFs & order_filtered_DNFs),
                             size=13,
                             marker='circle',
                             line_color='white',
                             fill_color=linear_cmap('Order', dnf_colors, low=min(dnfs['order']), high=max(dnfs['order'])),
                             hover_color='black',
                             legend_label='DNF Order {}'.format(len(dnf_len) - i),
                             fill_alpha=1)
        all_dnf_plots.append(dnf_plot)

    # Add hover tool for CCs
    p.add_tools(HoverTool(renderers = all_cc_plots,
                          tooltips=cc_TOOLS,
                          mode='mouse',
                          point_policy='follow_mouse'))

    # Add seperate hover tool for DNFs
    p.add_tools(HoverTool(renderers = all_dnf_plots,
                          tooltips=dnf_TOOLS,
                          mode='mouse',
                          point_policy='follow_mouse'))

    # Add color bar for fitness contours
    colorbar = contour_renderer.construct_color_bar(height=int(h/2),
                                                    location=(0,int(h/4)),
                                                    formatter = NumeralTickFormatter(format='0 a'),
                                                    bar_line_color='black',
                                                    major_tick_line_color='black',
                                                    title='Fitness, 10^')

    # General formatting
    p.legend.click_policy='hide'
    p.legend.location='bottom_left'
    p.add_layout(colorbar, 'right')
    nonselection_fill_alpha=0.2
    
    return p





def cc_heatmap_plotter(cc_heatmap_colormap, unique_features, cc_features, cc_plot_data, min_sens, max_sens):
    
    cc_image_hover = [
        ('Count', '@image')
    ]

    filter_idx = cc_plot_data[(cc_plot_data['min_sens'] >= min_sens.value) & (cc_plot_data['max_sens'] <= max_sens.value)].index.to_list()
    sens_filtered_ccs = [cc_features[i] for i in filter_idx]
    unique_features_filtered = pd.unique(post.flatten(sens_filtered_ccs))

    cc_heatmap = figure(height=len(unique_features)*20,
                        width=len(unique_features)*20,
                        aspect_ratio=1,
                        x_range=unique_features,
                        y_range=unique_features,
                        match_aspect=True,
                        tools=['hover', 'crosshair', 'save'],
                        tooltips=cc_image_hover)

    cc_matrix = post.CC_feature_heatmap(unique_features_filtered, sens_filtered_ccs)

    # CC feature image
    cc_image_data = {
        'image': [cc_matrix],
        'x': [0],
        'y': [0],
        'dw': [len(unique_features_filtered)],
        'dh': [len(unique_features_filtered)]
    }

    cc_image_data = ColumnDataSource(data=cc_image_data)

    # Figure setup
    cc_heatmap = figure(height=len(unique_features_filtered)*25,
                        aspect_ratio=1,
                        x_range=unique_features_filtered,
                        y_range=unique_features_filtered,    
                        match_aspect=True,
                        tools=['hover', 'crosshair', 'save'],
                        tooltips=cc_image_hover)

    # Color map for data
    img_color_mapper = LinearColorMapper(palette=cc_heatmap_colormap, low=0, high=len(unique_features_filtered))
    # Imshow
    img = cc_heatmap.image(source=cc_image_data, x='x', y='y', dw='dw', dh='dh', color_mapper=img_color_mapper)
    # Create colorbar
    color_bar = ColorBar(color_mapper=img_color_mapper, label_standoff=12, major_tick_line_color='black')
    # Add colorbar to figure
    cc_heatmap.add_layout(color_bar, 'right')

    # color for nan values
    img.glyph.color_mapper.nan_color = (0, 0, 0, 0)

    # rotate x labels
    cc_heatmap.xaxis.major_label_orientation = np.pi/2

    # turn off grid
    cc_heatmap.xgrid.visible = False
    cc_heatmap.ygrid.visible = False

    return cc_heatmap





def cc_feature_usage_plot(unique_features, stacked_features, stacked_feature_names, cat_map, cc_len, min_sens, max_sens):

    p2 = figure(width=max(len(unique_features)*20, 800), height=500,
            x_range=stacked_features['Feature'],
            x_axis_label='Feature',
            y_axis_label='Count',
            hidpi=True,
            tools='crosshair, reset, save, help')

    p2.vbar_stack(stacked_feature_names,
                x='Feature',
                width=0.6,
                color=cat_map[0:len(cc_len)],
                source=stacked_features,
                legend_label=stacked_feature_names)

    # General formatting
    p2.xaxis.major_label_orientation = 1
    p2.y_range.start = 0
    p2.legend.location = 'top_right'
    p2.legend.orientation = 'vertical'

    return p2





def dnf_usage_plot(unique_ccs, stacked_ccs, stacked_cc_names, cat_map, dnf_len, min_sens, max_sens):

    p3 = figure(width=len(unique_ccs)*13, height=500,
                x_range=stacked_ccs['CC'],
                x_axis_label='CC',
                y_axis_label='Count',
                hidpi=True,
                tools='crosshair, reset, save, help')

    p3.vbar_stack(stacked_cc_names,
                x='CC',
                width=0.6,
                color=cat_map[0:len(dnf_len)],
                source=stacked_ccs,
                legend_label=stacked_cc_names)

    # General formatting
    p3.xaxis.major_label_orientation = 1
    p3.y_range.start = 0
    p3.legend.location = 'top_right'
    p3.legend.orientation = 'vertical'

    return p3