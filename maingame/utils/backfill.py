from maingame.models import Group, Event, UserRole, UserGroupRole, UserEventRole
from maingame.utils.enums import UserRoles
from django.contrib.auth.models import User

def add_user_to_groupevent(user_id, group_id, event_id):
    try:
        group = Group.objects.get(id=group_id)
        event = Event.objects.get(id=event_id)
        group.players.add(user_id)
        event.players.add(user_id)
        group.save()
        event.save()

        user_group_role = UserGroupRole.objects.filter(
          user_id=user_id, 
          group_id=group_id
          )
        
        user_event_role = UserEventRole.objects.filter(
          user_id=user_id, 
          event_id=event_id
          )

        if not user_group_role and not user_event_role:
            role_basic = UserRole.objects.get(id=UserRoles.BASIC.value)

            UserGroupRole.objects.create(
                user_id=user_id, 
                group_id=group_id,
                role=role_basic
            )
            
            UserEventRole.objects.create(
                user_id=user_id, 
                event_id=event_id,
                role=role_basic
            )

    except:
        raise