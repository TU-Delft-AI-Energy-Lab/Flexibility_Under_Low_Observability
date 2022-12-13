#!/usr/bin/env python
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.spatial import ConvexHull
from matplotlib.colors import LogNorm

__author__ = "Demetris Chrysostomou"
__credits__ = ["Demetris Chrysostomou", "Jose Luis Rueda Torres", "Jochen Lorenz Cremer"]
__version__ = "1.0.0"
__maintainer__ = "Demetris Chrysostomou"
__email__ = "D.Chrysostomou@tudelft.nl"
__status__ = "Production"


def plot_mc(x_flexible, y_flexible, x_non_flexible, y_non_flexible, operating_point, no_samples, scenario_name,
            dur_samples, dur_pf):
    """ Plot Monte Carlo simulation results

    :param x_flexible: feasible P, [list of floats]
    :param y_flexible: feasible Q, [list of floats]
    :param x_non_flexible: infeasible P, [list of floats]
    :param y_non_flexible: infeasible Q, [list of floats]
    :param operating_point: initial y (PCC P,Q), [list of floats]
    :param no_samples: number of samples run, [int]
    :param scenario_name: name of scenario used, [str]
    :param dur_samples: duration in s for the sample creation, [float]
    :param dur_pf: duration in s for the power flows, [float]
    """
    text = f'Total duration: {dur_samples + dur_pf} [s]\n{no_samples} Sample creation duration: {dur_samples} [s]' \
           f'\nTotal Power Flow duration: {dur_pf} [s]'
    plot_only_feasible(x_flexible, y_flexible, operating_point, scenario_name, text)
    plot_feasible_and_infeasible(x_flexible, y_flexible, x_non_flexible, y_non_flexible, operating_point,
                                 scenario_name, text)
    return


def plot_feasible_and_infeasible(x_flexible, y_flexible, x_non_flexible, y_non_flexible, operating_point,
                                 scenario_name, text):
    """ Plot Monte Carlo simulation results including infeasible samples

    :param x_flexible: feasible P, [list of floats]
    :param y_flexible: feasible Q, [list of floats]
    :param x_non_flexible: infeasible P, [list of floats]
    :param y_non_flexible: infeasible Q, [list of floats]
    :param operating_point: initial y (PCC P,Q), [list of floats]
    :param scenario_name: name of scenario used, [str]
    :param text: text to be put at the bottom of the figure, [str]
    """
    sns.set(style="darkgrid")
    fig = plt.figure(figsize=(10, 5))
    plt.scatter(x_non_flexible, y_non_flexible, c="darkblue", s=10, label='Non Feasible Samples')
    plt.scatter(x_flexible, y_flexible, c="darkorange", s=10, label='Feasible Samples')
    plt.scatter(operating_point[0], operating_point[1], c="red", s=50, label='Operating Point')
    plt.grid()
    plt.xlabel("P [MW]")
    plt.ylabel("Q [MVAr]")
    plt.grid()
    plt.legend()
    plt.text(0.5, -0.1, text, horizontalalignment='center', verticalalignment='center', fontsize=12,
             transform=plt.gcf().transFigure)
    fig.savefig('plots/' + scenario_name + '_incl_infeasible.jpg', bbox_inches='tight', pad_inches=0.5, dpi=500)
    return


def plot_only_feasible(x_flexible, y_flexible, operating_point, scenario_name, text):
    """Plot Monte Carlo simulation results only for feasible samples

    :param x_flexible: feasible P, [list of floats]
    :param y_flexible: feasible Q, [list of floats]
    :param operating_point: initial y (PCC P,Q), [list of floats]
    :param scenario_name: name of scenario used, [str]
    :param text: text to be put at the bottom of the figure, [str]
    """
    sns.set(style="darkgrid")
    fig = plt.figure(figsize=(10, 5))
    plt.scatter(x_flexible, y_flexible, c="darkorange", s=10, label='Feasible Samples')
    plt.scatter(operating_point[0], operating_point[1], c="red", s=50, label='Operating Point')
    plt.grid()
    plt.xlabel("P [MW]")
    plt.ylabel("Q [MVAr]")
    plt.legend()
    plt.grid()
    plt.text(0.5, -0.1, text, horizontalalignment='center', verticalalignment='center', fontsize=12,
             transform=plt.gcf().transFigure)
    fig.savefig('plots/'+scenario_name+'.jpg', bbox_inches='tight', pad_inches=0.5, dpi=500)
    return


