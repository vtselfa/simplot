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
import importlib
import math
import matplotlib as mpl; mpl.use('Agg')
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
from matplotlib.ticker import FuncFormatter
from termcolor import colored
from cycler import cycler


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
mpl.rcParams['patch.force_edgecolor'] = True

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
    parser.add_argument('--mpl-style', default="default", metavar="STYLE", choices=mpl_styles, help='Matplotlib style. You can choose from: ' + ", ".join(mpl_styles))
    parser.add_argument('--size', type=float, nargs=2, default=(11.6, 8.2), metavar=('X', 'Y'), help='Size of the figure in inches.')
    parser.add_argument('--rect', type=float, nargs=4, default=[0, 0, 1, 1], metavar=('LEFT', 'BOTTOM', 'RIGHT', 'TOP'), help='Relative size of all the plots and titles in the figure.')
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
    write_output(figs, args.size, args.dpi, args.output, args.rect)


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
            fig.suptitle(title, fontsize=font["size"], y=1.05)
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
        if plot["kind"] in ["bars", "b", "stackedbars", "sb"]:
            plot = BarPlot(**plot)
        elif plot["kind"] == "box":
            plot = BoxPlot(**plot)
        else:
            plot = LinePlot(**plot)
        ax = axes[plot.ax]               # Set axes
        plt.sca(ax)
        ax.autoscale(enable=True, axis='both', tight=True)
        plot.plot()


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
def write_output(figs, size, dpi, output, rect):
    destdir = osp.dirname(output)
    if destdir != "":
        os.makedirs(osp.dirname(output), exist_ok=True)
    pdf = PdfPages(output)
    for p, fig in enumerate(figs):
        pl.figure(fig.number)
        fig.set_size_inches(*size)
        fig.set_dpi(dpi)
        extra_artists = [ax.legend_ for ax in fig.axes if ax.legend_]
        if fig._suptitle:
            extra_artists += [fig._suptitle]
        fig.tight_layout(pad=0, rect=rect) # Better spacing between plots
        pdf.savefig(fig, bbox_extra_artists=extra_artists, pad_inches = 0)
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

    # Horizontal aligment for x labels
    xtick_ha = "center"

    # Convert to percentages
    ypercent = None

    # Labels for axes
    ylabel = ""
    xlabel = ""

    # Use grid?
    xgrid = False
    ygrid = False

    # Limits
    ymin = None # None / Float
    ymax = None # None / Float

    # X/Y major/minor ticks locator. Either ["Locator", {"args": "for",  "the": "locator"}] or "Locator"
    # See http://matplotlib.org/api/ticker_api.html
    ymajorlocator = None
    xmajorlocator = None
    yminorlocator = None
    xminorlocator = None

    # Index column
    index = None # int

    colormap = None # Colormap to pick colors from
    color = None # Colors to override default style or colors from colormap
    starting_style = 0 # The colors and other propierties are cycled, this allows to pick a different starting style

    # Horizontal lines
    hl = []


    def __init__(self):
        # assert self.cols, colored("You shold provide some cols to plot e.g. --plot '{... cols: [1,2,3], ...}'", "red")
        assert self.index != None, colored("You shold provide an index e.g. --plot '{... index: 0, ...}'", "red")
        assert self.cols == None or self.index not in self.cols, colored("You are trying to plot the index... cols is {} and the index is {}".format(self.cols, self.index), "red")

        # If no cols are specified, we assume all but the index
        if not self.cols:
            self.cols = [i for i in range(len(self.df.columns)) if i != self.index]

        # Map col to label
        self.colabel = dict()
        if self.labels:
            assert len(self.labels) == len(self.cols), colored("The number of labels({}) and columns({}) is different".format(len(self.labels), len(self.cols)), 'red')
            for label, col in zip(self.labels, self.cols):
                self.colabel[self.df.columns[col]] = label

        # Store used columns names
        self.columns = [self.df.columns[col] for col in self.cols]

        # Set index
        self.df = self.df.set_index(self.df.columns[self.index])

        # In which ax has to be plotted
        if Plot.ax == self.ax:
            self.ax = Plot.ax
            Plot.ax += 1

        # Use colors from colormap
        if self.colormap:
            ax = plt.gca()
            cmap = plt.get_cmap(self.colormap)
            cmcolor = [cmap(c / (len(self.cols) + self.starting_style), 1) for c in range(len(self.cols) + self.starting_style)]

            # Override colors
            if self.color:
                for i, (c1, c2) in enumerate(zip(self.color, cmcolor)):
                    if (c1):
                        cmcolor[i] = c1
            self.color = cmcolor


    def check_and_set(self, kwds):
        for key in kwds:
            assert key in dir(self), colored("'{}' is not a valid keyword for this kind of plot".format(key), "red")
        self.__dict__.update(kwds)


    # Plot horizontal line
    def plot_hl(self):
        ax = plt.gca()
        if not isinstance(self.hl, list) or isinstance(self.hl[1], dict):
            self.hl = [self.hl]

        for line in self.hl:
            prop = {"color": "k", "lw" : 1}
            if isinstance(line, (list, tuple)):
                assert(len(line) == 2)
                assert(isinstance(line[1], dict))
                y = float(line[0])
                prop.update(line[1])
            else:
                y = float(line)

            x = ax.get_xlim()
            plt.plot((x[0], x[1]), (y, y), **prop)



    def plot(self):
        assert self.plotted == False, colored("This plot has been already plotted!", "red")

        # Mark this plot as plotted
        self.plotted = True

        ax = plt.gca()

        # Labels
        ax.set_title(self.title)
        ax.set_ylabel(self.ylabel, **self.font)
        ax.set_xlabel(self.xlabel, **self.font)

        if "size" in self.font:
            plt.tick_params(axis='both', which='major', labelsize=self.font["size"])

        # Limits
        ax.set_ylim(top=self.ymax, bottom=self.ymin)
        xmin = None
        if hasattr(self, "xmin"):
            xmin = self.xmin
        xmax = None
        if hasattr(self, "xmax"):
            xmax = self.xmax
        ax.set_xlim(left=xmin, right=xmax)

        # X/Y tick locators
        for setter, locator in [(ax.xaxis.set_major_locator, self.xmajorlocator), (ax.yaxis.set_major_locator, self.ymajorlocator), (ax.xaxis.set_minor_locator, self.xminorlocator), (ax.yaxis.set_minor_locator, self.yminorlocator)]:
            if locator:
                if isinstance(locator, list):
                    assert(len(locator) == 2)
                    loc = locator[0]
                    args = locator[1]
                    assert isinstance(loc, str)
                    assert isinstance(args, dict)
                else:
                    loc = locator
                    args = {}
                locator = getattr(ticker, loc)
                setter(locator(**args))

        # Percentage
        if self.ypercent:
            ax.yaxis.set_major_formatter(PercentFormatter)

        # X tick rotation and horizontal alingment
        if self.xrot != None:
            plt.xticks(rotation=self.xrot, horizontalalignment=self.xtick_ha)

        # Grid
        if self.xgrid != None:
            ax.xaxis.grid(self.xgrid)
        if self.ygrid != None:
            ax.yaxis.grid(self.ygrid)

        # Draw horizontal lines
        if self.hl:
            self.plot_hl()

        # Remove legend
        if self.legend_options == {}:
            ax.legend().remove()


