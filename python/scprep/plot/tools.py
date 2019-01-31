import numpy as np
try:
    import matplotlib as mpl
    import matplotlib.pyplot as plt
except ImportError:
    pass

from .utils import _with_matplotlib, _get_figure


@_with_matplotlib
def create_colormap(colors, name="scprep_custom_cmap"):
    """Create a custom colormap from a list of colors

    Parameters
    ----------
    colors : list-like
        List of `matplotlib` colors. Includes RGB, RGBA,
        string color names and more.
        See <https://matplotlib.org/api/colors_api.html>

    Returns
    -------
    cmap : `matplotlib.colors.LinearSegmentedColormap`
        Custom colormap
    """
    if len(colors) == 1:
        colors = np.repeat(colors, 2)
    vals = np.linspace(0, 1, len(colors))
    cdict = dict(red=[], green=[], blue=[], alpha=[])
    for val, color in zip(vals, colors):
        r, g, b, a = mpl.colors.to_rgba(color)
        cdict['red'].append((val, r, r))
        cdict['green'].append((val, g, g))
        cdict['blue'].append((val, b, b))
        cdict['alpha'].append((val, a, a))
    cmap = mpl.colors.LinearSegmentedColormap(name, cdict)
    return cmap


@_with_matplotlib
def create_normalize(vmin, vmax, scale="linear"):
    """Create a colormap normalizer

    Parameters
    ----------
    scale : {'linear', 'log', 'symlog', 'sqrt'} or `matplotlib.colors.Normalize`, optional (default: 'linear')
        Colormap normalization scale. For advanced use, see
        <https://matplotlib.org/users/colormapnorms.html>

    Returns
    -------
    norm : `matplotlib.colors.Normalize`
    """
    if scale == 'linear':
        norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    elif scale == 'log':
        if vmin <= 0:
            raise ValueError(
                "`vmin` must be positive for `cmap_scale='log'`. Got {}".format(vmin))
        norm = mpl.colors.LogNorm(vmin=vmin, vmax=vmin)
    elif scale == 'symlog':
        norm = mpl.colors.SymLogNorm(linthresh=0.03, linscale=0.03,
                                     vmin=vmin, vmax=vmax)
    elif scale == 'sqrt':
        norm = mpl.colors.PowerNorm(gamma=1. / 2.)
    elif isinstance(scale, mpl.colors.Normalize):
        norm = scale
    else:
        raise ValueError("Expected norm in ['linear', 'log', 'symlog',"
                         "'sqrt'] or a matplotlib.colors.Normalize object."
                         " Got {}".format(scale))
    return norm


