from django import forms
# form - wybór źrodla danych
class StockDataSourceForm(forms.Form):
    data_source = forms.ChoiceField(
    choices=[('uploaded', 'Upload CSV/Excel'), ('server', 'Server Data')],
    widget=forms.RadioSelect,
    required=True
    )
    file = forms.FileField(required=False)
class VisualizationSettingsForm(forms.Form):
    
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    view_type = forms.ChoiceField(choices=[('chart', 'Chart'), ('table', 'Table')], required=True)
    plot_type = forms.ChoiceField(choices=[('line', 'Line'), ('candlestick', 'Candlestick'), ('returns', 'pierwsze przyrosty'),
        ('histogram_close', 'Histogram close price'), ('histogram_returns', 'Histogram returns price'),
        ('log_histogram', "Logarithmic  returns histogram")], required=True)
    ticker = forms.CharField(required=True)


from django import forms

class BacktestSettingsForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        label='Start Date'
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        label='End Date'
    )
    backtest_method = forms.CharField(
        initial="expanding_window",
        widget=forms.Select(choices=[('expanding_window', 'Expanding Window'), ('full_period', 'Full Period')]),
        required=False,
        label='Backtest Method'
    )
    window_count = forms.IntegerField(
        initial=5,
        widget=forms.NumberInput(attrs={'min': 1}),
        required=False,
        label='Window Count'
    )
    commission = forms.FloatField(required=False, initial=0.0)
    cash = forms.FloatField(required=False, initial=100000.0)
    allow_short = forms.ChoiceField(choices=[('allow_short', 'Short sell active'), ('none', 'Short sell disactive')])
                                
    strategy = forms.CharField(
        widget=forms.Select(choices=[('SimpleMovingAverage', 'Simple Moving Average'),
                                   ('BollingerBand', 'Bollinger Band'), ('RSI', 'RSI'), ('SmaCross', 'SMACross'),
                                   ('MACDStrategy', 'MACD'), ('IchimokuStrategy', 'Ichimoku Cloud'),
                                   ('StochasticStrategy', 'Stochastic Oscillator')]),
        label='Strategy'
    )

    data_feed = forms.CharField(widget=forms.HiddenInput(), required=False)

    
    sma_period = forms.IntegerField(
        initial=20,
        widget=forms.NumberInput(attrs={'min': 1}),
        required=False,
        label='Simple Moving Average Period'
    )

    period = forms.IntegerField(
        initial=20,
        widget=forms.NumberInput(attrs={'min': 1}),
        required=False,
        label='Bollinger Band Period'
    )
    devfactor = forms.FloatField(
        initial=2.0,
        widget=forms.NumberInput(),
        required=False,
        label='Bollinger Band Standard Deviation'
    )
    midband = forms.FloatField(
        initial=0.5,
        widget=forms.NumberInput(),
        required=False,
        label='MID bollinger band'
    )
    rsi_period = forms.IntegerField(
        initial=14,
        widget=forms.NumberInput(attrs={'min': 1}),
        required=False,
        label='RSI Period'
    )

    sma_fast_period = forms.IntegerField(
        initial=10,
        widget=forms.NumberInput(attrs={'min': 1}),
        required=False,
        label='SMA Fast Period'
    )
    sma_slow_period = forms.IntegerField(
        initial=30,
        widget=forms.NumberInput(attrs={'min': 1}),
        required=False,
        label='SMA Slow Period'
    )
    # Backtest method specific parameters
    expanding_window_start = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        label='Expanding Window Start Date'
    )

    fast_period = forms.IntegerField(
         initial=12,
         widget=forms.NumberInput(attrs={'min': 1}),
         required=False,
         label='MACD Fast Period'
      )
    slow_period = forms.IntegerField(
         initial=26,
         widget=forms.NumberInput(attrs={'min': 1}),
          required=False,
          label='MACD Slow Period'
      )
    signal_period = forms.IntegerField(
       initial=9,
       widget=forms.NumberInput(attrs={'min': 1}),
       required=False,
        label='MACD Signal Period'
    )

    tenkan_period = forms.IntegerField(
      initial=9,
      widget=forms.NumberInput(attrs={'min': 1}),
      required=False,
      label='Tenkan Sen Period'
      )
    kijun_period = forms.IntegerField(
       initial=26,
       widget=forms.NumberInput(attrs={'min': 1}),
       required=False,
       label='Kijun Sen Period'
     )
    senkou_b_period = forms.IntegerField(
         initial=52,
         widget=forms.NumberInput(attrs={'min': 1}),
         required=False,
         label='Senkou Span B Period'
        )
    displacement = forms.IntegerField(
        initial=26,
        widget=forms.NumberInput(attrs={'min': 1}),
        required=False,
        label='Displacement'
       )
    period_k = forms.IntegerField(
       initial=14,
       widget=forms.NumberInput(attrs={'min': 1}),
       required=False,
       label='Stochastic K Period'
     )
    period_d = forms.IntegerField(
         initial=3,
         widget=forms.NumberInput(attrs={'min': 1}),
         required=False,
         label='Stochastic D Period'
     )
    period_s = forms.IntegerField(
      initial=3,
      widget=forms.NumberInput(attrs={'min': 1}),
      required=False,
      label='Stochastic S Period'
     )
    overbought = forms.IntegerField(
         initial=80,
         widget=forms.NumberInput(attrs={'min': 1}),
         required=False,
         label='Stochastic Overbought Level'
       )
    oversold = forms.IntegerField(
        initial=20,
        widget=forms.NumberInput(attrs={'min': 1}),
        required=False,
        label='Stochastic Oversold Level'
      )