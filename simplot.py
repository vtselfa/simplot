#!/bin/python

# Copyright (C) 2016  Vicent Selfa (viselol@disca.upv.es)
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
import math
import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.style
import matplotlib.ticker as ticker
import numpy as np
import os
import os.path as osp
import pandas as pd
import pylab as pl
import re
import sys
import traceback
import yaml

from matplotlib.backends.backend_pdf import PdfPages
from termcolor import colored


#
# Configure imports
#

# Better graph apparence
font = {
    'sans-serif' : 'DejaVu Sans',
    'monospace'  : 'DejaVu Sans Mono',
    'family'     : 'sans-serif',
    'weight'     : 'normal',
    'size'       : 20
}
legend = {
    'loc': 'best',
    'fontsize': 15
}
mpl.rc('font', **font)
mpl.rc('legend', **legend)

# Better dataframe pretty printing
pd.set_option('display.expand_frame_repr', False)


#
# Main program
#

def main():
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
    parser.add_argument('--mpl-style', default='bmh', metavar="STYLE", choices=mpl_styles, help='Matplotlib style. You can choose from: ' + ", ".join(mpl_styles))
    parser.add_argument('--size', type=float, nargs=2, default=(11.6, 8.2), metavar=('X', 'Y'), help='Size of the figure in inches.')
    parser.add_argument('--dpi', type=int, default=100, help='Dots Per Inch.')
    args = parser.parse_args()

    matplotlib.style.use(args.mpl_style)

    # Default grid
    if args.grid == []:
        args.grid = [(1,1)]

    # Merge plot_base + plot descriptions
    if args.plot_base:
        plots = list()
        for plot in args.plot:
            tmp = dict(args.plot_base)
            tmp.update(plot)
            plots.append(tmp)
        args.plot = plots

    figs, axes = create_figures(args.grid, args.title)

    # Read all datafiles into a dictionary indexed by filename and set it in the corresponding plot description
    dfs = dict()
    for plot in args.plot:
        datafile = plot["datafile"]
        if datafile not in dfs:
            dfs[datafile] = read_data(datafile)
        plot["df"] = dfs[datafile]
    del dfs

    plot_data(axes, args.plot)
    equalize_yaxis(axes, args.equal_yaxes)
    write_output(figs, args.size, args.dpi, args.output)


# Read CSV file and transform it to a pandas dataframe
def read_data(datafile):
    try:
        df = pd.read_table(datafile, sep=",")
    except:
        traceback.print_exc()
        print(colored("Error: Reading '{}'".format(datafile), "red"), file=sys.stderr)
        sys.exit(1)
    assert len(df.index) > 0, colored("The datafile '{}' is empty".format(datafile), "red")
    return df


# Create one figure per page and one ax per plot
def create_figures(grids, titles):
    assert titles == [] or len(grids) == len(titles), colored("If --title is used, a title for each figure must be provided", 'red')
    figures = []
    axes = []
    for (xgrid, ygrid), title in it.zip_longest(grids, titles):
        fig, axs = plt.subplots(xgrid, ygrid)
        if title:
            fig.suptitle(title, fontsize=15)
        try:
            axs = list(axs.ravel()) # 2D to 1D
        except AttributeError:
            axs = [axs]
        figures.append(fig)
        axes += axs
    return figures, axes


# Iterate plots and plot
def plot_data(axes, plots):
    for plot in plots:
        if plot["kind"] == "bars":
            plot = BarPlot(**plot)
        else:
            plot = LinePlot(**plot)
        ax = axes[plot.ax]               # Set axes
        plt.sca(ax)
        ax.autoscale(enable=True, axis='both', tight=True)
        plot.plot()


# Force the same ymin and mymax values for multiple plots
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
def write_output(figs, size, dpi, output):
    destdir = osp.dirname(output)
    if destdir != "":
        os.makedirs(osp.dirname(output), exist_ok=True)
    pdf = PdfPages(output)
    for p, fig in enumerate(figs):
        pl.figure(fig.number)
        fig.set_size_inches(*size)
        fig.set_dpi(dpi)
        fig.tight_layout(pad=0, w_pad=0, h_pad=0) # Better spacing between plots
        pdf.savefig(fig)
        plt.close(fig)
    pdf.close()


#
# Class that describes one plot
#

