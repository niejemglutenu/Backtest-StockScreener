from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
from .models import StockData
from .forms import StockDataSourceForm, VisualizationSettingsForm
import pandas as pd
import csv
import io
import json
from django.utils.html import format_html

import logging
import pandas as pd
import backtrader as bt
import plotly.graph_objects as go
from django.shortcuts import render
from django.http import JsonResponse
from .forms import BacktestSettingsForm
import logging
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .chart import create_plot
from .filters import StockDataFilter
from .models import StockData
from datetime import datetime, timezone
from django.template.loader import render_to_string
import logging
import pandas as pd
from datetime import datetime
from django.http import JsonResponse
from .models import StockData
from django_filters import rest_framework as filters
from django.shortcuts import render
logger = logging.getLogger(__name__)
import plotly.graph_objects as go
from django.http import JsonResponse
from django.shortcuts import render
from django.core.paginator import Paginator
import json
import pandas as pd
from backtesting.forms import BacktestSettingsForm
import backtrader as bt
import logging
import io
import base64
from backtrader.feeds import PandasData
import matplotlib.pyplot as plt
from backtrader import plot
import numpy as np
import plotly.graph_objects as go
from django.http import JsonResponse
from django.shortcuts import render
from django.core.paginator import Paginator
import json
import pandas as pd
from backtesting.forms import BacktestSettingsForm
import backtrader as bt
import logging
import io
import base64
from backtrader.feeds import PandasData
import matplotlib.pyplot as plt
from backtrader import plot

import numpy as np
from django.shortcuts import render, redirect
from django.http import JsonResponse
from backtrader import Cerebro, strategy, plot

from backtrader.feeds import PandasData
from .forms import BacktestSettingsForm
import pandas as pd
from backtrader.feeds import PandasData
from .forms import BacktestSettingsForm
import backtrader as bt
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import BacktestSettingsForm
import pandas as pd

from backtrader import Cerebro, plot
from backtrader.feeds import PandasData
import matplotlib.pyplot as plt

from .strategy import SmaCross, RSIStrategy
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import BacktestSettingsForm

import logging
import pandas as pd
from datetime import datetime
from django.http import JsonResponse
from .models import StockData
from django_filters import rest_framework as filters
from django import forms
from django.shortcuts import render
import backtrader as bt
from backtrader import TimeFrame
from .strategy import SimpleMovingAverageStrategy, BollingerBandStrategy, RSIStrategy, SmaCross, MACDStrategy, StochasticStrategy, IchimokuStrategy
import io
import base64
from matplotlib import pyplot as plt
import numpy as np

from backtrader import feed
import logging
import pandas as pd
from django.shortcuts import render
from django.http import JsonResponse
from .forms import BacktestSettingsForm
import backtrader as bt
from backtrader import TimeFrame
from backtrader.feeds import PandasData
from backtrader import plot
from .strategy import SmaCross, RSIStrategy
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
######################### USER ##########################

def index(request):
    return render(request, 'home.html')

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! You can now log in.")
            return redirect("login")
        else:
            messages.error(request, "Registration failed. Please try again.")
    else:
        form = UserCreationForm()
    return render(request, "register.html", {"form": form})

def login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, "You have successfully logged in!")
            return redirect("start")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})

def logout(request):
    auth_logout(request)  
    messages.success(request, "You have been logged out.")
    return redirect('login') 
def start(request):
    form = StockDataSourceForm()
    return render(request, 'select_stock_source.html', {'form': form})

######################### USER FILE UTILITY ##########################

def _detect_csv_delimiter(file):
    try:
        sample = file.read(1024).decode('utf-8')
        file.seek(0)  
        dialect = csv.Sniffer().sniff(sample, delimiters=",;")
        return dialect.delimiter
    except Exception as e:
        raise ValueError("Could not determine CSV delimiter automatically.")

