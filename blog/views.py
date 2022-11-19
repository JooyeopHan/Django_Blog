from django.shortcuts import render, redirect
from .models import Post, Category, Tag, Comment
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
    paginate_by = 5 # 5 page씩 보여줌

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
    # form에서 형성될 field를 지정
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

# LoginRequiredMixin : 로그인 되어 있지 않은 상대로 CommentUpdate에 POST방식으로 정보를 보내는것을 방지하기 위함

class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm # Form.py 에서 만들어놨던 CommentForm을 form_class로 활용

    '''
    dispath() 의 역할
    
    
    dispatch()의 역할을 요약하면 request와 response 사이의 중개자 역할이라고 할 수 있다.
     간단히 말하면 HTTP 메서드에 기반한 request를 해석하는(GET인지 POST인지) 일을 담당한다.

    기본적으로 클라이언트가 url을 입력하면 URLConf를 통해 요청정보가 view에게 전달된다. 
    클래스뷰는 as_view()를 통해 전달되는데 여기서 dispatch() 메서드가 항상 자동으로 불러진다.

    이러한 dispatch의 성격때문에 궁극적으로는 특정 유형의 요청이나 인수를 필터링하거나 수정하는데에 
    자주 사용된다. 위에서 내가 썼던 예시에서도 받은 요청으로 로그인한 사용자인지 확인 후 로그인한 
    사용자라면 다른 페이지로 리다이렉션 되도록 하였다.
    '''

    # 방문자가 <edit>버튼을 클릭해서 페이지로 접근했다면 GET방식으로 pk=1인 comment의 내용이 폼에 채워진 상태의 페이지가 나타난다.
    # 이페이지에서 <submit>을 클릭하면 /blog/update_comment/1/경로로 POST방식을 사용해 폼의 내용을 전달하고 처리하게 되어있따
    # 문제는 다른 사용자가 로그인한 상태에서 동일한 url을 입력하면 본인이 아닌데 수정이 가능하다
    # 이런 상황을 방지하기위해 dipatch() 메서드에서 GET방식인지 POST방식인지를 판단하기에 앞서 댓글 작성자와 로그인한 사용자가 다른경오 퍼미션 디나이드오류가 발생하도록 설정

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            # get_object() = Post.objects.get(pk=pk)
            return super(CommentUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied



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
            comment_form = CommentForm(request.POST) # form.py에 작성하였떤 CommentForm 이용
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

# pk 값을 가진 댓글을 쿼리셋을 받기 위해 pk를 인자값으로 넣음
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk) # 해당 pk에 해당하는 댓글이 없다면 오류발생
    post = comment.post # 댓글이 달려있는 포스트 저장 (리다이렉트용)
    if request.user.is_authenticated and request.user == comment.author:
        comment.delete()
        return redirect(post.get_absolute_url())
    else: # 권한 없을시 접근 불가
        raise PermissionDenied
'''
DeleteView는 장고에서도 역시 제공
그러나, 이걸 사용하기되면 기본으로 정말로 삭제할것인지 확인하는 메세지가 표시되므로
그런 삭제를 위한 페이지로 이동했다가 돌아오는 방식이 아닌 해당페이지에 그대로 머무르면서 모달을 확인하는 방식으로 처리
'''

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