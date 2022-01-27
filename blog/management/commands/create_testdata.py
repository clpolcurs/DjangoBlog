from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from blog.models import Article, Tag, Category


class Command(BaseCommand):
    help = 'Create test datas'

    def handle(self, *args, **options):
        user = get_user_model().objects.get_or_create(
            email='test@test.com', username='TestUser', password=make_password('123456@aA'))[0]

        pcategory = Category.objects.get_or_create(
            name='Parent Category', parent_category=None)[0]

        category = Category.objects.get_or_create(
            name='Child Category', parent_category=pcategory)[0]

        category.save()
        basetag = Tag()
        basetag.name = "Tag"
        basetag.save()
        for i in range(1, 20):
            article = Article.objects.get_or_create(
                category=category,
                title='Nice title ' + str(i),
                body='Nice content ' + str(i),
                author=user)[0]
            tag = Tag()
            tag.name = "Tag" + str(i)
            tag.save()
            article.tags.add(tag)
            article.tags.add(basetag)
            article.save()

        from djangoblog.utils import cache
        cache.clear()
        self.stdout.write(self.style.SUCCESS('created test datas \n'))
