from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .forms import *
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import timedelta
from itertools import groupby
from operator import attrgetter
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Count, Q
from django.http import HttpResponseBadRequest
from django.db import transaction
from django.db.models import Sum
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
from django.urls import reverse_lazy
from django.views import generic
# from django.contrib.auth.models import Group, Permission
from django.contrib.auth.hashers import make_password
import base64   
from django.http import Http404
import os
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.conf import settings
from django.views.defaults import permission_denied
from django.db.models.functions import ExtractMonth, ExtractQuarter, ExtractYear

#=============================== Quản lý trang chủ========================================
@login_required(login_url='login')
@permission_required('sessions.access_dashboard', raise_exception=True)
def dashboard(request):
        # Lấy ngày và giờ hiện tại
    current_date = timezone.now()

    # Thống kê số lượng văn bản đến theo tháng
    documents_by_month_incom = IncomingDocument.objects.filter(receipt_date__year=current_date.year) \
                                                   .annotate(month=ExtractMonth('receipt_date')) \
                                                   .values('month') \
                                                   .annotate(count=Count('id')).order_by('month')
                                                   
    # Thống kê số lượng văn bản đi theo tháng
    documents_by_month_out = OutgoingDocument.objects.filter(issuance_date__year=current_date.year) \
                                                  .annotate(month=ExtractMonth('issuance_date')) \
                                                  .values('month') \
                                                  .annotate(count=Count('id')).order_by('month')

    context = {
        'documents_by_month_incom': documents_by_month_incom,
        'documents_by_month_out':documents_by_month_out}
    return render(request, 'dashboard/dashboard.html', context)




@login_required(login_url='login')
def home(request):
    now = timezone.now()
    user = request.user
    # Lấy tất cả thông báo mà người dùng đó là người nhận
    notifications = Notification.objects.filter(recipients=user, status=True).order_by('-created_date')
    # Lấy số lượng thông báo mới chưa đọc
    unread_notification_count = notifications.exclude(read_by_users=user).count()
    
    tasks = Task.objects.filter(assigned_users=user).order_by('-created_date')
    
    # Lấy số công việc chưa xác nhận
    tasks_with_unconfirm_count = tasks.exclude(confirmed_users=user).count()
    context = {'notifications': notifications, 'now': now, 'unread_notification_count': unread_notification_count,
            'tasks_with_unconfirm_count': tasks_with_unconfirm_count,"tasks":tasks}
    return render(request, 'home/home.html', context)

#=============================== menu function ========================================
@login_required(login_url='login')
def view_notification_list(request):
    title = "Danh sách thông báo"
    user = request.user
    # Lấy tất cả thông báo mà người dùng đó là người nhận
    notifications = Notification.objects.filter(recipients=user, status=True).order_by('-created_date')
    context = {'notifications': notifications,'title':title}
    return render(request, 'notification/list_notification.html', context)

@login_required(login_url='login')
def view_task_list(request):
    title = "Danh sách công việc"
    # Lấy danh sách trạng thái từ mô hình Task
        
    user = request.user
    tasks = Task.objects.filter(assigned_users=user).order_by('-created_date')
    
    status_choices = Task.STSTUS_CHOICES
    # Lọc công việc dựa trên trạng thái nếu được chọn
    selected_status = request.GET.get('status')
    if selected_status and selected_status.isdigit():
        tasks = tasks.filter(status=int(selected_status))
        
    priority_choices = Task.PRIORITY_CHOICES
    selected_priority = request.GET.get('priority')
    if selected_priority and selected_priority.isdigit():
        tasks = tasks.filter(priority=int(selected_priority))
        
    context = {"tasks":tasks,"title":title,
               'status_choices':status_choices, 
               'priority_choices':priority_choices,
                'selected_status': request.GET.get('status', ''),
                'selected_priority': request.GET.get('priority', ''),}
    return render(request, 'work/task/list_task.html', context)

#=============================== Quên mật khẩu========================================
    

def send_otp_email(request,email):
    otp = get_random_string(length=6, allowed_chars='0123456789')
    subject = 'Xác nhận quên mật khẩu'
    message = f'Mã OTP của bạn là: {otp}'
    sender = 'UHL-Systeem'
    recipient_list = [email]
    send_mail(subject, message, sender, recipient_list)
    try:
        # Gửi email
        send_mail(subject, message, sender, recipient_list)
        
        # Lưu mã OTP vào session
        request.session['otp'] = otp
        
        # Thông báo gửi email thành công
        messages.success(request, "Gửi email thành công, vui lòng kiểm tra hòm thư email của bạn!")
        
    except Exception as e:
        # Xử lý lỗi khi gửi email
        messages.error(request, f"Có lỗi xảy ra khi gửi email: {e}")
    return otp

def send_email(request):
    if request.method == 'POST':
        form = SendEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if User.objects.filter(email=email).exists():
                # Email tồn tại trong hệ thống, thực hiện gửi email ở đây
                send_otp_email(request, email)
                
                request.session['reset_email'] = email
                return redirect('otp_auth')
            else:
                # Email không tồn tại trong hệ thống
                messages.error(request, "Email không tồn tại trong hệ thống.")
        else:
            # Form không hợp lệ, trả về form với các thông báo lỗi
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"<p>{field}: {error}</p>")
            messages.error(request,f"{error}")
    else:
        form = SendEmailForm()
    
    context = {'form': form}
    return render(request, 'auth/send_email.html', context)



def otp_auth(request):
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        otp_received = request.session.get('otp')  # Lấy mã OTP đã gửi từ email từ session
        
        # Kiểm tra xem mã OTP nhập vào có trùng khớp với mã OTP đã nhận được không
        if otp_entered == otp_received:
            # Mã OTP hợp lệ, thực hiện các hành động tương ứng ở đây
            # Ví dụ: chuyển hướng người dùng đến trang cài đặt lại mật khẩu
            request.session['otp_verified'] = True
            return redirect('reset_password')  # Chuyển hướng đến trang cài đặt lại mật khẩu
        else:
            # Mã OTP không hợp lệ, hiển thị thông báo lỗi cho người dùng
            messages.error(request, "Mã OTP không hợp lệ. Vui lòng thử lại.")
            return redirect('otp_auth')  # Chuyển hướng đến trang xác nhận OTP

    # Nếu phương thức không phải là POST, hoặc không có mã OTP nhận được, hiển thị lại form xác nhận OTP
    return render(request, 'auth/otp_auth.html')

def reset_password(request):
    
    # Kiểm tra xem người dùng đã xác nhận OTP chưa
    if not request.session.get('otp_verified'):
        messages.error(request, "Bạn phải xác nhận OTP trước khi đặt lại mật khẩu.")
        return redirect('send_email')  # Chuyển hướng về trang gửi email
    
    
    email = request.session.get('reset_email')
    username = None  # Gán giá trị mặc định cho biến username
    
    # Nếu phương thức là POST, xử lý dữ liệu và cài đặt lại mật khẩu
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm')
        
        # Kiểm tra xác nhận mật khẩu
        if password != confirm_password:
            messages.error(request, "Mật khẩu không khớp. Vui lòng nhập lại.")
            return redirect('reset_password')
        
        # Kiểm tra xem email có tồn tại trong hệ thống không
        try:
            user = User.objects.get(email=email)
            # Lấy username của người dùng từ đối tượng User
            username = user.username
        except User.DoesNotExist:
            messages.error(request, "Email không tồn tại trong hệ thống.")
            return redirect('reset_password')
        
        # Cập nhật mật khẩu cho người dùng
        user.password = make_password(password)
        user.save()
        
        subject = 'Thay đổi mật khẩu thành công'
        message = f'tên đăng nhập của bạn là: {username} và mật khẩu là{password}'
        sender = 'UHL-Systeem'
        recipient_list = [email]
        send_mail(subject, message, sender, recipient_list)
        
        messages.success(request, f"Cập nhật mật khẩu thành công. tên đăng nhập của bạn là: {username}")
        
        return redirect('login')
        
    return render(request, 'auth/reset_password.html',{'email':email})




#=============================== Quản lý log in/out========================================
def get_icheck():
    css_files = ['plugins/iCheck/custom.css']
    js_files = ['plugins/iCheck/icheck.min.js']
    custom_script = """
    $('.i-checks').iCheck({
        checkboxClass: 'icheckbox_square-green',
        radioClass: 'iradio_square-green',
    });
    """
    return {'custom_css': css_files, 'custom_js': js_files,'custom_script': custom_script}

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                new_user = form.save(commit=False)
                new_user.password = make_password(new_user.password)
                new_user.save()
                Account.objects.create(user=new_user)
                form.save()
                messages.success(request,"Đăng ký thành công, Vui lòng đợi xác nhận từ admin")
                return redirect('login')
            except Exception as e:
                messages.error(request,f"Có lỗi xảy ra khi lưu: {e}")
                print(f"Có lỗi xảy ra khi lưu: {e}")
                form.add_error(None, f"Có lỗi xảy ra khi lưu: {e}")
        else:
            print(f"Form không hợp lệ: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"<p>{field}: {error}</p>")
            messages.error(request,f"{error}")
    else:
        form = RegisterForm()
    
    context = {**get_icheck(),'form':form}
    return render(request, 'auth/register.html', context)


@login_required(login_url='login')
def logout(request):
    auth_logout(request)
    messages.success(request, 'Đăng xuất thành công')
    return redirect('login')


def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)
                messages.success(request, 'Đăng nhập thành công')
                if user.is_staff:
                    return redirect('dashboard')  # Chuyển hướng đến dashboard trong app backend
                else:
                    return redirect('home')  # Chuyển hướng đến home trong app frontend
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không chính xác.')
    else:
        form = AuthenticationForm()

    return render(request, 'auth/login.html', {'form': form})