class BoxPlot(Plot):
    kind = "box"
    xrot = 45

    def __init__(self, **kwds):
        self.check_and_set(kwds)
        super().__init__()


    def plot_box(self):
        columns = self.df[self.columns]
        if self.labels:
            labels = self.labels
        else:
            labels = columns.columns

        # Plot
        plt.boxplot(columns.T.values.tolist(), labels=labels)


    def plot(self):
        self.plot_box()
        super().plot()


class BarPlot(Plot):
    kind = "bars"

    # Columns to use for errorbars
    ecols = [] # List of ints

    # Errorbars {'min', 'max', 'both'}
    errorbars = "both"

    hatches = ('', '\\', 'x', '/', '.', '-', '|', '*', 'o', '+', 'O')


    def __init__(self, **kwds):
        self.check_and_set(kwds)

        # Store used error column names
        self.ecolumns = [self.df.columns[ecol] for ecol in self.ecols]

        super().__init__()

        assert not self.ecols or len(self.cols) == len(self.ecols) or 2 * len(self.cols) == len(self.ecols),\
                colored("You have {} cols but {} error cols: error cols shold be 0, equal or double the number of cols".format(len(self.cols), len(self.ecols)), "red")


    def plot_bars(self, stacked=False):
        ax = plt.gca()
        values = self.df[self.columns]
        errors = None

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

        legend = None
        if stacked:
            legend = "reverse"

        # Plot
        values.plot(yerr=errors, kind='bar', stacked=stacked, ax=ax, error_kw={"elinewidth":1}, legend=legend)

        # Ugly fix for hatches
        if self.hatches:
            # Posible hatches ('', '\\', 'x', '/', '.', '-', '|', '*', 'o', '+', 'O')
            bars = ax.patches
            aux = []
            for h in self.hatches:
                aux += [h] * len(values)
            hatches = aux
            for bar, hatch in zip(bars, hatches):
                bar.set_hatch(hatch)

        # Ugly fix for colors...
        bars = ax.patches
        aux = []
        for c, _ in zip(ax._get_lines.prop_cycler, bars):
            c = c["color"]
            aux += [c] * len(values)
        colors = aux
        for bar, c in zip(bars, colors):
            bar.set_facecolor(c)
        if self.color:
            colors = self.color
            bars = ax.patches
            aux = []
            for c in colors:
                aux += [c] * len(values)
            colors = aux
            for bar, c in zip(bars, colors):
                bar.set_facecolor(c)

        # Legend
        handles, labels = ax.get_legend_handles_labels()
        if self.labels:
            labels = self.labels
        ax.legend(handles, labels, **self.legend_options)


    def plot(self):
        if self.kind in ["sb", "stackedbars", "sbars"]:
            self.plot_bars(stacked=True)
        else:
            self.plot_bars()
        super().plot()


