from django.contrib import admin
from payroll.models import Position, Nationality, Currency
# Register your models here.

class NationalityAdmin(admin.ModelAdmin):
    list_display = ['name', 'country_code']
    
class PositionAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    pass

class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['name', 'symbol']
    
#admin.site.register(Position, PositionAdmin)
admin.site.register(Nationality, NationalityAdmin)
admin.site.register(Currency, CurrencyAdmin)
