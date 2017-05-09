#!/bin/python

# Copyright (C) 2017  Vicent Selfa (viselol@disca.upv.es)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


import argparse
import itertools as it
import matplotlib as mpl;
import matplotlib.pyplot as plt
import matplotlib.style
import numpy as np
import os
import os.path as osp
import pandas as pd
import pylab as pl
import traceback
import yaml

from matplotlib.backends.backend_pdf import PdfPages
from termcolor import colored

import plot


def parse_args(args=None):
    mpl_styles = matplotlib.style.available
    parser = argparse.ArgumentParser(description = colored('Line, area and bar plots for csv files. Required arguments are represented in ' + colored('red', 'red') + '.', attrs=['bold']))
    parser.add_argument('-p', '--plot', type=yaml.load, action='append', help='Plot in YAML dictionary format. '
            'E.g. --plot {kind: line, datafile: input.csv, index: 0, cols: [1,2,3,4], ylabel: Foo, xlabel: Bar} '
            'This option can be used multiple times to define more plots.', default=[], metavar=colored('PLOT', 'red'), required=True)
    parser.add_argument('--plot-base', type=yaml.load, help='Plot in YAML dictionary format. See --plot.', default="{}")
    parser.add_argument('-g', '--grid', action='append', type=int, nargs=2, default=[], metavar=('ROWS', 'COLS'), help='Number of rows and columns of plots. '
            'Use this argument multiple times to descrive the pages of a multipage PDF. Plots are put on the grid spaces left-right and up-down.')
    parser.add_argument('--equal-yaxes', action='append', nargs='+', default=[], metavar="PLOT_ID", help='Equalize the axes of the subplot IDs passed as an argument. '
            'This option can be specified multiple times in order to have diferent groups of plots with different axes.')
    parser.add_argument('--title', action='append', default=[], help='Title for each figure.')
    parser.add_argument('-o', '--output', default='./plot.pdf', help='PDF output.')
    parser.add_argument('--size', type=float, nargs=2, default=(11.6, 8.2), metavar=('X', 'Y'), help='Size of the figure in inches.')
    parser.add_argument('--rect', type=float, nargs=4, default=[0, 0, 1, 1], metavar=('LEFT', 'BOTTOM', 'RIGHT', 'TOP'), help='Relative size of all the plots and titles in the figure.')
    parser.add_argument('--dpi', type=int, default=100, help='Dots Per Inch.')

    args =  parser.parse_args(args)

    # Merge plot_base and plot descriptions
    if args.plot_base:
        plots = list()
        for p in args.plot:
            p = merge_dict(dict(args.plot_base), p)
            plots.append(p)
        args.plot = plots

    # Default grid
    if args.grid == []:
        args.grid = [(1,1)]

    return args


def main():
    args = parse_args()
    figs, axes = create_figures(args.grid, args.size, args.dpi)
    plot_data(figs, axes, args.plot, args.title, args.equal_yaxes, args.rect)
    write_output(figs, args.output, args.rect)


def merge_dicts(a, b, path=None):
    "merges b into a"
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            else:
                a[key] = b[key]
        else:
            a[key] = b[key]
    return a


# Create one figure per page and one ax per plot
def create_figures(grids, size, dpi):
    plt.style.use(['default'])
    mpl.rcParams['patch.force_edgecolor'] = True
    figures = []
    axes = []
    for (xgrid, ygrid) in grids:
        fig, axs = plt.subplots(xgrid, ygrid)
        fig.set_size_inches(*size)
        fig.set_dpi(dpi)
        try:
            axs = list(axs.ravel()) # 2D to 1D
        except AttributeError:
            axs = [axs]
        figures.append(fig)
        axes += axs
    return figures, axes


# Iterate plots and plot
def plot_data(figs, axes, plots, titles, equal_yaxes_groups, rect):
    assert titles == [] or len(figs) == len(titles), colored("If --title is used, a title for each figure must be provided", 'red')
    axnum = 0
    for p in plots:
        if p["kind"] in ["bars", "b", "stackedbars", "sb"]:
            p = plot.BarPlot(**p)
        elif p["kind"] == "box":
            p = plot.BoxPlot(**p)
        else:
            p = plot.LinePlot(**p)

        # Set ax to plot into
        if p.axnum != None:
            ax = axes[p.axnum]
        else:
            ax = axes[axnum]
            axnum += 1

        plt.sca(ax)
        ax.autoscale(enable=True, axis='both', tight=True)
        p.plot()
    equalize_yaxis(axes, equal_yaxes_groups)
    for fig, title in it.zip_longest(figs, titles):
        if title:
            fig.suptitle(title)
            if rect == [0, 0, 1, 1]:
                rect = (0, 0, 1, 0.91)
        fig.tight_layout(pad=0, rect=rect) # Better spacing between plots


# Force the same ymin and ymax values for multiple plots
def equalize_yaxis(axes, groups):
    for group in groups:
        ymin = float("+inf")
        ymax = float("-inf")
        group = [axes[i] for i in group] # Translate IDs to axes
        for ax in group:
            y1, y2 = ax.get_ylim()
            ymin = min(ymin, y1)
            ymax = max(ymax, y2)
        for ax in group:
            ax.set_ylim(top=ymax, bottom=ymin)


# Write plots to pdf, creating dirs, if needed
def write_output(figs, output, rect):
    destdir = osp.dirname(output)
    if destdir != "":
        os.makedirs(osp.dirname(output), exist_ok=True)
    pdf = PdfPages(output)
    for p, fig in enumerate(figs):
        pl.figure(fig.number)
        pdf.savefig(fig, pad_inches = 0)
        plt.close(fig)
    pdf.close()


if __name__ == "__main__":
        main()
