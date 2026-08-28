from django.contrib.auth.models import AbstractUser
from django.db import models


# ====================
# ئىشلەتكۈچى Model
# ====================
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'ئوقۇغۇچى'),
        ('teacher', 'ئوقۇتقۇچى'),
        ('admin', 'باشقۇرغۇچى'),
    ]

    phone = models.CharField(max_length=20, blank=True, verbose_name="تېلېفون نومۇرى")
    telegram_id = models.CharField(max_length=100, blank=True, verbose_name="تېلېگرامما ئادرېسى")
    full_name = models.CharField(max_length=200, blank=True, verbose_name="ئىسمى فامىلىسى")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student', verbose_name="رولى")

    class Meta:
        verbose_name = "ئىشلەتكۈچى"
        verbose_name_plural = "ئىشلەتكۈچىلەر"

    def __str__(self):
        return self.full_name or self.username

    def is_teacher(self):
        return self.role == 'teacher'

    def is_student(self):
        return self.role == 'student'


# ====================
# ئوقۇتقۇچىلار قوشۇنى Model (Team)
# ====================
class Teacher(models.Model):
    # ↓↓↓ ئىشلەتكۈچى ھېساباتى بىلەن باغلىنىش ↓↓↓
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='teacher_profile',
        verbose_name="كىرىش ھېساباتى (User)",
        limit_choices_to={'role': 'teacher'}
    )

    name = models.CharField(max_length=100, verbose_name="ئىسمى")
    role = models.CharField(max_length=100, verbose_name="ۋەزىپىسى")
    description = models.TextField(verbose_name="چۈشەندۈرۈش")
    photo = models.ImageField(upload_to='teachers/', blank=True, null=True, verbose_name="رەسىم")
    emoji = models.CharField(max_length=10, blank=True, verbose_name="ئېموجى")
    order = models.IntegerField(default=0, verbose_name="تەرتىپ نومۇرى")

    class Meta:
        verbose_name = "ئوقۇتقۇچى (Team)"
        verbose_name_plural = "ئوقۇتقۇچىلار قوشۇنى"
        ordering = ['order']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # ئەگەر user تاللانغان بولسا، ئىسمىنى ئاپتوماتىك تولدۇرۇش
        if self.user and not self.name:
            self.name = self.user.full_name or self.user.username
        super().save(*args, **kwargs)

    def get_students(self):
        """بۇ ئوقۇتقۇچىنىڭ بارلىق ئوقۇغۇچىلىرىنى قايتۇرىدۇ"""
        return Enrollment.objects.filter(course__instructor=self).select_related('user', 'course')


# ====================
class Course(models.Model):
    BADGE_CHOICES = [
        ('تور + سىنىپ', 'تور + سىنىپ'),
        ('بالىلار', 'بالىلار'),
        ('تېخنىكا', 'تېخنىكا'),
        ('ئىلمىي ساۋات', 'ئىلمىي ساۋات'),
        ('كۆپ تىللىق', 'كۆپ تىللىق'),
        ('مەخسۇس سىنىپ', 'مەخسۇس سىنىپ'),
    ]

    title = models.CharField(max_length=200, verbose_name="كۇرس ئىسمى")
    badge = models.CharField(max_length=50, choices=BADGE_CHOICES, verbose_name="بەلگە")

    # ↓↓↓ يېڭى قوشۇلغان مەيدان ↓↓↓
    emoji = models.CharField(max_length=50, blank=True, verbose_name="ئىموجى/Icon")

    description = models.TextField(verbose_name="چۈشەندۈرۈش")
    textbook = models.CharField(max_length=200, blank=True, verbose_name="ئاساسلىق دەرسلىك")
    level = models.CharField(max_length=100, blank=True, verbose_name="سەۋىيە تەلەپلىرى")
    teaching_method = models.CharField(max_length=200, blank=True, verbose_name="ئوقۇتۇش شەكلى")
    age_group = models.CharField(max_length=100, blank=True, verbose_name="مۇۋاپىق ياش")
    special_features = models.CharField(max_length=300, blank=True, verbose_name="ئالاھىدىلىكى")
    is_active = models.BooleanField(default=True, verbose_name="ئاكتىپمۇ؟")
    order = models.IntegerField(default=0, verbose_name="تەرتىپ نومۇرى")
    created_at = models.DateTimeField(auto_now_add=True)

    full_description = models.TextField(blank=True, verbose_name="تولۇق چۈشەندۈرۈش")
    duration = models.CharField(max_length=100, blank=True, verbose_name="ۋاقتى")
    schedule = models.CharField(max_length=200, blank=True, verbose_name="دەرس ۋاقتى")
    price = models.CharField(max_length=100, blank=True, verbose_name="باھاسى")
    max_students = models.IntegerField(default=20, verbose_name="ئەڭ كۆپ ئوقۇغۇچى")
    cover_image = models.ImageField(upload_to='courses/', blank=True, null=True, verbose_name="رەسىم")

    instructor = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses',
        verbose_name="مەسئۇل ئۇستاز"
    )

    class Meta:
        verbose_name = "كۇرس"
        verbose_name_plural = "كۇرسىلار"
        ordering = ['order']

    def __str__(self):
        return self.title

    def get_enrolled_count(self):
        return self.enrollments.count()

    def is_full(self):
        return self.get_enrolled_count() >= self.max_students


