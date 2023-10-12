from dataclasses import field
from django import forms
from blog.models import BlogPost, Comment, Reply, PostToAnotherPost

class CreateBlogPostForm(forms.ModelForm):

    class Meta:
        model = BlogPost
        fields = ('title', 'header_image', 'body', 'tag')


class UpdateBlogPostForm(forms.ModelForm):

    class Meta:
        model = BlogPost
        fields = ('title', 'header_image', 'body', 'tag')
    
    def save(self, commit=True):
        blog_post = self.instance
        blog_post.title = self.cleaned_data['title']
        blog_post.body = self.cleaned_data['body']

        if commit:
            blog_post.save()
        
        return blog_post


class CreateCommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('body',)



class CreateReplyForm(forms.ModelForm):

    class Meta:
        model = Reply
        fields = ('reply',)


class CreatePostAnotherPostForm(forms.ModelForm):

    class Meta:
        model = PostToAnotherPost
        fields = ('title', 'header_image', 'body', 'tag')