def _read_and_validate_file(file):
    if file.name.endswith('.csv'):
        delimiter = _detect_csv_delimiter(file)
        print(f"Detected delimiter: {delimiter}")
        file.seek(0)  
        file_content = io.StringIO(file.read().decode('utf-8'))

        try:
            df = pd.read_csv(file_content, encoding='utf-8', sep=delimiter)
            print(pd.DataFrame(df).head())
        except Exception as e:
            raise ValueError("Error reading CSV file.")
        
    elif file.name.endswith(('.xlsx', '.xls')):
        file_content = io.BytesIO(file.read())
        df = pd.read_excel(file_content)
    else:
        raise ValueError("Unsupported file format. Please upload a CSV or Excel file.")
  
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r'[\u200B-\u200D\uFEFF]', '', regex=True)
    )
    required_columns = ['timestamp', 'ticker', 'open', 'high', 'low', 'close', 'volume']
    
    if 'ticker' not in df.columns:
        df.insert(1, 'ticker', 'UNKNOWN')

    column_count = len(required_columns)

    if len(df.columns) < column_count:
        raise ValueError(
            f"Insufficient columns in the data. Expected at least {column_count} columns."
        )
    if len(df.columns) >= column_count:
        df = df.iloc[:, :column_count]  
        df.columns = required_columns  

    if df['timestamp'].isnull().any():
        raise ValueError("Invalid timestamp format. Ensure all timestamps are valid.")
  

    return df

######################### PROCCESS DATA SOURCE CHOICE ##########################

def get_unique_tickers():
    tickers = StockData.objects.values_list('ticker', flat=True).distinct()
    return list(tickers)


def filter_data(request, data_source, ticker, start_date, end_date):
    if data_source == 'uploaded':
        session_data = request.session.get('processed_stock_data')
        if not session_data:
            return pd.DataFrame()

        df = pd.DataFrame(session_data)

        start_date = pd.to_datetime(start_date, errors='coerce', utc=True)
        end_date = pd.to_datetime(end_date, errors='coerce', utc=True)

        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce', utc=True)
        if start_date:
            df = df[df['timestamp'] >= start_date]
        if end_date:
            df = df[df['timestamp'] <= end_date]

        if ticker:
            if isinstance(ticker, str):
                df = df[df['ticker'] == ticker]
            elif isinstance(ticker, list):
                df = df[df['ticker'].isin(ticker)]

         
        return df

    elif data_source == 'server':
        query_params = request.GET.copy()
        if isinstance(ticker, str):
             query_params.setlist('ticker', [ticker])
        elif isinstance(ticker, list) and ticker:
             query_params.setlist('ticker', ticker)
        filter = StockDataFilter(query_params, queryset=StockData.objects.all())
        stock_data = filter.qs
        df = pd.DataFrame(list(stock_data.values(
            'ticker', 'timestamp', 'open', 'high', 'low', 'close', 'volume', 'vwap'
        )))
        df['timestamp'] = df['timestamp'].dt.tz_localize(None).dt.date

        return df

    else:
        return pd.DataFrame()
    
def process_data_source(request):
    form = StockDataSourceForm(request.POST, request.FILES)
    
    if not form.is_valid():
        messages.error(request, "Invalid form submission.")
        return render(request, 'select_stock_source.html', {'form': form})

    data_source = form.cleaned_data['data_source']
    request.session['selected_data_source'] = data_source

    file = form.cleaned_data.get('file')
    request.session.pop('processed_stock_data', None)
    request.session.pop('available_tickers', None)
    request.session.pop('uploaded_file', None)
    
    try:
        tickers = None
        
        if data_source == 'uploaded' and file:
            df = _read_and_validate_file(file)
            tickers = df['ticker'].dropna().unique().tolist()
            
            df_json = json.loads(df.to_json(orient='records'))
            request.session['processed_stock_data'] = df_json
            request.session['uploaded_file'] = file.name
            request.session['available_tickers'] = tickers

            return redirect('analytical_page')
                
        elif data_source == 'server':
            tickers = get_unique_tickers()
            request.session['available_tickers'] = tickers
            return redirect('analytical_page')
        
        else:
            raise ValueError("Invalid data source")
          
    except ValueError as e:
        messages.error(request, str(e))
        return render(request, 'select_stock_source.html', {'form': form})

def analytical_page(request):
    tickers = request.session.get('available_tickers', [])
    current_ticker = request.session.get('current_ticker')

    form = VisualizationSettingsForm(initial={
        'ticker': request.session.get('current_ticker'),
        'start_date': request.session.get('start_date'),
        'end_date': request.session.get('end_date'),
        'view_type': request.session.get('view_type', 'table'),
        'plot_type': request.session.get('plot_type', 'line'),
    })

    return render(request, 'analytical_page.html', {
        'current_ticker': current_ticker,
        'available_tickers': tickers,
        'form': form
    })

