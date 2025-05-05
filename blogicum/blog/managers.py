from django.db import models

from .querysets import PostQuerySet


class PublishedPostManager(models.Manager):

    def get_queryset(self):
        return (
            PostQuerySet(self.model)
            .with_related()
            .published()
        )
