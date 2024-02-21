from typing import Any
from django.db import models
from tinymce.models import HTMLField
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
import threading
from unidecode import unidecode
from django.utils.text import slugify
from datetime import timedelta
from django.db.models.signals import post_save
from django.urls import reverse




#================================== Phòng ban ==================================
class Department(models.Model):
    head_of_department = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    department_name = models.CharField(max_length=255)
    description = HTMLField()
    status = models.BooleanField(default=True)
    address = models.CharField(max_length=255)
    def __str__(self):
        return self.department_name
   
#================================== Vị trí công việc ==================================
class Position(models.Model):
    position_name = models.CharField(max_length=255)
    description = models.TextField()
    status = models.BooleanField(default=True)
    def __str__(self):
        return self.position_name
    
#================================== Loại người dùng ==================================
class UserCategory(models.Model):
    user_category_name = models.CharField(max_length=255)
    description = models.TextField()
    status = models.BooleanField(default=True)
    
    
class Nationality(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = 'Quốc gia'
        verbose_name_plural = 'Quốc gia'
    def __str__(self):
        return self.name

class Ethnicity(models.Model):
    name = models.CharField(max_length=50, verbose_name='Dân tộc', unique=True)

    class Meta:
        verbose_name = 'Dân tộc'
        verbose_name_plural = 'Dân tộc'

    def __str__(self):
        return self.name

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Người dùng')
    date_of_birth = models.DateField(verbose_name='Ngày sinh', null=True, blank=True)
    GENDER_CHOICES = [ (True, 'Nam'),(False, 'Nữ'),]
    gender = models.BooleanField(default=True,choices=GENDER_CHOICES, verbose_name='Giới tính')
    phone_number = models.CharField(max_length=50, verbose_name='Số điện thoại',null=True, blank=True,unique=True)
    image = models.ImageField(upload_to='img/', null=True, blank=True, verbose_name='Hình ảnh')
    address = models.TextField(verbose_name='Địa chỉ',null=True, blank=True, )
    department_works_at = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Bộ phận làm việc')
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Chức vụ')

    ethnicity = models.ForeignKey(Ethnicity, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Dân tộc')
    nationality = models.ForeignKey(Nationality, on_delete=models.CASCADE,verbose_name='Quốc tịch', null=True, blank=True)
    educational_background = models.CharField(max_length=100, verbose_name='Trình độ văn hóa', null=True, blank=True)
    professional_degree = models.CharField(max_length=100, verbose_name='Trình độ chuyên môn', null=True, blank=True)
    current_company = models.CharField(max_length=100, verbose_name='Công ty hiện đang làm việc', null=True, blank=True)
    office_phone_number = models.CharField(max_length=15, verbose_name='Số điện thoại cơ quan', null=True, blank=True)
    office_address = models.TextField(verbose_name='Địa chỉ cơ quan', null=True, blank=True)
    citizen_id = models.CharField(max_length=20, verbose_name='Căn cước công dân', null=True, blank=True)
    citizen_id_issue_date = models.DateField(verbose_name='Ngày cấp căn cước công dân', null=True, blank=True)
    citizen_id_issuing_place = models.CharField(max_length=100, verbose_name='Nơi cấp căn cước công dân', null=True, blank=True)
    citizen_id_images = models.ManyToManyField('CitizenIDImage', related_name='citizen_id_images', blank=True, verbose_name='Hình ảnh căn cước công dân')

    # # Social Media Links
    link_facebook = models.URLField(verbose_name='Link Facebook', null=True, blank=True)
    link_zalo = models.URLField(verbose_name='Link Zalo', null=True, blank=True)
    link_instagram = models.URLField(verbose_name='Link Instagram', null=True, blank=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Tài khoản'
        verbose_name_plural = 'Tài khoản'
    
from django.utils.html import format_html
class CitizenIDImage(models.Model):
    image = models.FileField(upload_to='citizen_id_images/', null=True, verbose_name='Hình ảnh căn cước công dân')
    class Meta:
        verbose_name = 'Hình ảnh căn cước công dân'
        verbose_name_plural = 'Hình ảnh căn cước công dân'
        
    def display_image(self):
        return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', self.image.url)
    display_image.short_description = 'Hình ảnh'

    def __str__(self):
        return str(self.image.name)

#================================== Lấy user tự động ==================================
thread_locals = threading.local()
def get_current_user():
    return getattr(thread_locals, 'user', None)


#================================== Bình luận ==================================
class Comment(models.Model):
    content = models.TextField(verbose_name='Nội dung comment')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_date = models.DateTimeField(auto_now=True, verbose_name='Ngày chỉnh sửa')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='Người bình luận', related_name='create_comments',null=True, blank=True,)
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='edited_comments', verbose_name='Người chỉnh sửa')
    likes = models.ManyToManyField(User, related_name='comment_likes', blank=True, verbose_name='Người thích')
    parent_comment = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies', verbose_name='Bình luận cha')
    STATUS_CHOICES = [
        (True, 'Active'),
        (False, 'UnActive'),
    ]
    status = models.BooleanField(default=True, choices=STATUS_CHOICES, verbose_name='Trạng thái')
    is_edited = models.BooleanField(default=False, verbose_name='Đã chỉnh sửa')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='Địa chỉ IP')
    mentions = models.ManyToManyField(User, blank=True, related_name='mentioned_in_comments', verbose_name='Người được đề cập')
    original_content = models.TextField(blank=True)
    
    
    def save(self, *args, **kwargs):
        if not self.user:
            self.user = get_current_user()   
         # Chỉ lưu original_content nếu là lần tạo mới, không phải khi chỉnh sửa
        if not self.id:
            self.original_content = self.content     
        super(Comment, self).save(*args, **kwargs)
        
    def user_has_liked(self, user):
        return self.likes.filter(pk=user.pk).exists()

    def toggle_like(self, user):
        if self.user_has_liked(user):
            self.likes.remove(user)
        else:
            self.likes.add(user)
            
    def get_mentions(self):
        return self.mentions.all()

    def get_like_count(self):
        return self.likes.count()

    def get_reply_count(self):
        return self.replies.count()

    def get_reply_preview(self, count=3):
        return self.replies.all()[:count]

    def can_edit(self, user):
        return user == self.user

    def can_delete(self, user):
        return user == self.user
    
    def add_reply(self, user, content,ip_address ):
        """
        Tạo một reply mới cho comment.
        """
        reply = Comment.objects.create(
            content=content,
            user=user,
            ip_address = ip_address,
            parent_comment=self,
        )
        return reply

    def get_all_replies(self):
        replies = self.replies.all()
        for reply in replies:
            replies = replies | reply.get_all_replies()
        return replies
    
    def delete(self, *args, **kwargs):
        # Xóa tất cả các bình luận con trước
        for reply in self.replies.all():
            reply.delete()

        super().delete(*args, **kwargs)
    
    def edit_comment(self, user, new_content):
        self.content = new_content
        self.edited_by = user
        self.is_edited = True
        self.updated_date = timezone.now()
        self.save()
        
    def update_status_recursive(self, new_status):
        # Cập nhật trạng thái của bình luận hiện tại
        self.status = new_status
        self.save()

        # Lặp qua tất cả các bình luận con và cập nhật trạng thái của chúng
        for reply in self.replies.all():
            reply.update_status_recursive(new_status)

    def __str__(self):
        return f'{self.content} - {self.created_date}'
    