def handle(request):
    form = VisualizationSettingsForm(request.GET or None)

    if not form.is_valid():
        print("Form is not valid")
        print(form.errors)
        return JsonResponse({'error': 'Invalid form data'}, status=400)

    ticker_list = request.GET.getlist('ticker')
    current_ticker = ticker_list[0] if ticker_list else None
    print('CURRENT TICKER:', current_ticker)

    if current_ticker:
        request.session['current_ticker'] = current_ticker
    else:
        print("Ticker is missing")
        return JsonResponse({'error': 'Ticker is missing'}, status=400)

    start_date = form.cleaned_data.get('start_date')
    end_date = form.cleaned_data.get('end_date')
    view_type = form.cleaned_data.get('view_type')
    plot_type = form.cleaned_data.get('plot_type')
    
    request.session.update({
        'view_type': view_type,
        'plot_type': plot_type,
    })
    source = request.session.get('selected_data_source')
    print(start_date, end_date)
    filtered_data = filter_data(request, source, current_ticker, start_date, end_date)
    filtered_data = pd.DataFrame(filtered_data)
    print("Handlefunction, Filtered Data:", filtered_data.head(), filtered_data.shape, filtered_data.columns)
    
    if view_type == 'chart':
        plot_json = create_plot(filtered_data.to_dict('records'), plot_type)
        if plot_json:
            return render(request, 'partials/data_chart.html', {
                'ticker': current_ticker,
                'plot_json': plot_json,  
            })
        else:
            return JsonResponse({'error': 'Failed to generate plot'}, status=500)
    else:

        return render(request, 'partials/data_table.html', {
            'ticker': current_ticker,
            'data': filtered_data.to_dict('records'),
            'view_type': view_type,
            'plot_type': plot_type,
        })

def search(request):
    search_query = request.GET.get('search', '').lower()
    tickers = request.session.get('available_tickers', [])
    filtered_tickers = [ticker for ticker in tickers if search_query in ticker.lower()]
    return JsonResponse({'tickers': filtered_tickers})

############BACKTEST##############

def create_windows(df, start_date, end_date, window_count):
    logging.info(f"create_windows called with: df.shape='{df.shape}', start_date='{start_date}', end_date='{end_date}', window_count='{window_count}'")

    if not isinstance(df.index, pd.MultiIndex):
          logging.error("DataFrame does not have a MultiIndex with levels 'timestamp' and 'ticker'")
          return []  

    windows = []
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    all_dates = df.index.get_level_values('timestamp').unique()
    all_dates = [date for date in all_dates if start_date <= pd.to_datetime(date) <= end_date]

    if not all_dates:
         logging.warning(f"No dates were found for start date {start_date} and end date {end_date}")
         return []
    window_size = len(all_dates) // window_count
    
    for i in range(window_count):
        start_index = i * window_size
        end_index = (i+1) * window_size
        if end_index > len(all_dates) :
            logging.warning(f"window end index {end_index} is greater than length of dates {len(all_dates)}, skipping it")
            break;
        window_dates = all_dates[start_index:end_index]
        window = df.loc[(window_dates), :]
        windows.append(window)
    logging.info(f"Created windows: {len(windows)}")
    return windows


logging.basicConfig(level=logging.INFO)

TIMEFRAME = bt.TimeFrame.Days
TIMEFRAME_VAL = 1
def update_current_tickers(request):
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            tickers = data.get('tickers', [])
            tickers = [ticker for ticker in tickers if ticker]
            request.session['current_tickers'] = tickers
            return JsonResponse({'status': 'success', 'tickers': tickers})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    return JsonResponse({'status': 'error'}, status=400)


def get_strategy(strategy_type):
    if strategy_type == 'SimpleMovingAverage':
        return SimpleMovingAverageStrategy
    elif strategy_type == 'BollingerBand':
        return BollingerBandStrategy
    elif strategy_type == 'RSI':
         return RSIStrategy
    elif strategy_type == 'SmaCross':
         return SmaCross
    else:
         return SimpleMovingAverageStrategy
    

