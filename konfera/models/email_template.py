from django.db import models

from konfera.models.abstract import KonferaModel


class EmailTemplate(KonferaModel):
    name = models.CharField(max_length=255)
    text_template = models.TextField()
    html_template = models.TextField()
    counter = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def add_count(self, add=1):
        self.counter += add
        self.save()
