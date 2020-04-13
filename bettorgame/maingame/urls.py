from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('group-admin', views.group_admin, name='group_admin'),
    path('add-bets', views.add_bets, name='add_bets'),
    path('<int:group_id>/<int:event_id>/show-placements/', views.show_placements, name='show_placements'),
    path('leaderboard', views.leaderboard, name='leaderboard'),
]