class PandasData(feed.DataBase):

    params = (

        ('datetime', None),

        ('open', -1),
        ('high', -1),
        ('low', -1),
        ('close', -1),
        ('volume', -1),
        ('openinterest', -1),
    )

class custompandas(bt.feeds.PandasData):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'vwap' in self.dataname.columns:
              self.p.openinterest = 'vwap'
        else:
              self.p.openinterest = None

    params = (
        ('high', 'high'),
        ('low', 'low'),
        ('open', 'open'),
        ('close', 'close'),
        ('volume', 'volume'),
    )

TIMEFRAME = bt.TimeFrame.Days
TIMEFRAME_VAL = 1

class CustomPandasData(bt.feeds.PandasData):
    params = (
        ('datetime', None),
        ('open', 'open'),
        ('high', 'high'),
        ('low', 'low'),
        ('close', 'close'),
        ('volume', 'volume'),
        ('openinterest', None),  
    )


def backtest(request):
    form = BacktestSettingsForm(initial={
        'start_date': request.session.get('start_date'),
        'end_date': request.session.get('end_date'),
        'backtest_method': request.session.get('backtest_method'),
        'window_count': request.session.get('window_count'),
        'strategy': request.session.get('strategy'),
    })

    if request.method == 'POST':
        form = BacktestSettingsForm(request.POST)
        
        if form.is_valid():
            request.session['backtest_method'] = form.cleaned_data['backtest_method']
            request.session['window_count'] = form.cleaned_data['window_count']
            request.session['strategy'] = form.cleaned_data['strategy']
            request.session['start_date'] = form.cleaned_data['start_date']
            request.session['end_date'] = form.cleaned_data['end_date']

            analysis_results = {}  
            plot_html = None  
            if request.is_ajax():
                return JsonResponse({
                    'analysis_results': analysis_results,
                    'plot_html': plot_html,
                    'status': 'success',
                })

            return render(request, 'backtest.html', {
                'form': form,
                'analysis_results': analysis_results,
                'plot_html': plot_html,
            })
        
        else:
            return render(request, 'backtest.html', {
                'form': form,
                'analysis_results': {},
                'plot_html': None,
            })

    return render(request, 'backtest.html', {
        'form': form,
        'analysis_results': {},
        'plot_html': None,
    })


def plot_win_loss_distribution(wins, losses):
    print("WINS:", wins)

    labels = ['Wins', 'Losses']
    sizes = [wins, losses]


    trace = go.Pie(labels=labels, values=sizes, marker=dict(colors=['green', 'red']), textinfo='percent', hole=0.3)
    layout = go.Layout(title='Win/Loss Distribution')
    figure = go.Figure(data=[trace], layout=layout)


    plot_json = figure.to_json()
    
    return plot_json


def plot_pnl_histogram(pnl_data, bins=30, color='purple', alpha=0.7):
    print("PNL DATA:",pnl_data)
    if not pnl_data:
        return None 

    
    trace = go.Histogram(x=pnl_data, nbinsx=bins, marker=dict(color=color, opacity=alpha))
    layout = go.Layout(title='Profit and Loss Histogram', xaxis=dict(title='Profit/Loss'), yaxis=dict(title='Frequency'))
    figure = go.Figure(data=[trace], layout=layout)

    
    plot_json = figure.to_json()
    return plot_json


def add_analyzers(cerebro):
    
    analyzers = [
        (bt.analyzers.SharpeRatio, {"_name": "sharpe", "timeframe": bt.TimeFrame.Minutes, "compression": 60}),
        (bt.analyzers.Returns, {"_name": "returns"}),
        (bt.analyzers.TradeAnalyzer, {"_name": "trades"}),
        (bt.analyzers.DrawDown, {"_name": "drawdown"}),
        (bt.analyzers.AnnualReturn, {"_name": "annualreturn"}),
        (bt.analyzers.PeriodStats, {"_name": "periodstats"}),
        (bt.analyzers.TimeReturn, {"_name": "timereturn"}),
        (bt.analyzers.SQN, {"_name": "SQN"}),
        (bt.analyzers.GrossLeverage, {"_name": "GrossLeverage"}),
        (bt.analyzers.Transactions, {"_name": "transactions"}),
        (bt.analyzers.PositionsValue, {"_name": "PositionsValue"}),
        (bt.analyzers.VWR, {"_name": "vwr"}),  
        (bt.analyzers.SharpeRatio_A, {"_name": "sharpe_annual"}),  
    ]

    for analyzer, params in analyzers:
        cerebro.addanalyzer(analyzer, **params)

    cerebro.addobserver(bt.observers.Broker)
    cerebro.addobserver(bt.observers.DrawDown)


