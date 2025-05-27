from django.contrib import admin
from .models import (
    Stock,
    DepositProduct, DepositProductOptions,
    SavingProduct,  SavingProductOptions,
    DepositCompany, SavingCompany,
)

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("stock_code", "stock_name", "market", "listed_shares")

@admin.register(DepositProduct)
class DepositProductAdmin(admin.ModelAdmin):
    list_display = ("kor_co_nm", "fin_prdt_nm", "dcls_strt_day", "risk_level")

@admin.register(SavingProduct)
class SavingProductAdmin(admin.ModelAdmin):
    list_display = ("kor_co_nm", "fin_prdt_nm", "dcls_strt_day", "risk_level")

@admin.register(DepositCompany)
class DepositCompanyAdmin(admin.ModelAdmin):
    list_display = ("kor_co_nm", "top_fin_grp_no")

@admin.register(SavingCompany)
class SavingCompanyAdmin(admin.ModelAdmin):
    list_display = ("kor_co_nm", "top_fin_grp_no")


# admin.py 에 이어서

from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from html import unescape

User = get_user_model()

def send_rate_change_email(product, options_queryset, subject_prefix="금리 변경 알림"):
    # 1) 모든 활성 유저 이메일 수집
    recipient_list = list(
        User.objects.filter(is_active=True)
            .exclude(email="")  # 이메일 없는 사람 제외
            .values_list("email", flat=True)
    )
    if not recipient_list:
        return

    # 2) 메일 제목
    subject = f"[{subject_prefix}] {product.fin_prdt_nm}"

    # 3) 본문: 옵션 레코드 전체를 텍스트로 나열
    lines = [
        f"{opt.intr_rate_type_nm} / 기간 {opt.save_trm}개월 → 금리1: {opt.intr_rate}, 금리2: {opt.intr_rate2}"
        for opt in options_queryset
    ]
    message = "\n".join(lines)

    # 4) 메일 전송 (settings.EMAIL_HOST_* 설정 필요)
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
    )

@admin.register(DepositProductOptions)
class DepositProductOptionsAdmin(admin.ModelAdmin):
    list_display = ("deposit_product", "intr_rate_type_nm", "save_trm", "intr_rate", "intr_rate2")

    def save_model(self, request, obj, form, change):
        # 수정(changed) 상태일 때만
        if change:
            # DB 에 있던 원본 가져오기
            old = type(obj).objects.get(pk=obj.pk)
            # 금리 필드가 하나라도 다르면 이메일 발송
            if (
                old.intr_rate  != obj.intr_rate
                or old.intr_rate2 != obj.intr_rate2
            ):
                super().save_model(request, obj, form, change)
                # 해당 상품의 모든 옵션 레코드를 가져와서
                all_opts = obj.deposit_product.depositproductoptions.all()
                send_rate_change_email(obj.deposit_product, all_opts, subject_prefix="예금 금리 변경")
                return
        super().save_model(request, obj, form, change)


@admin.register(SavingProductOptions)
class SavingProductOptionsAdmin(admin.ModelAdmin):
    list_display = ("saving_product", "intr_rate_type_nm", "save_trm", "intr_rate", "intr_rate2")

    def save_model(self, request, obj, form, change):
        if change:
            old = type(obj).objects.get(pk=obj.pk)
            if (
                old.intr_rate  != obj.intr_rate
                or old.intr_rate2 != obj.intr_rate2
            ):
                super().save_model(request, obj, form, change)
                all_opts = obj.saving_product.savingproductoptions.all()
                send_rate_change_email(obj.saving_product, all_opts, subject_prefix="적금 금리 변경")
                return
        super().save_model(request, obj, form, change)
