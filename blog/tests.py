from django.test import TestCase, Client
from django.contrib.auth.models import User

from bs4 import BeautifulSoup
from .models import Post, Category, Tag

# Create your tests here.

class TestView(TestCase):
    # def test_post_list(self):
    #     self.assertEqual(2, 2)

    def setUp(self):
        self.client = Client()
        self.user_trump = User.objects.create_user(username='trump', password = 'somepassword')
        self.user_obama = User.objects.create_user(username='obama', password = 'somepassword')

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