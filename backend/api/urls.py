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
    path('blog/lists',api_views.BlogListAPIView.as_view()),
    path('blog/detail/<slug>',api_views.BlogDetailAPIView.as_view()), 
    path('blog/like-blog/',api_views.LikeBlogAPIView.as_view()),
    path('blog/comment-blog/',api_views.BlogCommentAPIView.as_view()),
    path('blog/bookmark-blog/',api_views.BookmarkBlogAPIView.as_view()),
    
    
    
    
    path('author/dashboard/stats/<user_id>/',api_views.DashboardStats.as_view()),
    path('author/dashboard/post-list/<user_id>/', api_views.DashboardPostLists.as_view()),
    path('author/dashboard/comment-list/', api_views.DashboardCommentLists.as_view()),
    path('author/dashboard/noti-list/<user_id>/', api_views.DashboardNotificationLists.as_view()),
    path('author/dashboard/noti-mark-seen/', api_views.DashboardMarkNotiSeenAPIView.as_view()),
    path('author/dashboard/reply-comment/', api_views.DashboardPostCommentAPIView.as_view()),
    # path('author/dashboard/post-create/', api_views.DashboardPostCreateAPIView.as_view()),
    # path('author/dashboard/post-detail/<user_id>/<post_id>/', api_views.DashboardPostEditAPIView.as_view()),
]
