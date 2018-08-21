__author__ = "Steven Kawuma <kawuma@gmail.com>"
__date__ = "Jan 10, 2017 12:51:55 PM"

from django.db.models.signals import post_save
from django.dispatch import receiver

from payroll.models import Payroll

@receiver(post_save, sender=Payroll)
def generate_payslips(sender, **kwargs):
    
    payroll = kwargs.get('instance')
    created = kwargs.get('created')
    
    if created:
        payroll.generate_payslips()
        
