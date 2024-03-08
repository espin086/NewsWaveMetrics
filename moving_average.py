import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def moving_average_strategy(data, short_window, long_window):
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0

    # Create short simple moving average
    signals['short_mavg'] = data['Closing_Price'].rolling(window=short_window, min_periods=1, center=False).mean()

    # Create long simple moving average
    signals['long_mavg'] = data['Closing_Price'].rolling(window=long_window, min_periods=1, center=False).mean()

    # Generate signals
    signals['signal'][short_window:] = np.where(
        signals['short_mavg'][short_window:] > signals['long_mavg'][short_window:], 1.0, 0.0
    )

    # Generate trading orders
    signals['positions'] = signals['signal'].diff()

    return signals

# def plot_stock_data(data, signals, graph_width=900, graph_height=600):
#     fig = go.Figure()

#     # Plot stock closing prices
#     fig.add_trace(go.Scatter(x=data.index, y=data['Closing_Price'], mode='lines', name='Stock Prices'))

#     # Plot short-term moving average
#     fig.add_trace(go.Scatter(x=signals.index, y=signals['short_mavg'],
#                              mode='lines', name='Short-Term Moving Average', line=dict(color='orange')))

#     # Plot long-term moving average
#     fig.add_trace(go.Scatter(x=signals.index, y=signals['long_mavg'],
#                              mode='lines', name='Long-Term Moving Average', line=dict(color='blue')))

#     # Plot buy signals
#     fig.add_trace(go.Scatter(x=signals.index[signals['positions'] == 1],
#                              y=signals['short_mavg'][signals['positions'] == 1],
#                              mode='markers', name='Buy Signal', marker=dict(color='green', size=10)))

#     # Plot sell signals
#     fig.add_trace(go.Scatter(x=signals.index[signals['positions'] == -1],
#                              y=signals['short_mavg'][signals['positions'] == -1],
#                              mode='markers', name='Sell Signal', marker=dict(color='red', size=10)))

#     # Set layout
#     fig.update_layout(title='Stock Prices and Moving Averages with Buy/Sell Signals',
#                       xaxis_title='Date',
#                       yaxis_title='Price',
#                       template='plotly_dark',
#                       width=graph_width,
#                       height=graph_height)

#     st.plotly_chart(fig)
def plot_stock_data(data, signals, graph_width=900, graph_height=600):
    fig = go.Figure()

    # Plot stock closing prices
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Closing_Price'],
        mode='lines',
        name='Stock Prices',
        hovertemplate='%{x|%b %d %Y}<br>%{y}',
    ))

    # Plot short-term moving average
    fig.add_trace(go.Scatter(
        x=signals.index,
        y=signals['short_mavg'],
        mode='lines',
        name='Short-Term Moving Average',
        line=dict(color='orange'),
        hovertemplate='%{x|%b %d %Y}<br>%{y}',
    ))

    # Plot long-term moving average
    fig.add_trace(go.Scatter(
        x=signals.index,
        y=signals['long_mavg'],
        mode='lines',
        name='Long-Term Moving Average',
        line=dict(color='blue'),
        hovertemplate='%{x|%b %d %Y}<br>%{y}',
    ))

    # Plot buy signals
    fig.add_trace(go.Scatter(
        x=signals.index[signals['positions'] == 1],
        y=signals['short_mavg'][signals['positions'] == 1],
        mode='markers',
        name='Buy Signal',
        marker=dict(color='green', size=10),
        hovertemplate='%{x|%b %d %Y}<br>%{y}',
    ))

    # Plot sell signals
    fig.add_trace(go.Scatter(
        x=signals.index[signals['positions'] == -1],
        y=signals['short_mavg'][signals['positions'] == -1],
        mode='markers',
        name='Sell Signal',
        marker=dict(color='red', size=10),
        hovertemplate='%{x|%b %d %Y}<br>%{y}',
    ))

    # Set layout
    fig.update_layout(
        title='Stock Prices with Buy/Sell Signals',
        xaxis_title='Date',
        yaxis_title='Price',
        template='plotly_dark',
        width=graph_width,
        height=graph_height
    )

    st.plotly_chart(fig)
