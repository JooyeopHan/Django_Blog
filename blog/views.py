from django.shortcuts import render, redirect
from .models import Post, Category, Tag
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify
from .forms import CommentForm

# pk가 없는경우에 오류발생시키기
from django.shortcuts import get_object_or_404

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
        context['comment_form'] = CommentForm # forms.py 에서 생성하였언 CommentForm 클래스를 PostDetail에 넘겨줌
        return context

class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']

    def test_func(self): # 이 페이지에 접근하는 사용자를 제한 하는 역할
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        current_user = self.request.user # 방문자를 의미한다.
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
            # 로그인 상태인지 확인 (is_authenticated : property)
            form.instance.author = current_user
            response = super(PostCreate,self).form_valid(form)

            tags_str = self.request.POST.get('tags_str')
            if tags_str:
                tags_str = tags_str.strip()
                tags_str = tags_str.replace(',', ';')
                tags_list = tags_str.split(';')

                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)

                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)

            # return super(PostCreate, self).form_valid(form)
            return response

        else: # 아니라면 redirect 함수를 사용해서 '/blog/'경로로 보내기
            return redirect('/blog/')


class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category', 'tags']

    # CreateView 와 UpdateView는 모델명 뒤에 _form_html이 붙은템플릿을 기본적으로 사용
    template_name = 'blog/post_update_form.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            # get_object() = Post.objects.get(pk=pk)
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

    # 기존의 있었던 태그들을 저장

    def get_context_data(self, **kwargs):
        context = super(PostUpdate, self).get_context_data()
        if self.object.tags.exists():
            tags_str_list = list()
            for t in self.object.tags.all():
                tags_str_list.append(t.name)
            context['tags_str_default'] = '; '.join(tags_str_list)

        return context

    def form_valid(self, form):
        response = super(PostUpdate,self).form_valid(form)
        self.object.tags.clear() # 삭제 기능을 구현하지 않아서 들어가면 태그 초기화
        tags_str = self.request.POST.get('tags_str')

        if tags_str:
            tags_str = tags_str.strip()
            tags_str = tags_str.replace(',', ';')
            tags_list = tags_str.split(';')

            for t in tags_list:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(name=t)

                if is_tag_created:
                    tag.slug = slugify(t, allow_unicode=True)
                    tag.save()
                self.object.tags.add(tag)

        # return super(PostCreate, self).form_valid(form)
        return response


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

def new_comment(request, pk):
    if request.user.is_authenticated:

        # post = Post.objects.get(pk=pk) 을 써도되지만 해당하는 pk(포스트)가 없는경우 404 오류를 발생시키기 위함
        post = get_object_or_404(Post,pk=pk)

        if request.method == 'POST': # 요청 방식이 POST인 경우
            # 정상적으로 폼을 작성하고 OST방식으로 서버에 요청이 들어왔다면 POST 방식으로 들어온 정보를 CommenForm형식으로 가져옴
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False) # 바로저장하는 기능을 잠시 미루고 comment Insatace만 가져옴
                # 그 외의 pk로 가져오 Post, 로그인한 사용자 정보 를 추가해서 저장
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect(comment.get_absolute_url())

        else: # get 방식으로 요청할 경우 로컬/pk/new_comment로 리다이렉트 하는식으로 설정
            return redirect(post.get_absolute_url())

    else :
        raise PermissionDenied

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