# ====================
# پىكىر Model
# ====================
class Review(models.Model):
    text = models.TextField(verbose_name="پىكىر")
    author = models.CharField(max_length=100, verbose_name="ئاپتور")
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name = "پىكىر"
        verbose_name_plural = "پىكىرلەر"
        ordering = ['order']

    def __str__(self):
        return self.author


# ====================
# تىزىملىتىش Model
# ====================
class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'كۈتۈلۈۋاتىدۇ'),
        ('approved', 'تەستىقلاندى'),
        ('rejected', 'رەت قىلىندى'),
    ]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name="ئوقۇغۇچى",
        related_name='enrollments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name="كۇرس",
        related_name='enrollments'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="ھالەت")
    message = models.TextField(blank=True, verbose_name="ئوقۇغۇچى ئۇچۇرى")
    teacher_note = models.TextField(blank=True, verbose_name="ئۇستاز ئىزاھى")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "تىزىملىتىش"
        verbose_name_plural = "تىزىملىتىشلار"
        unique_together = ('user', 'course')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.full_name} - {self.course.title}"

    def get_status_color(self):
        colors = {
            'pending': '#eab308',
            'approved': '#22c55e',
            'rejected': '#ef4444',
        }
        return colors.get(self.status, '#64748b')

    def get_status_text(self):
        texts = {
            'pending': '⏳ كۈتۈلۈۋاتىدۇ',
            'approved': '✅ تەستىقلاندى',
            'rejected': '❌ رەت قىلىندى',
        }
        return texts.get(self.status, self.status)

    def get_teacher(self):
        """بۇ تىزىملىتىشنىڭ ئۇستازىنى قايتۇرىدۇ"""
        return self.course.instructor


# ====================
# قىلغان خىزمەتلىرىمىز Model
# ====================
class Work(models.Model):
    title = models.CharField(max_length=200, verbose_name="ماۋزۇ")
    description = models.TextField(verbose_name="چۈشەندۈرۈش")
    image = models.ImageField(upload_to='works/', blank=True, null=True, verbose_name="رەسىم")
    order = models.IntegerField(default=0, verbose_name="تەرتىپ نومۇرى")

    class Meta:
        verbose_name = "خىزمەت"
        verbose_name_plural = "قىلغان خىزمەتلەر"
        ordering = ['order']

    def __str__(self):
        return self.title


