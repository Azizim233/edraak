from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, Course, Teacher, Review, Enrollment, Work,
    Notification, Message, SiteSettings, CourseMaterial,
    Lesson,Announcement
)


# ====================
# ئىشلەتكۈچىلەر Admin
# ====================
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('full_name', 'email', 'phone', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'full_name', 'phone')

    fieldsets = UserAdmin.fieldsets + (
        ('قوشۇمچە ئۇچۇرلار', {
            'fields': ('full_name', 'phone', 'telegram_id', 'role')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('قوشۇمچە ئۇچۇرلار', {
            'fields': ('full_name', 'phone', 'telegram_id', 'role')
        }),
    )


# ====================
# ئوقۇتقۇچىلار Admin
# ====================
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'user', 'course_count', 'order')
    list_editable = ('order',)
    search_fields = ('name', 'role')
    list_filter = ('role',)

    fieldsets = (
        ('كىرىش ھېساباتى', {
            'fields': ('user',),
            'description': '⚠️ ئالدى بىلەن ئوقۇتقۇچى role لىك ئىشلەتكۈچى قۇرۇڭ'
        }),
        ('ئوقۇتقۇچى ئۇچۇرلىرى', {
            'fields': ('name', 'role', 'description', 'photo', 'emoji', 'order')
        }),
    )

    def course_count(self, obj):
        return obj.courses.count()

    course_count.short_description = 'كۇرس سانى'


# ====================
# كۇرس ماتېرىياللىرى Inline
# ====================
class CourseMaterialInline(admin.TabularInline):
    model = CourseMaterial
    extra = 1
    fields = ('title', 'material_type', 'file', 'url', 'order')


# ====================
# دەرس جەدۋىلى Inline (يېڭى قوشۇلدى)
# ====================
class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ('title', 'day_of_week', 'start_time', 'end_time', 'location', 'online_link', 'is_active')


# ====================
# كۇرسىلار Admin
# ====================
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'badge', 'emoji', 'instructor', 'is_active', 'order', 'enrolled_count', 'materials_count',
                    'lessons_count')
    list_filter = ('badge', 'is_active', 'instructor')
    search_fields = ('title', 'description')
    list_editable = ('is_active', 'order')

    fieldsets = (
        ('ئاساسلىق ئۇچۇرلار', {
            'fields': ('title', 'badge', 'emoji', 'description', 'full_description', 'cover_image')
        }),
        ('ئۇستاز', {
            'fields': ('instructor',),
            'description': '⚠️ ئالدى بىلەن ئوقۇتقۇچى (Teacher) قۇرۇڭ'
        }),
        ('تەپسىلاتلار', {
            'fields': ('textbook', 'level', 'teaching_method', 'age_group', 'special_features')
        }),
        ('باشقۇرۇش', {
            'fields': ('duration', 'schedule', 'price', 'max_students', 'is_active', 'order')
        }),
    )

    # ↓↓↓ ئىككى Inline قوشۇلدى ↓↓↓
    inlines = [CourseMaterialInline, LessonInline]

    # ↑↑↑ Inline لار ئاخىرلاشتى ↑↑↑

    def enrolled_count(self, obj):
        return obj.enrollments.count()

    enrolled_count.short_description = 'تىزىملانغانلار'

    def materials_count(self, obj):
        return obj.materials.count()

    materials_count.short_description = 'ماتېرىياللار'

    def lessons_count(self, obj):
        return obj.lessons.count()

    lessons_count.short_description = 'دەرسلەر'


# ====================
# كۇرس ماتېرىياللىرى Admin
# ====================
@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'material_type', 'order', 'created_at')
    list_filter = ('material_type', 'course')
    search_fields = ('title', 'course__title')
    list_editable = ('order',)

    fieldsets = (
        ('ئاساسلىق ئۇچۇرلار', {
            'fields': ('course', 'title', 'material_type', 'description')
        }),
        ('مەزمۇن', {
            'fields': ('file', 'url'),
            'description': '💡 PDF/Doc ئۈچۈن "ھۆججەت"، Video/ئۇلىنىش ئۈچۈن "ئۇلىنىش" ئىشلىتىڭ'
        }),
        ('تەرتىپ', {
            'fields': ('order',)
        }),
    )


# ====================
# دەرس جەدۋىلى Admin (يېڭى قوشۇلدى)
# ====================
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'get_day_name', 'start_time', 'end_time', 'location', 'is_active')
    list_filter = ('day_of_week', 'course', 'is_active')
    search_fields = ('title', 'course__title')
    list_editable = ('is_active',)

    fieldsets = (
        ('ئاساسلىق ئۇچۇرلار', {
            'fields': ('course', 'title', 'description')
        }),
        ('ۋاقتى', {
            'fields': ('day_of_week', 'start_time', 'end_time')
        }),
        ('ئورنى', {
            'fields': ('location', 'online_link')
        }),
        ('باشقۇرۇش', {
            'fields': ('is_active',)
        }),
    )


# ====================
# پىكىرلەر Admin
# ====================
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'text_preview', 'order')
    list_editable = ('order',)
    search_fields = ('author', 'text')

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text

    text_preview.short_description = 'پىكىر'


