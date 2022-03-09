import os
import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from valuation.utils.gsheats import Sheet
from valuation.utils.data import standardize_date
from valuation.utils.data import eoy_period_generator
from valuation.random.distributions import TimeSeriesDistribution


def plot_realized_and_ts_distribution(realized: pd.Series = None, predicted_distribution: TimeSeriesDistribution = None,
                                      predicted_dates: list = None,
                                      analyst_estimates: pd.Series = None,
                                      data_label: str = None,
                                      savepath: str = None):
    fig = go.Figure()

    if isinstance(predicted_distribution, TimeSeriesDistribution):

        for percentile in [68, 90, 95]:
            tail = (100 - percentile) / 2
            lower_uncertainty = pd.Series(np.percentile(predicted_distribution.values, tail, axis=0),
                                          index=predicted_dates)
            upper_uncertainty = pd.Series(np.percentile(predicted_distribution.values, 100 - tail, axis=0),
                                          index=predicted_dates)

            if isinstance(realized, pd.Series) and len(realized) > 0:
                upper_uncertainty = pd.concat \
                    ([pd.Series({realized.index[-1]: realized.values[-1]}), upper_uncertainty]).sort_index()
                lower_uncertainty = pd.concat \
                    ([pd.Series({realized.index[-1]: realized.values[-1]}), lower_uncertainty]).sort_index()
            fig.add_trace(go.Scatter(x=lower_uncertainty.index, y=lower_uncertainty.values, mode='lines', line_width=0,
                                     line_color='orange', showlegend=False))
            fig.add_trace(go.Scatter(x=upper_uncertainty.index, y=upper_uncertainty.values, mode='lines', line_width=0,
                                     line_color='orange', fill='tonexty',
                                     name='{}% Credibility Interval'.format(percentile)))

        expected = pd.Series(np.mean(predicted_distribution.values, axis=0), index=predicted_dates)
        marker_opacity = np.ones(len(expected))
        if isinstance(realized, pd.Series) and len(realized) > 0:
            marker_opacity = np.ones(len(expected) + 1)
            marker_opacity[0] = 0
            expected = pd.concat([pd.Series({realized.index[-1]: realized.values[-1]}), expected]).sort_index()
        fig.add_trace(
            go.Scatter(x=expected.index, y=expected.values, mode='lines+markers', name='Expected', line_color='red',
                       marker_opacity=marker_opacity))

    if isinstance(realized, pd.Series) and len(realized) > 0:
        fig.add_trace(
            go.Scatter(x=realized.index, y=realized.values, mode='lines+markers', name='Realized', line_color='blue'))

    if isinstance(analyst_estimates, pd.Series) and len(analyst_estimates) > 0:
        fig.add_trace(go.Scatter(x=analyst_estimates.index, y=analyst_estimates.values,
                                 mode='markers', name='Analyst Estimates',
                                 marker=dict(color='rgba(0,0,0,0.0)', size=8,
                                             line=dict(color='rgba(0,255,0,1.0)', width=2))))

    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig.update_xaxes(showline=True, linewidth=2, linecolor='black')
    fig.update_yaxes(showline=True, linewidth=2, linecolor='black', title=data_label)

    if savepath is not None:
        fig.write_html(os.path.expanduser(savepath))

    return fig


