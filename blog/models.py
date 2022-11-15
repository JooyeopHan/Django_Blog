from django.db import models

# 작성자 표시
from django.contrib.auth.models import User

# markdonwx
from markdownx.models import MarkdownxField
from markdownx.utils import markdown
# 첨부 파일명과 확장자 아이콘 나타낼떄 사용(get_file_name() 함수)
import os

# Create your models here.


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return  f'/blog/tag/{self.slug}/'


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return  f'/blog/category/{self.slug}/'


    class Meta:
        verbose_name_plural = 'Categories'

class Post(models.Model):
    title = models.CharField(max_length=30)

    hook_text = models.CharField(max_length=100, blank=True)
    content = MarkdownxField()

    head_image = models.ImageField(upload_to="blog/images/%Y/%m/%d/", blank=True)
    file_upload = models.FileField(upload_to = 'blog/files/%Y/%m/%d/', blank=True)

    # on_delete = models.CASECADE ==> 이 포스트의 작성자가 데이터 베이스에서 삭제되었을 떄 이 포스트도 같이 삭제
    # author = models.ForeignKey(User, on_delete=models.CASCADE)

    # on_delete = models.SET_NULL ==> 데이터베이스에서 삭제되었 을 때 작성자 명을 빈칸으로 둔다.
    author = models.ForeignKey(User,null=True, on_delete=models.SET_NULL)

    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)

    tags = models.ManyToManyField(Tag, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



# admin의 포스트 pk, title 노출
    def __str__(self):
        return f'[{self.pk}]{self.title} :: {self.author}'

    def get_absolute_url(self):
        return f'/blog/{self.pk}/'

    def get_file_name(self):
        return os.path.basename(self.file_upload.name)

    def get_file_ext(self):
        return self.get_file_name().split('.')[-1]

    def get_content_markdown(self):
        return markdown(self.content)