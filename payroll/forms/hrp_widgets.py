__author__ = "Steven Kawuma <kawuma@gmail.com>"
__date__ = "Jan 4, 2017 6:32:31 PM"

from django.utils.safestring import mark_safe
from django.forms import CheckboxSelectMultiple, DateInput
from django.forms.utils import ErrorList

class PCheckboxSelectMultiple(CheckboxSelectMultiple):
    def render(self, *args, **kwargs):
        output = super(PCheckboxSelectMultiple, self).render(*args,**kwargs)
        return mark_safe(output.replace(u'<ul>', u'').replace(u'</ul>', u'').replace(u'<li>', u'').replace(u'</li>', u''))

class JQueryUIDatepickerWidget(DateInput):
    def __init__(self, **kwargs):
        super(DateInput, self).__init__(attrs={"size":10, "class": "dateinput"}, **kwargs)

    class Media:
#        css = {"all":("http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.6/themes/redmond/jquery-ui.css",)}
#        js = ("http://ajax.googleapis.com/ajax/libs/jquery/1.4.3/jquery.min.js",
#              "http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.6/jquery.min.js",)
#        css = {"all": ("/Users/steve/NetBeansProjects/Payroll/payroll/static/jquery-ui.css"),}
        js = ("js/jquery-1.3.2.min.js",)

class DivErrorList(ErrorList):
     def __str__(self):
         return self.as_divs()
     def as_divs(self):
         if not self: return u''
         return u'%s' % \
            ''.join([u'%s ' % e for e in self])