@_with_matplotlib
def generate_legend(cmap, ax, title=None, marker='o', markersize=10,
                    loc='best', bbox_to_anchor=None,
                    fontsize=14, title_fontsize=14,
                    max_rows=10, ncol=None, **kwargs):
    """Generate a legend on an axis.

    Parameters
    ----------
    cmap : dict
        Dictionary of label-color pairs.
    ax : `matplotlib.axes.Axes`
        Axis on which to draw the legend
    title : str, optional (default: None)
        Title to display alongside colorbar
    marker : str, optional (default: 'o')
        `matplotlib` marker to use for legend points
    markersize : float, optional (default: 10)
        Size of legend points
    loc : int or string or pair of floats, default: 'best'
        Matplotlib legend location.
        See <https://matplotlib.org/api/_as_gen/matplotlib.pyplot.legend.html>
        for details.
    bbox_to_anchor : `BboxBase`, 2-tuple, or 4-tuple
        Box that is used to position the legend in conjunction with loc.
        See <https://matplotlib.org/api/_as_gen/matplotlib.pyplot.legend.html>
        for details.
    fontsize : int, optional (default: 14)
        Font size for legend labels
    title_fontsize : int, optional (default: 14)
        Font size for legend title
    max_rows : int, optional (default: 10)
        Maximum number of labels in a column before overflowing to
        multi-column legend
    ncol : int, optional (default: None)
        Number of legend columns. Overrides `max_rows`.
    kwargs : additional arguments for `plt.legend`

    Returns
    -------
    legend : `matplotlib.legend.Legend`
    """
    handles = [mpl.lines.Line2D([], [], marker=marker, color=color,
                                linewidth=0, label=label,
                                markersize=markersize)
               for label, color in cmap.items()]
    if ncol is None:
        ncol = max(1, len(cmap) // max_rows)
    legend = ax.legend(handles=handles, title=title,
                       loc=loc, bbox_to_anchor=bbox_to_anchor,
                       fontsize=fontsize, ncol=ncol, **kwargs)
    plt.setp(legend.get_title(), fontsize=title_fontsize)
    return legend


@_with_matplotlib
def generate_colorbar(cmap, vmin=None, vmax=None, scale='linear', ax=None,
                      title=None, title_fontsize=12, title_rotation=270,
                      **kwargs):
    """Generate a colorbar on an axis.

    Parameters
    ----------
    cmap : `matplotlib` colormap or str
        Colormap with which to draw colorbar
    scale : {'linear', 'log', 'symlog', 'sqrt'} or `matplotlib.colors.Normalize`, optional (default: 'linear')
        Colormap normalization scale. For advanced use, see
        <https://matplotlib.org/users/colormapnorms.html>
    vmin, vmax : float, optional (default: None)
        Range of values to display on colorbar
    ax : `matplotlib.axes.Axes`, list or None, optional (default: None)
        Axis or list of axes from which to steal space for colorbar
        If `None`, uses the current axis
    title : str, optional (default: None)
        Title to display alongside colorbar
    title_fontsize : int, optional (default: 14)
        Font size for colorbar title
    title_rotation : int, optional (default: 270)
        Angle of rotation of the colorbar title
    kwargs : additional arguments for `plt.colorbar`

    Returns
    -------
    colorbar : `matplotlib.colorbar.Colorbar`
    """
    try:
        plot_axis = ax[0]
    except TypeError:
        # not a list
        plot_axis = ax
    if vmax is None and vmin is None:
        vmax = 1
        vmin = 0
        remove_ticks = True
        norm = None
    elif vmax is None or vmin is None:
        raise ValueError("Either both or neither of `vmax` and `vmin` should "
                         "be set. Got `vmax={}, vmin={}`".format(vmax, vmin))
    else:
        remove_ticks = False
        norm = create_normalize(vmin, vmax, scale=scale)
    fig, plot_axis, _ = _get_figure(plot_axis)
    if ax is None:
        ax = plot_axis
    xmin, xmax = plot_axis.get_xlim()
    ymin, ymax = plot_axis.get_ylim()
    im = plot_axis.imshow(np.linspace(vmin, vmax, 10).reshape(-1, 1),
                          vmin=vmin, vmax=vmax, cmap=cmap, norm=norm,
                          aspect='auto', origin='lower',
                          extent=[xmin, xmax, ymin, ymax])
    im.remove()
    colorbar = fig.colorbar(im, ax=ax, **kwargs)
    if title is not None:
        colorbar.set_label(title, rotation=title_rotation,
                           fontsize=title_fontsize)
    if remove_ticks:
        colorbar.set_ticks([])
    return colorbar


def label_axis(axis, ticks=True, ticklabels=True, label=None):
    """Set axis ticks and labels

    Parameters
    ----------
    axis : matplotlib.axis.{X,Y}Axis, mpl_toolkits.mplot3d.axis3d.{X,Y,Z}Axis
        Axis on which to draw labels and ticks
    ticks : True, False, or list-like (default: True)
        If True, keeps default axis ticks.
        If False, removes axis ticks.
        If a list, sets custom axis ticks
    ticklabels : True, False, or list-like (default: True)
        If True, keeps default axis tick labels.
        If False, removes axis tick labels.
        If a list, sets custom axis tick labels
    label : str or None (default : None)
        Axis labels. If None, no label is set.
    """
    if not ticks:
        axis.set_ticks([])
    elif ticks is True:
        pass
    else:
        axis.set_ticks(ticks)
    if not ticklabels:
        axis.set_ticklabels([])
    elif ticklabels is True:
        pass
    else:
        axis.set_ticklabels(ticklabels)
    if label is not None:
        axis.set_label_text(label)