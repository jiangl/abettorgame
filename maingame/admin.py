from django.contrib import admin
from maingame.models import User, Group, Event, UserGroupRole, UserEventRole, Bet, BetOption, Placement, EventResult, BetResult, EventType, StatusType, UserRole

# Model groups
class BetOptionInline(admin.TabularInline):
    model = BetOption
    extra = 2

class PlacementInline(admin.TabularInline):
    model = Placement

class BetResultInline(admin.TabularInline):
    model = BetResult

class BetAdmin(admin.ModelAdmin):
    inlines = [
       BetOptionInline,
       PlacementInline,
       BetResultInline
    ]

class UserEventRoleInline(admin.TabularInline):
    model = UserEventRole

class EventResultInline(admin.TabularInline):
    model = EventResult

class EventAdmin(admin.ModelAdmin):
    inlines = [
        UserEventRoleInline,
        EventResultInline
    ]

class UserGroupRoleInline(admin.TabularInline):
    model = UserGroupRole

class GroupAdmin(admin.ModelAdmin):
    inlines = [
        UserGroupRoleInline
    ]

class UserAdmin(admin.ModelAdmin):
    inlines = [
        UserEventRoleInline,
        UserGroupRoleInline
    ]

class BetInline(admin.TabularInline):
    model = Bet

class StatusTypeAdmin(admin.ModelAdmin):
    inlines = [
        BetInline
    ]

class EventInline(admin.TabularInline):
    model = Event

class EventTypeAdmin(admin.ModelAdmin):
    inlines = [
        EventInline
    ]

# Register models
admin.site.register(UserRole)
admin.site.register(User, UserAdmin)
admin.site.register(Bet, BetAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(StatusType, StatusTypeAdmin)
admin.site.register(EventType, EventTypeAdmin)

