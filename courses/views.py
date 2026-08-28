from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q, Count
import re
from datetime import datetime, date
from .models import (
    CustomUser, Course, Teacher, Review, Enrollment, Work,
    Notification, Message, SiteSettings, CourseMaterial, Lesson
    ,Attendance,AttendanceSession,Exam,ExamResult,Certificate,CourseRating
)
from .forms import SignUpForm, LoginForm
from .telegram_service import (
    send_enrollment_approved,
    send_enrollment_rejected,
    send_new_message,
    send_welcome_message
)



# ====================
# YouTube URL ئايلاندۇرۇش
# ====================
def youtube_to_embed(url):
    """YouTube URL نى embed URL غا ئايلاندۇرىدۇ"""
    if not url:
        return url

    patterns = [
        r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
        r'youtu\.be/([a-zA-Z0-9_-]+)',
        r'youtube\.com/embed/([a-zA-Z0-9_-]+)',
        r'youtube\.com/shorts/([a-zA-Z0-9_-]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            return f'https://www.youtube.com/embed/{video_id}'

    if 'vimeo.com' in url:
        match = re.search(r'vimeo\.com/(\d+)', url)
        if match:
            return f'https://player.vimeo.com/video/{match.group(1)}'

    return url


def index(request):
    from .models import FAQ, Announcement
    from django.utils import timezone

    courses = Course.objects.filter(is_active=True)
    teachers = Teacher.objects.all().order_by('order')
    reviews = Review.objects.all().order_by('order')
    works = Work.objects.all().order_by('order')
    faqs = FAQ.objects.filter(is_active=True).order_by('order')

    # ↓↓↓ يېڭى: ئېلانلارنى ئېلىش ↓↓↓
    now = timezone.now()
    announcements = Announcement.objects.filter(
        is_active=True
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gt=now)
    ).order_by('order', '-created_at')

    # نىشان ئوقۇرمەنگە قاراپ سۈزۈش
    if request.user.is_authenticated:
        if request.user.is_teacher():
            announcements = announcements.filter(target_audience__in=['all', 'teachers'])
        elif not request.user.is_staff:
            announcements = announcements.filter(target_audience__in=['all', 'students'])
    else:
        announcements = announcements.filter(target_audience='all')

    announcements = announcements[:5]  # ئەڭ كۆپ 5 ئېلان
    # ↑↑↑ ئېلانلار ↑↑↑

    # سۈزگۈچ پارامېتىرلىرى
    badge_filter = request.GET.get('badge', '')
    level_filter = request.GET.get('level', '')
    age_filter = request.GET.get('age', '')
    price_filter = request.GET.get('price', '')
    search_query = request.GET.get('q', '')

    if badge_filter:
        courses = courses.filter(badge__icontains=badge_filter)

    if level_filter:
        courses = courses.filter(level__icontains=level_filter)

    if age_filter:
        courses = courses.filter(age_group__icontains=age_filter)

    if price_filter:
        if price_filter == 'free':
            courses = courses.filter(price__icontains='ھەقسىز')
        elif price_filter == 'low':
            courses = courses.exclude(price__icontains='ھەقسىز').order_by('price')
        elif price_filter == 'high':
            courses = courses.exclude(price__icontains='ھەقسىز').order_by('-price')

    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(badge__icontains=search_query) |
            Q(instructor__name__icontains=search_query)
        ).distinct()

    courses = courses.order_by('order')

    available_badges = Course.objects.filter(is_active=True).values_list('badge', flat=True).distinct()
    available_levels = Course.objects.filter(is_active=True).exclude(level='').values_list('level',
                                                                                           flat=True).distinct()
    available_ages = Course.objects.filter(is_active=True).exclude(age_group='').values_list('age_group',
                                                                                             flat=True).distinct()

    context = {
        'courses': courses,
        'teachers': teachers,
        'reviews': reviews,
        'works': works,
        'faqs': faqs,
        'announcements': announcements,  # ← يېڭى قوشۇلغان

        'badge_filter': badge_filter,
        'level_filter': level_filter,
        'age_filter': age_filter,
        'price_filter': price_filter,
        'search_query': search_query,
        'available_badges': available_badges,
        'available_levels': available_levels,
        'available_ages': available_ages,
        'total_courses': Course.objects.filter(is_active=True).count(),
        'filtered_count': courses.count(),
    }
    return render(request, 'index.html', context)



def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            # ↓↓↓ Telegram قارشى ئېلىش ئۇچۇرى ↓↓↓
            send_welcome_message(user)
            # ↑↑↑ Telegram ↑↑↑

            messages.success(request, 'تىزىملىتىش مۇۋەپپەقىيەتلىك!')
            return redirect('index')
        else:
            for error in form.errors.values():
                messages.error(request, error[0])
            return redirect('index')
    return redirect('index')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'كىرىش مۇۋەپپەقىيەتلىك!')

            if user.is_staff or user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.is_teacher():
                return redirect('teacher_dashboard')
            else:
                return redirect('index')
        else:
            messages.error(request, 'ئېلېكترونلۇق خەت ياكى پارول خاتا')
            return redirect('index')

    return redirect('index')


