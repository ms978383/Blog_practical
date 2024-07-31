from django.urls import path
from .views import *

urlpatterns = [
    path('', signup_page, name='signup_page'),
    path('api/signup/', SignUpApiView, name='api_signup'),
    path('api/login/', LoginApiView, name='api_login'),
    path('blogs/', blog_list, name='blog_list'),
    path('blogs/<int:pk>/like/', like_post, name='like_post'),
    path('home/',blog,name="home"),
    path('share_blog', share_blog, name='share_blog'),
    path('blogs/<int:post_id>/is_liked/', is_liked, name='is_liked'),
    path('blogs/<int:post_id>/', blog_detail, name='blog_detail'),
    path('search/', search_blogs_by_title, name='search_blogs_by_title'),

    
    
]



