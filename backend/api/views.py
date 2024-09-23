from django.shortcuts import render
from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.db.models import Sum
# Restframework
from rest_framework import status
from rest_framework.decorators import api_view, APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime


import json
import random

from api import serializer as api_serializer
from api import models as api_models

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = api_serializer.MyTokenObtainPairSerializer
    
class RegisterView(generics.CreateAPIView): 
    queryset = api_models.User.objects.all()

    permission_classes = (AllowAny,)

    serializer_class = api_serializer.RegisterSerializer
    
class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes= [AllowAny]
    serializer_class=api_serializer.ProfileSerializer
    
    def get_object(self):
        user_id = self.kwargs['user_id']

        user = api_models.User.objects.get(id=user_id)
        profile = api_models.Profile.objects.get(user=user)
        return profile

class CategoryListAPIView(generics.ListAPIView):
    serializer_class= api_serializer.CategorySerializer
    permission_classes =[AllowAny]
    def get_queryset(self):
        return api_models.Category.objects.all()
    
class BlogCategoryListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.BlogSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        category_slug = self.kwargs['category_slug'] 
        category = api_models.Category.objects.get(slug=category_slug)
        return api_models.Blog.objects.filter(category=category, status="Active")
    
class BlogListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.BlogSerializer
    permission_classes= [AllowAny]
    def get_queryset(self):
        return api_models.Blog.objects.filter(status="Active")
    
class BlogDetailAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.BlogSerializer
    permission_classes=[AllowAny]
    def get_object(self):
        slug = self.kwargs['slug']
        blog = api_models.Blog.objects.get(slug=slug,status="Active")
        blog.view += 1
        blog.save()
        return blog
    
class LikeBlogAPIView(APIView):
      @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'blog_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            },
        ),
        )
      def post(self,request):
        user_id = request.data['user_id']
        blog_id = request.data['blog_id']
        
        user = api_models.User.objects.get(id=user_id)
        blog = api_models.Blog.objects.get(id=blog_id)
        if user in blog.likes.all():
            blog.likes.remove(user)
            return Response({"message":"Disliked"},status=status.HTTP_200_OK)
        else:
            blog.likes.add(user)
            api_models.Notification.objects.create(
                user=blog.user,
                blog=blog,
                type="Like",
            )
            return Response({"message": "Post Liked"}, status=status.HTTP_201_CREATED)
        
class BlogCommentAPIView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'blog_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'comment': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    )
    def post(self, request):
        blog_id = request.data.get('blog_id')
        name = request.data.get('name')
        email = request.data.get('email')
        comment_text = request.data.get('comment')

        blog = api_models.Blog.objects.get(id=blog_id)

        # Assign user if logged in, else None
        user = request.user if request.user.is_authenticated else None

        # Create the comment
        api_models.Comment.objects.create(
            blog=blog,
            name=name,
            email=email,
            comment=comment_text,
            user=user  # Save user if authenticated, else None
        )

        # Create a notification for the blog owner
        api_models.Notification.objects.create(
            user=blog.user,
            blog=blog,
            type="Comment",
        )

        return Response({"message": "Commented"}, status=status.HTTP_201_CREATED)


class BookmarkBlogAPIView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'blog_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            },
        ),
        )
    def post(self,request):
        user_id = request.data['user_id']
        blog_id = request.data['blog_id']
        
        user = api_models.User.objects.get(id=user_id)
        blog = api_models.Blog.objects.get(id=blog_id)
        bookmark = api_models.Bookmark.objects.filter(blog=blog,user=user).first()
        if bookmark:
            bookmark.delete()
            return Response({"message":"Post UnBookmarked"},status=status.HTTP_200_OK)
        else:
            api_models.Bookmark.objects.create(
                user = user,
                blog= blog
            )
            api_models.Notification.objects.create(
            user=blog.user,
            blog=blog,
            type="Bookmark",
        )
            return Response({"message": "Bookmark added"}, status=status.HTTP_201_CREATED)


class DashboardStats(generics.ListAPIView):
    serializer_class = api_serializer.AuthorSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = api_models.User.objects.get(id=user_id)

        views = api_models.Blog.objects.filter(user=user).aggregate(view=Sum("view"))['view']
        posts = api_models.Blog.objects.filter(user=user).count()
        likes = api_models.Blog.objects.filter(user=user).aggregate(total_likes=Sum("likes"))['total_likes']
        bookmarks = api_models.Bookmark.objects.all().count()

        return [{
            "views": views,
            "posts": posts,
            "likes": likes,
            "bookmarks": bookmarks,
        }]
    
    def list(self, request, *args, **kwargs):
        querset = self.get_queryset()
        serializer = self.get_serializer(querset, many=True)
        return Response(serializer.data)

class DashboardPostLists(generics.ListAPIView):
    serializer_class = api_serializer.BlogSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = api_models.User.objects.get(id=user_id)

        return api_models.Blog.objects.filter(user=user).order_by("-id")
    
class DashboardCommentLists(generics.ListAPIView):
    serializer_class = api_serializer.CommentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return api_models.Comment.objects.all()

class DashboardNotificationLists(generics.ListAPIView):
    serializer_class = api_serializer.NotificationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = api_models.User.objects.get(id=user_id)

        return api_models.Notification.objects.filter(seen=False, user=user)
    
class DashboardMarkNotiSeenAPIView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'noti_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            },
        ),
    )
    def post(self, request):
        noti_id = request.data['noti_id']
        noti = api_models.Notification.objects.get(id=noti_id)

        noti.seen = True
        noti.save()

        return Response({"message": "Noti Marked As Seen"}, status=status.HTTP_200_OK)
    
class DashboardPostCommentAPIView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'comment_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'reply': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    )
    def post(self, request):
        comment_id = request.data['comment_id']
        reply = request.data['reply']

        comment = api_models.Comment.objects.get(id=comment_id)
        comment.reply = reply
        comment.save()

        return Response({"message": "Comment Response Sent"}, status=status.HTTP_201_CREATED)
    