#=============================== Quản lý công việc - tiến độ========================================
@login_required(login_url='login')
def confirm_task_participation(request, task_id):
    user = request.user
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        return HttpResponseBadRequest("Công việc không tồn tại")
    # Kiểm tra xem người dùng đã xác nhận tham gia công việc chưa
    if user not in task.confirmed_users.all():
        # Nếu chưa xác nhận, thì thêm vào danh sách
        task.confirmed_users.add(user)
        UserConfirmationTime.objects.create(user=user, task=task ,name = "xác nhận công việc")
         # Gọi phương thức cập nhật trạng thái ngay lập tức
        task.update_status_if_needed()
    # Redirect lại trang chi tiết công việc
    return redirect(request.META.get('HTTP_REFERER', '/'))

 
@login_required(login_url='login')
@permission_required('backend.view_task', raise_exception=True)
def task_detail(request, task_url):
    user = request.user
    now = timezone.now()
    task = get_object_or_404(Task, url=task_url)
    user_confirm_times = UserConfirmationTime.objects.filter(task=task).order_by('-confirmation_time')
    current_files = task.get_task_files()
    files = task.get_files()
    title = "Chi tiết công việc được giao"
    
    # Xử lý bình luận
    if request.method == 'POST' and 'comment-submit' in request.POST:
        # Chỉ xử lý bình luận nếu người dùng nhấn nút "Bình luận"
        form = handle_comment(request)
        if isinstance(form, Comment):
            task.comments.add(form)
            messages.success(request, 'Bình luận thành công.')
    else:
        form = CommentForm()

    # Lấy danh sách bình luận và các thông tin khác để hiển thị
    comments = task.comments.filter(status=True).order_by('-created_date')
    liked_comments = Comment.objects.filter(likes=request.user)
    if request.method == 'POST' and 'file-submit' in request.POST:
        # Chỉ xử lý tải lên file nếu người dùng nhấn nút "Tải lên file"
        uploaded_files = request.FILES.getlist('taskfiles')
        file_names = ', '.join([file.name for file in uploaded_files])
        with transaction.atomic():
            for uploaded_file in uploaded_files:
                upload_file = uploadFileTask(file=uploaded_file, task=task, upload_by=user)
                upload_file.save()
                task.taskfiles.add(upload_file)
            task.update_sum_progress()
            UserConfirmationTime.objects.create(user=user, task=task, name=f"upload file ({file_names})")
            messages.success(request, 'Upload file thành công.')
        return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        return render(request, 'work/task/detail.html',
                      {'task': task, 'title': title, 'user_confirm_times': user_confirm_times, 
                       'current_files': current_files,'files':files,'now':now, 
                       'form':form,'liked_comments':liked_comments,'comments':comments })


@login_required(login_url='login')
@permission_required('backend.view_task', raise_exception=True)
def task(request):
    tasks= Task.objects.all().order_by('-created_date',)
    title = "Quản lý công việc"
    # Lấy danh sách trạng thái từ mô hình Task
    status_choices = Task.STSTUS_CHOICES
    # Lọc công việc dựa trên trạng thái nếu được chọn
    selected_status = request.GET.get('status')
    if selected_status and selected_status.isdigit():
        tasks = tasks.filter(status=int(selected_status))
        
    priority_choices = Task.PRIORITY_CHOICES
    selected_priority = request.GET.get('priority')
    if selected_priority and selected_priority.isdigit():
        tasks = tasks.filter(priority=int(selected_priority))
        
    context = {'tasks': tasks, 'title': title, 
               'status_choices':status_choices, 
               'priority_choices':priority_choices,
                'selected_status': request.GET.get('status', ''),
                'selected_priority': request.GET.get('priority', ''),
    }
    return render(request,'work/task/index.html', context)



@login_required(login_url='login')
@permission_required('backend.add_task', raise_exception=True)
def add_task(request):
    title = "Thêm công việc"
    if request.method == 'POST':
        files = request.FILES.getlist('uploadfile')
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                task = form.save(commit=False)
                task.save()  
                form.save_m2m()  
                for file in files:
                    upload_file = uploadFile(file=file)
                    upload_file.save()
                    task.uploadfile.add(upload_file)
                    
                messages.success(request, 'Thêm mới công việc thành công.')   
                return redirect('task') 
            except Exception as e:                
                messages.error(request, 'Thêm mới công việc thất bại.')
                print(f"An error occurred: {e}")
                form.add_error(None, f"An error occurred: {e}")
        else:
            messages.error(request, f"Vui lòng nhập đầy đủ dữ liệu: {form.errors}")
            print(f"Vui lòng nhập đủ và đúng dữ liệu: {form.errors}")
    else:
        form = TaskForm()

    return render(request, 'work/task/add.html', {**get_custom_files_duallistbox(),'form': form, 'title': title,})

@login_required(login_url='login')
@permission_required('backend.delete_task', raise_exception=True)
def delete_task(request, task_url):
    task = get_object_or_404(Task, url=task_url)
    if request.method == 'POST':
        form = EditTaskForm(request.POST, request.FILES, instance=task)
        task.delete()
        messages.success(request,"Xóa công việc thành công")
        return redirect('task')
    else:
        form = EditTaskForm(instance=task)
    title = "Xóa lịch công tác"
    files = task.uploadfile.all()
    files_task = task.get_task_files()
    return render(request, 'work/task/delete.html', 
                  {**get_custom_files_duallistbox(),'form': form, 'task': task, 'title': title,
                    'files': files,'files_task': files_task})

@login_required(login_url='login')
@permission_required('backend.change_task', raise_exception=True)
def edit_task(request, task_url):
    user = request.user
    task = get_object_or_404(Task, url=task_url)
    title = "Chỉnh sửa công tác việc"
    if request.method == 'POST':
        form = EditTaskForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            try:
                edited_task = form.save(commit=False)
                edited_task.save()
                form.save_m2m()
                messages.success(request, 'Chỉnh sửa công việc thành công.')
                UserConfirmationTime.objects.create(user=user, task=task, name=f"Cập nhật từ hệ thống")
                return redirect('task')
            except Exception as e:
                messages.error(request, 'Sửa công việc thất bại.')
                print(f"An error occurred: {e}")
                form.add_error(None, f"An error occurred: {e}")
        else:
            messages.error(request, f"Vui lòng nhập đúng đủ dữ liệu: {form.errors}")
            print(f"Vui lòng nhập đầy đủ dữ liệu: {form.errors}")
    else:
        form = EditTaskForm(instance=task)
    # Lấy danh sách các file đã đính kèm với công việc
    files = task.uploadfile.all()
    files_task = task.get_task_files()
    return render(request, 'work/task/edit.html',
                  {**get_custom_files_duallistbox(),'form': form, 'task': task,
                   'title': title, 'files': files,'files_task': files_task })
   

#=============================== Quản lý lịch tuần========================================
@login_required(login_url='login')
@permission_required('backend.delete_week', raise_exception=True)
def delete_week(request, id):
    week = get_object_or_404(Week, id=id)
    if request.method == 'POST':
        form = WeekForm(request.POST, instance=week)
        week.delete()
        # Tạo URL với thông tin về tuần
        messages.success(request,"Xóa tuần thành công")
        return redirect('week')
    else:
        form = WeekForm(instance=week)
    title = "Xóa tuần"
    return render(request, 'work/week/delete.html', {'form': form, 'week': week, 'title': title})

@login_required(login_url='login')
@permission_required('backend.change_week', raise_exception=True)
def edit_week(request, id):
    week = get_object_or_404(Week, id=id)
    title = "Chỉnh sửa tuần"
    if request.method == 'POST':
        form = WeekForm(request.POST, instance=week)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Chỉnh sửa tuần thành công.')
                return redirect('week')
            except Exception as e:
                messages.error(request, 'Sửa lịch công tác thất bại.')
                print(f"An error occurred: {e}")
                form.add_error(None, f"An error occurred: {e}")
        else:
            messages.error(request, 'Vui lòng nhập đầy đủ dữ liệu.')
            messages.error(request, f"Vui lòng nhập đúng dữ liệu: {form.errors}")
            print(f"Vui lòng nhập đầy đủ dữ liệu: {form.errors}")
    else:
        form = WeekForm(instance=week)
    # Lấy danh sách các file đã đính kèm với thông báo
    return render(request, 'work/week/edit.html',
                  {'form': form, 'week': week,'title': title})

@login_required(login_url='login')
@permission_required('backend.add_week', raise_exception=True)
def create_week(request):
    # Gọi phương thức tạo tuần mới từ mô hình Week
    Week.create_week()
    # Sau khi tạo tuần mới, chuyển hướng người dùng đến trang nào đó
    return redirect('week')

@login_required(login_url='login')
@permission_required('backend.view_week', raise_exception=True)
def week(request):
    weeks = Week.objects.all().order_by('-year','-week_number',)
    title = "Quản lý tuần - lịch công tác"
    context = {'weeks': weeks, 'title': title}
    return render(request,'work/week/index.html', context)

