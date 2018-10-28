from django.db import models
from django.contrib.auth.models import User, AbstractUser
# Create your models here.


class UserInfo(AbstractUser):
    """
    用户信息
    """
    nid = models.AutoField(primary_key=True)
    telephone = models.CharField(max_length=11, null=True, unique=True)
    avatar = models.FileField(upload_to='avatars/', default='avatars/default.png')
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    blog = models.OneToOneField(to='Blog', to_field='nid', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.username


class Blog(models.Model):
    """
    个人站点表(博客信息表)
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='个人博客标题', max_length=64)
    site_name = models.CharField(verbose_name='站点名称', max_length=64)
    theme = models.CharField(verbose_name='博客主题', max_length=32)

    def __str__(self):
        return self.title


class Category(models.Model):
    '''
    博客分类表
    '''
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='分类标题', max_length=32)
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Tag(models.Model):
    '''
    站点标签
    '''
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='标签名称', max_length=32)
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Article(models.Model):
    '''
    文章表
    '''
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='文章标题', max_length=50)
    desc = models.CharField(verbose_name='文章描述', max_length=255)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    content = models.TextField()

    comment_count = models.IntegerField(default=0)
    up_count = models.IntegerField(default=0)
    down_count = models.IntegerField(default=0)

    user = models.ForeignKey(verbose_name='作者', to='UserInfo', to_field='nid', on_delete=models.CASCADE)
    category = models.ForeignKey(to='Category', to_field='nid', null=True, on_delete=models.CASCADE)
    tags = models.ManyToManyField(to='Tag',
                                  through='Article2Tag',
                                  through_fields=('article', 'tag'),
                                  )

    def __str__(self):
        return self.title


class Article2Tag(models.Model):
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(verbose_name='文章', to='Article', to_field='nid', on_delete=models.CASCADE)
    tag = models.ForeignKey(verbose_name='标签', to='Tag', to_field='nid', on_delete=models.CASCADE)

    class Meta:
        '''
        联合唯一，两个字段不能重复，联合唯一的参数只能是列表或者元祖类型
        '''
        unique_together = [
            ('article', 'tag'),
        ]

    def __str__(self):
        v = self.article.title + '---' + self.tag.title
        return v


class ArticleUpDown(models.Model):
    '''
    文章点赞踩灭表
    '''
    nid = models.AutoField(primary_key=Tag)
    user = models.ForeignKey('UserInfo', null=True, on_delete=None)
    article = models.ForeignKey('Article', null=True, on_delete=None)
    is_up = models.BooleanField(default=True)

    class Meta:
        unique_together = [
            ('article', 'user'),
        ]


class Comment(models.Model):
    '''
    评论表
    根评论：对文章的评论
    子评论：对评论的评论
    '''
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(verbose_name='评论文章', to='Article', to_field='nid', on_delete=None)
    user = models.ForeignKey(verbose_name='评论者', to='UserInfo', to_field='nid', on_delete=None)
    content = models.CharField(verbose_name='评论内容', max_length=255)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    parent_comment_id = models.ForeignKey('self', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.content
































































