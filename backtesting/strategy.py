import backtrader as bt

class RSIStrategy(bt.Strategy):
    params = (
        ('window_size', 14),
        ('buy_level', 30),
        ('sell_level', 70),
    )

    def __init__(self):
      self.rsi = {data: bt.indicators.RSI(data, period=self.p.window_size) for data in self.datas}

    def next(self):
        for data in self.datas:
            if not self.position:  
                if self.rsi[data][0] < self.p.buy_level:  
                    self.buy(data=data)
            elif self.position:
                if self.rsi[data][0] > self.p.sell_level:  
                    self.close(data=data)


class SmaCross(bt.Strategy):
    params = (
        ('pfast', 10),  
        ('pslow', 30)  
    )

    def __init__(self):
        sma1 = bt.ind.SMA(period=self.p.pfast) 
        sma2 = bt.ind.SMA(period=self.p.pslow) 
        self.crossover = bt.ind.CrossOver(sma1, sma2) 

    def next(self):
        if not self.position: 
            if self.crossover > 0: 
                self.buy()  

        elif self.crossover < 0: 
            self.close()  

class SimpleMovingAverageStrategy(bt.Strategy):
    params = (
        ('maperiod', 20),
    )

    def __init__(self):
        self.sma = {data: bt.indicators.SimpleMovingAverage(data, period=self.p.maperiod) for data in self.datas}
        self.order = {}

    def next(self):
        for data in self.datas:
            if self.order.get(data):
                return

            if not self.position: 
                if data.close[0] > self.sma[data][0]: 
                    self.order[data] = self.buy(data=data)
                elif data.close[0] < self.sma[data][0]: 
                    self.order[data] = self.sell(data=data)
            else: 
                if data.close[0] < self.sma[data][0] and self.position.size > 0:  
                    self.order[data] = self.close(data=data)
                elif data.close[0] > self.sma[data][0] and self.position.size < 0: 
                    self.order[data] = self.close(data=data)


    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            self.order[order.data] = None

import backtrader as bt

class BollingerBandStrategy(bt.Strategy):
    params = (
        ('period', 20),
        ('devfactor', 2),
        ('midband', 0.5) 
    )

    def __init__(self):
        self.boll = {
            data: bt.indicators.BollingerBands(
                data, period=self.p.period, devfactor=self.p.devfactor
            )
            for data in self.datas
        }
        self.order = {} 
    def next(self):
        for data in self.datas:
            if self.order.get(data) and self.order[data].status in [self.order[data].Submitted, self.order[data].Accepted]:
                continue 
            
            if not self.getposition(data).size: 
                if data.close[0] < self.boll[data].lines.bot[0]: 
                    self.order[data] = self.buy(data=data)
                elif data.close[0] > self.boll[data].lines.top[0]:  
                     self.order[data] = self.sell(data=data)
            elif self.getposition(data).size > 0: 
                  if  data.close[0] > self.boll[data].lines.mid[0] * (1 + self.p.midband) : 
                     self.order[data] = self.close(data=data)
            elif self.getposition(data).size < 0: 
                if  data.close[0] < self.boll[data].lines.mid[0] * (1 - self.p.midband): 
                     self.order[data] = self.close(data=data)


    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            self.order[order.data] = None  


import backtrader as bt

class MACDStrategy(bt.Strategy):
    """
    A strategy that uses the Moving Average Convergence Divergence (MACD) indicator.
    """
    params = (
        ('fast_period', 12),
        ('slow_period', 26),
        ('signal_period', 9),
    )

    def __init__(self):
        self.macd = {data: bt.indicators.MACD(data,
                                            period_me1=self.p.fast_period,
                                            period_me2=self.p.slow_period,
                                            period_signal=self.p.signal_period)
                      for data in self.datas}
        self.order = {} 


    def next(self):
        for data in self.datas:
            if self.order.get(data):
                return
            if not self.position:
                if self.macd[data].macd[0] > self.macd[data].signal[0]:
                    self.order[data] = self.buy(data=data)
            elif self.position:
               if self.macd[data].macd[0] < self.macd[data].signal[0]:
                    self.order[data] = self.close(data=data)
    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            self.order[order.data] = None


import backtrader as bt
import numpy as np
import backtrader as bt
import numpy as np

