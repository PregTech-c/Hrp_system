from django.conf import settings

def global_settings(request):

    hrp_settings = getattr(settings, 'HRP')
    return {
        'COMPANY_NAME': hrp_settings['COMPANY']['NAME'],
        'HRP_SHORT_DATE_FORMAT': hrp_settings['HRP_SHORT_DATE_FORMAT']
    }

