from django.db import models

# Create your models here.
class Image(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_PUBLIC = "published"
    STATUS_SET = (
            (STATUS_DRAFT, "draft"),
            (STATUS_PUBLIC, "published"),
    )
    filepath = models.CharField(primary_key=True, max_length=1024)
    sender = models.CharField(max_length=32)
    title = models.CharField(max_length=128)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    lat = models.FloatField(default=34.75)
    lng = models.FloatField(default=135.5)
    status = models.CharField(choices=STATUS_SET, default=STATUS_DRAFT, max_length=9)

    def __str__(self):
        return '{}, {}, {}, {}, {}, {}, {}, {}, {}'.format(self.filepath, self.sender, self.title, self.body, self.created_at, self.updated_at, self.lat, self.lng, self.status)