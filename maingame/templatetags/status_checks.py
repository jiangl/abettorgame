from django import template
from maingame.utils.enums import StatusType

register = template.Library()

@register.simple_tag
def match_bet_status(bet, status):
    if not bet.status:
        return False
    else:
        return bet.status.id is StatusType[status].value