from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('subject/<int:subject_id>/', views.subject_detail, name='subject_detail'),
    path('group/<int:group_id>/', views.group_detail, name='group_detail'),
    path('students/', views.students_list_view, name='students_list'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('students/add/', views.add_student_to_system_view, name='add_student_system'),
    
    # Добавление элементов
    path('subject/add/', views.add_subject_view, name='add_subject'),
    path('group/add/', views.add_group_view, name='add_group'),
    path('group/<int:group_id>/add-student/', views.add_student_to_group, name='add_student_to_group'),
    
    # Удаление элементов
    path('students/delete/<int:student_id>/', views.delete_student_from_system, name='delete_student'),
    path('group/delete/<int:group_id>/', views.delete_group, name='delete_group'),
    path('group/<int:group_id>/remove-student/<int:student_id>/', views.remove_student_from_group, name='remove_student_from_group'),
]