@receiver(pre_save, sender=Comment)
def set_edited_by(sender, instance, **kwargs):
    if instance.content != instance.original_content:
        # Bình luận đã được chỉnh sửa, gán người chỉnh sửa là người thực hiện request
        instance.edited_by = instance.user
        instance.edited_date = timezone.now()

#================================== Thông báo ==================================
#============ Loại thông báo
class CatagoryNotification(models.Model):
    name = models.CharField(max_length=255,blank=True, null = True)
    tag = models.CharField(max_length=255,blank=True, null = True)
    description = models.TextField(blank=True, null = True)
    url = models.CharField(max_length=255, blank=True, null = True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL,blank=True, null=True, related_name='created_cata_nofi', verbose_name='Người tạo')
    created_date = models.DateTimeField(auto_now_add=True,verbose_name='Ngày tạo')
    updated_date = models.DateTimeField(auto_now=True,verbose_name='Cập nhật gần nhất')
    class Meta:
        verbose_name_plural ='Loại thông báo'
    def save(self, *args, **kwargs):
        if not self.creator:
            self.creator = get_current_user()
        # Tạo URL từ trường 'title' và kiểm tra tính duy nhất
        base_url = slugify(self.name)
        self.url = base_url
        counter = 1
        while CatagoryNotification.objects.filter(url=self.url).exclude(id=self.id).exists():
            self.url = f"{base_url}-{counter}"
            counter += 1
        super(CatagoryNotification, self).save(*args, **kwargs)
    def __str__(self):
        return f"Thể loại {self.name} - tag {self.tag}"
    
