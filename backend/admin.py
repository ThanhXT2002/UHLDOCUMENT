from django.contrib import admin
from backend.models import *
from django.contrib.auth.models import User, Permission
from django.contrib.auth.admin import UserAdmin
from datetime import datetime


class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'codename', 'content_type')
    search_fields = ('name', 'codename', 'content_type__app_label')
admin.site.register(Permission, PermissionAdmin)


class AdminDocumentLevel(admin.ModelAdmin):
    list_display=('name','description')
    
admin.site.register(DocumentLevel, AdminDocumentLevel)


class AccountInline(admin.StackedInline):
    model = Account
    can_delete = False
    verbose_name_plural = 'Accounts'
 
 
class CustomizeUserAdmin(UserAdmin):
    inlines = (AccountInline, )   
      
admin.site.unregister(User)
admin.site.register(User, CustomizeUserAdmin)

class AdminDepartment(admin.ModelAdmin):
    list_display=('head_of_department','department_name','status','address','description')
    list_editable = ('status',)
    
admin.site.register(Department, AdminDepartment)

class AdminAccount(admin.ModelAdmin):
    list_display=('user','phone_number','address')
admin.site.register(Account, AdminAccount)


class AdminReadRecord(admin.ModelAdmin):
    list_display=('user','notification','read_count', 'first_read_time')
admin.site.register(ReadRecord, AdminReadRecord)

class AdminNotification(admin.ModelAdmin):
    list_display=('title','start_date','end_date', 'status')
    list_editable = ('status',)

admin.site.register(Notification, AdminNotification)

class AdminDocumentType(admin.ModelAdmin):
    list_display=('document_name','description','status')
    list_editable = ('status',)
admin.site.register(DocumentType, AdminDocumentType)

admin.site.register(TemplateDocument)
admin.site.register(IncomingDocument)
admin.site.register(OutgoingDocument)
admin.site.register(Task)
admin.site.register(uploadFile)
admin.site.register(Schedule)
admin.site.register(Week)
admin.site.register(Position)
admin.site.register(uploadFileTask)
admin.site.register(CatagoryNotification)
admin.site.register(Comment)

class CitizenIDImageAdmin(admin.ModelAdmin):
    list_display = ('display_image', '__str__')

admin.site.register(CitizenIDImage, CitizenIDImageAdmin)

class AdminProcessStatus(admin.ModelAdmin):
    list_display=('name','description')
admin.site.register(ProcessStatus, AdminProcessStatus)


