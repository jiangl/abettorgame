from django import template
from maingame.models import UserGroupRole
from maingame.utils.enums import UserRoles, StandardEventStages

register = template.Library()

@register.filter(name='admin_group')
def check_group_admin(user, group):
    try:
        usergrouprole = UserGroupRole.objects.get(user=user.id, group=group)
        role_id = usergrouprole.role.id
        return (role_id == UserRoles.ADMIN.value)
    except:
        return False

@register.simple_tag
def match_eventstage(event, stage):
    if not event.current_stage:
        return False
    else:
        return event.current_stage.id is StandardEventStages[stage].value