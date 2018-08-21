from django import forms
from django.contrib.auth.models import User

from .models import *
    
class UserModelChoiceField(forms.ModelChoiceField):
    
    def __init__(self, queryset=None, empty_label=None, required=True):
        
        super(UserModelChoiceField, self).__init__(queryset=User.objects.none())
        self.queryset = User.objects.filter(profile__isnull=False)
        self.empty_label = empty_label
        self.required = required
        
    def label_from_instance(self, obj):
        return obj.profile.get_fullname()

class AssetIssuanceSearchForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(), 
        empty_label='-- All --',
        required=False)
    employee = UserModelChoiceField(
        empty_label='-- All --',
        required=False)
    issue_status = forms.ChoiceField(
        choices=(
            (0, '-- Any --'), 
            (1, 'Issued'), 
            (2, 'Available')
            )
        )
class AssetIssuanceForm(forms.ModelForm):
    class Meta:
        model = AssetIssuance
        exclude = ('returned_date', 'return_comment')
        widgets = {
            'asset': forms.HiddenInput()
        }
    employee = UserModelChoiceField()
    
class AssetReturnForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AssetReturnForm, self).__init__(*args, **kwargs)
        self.fields['returned_date'].widget = forms.HiddenInput()
        self.fields['asset'].widget = forms.HiddenInput()
        self.fields['returned_date'].widget = forms.HiddenInput()
        
    class Meta:
        model = AssetIssuance
        exclude = ()
        widgets = {
#            'return_date': forms.HiddenInput(),
            'return_comment': forms.Textarea(attrs={'cols': 30, 'rows': 4}),
            'asset': forms.HiddenInput(),
            'employee': forms.HiddenInput(),
        }
        
class AssetAllocationFormOld(forms.Form):
    def __init__(self, *args, **kwargs):
        cat_id = kwargs.pop('category')
        super(AssetAllocationForm, self).__init__(*args, **kwargs)
        self.fields['asset'].queryset = Asset.objects.filter(
            category__id=cat_id if cat_id else 1)

        q = Category.objects.all()
        self.fields['category'].queryset = q
        self.fields['category'].initial = Category.objects.get(pk=cat_id)
        self.fields['category'].widget.attrs = {
            'onChange': "post({}, {});".format(
                '"/asset/allocation/new/"',
                {'from_post': 1}
            )
        }
        
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        empty_label = None
    )
    asset = forms.ModelChoiceField(
        queryset = Asset.objects.none()
    )
    
    class Media:
        js = ('js/hrp.js', )