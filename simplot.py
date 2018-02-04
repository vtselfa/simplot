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
import matplotlib as mpl; mpl.use("Agg")
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
    parser.add_argument('--equal-yaxes', action='append', nargs='+', type=int,  default=[], metavar="PLOT_ID", help='Equalize the Y axes of the subplot IDs passed as an argument. '
            'This option can be specified multiple times in order to have diferent groups of plots with different axes.')
    parser.add_argument('--equal-xaxes', action='append', nargs='+', type=int, default=[], metavar="PLOT_ID", help='Equalize the X axes of the subplot IDs passed as an argument. '
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
            p = merge_dicts(dict(args.plot_base), p)
            plots.append(p)
        args.plot = plots

    # Default grid
    if args.grid == []:
        args.grid = [(1,1)]

    return args


def default_args():
    args = parse_args("--plot {}".split())
    args.plot = list()
    return args


def main():
    args = parse_args()
    figs, axes = create_figures(args.grid, args.size, args.dpi)
    plot_data(figs, axes, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    write_output(figs, args.output, args.rect)


def merge_dicts(a, b, path=None):
    "merges b into a"
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge_dicts(a[key], b[key], path + [str(key)])
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
def plot_data(figs, axes, plots, titles, equal_xaxes_groups, equal_yaxes_groups, rect):
    assert titles == [] or len(figs) == len(titles), colored("If --title is used, a title for each figure must be provided", 'red')
    axnum = 0
    for p, desc in enumerate(plots):
        if desc["kind"] in ["bars", "b", "stackedbars", "sb", "mibars"]:
            plots[p] = plot.BarPlot(**desc)
        elif desc["kind"] == "box":
            plots[p] = plot.BoxPlot(**desc)
        else:
            plots[p] = plot.LinePlot(**desc)

        obj = plots[p]

        # Set ax to plot into
        if obj.axnum != None:
            ax = axes[obj.axnum]
        else:
            assert len(axes) > axnum, colored("Too many plots for this grid", 'red')
            ax = axes[axnum]
            axnum += 1

        plt.sca(ax)
        ax.autoscale(enable=True, axis='both', tight=True)
        obj.plot()

    equalize_xaxis(plots, equal_xaxes_groups)
    equalize_yaxis(plots, equal_yaxes_groups)

    # Plot lines here because equalize axis may have modified the plots
    for obj in plots:
        plt.sca(obj.ax)
        obj.plot_hl()
        obj.plot_vl()

    for fig, title in it.zip_longest(figs, titles):
        if title:
            fig.suptitle(title)
            if rect == [0, 0, 1, 1]:
                rect = (0, 0, 1, 0.91)
        fig.tight_layout(pad=0, rect=rect) # Better spacing between plots


# Force the same ymin and ymax values for multiple plots
def equalize_yaxis(plots, groups):
    for group in groups:
        ymin = float("+inf")
        ymax = float("-inf")
        group = [plots[i].ax for i in group] # Translate IDs to axes
        for ax in group:
            y1, y2 = ax.get_ylim()
            ymin = min(ymin, y1)
            ymax = max(ymax, y2)
        for ax in group:
            ax.set_ylim(top=ymax, bottom=ymin)


# Force the same ymin and ymax values for multiple plots
def equalize_xaxis(plots, groups):
    for group in groups:
        xmin = float("+inf")
        xmax = float("-inf")
        group = [plots[i].ax for i in group] # Translate IDs to axes
        for ax in group:
            x1, x2 = ax.get_xlim()
            xmin = min(xmin, x1)
            xmax = max(xmax, x2)
        for ax in group:
            ax.set_xlim(right=xmax, left=xmin)


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
