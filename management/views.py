from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from .forms import UserRegistrationForm, SubjectForm, GroupForm
from .models import Attendance, Group, Lesson, UserProfile, Subject


@login_required
def index(request):
    user = request.user
    role = getattr(getattr(user, 'profile', None), 'role', 'student')

    context = {'role': role}

    if role == 'admin':
        context['subjects'] = Subject.objects.all()
        context['groups'] = Group.objects.all()

    elif role == 'teacher':
        context['my_groups'] = Group.objects.filter(teacher=user)

    elif role == 'student':
        context['my_groups'] = user.student_groups.all()

    return render(request, 'management/index.html', context)


@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    user = request.user
    role = getattr(getattr(user, 'profile', None), 'role', 'student')

    is_teacher_of_group = role == 'teacher' and lesson.group.teacher == user
    can_edit = role == 'admin' or is_teacher_of_group

    if request.method == 'POST' and can_edit:
        students = lesson.group.students.all()
        for student in students:
            is_present = request.POST.get(f'student_{student.id}') == 'on'

            Attendance.objects.update_or_create(
                lesson=lesson, student=student, defaults={'is_present': is_present}
            )

        lesson.is_confirmed = True
        lesson.save()
        return redirect('lesson_detail', lesson_id=lesson.id)

    attendances = Attendance.objects.filter(lesson=lesson)
    attendance_dict = {att.student.id: att.is_present for att in attendances}

    context = {
        'lesson': lesson,
        'students': lesson.group.students.all(),
        'attendance_dict': attendance_dict,
        'can_edit': can_edit,
        'role': role,
    }
    return render(request, 'management/lesson_detail.html', context)


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # При обычной регистрации роль всегда строго 'student'
            UserProfile.objects.update_or_create(user=user, defaults={'role': 'student'})

            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def subject_detail(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    groups = Group.objects.filter(subject=subject)
    
    context = {
        'subject': subject,
        'groups': groups,
    }
    return render(request, 'management/subject_detail.html', context)


@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    students = group.students.all()
    user = request.user
    role = getattr(getattr(user, 'profile', None), 'role', 'student')
    
    all_students = User.objects.filter(profile__role='student').exclude(id__in=students.values_list('id', flat=True))
    
    context = {
        'group': group,
        'students': students,
        'all_students': all_students,
        'role': role,
    }
    return render(request, 'management/group_detail.html', context)


@login_required
def students_list_view(request):
    user = request.user
    role = getattr(getattr(user, 'profile', None), 'role', 'student')
    
    if role not in ['admin', 'teacher']:
        return redirect('home')

    students = User.objects.filter(profile__role='student').select_related('profile')

    if request.method == 'POST' and role == 'admin':
        student_id = request.POST.get('student_id')
        is_paid = request.POST.get('is_paid') == 'on'
        
        target_student = get_object_or_404(User, id=student_id)
        target_student.profile.is_paid = is_paid
        target_student.profile.save()
        return redirect('students_list')

    context = {
        'students': students,
        'role': role,
    }
    return render(request, 'management/students_list.html', context)


@login_required
def delete_student_from_system(request, student_id):
    user = request.user
    role = getattr(getattr(user, 'profile', None), 'role', 'student')
    
    if role != 'admin':
        return redirect('students_list')

    target_student = get_object_or_404(User, id=student_id, profile__role='student')
    target_student.delete()
    return redirect('students_list')


@login_required
def delete_group(request, group_id):
    user = request.user
    role = getattr(getattr(user, 'profile', None), 'role', 'student')
    
    group = get_object_or_404(Group, id=group_id)
    
    is_teacher_owner = role == 'teacher' and group.teacher == user
    if role != 'admin' and not is_teacher_owner:
        return redirect('home')

    group.delete()
    return redirect('home')


@login_required
def remove_student_from_group(request, group_id, student_id):
    user = request.user
    role = getattr(getattr(user, 'profile', None), 'role', 'student')
    
    group = get_object_or_404(Group, id=group_id)
    
    is_teacher_owner = role == 'teacher' and group.teacher == user
    if role != 'admin' and not is_teacher_owner:
        return redirect('group_detail', group_id=group.id)

    student = get_object_or_404(User, id=student_id)
    group.students.remove(student)
    return redirect('group_detail', group_id=group.id)


@login_required
def profile_view(request):
    user = request.user
    profile = getattr(user, 'profile', None)
    
    if profile and profile.role == 'teacher':
        groups = user.teacher_groups.all()
    elif profile and profile.role == 'student':
        groups = user.student_groups.all()
    else:
        groups = []
        
    context = {
        'profile_user': user,
        'profile': profile,
        'groups': groups,
    }
    return render(request, 'management/profile.html', context)


@login_required
def add_subject_view(request):
    user = request.user
    role = getattr(getattr(user, 'profile', None), 'role', 'student')
    if role != 'admin':
        return redirect('home')
        
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = SubjectForm()
    return render(request, 'management/add_subject.html', {'form': form})


@login_required
def add_group_view(request):
    user = request.user
    role = getattr(getattr(user, 'profile', None), 'role', 'student')
    if role != 'admin':
        return redirect('home')
        
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = GroupForm()
    return render(request, 'management/add_group.html', {'form': form})


@login_required
def add_student_to_group(request, group_id):
    user = request.user
    role = getattr(getattr(user, 'profile', None), 'role', 'student')
    group = get_object_or_404(Group, id=group_id)
    
    is_teacher_owner = role == 'teacher' and group.teacher == user
    if role != 'admin' and not is_teacher_owner:
        return redirect('group_detail', group_id=group.id)
        
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        if student_id:
            student = get_object_or_404(User, id=student_id, profile__role='student')
            group.students.add(student)
    return redirect('group_detail', group_id=group.id)


@login_required
def add_student_to_system_view(request):
    user = request.user
    role = getattr(getattr(user, 'profile', None), 'role', 'student')
    
    if role not in ['admin', 'teacher']:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()

            UserProfile.objects.update_or_create(user=new_user, defaults={'role': 'student'})

            return redirect('students_list')
    else:
        form = UserRegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'management/add_student_system.html', context)