# ====================
# ئۇقتۇرۇش Model
# ====================
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('approved', 'تەستىقلاندى'),
        ('rejected', 'رەت قىلىندى'),
        ('message', 'ئۇچۇر'),
        ('system', 'سىستېما'),
    ]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="ئىشلەتكۈچى"
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        verbose_name="تىپى"
    )
    title = models.CharField(max_length=200, verbose_name="ماۋزۇ")
    message = models.TextField(verbose_name="ئۇچۇر")
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="كۇرس"
    )
    is_read = models.BooleanField(default=False, verbose_name="ئوقۇلدى")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "ئۇقتۇرۇش"
        verbose_name_plural = "ئۇقتۇرۇشلار"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.full_name} - {self.title}"

    def get_icon(self):
        icons = {
            'approved': 'fas fa-check-circle',
            'rejected': 'fas fa-times-circle',
            'message': 'fas fa-envelope',
            'system': 'fas fa-bell',
        }
        return icons.get(self.notification_type, 'fas fa-bell')

    def get_color(self):
        colors = {
            'approved': '#22c55e',
            'rejected': '#ef4444',
            'message': '#3b82f6',
            'system': '#eab308',
        }
        return colors.get(self.notification_type, '#64748b')


# ====================
# ئۇچۇر Model
# ====================
class Message(models.Model):
    sender = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name="يوللىغۇچى"
    )
    receiver = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name="قوبۇل قىلغۇچى"
    )
    subject = models.CharField(max_length=200, verbose_name="ماۋزۇ")
    message = models.TextField(verbose_name="ئۇچۇر")
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="مۇناسىۋەتلىك كۇرس"
    )
    is_read = models.BooleanField(default=False, verbose_name="ئوقۇلدى")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "ئۇچۇر"
        verbose_name_plural = "ئۇچۇرلار"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender.full_name} → {self.receiver.full_name}: {self.subject}"


# ====================
# توربەت تەڭشەكلىرى Model
# ====================
class SiteSettings(models.Model):
    site_name = models.CharField(max_length=200, default='Edraak Education', verbose_name="توربەت ئىسمى (ئېنگلىزچە)")
    site_name_ug = models.CharField(max_length=200, default='ئىدراك مائارىپى', verbose_name="توربەت ئىسمى (ئۇيغۇرچە)")
    tagline = models.CharField(max_length=300, blank=True, default='Guiding the Future | كەلگۈسىگە يېتەكلەش',
                               verbose_name="شۇئار")
    logo = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name="لوگو رەسىمى")

    # About Us
    about_title_ug = models.CharField(max_length=200, default='ئىدراك مائارىپى غايىسى',
                                      verbose_name="بىز ھەققىدە ماۋزۇسى (ئۇيغۇرچە)")
    about_text_ug = models.TextField(blank=True, verbose_name="بىز ھەققىدە مەزمۇنى (ئۇيغۇرچە)")
    about_title_en = models.CharField(max_length=200, default='Our Mission',
                                      verbose_name="بىز ھەققىدە ماۋزۇسى (ئېنگلىزچە)")
    about_text_en = models.TextField(blank=True, verbose_name="بىز ھەققىدە مەزمۇنى (ئېنگلىزچە)")

    # Contact
    whatsapp = models.CharField(max_length=50, blank=True, default='905444362947',
                                verbose_name="WhatsApp نومۇرى (پەقەت سان)")
    telegram = models.CharField(max_length=100, blank=True, default='salman_muallim', verbose_name="Telegram ئادرېسى")
    email = models.EmailField(blank=True, default='salmanuyghur3@gmail.com', verbose_name="Email")
    phone = models.CharField(max_length=50, blank=True, default='+90 544 436 29 47',
                             verbose_name="تېلېفون نومۇرى (كۆرۈنۈش)")
    address = models.CharField(max_length=300, blank=True, verbose_name="ئادرېس")

    # Footer
    footer_text = models.CharField(max_length=300, blank=True, default='© 2026 Edraak Education. All rights reserved.',
                                   verbose_name="Footer تېكىستى")

    class Meta:
        verbose_name = "توربەت تەڭشەكلىرى"
        verbose_name_plural = "توربەت تەڭشەكلىرى"

    def __str__(self):
        return self.site_name

    @classmethod
    def get_settings(cls):
        """تەڭشەكلەرنى قايتۇرىدۇ، يوق بولسا قۇرىدۇ"""
        settings, created = cls.objects.get_or_create(id=1)
        return settings