def logout_view(request):
    logout(request)
    messages.success(request, 'چىقىش مۇۋەپپەقىيەتلىك!')
    return redirect('index')


def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_active=True)

    enrollment = None
    can_view_materials = False
    unread_count = 0

    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(user=request.user, course=course).first()

        if request.user.is_staff or request.user.role == 'admin':
            can_view_materials = True
        elif request.user.is_teacher():
            try:
                if course.instructor and course.instructor.user == request.user:
                    can_view_materials = True
            except:
                pass
        elif enrollment and enrollment.status == 'approved':
            can_view_materials = True

        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    materials = list(course.materials.all()) if can_view_materials else []

    for material in materials:
        if material.material_type == 'video' and material.url:
            material.embed_url = youtube_to_embed(material.url)
        else:
            material.embed_url = None

    # ↓↓↓ يېڭى: باھا ستاتىستىكىسى (loop نىڭ سىرتىدا!) ↓↓↓
    rating_stats = get_course_rating_stats(course)
    ratings = CourseRating.objects.filter(course=course).select_related('student')

    my_rating = None
    if request.user.is_authenticated:
        my_rating = CourseRating.objects.filter(
            course=course,
            student=request.user
        ).first()
    # ↑↑↑ يېڭى قوشۇلغان ئاخىرلاشتى ↑↑↑

    context = {
        'course': course,
        'enrollment': enrollment,
        'materials': materials,
        'can_view_materials': can_view_materials,
        'enrolled': enrollment is not None,
        'enrolled_count': course.get_enrolled_count(),
        'unread_count': unread_count,
        'rating_stats': rating_stats,
        'ratings': ratings,
        'my_rating': my_rating,
    }
    return render(request, 'course_detail.html', context)

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_active=True)

    if course.is_full():
        messages.error(request, 'بۇ كۇرسنىڭ ئورنى تولدى.')
        return redirect('course_detail', course_id=course.id)

    existing = Enrollment.objects.filter(user=request.user, course=course).first()
    if existing:
        messages.info(request, 'سىز ئاللىبۇرۇن بۇ كۇرسقا تىزىملانغانسىز.')
        return redirect('course_detail', course_id=course.id)

    Enrollment.objects.create(user=request.user, course=course, status='pending')
    messages.success(request, 'تىزىملىتىش تەلىپىڭىز يوللاندى! ئوقۇتقۇچى تەستىقلىشىنى ساقلاڭ.')
    return redirect('course_detail', course_id=course.id)


@login_required
def my_enrollments(request):
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course', 'course__instructor')
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    context = {
        'enrollments': enrollments,
        'total': enrollments.count(),
        'approved_count': enrollments.filter(status='approved').count(),
        'pending_count': enrollments.filter(status='pending').count(),
        'unread_count': unread_count,
    }
    return render(request, 'my_enrollments.html', context)


@login_required
def cancel_enrollment(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, user=request.user)
    course_title = enrollment.course.title
    enrollment.delete()
    messages.success(request, f'«{course_title}» دىن تىزىملىتىشىڭىز بىكار قىلىندى.')
    return redirect('my_enrollments')


@login_required
def profile_view(request):
    if request.method == 'POST':
        request.user.full_name = request.POST.get('full_name', '')
        request.user.phone = request.POST.get('phone', '')
        request.user.telegram_id = request.POST.get('telegram_id', '')
        request.user.save()
        messages.success(request, 'ئارخىپىڭىز يېڭىلاندى!')
        return redirect('profile')

    return render(request, 'profile.html')


