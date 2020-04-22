from django import template
from maingame.models import UserGroupRole
from maingame.utils.enums import UserRoles

register = template.Library()

@register.filter(name='admin_group')
def check_group_admin(user, group):
    try:
        role = UserGroupRole.objects.filter(user_id=user.id, group_id=group)
        return (role == UserRoles.ADMIN)
    except:
        return False