# ====================
# كۇرس ماتېرىياللىرى Model
# ====================
class CourseMaterial(models.Model):
    MATERIAL_TYPES = [
        ('pdf', '📄 PDF ھۆججەت'),
        ('video', '🎬 Video'),
        ('link', '🔗 ئۇلىنىش'),
        ('doc', '📝 ھۆججەت'),
        ('other', '📦 باشقا'),
    ]

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='materials',
        verbose_name="كۇرس"
    )
    title = models.CharField(max_length=200, verbose_name="ماۋزۇ")
    material_type = models.CharField(
        max_length=20,
        choices=MATERIAL_TYPES,
        default='pdf',
        verbose_name="تىپى"
    )
    file = models.FileField(
        upload_to='materials/',
        blank=True,
        null=True,
        verbose_name="ھۆججەت (PDF/Doc)"
    )
    url = models.URLField(
        blank=True,
        max_length=500,
        verbose_name="ئۇلىنىش (Video/Web)"
    )
    description = models.TextField(blank=True, verbose_name="چۈشەندۈرۈش")
    order = models.IntegerField(default=0, verbose_name="تەرتىپ نومۇرى")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "كۇرس ماتېرىيالى"
        verbose_name_plural = "كۇرس ماتېرىياللىرى"
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    def get_icon(self):
        icons = {
            'pdf': 'fas fa-file-pdf',
            'video': 'fas fa-video',
            'link': 'fas fa-link',
            'doc': 'fas fa-file-word',
            'other': 'fas fa-file',
        }
        return icons.get(self.material_type, 'fas fa-file')

    def get_color(self):
        colors = {
            'pdf': '#ef4444',
            'video': '#8b5cf6',
            'link': '#3b82f6',
            'doc': '#2563eb',
            'other': '#64748b',
        }
        return colors.get(self.material_type, '#64748b')

    def get_material_url(self):
        """ماتېرىيالنىڭ ئۇلىنىشىنى قايتۇرىدۇ"""
        if self.material_type in ['video', 'link'] and self.url:
            return self.url
        elif self.file:
            return self.file.url
        return '#'

    def is_external(self):
        """سىرتقى ئۇلىنىشمۇ ياكى يەرلىك ھۆججەتمۇ"""
        return self.material_type in ['video', 'link']


# ====================
# دەرس جەدۋىلى Model
# ====================
class Lesson(models.Model):
    DAY_CHOICES = [
        (0, 'يەكشەنبە'),
        (1, 'دۈشەنبە'),
        (2, 'سەيشەنبە'),
        (3, 'چارشەنبە'),
        (4, 'پەيشەنبە'),
        (5, 'جۈمە'),
        (6, 'شەنبە'),
    ]

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name="كۇرس"
    )
    title = models.CharField(max_length=200, verbose_name="دەرس ماۋزۇسى")
    day_of_week = models.IntegerField(
        choices=DAY_CHOICES,
        verbose_name="ھەپتە كۈنى"
    )
    start_time = models.TimeField(verbose_name="باشلىنىش ۋاقتى")
    end_time = models.TimeField(verbose_name="ئاخىرلىشىش ۋاقتى")
    description = models.TextField(blank=True, verbose_name="چۈشەندۈرۈش")
    online_link = models.URLField(blank=True, verbose_name="تور دەرس ئۇلىنىشى (Zoom/Meet)")
    location = models.CharField(max_length=200, blank=True, verbose_name="سىنىپ ئورنى")
    is_active = models.BooleanField(default=True, verbose_name="ئاكتىپمۇ؟")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "دەرس جەدۋىلى"
        verbose_name_plural = "دەرس جەدۋىللىرى"
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.course.title} - {self.get_day_of_week_display()} {self.start_time.strftime('%H:%M')}"

    def get_day_name(self):
        days = {
            0: 'يەكشەنبە',
            1: 'دۈشەنبە',
            2: 'سەيشەنبە',
            3: 'چارشەنبە',
            4: 'پەيشەنبە',
            5: 'جۈمە',
            6: 'شەنبە',
        }
        return days.get(self.day_of_week, '')

    def get_time_range(self):
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"