@login_required
def teacher_dashboard(request):
    if not request.user.is_teacher():
        return redirect('index')

    try:
        teacher_profile = request.user.teacher_profile
    except Teacher.DoesNotExist:
        return redirect('index')

    from datetime import datetime
    import json

    my_courses = Course.objects.filter(instructor=teacher_profile)
    enrollments = Enrollment.objects.filter(course__in=teacher_profile.courses.all()).select_related('user', 'course')
    pending_enrollments = enrollments.filter(status='pending')

    # ====================
    # 📊 ئوقۇتقۇچى چارت سانلىق مەلۇماتلىرى
    # ====================

    # ئۇيغۇرچە ئاي ناملىرى
    month_names_ug = [
        'يانۋار', 'فېۋرال', 'مارت', 'ئاپرېل', 'ماي', 'ئىيۇن',
        'ئىيۇل', 'ئاۋغۇست', 'سېنتەبىر', 'ئۆكتەبىر', 'نويابىر', 'دېكابىر'
    ]

    # 1. ئايلىق تىزىملىتىش (ئۆز كۇرسلىرى ئۈچۈن)
    current_year = datetime.now().year
    monthly_enrollments = []
    for month in range(1, 13):
        count = Enrollment.objects.filter(
            course__instructor=teacher_profile,
            created_at__year=current_year,
            created_at__month=month
        ).count()
        monthly_enrollments.append(count)

    # 2. كۇرس بويىچە ئوقۇغۇچى سانى
    course_stats = Course.objects.filter(
        instructor=teacher_profile
    ).annotate(
        student_count=Count('enrollments')
    ).order_by('-student_count')

    course_labels = [c.title for c in course_stats]
    course_data = [c.student_count for c in course_stats]

    # 3. ھالەت بويىچە تەقسىمات
    status_pending = enrollments.filter(status='pending').count()
    status_approved = enrollments.filter(status='approved').count()
    status_rejected = enrollments.filter(status='rejected').count()

    context = {
        'teacher': teacher_profile,
        'my_courses': my_courses,
        'enrollments': enrollments,
        'pending_enrollments': pending_enrollments,
        'pending_count': pending_enrollments.count(),
        'approved_count': enrollments.filter(status='approved').count(),
        'total_students': enrollments.values('user').distinct().count(),

        # ↓↓↓ يېڭى: چارت سانلىق مەلۇماتلىرى ↓↓↓
        'current_year': current_year,
        'monthly_labels': json.dumps(month_names_ug, ensure_ascii=False),
        'monthly_data': json.dumps(monthly_enrollments),
        'course_labels': json.dumps(course_labels, ensure_ascii=False),
        'course_data': json.dumps(course_data),
        'status_pending': status_pending,
        'status_approved': status_approved,
        'status_rejected': status_rejected,
        # ↑↑↑ چارت سانلىق مەلۇماتلىرى ↑↑↑
    }
    return render(request, 'teacher_dashboard.html', context)

@login_required
def approve_enrollment(request, enrollment_id):
    if not request.user.is_teacher():
        return redirect('index')

    try:
        teacher_profile = request.user.teacher_profile
        enrollment = get_object_or_404(
            Enrollment,
            id=enrollment_id,
            course__instructor=teacher_profile
        )
    except Teacher.DoesNotExist:
        return redirect('index')

    enrollment.status = 'approved'
    enrollment.teacher_note = request.POST.get('note', '')
    enrollment.save()

    # ئىچكى ئۇقتۇرۇش
    Notification.objects.create(
        user=enrollment.user,
        notification_type='approved',
        title='تىزىملىتىشىڭىز تەستىقلاندى!',
        message=f'«{enrollment.course.title}» كۇرسىغا تىزىملىتىشىڭىز {enrollment.course.instructor.name} تەرىپىدىن تەستىقلاندى.',
        course=enrollment.course
    )

    # ↓↓↓ Telegram ئۇقتۇرۇش ↓↓↓
    send_enrollment_approved(enrollment.user, enrollment.course)
    # ↑↑↑ Telegram ↑↑↑

    messages.success(request, f'«{enrollment.user.full_name}» نىڭ تىزىملىتىشى تەستىقلاندى.')
    return redirect('teacher_dashboard')


@login_required
def reject_enrollment(request, enrollment_id):
    if not request.user.is_teacher():
        return redirect('index')

    try:
        teacher_profile = request.user.teacher_profile
        enrollment = get_object_or_404(
            Enrollment,
            id=enrollment_id,
            course__instructor=teacher_profile
        )
    except Teacher.DoesNotExist:
        return redirect('index')

    enrollment.status = 'rejected'
    enrollment.teacher_note = request.POST.get('note', '')
    enrollment.save()

    # ئىچكى ئۇقتۇرۇش
    Notification.objects.create(
        user=enrollment.user,
        notification_type='rejected',
        title='تىزىملىتىشىڭىز رەت قىلىندى',
        message=f'«{enrollment.course.title}» كۇرسىغا تىزىملىتىشىڭىز رەت قىلىندى. سەۋەبى: {enrollment.teacher_note or "بېرىلمىگەن"}',
        course=enrollment.course
    )

    # ↓↓↓ Telegram ئۇقتۇرۇش ↓↓↓
    send_enrollment_rejected(enrollment.user, enrollment.course, enrollment.teacher_note)
    # ↑↑↑ Telegram ↑↑↑

    messages.info(request, f'«{enrollment.user.full_name}» نىڭ تىزىملىتىشى رەت قىلىندى.')
    return redirect('teacher_dashboard')


