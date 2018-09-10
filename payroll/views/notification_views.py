from django.views.generic import TemplateView

class NotificationView(TemplateView):
    template_name = 'payroll/notifications.html'    
#    template_name = 'notifications/all.html'