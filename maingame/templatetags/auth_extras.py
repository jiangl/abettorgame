from django import template
from maingame.models import UserGroupRole
from maingame.utils.enums import UserRoles

register = template.Library()

@register.filter(name='admin_group')
def check_group_admin(user, group):
    try:
        usergrouprole = UserGroupRole.objects.filter(user=user.id, group=group)[0]
        role_name = usergrouprole.role.name
        return (role_name == UserRoles.ADMIN.value)
    except:
        return False