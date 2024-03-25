import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

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

def plot_sentiment_counts_per_year(df):

    df['Date'] = pd.to_datetime(df['Date'])
    
    df['Year'] = df['Date'].dt.year
    
    sentiment_counts = df.groupby(['Year', 'Sentiment']).size().reset_index(name='Count')
    
    sentiment_counts = sentiment_counts.groupby('Year').apply(lambda x: x.assign(Percentage=x['Count'] / x['Count'].sum() * 100)).reset_index(drop=True)
    
    color_mapping = {'positive': 'green', 'negative': 'red', 'neutral': 'grey'}
    
    fig = px.bar(sentiment_counts, x='Year', y='Percentage', color='Sentiment',
                 title='Sentiment Percentage per Year',
                 labels={'Percentage': 'Sentiment Percentage (%)', 'Year': 'Year'},
                 color_discrete_map=color_mapping)
    
    fig.update_xaxes(tickmode='linear', tick0=2010, dtick=1)
    
    st.plotly_chart(fig)

def plot_average_sentiment_by_date(df):

    df['Date'] = pd.to_datetime(df['Date'])
    
    average_sentiment = df.groupby(['Date', 'Sentiment_Score']).size().unstack(fill_value=0).mean(axis=1)
    
    average_sentiment = average_sentiment.reset_index(name='Average Sentiment Score')
    
    fig = px.line(average_sentiment, x='Date', y='Average Sentiment Score',
                  title='Average Sentiment Score by Date',
                  labels={'Average Sentiment': 'Average Sentiment', 'Date': 'Date'})
    
    st.plotly_chart(fig)

def plot_economic_data(df, selected_column):

    st.write("## Economic Data Plot")
    
    df['date'] = pd.to_datetime(df['date'])

    df_selected = df[['date', selected_column]]

    df_cleaned = df_selected.dropna()

    fig = px.line(df_cleaned, x='date', y=selected_column, title=f"{selected_column} Over Time")
    
    st.plotly_chart(fig)