class Plot:
    kind = "Line/Area/Bars"
    title = ""

    # Target ax to be plotted in
    ax = 0

    # If it has been already plotted
    plotted = False

    # Congiguration for Matplotlib fonts
    font = {}

    # CSV datafile
    datafile = None

    # Dataframe
    df = None

    cols = None # List of ints
    labels = None  # List of strings

    # Arguments passed to the legend constructor
    legend_options = {"loc": "best"} # {} -> No legend

    # Rotation degrees for the x labels
    xrot = None

    # Convert to percentages
    ypercent = None

    # Labels for axes
    ylabel = ""
    xlabel = ""

    index = None # int


    def __init__(self):
        assert self.cols, colored("You shold provide some cols to plot e.g. --plot '{... cols: [1,2,3], ...}'", "red")
        assert self.index != None, colored("You shold provide an index e.g. --plot '{... index: 0, ...}'", "red")
        assert self.index not in self.cols, colored("You are trying to plot the index... cols is {} and the index is {}".format(self.cols, self.index), "red")

        # Map col to label
        self.colabel = dict()
        if self.labels:
            assert len(self.labels) == len(self.cols), colored("The number of labels and columns is different", 'red')
            for label, col in zip(self.labels, self.cols):
                self.colabel[df.columns[col]] = label

        # Store used columns names
        self.columns = [self.df.columns[col] for col in self.cols]

        # Set index
        self.df = self.df.set_index(self.df.columns[self.index])

        # In which ax has to be plotted
        if Plot.ax == self.ax:
            self.ax = Plot.ax
            Plot.ax += 1


    def check_and_set(self, kwds):
        for key in kwds:
            assert key in dir(self), colored("'{}' is not a valid keyword for this kind of plot".format(key), "red")
        self.__dict__.update(kwds)


    def plot(self):
        assert self.plotted == False, colored("This plot has been already plotted!", "red")

        # Mark this plot as plotted
        self.plotted = True

        # Set Matplotlib font
        # if self.font:
        #     mpl.rc('font', **self.font)

        ax = plt.gca()

        # Labels
        ax.set_title(self.title)
        ax.set_ylabel(self.ylabel, **self.font)
        ax.set_xlabel(self.xlabel, **self.font)

        # Scientific format tick labels
        if hasattr(self, "xscy") and self.xscy:
            plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
        if self.yscy:
            plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

        # Limits
        ax.set_ylim(top=self.ymax, bottom=self.ymin)
        xmin = None
        if hasattr(self, "xmin"):
            xmin = self.xmin
        xmax = None
        if hasattr(self, "xmax"):
            xmax = self.xmax
        ax.set_xlim(left=xmin, right=xmax)

        # X ticks
        if hasattr(self, "xstepsize") and self.xstepsize:
            start, end = ax.get_xlim()
            ax.xaxis.set_ticks(np.arange(start, end, self.xstepsize))
        if hasattr(self, "xnumsteps") and self.xnumsteps:
            start, end = ax.get_xlim()
            ax.xaxis.set_ticks(np.linspace(start, end, num=self.xnumsteps))

        # Percentage
        if self.ypercent:
            ax.yaxis.set_major_formatter(PercentFormatter)

        # Rotation
        if self.xrot:
            plt.xticks(rotation=self.xrot)


class BarPlot(Plot):
    kind = "bars"

    # Columns to use for errorbars
    ecols = [] # List of ints

    # Available keyworks for style:
    # hatches:    List of hatches to use.
    # hatchdensity: Int. How dense are the hatches.
    style = {"hatchdensity": 3}

    # Limits
    ymin = None # None / Float
    ymax = None # None / Float

    # Scientific notation in axes
    yscy = False

    # Log scale
    ylog = False

    # Errorbars {'min', 'max', 'both'}
    errorbars = "both"


    def __init__(self, **kwds):
        self.check_and_set(kwds)

        # Store used error column names
        self.ecolumns = [self.df.columns[ecol] for ecol in self.ecols]

        super().__init__()

        assert not self.ecols or len(self.cols) == len(self.ecols) or 2 * len(self.cols) == len(self.ecols),\
                colored("You have {} cols but {} error cols: error cols shold be 0, equal or double the number of cols".format(len(self.cols), len(self.ecols)), "red")


    def plot_bars(self, use_color=True, use_hatches=False):
        ax = plt.gca()
        values = self.df[self.columns]
        errors = None

        hatches = None
        if use_hatches:
            hatches = self.style.get("hatches", ('', '\\', 'x', '/', '.', '-', '|', '*', 'o', '+', 'O'))
            assert(len(self.cols) <= len(hatches)), colored("Not eneugh hatches", "red")

        # Error bars
        if self.ecols:
            errors = self.df[self.ecolumns]
            if self.errorbars == "max":
                assert len(self.cols) == len(self.ecols), colored("An error column is needed for each value column", "red")
                new_errors = list()
                for row in errors.values.T:
                    new_errors.append([[0] * len(row), row])
                errors = new_errors
            elif self.errorbars == "min":
                assert len(self.cols) == len(self.ecols), colored("An error column is needed for each value column", "red")
                new_errors = list()
                for row in errors.values.T:
                    new_errors.append([row, [0] * len(row)])
                errors = new_errors
            else:
                assert self.errorbars == "both", colored("'errorbars' allowed values are 'max', 'min' or 'both'" , "red")
                assert len(self.cols) * 2 == len(self.ecols), colored("Two error columns are needed for each value column", "red")
                errors = errors.values.T

        # Plot
        if not use_color:
            values.plot(yerr=errors, kind='bar', ax=ax, color="w", hatch=hatches)
        values.plot(yerr=errors, kind='bar', ax=ax, hatch=hatches)


    def plot(self):
        self.plot_bars()
        super().plot()