# ======Thông báo
class Notification(models.Model):
    title = models.CharField(max_length=255)
    content = RichTextUploadingField(null = True)
    url = models.CharField(max_length=255, blank=True, null = True)
    start_date = models.DateField(null=True)  
    end_date = models.DateField(null=True)  
    sender = models.ForeignKey(User, on_delete=models.SET_NULL,blank=True, null=True)
    recipients = models.ManyToManyField(User, related_name='received_notifications')
    read_by_users = models.ManyToManyField(User, through='ReadRecord', related_name='read_notifications', blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    category = models.ManyToManyField(CatagoryNotification, related_name='notification_categories', blank=True)
    STATUS_CHOICES = [
        (True, 'Xuất bản'),
        (False, 'Ngưng xuất bản'),
    ]
    status = models.BooleanField(default=True, choices=STATUS_CHOICES)
    uploadfile = models.ManyToManyField('uploadFile',blank=True)  
    comments = models.ManyToManyField(
        Comment, 
        related_name='comments_notification',
        verbose_name='bình luận',
        blank=True
    )
    class Meta:
        verbose_name_plural ='Thông báo'
    
    def save(self, *args, **kwargs):
        if not self.sender:
            self.sender = get_current_user()

        # Tạo URL từ trường 'title' và kiểm tra tính duy nhất
        base_url = slugify(self.title)
        self.url = base_url

        counter = 1
        while Notification.objects.filter(url=self.url).exclude(id=self.id).exists():
            self.url = f"{base_url}-{counter}"
            counter += 1

        super(Notification, self).save(*args, **kwargs)
        
    def get_files(self):
        return self.uploadfile.all()
    
    def get_commnet(self):
        return self.comments.all()
    
    def __str__(self):
        return self.title
    
def set_current_user(user):
    thread_locals.user = user
    
@receiver(pre_save, sender=Notification)
def set_sender_on_notification(sender, instance, **kwargs):
    # Nếu sender chưa được thiết lập, và có một người dùng đăng nhập, hãy thiết lập sender là người dùng đó.
    if not instance.sender and hasattr(instance, 'request') and instance.request.user.is_authenticated:
        instance.sender = instance.request.user
#============== quản lý người độc thông báo
class ReadRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    read_count = models.PositiveIntegerField(default=1)
    first_read_time = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name_plural ='Lượt đọc'


#================================== Công việc ==================================                
class Task(models.Model):
    CHUA_HOAT_DONG = 1
    DANG_HOAT_DONG = 2
    HOAN_THANH = 3
    QUA_HAN = 4

    STSTUS_CHOICES = [
        (CHUA_HOAT_DONG, 'Chưa hoạt động'),
        (DANG_HOAT_DONG, 'Đang hoạt động'),
        (HOAN_THANH, 'Hoàn thành'),
        (QUA_HAN, 'Quá hạn'),
    ]
    
    BINH_THUONG = 1
    THAP = 2
    CAO = 3
    KHAN_CAP = 4
    QUAN_TRONG = 5
    XEM_XET = 6
    TU_DO = 7
    
    PRIORITY_CHOICES = [
        (BINH_THUONG, 'Bình thường'),
        (THAP, 'Thấp'),
        (CAO, 'Cao'),
        (KHAN_CAP, 'Khẩn cấp'),
        (QUAN_TRONG, 'Quan trọng'),
        (XEM_XET, 'Xem xét'),
        (TU_DO, 'Tự do'),
    ]
    
    title = models.CharField(max_length=500, verbose_name='Tiêu đề công việc', null = True, blank = True)
    description = models.TextField(verbose_name='Mô tả công việc', null = True, blank = True)
    image = models.ImageField(upload_to='task/', null=True, blank=True)
    start_date = models.DateField(verbose_name='Ngày bắt đầu', null = True, blank = True)
    end_date = models.DateField(verbose_name='Ngày kết thúc', null = True, blank = True)
    url = models.CharField(max_length=500, blank=True, null = True)
    taskfiles = models.ManyToManyField('uploadFileTask', blank=True, verbose_name='file tiến độ', related_name='task_uploadfiles')
    uploadfile = models.ManyToManyField('uploadFile', blank=True, verbose_name='file đính kèm', related_name='admin_uploadfiles')
    assigned_users = models.ManyToManyField(User, blank=True, verbose_name='Người được giao', related_name='assigned_tasks')
    confirmed_users = models.ManyToManyField(User, related_name='confirmed_tasks', blank=True,
                                              verbose_name='Người đã xác nhận tham gia công việc')
    status = models.IntegerField(choices=STSTUS_CHOICES,default=CHUA_HOAT_DONG,verbose_name='Trạng thái công việc')
    sum_progress = models.PositiveIntegerField(default=0, verbose_name='Tổng tiến độ')
    creator = models.ForeignKey(User, on_delete=models.SET_NULL,blank=True, null=True, related_name='created_tasks', verbose_name='Người tạo')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    priority = models.IntegerField(choices=PRIORITY_CHOICES,default=BINH_THUONG,verbose_name='Độ ưu tiên')
    comments = models.ManyToManyField(
        Comment, 
        related_name='comments_task',  # Thêm related_name ở đây
        verbose_name='bình luận',
        blank=True
    )
    class Meta:
        verbose_name_plural ='Công việc'
        
    def clean(self):
        # Kiểm tra nếu thời gian bắt đầu lớn hơn thời gian kết thúc
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError("Thời gian bắt đầu phải nhỏ hơn thời gian kết thúc.")
        
    def update_sum_progress(self):
            """
            Cập nhật tổng tiến độ của công việc dựa trên số lượng người được giao và số lượng người đã cập nhật taskfiles.
            """
            assigned_users_count = self.assigned_users.count()

            if assigned_users_count > 0:
                # Tính số lượng người đã cập nhật taskfiles
                users_with_taskfiles_count = self.taskfiles.values('upload_by').distinct().count()

                # Tính toán tiến độ dựa trên số lượng người đã cập nhật taskfiles
                progress_percentage = (users_with_taskfiles_count / assigned_users_count) * 100

                # Giới hạn giá trị của tiến độ trong khoảng [0, 100]
                progress_percentage = min(100, max(0, progress_percentage))

                # Cập nhật giá trị tiến độ
                self.sum_progress = int(progress_percentage)
                
                # Kiểm tra nếu tiến độ đạt 100% thì cập nhật trạng thái thành "Hoàn thành"
                if self.sum_progress == 100 and self.status == Task.DANG_HOAT_DONG:
                    self.status = Task.HOAN_THANH
                    
                self.save()
        
    def update_status_if_needed(self):
        if self.assigned_users.exists() and self.assigned_users.count() == self.confirmed_users.count():
            # Kiểm tra nếu số lượng người được giao và người đã xác nhận giống nhau
            if self.status != Task.DANG_HOAT_DONG:
                # Nếu trạng thái không phải là Đang hoạt động, cập nhật thành Đang hoạt động
                self.status = Task.DANG_HOAT_DONG
                self.save()
                
    def save(self, *args, **kwargs):
        if not self.creator:
            self.creator = get_current_user()
        
        # Tạo URL từ trường 'title' và kiểm tra tính duy nhất
        base_url = slugify(self.title)
        self.url = base_url

        counter = 1
        while Task.objects.filter(url=self.url).exclude(id=self.id).exists():
            self.url = f"{base_url}-{counter}"
            counter += 1
        
        # Kiểm tra trạng thái và ngày kết thúc để cập nhật trạng thái
        if self.status != Task.HOAN_THANH and self.end_date < timezone.now().date():
            self.status = Task.QUA_HAN
            
        super(Task, self).save(*args, **kwargs)
        
    def get_files(self):
        return self.uploadfile.all()

    def get_task_files(self):
        return self.taskfiles.all()
    
        
    def get_account_images(self):
        account_images = []
        try:
            # Loop through each user associated with the task
            for user in self.assigned_users.all():
                # Get the account associated with the user
                account = user.account
                # Append the image URL to the list if available
                if account and account.image:
                    account_images.append(account.image.url)
        except Account.DoesNotExist:
            pass

        return account_images
        
    class Meta:
        verbose_name_plural ='Công việc'
        
    def __str__(self):
        return self.title
    
    
from django.db import transaction

class uploadFileTask(models.Model):
    file = models.FileField(upload_to='task_files/', null=True)
    task = models.ForeignKey('Task', on_delete=models.CASCADE, null=True, related_name='upload_files')
    time = models.DateTimeField(default=timezone.now)
    upload_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Người cập đăng tải tập tin')
    def __str__(self):
        return f"{self.file.name} - Task: {self.task.title if self.task else 'N/A'} - Time: {self.time} - Uploaded by: {self.upload_by.username if self.upload_by else 'N/A'}"
    class Meta:
          verbose_name_plural ='Tệp tin công việc'
    def save(self, *args, **kwargs):
        # ... (code hiện tại của uploadFileTask)

        # Gọi phương thức cập nhật tiến độ của công việc
        self.task.update_sum_progress()

        super(uploadFileTask, self).save(*args, **kwargs)
    
@receiver(pre_save, sender=Task)
def check_sum_progress(sender, instance, **kwargs):
    # Kiểm tra xem sum_progress có vượt quá 100% không
    if instance.sum_progress > 100:
        # Nếu vượt quá, đặt giá trị về 100
        instance.sum_progress = 100
       
class TaskProgress(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='progress_updates', verbose_name='Công việc')
    update_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Người cập nhật tiến độ')
    progress_percentage = models.PositiveIntegerField(default=0, verbose_name='Phần trăm tiến độ')
    update_date = models.DateField(auto_now_add=True, verbose_name='Ngày cập nhật')
    fileupdate = models.ManyToManyField('uploadFile', blank=True, verbose_name='Files đính kèm')
    class Meta:
          verbose_name_plural ='Tiền độ công việc'
          
class UserConfirmationTime(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, default=None)
    confirmation_time = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=255, verbose_name='Tên hoạt động', null = True, blank = True)
     