# ====================
# Admin Dashboard
# ====================
@staff_member_required
def admin_dashboard(request):
    from datetime import datetime
    import json

    # ئاساسلىق ستاتىستىكا
    total_courses = Course.objects.count()
    total_teachers = Teacher.objects.count()
    total_students = CustomUser.objects.filter(role='student').count()
    total_enrollments = Enrollment.objects.count()
    pending_enrollments = Enrollment.objects.filter(status='pending').count()
    approved_enrollments = Enrollment.objects.filter(status='approved').count()
    total_messages = Message.objects.count()
    unread_messages = Message.objects.filter(is_read=False).count()

    recent_enrollments = Enrollment.objects.select_related('user', 'course').order_by('-created_at')[:10]
    pending_list = Enrollment.objects.filter(status='pending').select_related('user', 'course')[:10]
    active_courses = Course.objects.annotate(
        enrollment_count=Count('enrollments')
    ).order_by('-enrollment_count')[:5]

    # ====================
    # 📊 چارت سانلىق مەلۇماتلىرى
    # ====================

    # ئۇيغۇرچە ئاي ناملىرى
    month_names_ug = [
        'يانۋار', 'فېۋرال', 'مارت', 'ئاپرېل', 'ماي', 'ئىيۇن',
        'ئىيۇل', 'ئاۋغۇست', 'سېنتەبىر', 'ئۆكتەبىر', 'نويابىر', 'دېكابىر'
    ]

    # 1. ئايلىق تىزىملىتىش سانى (يىل بويىچە)
    current_year = datetime.now().year
    monthly_enrollments = []
    for month in range(1, 13):
        count = Enrollment.objects.filter(
            created_at__year=current_year,
            created_at__month=month
        ).count()
        monthly_enrollments.append(count)

    # 2. كۇرس بويىچە تەقسىمات (ئەڭ كۆپ 6 كۇرس)
    course_distribution = Course.objects.annotate(
        student_count=Count('enrollments')
    ).filter(student_count__gt=0).order_by('-student_count')[:6]

    course_labels = [c.title for c in course_distribution]
    course_data = [c.student_count for c in course_distribution]

    # 3. ھالەت بويىچە تەقسىمات
    status_data = {
        'pending': Enrollment.objects.filter(status='pending').count(),
        'approved': Enrollment.objects.filter(status='approved').count(),
        'rejected': Enrollment.objects.filter(status='rejected').count(),
    }

    context = {
        'total_courses': total_courses,
        'total_teachers': total_teachers,
        'total_students': total_students,
        'total_enrollments': total_enrollments,
        'pending_enrollments': pending_enrollments,
        'approved_enrollments': approved_enrollments,
        'total_messages': total_messages,
        'unread_messages': unread_messages,
        'recent_enrollments': recent_enrollments,
        'pending_list': pending_list,
        'active_courses': active_courses,

        # ↓↓↓ يېڭى: چارت سانلىق مەلۇماتلىرى ↓↓↓
        'current_year': current_year,
        'monthly_labels': json.dumps(month_names_ug, ensure_ascii=False),
        'monthly_data': json.dumps(monthly_enrollments),
        'course_labels': json.dumps(course_labels, ensure_ascii=False),
        'course_data': json.dumps(course_data),
        'status_pending': status_data['pending'],
        'status_approved': status_data['approved'],
        'status_rejected': status_data['rejected'],
        # ↑↑↑ چارت سانلىق مەلۇماتلىرى ↑↑↑
    }
    return render(request, 'admin_dashboard.html', context)

# ====================
# ئۇقتۇرۇشلار
# ====================
@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('my_enrollments')


@login_required
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'بارلىق ئۇقتۇرۇشلار ئوقۇلدى.')
    return redirect('my_enrollments')


# ====================
# ئۇچۇرلار
# ====================
@login_required
def messages_view(request):
    received_messages = Message.objects.filter(receiver=request.user).select_related('sender', 'course')
    sent_messages = Message.objects.filter(sender=request.user).select_related('receiver', 'course')
    unread_count = received_messages.filter(is_read=False).count()

    context = {
        'received_messages': received_messages,
        'sent_messages': sent_messages,
        'unread_count': unread_count,
    }
    return render(request, 'messages.html', context)


