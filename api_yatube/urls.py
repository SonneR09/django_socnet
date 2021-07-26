from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as aviews
from django.urls.conf import include

from . import views

router = DefaultRouter()
router.register(r'api/v1/posts/(?P<post_id>[0-9]+)/comments', views.CommentViewSet)
router.register('api/v1/users', views.UserViewSet)
router.register(r'api/v1/posts', views.PostViewSet)

urlpatterns = [
    # path('api/v1/posts/<int:id>', views.APIPostDetail.as_view(),
    #      name='api_posts_detail'),
    # path('api/v1/posts/', views.api_posts, name='api_posts'),
    # path('api/v1/token-auth/', aviews.obtain_auth_token),
    path('', include(router.urls)),
]