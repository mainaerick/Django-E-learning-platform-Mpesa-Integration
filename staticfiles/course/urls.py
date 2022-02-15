from django.urls import path

from .views import CourseDetailView, CourseListView, LessonDetailView

app_name = 'course'
urlpatterns = [
    path('', CourseListView.as_view(), name='home'),
    path('<slug>', CourseDetailView.as_view(), name='detail'),
    path('<course_slug>/<lesson_slug>',
         LessonDetailView.as_view(),
         name='lesson-detail'),
]