@login_required
def send_message(request, receiver_id=None):
    receiver = None
    if receiver_id:
        receiver = get_object_or_404(CustomUser, id=receiver_id)

    if request.user.is_teacher() and receiver:
        try:
            teacher_profile = request.user.teacher_profile
            my_student_ids = Enrollment.objects.filter(
                course__instructor=teacher_profile
            ).values_list('user_id', flat=True)
            if receiver.id not in my_student_ids:
                messages.error(request, 'بۇ ئىشلەتكۈچى سىزنىڭ ئوقۇغۇچىڭىز ئەمەس.')
                return redirect('teacher_dashboard')
        except Teacher.DoesNotExist:
            pass

    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        message_text = request.POST.get('message', '').strip()
        course_id = request.POST.get('course', '')

        if not subject or not message_text:
            messages.error(request, 'ماۋزۇ ۋە ئۇچۇر بوش بولماسلىقى كېرەك.')
        else:
            course = Course.objects.filter(id=course_id).first() if course_id else None
            Message.objects.create(
                sender=request.user,
                receiver=receiver,
                subject=subject,
                message=message_text,
                course=course
            )

            # ↓↓↓ Telegram ئۇقتۇرۇش ↓↓↓
            send_new_message(receiver, request.user.full_name or request.user.username, subject)
            # ↑↑↑ Telegram ↑↑↑

            messages.success(request, f'ئۇچۇر {receiver.full_name} غا يوللاندى!')
            return redirect('messages_view')

    context = {'receiver': receiver}
    return render(request, 'send_message.html', context)


@login_required
def message_detail(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    if request.user != message.sender and request.user != message.receiver:
        messages.error(request, 'بۇ ئۇچۇرنى كۆرۈش ھوقۇقىڭىز يوق.')
        return redirect('messages_view')

    if request.user == message.receiver and not message.is_read:
        message.is_read = True
        message.save()

    return render(request, 'message_detail.html', {'message': message})


@login_required
def get_my_students(request):
    if not request.user.is_teacher():
        return redirect('index')

    try:
        teacher_profile = request.user.teacher_profile
        students = CustomUser.objects.filter(
            enrollments__course__instructor=teacher_profile
        ).distinct()
    except Teacher.DoesNotExist:
        students = CustomUser.objects.none()

    return render(request, 'my_students.html', {'students': students})


# ====================
# ئىزدەش
# ====================
def search_view(request):
    query = request.GET.get('q', '').strip()
    courses = []
    teachers = []

    if query:
        courses = Course.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(badge__icontains=query) |
            Q(instructor__name__icontains=query)
        ).distinct()

        teachers = Teacher.objects.filter(
            Q(name__icontains=query) |
            Q(role__icontains=query) |
            Q(description__icontains=query)
        ).distinct()

    context = {
        'query': query,
        'courses': courses,
        'teachers': teachers,
        'total_results': len(courses) + len(teachers),
    }
    return render(request, 'search.html', context)


# ====================
# دەرس جەدۋىلى
# ====================
@login_required
def my_schedule(request):
    """ئوقۇغۇچىنىڭ دەرس جەدۋىلى"""
    approved_courses = Enrollment.objects.filter(
        user=request.user,
        status='approved'
    ).values_list('course_id', flat=True)

    lessons = Lesson.objects.filter(
        course_id__in=approved_courses,
        is_active=True
    ).select_related('course').order_by('day_of_week', 'start_time')

    schedule_by_day = {i: [] for i in range(7)}
    for lesson in lessons:
        schedule_by_day[lesson.day_of_week].append(lesson)

    today_python = datetime.now().weekday()
    today_our = (today_python + 1) % 7

    context = {
        'schedule_by_day': schedule_by_day,
        'lessons': lessons,
        'today': today_our,
        'total_lessons': lessons.count(),
    }
    return render(request, 'my_schedule.html', context)


@login_required
def teacher_schedule(request):
    """ئوقۇتقۇچىنىڭ دەرس جەدۋىلى"""
    if not request.user.is_teacher():
        return redirect('index')

    try:
        teacher_profile = request.user.teacher_profile
    except Teacher.DoesNotExist:
        return redirect('index')

    lessons = Lesson.objects.filter(
        course__instructor=teacher_profile,
        is_active=True
    ).select_related('course').order_by('day_of_week', 'start_time')

    schedule_by_day = {i: [] for i in range(7)}
    for lesson in lessons:
        schedule_by_day[lesson.day_of_week].append(lesson)

    today_python = datetime.now().weekday()
    today_our = (today_python + 1) % 7

    context = {
        'schedule_by_day': schedule_by_day,
        'lessons': lessons,
        'today': today_our,
        'total_lessons': lessons.count(),
        'teacher': teacher_profile,
    }
    return render(request, 'teacher_schedule.html', context)


