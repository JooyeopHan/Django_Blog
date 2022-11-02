from django.db import models

# Create your models here.

class Post(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # author 추후 작성 예쩡 ( 나중에 모델에서 외래키를 구현 할 때 다룰 것)

    def __str__(self):
        return f'[{self.pk}]{self.title}'