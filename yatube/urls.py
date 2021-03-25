from django.contrib import admin
from django.urls import path, include
from django.contrib.flatpages import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('about/', include('django.contrib.flatpages.urls')),
    path('', include('posts.urls')),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls'))
]

urlpatterns += [
   path('about-author/', views.flatpage, {'url': '/about-author/'}, name='about'),
   path('about-spec/', views.flatpage, {'url': '/about-spec/'}, name='terms')
]