class IchimokuStrategy(bt.Strategy):
    """
    Enhanced Ichimoku Cloud strategy with position sizing and risk management.
    """
    params = (
        ('tenkan_period', 9),
        ('kijun_period', 26),
        ('senkou_b_period', 52),
        ('displacement', 26),
        ('risk_percent', 2.0),      
        ('atr_period', 14),         
        ('trailing_stop', True),   
        ('trail_percent', 1.5),    
    )

    def __init__(self):
       
        self.ichimoku = {
            data: bt.indicators.Ichimoku(
                data,
                tenkan=self.p.tenkan_period,
                kijun=self.p.kijun_period,
                senkou=self.p.senkou_b_period
            ) for data in self.datas
        }
        
      
        self.atr = {
            data: bt.indicators.ATR(
                data,
                period=self.p.atr_period
            ) for data in self.datas
        }
        
      
        self.orders = {}
        self.stops = {}
        self.trailing_stops = {}

    def calculate_position_size(self, data, stop_price):
        """Calculate position size based on risk percentage"""
        risk_amount = self.broker.getvalue() * (self.p.risk_percent / 100)
        point_risk = abs(data.close[0] - stop_price)
        if point_risk > 0:
            size = risk_amount / point_risk
            return int(size)
        return 0

    def next(self):
        for data in self.datas:
            if self.orders.get(data):
                self.manage_trailing_stop(data)
                continue

            ichimoku = self.ichimoku[data]
            
           
            span_a = ichimoku.l.senkou_span_a[-self.p.displacement] if len(ichimoku.l.senkou_span_a) > self.p.displacement else None
            span_b = ichimoku.l.senkou_span_b[-self.p.displacement] if len(ichimoku.l.senkou_span_b) > self.p.displacement else None
            
            if not span_a or not span_b:
                continue

           
            if not self.getposition(data):
                if (data.close[0] > span_a and
                    data.close[0] > span_b and
                    ichimoku.l.tenkan_sen[0] > ichimoku.l.kijun_sen[0] and
                    data.volume[0] > data.volume[-1]):  
                    
                    stop_price = data.close[0] - self.atr[data][0] * 2
                    size = self.calculate_position_size(data, stop_price)
                    
                    if size > 0:
                        self.orders[data] = self.buy(data=data, size=size)
                        self.stops[data] = stop_price

          
            elif self.getposition(data):
                if (data.close[0] < span_a and
                    data.close[0] < span_b and
                    ichimoku.l.tenkan_sen[0] < ichimoku.l.kijun_sen[0]):
                    self.orders[data] = self.close(data=data)

    def manage_trailing_stop(self, data):
        """Update trailing stops for open positions"""
        if not self.p.trailing_stop or not self.getposition(data):
            return

        current_price = data.close[0]
        if data not in self.trailing_stops:
            self.trailing_stops[data] = current_price

        trail_amount = current_price * (self.p.trail_percent / 100)
        
        if current_price > self.trailing_stops[data]:
            self.trailing_stops[data] = current_price - trail_amount
        elif current_price < self.trailing_stops[data]:
            self.orders[data] = self.close(data=data)

    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            self.orders[order.data] = None
            
            if order.status == order.Completed:
                if order.isbuy():
                    self.trailing_stops[order.data] = order.executed.price
            elif order.status == order.Canceled:
                self.stops.pop(order.data, None)
                self.trailing_stops.pop(order.data, None)


import backtrader as bt
import numpy as np

import backtrader as bt
import numpy as np

class StochasticStrategy(bt.Strategy):
    """
    Enhanced Stochastic Oscillator strategy with advanced features.
    """
    params = (
        ('period_k', 14),
        ('period_d', 3),
        ('period_s', 3),
        ('overbought', 80),
        ('oversold', 20),
        ('risk_percent', 1.5),      
        ('atr_period', 14),         
        ('volume_factor', 1.5),     
        ('profit_target', 2.0),     
    )

    def __init__(self):
        self.stochastic = {
            data: bt.indicators.StochasticFast(
                data,
                period=self.p.period_k,
                period_dfast=self.p.period_d
            ) for data in self.datas
        }
        
        self.atr = {
            data: bt.indicators.ATR(
                data,
                period=self.p.atr_period
            ) for data in self.datas
        }
        
        self.sma = {
            data: bt.indicators.SMA(
                data,
                period=20
            ) for data in self.datas
        }
        
        self.volume_ma = {
            data: bt.indicators.SMA(
                data.volume,
                period=5
            ) for data in self.datas
        }
        
        self.orders = {}
        self.stops = {}
        self.targets = {}

    def calculate_position_size(self, data, stop_price):
        """Calculate position size based on risk percentage"""
        risk_amount = self.broker.getvalue() * (self.p.risk_percent / 100)
        point_risk = abs(data.close[0] - stop_price)
        if point_risk > 0:
            size = risk_amount / point_risk
            return int(max(1, size)) 
        return 0

    def next(self):
        for data in self.datas:
            if self.orders.get(data):
                self.manage_position(data)
                continue

            stoch = self.stochastic[data]
            
            try:
                if not self.getposition(data):
                    if len(data) < 6 or not stoch[0]:
                        continue
                        
                    volume_increase = (data.volume[0] / self.volume_ma[data][0] 
                                     if self.volume_ma[data][0] else 0)
                    
                    if (stoch.percK[0] < self.p.oversold and
                        stoch.percD[0] < self.p.oversold and
                        data.close[0] > self.sma[data][0] and
                        volume_increase > self.p.volume_factor):
                        
                        stop_price = data.close[0] - self.atr[data][0] * 1.5
                        size = self.calculate_position_size(data, stop_price)
                        
                        if size > 0:
                            self.orders[data] = self.buy(data=data, size=size)
                            self.stops[data] = stop_price
                            self.targets[data] = data.close[0] + (data.close[0] - stop_price) * self.p.profit_target

                elif self.getposition(data):
                    if (stoch.percK[0] > self.p.overbought and
                        stoch.percD[0] > self.p.overbought):
                        self.orders[data] = self.close(data=data)
                        
            except Exception as e:
                print(f'Error in next() for {data._name}: {str(e)}')
                continue

    def manage_position(self, data):
        """Manage open positions with stops and targets"""
        if not self.getposition(data):
            return

        try:
            current_price = data.close[0]
            
            if current_price < self.stops.get(data, 0):
                self.orders[data] = self.close(data=data)
                return

            if current_price >= self.targets.get(data, float('inf')):
                self.orders[data] = self.close(data=data)
                return
                
        except Exception as e:
            print(f'Error in manage_position() for {data._name}: {str(e)}')

    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            self.orders[order.data] = None
            
            if order.status == order.Completed and not order.isbuy():
                self.stops.pop(order.data, None)
                self.targets.pop(order.data, None)
                
            if order.status == order.Completed:
                action = 'BUY' if order.isbuy() else 'SELL'
                print(f'{action} EXECUTED, Price: {order.executed.price:.2f}, Size: {order.executed.size}')
            elif order.status == order.Canceled:
                print('Order Canceled')
            elif order.status == order.Margin:
                print('Order Margin')