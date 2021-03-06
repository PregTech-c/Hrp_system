from django import template
from django.conf import settings
import locale
#locale.setlocale(locale.LC_ALL, '')
register = template.Library()


@register.filter()
def currency1(value):
    return locale.currency(value, grouping=True)


register = template.Library()

@register.filter()
def currency(value):
    symbol = '$'
    thousand_sep = ''
    decimal_sep = ''
    # try to use settings if set
    try:
        symbol = settings.CURRENCY_SYMBOL
    except AttributeError:
        pass

    try:
        thousand_sep = settings.THOUSAND_SEPARATOR
        decimal_sep = settings.DECIMAL_SEPARATOR
    except AttributeError:
        thousand_sep = ','
        decimal_sep = '.'

    intstr = str(int(value))
    f = lambda x, n, acc=[]: f(x[:-n], n, [(x[-n:])]+acc) if x else acc
    intpart = thousand_sep.join(f(intstr, 3))
    return "%s%s%s%s" % (symbol, intpart, decimal_sep, ("%0.2f" % value)[-2:])

@register.filter
def get_allw_ded_totals(list, arg):
    for item in list:
        try:
            if arg == item['allowance_type__name']:
                return int(item['sum'])
        except:
            return 0
    return 0
#    return sum(d for d in list)