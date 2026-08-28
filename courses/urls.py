from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # ئاساسلىق بەتلەر
    path('', views.index, name='index'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # كۇرس
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),

    # ئوقۇغۇچى
    path('my-enrollments/', views.my_enrollments, name='my_enrollments'),
    path('cancel-enrollment/<int:enrollment_id>/', views.cancel_enrollment, name='cancel_enrollment'),
    path('my-schedule/', views.my_schedule, name='my_schedule'),
    path('profile/', views.profile_view, name='profile'),

    # ئوقۇتقۇچى
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher-schedule/', views.teacher_schedule, name='teacher_schedule'),
    path('approve-enrollment/<int:enrollment_id>/', views.approve_enrollment, name='approve_enrollment'),
    path('reject-enrollment/<int:enrollment_id>/', views.reject_enrollment, name='reject_enrollment'),
    path('my-students/', views.get_my_students, name='my_students'),

    # Admin Dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # ئۇقتۇرۇشلار
    path('notification/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),

    # ئۇچۇرلار
    path('messages/', views.messages_view, name='messages_view'),
    path('messages/send/', views.send_message, name='send_message'),
    path('messages/send/<int:receiver_id>/', views.send_message, name='send_message_to'),
    path('messages/<int:message_id>/', views.message_detail, name='message_detail'),

    # ئىزدەش
    path('search/', views.search_view, name='search'),

    # پارول ئەسلىگە كەلتۈرۈش
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='password_reset/password_reset.html',
             email_template_name='password_reset/password_reset_email.html',
             subject_template_name='password_reset/password_reset_subject.txt',
             success_url='/password-reset/done/'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='password_reset/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='password_reset/password_reset_confirm.html',
             success_url='/password-reset-complete/'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='password_reset/password_reset_complete.html'
         ),
         name='password_reset_complete'),

# ھازىرلىق سىستېمىسى
    path('mark-attendance/<int:lesson_id>/', views.mark_attendance, name='mark_attendance'),
    path('attendance-report/', views.attendance_report, name='attendance_report'),
    path('teacher-attendance-report/', views.teacher_attendance_report, name='teacher_attendance_report'),
    # ئىمتىھان/باھا سىستېمىسى
    path('exams/', views.exam_list, name='exam_list'),
    path('exams/<int:exam_id>/', views.exam_detail, name='exam_detail'),
    path('exams/<int:exam_id>/grade/', views.grade_exam, name='grade_exam'),
    path('my-grades/', views.my_grades, name='my_grades'),
    # گۇۋاھنامە سىستېمىسى
    path('certificates/', views.my_certificates, name='my_certificates'),
    path('certificate/<int:certificate_id>/download/', views.download_certificate, name='download_certificate'),
    path('issue-certificate/<int:enrollment_id>/', views.issue_certificate, name='issue_certificate'),
# كۇرس باھالاش
    path('course/<int:course_id>/rate/', views.rate_course, name='rate_course'),
    path('rating/<int:rating_id>/delete/', views.delete_rating, name='delete_rating'),
]