#================================== Tuần làm việc ==================================
class Week(models.Model):
    week_number = models.PositiveIntegerField(verbose_name='Tuần', null = True)
    year = models.PositiveIntegerField(verbose_name='Năm',null = True,default=timezone.now().year)
    start_date = models.DateField(verbose_name='Ngày bắt đầu',null = True)
    end_date = models.DateField(verbose_name='Ngày kết thúc', null = True)
    description = models.TextField(verbose_name='Ghi chú', null=True, blank=True)
    def __str__(self):
        return f"Tuần {self.week_number} - từ ngày {self.start_date} - đến ngày {self.end_date}"

    class Meta:
        verbose_name_plural = 'Tuần'
    def clean(self):
        one_week = timedelta(days=6)
        if (self.end_date - self.start_date) != one_week:
            raise ValidationError("Từ ngày và Đến ngày phải cách nhau đúng một tuần.")
        
    def get_schedule_count(self):
        # Sử dụng reverse relationship để đếm số lịch công tác
        return self.schedule_set.count()
    @classmethod
    def create_week(cls):
        # Lấy tuần có ngày kết thúc gần nhất
        latest_week = cls.objects.order_by('-end_date').first()

        # Tính toán các giá trị cho tuần mới
        week_number = latest_week.week_number + 1 if latest_week else 1
        year = timezone.now().year
        start_date = latest_week.end_date + timedelta(days=1) if latest_week else timezone.now().date()
        end_date = start_date + timedelta(days=6)
        description = "Chưa có"

        # Tạo đối tượng tuần mới
        new_week = cls.objects.create(
            week_number=week_number,
            year=year,
            start_date=start_date,
            end_date=end_date,
            description=description
        )

        return new_week
    
    
