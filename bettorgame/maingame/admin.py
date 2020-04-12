from django.contrib import admin
from .models import User, Group, Event, UserGroupRole, UserEventRole, Bet, BetOption, Placement, Result, EventType, StatusType, UserRole

# Register your models here.
admin.site.register(User)
admin.site.register(Group)
admin.site.register(Event)
admin.site.register(UserGroupRole)
admin.site.register(UserEventRole)
admin.site.register(Bet)
admin.site.register(BetOption)
admin.site.register(Placement)
admin.site.register(Result)
admin.site.register(EventType)
admin.site.register(StatusType)
admin.site.register(UserRole)

