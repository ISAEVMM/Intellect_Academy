from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Администратор'),
        ('teacher', 'Преподаватель'),
        ('student', 'Ученик'),
    )
    
    GENDER_CHOICES = (
        ('male', 'Мужской'),
        ('female', 'Женский'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True, verbose_name='Пол')
    is_paid = models.BooleanField(default=False, verbose_name='Оплата')

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'


class Subject(models.Model):
    name = models.CharField(max_length=100)  # Английский, Китайский, IT, Русский

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=100)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teacher_groups',
        limit_choices_to={'profile__role': 'teacher'},
    )
    students = models.ManyToManyField(
        User,
        related_name='student_groups',
        blank=True,
        limit_choices_to={'profile__role': 'student'},
    )
    schedule = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Время занятий"
    )

    def __str__(self):
        return f'{self.name} ({self.subject.name})'


class Lesson(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_confirmed = models.BooleanField(default=False)  # Подтверждено ли учителем

    def __str__(self):
        return f'{self.group.name} - {self.date} ({self.start_time} - {self.end_time})'


class Attendance(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    is_present = models.BooleanField(default=False)  # Галочка: пришел / не пришел

    def __str__(self):
        status = 'Присутствовал' if self.is_present else 'Отсутствовал'
        return f'{self.student.username} - {self.lesson} [{status}]'