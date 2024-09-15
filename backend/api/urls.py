from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from api import views as api_views
urlpatterns = [
     path('user/token/', api_views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/register/', api_views.RegisterView.as_view(), name='auth_register'),
    path('user/profile/<user_id>/', api_views.ProfileView.as_view(), name='user_profile'),
    #blog endpoint
    path('blog/category/list',api_views.CategoryListAPIView.as_view()),
    path('blog/category/blogs/<category_slug>/', api_views.BlogCategoryListAPIView.as_view()),    
]
