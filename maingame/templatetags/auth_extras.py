from django import template
from maingame.models import UserGroupRole
from maingame.utils.enums import UserRoles

register = template.Library()

@register.filter(name='admin_group')
def check_group_admin(user, group):
    role = UserGroupRole.objects.get(user_id=user.id, group_id=group)
    is_admin = (role == UserRoles.ADMIN)
    return is_admin