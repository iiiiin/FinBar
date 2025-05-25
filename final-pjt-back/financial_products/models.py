from django.db import models

# Create your models here.


class Stock(models.Model):
    stock_code = models.CharField(max_length=6, unique=True)
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
    face_value = models.FloatField(
        null=True, blank=True, help_text="액면가 (무액면은 null)"
    )
    #  상장주식수 ( 중요도  : 상 )
    listed_shares = models.BigIntegerField()


class DepositProduct(models.Model):
    top_fin_grp_no = models.CharField(max_length=100)
    fin_co_no = models.CharField(max_length=200)
    kor_co_nm = models.CharField(max_length=200)
    fin_prdt_cd = models.CharField(max_length=200)
    fin_prdt_nm = models.CharField(max_length=200)
    join_way = models.CharField(max_length=200, null=True)
    mtrt_int = models.TextField(max_length=20000)
    spcl_cnd = models.TextField(max_length=20000)
    join_deny = models.CharField(max_length=200)
    join_member = models.CharField(max_length=200)
    etc_note = models.TextField(max_length=20000)
    max_limit = models.BigIntegerField(null=True)
    dcls_strt_day = models.DateField()
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["fin_prdt_cd", "fin_co_no"], name="unique_deposit_product"
            )
        ]



class DepositProductOptions(models.Model):
    deposit_product = models.ForeignKey(
        DepositProduct, on_delete=models.CASCADE
    )
    fin_co_no = models.CharField(max_length=200)
    intr_rate_type_nm = models.CharField(max_length=200)
    save_trm = models.CharField(max_length=200)
    intr_rate = models.FloatField(null=True)
    intr_rate2 = models.FloatField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["fin_co_no","deposit_product", "intr_rate_type_nm", "save_trm"], name="unique_option_deposit"
            )
        ]


class SavingProduct(models.Model):
    top_fin_grp_no = models.CharField(max_length=100)
    fin_co_no = models.CharField(max_length=200)
    kor_co_nm = models.CharField(max_length=200)
    fin_prdt_cd = models.CharField(max_length=200)
    fin_prdt_nm = models.CharField(max_length=200)
    join_way = models.CharField(max_length=200, null=True)
    mtrt_int = models.TextField(max_length=20000)
    spcl_cnd = models.TextField(max_length=20000)
    join_deny = models.CharField(max_length=200)
    join_member = models.CharField(max_length=200)
    etc_note = models.TextField(max_length=20000)
    max_limit = models.BigIntegerField(null=True)
    dcls_strt_day = models.DateField()

    class Meta:
            constraints = [
                models.UniqueConstraint(
                    fields=["fin_prdt_cd", "fin_co_no"], name="unique_saving_product"
                )
            ]

class SavingProductOptions(models.Model):
    saving_product = models.ForeignKey(
        SavingProduct, on_delete=models.CASCADE
    )
    fin_co_no = models.CharField(max_length=200)
    intr_rate_type_nm = models.CharField(max_length=200)
    rsrv_type_nm = models.CharField(max_length=200)
    save_trm = models.CharField(max_length=200)
    intr_rate = models.FloatField(null=True)
    intr_rate2 = models.FloatField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["fin_co_no","saving_product", "intr_rate_type_nm", "save_trm", "rsrv_type_nm"], name="unique_option_saving"
            )
        ]
