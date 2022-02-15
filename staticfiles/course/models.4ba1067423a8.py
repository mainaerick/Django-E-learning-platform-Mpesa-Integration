from django.db import models
from django.urls import reverse

from membership.models import Membership


# Create your models here.
class Course(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=120)
    description = models.TextField()
    allowed_memberships = models.ManyToManyField(Membership)
    thumbnail = models.ImageField(null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("course:detail", kwargs={"slug": self.slug})

    @property
    def lessons(self):
        return self.lesson_set.all().order_by('position')


class Lesson(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=120)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True)
    position = models.IntegerField()
    video_url = models.CharField(max_length=200)
    videofile = models.FileField(upload_to='videos/',
                                 null=True,
                                 verbose_name="")
    thumbnail = models.ImageField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("course:lesson-detail",
                       kwargs={
                           "course_slug": self.course.slug,
                           "lesson_slug": self.slug
                       })