# ====================
# ھازىرلىق سىستېمىسى
# ====================
@login_required
def mark_attendance(request, lesson_id):
    """ئوقۇتقۇچى ھازىرلىق بەلگىلەيدۇ"""
    if not request.user.is_teacher():
        messages.error(request, 'پەقەت ئوقۇتقۇچىلار ھازىرلىق بەلگىلەيدۇ.')
        return redirect('index')

    lesson = get_object_or_404(Lesson, id=lesson_id)

    try:
        teacher_profile = request.user.teacher_profile
        if lesson.course.instructor != teacher_profile:
            messages.error(request, 'بۇ دەرس سىزنىڭ كۇرسىڭىز ئەمەس.')
            return redirect('teacher_dashboard')
    except Teacher.DoesNotExist:
        return redirect('index')

    approved_students = Enrollment.objects.filter(
        course=lesson.course,
        status='approved'
    ).select_related('user')

    today = date.today()

    if request.method == 'POST':
        session, created = AttendanceSession.objects.get_or_create(
            lesson=lesson,
            session_date=today,
            defaults={'created_by': request.user}
        )

        for enrollment in approved_students:
            student = enrollment.user
            status = request.POST.get(f'status_{student.id}', 'present')
            note = request.POST.get(f'note_{student.id}', '')

            Attendance.objects.update_or_create(
                lesson=lesson,
                student=student,
                attendance_date=today,
                defaults={
                    'status': status,
                    'note': note,
                    'marked_by': request.user
                }
            )

        messages.success(request, f'«{lesson.title}» دەرسىنىڭ ھازىرلىقى ساقلىنىۋاتىدۇ.')
        return redirect('teacher_dashboard')

    existing_attendance = {
        att.student_id: att
        for att in Attendance.objects.filter(
            lesson=lesson,
            attendance_date=today
        )
    }

    context = {
        'lesson': lesson,
        'students': approved_students,
        'existing_attendance': existing_attendance,
        'today': today,
    }
    return render(request, 'mark_attendance.html', context)


@login_required
def attendance_report(request):
    """ئوقۇغۇچىنىڭ ھازىرلىق دوكلاتى"""
    if not request.user.is_authenticated:
        return redirect('index')

    attendances = Attendance.objects.filter(
        student=request.user
    ).select_related('lesson', 'lesson__course').order_by('-attendance_date')

    total = attendances.count()
    present = attendances.filter(status='present').count()
    absent = attendances.filter(status='absent').count()
    late = attendances.filter(status='late').count()

    attendance_rate = round((present / total * 100), 1) if total > 0 else 0

    context = {
        'attendances': attendances,
        'total': total,
        'present': present,
        'absent': absent,
        'late': late,
        'attendance_rate': attendance_rate,
    }
    return render(request, 'attendance_report.html', context)


@login_required
def teacher_attendance_report(request):
    """ئوقۇتقۇچىنىڭ ھازىرلىق دوكلاتى"""
    if not request.user.is_teacher():
        return redirect('index')

    try:
        teacher_profile = request.user.teacher_profile
    except Teacher.DoesNotExist:
        return redirect('index')

    my_courses = Course.objects.filter(instructor=teacher_profile)

    attendances = Attendance.objects.filter(
        lesson__course__in=my_courses
    ).select_related('student', 'lesson', 'lesson__course').order_by('-attendance_date')[:50]

    context = {
        'attendances': attendances,
        'my_courses': my_courses,
    }
    return render(request, 'teacher_attendance_report.html', context)


# ====================
# ئىمتىھان/باھا سىستېمىسى
# ====================
@login_required
def exam_list(request):
    """بارلىق ئىمتىھانلار تىزىملىكى"""
    if request.user.is_teacher():
        try:
            teacher_profile = request.user.teacher_profile
            exams = Exam.objects.filter(
                course__instructor=teacher_profile
            ).select_related('course').order_by('-exam_date')
        except Teacher.DoesNotExist:
            exams = Exam.objects.none()
    elif request.user.is_staff or request.user.role == 'admin':
        exams = Exam.objects.all().select_related('course').order_by('-exam_date')
    else:
        # ئوقۇغۇچى پەقەت ئۆزى تىزىملانغان كۇرسنىڭ ئىمتىھانلىرىنى كۆرىدۇ
        approved_courses = Enrollment.objects.filter(
            user=request.user,
            status='approved'
        ).values_list('course_id', flat=True)

        exams = Exam.objects.filter(
            course_id__in=approved_courses,
            is_published=True
        ).select_related('course').order_by('-exam_date')

    context = {
        'exams': exams,
    }
    return render(request, 'exam_list.html', context)


