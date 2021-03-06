import itertools as it
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import random
import re
import sys
import traceback

from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import FuncFormatter
from termcolor import colored
from cycler import cycler
from matplotlib.patches import Patch
from matplotlib.lines import Line2D


# Read CSV file and transform it to a pandas dataframe
def read_data(datafile):
    try:
        df = pd.read_table(datafile, sep=",", comment="#")
    except:
        traceback.print_exc()
        print(colored("Error: Reading '{}'".format(datafile), "red"), file=sys.stderr)
        sys.exit(1)
    assert len(df.index) > 0, colored("The datafile '{}' is empty".format(datafile), "red")
    return df


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


#
# Class that describes one plot
#


class Plot:
    kind = "Line/Area/Bars"
    title = ""
    dfs = dict()

    # Target ax to be plotted in
    axnum = None

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

    # Show the legend or not
    legend = True

    # Arguments passed to the legend constructor
    default_legend_options = {"loc": "best"}
    legend_options = {}

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
    xgrid = None
    ygrid = None

    # Limits
    ymin = None # None / Float
    ymax = None # None / Float

    # X/Y major/minor ticks locator. Either ["Locator", {"args": "for",  "the": "locator"}] or "Locator"
    # See http://matplotlib.org/api/ticker_api.html
    ymajorlocator = None
    xmajorlocator = None
    yminorlocator = None # "AutoMinorLocator" should be a good choice
    xminorlocator = None # "AutoMinorLocator" should be a good choice

    ymajorformatter = None
    xmajorformatter = None
    yminorformatter = None
    xminorformatter = None

    # Index column
    index = None # int or list

    colormap = None # Colormap to pick colors from
    numcolors = None
    color = None # Colors to override default style or colors from colormap
    starting_style = 0 # The colors and other propierties are cycled, this allows to pick a different starting style

    # Horizontal lines
    hl = []

    # Vertical lines
    vl = []

    # Ax this is plotted into
    ax = None

    # Put Y scale on the right
    yright = False

    # Tick params, list of dictionaries with the parameters for the call plt.tick_params(...)
    # See https://matplotlib.org/devdocs/api/_as_gen/matplotlib.axes.Axes.tick_params.html
    tick_params = []


    def __init__(self):
        # assert self.cols, colored("You shold provide some cols to plot e.g. --plot '{... cols: [1,2,3], ...}'", "red")
        assert self.index != None, colored("You shold provide an index e.g. --plot '{... index: 0, ...}'", "red")
        assert self.cols == None or self.index not in self.cols, colored("You are trying to plot the index... cols is {} and the index is {}".format(self.cols, self.index), "red")

        # If no cols are specified, we assume all but the index
        if not self.cols:
            self.cols = [i for i in range(len(self.df.columns)) if i != self.index]

        ax = plt.gca()

        # Map col to label
        self.colabel = dict()
        if self.labels:
            assert len(self.labels) == len(self.cols), colored("The number of labels({}) and columns({}) is different".format(len(self.labels), len(self.cols)), 'red')
            for label, col in zip(self.labels, self.cols):
                self.colabel[self.df.columns[col]] = label

        # Store used columns names
        self.columns = [self.df.columns[col] for col in self.cols]

        # Set index
        if not isinstance(self.index, list):
            self.index = [self.index]
        self.df = self.df.set_index([self.df.columns[index] for index in self.index])

        assert not isinstance(self.color, str), colored("Color has to be an iterable of strings, not '{}'".format(self.color), 'red')

        # Use colors from colormap
        if self.colormap:
            ax = plt.gca()
            cmap = plt.get_cmap(self.colormap)
            numcolors = len(self.cols)
            if self.numcolors:
                numcolors = self.numcolors
            norm = mpl.colors.Normalize(vmin=0, vmax=numcolors - 1)
            cmcolor = [cmap(norm(c)) for c in range(numcolors)]
            # Override colors
            color = list(cmcolor)
            if self.color:
                for i, (c1, c2) in enumerate(zip(self.color, cmcolor)):
                    if (c1):
                        if (re.match(r'[dD][0-9]', c1)): # Use d0, d1, d2,... to refer to the colors in the colormap in positional order
                            pos = int(c1[1:])
                            color[i] = cmcolor[pos]
                        else:
                            color[i] = c1
            self.color = color

        # Use default colors, but override them with the colors in self.color
        else:
            default_color = plt.rcParams['axes.prop_cycle'].by_key()['color']
            color = list(default_color)
            if self.color:
                for i, (c1, c2) in enumerate(zip(self.color, default_color)):
                    if (c1):
                        if (re.match(r'[dD][0-9]', c1)): # Use d0, d1, d2,... to refer to default colors in positional order
                            pos = int(c1[1:])
                            color[i] = default_color[pos]
                        else:
                            color[i] = c1
            self.color = color

        # Legend options
        lo = dict(self.default_legend_options)
        merge_dicts(lo, self.legend_options)
        self.legend_options = lo


    def check_and_set(self, kwds):
        for key in kwds:
            assert key in dir(self), colored("'{}' is not a valid keyword for this kind of plot".format(key), "red")
        self.__dict__.update(kwds)


    def prepare_data(self):
        if self.datafile not in Plot.dfs:
            Plot.dfs[self.datafile] = read_data(self.datafile)
        self.df = Plot.dfs[self.datafile]


    # Plot horizontal line
    def plot_hl(self):
        if not self.hl:
            return

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

            if re.match(r'[dD][0-9]', prop["color"]): # Use d0, d1, d2,... to refer to self.color in positional order
                pos = int(prop["color"][1:])
                prop["color"] = self.color[pos]

            x = ax.get_xlim()
            plt.errorbar((x[0], x[1]), (y, y), **prop)


    # Plot vertical line
    def plot_vl(self):
        if not self.vl:
            return

        ax = plt.gca()
        if not isinstance(self.vl, list) or isinstance(self.vl[1], dict):
            self.vl = [self.vl]

        for line in self.vl:
            prop = {"color": "k", "lw" : 1}
            if isinstance(line, (list, tuple)):
                assert(len(line) == 2)
                assert(isinstance(line[1], dict))
                x = float(line[0])
                prop.update(line[1])
            else:
                x = float(line)

            if re.match(r'[dD][0-9]', prop["color"]): # Use d0, d1, d2,... to refer to self.color in positional order
                pos = int(prop["color"][1:])
                prop["color"] = self.color[pos]

            y = ax.get_ylim()
            mid = (y[0] + y[1]) / 2
            mid += mid * random.uniform(-0.05, 0.05)
            plt.errorbar((x, x, x), [y[0], mid, y[1]], **prop)


    def make_style_cycler(self, style_props):
        # Convert all the style propierties into cycle iterators and set them to the correct starting point
        style_cycler = None
        for prop in style_props:
            value = getattr(self, prop)
            if value == None:
                continue
            if not isinstance(value, list):
                value = [value]
            prop_cycler = cycler(prop, value) * (len(self.columns) + self.starting_style)
            if not style_cycler:
                style_cycler = prop_cycler
            else:
                style_cycler += prop_cycler

        for _ in range(self.starting_style):
            next(style_cycler)

        return style_cycler


    def show_legend(self, options):
        ax = plt.gca()
        handles, labels = ax.get_legend_handles_labels()

        # Handle edge color and line width
        hec = options.pop("handleedgecolor", options.pop("hec", None))
        hlw = options.pop("handlelinewidth", options.pop("hlw", None))
        if hec or hlw:
            for h, handle in enumerate(handles):
                if isinstance(handle, Patch):
                    handles[h] = Patch(handle)
                elif isinstance(handle, Line2D):
                    handles[h] = Line2D(handle)
                else:
                    print(colored("Unknown matplotlib class", "red"))
                handles[h].set_edgecolor(hec)
                handles[h].set_linewidth(hlw)

        # Reverse if specified
        if options.pop("reverse", False):
            handles = handles[::-1]
            labels = labels[::-1]

        ax.legend(handles, labels, **options)


    def plot(self):
        assert self.plotted == False, colored("This plot has been already plotted!", "red")

        # Mark this plot as plotted
        self.plotted = True

        ax = plt.gca()
        self.ax = ax

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
                if isinstance(locator, (list, tuple)):
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

        # X/Y tick formatters
        for setter, formatter in [(ax.xaxis.set_major_formatter, self.xmajorformatter), (ax.yaxis.set_major_formatter, self.ymajorformatter), (ax.xaxis.set_minor_formatter, self.xminorformatter), (ax.yaxis.set_minor_formatter, self.yminorformatter)]:
            if formatter:
                if isinstance(formatter, (list, tuple)):
                    assert(len(formatter) == 2)
                    form = formatter[0]
                    args = formatter[1]
                    assert isinstance(form, str)
                    assert isinstance(args, dict)
                else:
                    form = formatter
                    args = {}
                constr = getattr(ticker, form) # Constructor for the formatter

                # Workaround to the fact that the ScalarFormatter constructor does not accept scilimits
                if form == "ScalarFormatter":
                    scilimits = None
                    if "scilimits" in args:
                        scilimits = args["scilimits"]
                        assert isinstance(scilimits, (list, tuple))
                        assert len(scilimits) == 2
                        del args["scilimits"]
                    obj = constr(**args)
                    obj.set_powerlimits(scilimits)
                    setter(obj)
                # Normal formatter
                else:
                    setter(constr(**args))

        # Percentage
        if self.ypercent:
            ax.yaxis.set_major_formatter(PercentFormatter)

        # X tick rotation and horizontal alingment
        if self.xrot != None:
            plt.xticks(rotation=self.xrot, horizontalalignment=self.xtick_ha)

        # Grid
        if self.xgrid != None:
            ax.set_axisbelow(True)
            if self.xgrid == True:
                self.xgrid = {}
            ax.xaxis.grid(**self.xgrid)
        if self.ygrid != None:
            ax.set_axisbelow(True)
            if self.ygrid == True:
                self.ygrid = {}
            ax.yaxis.grid(**self.ygrid)

        # Legend
        if self.legend:
            self.show_legend(self.legend_options)

        for tp in self.tick_params:
            plt.tick_params(**tp)


