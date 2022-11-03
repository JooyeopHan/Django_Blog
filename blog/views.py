from django.shortcuts import render
from .models import Post
from django.views.generic import ListView, DetailView
# Create your views here.

## CBV 방식
## ListView 클래스를 상속해서 PostList 클래스 생성
## 간단하게 model = post 입력 하면 됌
class PostList(ListView):
    model = Post
    ordering = '-pk' # pk 내림차순
    #이름 바꾸는방법 (그냥 index.html을 post_list.html로 바꾸는걸로)
    # template_name = 'blog/post_list.html'
class PostDetail(DetailView):
    model = Post


## FBV 방식
# def index(request):
#
#     posts = Post.objects.all().order_by('-pk')
#
#     return render(
#         request,
#         'blog/post_list.html',
#         {
#             'posts' : posts
#
#         }
#
#     )
#
# def single_post_page(request, pk):
#     post = Post.objects.get(pk=pk)
#
#     return render(
#         request,
#         'blog/post_detail.html',
#         {
#             'post' : post
#
#         }
#
#     )