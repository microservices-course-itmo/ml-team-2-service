from django.contrib import admin
from .models import Wine, User, Review

# Register your models here.


class WineAdmin(admin.ModelAdmin):
    fields = ('internal_id', 'all_names')
    list_display = ('internal_id', 'all_names')
    list_filter = ('internal_id', 'all_names')


class UserAdmin(admin.ModelAdmin):
    fields = ('internal_id',)
    list_display = ('internal_id',)
    list_filter = ('internal_id',)


class ReviewAdmin(admin.ModelAdmin):
    fields = ('rating', 'variants', 'get_wine', 'get_user')
    list_display = ('rating', 'variants', 'get_wine', 'get_user')

    def get_wine(self, obj):
        return obj.wine.internal_id
    get_wine.admin_order_field = 'wine'
    get_wine.short_description = 'Wine internal id'

    def get_user(self, obj):
        return obj.user.internal_id
    get_user.admin_order_field = 'user'
    get_user.short_description = 'User internal id'

    list_filter = ('rating', 'variants', 'wine__internal_id', 'user__internal_id')


admin.site.register(Wine, WineAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Review, ReviewAdmin)