class BoxPlot(Plot):
    kind = "box"
    xrot = 45

    def __init__(self, **kwds):
        self.check_and_set(kwds)
        self.prepare_data()
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

    hatch = [" "] #('', '\\', 'x', '/', '.', '-', '|', '*', 'o', '+', 'O')

    width = 1

    def __init__(self, **kwds):
        self.check_and_set(kwds)
        self.prepare_data()

        # Store used error column names
        self.ecolumns = [self.df.columns[ecol] for ecol in self.ecols]

        super().__init__()

        assert not self.ecols or len(self.cols) == len(self.ecols) or 2 * len(self.cols) == len(self.ecols),\
                colored("You have {} cols but {} error cols: error cols shold be 0, equal or double the number of cols".format(len(self.cols), len(self.ecols)), "red")


    def plot_bars(self):
        def compute_bar_locations(df, width, bar_num):
            def sep(width):
                return width * 0.5

            block_size = width * len(df.columns) + sep(width) # Size of a group of bars + the space to the right
            indexes = np.array(range(len(df)))
            indexes = indexes * block_size
            indexes = indexes + (width * bar_num) # bar_num 0, correstponds to the first column, 1 to the second, etc.
            return indexes

        style_cycler = self.make_style_cycler(["color", "hatch"])

        ax = plt.gca()
        values = self.df[self.columns]

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
        else:
            errors = it.cycle([None])

        for c, (col, ecol, sty) in enumerate(zip(values.columns, errors, style_cycler)):
            ind = compute_bar_locations(values, self.width, c)
            bars = plt.bar(ind, values[col], self.width, label=self.colabel.get(col, col), yerr=ecol, **sty)

        ind = compute_bar_locations(values, self.width, len(values.columns) / 2 - 0.5) # Positions of the xticks
        ax.set_xticks(ind)
        ax.set_xticklabels(values.index.values)


    def plot_stacked_bars(self):
        def compute_bar_locations(df, width):
            def sep(width):
                return width * 0.5

            block_size = width + sep(width) # Size of a group of bars + the space to the right
            indexes = np.array(range(len(df)))
            indexes = indexes * block_size
            indexes = indexes + width / 2
            return indexes

        style_cycler = self.make_style_cycler(["color", "hatch"])

        ax = plt.gca()
        values = self.df[self.columns]
        values = values.cumsum(axis=1) # To make them "stacked"

        ind = compute_bar_locations(values, self.width)

        # To be able to reverse the styles
        styles = []
        for s, sty in enumerate(style_cycler):
            if s == len(values.columns):
                break
            styles.append(sty)

        for col, sty in zip(reversed(values.columns), reversed(styles)):
            bars = plt.bar(ind, values[col], self.width, label=self.colabel.get(col, col), **sty)

        ax.set_xticks(ind)
        ax.set_xticklabels(values.index.values)


    def plot_multiindexed_bars(self):
        def compute_bar_locations(df, width):
            def sep(width, level):
                return width * (1.75 * level + 0.5)
            result = []
            all_values = []
            for l, level in enumerate(reversed(df.index.labels)):
                values = []
                prev = level[0]
                for e in level:
                    if e != prev:
                        values.append(sep(width, l))
                    else:
                        values.append(0)
                    prev = e
                all_values.append(np.array(values))
                result.append(np.cumsum(values))
            result = np.array(result)
            indexes = np.sum(result, axis=0)
            for i in range(len(indexes)):
               indexes[i] += width * i
            return indexes

        def xtick_loc_per_level(df, level, bar_positions):
            indexes = bar_positions
            canvis = [-1] + list(np.where(np.diff(df.index.labels[level]) != 0)[0]) + [len(indexes) - 1]
            locations = []
            for i in range(len(canvis) - 1):
                act = canvis[i]
                seg = canvis[i + 1]
                start = indexes[act + 1]
                end = indexes[seg]
                locations.append((start + end) / 2)
            return locations

        ax = plt.gca()
        ind = compute_bar_locations(self.df, self.width)
        values = self.df[self.columns]
        values = values.cumsum(axis=1) # To make them "stacked"

        style_cycler = self.make_style_cycler(["color", "hatch"])
        # To be able to reverse the styles
        styles = []
        for s, sty in enumerate(style_cycler):
            if s == len(values.columns):
                break
            styles.append(sty)

        for col, sty in zip(reversed(values.columns), reversed(styles)):
            bars = plt.bar(ind, values[col], self.width, label=self.colabel.get(col, col), **sty)

        assert(len(values.index.levels) <= 2)
        ax.set_xticks(xtick_loc_per_level(values, 0, ind), minor=True)
        ax.set_xticks(xtick_loc_per_level(values, 1, ind))

        idx = values.index

        changes = [0] + list(np.where(np.diff(values.index.labels[0]) != 0)[0] + 1)
        ax.set_xticklabels([idx.levels[0][idx.labels[0][l]] for l in changes], minor=True)

        changes = [0] + list(np.where(np.diff(values.index.labels[1]) != 0)[0] + 1)
        ax.set_xticklabels([idx.levels[1][idx.labels[1][l]] for l in changes])

        ax.tick_params(which='minor', pad=20, length=0)


    def plot(self):
        if self.kind in ["sb", "stackedbars", "sbars"]:
            self.plot_stacked_bars()
        elif self.kind == "mibars":
            self.plot_multiindexed_bars()
        else:
            self.plot_bars()
        super().plot()