def plot_realized_and_predicted_series(realized: pd.Series = None, expected: pd.Series = None,
                                           lower_uncertainty: pd.Series = None, upper_uncertainty: pd.Series = None,
                                           analyst_estimates: pd.Series = None,
                                           data_label: str = None,
                                           savepath: str = None):
    fig = go.Figure()

    if isinstance(lower_uncertainty, pd.Series) and len(lower_uncertainty) > 0 and isinstance(upper_uncertainty,
                                                                                              pd.Series) and len(
            upper_uncertainty) > 0:
        if isinstance(realized, pd.Series) and len(realized) > 0:
            upper_uncertainty = pd.concat \
                ([pd.Series({realized.index[-1]: realized.values[-1]}), upper_uncertainty]).sort_index()
            lower_uncertainty = pd.concat \
                ([pd.Series({realized.index[-1]: realized.values[-1]}), lower_uncertainty]).sort_index()
        fig.add_trace(go.Scatter(x=lower_uncertainty.index, y=lower_uncertainty.values, mode='lines', line_width=0,
                                 line_color='orange', showlegend=False))
        fig.add_trace(go.Scatter(x=upper_uncertainty.index, y=upper_uncertainty.values, mode='lines', line_width=0,
                                 line_color='orange', fill='tonexty', name='Uncertainty'))

    if isinstance(expected, pd.Series) and len(expected) > 0:
        marker_opacity = np.ones(len(expected))
        if isinstance(realized, pd.Series) and len(realized) > 0:
            marker_opacity = np.ones(len(expected) + 1)
            marker_opacity[0] = 0
            expected = pd.concat([pd.Series({realized.index[-1]: realized.values[-1]}), expected]).sort_index()
        fig.add_trace(
            go.Scatter(x=expected.index, y=expected.values, mode='lines+markers', name='Expected', line_color='red',
                       marker_opacity=marker_opacity))

    if isinstance(realized, pd.Series) and len(realized) > 0:
        fig.add_trace(
            go.Scatter(x=realized.index, y=realized.values, mode='lines+markers', name='Realized', line_color='blue'))

    if isinstance(analyst_estimates, pd.Series) and len(analyst_estimates) > 0:
        fig.add_trace(go.Scatter(x=analyst_estimates.index, y=analyst_estimates.values,
                                 mode='markers', name='Analyst Estimates',
                                 marker=dict(color='rgba(0,0,0,0.0)', size=8,
                                             line=dict(color='rgba(0,255,0,1.0)', width=2))))

    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig.update_xaxes(showline=True, linewidth=2, linecolor='black')
    fig.update_yaxes(showline=True, linewidth=2, linecolor='black', title=data_label)

    if savepath is not None:
        fig.write_html(os.path.expanduser(savepath))

    return fig


def plot_history_and_time_series_dist_from_sheet(sheet: Sheet, metric: str, timeseries_dist: TimeSeriesDistribution,
                                                 analyst_estimates: pd.Series = None,
                                                 future_dates: list[datetime.date] = None, savepath: str = None):
    realized = pd.Series(
        sheet[metric, sheet.date_columns()],
        index=standardize_date(sheet.date_columns())
    )

    if future_dates is None:
        valuation_date = datetime.datetime.now().date()
        terminal_date = (valuation_date + datetime.timedelta(days=365 * (timeseries_dist.num_periods - 1))).replace(
            day=31, month=12)
        future_dates = [v[1] for v in eoy_period_generator(valuation_date, terminal_date)]

    mean = pd.Series(timeseries_dist.values.mean(axis=0), index=future_dates)

    fig = plot_realized_and_ts_distribution(
        realized,
        timeseries_dist,
        future_dates,
        analyst_estimates,
        metric,
        savepath=savepath
    )

    return fig


def plot_history_and_time_series_dist_from_series(realized: pd.Series, metric: str,
                                                  timeseries_dist: TimeSeriesDistribution,
                                                  analyst_estimates: pd.Series = None,
                                                  future_dates: list[datetime.date] = None,
                                                  savepath: str = None):
    if future_dates is None:
        valuation_date = datetime.datetime.now().date()
        terminal_date = (valuation_date + datetime.timedelta(days=365 * (timeseries_dist.num_periods - 1))).replace(
            day=31, month=12)
        future_dates = [v[1] for v in eoy_period_generator(valuation_date, terminal_date)]

    fig = plot_realized_and_ts_distribution(
        realized,
        timeseries_dist,
        future_dates,
        analyst_estimates,
        metric,
        savepath=savepath
    )

    return fig


def plot_histogram(samples: np.ndarray, vline: float = None, title: str = '', xlabel: str = '',
                   ylabel: str = 'Probability', savepath: str = None, nbins: int = None):

    fig = go.Figure(data=[go.Histogram(x=samples, histnorm='probability', nbinsx=nbins)])

    if vline is not None:
        fig.add_vline(x=vline, line_color='red')

    fig.update_layout(title=title, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig.update_xaxes(showline=True, linewidth=2, linecolor='black', title=xlabel)
    fig.update_yaxes(showline=True, linewidth=2, linecolor='black', title=ylabel)

    if savepath is not None:
        fig.write_html(os.path.expanduser(savepath))

    return fig
