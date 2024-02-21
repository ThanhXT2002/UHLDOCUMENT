from django import forms
from .models import *
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from ckeditor.widgets import CKEditorWidget
from django.contrib.auth.forms import UserChangeForm
from .models import Account
from django.contrib.auth.models import User,Group, Permission
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from validate_email import validate_email


def is_valid_email(email):
    try:
        is_valid = validate_email(email, verify=True)
        return is_valid
    except Exception as e:
        print(f"An error occurred while validating email: {e}")
        return False
    
class SendEmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']
        
    def __init__(self, *args, **kwargs):
        super(SendEmailForm, self).__init__(*args, **kwargs)   
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not is_valid_email(email):
            raise forms.ValidationError("Email không hợp lệ.")
        return email

class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','email','password','is_active']
        
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)   
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not is_valid_email(email):
            raise forms.ValidationError("Email không hợp lệ.")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email đã tồn tại.")
        return email
        
    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.is_active = False  # Thiết lập trạng thái mặc định là False
        if commit:
            user.save()
        return user

class ImageUpdateForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['image']


class GroupForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        required=False,
        label='Quyền người dùng'
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['permissions'].widget.attrs.update({'class': 'form-control dual_select'})



class UserForm(forms.ModelForm):
    user_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        required=False,
        label='Quyền người dùng'
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label='Nhóm người dùng'
    )
    CHOICES = (
        (False, 'Không hoạt động'),
        (True, 'Hoạt động')
    )
    
    is_superuser = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Superuser'
    )
    
    is_staff = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Staff'
    )
    
    is_active = forms.ChoiceField(
        initial=True,
        choices=CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Active'
    )
    class Meta:
        model = User
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)   
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})
        self.fields['date_joined'].widget.attrs.update({'class': 'form-control','readonly': 'readonly'})
        self.fields['last_login'].widget.attrs.update({'class': 'form-control'})
        self.fields['user_permissions'].widget.attrs.update({'class': 'form-control dual_select'})
        self.fields['groups'].widget.attrs.update({'class': 'form-control dual_select'})


class EditAccountForm(UserChangeForm):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, label='First Name', widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, label='Last Name', widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Account
        fields = ['email', 'first_name', 'last_name', 'date_of_birth', 'gender', 'phone_number', 'image', 'address', 
                  'department_works_at', 'position', 'ethnicity', 'nationality', 'educational_background', 
                  'professional_degree', 'current_company', 'office_phone_number', 'office_address', 'citizen_id', 
                  'citizen_id_issue_date', 'citizen_id_issuing_place', 'link_facebook', 
                  'link_zalo', 'link_instagram']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'department_works_at': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control'}),   
            'ethnicity': forms.Select(attrs={'class': 'form-control select2_demo_1 '}),
            'nationality': forms.Select(attrs={'class': 'form-control select2_demo_1 '}),
            'educational_background': forms.TextInput(attrs={'class': 'form-control'}),
            'professional_degree': forms.TextInput(attrs={'class': 'form-control'}),
            'current_company': forms.TextInput(attrs={'class': 'form-control'}),
            'office_phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'office_address': forms.TextInput(attrs={'class': 'form-control'}),
            'citizen_id': forms.TextInput(attrs={'class': 'form-control'}),
            'citizen_id_issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'citizen_id_issuing_place': forms.TextInput(attrs={'class': 'form-control'}),
            'link_facebook': forms.URLInput(attrs={'class': 'form-control'}),
            'link_zalo': forms.URLInput(attrs={'class': 'form-control'}),
            'link_instagram': forms.URLInput(attrs={'class': 'form-control'}),
        }

        


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['date_of_birth', 'gender', 'phone_number', 'image', 'address', 'department_works_at', 'position',
                    'ethnicity', 'nationality', 'educational_background', 'professional_degree',
                  'current_company', 'office_phone_number', 'office_address', 'citizen_id', 'citizen_id_issue_date',
                  'citizen_id_issuing_place', 'citizen_id_images', 'link_facebook', 'link_zalo', 'link_instagram']

        widgets = {
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'address': forms.Textarea(attrs={'class': 'form-control'}),
            'department_works_at': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
            
            'ethnicity': forms.Select(attrs={'class': 'form-control'}),
            'nationality': forms.Select(attrs={'class': 'form-control'}),
            'educational_background': forms.TextInput(attrs={'class': 'form-control'}),
            'professional_degree': forms.TextInput(attrs={'class': 'form-control'}),
            'current_company': forms.TextInput(attrs={'class': 'form-control'}),
            'office_phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'office_address': forms.Textarea(attrs={'class': 'form-control'}),
            'citizen_id': forms.TextInput(attrs={'class': 'form-control'}),
            'citizen_id_issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'citizen_id_issuing_place': forms.TextInput(attrs={'class': 'form-control'}),
            'citizen_id_images': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'link_facebook': forms.URLInput(attrs={'class': 'form-control'}),
            'link_zalo': forms.URLInput(attrs={'class': 'form-control'}),
            'link_instagram': forms.URLInput(attrs={'class': 'form-control'}),
        }


class CommentForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea)

class EditTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description','image', 'start_date','end_date','taskfiles','confirmed_users',
                  'uploadfile','assigned_users','priority','status','creator','sum_progress']
    def __init__(self, *args, **kwargs):
        super(EditTaskForm, self).__init__(*args, **kwargs)   
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control inbox-textarea'})
        self.fields['start_date'].widget.attrs.update({'class': 'form-control'})
        self.fields['end_date'].widget.attrs.update({'class': 'form-control'})
        self.fields['priority'].widget.attrs.update({'class': 'form-control'})
        self.fields['status'].widget.attrs.update({'class': 'form-control'})
        self.fields['taskfiles'].widget.attrs.update({'class': 'form-control'})
        self.fields['uploadfile'].widget.attrs.update({'class': 'form-control'})
        self.fields['assigned_users'].widget.attrs.update({'class': 'form-control dual_select'})
        self.fields['confirmed_users'].widget.attrs.update({'class': 'form-control dual_select'})
        self.fields['start_date'].widget.input_type = 'date'
        self.fields['end_date'].widget.input_type = 'date'
        self.fields['creator'].widget.attrs.update({'class': 'form-control','readonly': 'readonly'})
        self.fields['sum_progress'].widget.attrs.update({'class': 'form-control'})
        
        
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description','image', 'start_date','end_date','assigned_users','priority','status']
    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)   
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control inbox-textarea'})
        self.fields['start_date'].widget.attrs.update({'class': 'form-control'})
        self.fields['end_date'].widget.attrs.update({'class': 'form-control'})
        self.fields['priority'].widget.attrs.update({'class': 'form-control'})
        self.fields['status'].widget.attrs.update({'class': 'form-control'})
        self.fields['assigned_users'].widget.attrs.update({'class': 'form-control dual_select'})
        self.fields['start_date'].widget.input_type = 'date'
        self.fields['end_date'].widget.input_type = 'date'
    
class WeekForm(forms.ModelForm):
    class Meta:
        model = Week
        fields = ['week_number', 'year', 'start_date','end_date','description']
    def __init__(self, *args, **kwargs):
        super(WeekForm, self).__init__(*args, **kwargs)
        self.fields['week_number'].widget.attrs.update({'class': 'form-control'})
        self.fields['year'].widget.attrs.update({'class': 'form-control'})
        self.fields['start_date'].widget.attrs.update({'class': 'form-control'})
        self.fields['end_date'].widget.attrs.update({'class': 'form-control '})
        self.fields['description'].widget.attrs.update({'class': 'form-control inbox-textarea'})
        self.fields['start_date'].widget.input_type = 'date'
        self.fields['end_date'].widget.input_type = 'date'


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['schedule_category', 'week', 'work_date','morning_or_afternoon','start_time', 'end_time', 
                  'location', 'leading_official','participants','preparation',
                  'content', 'description','status','department','user']
    def __init__(self, *args, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)
        # Tạo danh sách tuple (value, label) cho Select widget, đảo ngược thứ tự
        self.fields['week'].widget.choices = [
            (week.pk, str(week)) for week in Week.objects.order_by('-start_date')
        ]
        self.fields['week'].widget.attrs.update({'class': 'form-control select2_demo_1'})
        self.fields['status'].widget.attrs.update({'class': 'form-control'})
        self.fields['schedule_category'].widget.attrs.update({'class': 'form-control'})
        self.fields['morning_or_afternoon'].widget.attrs.update({'class': 'form-control '})
        self.fields['participants'].widget.attrs.update({'class': 'form-control inbox-textarea'})
        self.fields['preparation'].widget.attrs.update({'class': 'form-control inbox-textarea'})
        self.fields['content'].widget.attrs.update({'class': 'form-control inbox-textarea'})
        self.fields['description'].widget.attrs.update({'class': 'form-control inbox-textarea'})
        self.fields['department'].widget.attrs.update({'class': 'form-control dual_select'})
        self.fields['user'].widget.attrs.update({'class': 'form-control dual_select'})
        self.fields['end_time'].widget.attrs.update({'class': 'form-control'})
        self.fields['start_time'].widget.attrs.update({'class': 'form-control'})
        self.fields['location'].widget.attrs.update({'class': 'form-control'})
        self.fields['leading_official'].widget.attrs.update({'class': 'form-control'})
        self.fields['work_date'].widget.attrs.update({'class': 'form-control'})
        self.fields['work_date'].widget.input_type = 'date'