def get_convex_hull_combination(filenames, legends, operating_point, name='', plot_type='svg'):
    """Plot Monte Carlo simulation results including the convex hull area for 6 scenarios

    :param filenames: filenames of csv results from the scenarios that will be plotted, [list of str]
    :param legends: scenario names, [list of str]
    :param operating_point: initial y (PCC P,Q) for all scenarios, [list of (scenarios) list of (P,Q) floats]
    :param name: name for plot, [str]
    :param plot_type: type of figure e.g.svg, png, jpg, [str]
    """
    df_list = []
    sns.set(style="darkgrid")
    back_ground_col = 'darkblue'
    fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(15, 10))
    for filename in filenames:
        df_list.append(pd.read_csv(f"csv_results/{filename}"))
    axs = [ax1, ax2, ax3, ax4, ax5, ax6]
    hull_areas = {}
    for idx, df in enumerate(df_list):
        xy_flexible = df[['x flex', 'y flex']].to_numpy()
        xy_flexible = xy_flexible[~np.all(xy_flexible == 0, axis=1)]
        xy_hull = ConvexHull(xy_flexible)
        axs[idx].scatter(xy_flexible[:, 0], xy_flexible[:, 1], s=15, label=f'Feasible Samples', c='darkorange', alpha=1)
        kl = 0
        for simplex in xy_hull.simplices:
            if kl == 0:
                kl = 1
                axs[idx].plot(xy_flexible[simplex, 0], xy_flexible[simplex, 1], 'k-', label='Convex Hull Area',
                              c='green', linewidth=3)
            else:
                axs[idx].plot(xy_flexible[simplex, 0], xy_flexible[simplex, 1], 'k-', c='green', linewidth=3)
        axs[idx].scatter(operating_point[idx][0], operating_point[idx][1], c="red", s=200, label='Operating Point')
        axs[idx].grid()
        axs[idx].set_xlabel("P [MW]", fontsize=12)
        axs[idx].set_ylabel("Q [MVAr]", fontsize=12)
        axs[idx].set_title(legends[idx], fontsize=12)
        axs[idx].legend(prop={'size': 12})

    fig.savefig('plots/Hull_combination'+name+'.'+plot_type, bbox_inches='tight', pad_inches=0.5, dpi=500)

    fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(15, 10))
    axs = [ax1, ax2, ax3, ax4, ax5, ax6]
    for idx, df in enumerate(df_list):
        x_non_flexible = df['x non-flex']
        y_non_flexible = df['y non-flex']
        x_non_flexible = x_non_flexible[x_non_flexible != 0.]
        y_non_flexible = y_non_flexible[y_non_flexible != 0.]

        axs[idx].scatter(x_non_flexible, y_non_flexible, c=back_ground_col, s=15, label='Non Feasible Samples', alpha=1)
        xy_flexible = df[['x flex', 'y flex']].to_numpy()
        xy_flexible = xy_flexible[~np.all(xy_flexible == 0., axis=1)]
        xy_hull = ConvexHull(xy_flexible)
        axs[idx].scatter(xy_flexible[:, 0], xy_flexible[:, 1], s=15, label=f'Feasible Samples', c='darkorange', alpha=1)
        kl = 0
        for simplex in xy_hull.simplices:
            if kl == 0:
                kl = 1
                axs[idx].plot(xy_flexible[simplex, 0], xy_flexible[simplex, 1], 'k-',
                              label='Convex Hull Area', c='green', linewidth=3)
            else:
                axs[idx].plot(xy_flexible[simplex, 0], xy_flexible[simplex, 1], 'k-', c='green', linewidth=3)

        axs[idx].scatter(operating_point[idx][0], operating_point[idx][1], c="red", s=200, label='Operating Point')
        axs[idx].grid()
        axs[idx].set_xlabel("P [MW]", fontsize=12)
        axs[idx].set_ylabel("Q [MVAr]", fontsize=12)
        if idx == len(df_list) -1:
            axs[idx].set_title(legends[idx], fontsize=12)
            axs[idx].legend(prop={'size': 12})
        hull_areas[legends[idx]] = xy_hull.area
    fig.tight_layout(pad=1.0)
    fig.savefig('plots/Hull_combination'+name+'_incl_infeas.'+plot_type,
                bbox_inches='tight', pad_inches=0.5, dpi=300)
    return hull_areas