class LinePlot(Plot):
    kind = "line"

    # Available keyworks for style:
    # markers:    List of markers to use.
    # dashes:     List of dashes to use. Each dash is expressed as an string of chunks of symbols e.g. "---..." or "-.".
    #             "---..." is translated to 3 * dashsize dots of continuous line followed by  3 * dashsize blanc dots.
    # markersize: Size of the markers. Float value.
    # markevery:  Don't put a marker in every datapoint. Int value.
    # dashsize:   How many dots per symbol used describing the dashes.
    # linewidth   How thick the lines are.
    style = {}

    # Limits
    xmin = None # None / Float
    xmax = None # None / Float
    ymin = None # None / Float
    ymax = None # None / Float

    xstepsize = None
    xnumsteps = None

    # Scientific notation in axes
    xscy = False
    yscy = False

    # Log scale
    xlog = False
    ylog = False


    def __init__(self, **kwds):
        self.check_and_set(kwds)
        super().__init__()


    def plot_area(self):
        # Plot
        ax = plt.gca()
        columns = self.columns
        df[columns].plot(kind="area", colormap='cubehelix_r', ax=ax)

        # Workaround for inverting legend order
        handles, labels = ax.get_legend_handles_labels()
        labels = list(map(lambda x: self.colabel[x], labels))
        proxy = list()
        for i,h in enumerate(handles):
            proxy.append(mpl.patches.Rectangle((0, 0), 1, 1, fc=h.get_color()))
            ax.legend(proxy[::-1], labels[::-1], **self.legend_options)


    def plot_line(self, use_dashes=False, use_markers=False):
        ax = plt.gca()
        columns = self.columns

        lw = self.style.get("linewidth", 2)
        ms = self.style.get("markersize", 5)
        me = self.style.get("markevery", 1)
        ds = self.style.get("dashsize", 5)

        markers = [None]
        if use_markers:
            markers = self.style.get("markers", ('s', 'o', '^', '*', '>', '8', '<', 'p', 'v', 'h', 'H', 'D', 'd'))
            assert(len(columns) <= len(markers)), colored("Not eneugh markers", "red")

        dashes = [None]
        if use_dashes:
            dashes = self.style.get("dashes", ("-", "--..", "---.", "-."))
            tmp = list()
            for i, ls in enumerate(dashes):
                tmp.append([ds * len(list(group)) for c, group in it.groupby(ls)])
            dashes = tmp

        for c, (column, marker, dash) in enumerate(zip(columns, it.cycle(markers), it.cycle(dashes))):
            serie = self.df[column]
            serie = serie.dropna()
            line, = plt.plot(serie.index.values, serie.tolist(), linewidth=lw, label=self.colabel.get(column, column), axes=ax, color=cm.cubehelix(c / len(columns), 1), marker=marker, markersize=ms, markevery=me)
            if use_dashes:
                assert dash, "Invalid dash style"
                if len(dash) == 1:
                    dash = [] # Normal line
                line.set_dashes(dash)

        # Legend
        if self.legend_options != {}:
            handles, labels = ax.get_legend_handles_labels()
            ax.legend(handles, labels, **self.legend_options)

    def plot(self):
        if self.kind == "area" or self.kind == "a":
            self.plot_area()
        elif self.kind == "line" or self.kind == "l":
            self.plot_line()
        elif self.kind == "dashedline" or self.kind == "dl":
            self.plot_line(use_dashes=True)
        elif self.kind == "markedline" or self.kind == "ml":
            self.plot_line(use_markers=True)
        elif self.kind == "dashedmarkedline" or self.kind == "markeddashedline" or self.kind == "mdl" or self.kind == "dml":
            self.plot_line(use_markers=True, use_dashes=True)
        else:
            assert False, colored("Plot kind '{}' invalid)", "red")

        super().plot()




if __name__ == "__main__":
	main()
