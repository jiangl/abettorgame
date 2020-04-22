from django import template
from maingame.models import UserGroupRole
from maingame.utils.enums import UserRoles

register = template.Library()

@register.filter(name='admin_group')
def check_group_admin(user, group):
    try:
        usergrouprole = UserGroupRole.objects.filter(user=user.id, group=group)[0]
        role_id = usergrouprole.role.id
        return (role_id == UserRoles.ADMIN.value)
    except:
        return False