# ====================
# FAQ Model (كۆپ سورىلىدىغان سوئاللار)
# ====================
class FAQ(models.Model):
    CATEGORY_CHOICES = [
        ('registration', 'تىزىملىتىش'),
        ('courses', 'كۇرسىلار'),
        ('payment', 'تۆلەم'),
        ('schedule', 'دەرس جەدۋىلى'),
        ('other', 'باشقا'),
    ]

    question = models.CharField(max_length=500, verbose_name="سوئال")
    answer = models.TextField(verbose_name="جاۋاب")
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name="تۈر"
    )
    order = models.IntegerField(default=0, verbose_name="تەرتىپ نومۇرى")
    is_active = models.BooleanField(default=True, verbose_name="ئاكتىپمۇ؟")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ سوئال-جاۋابلار"
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.question

    def get_category_name(self):
        categories = {
            'registration': 'تىزىملىتىش',
            'courses': 'كۇرسىلار',
            'payment': 'تۆلەم',
            'schedule': 'دەرس جەدۋىلى',
            'other': 'باشقا',
        }
        return categories.get(self.category, 'باشقا')


# ====================
# ئېلانلار Model
# ====================
class Announcement(models.Model):
    TYPE_CHOICES = [
        ('info', '📢 ئادەتتىكى ئېلان'),
        ('success', '🎉 مۇۋەپپەقىيەت'),
        ('warning', '⚠️ ئاگاھلاندۇرۇش'),
        ('important', '🔴 مۇھىم ئېلان'),
    ]

    TARGET_CHOICES = [
        ('all', 'ھەممىسى'),
        ('students', 'پەقەت ئوقۇغۇچىلار'),
        ('teachers', 'پەقەت ئوقۇتقۇچىلار'),
    ]

    title = models.CharField(max_length=300, verbose_name="ئېلان ماۋزۇسى")
    content = models.TextField(verbose_name="ئېلان مەزمۇنى")
    announcement_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='info',
        verbose_name="ئېلان تىپى"
    )
    target_audience = models.CharField(
        max_length=20,
        choices=TARGET_CHOICES,
        default='all',
        verbose_name="نىشان ئوقۇرمەن"
    )
    is_active = models.BooleanField(default=True, verbose_name="ئاكتىپمۇ؟")
    start_date = models.DateTimeField(auto_now_add=True, verbose_name="باشلىنىش ۋاقتى")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="ئاخىرلىشىش ۋاقتى (ئىختىيارى)")
    link_url = models.URLField(blank=True, verbose_name="ئۇلىنىش (ئىختىيارى)")
    link_text = models.CharField(max_length=100, blank=True, verbose_name="ئۇلىنىش تېكىستى")
    order = models.IntegerField(default=0, verbose_name="تەرتىپ نومۇرى")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "ئېلان"
        verbose_name_plural = "ئېلانلار"
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

    def get_type_color(self):
        colors = {
            'info': '#3b82f6',
            'success': '#22c55e',
            'warning': '#eab308',
            'important': '#ef4444',
        }
        return colors.get(self.announcement_type, '#3b82f6')

    def get_type_bg(self):
        bgs = {
            'info': '#eff6ff',
            'success': '#f0fdf4',
            'warning': '#fefce8',
            'important': '#fef2f2',
        }
        return bgs.get(self.announcement_type, '#eff6ff')

    def get_type_icon(self):
        icons = {
            'info': 'fas fa-bullhorn',
            'success': 'fas fa-check-circle',
            'warning': 'fas fa-exclamation-triangle',
            'important': 'fas fa-exclamation-circle',
        }
        return icons.get(self.announcement_type, 'fas fa-bullhorn')

    def is_expired(self):
        """ئېلان ۋاقتى ئۆتكەنمۇ"""
        from django.utils import timezone
        if self.end_date:
            return timezone.now() > self.end_date
        return False

    def is_visible(self):
        """ئېلان كۆرۈنەمدۇ"""
        return self.is_active and not self.is_expired()


