from django.test import TestCase, Client
from django.contrib.auth.models import User

from bs4 import BeautifulSoup
from .models import Post, Category, Tag, Comment

# Create your tests here.

class TestView(TestCase):
    # def test_post_list(self):
    #     self.assertEqual(2, 2)

    def setUp(self):
        self.client = Client()
        self.user_trump = User.objects.create_user(username='trump', password = 'somepassword')
        self.user_obama = User.objects.create_user(username='obama', password = 'somepassword')
        self.user_obama.is_staff = True
        self.user_obama.save()


        self.category_animal = Category.objects.create(name = 'animal', slug= 'animal' )
        self.category_spongebob = Category.objects.create(name = 'spongebob', slug= 'spongebob' )

        self.tag_hobby_kor = Tag.objects.create(name='취미', slug = '취미')
        self.tag_hobby = Tag.objects.create(name='hobby', slug = 'hobby')
        self.tag_working = Tag.objects.create(name='working', slug = 'working')

        self.post_001 = Post.objects.create(
            title='첫 번 째 포스트 입니다',
            content='Hello World. 첫번쨰 포스트',
            category = self.category_animal,
            author=self.user_trump
        )
        self.post_001.tags.add(self.tag_working)

        self.post_002 = Post.objects.create(
            title='두 번 째 포스트 입니다',
            content='1등이 전부가 아니래요 두번째',
            category = self.category_spongebob,
            author=self.user_obama
        )

        self.post_003 = Post.objects.create(
            title='세 번 째 포스트 입니다.',
            content='카테고리가 없을수 도 있죠',
            author=self.user_obama
        )
        self.post_003.tags.add(self.tag_hobby)
        self.post_003.tags.add(self.tag_hobby_kor)

        self.comment_001 = Comment.objects.create(
            post = self.post_001,
            author = self.user_obama,
            content = '첫번째 댓글'
        )

    def test_comment_form(self):
        # 로그인한 사람만 댓글을 달 수 있또록 허용ㅇ할 예정
        # 상단의 작성한 코멘트가 하나인가? 그리고 포스트 1에 작성된 댓글도 하나인가?
        self.assertEqual(Comment.objects.count(),1)
        self.assertEqual(self.post_001.comment_set.count(),1)

        # 로그인 하지 않은상태 client의 post001 url을 가져옴 (로그인 되지않아도 포스트에 접속은 가능함 댓글작성만 x)
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200) # 정상적으로 url 접속이 허영되는지
        soup = BeautifulSoup(response.content, 'html.parser') #post_001 url에 포함된 html content parsing

        comment_area = soup.find('div', id = 'comment-area')
        self.assertFalse(comment_area.find('form', id = 'comment-form')) # comment-form이라는 id의 form 이 없는지 확인

        # 로그인을 했을 떄
        self.client.login(username = 'obama', password= 'somepassword')
        # 위처럼 client를 self.client.login 처리한 경우 아래의 self.client.get은 로그인 한 상태로 접속하는것을 의미
        response = self.client.get(self.post_001.get_absolute_url()) # 로그인 하지 않았을떄와 동일하게 response 받음
        self.assertEqual(response.status_code, 200) # 위와 동일
        soup = BeautifulSoup(response.content, 'html.parser') #위와 동일

        comment_area = soup.find('div', id = 'comment-area')

        comment_form = comment_area.find('form', id = 'comment-form') # 위와 다르게 comment-form을 변수로 지정
        self.assertTrue(comment_form.find('textarea', id = 'id_content')) # id_content라는 id의 textarea가 있는지 확인

        # POST 방식으로 댓글 내용을 서보에 보낸다. 그요청 결과를 response에 담는다.
        # 이 떄 서버에 요청하는 url이 중요하며, 곧 템플릿 수정할 때 적용
        # follow = True의 역할 : POST로 보내는 경우 서버에 처리한 후 리다이렉트가 되는데 이떄 따라가도록 설정하는 역할을 한다.
        response = self.client.post(
            self.post_001.get_absolute_url() + 'new_comment/',
            {
                'content' : '오바마의 댓글입니다.'
            },
            follow=True

        )

        self.assertEqual(response.status_code, 200)
        # 추가 댓글이 달려 댓글이 2개인지 확인
        self.assertEqual(Comment.objects.count(),2)
        self.assertEqual(self.post_001.comment_set.count(), 2)

        new_comment = Comment.objects.last() # Comments object의 가장 나중에 것을 new_comment 변수에 저장

        soup = BeautifulSoup(response.content, 'html.parser') # 이것도 new_comment가 달린 포스트의 상세 페이지가 리다이렉트 된다
        self.assertIn(new_comment.post.title, soup.title.text) # 새로운 코멘트의 포스트 제목과, 포스트 상세 페이지의 제목이 일치하는지 확인

        comment_area = soup.find('div', id = 'comment-area')
        new_comment_div = comment_area.find('div', id=f'comment-{new_comment.pk}') # new comment 생성시 id는 자동생성??
        self.assertIn('obama', new_comment_div.text) # obama 있니?
        self.assertIn('오바마의 댓글입니다.', new_comment_div.text) # 오바마의 댓글입니다 있니?






    def test_update_post(self):
        update_post_url = f'/blog/update_post/{self.post_003.pk}/'

        # 로그인 x
        response = self.client.get(update_post_url)
        self.assertNotEqual(response.status_code, 200)

        # 로그인은 했지만 작성자가 아닌 경우
        self.assertNotEqual(self.post_003.author, self.user_trump)
        self.client.login(
            username = self.user_trump.username,
            password = 'somepassword'
        )

        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 403)

        # 작성자가 접근하는 경우
        self.client.login(
            username = self.post_003.author.username, #오바마
            password = 'somepassword'
        )

        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Edit Post - Blog', soup.title.text)
        main_area = soup.find('div', id = 'main-area')
        self.assertIn('Edit Post', main_area.text)

        tag_str_input = main_area.find('input', id = 'id_tags_str')
        self.assertTrue(tag_str_input)
        self.assertIn('취미; hobby', tag_str_input.attrs['value'])

        response = self.client.post(
            update_post_url,
            {
                'title' : '세 번째 포스트를 수정했습니다.',
                'content' : '세 번째 포스트 내용',
                'category' : self.category_animal.pk,
                'tags_str' : '파이썬 공부; 한글 태그, some tag'
            }
            ,follow=True # 이건 뭘까용 redirect를 하게 허용?
        )

        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id = 'main-area')
        self.assertIn('세 번째 포스트를 수정했습니다.', main_area.text)
        self.assertIn('세 번째 포스트 내용', main_area.text)
        self.assertIn(self.category_animal.name, main_area.text)
        self.assertIn('파이썬 공부', main_area.text)
        self.assertIn('한글 태그', main_area.text)
        self.assertIn('some tag', main_area.text)
        self.assertNotIn('python', main_area.text)





    def test_create_post(self):
        #로그인하지 않으면 status code가 200이 아니다.
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # 로그인을 한다. (staff 아님)
        self.client.login(username = 'trump', password='somepassword')
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # obama 로그인
        self.client.login(username='obama', password='somepassword')
        response = self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code, 200)


        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Create Post - Blog', soup.title.text)
        main_area = soup.find('div', id = 'main-area')
        self.assertIn('Create New Post',main_area.text)

        tag_str_input = main_area.find('input', id = 'id_tags_str')
        self.assertTrue(tag_str_input)

        self.client.post(
            '/blog/create_post/',
            {
                'title' : 'Post Form 만들기',
                'content' : "Post Form 페이지를 만듭시다",
                'tags_str' : 'new tag; 한글 태그, hobby'
            }
        )
        self.assertEqual(Post.objects.count(),4)
        last_post = Post.objects.last()
        self.assertEqual(last_post.title, "Post Form 만들기")
        self.assertEqual(last_post.author.username, 'obama')

        self.assertEqual(last_post.tags.count(), 3)
        self.assertTrue(Tag.objects.get(name='new tag'))
        self.assertTrue(Tag.objects.get(name='hobby'))
        self.assertEqual(Tag.objects.count(), 5)


    def test_tag_page(self):
        response = self.client.get(self.tag_working.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.tag_working.name, soup.h1.text)

        main_area = soup.find('div', id = 'main-area')
        self.assertIn(self.tag_working.name, main_area.text)

        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)


    def test_category_page(self):
        response = self.client.get(self.category_animal.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.category_animal.name, soup.h1.text)

        main_area = soup.find('div', id = 'main-area')
        self.assertIn(self.category_animal.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)


    def category_card_test(self, soup):
        categories_card = soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(f'{self.category_animal.name}({self.category_animal.post_set.count()})', categories_card.text)
        self.assertIn(f'{self.category_spongebob.name}({self.category_spongebob.post_set.count()})', categories_card.text)
        self.assertIn(f'미분류 (1)', categories_card.text)


    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn('Blog',navbar.text)
        self.assertIn('About Me',navbar.text)

        logo_btn = navbar.find('a', text='Do It Django')
        self.assertEqual(logo_btn.attrs['href'],'/')

        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        blog_btn = navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'], '/blog/')

        about_me_btn = navbar.find('a', text='About Me')
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')

    def test_post_list(self):

        # 포스트가 있는 경우 #
        self.assertEqual(Post.objects.count(), 3)

        # 1.1 포스트 목록페이지를 가져온다.
        response = self.client.get('/blog/')
        # 1.2 정상적으로 페이지가 로드된다.
        self.assertEqual(response.status_code, 200)
        # 1.3 페이지 타이틀은 'Blog'이다.
        soup = BeautifulSoup(response.content,'html.parser')
        self.assertEqual(soup.title.text, 'Blog')


        # # 1.4 내비게이션 바가 있따.
        # navbar = soup.nav
        # # 1.5 Blog, About Me 라는 문구가 내비게이션 바에 있다.
        # self.assertIn('Blog',navbar.text)
        # self.assertIn('About Me',navbar.text)

        self.navbar_test(soup)
        self.category_card_test(soup)


        # 2.1 메인 영역에 게시물이 하나도 없다면
        # self.assertEqual(Post.objects.count(),0)


        # 2.2 '아직 게시물이 없습니다'라는 문구가 보인다.
        main_area = soup.find('div', id = 'main-area')
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)


        # # 3.2 포스트 목록 페이지를 새로고침했을 때
        # response = self.client.get('/blog/')
        # soup = BeautifulSoup(response.content, 'html.parser')
        # self.assertEqual(response.status_code, 200)

        # main_area = soup.find('div', id='main-area')

        post_001_card = main_area.find('div', id ='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.post_001.author.username.upper(), post_001_card.text)
        self.assertIn(self.tag_working.name, post_001_card.text)
        self.assertNotIn(self.tag_hobby.name, post_001_card.text)
        self.assertNotIn(self.tag_hobby_kor.name, post_001_card.text)

        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertIn(self.post_002.author.username.upper(), post_002_card.text)
        self.assertNotIn(self.tag_working.name, post_002_card.text)
        self.assertNotIn(self.tag_hobby.name, post_002_card.text)
        self.assertNotIn(self.tag_hobby_kor.name, post_002_card.text)

        post_003_card = main_area.find('div', id='post-3')
        self.assertIn('미분류', post_003_card.text)
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn(self.post_003.author.username.upper(), post_003_card.text)
        self.assertNotIn(self.tag_working.name, post_003_card.text)
        self.assertIn(self.tag_hobby.name, post_003_card.text)
        self.assertIn(self.tag_hobby_kor.name, post_003_card.text)



        # 3.5 main_area 에 trump와 obama가 있는지
        self.assertIn(self.user_trump.username.upper(), main_area.text)
        self.assertIn(self.user_obama.username.upper(), main_area.text)


        # 포스트가 없는경우 #

        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id = 'main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)

    def test_post_detail(self):

        # 1.2 그 포스트의 url은 '/blog/1/' 이다.
        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1/')

        # 2. 첫 번째 포스트의 상세 페이지 테스트
        # 2.1 첫 번째 포스트의 url로 접근하면 정상적으로 작동한다(status code: 200)
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        # # 2.2 포스트 목록 페이지와 똑같은 내비게이션 바가 있다.
        # navbar = soup.nav
        # self.assertIn('Blog', navbar.text)
        # self.assertIn('About Me', navbar.text)
        self.navbar_test(soup)
        self.category_card_test(soup)

        # 2.3 첫 번째 포스트의 제목이 웹브라우저 탭 타이틀에 들어 있다.
        self.assertIn(self.post_001.title,soup.title.text)

        # 2.4 첫 번째 포스트의 제목이 포스트 영역에 있따.
        main_area = soup.find('div', id='main-area')
        post_area = soup.find('div', id ='post-area')
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.category_animal.name, post_area.text)


        # 2.5 첫 번째 포스트의 작성자가 포스트 영역에 있다.(아직 구현 x)
        self.assertIn(self.user_trump.username.upper(), post_area.text)

        # 2.6 첫 번째 포스트의 내용(content)이 포스트 영역에 있다.
        self.assertIn(self.post_001.content, post_area.text)

        self.assertIn(self.tag_working.name, post_area.text)
        self.assertNotIn(self.tag_hobby.name, post_area.text)
        self.assertNotIn(self.tag_hobby_kor.name, post_area.text)

        # comment area 체크
        comment_area = soup.find('div', id = 'comment-area')
        comment_001_area  = comment_area.find('div', id = 'comment-1')
        self.assertIn(self.comment_001.author.username, comment_001_area.text)
        self.assertIn(self.comment_001.content, comment_001_area.text)