@login_required(login_url='login')
@permission_required('backend.view_week', raise_exception=True)
def add_week(request):
    # Gọi phương thức tạo tuần mới từ mô hình Week
    Week.create_week()
    # Sau khi tạo tuần mới, chuyển hướng người dùng đến trang nào đó
    return redirect(request.META.get('HTTP_REFERER', '/'))     

#=============================== Quản lý lịch công tác========================================
@login_required(login_url='login')
@permission_required('backend.delete_schedule', raise_exception=True)
def delete_schedule(request, id):
    schedule = get_object_or_404(Schedule, id=id)
    # Lấy thông tin về tuần trước khi xóa lịch công tác
    selected_week_id = schedule.week_id
    try:
        selected_week = Week.objects.get(pk=selected_week_id)
    except ObjectDoesNotExist:
        messages.error(request, 'Tuần không tồn tại.')
        return redirect('schedule')
    if request.method == 'POST':
        form = ScheduleForm(request.POST, request.FILES, instance=schedule)
        schedule.delete()
        # Tạo URL với thông tin về tuần
        messages.success(request,"Xóa lịch công tác thành công")
        url = reverse('schedule') + f'?page={selected_week.week_number}'
        return HttpResponseRedirect(url)
    else:
        form = ScheduleForm(instance=schedule)
    title = "Xóa lịch công tác"
    return render(request, 'work/schedule/delete.html', {**get_custom_files_duallistbox(),'form': form, 'schedule': schedule, 'title': title})

@login_required(login_url='login')
@permission_required('backend.change_schedule', raise_exception=True)
def edit_schedule(request, id):
    schedule = get_object_or_404(Schedule, id=id)
    title = "Chỉnh sửa lịch công tác"
    selected_week_id = schedule.week_id
    try:
        selected_week = Week.objects.get(pk=selected_week_id)
    except ObjectDoesNotExist:
        messages.error(request, 'Tuần không tồn tại.')
        return redirect('schedule')
    if request.method == 'POST':
        form = ScheduleForm(request.POST, request.FILES, instance=schedule)
        if form.is_valid():
            try:
                edited_schedule = form.save(commit=False)
                edited_schedule.save()
                form.save_m2m()
                messages.success(request, 'Chỉnh sửa lịch công tác thành công.')
                url = reverse('schedule') + f'?page={selected_week.week_number}'
                return HttpResponseRedirect(url)
            except Exception as e:
                messages.error(request, 'Sửa lịch công tác thất bại.')
                print(f"An error occurred: {e}")
                form.add_error(None, f"An error occurred: {e}")
        else:
            messages.error(request, 'Vui lòng nhập đầy đủ dữ liệu.')
            messages.error(request, f"Vui lòng nhập đúng dữ liệu: {form.errors}")
            print(f"Vui lòng nhập đầy đủ dữ liệu: {form.errors}")
    else:
        form = ScheduleForm(instance=schedule)
    # Lấy danh sách các file đã đính kèm với thông báo
    return render(request, 'work/schedule/edit.html',
                  {**get_custom_files_duallistbox(),'form': form, 'schedule': schedule,'title': title})


@login_required(login_url='login')
@permission_required('backend.add_schedule', raise_exception=True)
def add_schedule(request):
    title = "Thêm lịch công tác"
    if request.method == 'POST':
        form = ScheduleForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                schedule = form.save(commit=False)   
                schedule.save()  
                form.save_m2m()
                selected_week_id = schedule.week_id
                try:
                    selected_week = Week.objects.get(pk=selected_week_id)
                except ObjectDoesNotExist:
                    messages.error(request, 'Tuần không tồn tại.')
                    return redirect('schedule')
                
                messages.success(request, 'Thêm mới lịch công tác thành công.')
                url = reverse('schedule') + f'?page={selected_week.week_number}'
                return HttpResponseRedirect(url)
            except Exception as e:                
                messages.error(request, 'Thêm mới lịch công tác thất bại.')
                messages.error(request, f"An error occurred: {e}")
                print(f"An error occurred: {e}")
                form.add_error(None, f"An error occurred: {e}")
        else:
            messages.error(request, 'Vui lòng nhập đầy đủ dữ liệu.')
            messages.error(request, f"Vui lòng nhập đúng dữ liệu: {form.errors}")
            print(f"Vui lòng nhập đầy đủ dữ liệu: {form.errors}")
    else:
        form = ScheduleForm()

    return render(request, 'work/schedule/add.html', {**get_custom_files_duallistbox(),'form': form, 'title': title,})
   
@login_required(login_url='login')
@permission_required('backend.view_schedule', raise_exception=True)
def schedule(request):
    weeks = Week.objects.all().order_by('start_date')
    weeks_per_page = 1 
    paginator = Paginator(weeks, weeks_per_page)
    # Kiểm tra xem có tham số 'page' trong URL không
    if 'page' not in request.GET:
        # Nếu không có, chuyển hướng đến trang cuối cùng
        return redirect(reverse('schedule') + f'?page={paginator.num_pages}')
    page = request.GET.get('page', 1)
    try:
        current_weeks = paginator.page(page)
    except PageNotAnInteger:
        # Nếu 'page' không phải là số nguyên, chuyển hướng đến trang cuối cùng
        return redirect(f'?page={paginator.num_pages}')
    except EmptyPage:
        # Nếu 'page' lớn hơn số lượng trang, chuyển hướng đến trang cuối cùng
        return redirect(f'?page={paginator.num_pages}')
    start_page = max(1, current_weeks.number - 1)
    end_page = min(current_weeks.paginator.num_pages, current_weeks.number + 1)
    page_list = range(start_page, end_page + 1)
    # Lấy ngày bắt đầu của tuần
    start_date_of_week = current_weeks.object_list[0].start_date
    # Lấy ngày thứ hai, thứ ba, v.v.
    days_of_week = [start_date_of_week + timedelta(days=i) for i in range(7)]
    latest_week_schedule = (
        Schedule.objects.filter(week=current_weeks.object_list[0]) if current_weeks.object_list else []
    ).order_by('work_date', 'start_time')    
    title = "Quản lý lịch công tác"
    context = {
        'latest_week_schedule': latest_week_schedule,
        'weeks': current_weeks,
        'title': title,
        'page_list': page_list,
        'days_of_week': days_of_week,
      
    }
    return render(request, 'work/schedule/index.html', context)


@login_required(login_url='login')
def search_schedule(request):
    query = request.GET.get('q', '')
    page_number = request.GET.get('page', 1)

    category_mapping = {
        'Lịch cá nhân': Schedule.CA_NHAN,
        'Lịch phòng ban': Schedule.PHONG_BAN,
        'Lịch khoa': Schedule.PHONG_BAN,
        'Lịch trường': Schedule.TRUONG,
        'Lịch lãnh đạo': Schedule.LANH_DAO,
    }

    category_value = category_mapping.get(query, None)

    if category_value is not None:
        latest_week_schedule = Schedule.objects.filter(schedule_category=category_value).order_by('-work_date', 'start_time')
    else:
        latest_week_schedule = Schedule.objects.filter(
            Q(content__icontains=query) |
            Q(location__icontains=query) |
            Q(leading_official__icontains=query) |
            Q(schedule_category__icontains=query) |
            Q(department__department_name__icontains=query)  # Assuming department has a 'name' field
        ).order_by('-work_date', 'start_time')
        
        

    title = f"Kết quả tìm kiếm cho '{query}'"

    context = {
        'latest_week_schedule': latest_week_schedule,
        'title': title,
    }

    return render(request, 'work/schedule/search.html', context)



#=============================== Quản lý văn bản đi========================================

@login_required(login_url='login')
@permission_required('backend.delete_outgoingdocument', raise_exception=True)
def delete_outgoing_docu(request, id):
    outgoing_docu = get_object_or_404(OutgoingDocument, id=id)
    files = outgoing_docu.uploadfile.all()
    if request.method == 'POST':
        form = EditOutgoingDocuForm(request.POST, request.FILES, instance=outgoing_docu)
        outgoing_docu.delete()
        return redirect('outgoing_docu') 
    else:
        form = EditOutgoingDocuForm(instance=outgoing_docu) 

    title = "Xóa văn bản đến"
    docutypes = DocumentType.objects.filter(status=True)
    return render(request, 'document/outgoingdocument/delete.html', 
                  {'form':form,'outgoing_docu': outgoing_docu, 
                   'title': title, 'files':files,'docutypes':docutypes})

@login_required(login_url='login')
@permission_required('backend.change_outgoingdocument', raise_exception=True)
def edit_outgoing_docu(request, id):
    outgoing_docu = get_object_or_404(OutgoingDocument, id=id)
    title = "Chỉnh sửa văn bản đến"
    if request.method == 'POST':
        form = EditOutgoingDocuForm(request.POST, request.FILES, instance=outgoing_docu)
        publish = request.POST.get('publish')
        if form.is_valid():
            try:
                edited_outgoing_docu = form.save(commit=False)
                edited_outgoing_docu.publish = bool(int(publish))
                edited_outgoing_docu.save()
                form.save_m2m()
                return redirect('outgoing_docu')
            except Exception as e:
                print(f"Có lỗi xảy ra khi lưu: {e}")
                form.add_error(None, f"Có lỗi xảy ra khi lưu: {e}")
        else:
            print(f"Form không hợp lệ: {form.errors}")
    else:
        form = EditOutgoingDocuForm(instance=outgoing_docu)
    # Lấy danh sách các file đã đính kèm với thông báo
    files = outgoing_docu.uploadfile.all()
    docutypes = DocumentType.objects.filter(status=True)
    return render(request, 'document/outgoingdocument/edit.html', 
                  {'form': form, 'outgoing_docu': outgoing_docu, 
                   'title': title, 'files': files, 'docutypes':docutypes})