# ====================
# ھازىرلىق Model
# ====================
class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'ھازىر'),
        ('absent', 'يوق'),
        ('late', 'كېچىكىپ كەلدى'),
        ('excused', 'سەۋەبلىك يوق'),
    ]

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name="دەرس"
    )
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name="ئوقۇغۇچى"
    )
    attendance_date = models.DateField(verbose_name="ھازىرلىق ۋاقتى")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='present',
        verbose_name="ھالەت"
    )
    note = models.TextField(blank=True, verbose_name="ئىزاھات")
    marked_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='marked_attendances',
        verbose_name="بەلگىلىگۈچى"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "ھازىرلىق"
        verbose_name_plural = "ھازىرلىق خاتىرىسى"
        unique_together = ('lesson', 'student', 'attendance_date')
        ordering = ['-attendance_date']

    def __str__(self):
        return f"{self.student.full_name} - {self.attendance_date} - {self.get_status_display()}"

    def get_status_color(self):
        colors = {
            'present': '#22c55e',
            'absent': '#ef4444',
            'late': '#eab308',
            'excused': '#3b82f6',
        }
        return colors.get(self.status, '#64748b')

    def get_status_icon(self):
        icons = {
            'present': 'fas fa-check-circle',
            'absent': 'fas fa-times-circle',
            'late': 'fas fa-clock',
            'excused': 'fas fa-info-circle',
        }
        return icons.get(self.status, 'fas fa-question-circle')


# ====================
# ھازىرلىق Session Model
# ====================
class AttendanceSession(models.Model):
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name="دەرس"
    )
    session_date = models.DateField(verbose_name="دەرس ۋاقتى")
    topic = models.CharField(max_length=300, blank=True, verbose_name="دەرس تېمىسى")
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_sessions',
        verbose_name="قۇرغۇچى"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "ھازىرلىق Session"
        verbose_name_plural = "ھازىرلىق Session لار"
        ordering = ['-session_date']

    def __str__(self):
        return f"{self.lesson.title} - {self.session_date}"

    def get_attendance_count(self):
        return Attendance.objects.filter(lesson=self.lesson, attendance_date=self.session_date).count()

    def get_present_count(self):
        return Attendance.objects.filter(
            lesson=self.lesson,
            attendance_date=self.session_date,
            status='present'
        ).count()


# ====================
# ئىمتىھان Model
# ====================
class Exam(models.Model):
    EXAM_TYPES = [
        ('written', '📝 يېزىقچە'),
        ('oral', '🗣️ ئاغزاكى'),
        ('practical', '🛠️ ئەمەلىي'),
        ('quiz', '❓ تېز سوئال'),
        ('midterm', '📘 ئارىلىق ئىمتىھان'),
        ('final', '📕 ئاخىرقى ئىمتىھان'),
    ]

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='exams',
        verbose_name="كۇرس"
    )
    title = models.CharField(max_length=200, verbose_name="ئىمتىھان ماۋزۇسى")
    exam_type = models.CharField(
        max_length=20,
        choices=EXAM_TYPES,
        default='written',
        verbose_name="ئىمتىھان تىپى"
    )
    total_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100.00,
        verbose_name="ئومۇمىي نومۇر"
    )
    exam_date = models.DateField(verbose_name="ئىمتىھان ۋاقتى")
    description = models.TextField(blank=True, verbose_name="چۈشەندۈرۈش")
    is_published = models.BooleanField(default=False, verbose_name="ئېلان قىلىندىمۇ؟")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "ئىمتىھان"
        verbose_name_plural = "ئىمتىھانلار"
        ordering = ['-exam_date']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    def get_average_score(self):
        """ئوتتۇرىچە نومۇر"""
        results = self.results.all()
        if results.count() == 0:
            return 0
        total = sum(r.score for r in results)
        return round(total / results.count(), 2)

    def get_pass_rate(self):
        """ئۆتكۈزۈش نىسبىتى (60% دىن يۇقىرى)"""
        results = self.results.all()
        if results.count() == 0:
            return 0
        passed = sum(1 for r in results if (r.score / float(self.total_score)) >= 0.6)
        return round((passed / results.count()) * 100, 1)

    def get_results_count(self):
        return self.results.count()