def display_results(strategy, cerebro, data):
    
    try:
        analyzers = strategy.analyzers
        trade_analyzer = analyzers.trades.get_analysis()

        total_trades = trade_analyzer.get('total', {}).get('closed', 0)
        win_count = trade_analyzer.get('won', {}).get('total', 0)
        loss_count = trade_analyzer.get('lost', {}).get('total', 0)
        win_rate = f"{win_count / total_trades:.2%}" if total_trades > 0 else "N/A"

        holding_times = [
            (trade['dtclose'] - trade['dtopen']).total_seconds() / 60.0
            for trade in trade_analyzer.get('trades', []) if isinstance(trade, dict)
        ]
        average_holding_time = f"{sum(holding_times) / len(holding_times):.2f} minutes" if holding_times else "N/A"

        positions_value = analyzers.PositionsValue.get_analysis()
        avg_position_value = (
            sum(pos['value'] for pos in positions_value.get('positions', [])) / len(positions_value.get('positions', []))
            if positions_value.get('positions') else "N/A"
        )
        annual_return_data = analyzers.annualreturn.get_analysis()
        print(annual_return_data)
        
        def get_analyzer_value(analyzer, key, default=None):
            analysis = analyzer.get_analysis()
            return analysis.get(key, default) if analysis else default

        def _render_nested_list(item, level=0, max_depth=3):
          if level > max_depth:
            return format_html("<span>...</span>")

          if isinstance(item, dict):
            list_items = []
            for key, value in item.items():
              list_items.append(
                format_html(
                  "<li><strong>{}</strong>: {}</li>",
                    key,
                    _render_nested_list(value, level + 1, max_depth)
                  )
                )
            return format_html("<ul>{}</ul>", format_html("".join(list_items)))

          elif isinstance(item, list):
                list_items = [format_html("<li>{}</li>", _render_nested_list(value, level + 1, max_depth)) for value in item]
                return format_html('<ul>{}</ul>', format_html("".join(list_items)))
          else:
                try:
                    return format_html("{:.4f}", float(item))
                except (ValueError, TypeError):
                    return format_html("{}", item)


        filtered_trade_analyzer = {key: trade_analyzer.get(key, "N/A") for key in ["total", "streak", "pnl", "won", "lost", "long", "short"]}
        trade_analyzer_list = _render_nested_list(filtered_trade_analyzer)
        print(trade_analyzer_list)
        drawdown = analyzers.drawdown.get_analysis()
        max_drawdown = drawdown.get('max',{}).get('drawdown', None) if drawdown else None


        final_value = cerebro.broker.get_value()

        fund_shares = cerebro.broker.get_fundshares()
        print("FUND SHARES", fund_shares)

        return {
            'final_value': final_value,
            'fund_shares': fund_shares,
            'sharpe_ratio': get_analyzer_value(analyzers.sharpe, 'sharperatio'),
            'sharpe_ratio_annual': get_analyzer_value(analyzers.sharpe_annual, 'sharperatio'),
            'total_return': get_analyzer_value(analyzers.returns, 'rtot'),
            'total_trades': total_trades,
            'win_count': win_count,
            'loss_count': loss_count,
            'win_rate': win_rate,
            'average_holding_time': average_holding_time,
            'SQN': get_analyzer_value(analyzers.SQN, 'sqn'),
            'max_drawdown': max_drawdown,
            'annual_return': annual_return_data,
            'vwr': get_analyzer_value(analyzers.vwr, 'vwr'),
            'average_position_value': avg_position_value,
            'trade_analyzer_list':trade_analyzer_list
        }
    except Exception as e:
        logging.error(f"Error in display_results: {e}")
        return {}
    
