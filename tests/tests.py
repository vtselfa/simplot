import simplot

import matplotlib as mpl
import matplotlib.pyplot as plt
import shlex
from matplotlib.testing.decorators import image_comparison


@image_comparison(baseline_images=['t1'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_lineplot():
    args =  " --plot '{kind: l, index: 0, cols: [1,2,3,4], datafile: data/stp.csv, ylabel: Ylabel, xlabel: Xlabel, labels: [Y1, Y2, Y3, Y4]}'"
    args += " --size 4 2.5 --dpi 100"

    args = simplot.parse_args(shlex.split(args))
    figs, axes = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]


@image_comparison(baseline_images=['t2'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_lineplot_with_title():
    args =  " --plot '{kind: l, index: 0, cols: [1,2,3,4], datafile: data/stp.csv, ylabel: Ylabel, xlabel: Xlabel, labels: [Y1, Y2, Y3, Y4]}'"
    args += " --size 4 2.5 --dpi 100 --title 'Super nice title'"

    args = simplot.parse_args(shlex.split(args))
    figs, axes = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]


@image_comparison(baseline_images=['t3'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_lineplot_with_title2():
    args =  " --plot '{kind: l, index: 0, cols: [1,2], datafile: data/stp.csv, ylabel: Ylabel, xlabel: Xlabel, labels: [Y1, Y2]}'"
    args += " --plot '{kind: l, index: 0, cols: [3,4], datafile: data/stp.csv, ylabel: Ylabel, xlabel: Xlabel, labels: [Y3, Y4]}'"
    args += " -g 1 2 --size 4 2.5 --dpi 100 --title 'Super nice title'"

    args = simplot.parse_args(shlex.split(args))
    figs, axes = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]


@image_comparison(baseline_images=['t4'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_lineplot_manual_axis():
    args =  " --plot '{kind: l, index: 0, cols: [1,2], datafile: data/stp.csv, ylabel: Ylabel, xlabel: Xlabel, labels: [Y1, Y2]}'"
    args += " --plot '{axnum: 0, kind: l, index: 0, cols: [3,4], datafile: data/stp.csv, ylabel: Ylabel, xlabel: Xlabel, labels: [Y3, Y4]}'"
    args += " --plot '{kind: l, index: 0, cols: [1,2,3,4], datafile: data/stp.csv, ylabel: Ylabel, xlabel: Xlabel, labels: [Y1, Y2, Y3, Y4]}'"
    args += " -g 1 2 --size 4 2.5 --dpi 100 --title 'Super nice title'"

    args = simplot.parse_args(shlex.split(args))
    figs, axes = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]


@image_comparison(baseline_images=['t5'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_area():
    args =  " --plot '{kind: area, datafile: data/cos.csv, index: 0, xlabel: Seconds, ylabel: Ways, colormap: magma_r, legend_options: {loc: 4, frameon: False, ncol: 1}}'"
    args += " --size 4 2.5 --dpi 100"

    args = simplot.parse_args(shlex.split(args))
    figs, axes = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]


@image_comparison(baseline_images=['t5'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_area():
    args =  " --plot '{kind: area, datafile: data/cos.csv, index: 0, xlabel: Seconds, ylabel: Ways, colormap: magma_r, legend_options: {loc: 4, frameon: False, ncol: 1}}'"
    args += " --size 4 2.5 --dpi 100"

    args = simplot.parse_args(shlex.split(args))
    figs, axes = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]


@image_comparison(baseline_images=['t6'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_stacked_bars():
    args = """ --plot '{kind: sb, datafile: data/prog_vs_ways.csv, index: 0, xlabel: Applications, ylabel: Progress, ymin: 0.6, ymax: 1, hatches: ["///", "", "", "", "%%%"], colormap: cubehelix, color: ["#ffffff"], legend_options: {loc: 1, frameon: False, ncol: 1, bbox_to_anchor: [1.09, 1.], title: Ways}}' --size 10 6 --rect 0 0 0.937 1"""

    args = simplot.parse_args(shlex.split(args))
    figs, axes = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]


@image_comparison(baseline_images=['t7'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_scatter():
    args =  """ --plot '{markeredgewidth: 0, markersize: 4, color: ["#d490c6"], kind: ml, datafile: data/stalls_slowdown_correlation.csv, index: 4, cols: [5], linewidth: 0, marker: ["X"]}'"""
    args += """ --plot '{axnum: 0, markeredgewidth: 0, markersize: 4, color: ["#2b6f39"], kind: ml, datafile: data/stalls_slowdown_correlation.csv, index: 2, cols: [3], linewidth: 0, marker: ["v"]}'"""
    args += """ --plot '{axnum: 0, markeredgewidth: 0, color: [k], kind: ml, datafile: data/stalls_slowdown_correlation.csv, index: 0, cols: [1], linewidth: 0, marker: ["s"], markersize: 3, ylabel: Slowdown, xlabel: "Exec stall cycles due L2 misses", legend_options: {loc: 2, frameon: False, ncol: 1, markerscale: 1.5}, xmin: 0, ymin: 0, ymax: 12.2, xmax: 1.2e+12}' --size 8 5"""

    args = simplot.parse_args(shlex.split(args))
    figs, axes = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]


@image_comparison(baseline_images=['t8'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_bars_with_maxerror():
    args = """ --plot '{kind: b, datafile: data/progress_estimation.csv, index: 0, cols: [1,2], ecols: [3,4], errorbars: max, labels: [ASM,PTCA], ylabel: "Progress Estimation Error", legend_options: {loc: 9, frameon: False, ncol: 2}, xlabel: Number of applications, xrot: 0, ymax: 0.25, ypercent: True}' --size 4 2.5 --dpi 100"""
    args = simplot.parse_args(shlex.split(args))
    figs, axes = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]


@image_comparison(baseline_images=['t9'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_equalize_xy1():
    args =  " --plot '{kind: l, index: 0, cols: [1], datafile: data/A.csv, ylabel: Ylabel, xlabel: Xlabel, labels: [Y]}'"
    args += " --plot '{kind: l, index: 0, cols: [1], xmax: 35, datafile: data/a.csv, ylabel: Ylabel, xlabel: Xlabel, labels: [Y cutted]}'"
    args += " -g 1 2 --size 4 2.5 --dpi 100 --equal-xaxes 0 1 --equal-yaxes 0 1 "

    args = simplot.parse_args(shlex.split(args))
    figs, axes = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]


@image_comparison(baseline_images=['t10'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_equalize_xy2():
    args =  " --plot '{kind: l, index: 0, cols: [1], datafile: data/A.csv, ylabel: Ylabel, xlabel: Xlabel, labels: [Y]}'"
    args += " --plot '{kind: l, index: 0, cols: [1], datafile: data/a.csv, ylabel: Ylabel, xlabel: Xlabel, labels: [Y cutted]}'"
    args += " -g 1 2 --size 4 2.5 --dpi 100 --equal-xaxes 0 1 --equal-yaxes 0 1 "

    args = simplot.parse_args(shlex.split(args))
    figs, axes = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]
