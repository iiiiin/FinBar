from django.db import models

# Create your models here.


class Stock(models.Model):
    stock_code = models.CharField(max_length=6)
    stock_name = models.CharField(max_length=100)
    # stock_name_short = models.CharField(max_length=100)
    stock_name_en = models.CharField(max_length=100)
    # 상장일 (유용한 보조 지표)
    first_trade_date = models.DateField()
    # 시장 구분 ( 중요도  : 상 )
    market = models.CharField(max_length=50)
    # 증권 구분 ( 중요도  : 중 )
    security_type = models.CharField(max_length=20)
    # 소속부  ( 중요도  : 중 )
    market_division = models.CharField(max_length=20)
    # 주식종류 ( 중요도  : 상 )
    stock_type = models.CharField(max_length=20)
    # 액면가 ( 중요도  : 하 )
    face_value = models.FloatField(null=True, blank=True, help_text="액면가 (무액면은 null)")
    #  상장주식수 ( 중요도  : 상 )
    listed_shares = models.BigIntegerField()
