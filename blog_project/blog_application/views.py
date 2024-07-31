from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404
from django.http import JsonResponse
from django.contrib.auth import login as auth_login
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.db.models import F, Count
from django.contrib.postgres.search import SearchQuery, SearchRank, TrigramSimilarity
from django.conf import settings
from .models import BlogUser, BlogPost, Tag, Like
import json

def signup_page(request):
    return render(request,'signup.html')

def blog(request):
    return render(request,'blog.html')


@csrf_exempt
def SignUpApiView(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('signup-email')
            password = data.get('signup-password')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'invalid json data.'}, status=400)

        if not email or not password:
            return JsonResponse({'error': 'email and password are required.'}, status=400)

        if BlogUser.objects.filter(email=email).exists():
            return JsonResponse({'error': 'email is already taken.'}, status=400)

        try:
            user = BlogUser(email=email, password=make_password(password))
            user.save()
            auth_login(request, user)
            return JsonResponse({'message': 'user created successfully.'}, status=201)
        except Exception as e:
            return JsonResponse({'error': f'error creating user: {str(e)}'}, status=400)

    return JsonResponse({'error': 'invalid request method.'}, status=405)

@csrf_exempt
def LoginApiView(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('login-email')
            password = data.get('login-password')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'invalid json data.'}, status=400)

        if not email or not password:
            return JsonResponse({'error': 'email and password are required.'}, status=400)

        try:
            user = BlogUser.objects.get(email=email)
        except BlogUser.DoesNotExist:
            return JsonResponse({'error': 'invalid email or password.'}, status=400)

        if check_password(password, user.password):
            auth_login(request, user)
            return JsonResponse({'message': 'login successful.'}, status=200)
        else:
            return JsonResponse({'error': 'invalid email or password.'}, status=400)

    return JsonResponse({'error': 'invalid request method.'}, status=405)



@login_required
def blog_list(request):
    page_number = request.GET.get('page', 1)

    try:
        posts = BlogPost.objects.all()
        paginator = Paginator(posts, 5)
        page_obj = paginator.get_page(page_number)
        
        post_ids = [post.id for post in page_obj.object_list]
        
        likes = Like.objects.filter(post__id__in=post_ids).values('post_id').annotate(count=Count('id'))
        user_likes = Like.objects.filter(post__id__in=post_ids, user=request.user).values_list('post_id', flat=True)
        
        posts_data = []
        for post in page_obj.object_list:
            post_data = {
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'created_at': post.created_at,
                'likes': next((like['count'] for like in likes if like['post_id'] == post.id), 0),
                'liked': post.id in user_likes
            }
            posts_data.append(post_data)

        response_data = {
            'posts': posts_data,
            'page': page_obj.number,
            'num_pages': paginator.num_pages,
            'total_posts': paginator.count,
        }
        return JsonResponse(response_data, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def search_blogs_by_title(request):
    if request.method == 'GET':
        query = request.GET.get('query', '').strip()
        if query:
            posts = BlogPost.objects.filter(
                title__icontains=query
            ) | BlogPost.objects.filter(
                content__icontains=query
            )
            posts_data = list(posts.values('id', 'title', 'content', 'created_at'))
            return JsonResponse({'posts': posts_data})
        else:
            return JsonResponse({'error': 'query parameter is required.'}, status=400)
    return JsonResponse({'error': 'invalid request method.'}, status=405)


def blog_detail(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    return render(request, 'blog-desc.html', {'post': post})



@login_required
def like_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if request.method == 'POST':
        try:
            like, created = Like.objects.get_or_create(post=post, user=request.user)
            if created:
                return JsonResponse({'message': 'post liked successfully.'}, status=200)
            else:
                like.delete()
                return JsonResponse({'message': 'post disliked successfully.'}, status=200)
        except Exception as e:
            return JsonResponse({'error': f'an error occurred: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'invalid request method.'}, status=405)


@csrf_exempt
def share_blog(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        comments = request.POST.get('comments')
        post_title = request.POST.get('post_title')
        
        if not name or not email or not post_title:
            return JsonResponse({'error': 'name, email, and post title are required.'}, status=400)

        subject = f"Check out this blog post: {post_title}"
        message = f"Post Title: {post_title}\n\nComments:\n{comments}\n\nShared by: {name}\n\nShared via My Blog."
        from_email = settings.DEFAULT_FROM_EMAIL
        
        try:
            send_mail(subject, message, from_email, [email])
            return redirect('home')
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'invalid request method.'}, status=405)


@login_required
def is_liked(request, post_id):
    try:
        post = BlogPost.objects.get(id=post_id)
        liked = Like.objects.filter(post=post, user=request.user).exists()
        return JsonResponse({'liked': liked}, status=200)
    except BlogPost.DoesNotExist:
        return JsonResponse({'error': 'post not found'}, status=404)