@login_required
def grade_exam(request, exam_id):
    """ئوقۇتقۇچى ئىمتىھان نەتىجىسى كىرگۈزىدۇ"""
    exam = get_object_or_404(Exam, id=exam_id)

    # ئوقۇتقۇچى ھوقۇقىنى تەكشۈرۈش
    if not request.user.is_teacher():
        messages.error(request, 'پەقەت ئوقۇتقۇچىلار نەتىجە كىرگۈزەلەيدۇ.')
        return redirect('index')

    try:
        teacher_profile = request.user.teacher_profile
        if exam.course.instructor != teacher_profile:
            messages.error(request, 'بۇ ئىمتىھان سىزنىڭ كۇرسىڭىز ئەمەس.')
            return redirect('exam_list')
    except Teacher.DoesNotExist:
        return redirect('index')

    # تەستىقلانغان ئوقۇغۇچىلارنى ئېلىش
    approved_students = Enrollment.objects.filter(
        course=exam.course,
        status='approved'
    ).select_related('user')

    if request.method == 'POST':
        saved_count = 0
        for enrollment in approved_students:
            student = enrollment.user
            score_key = f'score_{student.id}'
            note_key = f'note_{student.id}'

            score_str = request.POST.get(score_key, '')
            note = request.POST.get(note_key, '')

            if score_str:
                try:
                    score = float(score_str)
                    if 0 <= score <= float(exam.total_score):
                        ExamResult.objects.update_or_create(
                            exam=exam,
                            student=student,
                            defaults={
                                'score': score,
                                'note': note,
                                'graded_by': request.user
                            }
                        )
                        saved_count += 1
                except ValueError:
                    continue

        # ئىمتىھاننى ئېلان قىلىش
        if request.POST.get('publish'):
            exam.is_published = True
            exam.save()

        messages.success(request, f'{saved_count} ئوقۇغۇچىنىڭ نەتىجىسى ساقلاندى.')
        return redirect('exam_list')

    # بار بولغان نەتىجىلەرنى ئېلىش
    existing_results = {
        r.student_id: r
        for r in ExamResult.objects.filter(exam=exam)
    }

    context = {
        'exam': exam,
        'students': approved_students,
        'existing_results': existing_results,
    }
    return render(request, 'grade_exam.html', context)


@login_required
def exam_detail(request, exam_id):
    """ئىمتىھان تەپسىلاتى ۋە نەتىجىلەر"""
    exam = get_object_or_404(Exam, id=exam_id)

    # ھوقۇق تەكشۈرۈش
    can_view = False
    is_teacher = False

    if request.user.is_staff or request.user.role == 'admin':
        can_view = True
    elif request.user.is_teacher():
        try:
            teacher_profile = request.user.teacher_profile
            if exam.course.instructor == teacher_profile:
                can_view = True
                is_teacher = True
        except Teacher.DoesNotExist:
            pass
    else:
        # ئوقۇغۇچى - پەقەت ئېلان قىلىنغان ئىمتىھان ۋە ئۆزى تىزىملانغان كۇرس
        if exam.is_published:
            enrolled = Enrollment.objects.filter(
                user=request.user,
                course=exam.course,
                status='approved'
            ).exists()
            if enrolled:
                can_view = True

    if not can_view:
        messages.error(request, 'بۇ ئىمتىھاننى كۆرۈش ھوقۇقىڭىز يوق.')
        return redirect('exam_list')

    results = ExamResult.objects.filter(exam=exam).select_related('student')

    # ئوقۇغۇچى بولسا پەقەت ئۆز نەتىجىسىنى كۆرسىتىش
    my_result = None
    if not is_teacher and not request.user.is_staff:
        my_result = results.filter(student=request.user).first()

    context = {
        'exam': exam,
        'results': results,
        'my_result': my_result,
        'is_teacher': is_teacher,
        'average_score': exam.get_average_score(),
        'pass_rate': exam.get_pass_rate(),
        'total_students': results.count(),
    }
    return render(request, 'exam_detail.html', context)


@login_required
def my_grades(request):
    """ئوقۇغۇچىنىڭ بارلىق نەتىجىلىرى"""
    results = ExamResult.objects.filter(
        student=request.user,
        exam__is_published=True
    ).select_related('exam', 'exam__course').order_by('-exam__exam_date')

    # ئومۇمىي ئوتتۇرىچە
    total_score = 0
    total_max = 0
    passed = 0

    for r in results:
        total_score += float(r.score)
        total_max += float(r.exam.total_score)
        if r.is_passed():
            passed += 1

    overall_percentage = round((total_score / total_max) * 100, 1) if total_max > 0 else 0
    pass_rate = round((passed / results.count()) * 100, 1) if results.count() > 0 else 0

    context = {
        'results': results,
        'total_exams': results.count(),
        'overall_percentage': overall_percentage,
        'pass_rate': pass_rate,
        'passed_count': passed,
        'failed_count': results.count() - passed,
    }
    return render(request, 'my_grades.html', context)


# ====================
# گۇۋاھنامە سىستېمىسى
# ====================

@login_required
def my_certificates(request):
    """ئوقۇغۇچىنىڭ گۇۋاھنامىلىرى تىزىملىكى"""
    certificates = Certificate.objects.filter(
        student=request.user
    ).select_related('course', 'course__instructor').order_by('-issue_date')

    context = {
        'certificates': certificates,
    }
    return render(request, 'my_certificates.html', context)


