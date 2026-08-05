from django.contrib import admin
from .models import Attendance, Group, Lesson, Subject, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'gender', 'is_paid')
    list_filter = ('role', 'gender', 'is_paid')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'teacher')
    list_filter = ('subject',)
    filter_horizontal = ('students',)  # Удобный выбор учеников галочками


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('group', 'date', 'start_time', 'end_time', 'is_confirmed')
    list_filter = ('is_confirmed', 'date', 'group')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'student', 'is_present')
    list_filter = ('is_present',)