#================================== Lịch công tác ==================================
class Schedule(models.Model):
    TRUONG = 1
    PHONG_BAN = 2
    LANH_DAO = 3
    CA_NHAN = 4

    SCHEDULE_CATEGORY_CHOICES = [
        (TRUONG, 'Lịch trường'),
        (PHONG_BAN, 'Lịch phòng ban'),
        (LANH_DAO, 'Lịch lãnh đạo'),
        (CA_NHAN, 'Lịch cá nhân'),
    ]
    schedule_category = models.IntegerField(
        choices=SCHEDULE_CATEGORY_CHOICES,
        default=TRUONG,
        verbose_name='Loại lịch công tác'
    )
    BUOI_SANG = True
    BUOI_CHIEU = False

    MORNING_OR_AFTERNOON_CHOICES = [
        (BUOI_SANG, 'Buổi sáng'),
        (BUOI_CHIEU, 'Buổi chiều'),
    ]
    HOAN_THANH = True
    CHUA_HOAN_THANH = False

    STATUS = [
        (HOAN_THANH, 'Hoàn thành'),
        (CHUA_HOAN_THANH, 'Chưa hoàn thành'),
    ]
    week = models.ForeignKey(Week, on_delete=models.SET_NULL, null=True, verbose_name='Tuần thứ')
    work_date = models.DateField(verbose_name='Ngày làm việc')
    morning_or_afternoon = models.BooleanField(choices=MORNING_OR_AFTERNOON_CHOICES,default=BUOI_SANG,verbose_name='Buổi sáng hoặc buổi chiều')
    start_time = models.TimeField(verbose_name='Thời gian bắt đầu', null = True)
    end_time = models.TimeField(verbose_name='Thời gian kết thúc', null=True)
    location = models.CharField(max_length=255, verbose_name='Địa điểm', null=True)
    leading_official = models.CharField(max_length=255, verbose_name='Người lãnh đạo', null=True)
    participants = models.TextField(verbose_name='Thành phần tham gia', null=True)
    preparation = models.TextField(verbose_name='Chuẩn bị', null=True)
    content = models.TextField(verbose_name='Nội dung', null=True)
    description = models.TextField(verbose_name='Ghi chú', null=True)
    status = models.BooleanField(choices=STATUS,default=CHUA_HOAN_THANH,verbose_name='Trạng thái')
    created_at = models.DateField(auto_now_add=True, verbose_name='Tạo ngày')
    updated_at = models.DateField(auto_now=True, verbose_name='Cập nhật ngày')
    department = models.ManyToManyField(Department,  blank=True, verbose_name='Phòng ban')
    user = models.ManyToManyField(User,  blank=True, verbose_name='Người dùng')
    creator = models.ForeignKey(User, on_delete=models.SET_NULL,blank=True,  null=True, related_name='created_schedule_documents', verbose_name='Người tạo')
    
    class Meta:
        verbose_name_plural ='Lịch công tác'
    
    def clean(self):
        if self.week and self.work_date:
            if self.work_date < self.week.start_date or self.work_date > self.week.end_date:
                raise ValidationError("Ngày làm việc không nằm trong khoảng ngày bắt đầu và kết thúc của tuần.")
        # Kiểm tra nếu thời gian bắt đầu lớn hơn thời gian kết thúc
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("Thời gian bắt đầu phải nhỏ hơn thời gian kết thúc.")
    
    def save(self, *args, **kwargs):
        self.clean()
        if not self.creator:
            self.creator = get_current_user()

        super(Schedule, self).save(*args, **kwargs)
        
    @classmethod
    def current_week(cls):
        current_date = timezone.now()
        week_number = current_date.isocalendar()[1]  # Lấy số tuần hiện tại
        year = current_date.year
        return cls.objects.get(week_number=week_number, year=year)
        
    def __str__(self):
        return self.content
    
 #================================== Loại văn bản ==================================