# ====================
# ئىمتىھان نەتىجىسى Model
# ====================
class ExamResult(models.Model):
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='results',
        verbose_name="ئىمتىھان"
    )
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='exam_results',
        verbose_name="ئوقۇغۇچى"
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="نومۇر"
    )
    note = models.TextField(blank=True, verbose_name="ئوقۇتقۇچى ئىزاھى")
    graded_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_exams',
        verbose_name="باھالىغۇچى"
    )
    graded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "ئىمتىھان نەتىجىسى"
        verbose_name_plural = "ئىمتىھان نەتىجىلىرى"
        unique_together = ('exam', 'student')
        ordering = ['-score']

    def __str__(self):
        return f"{self.student.full_name} - {self.exam.title}: {self.score}"

    def get_percentage(self):
        """پىرسەنت"""
        return round((float(self.score) / float(self.exam.total_score)) * 100, 1)

    def get_grade(self):
        """باھا ھەرىپى"""
        percentage = self.get_percentage()
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'

    def get_grade_color(self):
        """باھا رەڭگى"""
        grade = self.get_grade()
        colors = {
            'A': '#22c55e',  # يېشىل
            'B': '#3b82f6',  # كۆك
            'C': '#eab308',  # سېرىق
            'D': '#f97316',  # قىزغۇچ
            'F': '#ef4444',  # قىزىل
        }
        return colors.get(grade, '#64748b')

    def is_passed(self):
        """ئۆتكەنمۇ؟"""
        return self.get_percentage() >= 60

    def get_status_text(self):
        if self.is_passed():
            return '✅ ئۆتتى'
        return '❌ قالدى'


# ====================
# گۇۋاھنامە Model
# ====================
class Certificate(models.Model):
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='certificates',
        verbose_name="ئوقۇغۇچى"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='certificates',
        verbose_name="كۇرس"
    )
    certificate_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="گۇۋاھنامە نومۇرى"
    )
    issue_date = models.DateField(auto_now_add=True, verbose_name="بېرىلغان ۋاقتى")
    issued_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='issued_certificates',
        verbose_name="بەرگۈچى"
    )

    class Meta:
        verbose_name = "گۇۋاھنامە"
        verbose_name_plural = "گۇۋاھنامىلەر"
        ordering = ['-issue_date']

    def __str__(self):
        return f"{self.student.full_name} - {self.course.title}"

    def save(self, *args, **kwargs):
        if not self.certificate_number:
            import uuid
            self.certificate_number = f"EDR-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


# ====================
# كۇرس باھالاش سىستېمىسى
# ====================
class CourseRating(models.Model):
    RATING_CHOICES = [
        (1, '⭐'),
        (2, '⭐⭐'),
        (3, '⭐⭐⭐'),
        (4, '⭐⭐⭐⭐'),
        (5, '⭐⭐⭐⭐⭐'),
    ]

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name="كۇرس"
    )
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='course_ratings',
        verbose_name="ئوقۇغۇچى"
    )
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        default=5,
        verbose_name="باھا (1-5)"
    )
    comment = models.TextField(
        blank=True,
        verbose_name="ئىنكاس"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="يېزىلغان ۋاقتى")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="يېڭىلانغان ۋاقتى")

    class Meta:
        verbose_name = "كۇرس باھاسى"
        verbose_name_plural = "كۇرس باھالىرى"
        unique_together = ('course', 'student')  # ھەر ئوقۇغۇچى بىر قېتىم باھا بېرىدۇ
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.full_name} - {self.course.title}: {self.rating}/5"

    def get_rating_stars(self):
        """يۇلتۇز سانى"""
        return '⭐' * self.rating

    def get_empty_stars(self):
        """بوش يۇلتۇز سانى"""
        return '☆' * (5 - self.rating)

    def get_rating_text(self):
        """باھا تېكىستى"""
        texts = {
            1: 'ناچار',
            2: 'ئوتتۇرا',
            3: 'ياخشى',
            4: 'ناھايىتى ياخشى',
            5: 'مۇنەۋۋەر',
        }
        return texts.get(self.rating, '')