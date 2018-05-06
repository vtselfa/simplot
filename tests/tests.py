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
    figs, axes, axes_r = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, axes_r, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]


@image_comparison(baseline_images=['t2'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_lineplot_with_title():
    args =  " --plot '{kind: l, index: 0, cols: [1,2,3,4], datafile: data/stp.csv, ylabel: Ylabel, xlabel: Xlabel, labels: [Y1, Y2, Y3, Y4]}'"
    args += " --size 4 2.5 --dpi 100 --title 'Super nice title'"

    args = simplot.parse_args(shlex.split(args))
    figs, axes, axes_r = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, axes_r, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]


@image_comparison(baseline_images=['t3'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_lineplot_with_title2():
    args =  " --plot '{kind: l, index: 0, cols: [1,2], datafile: data/stp.csv, ylabel: Ylabel, xlabel: Xlabel, labels: [Y1, Y2]}'"
    args += " --plot '{kind: l, index: 0, cols: [3,4], datafile: data/stp.csv, ylabel: Ylabel, xlabel: Xlabel, labels: [Y3, Y4]}'"
    args += " -g 1 2 --size 4 2.5 --dpi 100 --title 'Super nice title'"

    args = simplot.parse_args(shlex.split(args))
    figs, axes, axes_r = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, axes_r, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]


@image_comparison(baseline_images=['t4'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_lineplot_manual_axis():
    args =  " --plot '{kind: l, index: 0, cols: [1,2], datafile: data/stp.csv, ylabel: Ylabel, xlabel: Xlabel, labels: [Y1, Y2]}'"
    args += " --plot '{axnum: 0, color: [d2, d3], kind: l, index: 0, cols: [3,4], datafile: data/stp.csv, ylabel: Ylabel, xlabel: Xlabel, labels: [Y3, Y4]}'"
    args += " --plot '{kind: l, index: 0, cols: [1,2,3,4], datafile: data/stp.csv, ylabel: Ylabel, xlabel: Xlabel, labels: [Y1, Y2, Y3, Y4]}'"
    args += " -g 1 2 --size 4 2.5 --dpi 100 --title 'Super nice title'"

    args = simplot.parse_args(shlex.split(args))
    figs, axes, axes_r = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, axes_r, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]


@image_comparison(baseline_images=['t5'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_area():
    args =  " --plot '{kind: area, datafile: data/cos.csv, index: 0, xlabel: Seconds, ylabel: Ways, colormap: magma_r, legend_options: {loc: 4, frameon: False, ncol: 1}}'"
    args += " --size 4 2.5 --dpi 100"

    args = simplot.parse_args(shlex.split(args))
    figs, axes, axes_r = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, axes_r, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]


@image_comparison(baseline_images=['t5'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_area():
    args =  " --plot '{kind: area, datafile: data/cos.csv, index: 0, xlabel: Seconds, ylabel: Ways, colormap: magma_r, legend_options: {loc: 4, frameon: False, ncol: 1}}'"
    args += " --size 4 2.5 --dpi 100"

    args = simplot.parse_args(shlex.split(args))
    figs, axes, axes_r = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, axes_r, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]


@image_comparison(baseline_images=['stacked_bars'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_stacked_bars():
    args = """ --plot '{kind: sb, datafile: data/prog_vs_ways.csv, index: 0, xlabel: Applications, ylabel: Progress, ymin: 0.6, ymax: 1, hatch: ["///", "", "", "", "", "...", ""], colormap: cubehelix, color: ["#ffffff"], legend_options: {loc: 1, frameon: False, ncol: 1, bbox_to_anchor: [1.09, 1.], title: Ways}, xrot: 90}' --size 10 6 --rect 0 0 0.997 1"""

    args = simplot.parse_args(shlex.split(args))
    figs, axes, axes_r = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, axes_r, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]


@image_comparison(baseline_images=['t7'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_scatter():
    args =  """ --plot '{markeredgewidth: 0, markersize: 4, color: ["#d490c6"], kind: ml, datafile: data/stalls_slowdown_correlation.csv, index: 4, cols: [5], linewidth: 0, marker: ["X"]}'"""
    args += """ --plot '{axnum: 0, markeredgewidth: 0, markersize: 4, color: ["#2b6f39"], kind: ml, datafile: data/stalls_slowdown_correlation.csv, index: 2, cols: [3], linewidth: 0, marker: ["v"]}'"""
    args += """ --plot '{axnum: 0, markeredgewidth: 0, color: [k], kind: ml, datafile: data/stalls_slowdown_correlation.csv, index: 0, cols: [1], linewidth: 0, marker: ["s"], markersize: 3, ylabel: Slowdown, xlabel: "Exec stall cycles due L2 misses", legend_options: {loc: 2, frameon: False, ncol: 1, markerscale: 1.5}, xmin: 0, ymin: 0, ymax: 12.2, xmax: 1.2e+12}' --size 8 5"""

    args = simplot.parse_args(shlex.split(args))
    figs, axes, axes_r = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, axes_r, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]


@image_comparison(baseline_images=['bars_with_max_error'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_bars_with_maxerror():
    args = """ --plot '{kind: b, datafile: data/progress_estimation.csv, index: 0, cols: [1,2], ecols: [3,4], errorbars: max, labels: [ASM,PTCA], ylabel: "Progress Estimation Error", legend_options: {loc: 9, frameon: False, ncol: 2}, xlabel: Number of applications, xrot: 0, ymax: 0.25, ypercent: True, hatch: [" ", "//"]}' --size 4 2.5"""
    args = simplot.parse_args(shlex.split(args))
    figs, axes, axes_r = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, axes_r, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]


@image_comparison(baseline_images=['t9'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_equalize_xy1():
    args =  " --plot '{kind: l, index: 0, cols: [1], datafile: data/A.csv, ylabel: Ylabel, xlabel: Xlabel, labels: [Y]}'"
    args += " --plot '{kind: l, index: 0, cols: [1], xmax: 35, datafile: data/a.csv, ylabel: Ylabel, xlabel: Xlabel, labels: [Y cutted]}'"
    args += " -g 1 2 --size 4 2.5 --dpi 100 --equal-xaxes 0 1 --equal-yaxes 0 1 "

    args = simplot.parse_args(shlex.split(args))
    figs, axes, axes_r = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, axes_r, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]


@image_comparison(baseline_images=['t10'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_equalize_xy2():
    args =  " --plot '{kind: l, index: 0, cols: [1], datafile: data/A.csv, ylabel: Ylabel, xlabel: Xlabel, labels: [Y]}'"
    args += " --plot '{kind: l, index: 0, cols: [1], datafile: data/a.csv, ylabel: Ylabel, xlabel: Xlabel, labels: [Y cutted]}'"
    args += " -g 1 2 --size 4 2.5 --dpi 100 --equal-xaxes 0 1 --equal-yaxes 0 1 "

    args = simplot.parse_args(shlex.split(args))
    figs, axes, axes_r = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, axes_r, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]


@image_comparison(baseline_images=['t11'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_vh_lines():
    args = """--plot '{kind: l, index: 0, cols: [1], datafile: data/A.csv, ylabel: Ylabel, xlabel: Xlabel, labels: [Y1], hl: [3.2, 3.4]}' --plot '{kind: l, index: 0, cols: [1], datafile: data/a.csv, hl: [[4, {lw: 2, ls: ":", color: "r"}], [3.4, {lw: 0.5, ls: "--", color: "g"}]], vl: 2, ylabel: Ylabel, xlabel: Xlabel, labels: [Y1 cutted]}' -g 1 2 --size 4 2.5 --dpi 100 --equal-xaxes 0 1  --equal-yaxes 0 1"""

    args = simplot.parse_args(shlex.split(args))
    figs, axes, axes_r = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, axes_r, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]

@image_comparison(baseline_images=['line_with_errorbars'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_vh_lines():
    args = """--plot '{kind: l, index: 0, cols: [1], ecols: [2], datafile: data/err.csv, ylabel: Ylabel, xlabel: Xlabel, labels: [Y1], ymax: 5}' --size 4 2.5 --dpi 100 --title 'Super nice title' """

    args = simplot.parse_args(shlex.split(args))
    figs, axes, axes_r = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, axes_r, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]


@image_comparison(baseline_images=['line_yright'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_lineplot_yright():
    args =  " --plot '{kind: l, index: 0, colormap: cubehelix, numcolors: 3, color: [D1], cols: [1], datafile: data/stp.csv, ylabel: Hello from the left, xlabel: Xlabel, labels: [Yleft]}'"
    args += """ --plot '{axnum: 0, colormap: cubehelix, numcolors: 3, color: [D2], yright: True, kind: dl, linestyle: ":", index: 0, cols: [2], datafile: data/stp.csv, ylabel: Hello from the right, xlabel: Xlabel, labels: [Yright], legend_options: {loc: 4}}'"""
    args += " --plot '{kind: l, index: 0, cols: [3], datafile: data/stp.csv, ylabel: Ylabel, xlabel: Xlabel, labels: [Y3]}'"
    args += " -g 1 2 --size 4 2.5 --dpi 100 --title 'Super nice title'"

    args = simplot.parse_args(shlex.split(args))
    figs, axes, axes_r = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, axes_r, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]


@image_comparison(baseline_images=['line_yright2'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_lineplot_yright2():
    args = """ --plot '{yright: True, kind: dl, linestyle: ":", index: 0, cols: [2], datafile: data/stp.csv, ylabel: Hello from the right, xlabel: Xlabel, labels: [Y2], legend_options: {loc: 4}}'"""
    args += " --plot '{kind: l, index: 0, cols: [3], datafile: data/stp.csv, ylabel: Ylabel, xlabel: Xlabel, labels: [Y3]}'"
    args += " -g 1 2 --size 4 2.5 --dpi 100 --title 'Super nice title'"

    args = simplot.parse_args(shlex.split(args))
    figs, axes, axes_r = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, axes_r, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]


@image_comparison(baseline_images=['line_yright3'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_lineplot_yright3():
    args =  " --plot '{kind: l, yright: True, index: 0, cols: [1], datafile: data/stp.csv, ylabel: Hello from the right, xlabel: Xlabel, labels: [Yright]}'"
    args += """ --plot '{axnum: 0, kind: dl, color: ['C1'], linestyle: ":", index: 0, cols: [2], datafile: data/stp.csv, ylabel: Hello from the left, xlabel: Xlabel, labels: [Yleft], legend_options: {loc: 4}}'"""
    args += " --plot '{kind: l, index: 0, cols: [3], datafile: data/stp.csv, ylabel: Ylabel, xlabel: Xlabel, labels: [Y3]}'"
    args += " -g 1 2 --size 4 2.5 --dpi 100 --title 'Super nice title'"

    args = simplot.parse_args(shlex.split(args))
    figs, axes, axes_r = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, axes_r, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]


@image_comparison(baseline_images=['line_yright_alone'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_lineplot_yright3():
    args =  " --plot '{kind: l, yright: True, index: 0, cols: [1], datafile: data/stp.csv, ylabel: Hello from the right, xlabel: Xlabel, labels: [Yright]}'"
    args += " -g 1 1 --size 4 2.5 --dpi 100 --title 'Super nice title'"

    args = simplot.parse_args(shlex.split(args))
    figs, axes, axes_r = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, axes_r, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]


@image_comparison(baseline_images=['test_line_yright_equalize_yaxis'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_line_yright_equalize_yaxis():
    args =  " --plot '{kind: l, yright: True, index: 0, cols: [2], datafile: data/stp.csv, ylabel: Hello from the left, xlabel: Xlabel, labels: [Y1]}'"
    args += """ --plot '{axnum: 0, kind: dl, linestyle: ":", color: ['C1'], index: 0, cols: [1], datafile: data/a.csv, ylabel: Hello from the right, xlabel: Xlabel, labels: [Y2], legend_options: {loc: 4}}'"""
    args += " --plot '{kind: l, index: 0, cols: [3], datafile: data/stp.csv, ylabel: Ylabel, xlabel: Xlabel, labels: [Y3]}'"
    args += " -g 1 2 --size 4 2.5 --dpi 100 --title 'Super nice title' --equal-yaxes 0 1 2"

    args = simplot.parse_args(shlex.split(args))
    figs, axes, axes_r = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, axes_r, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]


@image_comparison(baseline_images=['test_hl_colors'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_line_yright_equalize_yaxis():
    args =  " --plot '{kind: l, index: 0, cols: [1, 2, 3], datafile: data/olines.csv, ylabel: Some lines, xlabel: X label, labels: [A1, A2, A3], hl: [[1, {color: d0}], [2, {color: d1}], [3, {color: d2}]]}'"
    args += " --plot '{ymin: 0, axnum: 0, kind: l, color: [d3, d4, d5], index: 0, cols: [4, 5, 6], datafile: data/olines.csv, labels: [B1, B2, B3], hl: [[4, {color: d3}], [5, {color: d4}], [6, {color: d5}]]}'"
    args += " -g 1 1 --size 4 2.5 --dpi 100 --title 'Super nice title'"

    args = simplot.parse_args(shlex.split(args))
    figs, axes, axes_r = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, axes_r, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]


@image_comparison(baseline_images=['test_multiindexed_bars'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_multiindexed_bars():
    args = """ --plot '{kind: mibars, datafile: data/multiindexed_bars.csv, index: [0, 2], cols: [3], ylabel: "Progress Estimation Error", xlabel: X Label}' --size 4 2.5 --dpi 100"""
    args = simplot.parse_args(shlex.split(args))
    figs, axes, axes_r = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, axes_r, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]


@image_comparison(baseline_images=['test_stacked_multiindexed_bars'], extensions=['pdf'], savefig_kwarg=dict(pad_inches = 0))
def test_stacked_multiindexed_bars():
    args = """ --plot '{kind: mibars, datafile: data/multiindexed_bars.csv, index: [0, 2], cols: [3, 4], ylabel: "Progress Estimation Error", xlabel: X Label}' --size 4 2.5 --dpi 100"""
    args = simplot.parse_args(shlex.split(args))
    figs, axes, axes_r = simplot.create_figures(args.grid, args.size, args.dpi)
    simplot.plot_data(figs, axes, axes_r, args.plot, args.title, args.equal_xaxes, args.equal_yaxes, args.rect)
    fig = figs[0]
