from django.shortcuts import render
from .models import Post, Category, Tag
from django.views.generic import ListView, DetailView
# Create your views here.

## CBV 방식
## ListView 클래스를 상속해서 PostList 클래스 생성
## 간단하게 model = post 입력 하면 됌
## ListView 나 클래스 View는 get_context_data()를 기본적으로 가지고 있다.

class PostList(ListView):
    model = Post
    ordering = '-pk' # pk 내림차순
    #이름 바꾸는방법 (그냥 index.html을 post_list.html로 바꾸는걸로)
    # template_name = 'blog/post_list.html'

    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()
        # 카테고리가 지정되지 않은 포스트의 개수를 세라
        context['no_category_post_count'] = Post.objects.filter(category = None).count()

        return context

class PostDetail(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        # 카테고리가 지정되지 않은 포스트의 개수를 세라
        context['no_category_post_count'] = Post.objects.filter(category = None).count()

        return context


## FBV 방식

def category_page(request, slug):

    if slug == 'no_category':
        category = '미분류'
        post_list = Post.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)
        post_list = Post.objects.filter(category=category)

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list' : post_list,
            'categories' : Category.objects.all(),
            'no_category_post_count' : Post.objects.filter(category=None).count(),
            'category' : category,
        }

    )

def tag_page(request, slug):

    tag = Tag.objects.get(slug=slug)
    post_list = tag.post_set.all()

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list' : post_list,
            'tag' : tag,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
        }

    )


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