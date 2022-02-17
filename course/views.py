from django.shortcuts import get_object_or_404, render

# Create your views here.
from django.views.generic import ListView, DetailView, View

from membership.models import UserMembership
from .models import Course, Lesson
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

app_name = 'course'


class CourseListView(ListView):
    model = Course


class CourseDetailView(DetailView):
    model = Course


class LessonDetailView(LoginRequiredMixin, View):
    login_url = '/membership/login/'
    redirect_field_name = "redirect_to"

    def get(self, request, course_slug, lesson_slug, *args, **kwargs):
        course = get_object_or_404(Course, slug=course_slug)
        lesson = get_object_or_404(Lesson, slug=lesson_slug)
        user_membership = get_object_or_404(UserMembership, user=request.user)
        print(user_membership)
        user_membership_type = user_membership.membership.membership_type
        course_allowed_mem_types = course.allowed_memberships.all()
        context = {'object': None}
        if course_allowed_mem_types.filter(
                membership_type=user_membership_type).exists() or course_allowed_mem_types.filter(
                membership_type="free").exists():
            context = {'object': lesson}
        return render(request, "course/lesson_detail.html", context)