@login_required
def download_certificate(request, certificate_id):
    """گۇۋاھنامە بېسىش بېتى"""
    certificate = get_object_or_404(Certificate, id=certificate_id)

    # ھوقۇق تەكشۈرۈش
    if request.user != certificate.student and not request.user.is_staff:
        if request.user.is_teacher():
            try:
                teacher_profile = request.user.teacher_profile
                if certificate.course.instructor != teacher_profile:
                    messages.error(request, 'ھوقۇقىڭىز يوق.')
                    return redirect('index')
            except Teacher.DoesNotExist:
                messages.error(request, 'ھوقۇقىڭىز يوق.')
                return redirect('index')
        else:
            messages.error(request, 'ھوقۇقىڭىز يوق.')
            return redirect('index')

    context = {
        'certificate': certificate,
    }
    return render(request, 'certificate_print.html', context)


@login_required
def issue_certificate(request, enrollment_id):
    """ئوقۇتقۇچى گۇۋاھنامە بېرىدۇ"""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)

    if not request.user.is_teacher() and not request.user.is_staff:
        messages.error(request, 'ھوقۇقىڭىز يوق.')
        return redirect('index')

    existing = Certificate.objects.filter(
        student=enrollment.user,
        course=enrollment.course
    ).first()

    if existing:
        messages.info(request, 'بۇ ئوقۇغۇچىغا ئاللىبۇرۇن گۇۋاھنامە بېرىلگەن.')
        return redirect('teacher_dashboard')

    certificate = Certificate.objects.create(
        student=enrollment.user,
        course=enrollment.course,
        issued_by=request.user
    )

    messages.success(request, f'«{enrollment.user.full_name}» غا گۇۋاھنامە بېرىلدى.')
    return redirect('teacher_dashboard')


# ====================
# كۇرس باھالاش سىستېمىسى
# ====================
@login_required
def rate_course(request, course_id):
    """ئوقۇغۇچى كۇرسنى باھالايدۇ"""
    course = get_object_or_404(Course, id=course_id)

    # ئوقۇغۇچى بۇ كۇرسقا تىزىملانغانمۇ؟
    enrolled = Enrollment.objects.filter(
        user=request.user,
        course=course,
        status='approved'
    ).exists()

    if not enrolled:
        messages.error(request, 'بۇ كۇرسنى باھالاش ئۈچۈن ئالدى بىلەن تىزىملىنىڭ.')
        return redirect('course_detail', course_id=course.id)

    # بار بولغان باھانى ئېلىش
    existing_rating = CourseRating.objects.filter(
        course=course,
        student=request.user
    ).first()

    if request.method == 'POST':
        rating_value = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        if not rating_value or not rating_value.isdigit():
            messages.error(request, 'باھا تاللاڭ (1-5 يۇلتۇز).')
            return redirect('course_detail', course_id=course.id)

        rating_value = int(rating_value)
        if rating_value < 1 or rating_value > 5:
            messages.error(request, 'باھا 1 دىن 5 كىچە بولۇشى كېرەك.')
            return redirect('course_detail', course_id=course.id)

        if existing_rating:
            # يېڭىلاش
            existing_rating.rating = rating_value
            existing_rating.comment = comment
            existing_rating.save()
            messages.success(request, 'باھايىڭىز يېڭىلاندى! رەھمەت.')
        else:
            # يېڭى قۇرۇش
            CourseRating.objects.create(
                course=course,
                student=request.user,
                rating=rating_value,
                comment=comment
            )
            messages.success(request, 'باھايىڭىز قوبۇل قىلىندى! رەھمەت.')

        return redirect('course_detail', course_id=course.id)

    # GET بولسا كۇرس تەپسىلاتىغا يۆتكەش
    return redirect('course_detail', course_id=course.id)


@login_required
def delete_rating(request, rating_id):
    """ئوقۇغۇچى ئۆز باھاسىنى ئۆچۈرىدۇ"""
    rating = get_object_or_404(CourseRating, id=rating_id)

    if rating.student != request.user:
        messages.error(request, 'پەقەت ئۆزىڭىزنىڭ باھاسىنى ئۆچۈرەلەيسىز.')
        return redirect('index')

    course_id = rating.course.id
    rating.delete()
    messages.success(request, 'باھايىڭىز ئۆچۈرۈلدى.')
    return redirect('course_detail', course_id=course_id)


def get_course_rating_stats(course):
    """كۇرسنىڭ باھا ستاتىستىكىسىنى ھېسابلاش"""
    ratings = CourseRating.objects.filter(course=course)
    total = ratings.count()

    if total == 0:
        return {
            'average': 0,
            'total': 0,
            'stars': [0] * 5,
        }

    avg = sum(r.rating for r in ratings) / total

    # ھەر دەرىجىدىكى باھا سانى
    stars = [0] * 5
    for r in ratings:
        stars[r.rating - 1] += 1

    return {
        'average': round(avg, 1),
        'total': total,
        'stars': stars,
        'stars_reverse': stars[::-1],  # 5 دىن 1 گە
    }