# ====================
# تىزىملىتىشلار Admin
# ====================
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'get_teacher', 'status', 'created_at')
    list_filter = ('status', 'course', 'course__instructor')
    list_editable = ('status',)
    search_fields = ('user__full_name', 'user__email', 'course__title')

    def get_teacher(self, obj):
        return obj.course.instructor.name if obj.course.instructor else '-'

    get_teacher.short_description = 'ئۇستاز'


# ====================
# خىزمەتلەر Admin
# ====================
@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    list_editable = ('order',)
    search_fields = ('title',)


# ====================
# ئۇقتۇرۇشلار Admin
# ====================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__full_name', 'title', 'message')
    list_editable = ('is_read',)


# ====================
# ئۇچۇرلار Admin
# ====================
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__full_name', 'receiver__full_name', 'subject')


# ====================
# توربەت تەڭشەكلىرى Admin
# ====================
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'site_name_ug', 'email')

    fieldsets = (
        ('ئاساسلىق ئۇچۇرلار', {
            'fields': ('site_name', 'site_name_ug', 'tagline', 'logo')
        }),
        ('بىز ھەققىدە (About Us)', {
            'fields': ('about_title_ug', 'about_text_ug', 'about_title_en', 'about_text_en')
        }),
        ('ئالاقىلىشىش (Contact)', {
            'fields': ('whatsapp', 'telegram', 'email', 'phone', 'address')
        }),
        ('Footer', {
            'fields': ('footer_text',)
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


from .models import FAQ


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question_preview', 'category', 'order', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('question', 'answer')
    list_editable = ('order', 'is_active')

    fieldsets = (
        ('سوئال-جاۋاب', {
            'fields': ('question', 'answer')
        }),
        ('تۈر ۋە تەرتىپ', {
            'fields': ('category', 'order', 'is_active')
        }),
    )

    def question_preview(self, obj):
        return obj.question[:60] + '...' if len(obj.question) > 60 else obj.question

    question_preview.short_description = 'سوئال'


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title_preview', 'announcement_type', 'target_audience', 'is_active', 'order', 'start_date',
                    'end_date')
    list_filter = ('announcement_type', 'target_audience', 'is_active')
    search_fields = ('title', 'content')
    list_editable = ('is_active', 'order')
    date_hierarchy = 'start_date'

    fieldsets = (
        ('ئېلان مەزمۇنى', {
            'fields': ('title', 'content')
        }),
        ('تىپى ۋە نىشانى', {
            'fields': ('announcement_type', 'target_audience')
        }),
        ('ئۇلىنىش (ئىختىيارى)', {
            'fields': ('link_url', 'link_text'),
            'classes': ('collapse',),
            'description': 'ئېلانغا ئۇلىنىش قوشماقچى بولسىڭىز تولدۇرۇڭ'
        }),
        ('باشقۇرۇش', {
            'fields': ('is_active', 'end_date', 'order')
        }),
    )

    def title_preview(self, obj):
        return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title

    title_preview.short_description = 'ئېلان ماۋزۇسى'

from .models import Attendance, AttendanceSession


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'attendance_date', 'status', 'marked_by')
    list_filter = ('status', 'attendance_date', 'lesson')
    search_fields = ('student__full_name', 'lesson__title')
    list_editable = ('status',)


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'session_date', 'topic', 'created_by')
    list_filter = ('session_date', 'lesson')
    search_fields = ('lesson__title', 'topic')


from .models import Exam, ExamResult


class ExamResultInline(admin.TabularInline):
    model = ExamResult
    extra = 0
    fields = ('student', 'score', 'note')
    readonly_fields = ('graded_at',)


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'exam_type', 'exam_date', 'total_score', 'is_published', 'results_count',
                    'average_score')
    list_filter = ('exam_type', 'is_published', 'course')
    search_fields = ('title', 'course__title')
    list_editable = ('is_published',)
    date_hierarchy = 'exam_date'
    inlines = [ExamResultInline]

    fieldsets = (
        ('ئاساسلىق ئۇچۇرلار', {
            'fields': ('course', 'title', 'exam_type', 'description')
        }),
        ('تەپسىلاتلار', {
            'fields': ('total_score', 'exam_date', 'is_published')
        }),
    )

    def results_count(self, obj):
        return obj.get_results_count()

    results_count.short_description = 'نەتىجە سانى'

    def average_score(self, obj):
        return obj.get_average_score()

    average_score.short_description = 'ئوتتۇرىچە'


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'score', 'percentage', 'grade', 'status')
    list_filter = ('exam', 'exam__course')
    search_fields = ('student__full_name', 'exam__title')

    def percentage(self, obj):
        return f"{obj.get_percentage()}%"

    percentage.short_description = 'پىرسەنت'

    def grade(self, obj):
        return obj.get_grade()

    grade.short_description = 'باھا'

    def status(self, obj):
        return obj.get_status_text()

    status.short_description = 'ھالەت'

from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'certificate_number', 'issue_date', 'issued_by')
    list_filter = ('issue_date', 'course')
    search_fields = ('student__full_name', 'course__title', 'certificate_number')
    readonly_fields = ('certificate_number', 'issue_date')


from .models import CourseRating


@admin.register(CourseRating)
class CourseRatingAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'rating_display', 'comment_preview', 'created_at')
    list_filter = ('rating', 'course')
    search_fields = ('student__full_name', 'course__title', 'comment')

    def rating_display(self, obj):
        return obj.get_rating_stars()

    rating_display.short_description = 'باھا'

    def comment_preview(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment

    comment_preview.short_description = 'ئىنكاس'