from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.urls.conf import include

from . import views

router = DefaultRouter()
router.register(r'api/v1/posts/(?P<post_id>[0-9]+)/comments',
                views.CommentViewSet)
router.register(r'api/v1/users/(?P<username>\w+)', views.UserViewSet,
                'UsersModel')
router.register(r'api/v1/users', views.UserViewSet, 'UsersModel-1')

# router.register(r'api/v1/users', views.UserViewSet, 'UsersList')
# router.register(r'api/v1/posts', views.PostViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/v1/posts/<int:pk>/',
         views.PostRetrieveUpdateDestroyAPIView.as_view(),
         name='api_posts_detail'),
    path('api/v1/posts/',
         views.PostListCreateAPIView.as_view(),
         name='api_posts'),
    path('api/v1/follow/', views.FollowListCreateAPIView.as_view()),
    path('api/v1/token/',
         TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('api/v1/token/refresh/',
         TokenRefreshView.as_view(),
         name='token_refresh'),
    # path('api/v1/token-auth/', aviews.obtain_auth_token),
    # path('api/v1/users/<str:username>/', views.UserList.as_view()),
]

urlpatterns += [path('api/v1/group/', views.GroupListCreateAPIView.as_view())]