class OutgoingDocuForm(forms.ModelForm):
    class Meta:
        model = OutgoingDocument
        fields = ['document_type', 'level', 'summary','receipt_date','issuance_date', 'current_number', 
                  'arrival_number', 'advisory_opinions','status','reference_number']
    def __init__(self, *args, **kwargs):
        super(OutgoingDocuForm, self).__init__(*args, **kwargs)
        self.fields['level'].widget.attrs.update({'class': 'form-control select2_demo_1'})
        self.fields['level'].empty_label = "-------------------Vui lòng chọn mức độ văn bản------------------"
        self.fields['status'].widget.attrs.update({'class': 'form-control select2_demo_1 '})
        self.fields['status'].empty_label = "------------------Vui lòng chọn trạng thái văn bản--------------"
        self.fields['advisory_opinions'].required = False


class EditOutgoingDocuForm(forms.ModelForm):
    class Meta:
        model = OutgoingDocument
        fields = ['document_type', 'level', 'summary',
                  'receipt_date','issuance_date', 'current_number', 'arrival_number', 
                  'advisory_opinions','status','reference_number', 'uploadfile']
        
        
    def __init__(self, *args, **kwargs):
        super(EditOutgoingDocuForm, self).__init__(*args, **kwargs)
        self.fields['document_type'].widget.attrs.update({'id':'select2','class': 'form-control select2_demo_1 select2-hidden-accessible', 'tabindex':'-1','aria-hidden':'true' })
        self.fields['document_type'].empty_label = "-------------------Vui lòng chọn mức độ văn bản------------------"
        self.fields['level'].widget.attrs.update({'class': 'form-control select2_demo_1'})
        self.fields['level'].empty_label = "-------------------Vui lòng chọn mức độ văn bản------------------"
        self.fields['status'].widget.attrs.update({'class': 'form-control select2_demo_1 '})
        self.fields['status'].empty_label = "------------------Vui lòng chọn trạng thái văn bản--------------"
        self.fields['advisory_opinions'].required = False
        self.fields['uploadfile'].widget.attrs.update({'class': 'form-control select2_demo_1 '})
        
class EditIncomeDocuForm(forms.ModelForm):
    class Meta:
        model = IncomingDocument
        fields = ['issuing_agency','responsible_agency','document_type', 'level', 'summary',
                  'receipt_date','issuance_date', 'current_number', 'arrival_number', 
                  'advisory_opinions','status','reference_number', 'uploadfile']
        
        
    def __init__(self, *args, **kwargs):
        super(EditIncomeDocuForm, self).__init__(*args, **kwargs)
        self.fields['document_type'].widget.attrs.update({'id':'select2','class': 'form-control select2_demo_1 select2-hidden-accessible', 'tabindex':'-1','aria-hidden':'true' })
        self.fields['document_type'].empty_label = "-------------------Vui lòng chọn mức độ văn bản------------------"
        
        self.fields['level'].widget.attrs.update({'class': 'form-control select2_demo_1'})
        self.fields['level'].empty_label = "-------------------Vui lòng chọn mức độ văn bản------------------"
        self.fields['status'].widget.attrs.update({'class': 'form-control select2_demo_1 '})
        self.fields['status'].empty_label = "------------------Vui lòng chọn trạng thái văn bản--------------"
        self.fields['advisory_opinions'].required = False
        self.fields['responsible_agency'].required = False
        self.fields['uploadfile'].widget.attrs.update({'class': 'form-control select2_demo_1 '})
        
class IncomeDocuForm(forms.ModelForm):
    class Meta:
        model = IncomingDocument
        fields = ['issuing_agency','responsible_agency','document_type', 'level', 'summary',
                  'receipt_date','issuance_date', 'current_number', 'arrival_number', 
                  'advisory_opinions','status','reference_number']
    def __init__(self, *args, **kwargs):
        super(IncomeDocuForm, self).__init__(*args, **kwargs)
        self.fields['level'].widget.attrs.update({'class': 'form-control select2_demo_1'})
        self.fields['level'].empty_label = "-------------------Vui lòng chọn mức độ văn bản------------------"
        self.fields['status'].widget.attrs.update({'class': 'form-control select2_demo_1 '})
        self.fields['status'].empty_label = "------------------Vui lòng chọn trạng thái văn bản--------------"
        self.fields['advisory_opinions'].required = False
        self.fields['responsible_agency'].required = False
        self.fields['document_type'].widget.attrs.update({
            'class': 'form-control select2_demo_1',
            'id': 'select2',  # Đặt ID theo ý muốn của bạn
        })
        self.fields['document_type'].empty_label = "----------------------------- Chọn loại văn bản --------------------------"
        
