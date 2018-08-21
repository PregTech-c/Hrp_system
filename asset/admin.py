from django.contrib import admin

from .models import Asset, Category, IdType

#class HrpAdminSite(admin.AdminSite):
#    site_header = "HRP Administration"
#admin_site = MyAdminSite()

admin.site.site_header = "HRP Administration"
admin.site.index_title = "Modules"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    class Meta:
        exclude = ()
    list_display = ('name', 'description')

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    class Meta:
        exclude = ()
    list_display = ('category', 'id_number', 'description')

@admin.register(IdType)
class CategoryAdmin(admin.ModelAdmin):
    class Meta:
        exclude = ()
    list_display = ('description',)