class LinePlot(Plot):
    kind = "line"

    linewidth = 2
    linestyle = None
    marker = None
    markersize = 6
    markevery = 1
    markeredgecolor = 'k'
    markeredgewidth = 0.5

    # Limits
    xmin = None # None / Float
    xmax = None # None / Float


    def __init__(self, **kwds):
        self.check_and_set(kwds)
        super(LinePlot, self).__init__()


    def plot_area(self, stacked=False):
        # Plot
        ax = plt.gca()
        columns = self.columns

        legend = None
        if stacked:
            legend = "reverse"

        self.df[columns].plot(kind="area", colormap=self.colormap, ax=ax, stacked=stacked, legend=legend)

        # Legend
        handles, labels = ax.get_legend_handles_labels()
        labels = [self.colabel.get(column, column) for column in columns]
        ax.legend(handles, labels, **self.legend_options)


    def plot_line(self):
        ax = plt.gca()
        columns = self.columns
        style_props = ["color", "linewidth", "linestyle", "marker", "markersize", "markevery", "markeredgecolor", "markeredgewidth"]

        # Convert all the style propierties into cycle iterators and set them to the correct starting point
        style_cycler = None
        for prop in style_props:
            value = getattr(self, prop)
            if value == None:
                continue
            if not isinstance(value, list):
                value = [value]
            prop_cycler = cycler(prop, value) * (len(columns) + self.starting_style)
            if not style_cycler:
                style_cycler = prop_cycler
            else:
                style_cycler += prop_cycler

        for _ in range(self.starting_style):
            next(style_cycler)

        for column, sty in zip(columns, style_cycler):
            serie = self.df[column]
            serie = serie.dropna()
            line, = plt.plot(serie.index.values, serie.tolist(), label=self.colabel.get(column, column), axes=ax, **sty)

        # Legend
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels, **self.legend_options)


    def plot(self):
        valid = False

        if self.kind == "area" or self.kind == "a":
            valid = True
            self.plot_area()
        elif self.kind == "stackedarea" or self.kind == "sa":
            valid = True
            self.plot_area(stacked=True)
        else:
            if self.kind == "line" or self.kind == "l":
                valid = True

            if self.kind in ["dashedline", "dl", "dashedmarkedline", "markeddashedline", "mdl", "dml"]:
                valid = True
                if not self.linestyle:
                    self.linestyle = ('-', '--  ', '--- ', '- ')

            if self.kind in ["markedline", "ml", "dashedmarkedline", "markeddashedline", "mdl", "dml"]:
                valid = True
                if not self.marker:
                    self.marker = ['s', 'o', '^', '>', '*', '<', 'p', 'v', 'h', 'H', 'D', 'd']

            self.plot_line()

        if not valid:
            assert False, colored("Plot kind '{}' is not valid)".format(self.kind), "red")

        super().plot()


def to_percent(y, position):
    # Ignore the passed in position. This has the effect of scaling the default
    # tick locations.
    s = "{0:g}".format(100 * y)

    # The percent symbol needs escaping in latex
    if mpl.rcParams['text.usetex'] is True:
        return s + r'$\%$'
    else:
        return s + '%'
PercentFormatter = FuncFormatter(to_percent)



if __name__ == "__main__":
	main()
