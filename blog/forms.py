from .models import Comment
from django import forms

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment

        # Comment model에는 여러가지 필드가 있지만 여기에서는 content필드만 필요하므로 아래를 입력
        # 다른 방법으로 exlude로 필드를 제외시킬수 있으면 fileds혹은 exclude중 하나는 꼭 사용해야함
        fields = ('content',)
        # exclude =('post', author', 'created_at', 'modifed_at')