from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib import admin


urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('user.urls')), 
    path('student/', include('students.urls')),
    path('todo/', include('todo.urls')),
    path('shop/', include('shop.urls')),
    path('tasks/', include('tasks.urls')),
    path('tracker/', include('tracker.urls')),
    # JWT
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('api/auth/register/', include('shop.auth_urls')),  # or add the view mapping

]








