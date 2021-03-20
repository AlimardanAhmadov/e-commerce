from django.contrib import admin
from .models import Profile, Address, WishListItem, SellerRequest, ApproveSellerEmail, Seller


admin.site.register(Profile)
admin.site.register(Address)
admin.site.register(WishListItem)
admin.site.register(SellerRequest)
admin.site.register(Seller)

def send_email(modeladmin, request, queryset):
    for newsletter in queryset:
        newsletter.send(request)

send_email.short_description = "Send approvement email to approved sellers"

class ApproveSellerEmailAdmin(admin.ModelAdmin):
    actions = [send_email]

admin.site.register(ApproveSellerEmail, ApproveSellerEmailAdmin)    