import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.utils import PlotlyJSONEncoder
import json
import numpy as np

import plotly.figure_factory as ff
from scipy import stats

def create_plot(data, plot_type):
    data = pd.DataFrame(data)  
    
    if data.empty or 'timestamp' not in data.columns:
        return None  

    try:
        
        data['timestamp'] = pd.to_datetime(data['timestamp'], errors='coerce')
        data = data.dropna(subset=['timestamp'])  
        
        data['timestamp'] = data['timestamp'].dt.date
    except Exception as e:
        print(f"Error processing timestamps: {e}")
        return None

    fig = None

    
    if plot_type == 'line':
        try:
            fig = px.line(
                data,
                x='timestamp',
                y='close',
                color='ticker',
                title='Close Prices Over Time',
                labels={'timestamp': 'Date', 'close': 'Close Price'}
            )
            fig.update_layout(
                plot_bgcolor='white',  
                paper_bgcolor='white',  
                title_font=dict(size=24, color='black', family='Arial'),
                xaxis=dict(
                    title='Date',
                    titlefont=dict(size=18, color='black'),
                    tickfont=dict(size=14, color='black'),
                    showgrid=True,
                    gridcolor='lightgrey',
                    linecolor='black',
                    linewidth=2
                ),
                yaxis=dict(
                    title='Close Price',
                    titlefont=dict(size=18, color='black'),
                    tickfont=dict(size=14, color='black'),
                    showgrid=True,
                    gridcolor='lightgrey',
                    linecolor='black',
                    linewidth=2
                ),
                legend=dict(
                    font=dict(size=14, color='black')
                )
            )
            fig.update_traces(line=dict(width=2, color='black'))  
        except Exception as e:
            print(f"Error creating line plot: {e}")
    elif plot_type == 'candlestick':
        fig = go.Figure()
        try:
            for ticker, group in data.groupby('ticker'):
                if group.empty:
                    continue
                fig.add_trace(go.Candlestick(
                    x=group['timestamp'],
                    open=group['open'],
                    high=group['high'],
                    low=group['low'],
                    close=group['close'],
                    name=ticker,
                    increasing=dict(line=dict(color='green'), fillcolor='green'),  
                    decreasing=dict(line=dict(color='red'), fillcolor='red')  
                ))
            fig.update_layout(
                title='Candlestick Chart',
                xaxis_title='Date',
                yaxis_title='Price',
                height=600,
                margin=dict(l=20, r=20, t=50, b=50),
                plot_bgcolor='white',  
                paper_bgcolor='white',  
                title_font=dict(size=24, color='black', family='Arial'),
                xaxis=dict(
                    title='Date',
                    titlefont=dict(size=18, color='black'),
                    tickfont=dict(size=14, color='black'),
                    showgrid=True,
                    gridcolor='lightgrey',
                    linecolor='black',
                    linewidth=2
                ),
                yaxis=dict(
                    title='Price',
                    titlefont=dict(size=18, color='black'),
                    tickfont=dict(size=14, color='black'),
                    showgrid=True,
                    gridcolor='lightgrey',
                    linecolor='black',
                    linewidth=2
                ),
                legend=dict(
                    font=dict(size=14, color='black')
                )
            )
        except Exception as e:
            print(f"Error creating candlestick plot: {e}")
    elif plot_type == 'returns':
        fig = go.Figure()
        try:
            for ticker, group in data.groupby('ticker'):
                if group.empty:
                    continue
                group['returns'] = group['close'].pct_change() * 100
                fig.add_trace(go.Scatter(
                    x=group['timestamp'],
                    y=group['returns'],
                    mode='lines',
                    name=ticker
                ))
            fig.update_layout(
                title='Returns Over Time',
                xaxis_title='Date',
                yaxis_title='Returns (%)',
                height=600,
                margin=dict(l=20, r=20, t=50, b=50),
                plot_bgcolor='white', 
                paper_bgcolor='white',  
                title_font=dict(size=24, color='black', family='Arial'),
                xaxis=dict(
                    title='Date',
                    titlefont=dict(size=18, color='black'),
                    tickfont=dict(size=14, color='black'),
                    showgrid=True,
                    gridcolor='lightgrey',
                    linecolor='black',
                    linewidth=2
                ),
                yaxis=dict(
                    title='Returns (%)',
                    titlefont=dict(size=18, color='black'),
                    tickfont=dict(size=14, color='black'),
                    showgrid=True,
                    gridcolor='lightgrey',
                    linecolor='black',
                    linewidth=2,
                    
                ),
                legend=dict(
                    font=dict(size=14, color='black')
                )
            )
            fig.update_traces(line=dict(width=2, color='black'))  
           
        except Exception as e:
            print(f"Error creating returns plot: {e}")
    elif plot_type == 'histogram_close':
        fig = go.Figure()

        try:
            
            x_data = data['close'].dropna()
            group_labels = [data['ticker'][0]]
            colors = ['#7a3e68']  

            
            fig = ff.create_distplot(
                [x_data], group_labels, bin_size=0.5,
                curve_type='normal',  
                colors=colors
            )

            df = len(x_data) - 1  
            x_vals = np.linspace(min(x_data), max(x_data), 1000)
            t_pdf = stats.t.pdf(x_vals, df)

            fig.add_trace(go.Scatter(
                x=x_vals, y=t_pdf, mode='lines', name='T',
                line=dict(color='blue', dash='dash')
            ))

            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                title_font=dict(size=24, color='black', family='Arial'),
                xaxis=dict(
                    title='Close price',
                    titlefont=dict(size=18, color='black'),
                    tickfont=dict(size=14, color='black'),
                    showgrid=True,
                    gridcolor='lightgrey',
                    linecolor='black',
                    linewidth=2,
                    range=[x_data.min(), x_data.max()]  

                ),
                yaxis=dict(
                    title='Probability Density',
                    titlefont=dict(size=18, color='black'),
                    tickfont=dict(size=14, color='black'),
                    showgrid=True,
                    gridcolor='lightgrey',
                    linecolor='black',
                    linewidth=2
                ),
                title='Close price distribution',
            )
        except Exception as e:
            return None


    elif plot_type == 'histogram_returns':
        fig = go.Figure()

        try:
            
            data['returns'] = data['close'].pct_change() * 100
            x_data = data['returns'].dropna()
            group_labels = [data['ticker'][0]]
            colors = ['#7a3e68']  

            fig = ff.create_distplot(
                [x_data], group_labels, bin_size=0.5,
                curve_type='normal',  
                colors=colors
            )
        
            df = len(x_data) - 1  

            x_vals = np.linspace(min(x_data), max(x_data), 1000)
            t_pdf = stats.t.pdf(x_vals, df)

            fig.add_trace(go.Scatter(
                x=x_vals, y=t_pdf, mode='lines', name='T',
                line=dict(color='blue', dash='dash')
            ))

            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                title_font=dict(size=24, color='black', family='Arial'),
                xaxis=dict(
                    title='Returns (%)',
                    titlefont=dict(size=18, color='black'),
                    tickfont=dict(size=14, color='black'),
                    showgrid=True,
                    gridcolor='lightgrey',
                    linecolor='black',
                    linewidth=2,
                    range=[x_data.min(), x_data.max()]  

                ),
                yaxis=dict(
                    title='Probability Density',
                    titlefont=dict(size=18, color='black'),
                    tickfont=dict(size=14, color='black'),
                    showgrid=True,
                    gridcolor='lightgrey',
                    linecolor='black',
                    linewidth=2
                ),
                title='Returns Distribution',
            )
            
        except Exception as e:
            print(f"Error creating histogram plot: {e}")
            return None

    elif plot_type == 'log_histogram':
        fig = go.Figure()

        try:
            
            data['returns'] = data['close'].pct_change() * 100
            data['log_returns'] = np.log(1 + data['returns']).dropna()

            x_data = data['log_returns'].dropna()

            group_labels = [data['ticker'][0]]
            colors = ['#7a3e68']  

            
            fig = ff.create_distplot(
                [x_data], group_labels, bin_size=0.5,
                curve_type='normal',  
                colors=colors
            )

            
            df = len(x_data) - 1  

            
            x_vals = np.linspace(min(x_data), max(x_data), 1000)

            
            t_pdf = stats.t.pdf(x_vals, df)

            
            fig.add_trace(go.Scatter(
                x=x_vals, y=t_pdf, mode='lines', name='T',
                line=dict(color='blue', dash='dash')
            ))

            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                title_font=dict(size=24, color='black', family='Arial'),
                xaxis=dict(
                    title='Logarithmic returns',
                    titlefont=dict(size=18, color='black'),
                    tickfont=dict(size=14, color='black'),
                    showgrid=True,
                    gridcolor='lightgrey',
                    linecolor='black',
                    linewidth=2,
                    range=[x_data.min(), x_data.max()]  

                ),
                yaxis=dict(
                    title='Probability Density',
                    titlefont=dict(size=18, color='black'),
                    tickfont=dict(size=14, color='black'),
                    showgrid=True,
                    gridcolor='lightgrey',
                    linecolor='black',
                    linewidth=2
                ),
                title='Logarithmic returns distribution',
            )

            
        except Exception as e:
            return None

    
    if fig:
        try:
            plot_json = json.dumps(fig, cls=PlotlyJSONEncoder)
            return plot_json
        except Exception as e:
            return None
    return None