from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ActivateUserView, LogoutView, UserProfileView, AdminUserViewSet

from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'admin/users', AdminUserViewSet, basename='admin-users')


urlpatterns = [
    path('activate/<uid>/<token>/', ActivateUserView.as_view(), name='activate'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)