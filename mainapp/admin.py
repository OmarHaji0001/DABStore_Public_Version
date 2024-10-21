from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

admin.site.register(Theme)


class UserAdmin(BaseUserAdmin):
    ordering = ('phone_number',)
    list_display = ('phone_number', 'first_name', 'last_name', 'is_staff','whatsapp')

    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'whatsapp')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser')}),
    )


admin.site.register(CustomUser, UserAdmin)

admin.site.register(Category)
admin.site.register(Product)

class UserProductOrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'total_price', 'order_date')
    readonly_fields = ('order_date', 'total_price')

    def total_price(self, obj):
        return obj.total_price

    total_price.short_description = 'Total Price (₪)'


admin.site.register(UserProductOrder, UserProductOrderAdmin)

admin.site.register(City)
admin.site.register(Orders)

admin.site.register(MultiImage)