def get_convex_hull(filenames, legends, operating_point, name='', plot_type='svg'):
    """Plot n Monte Carlo simulation results individually for n scenarios including their convex hull area

    :param filenames: filenames of csv results from the scenarios that will be plotted, [list of str]
    :param legends: scenario names, [list of str]
    :param operating_point: initial y (PCC P,Q) for all scenarios, [list of (scenarios) list of (P,Q) floats]
    :param name: name for plot, [str]
    :param plot_type: type of figure e.g.svg, png, jpg, [str]
    """
    df_list = []
    plt.rcParams['svg.fonttype'] = 'none'
    sns.set(style="ticks")
    back_ground_col = 'darkblue'
    for filename in filenames:
        df_list.append(pd.read_csv(f"csv_results/{filename}"))
    hull_areas = {}

    for idx, df in enumerate(df_list):
        fig = plt.figure(figsize=(6, 6))

        x_non_flexible = df['x non-flex']
        y_non_flexible = df['y non-flex']
        x_non_flexible = x_non_flexible[x_non_flexible != 0]
        y_non_flexible = y_non_flexible[y_non_flexible != 0]

        plt.scatter(x_non_flexible, y_non_flexible, c=back_ground_col, s=15,
                    label='Non Feasible Samples', alpha=1, rasterized=True)
        xy_flexible = df[['x flex', 'y flex']].to_numpy()
        xy_flexible = xy_flexible[~np.all(xy_flexible == 0, axis=1)]
        xy_hull = ConvexHull(xy_flexible)
        plt.scatter(xy_flexible[:, 0], xy_flexible[:, 1], s=15,
                    label=f'Feasible Samples', c='darkorange', alpha=1, rasterized=True)
        kl = 0
        for simplex in xy_hull.simplices:
            if kl == 0:
                kl = 1
                plt.plot(xy_flexible[simplex, 0], xy_flexible[simplex, 1], 'k-', label='Convex Hull Area',
                              c='green', linewidth=3)
            else:
                plt.plot(xy_flexible[simplex, 0], xy_flexible[simplex, 1], 'k-', c='green', linewidth=3)
        plt.scatter(operating_point[idx][0], operating_point[idx][1], c="red",
                    s=200, label='Operating Point', rasterized=True)
        plt.grid()
        plt.xlabel(r"P $[MW]$", fontsize=18)
        plt.ylabel(r"Q $[MVAr]$", fontsize=18)
        hull_areas[legends[idx]] = xy_hull.area
        fig.savefig('plots/convex_hull' + name + legends[idx] + '.'+plot_type, dpi=300)
    return hull_areas


def plot_6_mc_flex_from_file(filenames, legends, operating_point, name='', plot_type='jpg'):
    """ Plot Monte Carlo simulation results for 6 scenarios

    :param filenames: filenames of csv results from the scenarios that will be plotted, [list of str]
    :param legends: scenario names, [list of str]
    :param operating_point: initial y (PCC P,Q) for all scenarios, [list of (scenarios) list of (P,Q) floats]
    :param name: name for plot, [str]
    :param plot_type: type of figure e.g.svg, png, jpg, [str]
    """
    df_list = []
    sns.set(style="darkgrid")
    back_ground_col = 'darkblue'
    fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(15, 10))
    for filename in filenames:
        df_list.append(pd.read_csv(f"csv_results/{filename}"))
    axs = [ax1, ax2, ax3, ax4, ax5, ax6]
    for idx, df in enumerate(df_list):
        x_flexible = df['x flex']
        y_flexible = df['y flex']
        x_flexible = x_flexible[x_flexible != 0.]
        y_flexible = y_flexible[y_flexible != 0.]
        axs[idx].scatter(x_flexible, y_flexible, s=15, label=f'Feasible Samples', c='darkorange', alpha=1)
        axs[idx].scatter(operating_point[idx][0], operating_point[idx][1], c="red", s=200, label='Operating Point')
        axs[idx].grid()
        axs[idx].set_xlabel("P [MW]", fontsize=12)
        axs[idx].set_ylabel("Q [MVAr]", fontsize=12)
        axs[idx].set_title(legends[idx], fontsize=12)
        axs[idx].legend(prop={'size': 12})
    fig.savefig(f'plots/combination_of_6_areas_{name}.{plot_type}', bbox_inches='tight', pad_inches=0.5, dpi=500)
    fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(15, 10))
    axs = [ax1, ax2, ax3, ax4, ax5, ax6]
    for idx, df in enumerate(df_list):

        x_non_flexible = df['x non-flex']
        y_non_flexible = df['y non-flex']
        x_non_flexible = x_non_flexible[x_non_flexible != 0.]
        y_non_flexible = y_non_flexible[y_non_flexible != 0.]

        axs[idx].scatter(x_non_flexible, y_non_flexible, c=back_ground_col, s=15, label='Non Feasible Samples', alpha=1)
        x_flexible = df['x flex']
        y_flexible = df['y flex']
        x_flexible = x_flexible[x_flexible != 0.]
        y_flexible = y_flexible[y_flexible != 0.]
        axs[idx].scatter(x_flexible, y_flexible, s=15, label=f'Feasible Samples', c='darkorange', alpha=1)
        axs[idx].scatter(operating_point[idx][0], operating_point[idx][1], c="red", s=200, label='Operating Point')
        axs[idx].grid()
        axs[idx].set_xlabel("P [MW]", fontsize=12)
        axs[idx].set_ylabel("Q [MVAr]", fontsize=12)
        axs[idx].set_title(legends[idx], fontsize=12)
        axs[idx].legend(prop={'size': 12})
    fig.tight_layout(pad=1.0)
    fig.savefig(f'plots/combination_of_6_areas_{name}_incl_infeas.{plot_type}',
                bbox_inches='tight', pad_inches=0.5, dpi=500)
    return