class TemplateDocuForm(forms.ModelForm):
    class Meta:
        model = TemplateDocument
        fields = ['document_type', 'level', 'summary', 'origin', 'number', 'publication_date', 'uploadfile', 'description']
    
    def __init__(self, *args, **kwargs):
        super(TemplateDocuForm, self).__init__(*args, **kwargs)
        self.fields['document_type'].widget.attrs.update({'class': 'form-control select2_demo_1'})
        self.fields['document_type'].empty_label = "------------------Vui lòng chọn loại văn bản--------------------"
        self.fields['level'].widget.attrs.update({'class': 'form-control select2_demo_1'})
        self.fields['level'].empty_label = "---------------Vui lòng chọn mức độ văn bản--------------------"
        self.fields['uploadfile'].widget.attrs.update({'class': 'form-control file-upload'})
        self.fields['origin'].widget.attrs.update({'class': 'form-control file-upload', 'value': 'request.POST.origin'})
        self.fields['uploadfile'].required = False
        
class ProcessStatusForm(forms.ModelForm):
    class Meta:
        model = ProcessStatus
        fields = ['name', 'description']
        
class DocumentLevelForm(forms.ModelForm):
    class Meta:
        model = DocumentLevel
        fields = ['name', 'description']
        
class DocumentTypeForm(forms.ModelForm):
    class Meta:
        model = DocumentType
        fields = ['document_name', 'description', 'status']
        
class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['position_name', 'description', 'status']
        
class UserCategoryForm(forms.ModelForm):
    class Meta:
        model = UserCategory
        fields = ['user_category_name', 'description', 'status']
         
            
                
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['head_of_department', 'department_name', 'description','description','address', 'status']
        
        
class NotificationForm(forms.ModelForm):
    recipients = forms.ModelMultipleChoiceField(queryset=User.objects.all(), required=False)
    class Meta:
        model = Notification
        fields = ['title', 'content', 'url', 'start_date', 'end_date', 'recipients', 'uploadfile']
        
    def __init__(self, *args, **kwargs):
        super(NotificationForm, self).__init__(*args, **kwargs)
         # Sử dụng CKEditorWidget cho trường 'content'
        self.fields['content'].widget = CKEditorWidget(config_name='default')
        # Điều chỉnh hiển thị cho trường 'start_date' và 'end_date' nếu bạn muốn
        self.fields['start_date'].widget.attrs.update({'class': 'datepicker'})
        self.fields['end_date'].widget.attrs.update({'class': 'datepicker'})
        self.fields['uploadfile'].widget.attrs.update({'class': 'form-control file-upload dual_select'})
        self.fields['recipients'].widget.attrs.update({'class': 'form-control dual_select' })
        self.fields['uploadfile'].required = False
        
       # Lấy danh sách các đối tượng User bạn muốn hiển thị ban đầu
        initial_recipients = User.objects.filter(is_active=True)
        
        # Đặt giá trị initial cho trường recipients
        self.fields['recipients'].initial = initial_recipients
        
class AddNotificationForm(forms.ModelForm):
    recipients = forms.ModelMultipleChoiceField(queryset=User.objects.all(), widget=forms.SelectMultiple(attrs={'class': 'form-control'}), required=False)
    class Meta:
        model = Notification
        fields = ['title', 'content', 'url', 'start_date', 'end_date', 'recipients', ]
        
    def __init__(self, *args, **kwargs):
        super(AddNotificationForm, self).__init__(*args, **kwargs)
         # Sử dụng CKEditorWidget cho trường 'content'
        self.fields['content'].widget = CKEditorWidget(config_name='default')
        # Điều chỉnh hiển thị cho trường 'start_date' và 'end_date' nếu bạn muốn
        self.fields['start_date'].widget.attrs.update({'class': 'datepicker'})
        self.fields['end_date'].widget.attrs.update({'class': 'datepicker'})
        self.fields['recipients'].widget.attrs.update({'class': 'form-control dual_select' }) 
       # Lấy danh sách các đối tượng User bạn muốn hiển thị ban đầu
        initial_recipients = User.objects.filter(is_active=True)
        
        # Đặt giá trị initial cho trường recipients
        self.fields['recipients'].initial = initial_recipients
        
       