def backtest_run(request):

    form = BacktestSettingsForm(request.GET or None)

    if not form.is_valid():
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid form data.',
            'errors': form.errors
        }, status=400)

    try:
        session = request.session
        start_date, end_date = form.cleaned_data['start_date'], form.cleaned_data['end_date']
        backtest_method = form.cleaned_data['backtest_method']
        strategy_name = form.cleaned_data['strategy']
        commission = form.cleaned_data['commission']
        cerebro = bt.Cerebro()
        cash = form.cleaned_data['cash']
        cerebro.broker.setcash(cash)
        cerebro.broker.setcommission(commission)

        add_analyzers(cerebro)
        tickers = session.get('current_tickers', [])
        all_data = []

        for ticker in tickers:
            filtered_data = filter_data(request, session.get('selected_data_source'), ticker, start_date, end_date)
            if filtered_data.empty:
                logging.warning(f"No data for ticker: {ticker}")
                continue
            filtered_data = pd.DataFrame(filtered_data).assign(
              datetime=lambda df: pd.to_datetime(df['timestamp'], utc=True).dt.tz_localize(None)
            ).set_index('datetime')
            data = CustomPandasData(dataname=filtered_data[['open', 'high', 'low', 'close', 'volume']])
            cerebro.adddata(data, name=ticker)
            all_data.append(filtered_data)

        strategy_mapping = {
            'SimpleMovingAverage': SimpleMovingAverageStrategy,
            'BollingerBand': BollingerBandStrategy,
            'RSI': RSIStrategy,
            'SmaCross': SmaCross,
            'MACDStrategy': MACDStrategy,
            'IchimokuStrategy': IchimokuStrategy,
            'StochasticStrategy':StochasticStrategy,
        }

        strategy_class = strategy_mapping.get(strategy_name)

        if not strategy_class:
            return JsonResponse({
            'status': 'error',
            'message': f'Strategy {strategy_name} not found.',
             }, status=400)
        
        strategy_params_mapping = {
            'SimpleMovingAverage': {'maperiod': 'sma_period'},
            'BollingerBand': {'period': 'period', 'devfactor': 'devfactor', 'mid_band': 'mid_band'},
            'RSI': {'window_size': 'rsi_period'},
            'SmaCross': {'pfast': 'sma_fast_period', 'pslow': 'sma_slow_period'},
            'MACDStrategy': {'fast_period':'fast_period', 'slow_period': 'slow_period', 'signal_period':'signal_period'},
             'IchimokuStrategy':{'tenkan_period':'tenkan_period', 'kijun_period':'kijun_period', 'senkou_b_period':'senkou_b_period', 'displacement':'displacement'},
            'StochasticStrategy':{'period_k':'period_k', 'period_d':'period_d', 'period_s':'period_s', 'overbought':'overbought', 'oversold':'oversold'}
        }


        strategy_params = {}
        if strategy_name in strategy_params_mapping:
          for strategy_param, form_field in strategy_params_mapping[strategy_name].items():
                strategy_params[strategy_param] = form.cleaned_data.get(form_field)



        backtest_params = {}
        if backtest_method == 'expanding_window':
          backtest_params['startdate'] = form.cleaned_data.get('expanding_window_start')



        strategy_params = {k: v for k, v in strategy_params.items() if v is not None}
        backtest_params = {k: v for k, v in backtest_params.items() if v is not None}

        cerebro.addstrategy(strategy_class, **strategy_params)
        cerebro.addsizer(bt.sizers.PercentSizer, percents=10)
        
        allow_short = form.cleaned_data['allow_short']
        if allow_short != 'allow_short':
            cerebro.broker = bt.brokers.BackBroker(shortcash=False)
    


        results = cerebro.run(**backtest_params)
        strategy_result = results[0]

        analysis_results = display_results(strategy_result, cerebro, pd.concat(all_data, ignore_index=True))
        rendered_results = render_to_string('partials/backtest_result.html', {
            'analysis_results': analysis_results,
        })
        win_loss_plot = plot_win_loss_distribution(analysis_results.get('win_count', 0), analysis_results.get('loss_count', 0))

        return JsonResponse({
            'status': 'success',
            'analysis_results': rendered_results,
             'win_loss_plot': win_loss_plot,
        })

    except Exception as e:
        logging.error(f"Error during backtest execution: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Error during backtest execution. Check server logs',
            'errors': str(e)
        }, status=500)