from django.conf import settings
from appconf import AppConf
from django.utils.translation import ugettext as _

class AxessProConf(AppConf):
    
    REQUEST_SENT_MESSAGE = _("""Hello {},

Your leave request has been submitted for review.

Leave Details: {}.

==
HRP
""")
    REQUEST_RECEIVED_MESSAGE = _("""Hello {approver},

{employee} has requested for leave days. 

Details: {leave_details}

Please login to the HRP portal and review.

==
HRP
""")
    