class LinePlot(Plot):
    kind = "line"

    linewidth = None
    elinewidth = 1
    linestyle = None
    marker = None
    markersize = 6
    markevery = 1
    markeredgecolor = 'k'
    markeredgewidth = 0.5

    # Limits
    xmin = None # None / Float
    xmax = None # None / Float

    # Columns to use for errorbars
    ecols = [] # List of ints

    def __init__(self, **kwds):
        self.check_and_set(kwds)
        self.prepare_data()

        self.ecolumns = [self.df.columns[ecol] for ecol in self.ecols]

        super().__init__()

        assert not self.ecols or len(self.cols) == len(self.ecols), \
                colored("You have {} cols but {} error cols: error cols shold be 0, equal or double the number of cols".format(len(self.cols), len(self.ecols)), "red")


    def plot_area(self, stacked=False):
        # Plot
        ax = self.ax
        columns = self.columns
        lw = 0
        if self.linewidth:
            lw = self.linewidth

        y = [self.df[col].values for col in columns]
        x = self.df.index.values
        labels = [self.colabel.get(col, col) for col in columns]

        if stacked:
            ax.stackplot(x, *y, colors=self.color, linewidth=lw, labels=labels)
        else:
            style_cycler = self.make_style_cycler(["color", "linewidth", "linestyle",])
            for label, values, sty in zip(labels, y, style_cycler):
                ax.fill_between(x, values, alpha=0.5, label=label, **sty)


    def plot_line(self):
        ax = self.ax
        columns = self.columns
        ecolumns = self.ecolumns
        if not ecolumns:
            ecolumns = [None] * len(columns)

        style_props = ["color", "linewidth", "linestyle", "marker", "markersize", "markevery", "markeredgecolor", "markeredgewidth", "elinewidth"]
        style_cycler = self.make_style_cycler(style_props)


        for column, ecolumn, sty in zip(columns, ecolumns, style_cycler):
            if ecolumn:
                data = self.df[[column, ecolumn]]
            else:
                data = self.df[column]

            data = data.dropna()
            x = data.index.values

            if ecolumn:
                yerr = data[ecolumn].tolist()
                y = data[column].tolist()
            else:
                yerr = None
                y = data.tolist()

            plt.errorbar(x, y, yerr=yerr, label=self.colabel.get(column, column), axes=ax, **sty)


    def plot(self):
        # Put Y axis on the right
        ax = plt.gca()
        self.ax = ax

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
                    self.linestyle = ['-', '--', '-.', ':']

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