class DocumentType(models.Model):
    document_name = models.CharField(max_length=255)
    description = models.TextField()
    status = models.BooleanField(default=True)
    class Meta:
        verbose_name_plural ='Loại văn bản'
    def __str__(self):
        return self.document_name
    
    
#================================== Cấp độ văn bản==================================
class DocumentLevel(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    class Meta:
        verbose_name_plural ='Mức độ văn bản'
    def __str__(self):
        return self.name
#================================== Văn bản mẫu  ==================================
class TemplateDocument(models.Model):
    document_type = models.ForeignKey(DocumentType,on_delete=models.SET_NULL,null=True,verbose_name='Loại văn bản')
    level = models.ForeignKey(DocumentLevel,on_delete=models.SET_NULL, null=True,verbose_name='Mức độ văn bản' )
    summary = models.TextField(verbose_name='Trích yêu')
    origin = models.CharField(max_length=255, null=True,  verbose_name='Nguồn gốc')
    number = models.CharField(max_length=255, null=True,  verbose_name='Số hiệu')
    publication_date = models.DateField(null=True, verbose_name='Ngày tạo gốc')
    status = models.BooleanField(default=True, verbose_name='Trạng thái')
    uploadfile = models.ManyToManyField('uploadFile',  verbose_name='File đính kèm')
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_template_documents', verbose_name='Người tạo')
    created_at = models.DateField(auto_now_add=True, verbose_name='Tạo ngày')
    updated_at = models.DateField(auto_now=True, verbose_name='Cập nhật ngày')
    description = models.TextField(null=True, verbose_name='Mô tả')

    class Meta:
        verbose_name_plural = 'Văn bản mẫu'

    def save(self, *args, **kwargs):
        if not self.creator:
            self.creator = get_current_user()

        super(TemplateDocument, self).save(*args, **kwargs)

    def get_files(self):
        return self.uploadfile.all()

    def __str__(self):
        return f'{self.document_type} - {self.summary}'


#================================== Trạng thái văn bản==================================
class ProcessStatus(models.Model):
    name = models.CharField(max_length=255, verbose_name='Tên trạng thái')
    description = models.TextField(blank=True, null=True, verbose_name='Mô tả')
    class Meta:
        verbose_name_plural ='Trạng thái xử lý văn bản'
    def __str__(self):
        return self.name


#================================== văn bản đến ==================================
class IncomingDocument(models.Model):
    issuing_agency = models.CharField(max_length=255, verbose_name='Cơ quan pháp hành')
    responsible_agency = models.CharField(max_length=255,verbose_name='Cơ quan chủ quản', null=True)
    reference_number = models.CharField(max_length=255,verbose_name='Số ký hiệu')
    level = models.ForeignKey(DocumentLevel,on_delete=models.SET_NULL, null=True,verbose_name='Mức độ văn bản' )
    document_type = models.ForeignKey(DocumentType,verbose_name='Loại văn bản', on_delete=models.SET_NULL, null=True )
    receipt_date = models.DateField(verbose_name='Ngày nhận văn bản',null=True)
    issuance_date = models.DateField(verbose_name='Ngày ban hành văn bản', null=True)
    current_number = models.CharField(max_length=255,verbose_name='Số hiện tại', null=True)
    arrival_number = models.CharField(max_length=255,verbose_name='Số đến', null=True) 
    summary = models.TextField(verbose_name='Trích yếu')
    advisory_opinions = models.TextField(verbose_name='Ý kiến tham mưu', null=True)
    uploadfile = models.ManyToManyField('uploadFile',  verbose_name='File đính kèm', blank=True)
    publish = models.BooleanField(default=True,verbose_name='Trạng thái lưu hành' )
    status = models.ForeignKey(ProcessStatus,verbose_name='Trạng thái xử lý', on_delete=models.SET_NULL, null=True )
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Người tạo')
    created_date = models.DateField(auto_now_add=True, verbose_name='Tạo ngày')
    updated_date = models.DateField(auto_now=True, verbose_name='Cập nhật ngày')
    
    class Meta:
        verbose_name_plural ='Văn bản đến'
        
    def save(self, *args, **kwargs):
        if not self.creator:
            self.creator = get_current_user()

        super(IncomingDocument, self).save(*args, **kwargs)

    def get_files(self):
        return self.uploadfile.all()
    
    def __str__(self):
        return self.summary


#================================== Văn bản đi ==================================
class OutgoingDocument(models.Model):
    reference_number = models.CharField(max_length=255,verbose_name='Số ký hiệu')
    level = models.ForeignKey(DocumentLevel,on_delete=models.SET_NULL, null=True,verbose_name='Mức độ văn bản' )
    document_type = models.ForeignKey(DocumentType,verbose_name='Loại văn bản', on_delete=models.SET_NULL, null=True )
    receipt_date = models.DateField(verbose_name='Ngày nhận văn bản',null=True)
    issuance_date = models.DateField(verbose_name='Ngày ban hành văn bản', null=True)
    current_number = models.CharField(max_length=255,verbose_name='Số hiện tại', null=True)
    arrival_number = models.CharField(max_length=255,verbose_name='Số đến', null=True) 
    summary = models.TextField(verbose_name='Trích yếu')
    advisory_opinions = models.TextField(verbose_name='Ý kiến tham mưu', null=True)
    uploadfile = models.ManyToManyField('uploadFile',  verbose_name='File đính kèm',  blank=True)
    publish = models.BooleanField(default=True,verbose_name='Trạng thái lưu hành' )
    status = models.ForeignKey(ProcessStatus,verbose_name='Trạng thái xử lý', on_delete=models.SET_NULL, null=True )
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Người tạo')
    created_at = models.DateField(auto_now_add=True, verbose_name='Tạo ngày')
    updated_at = models.DateField(auto_now=True, verbose_name='Cập nhật ngày')
    class Meta:
        verbose_name_plural ='Văn bản đi'
        
    def save(self, *args, **kwargs):
        if not self.creator:
            self.creator = get_current_user()

        super(OutgoingDocument, self).save(*args, **kwargs)

    def get_files(self):
        return self.uploadfile.all()
    
    def __str__(self):
        return self.summary



#================================== Quản lý file dùng chung ==================================
class uploadFile(models.Model):
    file = models.FileField(upload_to='files/', null=True)
    def __str__(self):
        return self.file.name

    
# Đặt trường request vào mô hình để có thể truy cập thông tin về người dùng hiện tại trong pre_save signal.
# Bạn có thể cài đặt middleware để đặt giá trị cho trường này từ mỗi request.
# Middleware sẽ giống như sau:
class RequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        request.user = request.user
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        setattr(request, 'user', request.user)
        
