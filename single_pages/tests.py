from django.test import TestCase, Client
from django.contrib.auth.models import User
from bs4 import BeautifulSoup
from blog.models import Post


# Create your tests here.

class TestView(TestCase):

    # setup()의 역할 : 함수에서 브라우저 역할을 하는 CLient를 불러오고 trump라는 사용자를 만든다.
    # 실제 테스트트 test_landing()함수에서 이러우짐
    def setUp(self):
        self.client = Client()
        self.user_trump = User.objects.create_user(username = 'trump', password = 'somepassword')

    def test_lading(self):
        # 4 개의 포스트중 3개만 표시할 예정
        post_001 = Post.objects.create(
            title = "첫 번째 포스트",
            content = "첫 포스트 입니다.",
            author = self.user_trump
        )

        post_002 = Post.objects.create(
            title="두 번째 포스트",
            content="두 포스트 입니다.",
            author=self.user_trump
        )


        post_003 = Post.objects.create(
            title="세 번째 포스트",
            content="세 포스트 입니다.",
            author=self.user_trump
        )

        post_004 = Post.objects.create(
            title="네 번째 포스트",
            content="네 포스트 입니다.",
            author=self.user_trump
        )

        # 대문페이지에 접근
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        body = soup.body # 새로운 방법인듯? body인 부분을 뽑아오기

        self. assertNotIn(post_001.title, body.text)
        self. assertIn(post_002.title, body.text)
        self. assertIn(post_003.title, body.text)
        self. assertIn(post_004.title, body.text)

