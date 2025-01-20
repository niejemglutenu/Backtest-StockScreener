from django.db import models

# model reprezentujący tabele z danymi giełdowymi(data, nazwa symbolu), dane OHCLV + VWAP)
class StockData(models.Model):
    ticker = models.CharField(max_length=10)  
    timestamp = models.DateTimeField()       
    open = models.FloatField()         
    high = models.FloatField()         
    low = models.FloatField()          
    close = models.FloatField()        
    volume = models.BigIntegerField()  
    vwap = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f'{self.ticker} - {self.timestamp}'

    class Meta:
        indexes = [
            models.Index(fields=['timestamp', 'ticker']),  
        ]
        unique_together = ('ticker', 'timestamp')  

