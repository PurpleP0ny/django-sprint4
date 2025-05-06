from django.db import models
from django.utils import timezone


class PostQuerySet(models.QuerySet):

    def with_related(self):
        return self.select_related('category', 'author', 'location')

    def with_comments_count(self):
        return self.annotate(comment_count=models.Count('comments'))

    def published(self):
        return self.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )
