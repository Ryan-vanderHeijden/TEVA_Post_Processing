
# Import libraries
import numpy as np
import pandas as pd
import holoviews as hv
import panel as pn
from bokeh.plotting import figure
from bokeh.models import LinearColorMapper
from bokeh.palettes import Viridis256
from bokeh.models import HoverTool, CDSView, GroupFilter, NumeralTickFormatter, LinearColorMapper, ColorBar, IndexFilter
from bokeh.transform import linear_cmap
import TEVA_Post_Processing as post


# Dynamic / Interactive Plots
def feature_plotter(selected_cc, data, cc_features, feature_values_by_cc):
    '''
    Generates flexible region that contains KDE plots of the features associated with a selected CC.
    Also plots the feature ranges associaated with the selected CC.
    '''

    fig = []
    for i in range(len(cc_features[selected_cc])):
        # KDE plot
        kde_plot = data[cc_features[selected_cc][i]].dropna().hvplot.kde(height=200, width=300, hover=False).opts(color='lightgray')

        # VSpan glyph to show feature range        
        feat_range_plot = hv.VSpan(feature_values_by_cc[selected_cc][i][0], feature_values_by_cc[selected_cc][i][1]).opts(color='red', alpha=0.3)
        
        # Combine plots and add to fig list, set options
        fig.append(kde_plot * feat_range_plot)
        fig[i].opts(shared_axes=False, toolbar=None)

    return pn.FlexBox(objects=fig)



def confusion_matrix_plotter(selected_cc, ccs):
    '''
    Plots a confusion matrix based on the selected CC.
    '''

    conf = post.confusion_matrix(ccs, selected_cc)
    conf_data = {
        'image': [conf],
        'x': [0],
        'y': [0],
        'dw': [2],
        'dh': [2]
    }

    conf_color_mapper = LinearColorMapper(palette=Viridis256, low=0, high=1)

    conf_mat_fig = figure(title='Confusion Matrix',
                        width=400,
                        height=300,
                        x_axis_label='Observation',
                        y_axis_label='Prediction',
                        x_range=['Positive', 'Negative'],
                        y_range=['Positive', 'Negative'])

    conf_mat_fig.image(source=conf_data, x='x', y='y', dw='dw', dh='dh', color_mapper=conf_color_mapper)
    conf_mat_fig.add_tools(HoverTool(tooltips=[('Value', '@image')]))
    color_bar = ColorBar(color_mapper=conf_color_mapper, label_standoff=12, major_tick_line_color='black')
    conf_mat_fig.add_layout(color_bar, 'right')

    return conf_mat_fig



def cc_plotter(min_sens, max_sens, fitness, x_fit, y_fit, z_fit, contour_colors, cc_plot_data, cc_len, cc_plot_source, cc_colors, ccs, dnf_len, dnf_plot_source, dnf_colors, dnfs):
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
    
    # CCs filtered by sensitivity and order
    filter_idx = cc_plot_data[(cc_plot_data['min_sens'] >= min_sens) & (cc_plot_data['max_sens'] <= max_sens)].index.to_list()
    sens_filtered_CDS = IndexFilter(filter_idx)
    
    # Plot CCs, colored by order
    if len(np.floor(ccs['min_feat_sensitivity'][np.isinf(ccs['min_feat_sensitivity'])==False])) == 0:

        for i in range(0, len(cc_len)):
            order_filtered_CDS = GroupFilter(column_name='Order', group=len(cc_len) - i)

            p.scatter('x_values', 'y_values', source=cc_plot_source,
                    view=CDSView(filter=order_filtered_CDS),
                    size=12,
                    marker='square',
                    line_color='white',
                    fill_color=linear_cmap('Order', cc_colors, low=min(ccs['order']), high=max(ccs['order'])),
                    hover_color='black',
                    legend_label='CC Order {}'.format(len(cc_len) - i),
                    fill_alpha=1)

    else:
        for i in range(0, len(cc_len)):
            order_filtered_CDS = GroupFilter(column_name='Order', group=len(cc_len) - i)

            p.scatter('x_values', 'y_values', source=cc_plot_source,
                    view=CDSView(filter=sens_filtered_CDS & order_filtered_CDS),
                    size=12,
                    marker='square',
                    line_color='white',
                    fill_color=linear_cmap('Order', cc_colors, low=min(ccs['order']), high=max(ccs['order'])),
                    hover_color='black',
                    legend_label='CC Order {}'.format(len(cc_len) - i),
                    fill_alpha=1)
    
    # Add hover tool for CCs
    p.add_tools(HoverTool(tooltips=cc_TOOLS,
                        mode='mouse',
                        point_policy='follow_mouse'))

    # DNFs filtered by order
    all_dnf_plots = []
    for i in range(0, len(dnf_len)):
        dnf_plot = p.scatter('x_values', 'y_values', source=dnf_plot_source,
                view=CDSView(filter=GroupFilter(column_name='Order', group=len(dnf_len) - i)),
                size=13,
                marker='circle',
                line_color='white',
                fill_color=linear_cmap('Order', dnf_colors, low=min(dnfs['order']), high=max(dnfs['order'])),
                hover_color='black',
                legend_label='DNF Order {}'.format(len(dnf_len) - i),
                fill_alpha=1)
        all_dnf_plots.append(dnf_plot)

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


