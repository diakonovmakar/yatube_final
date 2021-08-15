from django.urls import path

from . import views

app_name = 'post'
urlpatterns = [
    path('', views.index, name='index'),
    path("follow/", views.follow_index, name="follow_index"),
    path('new/', views.post_create, name='post_create'),
    path('<username>/', views.profile, name='profile'),
    path('<username>/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('<username>/<int:post_id>/', views.post_detail, name='post_detail'),
    path(
        "<username>/<int:post_id>/comment",
        views.add_comment,
        name="add_comment"),
    path("<username>/follow/", views.profile_follow, name="profile_follow"),
    path(
        "<username>/unfollow/",
        views.profile_unfollow,
        name="profile_unfollow"),
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
]
