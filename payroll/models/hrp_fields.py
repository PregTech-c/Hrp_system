from django.db import models
from decimal import Decimal

class CurrencyField(models.DecimalField):
    
#    __metaclass__ = models.SubfieldBase
    def __init__(self, verbose_name=None, name=None, **kwargs):
        max_digits = kwargs.pop('max_digits', 16)
        decimal_places = kwargs.pop('decimal_places', 2)
        default = kwargs.pop('default', Decimal('0.0'))
        super(CurrencyField, self).__init__(
            name=name,
            verbose_name=verbose_name,
            max_digits=max_digits,
            decimal_places=decimal_places,
            default=default
        )
    
    def to_python(self, value):
        try:
            return super(CurrencyField, self).to_python(
                value).quantize(Decimal("0.01"))
        except AttributeError:
           return None