@login_required(login_url='login')
@permission_required('backend.view_outgoingdocument', raise_exception=True)
def outgoing_docu(request):
    outgoing_docus = OutgoingDocument.objects.all().order_by('-created_at')
    title = "Quản lý văn bản đi"
    context = {'outgoing_docus': outgoing_docus, 'title': title}
    return render(request,'document/outgoingdocument/index.html', context)


def update_status_outgoing_docu(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        publish = request.POST.get('publish')
        try:
            outgoing_docu = OutgoingDocument.objects.get(id=id)
            outgoing_docu.publish = bool(int(publish))
            outgoing_docu.save()

            return JsonResponse({'success': True})
        except Position.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'DocumentType not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required(login_url='login')
@permission_required('backend.add_outgoingdocument', raise_exception=True)
def add_outgoing_docu(request):
    docutypes = DocumentType.objects.filter(status=True)
    title = "Thêm văn bản đi"
    if request.method == 'POST':
        files = request.FILES.getlist('uploadfile')
        publish = request.POST.get('publish')
        form = OutgoingDocuForm(request.POST, request.FILES)
        print(request.POST)
        if form.is_valid():
            try:
                outgoing_docu = form.save(commit=False)
                outgoing_docu.publish = bool(int(publish))
                outgoing_docu.save()  
                form.save_m2m()  
                for file in files:
                    upload_file = uploadFile(file=file)
                    upload_file.save()
                    outgoing_docu.uploadfile.add(upload_file)
                    
                messages.success(request, 'Thêm mới văn bản đi thành công.')   
                return redirect('outgoing_docu') 
            except Exception as e:                
                messages.error(request, 'Thêm mới văn bản đi thất bại.')
                print(f"An error occurred: {e}")
                form.add_error(None, f"An error occurred: {e}")
        else:
            messages.error(request, 'Vui lòng nhập đầy đủ dữ liệu.')
            print(f"Vui lòng nhập đầy đủ dữ liệu: {form.errors}")
    else:
        form = OutgoingDocuForm()

    return render(request, 'document/outgoingdocument/add.html', {'form': form, 'title': title, 
                                                                  'docutypes': docutypes
                                                                 })
    
#=============================== Quản lý văn bản đến========================================

@login_required(login_url='login')
@permission_required('backend.delete_incomingdocument', raise_exception=True)
def delete_income_docu(request, id):
    income_docu = get_object_or_404(IncomingDocument, id=id)
    files = income_docu.uploadfile.all()
    if request.method == 'POST':
        form = EditIncomeDocuForm(request.POST, request.FILES, instance=income_docu)
        income_docu.delete()
        return redirect('income_docu') 
    else:
        form = EditIncomeDocuForm(instance=income_docu) 

    title = "Xóa văn bản đến"
    docutypes = DocumentType.objects.filter(status=True)
    return render(request, 'document/incomingdocument/delete.html', 
                  {'form':form,'income_docu': income_docu, 
                   'title': title, 'files':files,'docutypes':docutypes})

@login_required(login_url='login')
@permission_required('backend.change_incomingdocument', raise_exception=True)
def edit_income_docu(request, id):
    income_docu = get_object_or_404(IncomingDocument, id=id)
    title = "Chỉnh sửa văn bản đến"
    if request.method == 'POST':
        form = EditIncomeDocuForm(request.POST, request.FILES, instance=income_docu)
        publish = request.POST.get('publish')
        if form.is_valid():
            try:
                edited_income_docu = form.save(commit=False)
                edited_income_docu.publish = bool(int(publish))
                edited_income_docu.save()
                form.save_m2m()
                return redirect('income_docu')
            except Exception as e:
                print(f"Có lỗi xảy ra khi lưu: {e}")
                form.add_error(None, f"Có lỗi xảy ra khi lưu: {e}")
        else:
            print(f"Form không hợp lệ: {form.errors}")
    else:
        form = EditIncomeDocuForm(instance=income_docu)
    # Lấy danh sách các file đã đính kèm với thông báo
    files = income_docu.uploadfile.all()
    docutypes = DocumentType.objects.filter(status=True)
    return render(request, 'document/incomingdocument/edit.html', 
                  {'form': form, 'income_docu': income_docu, 
                   'title': title, 'files': files, 'docutypes':docutypes})

@login_required(login_url='login')
@permission_required('backend.view_incomingdocument', raise_exception=True)
def income_docu(request):
    income_docus = IncomingDocument.objects.all().order_by('-id')
    title = "Quản lý văn bản đến"
    context = {'income_docus': income_docus, 'title': title}
    return render(request,'document/incomingdocument/index.html', context)

@login_required(login_url='login')
@permission_required('backend.view_incomingdocument', raise_exception=True)
def update_status_income_docu(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        publish = request.POST.get('publish')
        try:
            income_docu = IncomingDocument.objects.get(id=id)
            income_docu.publish = bool(int(publish))
            income_docu.save()

            return JsonResponse({'success': True})
        except Position.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'DocumentType not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required(login_url='login')
@permission_required('backend.add_incomingdocument', raise_exception=True)
def add_income_docu(request):
    docutypes = DocumentType.objects.filter(status=True)
    title = "Thêm văn bản mẫu"
    if request.method == 'POST':
        files = request.FILES.getlist('uploadfile')
        publish = request.POST.get('publish')
        form = IncomeDocuForm(request.POST, request.FILES)
        print(request.POST)
        if form.is_valid():
            try:
                income_docu = form.save(commit=False)
                income_docu.publish = bool(int(publish))
                income_docu.save()  
                form.save_m2m()  
                for file in files:
                    upload_file = uploadFile(file=file)
                    upload_file.save()
                    income_docu.uploadfile.add(upload_file)
                    
                messages.success(request, 'Thêm mới văn bản đến thành công.')   
                return redirect('income_docu') 
            except Exception as e:                
                messages.error(request, 'Thêm mới văn bản đến thất bại.')
                print(f"An error occurred: {e}")
                form.add_error(None, f"An error occurred: {e}")
        else:
            messages.error(request, 'Vui lòng nhập đầy đủ dữ liệu.')
            print(f"Vui lòng nhập đầy đủ dữ liệu: {form.errors}")
    else:
        form = IncomeDocuForm()

    return render(request, 'document/incomingdocument/add.html', {'form': form, 'title': title, 
                                                                  'docutypes': docutypes
                                                                 })



#=============================== Quản lý trạng thái văn bản========================================
@login_required(login_url='login')
@permission_required('backend.delete_processstatus', raise_exception=True)
def delete_docu_status(request, id):
    title = "Xóa trạng thái xử lý văn bản"
    docu_status = get_object_or_404(ProcessStatus, id=id)

    if request.method == 'POST':
        # Xóa loại văn bản
        docu_status.delete()
        return redirect('docu_status')

    return render(request, 'document/docustatus/delete.html', {'docu_status': docu_status, 'title':title})

@login_required(login_url='login')
@permission_required('backend.change_processstatus', raise_exception=True)
def edit_docu_status(request, id):
    docu_status = get_object_or_404(ProcessStatus, id=id)
    title = "Chỉnh sửa trạng thái xử lý văn bản"
    if request.method == 'POST':
        form = ProcessStatusForm(request.POST)  # Sử dụng form nếu có
        if form.is_valid():
            # Lưu thông tin chỉnh sửa vào đối tượng docu_cate
            docu_status.name = form.cleaned_data['name']
            docu_status.description = form.cleaned_data['description']
            docu_status.save()
            return redirect('docu_status')
    else:
        # Nếu là GET request, hiển thị form với thông tin hiện tại
        form = ProcessStatusForm(instance=docu_status)
    context = {'form': form, 'title': title, 'docu_status': docu_status}
    return render(request, 'document/docustatus/edit.html', context)

@login_required(login_url='login')
@permission_required('backend.add_processstatus', raise_exception=True)
def add_docu_status(request):
    title = "Thêm trạng thái xử lý văn bản"
    if request.method == 'POST':
        form = ProcessStatusForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            form.save()
            return redirect('docu_status')  # Redirect to a page where you list all positions
    else:
        form = ProcessStatusForm()

    context = {'form': form, 'title': title}
    return render(request, 'document/docustatus/add.html', context)

@login_required(login_url='login')
@permission_required('backend.view_processstatus', raise_exception=True)
def docu_status(request):
    title = "Quản lý trạng thái xử lý văn bản"
    docu_status = ProcessStatus.objects.all()
    context = {'docu_status': docu_status, 'title': title}
    return render(request, 'document/docustatus/index.html', context)

#=============================== Quản lý uploadfile========================================

@login_required(login_url='login')
@permission_required('backend.change_uploadfile', raise_exception=True)
def upload_file_view(request):
    if request.method == 'POST':
        uploaded_files = request.FILES.getlist('file')
        success_count = 0

        for uploaded_file in uploaded_files:
            upload_file_instance = uploadFile(file=uploaded_file)
            upload_file_instance.save()
            success_count += 1

        if success_count > 0:
            messages.success(request, f'Upload {success_count} file thành công!')
        else:
            messages.error(request, 'Không tìm thấy file để tải lên.')

    # Sau khi xử lý xong, chuyển hướng về trang trước đó
    return redirect(request.META.get('HTTP_REFERER', '/'))


#=============================== Quản lý văn bản mẫu========================================
@login_required(login_url='login')
@permission_required('backend.change_templatedocument', raise_exception=True)
def edit_tem_docu(request, id):
    tem_docu = get_object_or_404(TemplateDocument, id=id)
    title = "Chỉnh sửa văn bản mẫu"
    if request.method == 'POST':
        form = TemplateDocuForm(request.POST, request.FILES, instance=tem_docu)
        status = request.POST.get('status')
        if form.is_valid():
            try:
                edited_tem_docu = form.save(commit=False)
                edited_tem_docu.status = bool(int(status))
                edited_tem_docu.save()
                form.save_m2m()
                return redirect('tem_docu')
            except Exception as e:
                print(f"Có lỗi xảy ra khi lưu: {e}")
                form.add_error(None, f"Có lỗi xảy ra khi lưu: {e}")
        else:
            print(f"Form không hợp lệ: {form.errors}")
    else:
        form = TemplateDocuForm(instance=tem_docu)
    # Lấy danh sách các file đã đính kèm với thông báo
    files = tem_docu.uploadfile.all()
    return render(request, 'document/templatedocument/edit.html', {'form': form, 'tem_docu': tem_docu, 'title': title, 'files': files})

    
@login_required(login_url='login')
@permission_required('backend.change_templatedocument', raise_exception=True)
def tem_docu(request):
    current_page = 'tem_docu'  # Đặt tên trang hiện tại, ví dụ: 'tem_docu'
    tem_docus = TemplateDocument.objects.all().order_by('-created_at')
    title = "Quản lý văn bản mẫu"
    context = {'tem_docus': tem_docus, 'title': title, 'current_page': current_page}
    return render(request, 'document/templatedocument/index.html', context)

@login_required(login_url='login')
@permission_required('backend.view_templatedocument', raise_exception=True)
def update_status_tem_docu(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        status = request.POST.get('status')

        try:
            tem_docu = TemplateDocument.objects.get(id=id)
            tem_docu.status = bool(int(status))
            tem_docu.save()

            return JsonResponse({'success': True})
        except Position.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'DocumentType not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required(login_url='login')
@permission_required('backend.add_templatedocument', raise_exception=True)
def add_tem_docu(request):
    title = "Thêm văn bản mẫu"
    if request.method == 'POST':
        form = TemplateDocuForm(request.POST, request.FILES)
        print(request.POST)
        if form.is_valid():
            try:
                tem_docu = form.save(commit=False)
                tem_docu.save()  
                form.save_m2m()  

                files = request.FILES.getlist('uploadfile')
                for file in files:
                    upload_file = uploadFile(file=file)
                    upload_file.save()
                    tem_docu.uploadfile.add(upload_file)
                    
                messages.success(request, 'Thêm mới văn bản mẫu thành công.')   
                return redirect('tem_docu')  # Chuyển hướng đến trang danh sách thông báo sau khi thêm thành công
            except Exception as e:
                # Handle the exception, e.g., log it or display an error message to the user
                messages.error(request, 'Thêm mới văn bản mẫu thất bại.')
                print(f"An error occurred: {e}")
                form.add_error(None, f"An error occurred: {e}")
        else:
            messages.error(request, 'Vui lòng nhập đầy đủ dữ liệu.')
            messages.error(request, f"Form is not valid: {form.errors}")
            # Handle the case where the form is not valid
            print(f"Form is not valid: {form.errors}")

    # If form is not valid or there was an error, it will render the form with errors
    else:
        form = TemplateDocuForm()

    return render(request, 'document/templatedocument/add.html', {'form': form, 'title': title})


@login_required(login_url='login')
@permission_required('backend.delete_templatedocument', raise_exception=True)
def delete_tem_docu(request, id):
    tem_docu = get_object_or_404(TemplateDocument, id=id)
    files = tem_docu.uploadfile.all()

    if request.method == 'POST':
        tem_docu.delete()
        return redirect('tem_docu')  # Chuyển hướng đến trang danh sách thông báo sau khi xóa thành công

    title = "Xóa văn bản mẫu"
    return render(request, 'document/templatedocument/delete.html', {'tem_docu': tem_docu, 'title': title, 'files':files})


#=============================== Quản lý mức độ văn bản========================================

@login_required(login_url='login')
@permission_required('backend.delete_documentlevel', raise_exception=True)
def delete_docu_level(request, id):
    title = "Xóa mức độ văn bản"
    docu_level = get_object_or_404(DocumentLevel, id=id)

    if request.method == 'POST':
        # Xóa loại văn bản
        docu_level.delete()
        return redirect('docu_level')

    return render(request, 'document/documentlevel/delete.html', {'docu_level': docu_level, 'title':title})

@login_required(login_url='login')
@permission_required('backend.change_documentlevel', raise_exception=True)
def edit_docu_level(request, id):
    docu_level = get_object_or_404(DocumentLevel, id=id)
    title = "Chỉnh sửa mức độ văn bản"
    if request.method == 'POST':
        form = DocumentLevelForm(request.POST)  # Sử dụng form nếu có
        if form.is_valid():
            # Lưu thông tin chỉnh sửa vào đối tượng docu_cate
            docu_level.name = form.cleaned_data['name']
            docu_level.description = form.cleaned_data['description']
            docu_level.save()
            return redirect('docu_level')
    else:
        # Nếu là GET request, hiển thị form với thông tin hiện tại
        form = DocumentLevelForm(instance=docu_level)
    context = {'form': form, 'title': title, 'docu_level': docu_level}
    return render(request, 'document/documentlevel/edit.html', context)

@login_required(login_url='login')
@permission_required('backend.add_documentlevel', raise_exception=True)
def add_docu_level(request):
    title = "Thêm mức độ văn bản"
    if request.method == 'POST':
        form = DocumentLevelForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            form.save()
            return redirect('docu_level')  # Redirect to a page where you list all positions
    else:
        form = DocumentLevelForm()

    context = {'form': form, 'title': title}
    return render(request, 'document/documentlevel/add.html', context)

@login_required(login_url='login')
@permission_required('backend.view_documentlevel', raise_exception=True)
def docu_level(request):
    title = "Quản lý mức độ văn bản"
    docu_levels = DocumentLevel.objects.all()
    context = {'docu_levels': docu_levels, 'title': title}
    return render(request, 'document/documentlevel/index.html', context)


#=============================== Quản lý loại văn bản========================================
@login_required(login_url='login')
@permission_required('backend.add_documenttype', raise_exception=True)
def delete_docu_cate(request, docu_cate_id):
    title = "Xóa loại văn bản"
    docu_cate = get_object_or_404(DocumentType, id=docu_cate_id)

    if request.method == 'POST':
        # Xóa loại văn bản
        docu_cate.delete()
        return redirect('docu_cate')

    return render(request, 'document/documentcategory/delete.html', {'docu_cate': docu_cate, 'title':title})

@login_required(login_url='login')
@permission_required('backend.change_documenttype', raise_exception=True)
def edit_docu_cate(request, docu_cate_id):
    docu_cate = get_object_or_404(DocumentType, id=docu_cate_id)
    title = "Chỉnh sửa loại văn bản"
    if request.method == 'POST':
        form = DocumentTypeForm(request.POST)  # Sử dụng form nếu có
        if form.is_valid():
            # Lưu thông tin chỉnh sửa vào đối tượng docu_cate
            docu_cate.document_name = form.cleaned_data['document_name']
            docu_cate.description = form.cleaned_data['description']
            docu_cate.save()
           
            return redirect('docu_cate')
    else:
        # Nếu là GET request, hiển thị form với thông tin hiện tại
        form = DocumentTypeForm(instance=docu_cate)
    context = {'form': form, 'title': title, 'docu_cate': docu_cate}
    return render(request, 'document/documentcategory/edit.html', context)

@login_required(login_url='login')
@permission_required('backend.view_documenttype', raise_exception=True)
def update_status_docu_cate(request):
    if request.method == 'POST':
        docu_cate_id = request.POST.get('docu_cate_id')
        status = request.POST.get('status')

        try:
            position = DocumentType.objects.get(id=docu_cate_id)
            position.status = bool(int(status))
            position.save()

            return JsonResponse({'success': True})
        except Position.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'DocumentType not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required(login_url='login')
@permission_required('backend.add_documenttype', raise_exception=True)
def add_docu_cate(request):
    title = "Thêm loại văn bản"
    if request.method == 'POST':
        form = DocumentTypeForm(request.POST)
        if form.is_valid():
            position = form.save(commit=False)
            position.status = True
            form.save()
            return redirect('docu_cate')  # Redirect to a page where you list all positions
    else:
        form = DocumentTypeForm()

    context = {'form': form, 'title': title}
    return render(request, 'document/documentcategory/add.html', context)

@login_required(login_url='login')
@permission_required('backend.view_documenttype', raise_exception=True)
def docu_cate(request):
    title = "Quản lý loại văn bản"
    docu_cates = DocumentType.objects.all()
    context = {'docu_cates': docu_cates, 'title': title}
    return render(request, 'document/documentcategory/index.html', context)


# =============== COmmnet =====================
@login_required(login_url='login')
@permission_required('backend.delete_comment', raise_exception=True)
def delete_comment2(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.method == 'GET':
        comment.delete()
    
    return redirect('comment')  # Redirect to the comment listing page

def toggle_like(request, comment_id):
    user = request.user
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user.is_authenticated:
        comment.toggle_like(user)

    likes_count = comment.get_like_count()
    user_has_liked = comment.user_has_liked(user)
    return JsonResponse({'likes_count': likes_count, 'user_has_liked': user_has_liked})

@login_required(login_url='login')
@permission_required('backend.add_comment', raise_exception=True)
def add_reply(request, comment_id):
    if request.method == 'POST':
        parent_comment = Comment.objects.get(id=comment_id)
        content = request.POST.get('content', '')
        user = request.user  # Đảm bảo người dùng đã đăng nhập
        ip_address = request.ip_address
        parent_comment.add_reply(user, content, ip_address)

        return redirect(request.META.get('HTTP_REFERER', '/')) 

    return redirect(request.META.get('HTTP_REFERER', '/')) 

@login_required(login_url='login')
@permission_required('backend.delete_comment', raise_exception=True)
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    # Kiểm tra quyền hạn xóa, ví dụ: chỉ người tạo mới có thể xóa
    print("============================",comment.can_delete(request.user))
    if not comment.can_delete(request.user):
        return redirect(request.META.get('HTTP_REFERER', '/'))
    # Xóa bình luận và tất cả các bình luận con
    comment.delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='login')
@permission_required('backend.change_comment', raise_exception=True)
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if not comment.can_edit(request.user):
        messages.error(request, "Bạn không có quyền chỉnh sửa bình luận này.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    if request.method == 'POST':
        new_content = request.POST.get('content', '')
        comment.edit_comment(request.user, new_content)
        messages.success(request, "Bình luận đã được chỉnh sửa thành công.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    return render(request, 'edit_comment.html', {'comment': comment})

@login_required(login_url='login')
@permission_required('backend.view_comment', raise_exception=True)
def comment(request):
    comments = Comment.objects.all().order_by('-created_date')
    title = "Quản lý bình luận"
    status_choices = Comment.STATUS_CHOICES

    selected_status = request.GET.get('status', '')

    if selected_status and selected_status != 'all':
        comments = comments.filter(status=selected_status)
    
    context = {'comments': comments, 'title': title, 'status_choices': status_choices, 'selected_status': selected_status}
    return render(request, 'comment/index.html', context)

@login_required(login_url='login')
@permission_required('backend.view_comment', raise_exception=True)
def update_status_comment(request):
    if request.method == 'POST':
        comment_id = request.POST.get('comment_id')
        status = request.POST.get('status')

        try:
            comment = get_object_or_404(Comment, id=comment_id)
            new_status = bool(int(status))

            # Cập nhật trạng thái và lan truyền đến các bình luận con
            comment.update_status_recursive(new_status)

            return JsonResponse({'success': True})
        except Comment.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'comment_id not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def handle_comment(request, form_data=None):
    if request.method == 'POST':
        if form_data is None:
            form = CommentForm(request.POST)
        else:
            form = CommentForm(form_data)

        if form.is_valid():
            content = form.cleaned_data['content']
            comment = Comment(content=content, user=request.user, ip_address = request.ip_address)
            comment.save()

            return comment  # Hoặc trả về bất kỳ giá trị nào bạn cần sau khi xử lý comment
    else:
        if form_data is None:
            form = CommentForm()
        else:
            form = CommentForm(form_data)
    return form

#=============================== Quản lý thông báo========================================
def get_custom_files_notification():
    css_files = ['plugins/summernote/summernote.css', 
                 'plugins/summernote/summernote-bs3.css',
                 'plugins/dualListbox/bootstrap-duallistbox.min.css']
    js_files = ['plugins/summernote/summernote.min.js',
                'plugins/dualListbox/jquery.bootstrap-duallistbox.js']
    custom_script = "$('.summernote').summernote(); \n $('.dual_select').bootstrapDualListbox({selectorMinimalHeight: 160});"
    return {'custom_css': css_files, 'custom_js': js_files, 'custom_script': custom_script}



@login_required(login_url='login')
def notification(request, notification_url):
    now = timezone.now()
    title="Chi tiết thông báo"
    notification = get_object_or_404(Notification, url=notification_url)
    # Kiểm tra xem người dùng đã đọc thông báo chưa
    read_record, created = ReadRecord.objects.get_or_create(user=request.user, notification=notification)
    # Nếu chưa đọc, tăng số lần đọc
    if not created:
        read_record.read_count += 1
        read_record.save()

    files = notification.get_files()
    
    # Tính tổng số lượt đọc từ tất cả người dùng
    total_read_count = notification.read_by_users.aggregate(Sum('readrecord__read_count'))['readrecord__read_count__sum'] or 0
        
    form = handle_comment(request)

    if isinstance(form, Comment):
        # Nếu handle_comment trả về một Comment object, thực hiện các bước tiếp theo
        notification.comments.add(form)

        # Redirect để tránh việc gửi lại dữ liệu khi người dùng làm mới trang
        return redirect('notification', notification_url=notification_url)
        
    comments = notification.get_commnet().filter(status=True).order_by('-created_date')
    liked_comments = Comment.objects.filter(likes=request.user)
    
    return render(request, 'notification/notification.html', 
                  {'notification': notification,'now':now,
                   'files': files, 'title': title,
                   'form': form,'comments':comments,
                   'total_read_count': total_read_count,
                   'liked_comments':liked_comments})
    
@login_required(login_url='login')
@permission_required('backend.view_notification', raise_exception=True)
def list_noti(request):
    notifications = Notification.objects.all().order_by('-created_date')
    title = "Quản lý thông báo"
    # Lấy danh sách giá trị trạng thái từ mô hình Notification
    status_choices = Notification.STATUS_CHOICES

    # Lấy giá trị trạng thái từ request.GET
    selected_status = request.GET.get('status', '')

    # Xử lý lọc nếu có giá trị trạng thái được chọn
    if selected_status:
        notifications = notifications.filter(status=selected_status)
    
    context = {'notifications': notifications, 'title': title, 'status_choices': status_choices}
    return render(request,'notification/index.html', context)

@login_required(login_url='login')
@permission_required('backend.add_notification', raise_exception=True)
def add_notification(request):
    title = "Thêm thông báo"
    if request.method == 'POST':
        form = AddNotificationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                notification = form.save(commit=False)
                notification.save()  # Save the Notification instance to get an id
                form.save_m2m()  # Save the many-to-many relationships
                
                # Save the uploaded files and link them to the notification
                files = request.FILES.getlist('uploadfile')
                for file in files:
                    upload_file = uploadFile(file=file)
                    upload_file.save()
                    notification.uploadfile.add(upload_file)
                messages.success(request,"Thêm thông báo thành công!")
                return redirect('list_noti')  # Chuyển hướng đến trang danh sách thông báo sau khi thêm thành công
            except Exception as e:
                messages.error(request,f"An error occurred: {e}")
                print(f"An error occurred: {e}")
                form.add_error(None, f"An error occurred: {e}")
        else:
            # Handle the case where the form is not valid
            print(f"Form is not valid: {form.errors}")

    # If form is not valid or there was an error, it will render the form with errors
    else:
        form = AddNotificationForm()
    context = {**get_custom_files_notification(), 'form': form, 'title': title}
    return render(request, 'notification/add.html', context)


@login_required(login_url='login')
@permission_required('backend.change_notification', raise_exception=True)
def edit_notification(request, notification_url):
    notification = get_object_or_404(Notification, url=notification_url)
    title = "Chỉnh sửa thông báo"

    # Handle form submission
    if request.method == 'POST':
        form = NotificationForm(request.POST, request.FILES, instance=notification)
        status = request.POST.get('status')
        if form.is_valid():
            try:
                edited_notification = form.save(commit=False)
                edited_notification.status = bool(int(status))
                edited_notification.save()
                form.save_m2m()
                return redirect('list_noti')
            except Exception as e:
                print(f"Có lỗi xảy ra khi lưu: {e}")
                form.add_error(None, f"Có lỗi xảy ra khi lưu: {e}")
        else:
            print(f"Form không hợp lệ: {form.errors}")
            return render(request, 'notification/edit.html', {'form': form, 'notification': notification})
    else:
        form = NotificationForm(instance=notification)

    # Lấy danh sách các file đã đính kèm với thông báo
    files = notification.uploadfile.all()

    return render(request, 'notification/edit.html', 
                  {**get_custom_files_notification(),'form': form, 'notification': notification, 
                   'title': title, 'files': files})

@login_required(login_url='login')
@permission_required('backend.delete_notification', raise_exception=True)
def delete_notification(request, notification_url):
    notification = get_object_or_404(Notification, url=notification_url)

    if request.method == 'POST':
        notification.delete()
        return redirect('list_noti')  # Chuyển hướng đến trang danh sách thông báo sau khi xóa thành công

    title = "Xóa thông báo"
    return render(request, 'notification/delete.html', {**get_custom_files_notification(),'notification': notification, 'title': title})

@login_required(login_url='login')
@permission_required('backend.view_readrecord', raise_exception=True)
def report_noti(request, notification_url):
    title="Thống kê người xem thông báo"
    notification = get_object_or_404(Notification, url=notification_url)
    
    # Lấy danh sách người đã đọc và chưa đọc thông báo
    read_users = notification.read_by_users.all()
    unread_users = notification.recipients.exclude(id__in=read_users)

    # Tạo một danh sách chứa thông tin về lượt xem và lần đầu xem
    read_records = ReadRecord.objects.filter(notification=notification, user__in=read_users)
    
    # Truy xuất thông tin từ bảng trung gian ReadRecord
    user_read_info = [{'user': record.user,
                       'read_count': record.read_count,
                       'first_read_time': record.first_read_time} for record in read_records]

    return render(request, 'notification/report_noti.html', 
                  {'notification': notification, 'title': title,
                   'user_read_info': user_read_info, 
                   'unread_users': unread_users})

@login_required(login_url='login')
def update_status_noti(request):
    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        status = request.POST.get('status')

        try:
            notification = get_object_or_404(Notification, id=notification_id)
            notification.status = bool(int(status))
            notification.save()

            return JsonResponse({'success': True})
        except Notification.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'department_id not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required(login_url='login')
@permission_required('backend.view_readrecord', raise_exception=True)
def readRecord(request):
    title = "Quản lý lượt xem"
    readrecords = ReadRecord.objects.all()
    context = {'readrecords': readrecords, 'title': title}
    return render(request,'readrecord/index.html', context)


#=============================== Quản lý chức vụ ========================================
@login_required(login_url='login')
@permission_required('backend.view_position', raise_exception=True)
def position(request):
    title = "Quản lý chức vụ"
    positions = Position.objects.all()
    context = {'positions': positions,'title':title}
    return render(request,'account/position/index.html', context)

@login_required(login_url='login')
@permission_required('backend.add_position', raise_exception=True)
def addPosition(request):
    title = "Thêm chức vụ"
    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            position = form.save(commit=False)
            position.status = True
            form.save()
            return redirect('position')  # Redirect to a page where you list all positions
    else:
        form = PositionForm()

    context = {'form': form,'title':title}
    return render(request, 'account/position/add.html', context)

@login_required(login_url='login')
@permission_required('backend.change_position', raise_exception=True)
def editPosition(request, position_id):
    position = get_object_or_404(Position, pk=position_id)
    title = "Chỉnh sửa chức vụ"

    if request.method == 'POST':
        # Xử lý dữ liệu khi form được submit
        position.position_name = request.POST.get('position_name')
        position.description = request.POST.get('description')
        position.save()

        # Chuyển hướng hoặc hiển thị thông báo thành công
        return redirect('position')

    else:
        # Hiển thị form để chỉnh sửa dữ liệu hiện tại
        context = {'position': position,'title':title}
        return render(request, 'account/position/edit.html', context)
    
@login_required(login_url='login')
def update_status(request):
    if request.method == 'POST':
        position_id = request.POST.get('position_id')
        status = request.POST.get('status')

        try:
            position = Position.objects.get(id=position_id)
            position.status = bool(int(status))
            position.save()

            return JsonResponse({'success': True})
        except Position.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Position not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required(login_url='login')
@permission_required('backend.delete_position', raise_exception=True)
def deletePosition(request, position_id):
    position = get_object_or_404(Position, pk=position_id)
    title = "Xóa chức vụ"
    if request.method == 'POST':
        # Xác nhận xóa bằng cách kiểm tra giá trị trong form (có thể thêm một form xác nhận nếu cần)
        # Nếu bạn muốn xác nhận xóa, bạn có thể sử dụng một form và kiểm tra dữ liệu của nó ở đây

        # Xóa bản ghi
        position.delete()

        # Chuyển hướng hoặc hiển thị thông báo thành công
        return redirect('position')

    # Hiển thị trang xác nhận xóa
    context = {'position': position,'title':title}
    return render(request, 'account/position/delete.html', context)


#=============================== Quản lý loại người dùng ========================================

@login_required(login_url='login')
def user_category(request):
    user_categorys = UserCategory.objects.all()
    context = {'user_categorys': user_categorys}
    return render(request,'account/usercategory/index.html', context)

@login_required(login_url='login')
def add_user_category(request):
    if request.method == 'POST':
        form = UserCategoryForm(request.POST)
        if form.is_valid():
            user_category = form.save(commit=False)
            user_category.status = True
            form.save()
            return redirect('user_category')  # Redirect to a page where you list all positions
    else:
        form = PositionForm()

    context = {'form': form}
    return render(request, 'account/usercategory/add.html', context)

@login_required(login_url='login')
def edit_user_category(request, user_category_id):
    user_categorys = get_object_or_404(UserCategory, pk=user_category_id)

    if request.method == 'POST':
        # Xử lý dữ liệu khi form được submit
        user_categorys.user_category_name = request.POST.get('user_category_name')
        user_categorys.description = request.POST.get('description')
        user_categorys.save()

        # Chuyển hướng hoặc hiển thị thông báo thành công
        return redirect('user_category')

    else:
        # Hiển thị form để chỉnh sửa dữ liệu hiện tại
        context = {'user_categorys': user_categorys}
        return render(request, 'account/usercategory/edit.html', context)
    
@login_required(login_url='login')
def update_status_user_category(request):
    if request.method == 'POST':
        user_category_id = request.POST.get('user_category_id')
        status = request.POST.get('status')

        try:
            usercategory = get_object_or_404(UserCategory, id=user_category_id)
            usercategory.status = bool(int(status))
            usercategory.save()

            return JsonResponse({'success': True})
        except UserCategory.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'user_category_id not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required(login_url='login')
def delete_user_category(request, user_category_id):
    usercategorys = get_object_or_404(UserCategory, pk=user_category_id)

    if request.method == 'POST':
        # Xác nhận xóa bằng cách kiểm tra giá trị trong form (có thể thêm một form xác nhận nếu cần)
        # Nếu bạn muốn xác nhận xóa, bạn có thể sử dụng một form và kiểm tra dữ liệu của nó ở đây

        # Xóa bản ghi
        usercategorys.delete()

        # Chuyển hướng hoặc hiển thị thông báo thành công
        return redirect('user_category')

    # Hiển thị trang xác nhận xóa
    context = {'usercategorys': usercategorys}
    return render(request, 'account/usercategory/delete.html', context)


#=============================== Quản lý phòng ban========================================
@login_required(login_url='login')
@permission_required('backend.view_department', raise_exception=True)
def department(request):
    title = "Quản lý phòng ban"
    departments = Department.objects.all()
    context = {'departments': departments,'title':title}
    return render(request,'account/department/index.html', context)


@login_required(login_url='login')
@permission_required('backend.add_department', raise_exception=True)
def add_department(request):
    title = "Thêm phòng ban"
    users = User.objects.all()
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            user_category = form.save(commit=False)
            user_category.status = True
            form.save()
            return redirect('department')  # Redirect to a page where you list all positions
    else:
        form = DepartmentForm()

    context = {'form': form, 'users':users,'title':title}
    return render(request, 'account/department/add.html', context)


@login_required(login_url='login')
@permission_required('backend.change_department', raise_exception=True)
def edit_department(request, department_id):
    title = "Chỉnh sửa thông tin phòng ban"
    department = get_object_or_404(Department, pk=department_id)
    users = User.objects.all()
    if request.method == 'POST':
        # Xử lý dữ liệu khi form được submit
        selected_user_id = request.POST.get('head_of_department')
        selected_user = get_object_or_404(User, pk=selected_user_id)
        
        department.department_name = request.POST.get('department_name')
        department.description = request.POST.get('description')
        department.head_of_department = selected_user
        department.address = request.POST.get('address')
        department.save()

        # Chuyển hướng hoặc hiển thị thông báo thành công
        return redirect('department')

    else:
        # Hiển thị form để chỉnh sửa dữ liệu hiện tại
        context = {'department': department, 'users':users,'title':title}
        return render(request, 'account/department/edit.html', context)


@login_required(login_url='login')
@permission_required('backend.change_department', raise_exception=True)
def update_status_department(request):
    if request.method == 'POST':
        department_id = request.POST.get('department_id')
        status = request.POST.get('status')

        try:
            usercategory = get_object_or_404(Department, id=department_id)
            usercategory.status = bool(int(status))
            usercategory.save()

            return JsonResponse({'success': True})
        except Department.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'department_id not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required(login_url='login')
@permission_required('backend.delete_department', raise_exception=True)
def delete_department(request, department_id):
    title = "Xóa phòng ban"
    department = get_object_or_404(Department, pk=department_id)
    users = User.objects.all()
    if request.method == 'POST':
        # Xóa bản ghi
        department.delete()

        # Chuyển hướng hoặc hiển thị thông báo thành công
        return redirect('department')

    # Hiển thị trang xác nhận xóa
    context = {'department': department, 'users':users,'title':title}
    return render(request, 'account/department/delete.html', context)


#=============================== Quản lý người dùng ========================================

def get_custom_files_duallistbox():
    css_files = ['plugins/dualListbox/bootstrap-duallistbox.min.css']
    js_files = ['plugins/dualListbox/jquery.bootstrap-duallistbox.js']
    custom_script = "$('.dual_select').bootstrapDualListbox({selectorMinimalHeight: 160});"
    return {'custom_css': css_files, 'custom_js': js_files,'custom_script': custom_script}


@login_required(login_url='login')
@permission_required('auth.add_user', raise_exception=True)
def add_user(request):
    title = "Thêm thành viên"
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            try:
                add_user = form.save(commit=False)
                add_user.password = make_password(add_user.password)
                add_user.save()
                Account.objects.create(user=add_user)
                form.save()
                messages.success(request,"Thêm thành công")
                return redirect('user')
            except Exception as e:
                messages.error(request,f"Có lỗi xảy ra khi lưu: {e}")
                print(f"Có lỗi xảy ra khi lưu: {e}")
                form.add_error(None, f"Có lỗi xảy ra khi lưu: {e}")
        else:
            print(f"Form không hợp lệ: {form.errors}")
    else:
        form = UserForm()
    return render(request, 'account/user/add.html', {**get_custom_files_duallistbox(),'form': form, 'title': title})

@login_required(login_url='login')
@permission_required('auth.view_user', raise_exception=True)
def user(request):
    title = "Quản lý thành viên"
    users = User.objects.select_related('account').all()
    context = {'users': users, 'title': title}
    return render(request, 'account/user/index.html', context)

@login_required(login_url='login')
@permission_required('auth.change_user', raise_exception=True)
def update_status_user(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        is_active = request.POST.get('is_active')
        print('===========================', id)
        try:
            user = User.objects.get(id=id)
            user.is_active = bool(int(is_active))
            user.save()

            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'DocumentType not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required(login_url='login')
@permission_required('auth.change_user', raise_exception=True)
def edit_user(request, id):
    user = get_object_or_404(User, id=id)
    title = "Chỉnh sửa thông tin thành viên"
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            try:
                edited_user = form.save(commit=False)
                # Kiểm tra xem mật khẩu đã thay đổi hay chưa
                if 'password' in form.changed_data:
                    # Mã hóa mật khẩu mới trước khi lưu
                    edited_user.password = make_password(edited_user.password)
                edited_user.save()
                form.save_m2m()
                messages.success(request,"Chỉnh sửa thành công")
                return redirect('user')
            except Exception as e:
                print(f"Có lỗi xảy ra khi lưu: {e}")
                form.add_error(None, f"Có lỗi xảy ra khi lưu: {e}")
        else:
            print(f"Form không hợp lệ: {form.errors}")
    else:
        form = UserForm(instance=user)
    return render(request, 'account/user/edit.html', {**get_custom_files_duallistbox(),'form': form, 'user': user, 'title': title})

@login_required(login_url='login')
@permission_required('auth.delete_user', raise_exception=True)
def delete_user(request, id):
    user = get_object_or_404(User, id=id)
    title = "Xóa thành viên"
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            try:
                user.delete()
                messages.success(request,"Xóa thành công")
                return redirect('user')
            except Exception as e:
                messages.error(request,f"Có lỗi xảy ra khi lưu: {e}")
                print(f"Có lỗi xảy ra khi lưu: {e}")
                form.add_error(None, f"Có lỗi xảy ra khi lưu: {e}")
        else:
            print(f"Form không hợp lệ: {form.errors}")
    else:
        form = UserForm(instance=user)
    return render(request, 'account/user/delete.html', {**get_custom_files_duallistbox(),'form': form, 'user': user, 'title': title})

@login_required(login_url='login')
def user_update(request, id):
    user = get_object_or_404(User, id=id)
    title = "Chỉnh sửa thông tin thành viên"
    if request.method == 'POST':
        form = UserChangeForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            try:
                edited_user = form.save(commit=False)
                edited_user.save()
                form.save_m2m()
                return redirect('user')
            except Exception as e:
                print(f"Có lỗi xảy ra khi lưu: {e}")
                form.add_error(None, f"Có lỗi xảy ra khi lưu: {e}")
        else:
            print(f"Form không hợp lệ: {form.errors}")
    else:
        form = UserChangeForm(instance=user)
    return render(request, 'account/user/edit.html', {'form': form, 'user': user, 'title': title})


@login_required(login_url='login')
def update_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']

        # Lấy đường dẫn ảnh cũ nếu có
        old_image_path = None
        if request.user.account.image:
            old_image_path = request.user.account.image.path
        
        # Lưu ảnh mới vào hệ thống
        request.user.account.image = image
        request.user.account.save()
        
        # Kiểm tra và xóa ảnh cũ nếu tồn tại
        if old_image_path and os.path.exists(old_image_path):
            os.remove(old_image_path)

        return JsonResponse({'status': 'success', 'message': 'Image updated successfully.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request.'})
    

@login_required(login_url='login')
def profile(request, encoded_id):
    # Decode the custom-encoded ID
    try:
        decoded_id = base64.b64decode(encoded_id.replace('x', '=')).decode('utf-8')
    except Exception as e:
        raise Http404("Invalid encoded ID")
    
    # Retrieve the user based on the decoded ID
    user = get_object_or_404(User, id=decoded_id)
    title = "Profile"
    
    # Kiểm tra xem người dùng hiện tại có phải là chủ sở hữu của trang profile không
    is_owner = request.user == user
    
    if request.method == 'POST':
        form = EditAccountForm(request.POST, request.FILES, instance=user.account)
        files = request.FILES.getlist('citizen_id_images')
    
        if form.is_valid():
            try:
                edited_user = form.save(commit=False)
                edited_user.user.email = form.cleaned_data['email']
                edited_user.user.first_name = form.cleaned_data['first_name']
                edited_user.user.last_name = form.cleaned_data['last_name']
                edited_user.user.save()
                edited_user.save()
                form.save_m2m()
                # Thêm ảnh mới vào danh sách và thư mục
                for file in files:
                    upload_file = CitizenIDImage(image=file)
                    upload_file.save()
                    edited_user.citizen_id_images.add(upload_file)
                edited_user.save()  # Lưu một lần nữa để cập nhật thông tin mới
                messages.success(request,"Update Thành Công!")
                return redirect('profile', encoded_id=encoded_id)
            except Exception as e:
                print(f"Có lỗi xảy ra khi lưu: {e}")
                messages.error(request,f"Có lỗi xảy ra khi lưu: {e}")
                form.add_error(None, f"Có lỗi xảy ra khi lưu: {e}")
        else:
            messages.error(request,f"Có lỗi xảy ra: {form.errors}")
            print(f"Form không hợp lệ: {form.errors}")
    else:
        form = EditAccountForm(instance=user.account, initial={'email': user.email, 'first_name': user.first_name, 'last_name': user.last_name})
      
    js_cnd_file = 'https://cdnjs.cloudflare.com/ajax/libs/js-cookie/3.0.1/js.cookie.min.js'
    
    return render(request, 'account/user/profile.html', {'encoded_id': encoded_id,'form': form, 'is_owner': is_owner, 
                                                         'user': user, 'title': title,'js_cnd_file':js_cnd_file})

# ===============User group ====================
@login_required(login_url='login')
@permission_required('auth.add_group', raise_exception=True)
def add_group(request):
    title = "Thêm loại thành viên"
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('group')  # Redirect to a page where you list all positions
    else:
        form = GroupForm()

    context = {**get_custom_files_duallistbox(),'form': form, 'title':title}
    return render(request, 'account/group/add.html', context)


@login_required(login_url='login')
@permission_required('auth.view_group', raise_exception=True)
def group(request):
    title = "Quản lý loại thành viên"
    groups = Group.objects.all()
    # Thêm số lượng thành viên cho mỗi nhóm vào mỗi đối tượng Group
    for group in groups:
        group.member_count = group.user_set.count()
    context = {'groups': groups, 'title': title}
    return render(request, 'account/group/index.html', context)

@login_required(login_url='login')
@permission_required('auth.change_group', raise_exception=True)
def edit_group(request, id):
    group = get_object_or_404(Group, id=id)
    title = "Chỉnh sửa loại thành viên"
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            try:
                edited_group = form.save(commit=False)
                edited_group.save()
                form.save_m2m()
                messages.success(request,"Chỉnh sửa thành công")
                return redirect('group')
            except Exception as e:
                print(f"Có lỗi xảy ra khi lưu: {e}")
                form.add_error(None, f"Có lỗi xảy ra khi lưu: {e}")
        else:
            print(f"Form không hợp lệ: {form.errors}")
    else:
        form = GroupForm(instance=group)
    return render(request, 'account/group/edit.html', {**get_custom_files_duallistbox(),'form': form, 'group': group, 'title': title})

@login_required(login_url='login')
@permission_required('auth.delete_group', raise_exception=True)
def delete_group(request, id):
    group = get_object_or_404(Group, id=id)
    title = "Xóa loại thành viên"
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            try:
                group.delete()
                messages.success(request,"Xóa thành công")
                return redirect('group')
            except Exception as e:
                messages.error(request,f"Có lỗi xảy ra khi lưu: {e}")
                print(f"Có lỗi xảy ra khi lưu: {e}")
                form.add_error(None, f"Có lỗi xảy ra khi lưu: {e}")
        else:
            print(f"Form không hợp lệ: {form.errors}")
    else:
        form = GroupForm(instance=group)
    return render(request, 'account/group/delete.html', {**get_custom_files_duallistbox(),'form': form, 'group': group, 'title': title})

def custom_permission_denied(request, exception):
    print("================ikwvniks gi seg")
    return render(request, 'error_page/403_page.html', status=403)