def get_multiplicity(filenames, legends, name='', plot_type='jpg', decimals=2, step=0.01):
    """ Plot Monte Carlo simulation multiplicity results for 6 scenarios

    :param filenames: filenames of csv results from the scenarios that will be plotted, [list of str]
    :param legends: scenario names, [list of str]
    :param name: name for plot, [str]
    :param plot_type: type of figure e.g.svg, png, jpg, [str]
    :param decimals: decimals by which the resulted y will be roundedm [int]
    :param step: smallest step in the above decimals e.g.3 decimals -> 0.001, [float]
    """
    df_list = []
    sns.set(style="darkgrid")
    fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(15, 10))
    for filename in filenames:
        df_list.append(pd.read_csv(f"csv_results/{filename}"))
    axs = [ax1, ax2, ax3, ax4, ax5, ax6]
    for idx, df in enumerate(df_list):
        xy_flexible = df[['x flex', 'y flex']].round(decimals)
        xy_flexible['Multiplicity'] = np.ones_like(df['x flex'].to_numpy())
        xy_flexible["Multiplicity"] = xy_flexible["Multiplicity"].astype(int)
        xy_new = xy_flexible.groupby(['x flex', 'y flex'], as_index=False).sum()
        heat_mat, x_axis, y_axis = get_heatmap_matrix(xy_new, decimals, step)
        sns.heatmap(heat_mat, norm=LogNorm(), ax=axs[idx], cmap='flare')
        axs[idx].grid()
        axs[idx].set_xlabel("P [MW]", fontsize=12)
        axs[idx].set_ylabel("Q [MVAr]", fontsize=12)
        axs[idx].set_xticks(x_axis)
        axs[idx].set_yticks(y_axis)
        axs[idx].invert_yaxis()
        axs[idx].set_title(legends[idx], fontsize=12)
        plt.tight_layout()
    print('Plotting multiplicity...')
    fig.savefig('plots/Multiplicity'+name+'.'+plot_type, bbox_inches='tight', pad_inches=0.5, dpi=500)
    return


def get_heatmap_matrix(df, decimals, step):
    """ Returns the heatmap of the dataframe with feasible y

    :param df: dataframe with flexibility area values y
    :param decimals: decimals by which the resulted y will be roundedm [int]
    :param step: smallest step in the above decimals e.g.3 decimals -> 0.001, [float]
    :return: heat_mat=heatmap matrix, x_axis=x axis values, y_axis=y_axis values
    """
    mix_x = round(np.min(df['x flex']) - (np.max(df['x flex']) - np.min(df['x flex']))/10, decimals)
    max_x = round(np.max(df['x flex']) + (np.max(df['x flex']) - np.min(df['x flex']))/10, decimals)
    mix_y = round(np.min(df['y flex']) - (np.max(df['y flex']) - np.min(df['y flex']))/10, decimals)
    max_y = round(np.max(df['y flex']) + (np.max(df['y flex']) - np.min(df['y flex']))/10, decimals)
    x_axis = np.arange(mix_x, max_x+step, step)
    y_axis = np.arange(mix_y, max_y+step, step)
    heat_mat = np.zeros((len(y_axis), len(x_axis)))
    for row in df.iterrows():
        x_idx, = np.where(np.isclose(x_axis, row[1]['x flex'], atol=step/2))
        y_idx, = np.where(np.isclose(y_axis, row[1]['y flex'], atol=step/2))
        heat_mat[y_idx, x_idx] = heat_mat[y_idx, x_idx] + row[1]['Multiplicity']
    return heat_mat, x_axis, y_axis


