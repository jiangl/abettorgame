from maingame.models import Group, Event
from django.contrib.auth.models import User

def add_user_to_groupevent(user_id, group_id, event_id):
    try:
        group = Group.objects.get(id=group_id)
        event = Event.objects.get(id=event_id)
        group.players.add(user_id)
        event.players.add(user_id)
        group.save()
        event.save()
    except:
        raise