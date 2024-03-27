from django.contrib import admin
from .models import Image,AuctionItem,Bid,User

# Register your models here.
admin.site.register(User)
admin.site.register(Image)
# admin.site.register(Item)
# admin.site.register(Auction)
admin.site.register(AuctionItem)
admin.site.register(Bid)
