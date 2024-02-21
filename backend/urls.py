from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from ckeditor_uploader import views as ckeditor_views

urlpatterns = [
   path('login/', views.login, name='login'),
   path('register/', views.register, name='register'),
   path('send_email/', views.send_email, name='send_email'),
   path('otp_auth/', views.otp_auth, name='otp_auth'),
   path('reset_password/', views.reset_password, name='reset_password'),
   path('logout/', views.logout, name='logout'),
   path('dashboard/', views.dashboard, name='dashboard'),
   path('list_task/', views.view_task_list, name='list_task'),
   path('list_notification/', views.view_notification_list, name='list_notification'),
   path('', views.home, name='home'),
   
   path('user_position/add/', views.addPosition, name='add_position'),
   path('user_position/edit/<int:position_id>/', views.editPosition, name='edit_position'),
   path('user_position/delete/<int:position_id>/', views.deletePosition, name='delete_position'),
   path('user_position/', views.position, name='position'),
   path('update_status/', views.update_status, name='update_status'),
   
   path('user_category/add/', views.add_user_category, name='add_user_category'),
   path('user_category/edit/<int:user_category_id>/', views.edit_user_category, name='edit_user_category'),
   path('user_category/delete/<int:user_category_id>/', views.delete_user_category, name='delete_user_category'),
   path('user_category/', views.user_category, name='user_category'),
   path('update_status_user_category/', views.update_status_user_category, name='update_status_user_category'),
   
   path('user_department/add/', views.add_department, name='add_department'),
   path('user_department/edit/<int:department_id>/', views.edit_department, name='edit_department'),
   path('user_department/delete/<int:department_id>/', views.delete_department, name='delete_department'),
   path('user_department/', views.department, name='department'),
   path('update_status_department/', views.update_status_department, name='update_status_department'),
   
   path('user_account/add/', views.add_user, name='add_user'),
   path('user_account/edit/<int:id>/', views.edit_user, name='edit_user'),
   path('user_account/update/<int:id>/', views.user_update, name='user_update'),
   path('user_account/delete/<int:id>/', views.delete_user, name='delete_user'),
   path('user_account/', views.user, name='user'),
   path('update_status_user/', views.update_status_user, name='update_status_user'),
   path('update_status_noti/', views.update_status_noti, name='update_status_noti'),
   # path('profile/<int:id>/', views.profile, name='profile'),
   path('profile/<str:encoded_id>/', views.profile, name='profile'),
   path('update_image/', views.update_image, name='update_image'),
   
   path('user_group/add/', views.add_group, name='add_group'),
   path('user_group/edit/<int:id>/', views.edit_group, name='edit_group'),
   path('user_group/delete/<int:id>/', views.delete_group, name='delete_group'),
   path('user_group/', views.group, name='group'),
   
   path('notify_notification/', views.list_noti, name='list_noti'),
   path('notification/<str:notification_url>/', views.notification, name='notification'),
   path('notify_notification/report/<str:notification_url>/', views.report_noti, name='report_noti'),
   path('notify_notification/add', views.add_notification, name='add_notification'),
   path('notify_notification/delete/<str:notification_url>', views.delete_notification, name='delete_notification'),
   path('notify_notification/edit/<str:notification_url>/', views.edit_notification, name='edit_notification'),
    
   path('notify_readrecord/', views.readRecord, name='readrecord'),
   path('ckeditor/upload/', ckeditor_views.upload, name='ckeditor_upload'),
   path('ckeditor/browse/', ckeditor_views.browse, name='ckeditor_browse'),
   
   path('docu_cate/', views.docu_cate, name='docu_cate'),
   path('docu_cate/add/', views.add_docu_cate, name='add_docu_cate'),
   path('docu_cate/edit/<int:docu_cate_id>/', views.edit_docu_cate, name='edit_docu_cate'),
   path('docu_cate/delete/<int:docu_cate_id>/', views.delete_docu_cate, name='delete_docu_cate'),
   path('update_status_docu_cate/', views.update_status_docu_cate, name='update_status_docu_cate'),
   
   path('docu_level/', views.docu_level, name='docu_level'),
   path('docu_level/add/', views.add_docu_level, name='add_docu_level'),
   path('docu_level/edit/<int:id>/', views.edit_docu_level, name='edit_docu_level'),
   path('docu_level/delete/<int:id>/', views.delete_docu_level, name='delete_docu_level'),
   
   path('docu_tem/', views.tem_docu, name='tem_docu'),
   path('update_status_tem_docu/', views.update_status_tem_docu, name='update_status_tem_docu'),
  
   path('docu_tem/add/', views.add_tem_docu, name='add_tem_docu'),
   path('docu_tem/edit/<int:id>/', views.edit_tem_docu, name='edit_tem_docu'),
   path('docu_tem/delete/<int:id>/', views.delete_tem_docu, name='delete_tem_docu'),
   
   path('upload_file_view/', views.upload_file_view, name='upload_file_view'),
   
   path('docu_status/', views.docu_status, name='docu_status'),
   path('docu_status/add/', views.add_docu_status, name='add_docu_status'),
   path('docu_status/edit/<int:id>/', views.edit_docu_status, name='edit_docu_status'),
   path('docu_status/delete/<int:id>/', views.delete_docu_status, name='delete_docu_status'),
   
   path('docu_income/', views.income_docu, name='income_docu'),
   path('docu_income/add/', views.add_income_docu, name='add_income_docu'),
   path('docu_income/edit/<int:id>/', views.edit_income_docu, name='edit_income_docu'),
   path('docu_income/delete/<int:id>/', views.delete_income_docu, name='delete_income_docu'),
   
   path('update_status_income_docu/', views.update_status_income_docu, name='update_status_income_docu'),
   
   path('docu_outgoing/', views.outgoing_docu, name='outgoing_docu'),
   path('docu_outgoing/add/', views.add_outgoing_docu, name='add_outgoing_docu'),
   path('docu_outgoing/edit/<int:id>/', views.edit_outgoing_docu, name='edit_outgoing_docu'),
   path('docu_outgoing/delete/<int:id>/', views.delete_outgoing_docu, name='delete_outgoing_docu'),
   path('update_status_outgoing_docu/', views.update_status_outgoing_docu, name='update_status_outgoing_docu'),
   
   
   path('work_schedule/', views.schedule, name='schedule'),
   path('work_schedule/add/', views.add_schedule, name='add_schedule'),
   path('work_schedule/edit/<int:id>/', views.edit_schedule, name='edit_schedule'),
   path('work_delete_schedule/delete/<int:id>/', views.delete_schedule, name='delete_schedule'),
   
   path('work_week/add', views.add_week, name='add_week'),
   path('work_week/create', views.create_week, name='create_week'),
   path('work_week/', views.week, name='week'),
   path('work_week/edit/<int:id>/', views.edit_week, name='edit_week'),
   path('work_week/delete/<int:id>/', views.delete_week, name='delete_week'),
   path('work_search/', views.search_schedule, name='search_schedule'),
   
   #công việc
   path('work_task/', views.task, name='task'),
   path('work_task/add', views.add_task, name='add_task'),
   path('task_detail/<str:task_url>/', views.task_detail, name='task_detail'),
   path('confirm_task_participation/<int:task_id>/', views.confirm_task_participation, name='confirm_task_participation'),
   path('task_detail/<str:task_url>/', views.task_detail, name='task_detail'),
   
   path('work_task/edit/<str:task_url>/', views.edit_task, name='edit_task'),
   path('work_task/delete/<str:task_url>/', views.delete_task, name='delete_task'),
   
   
   path('toggle_like/<int:comment_id>/', views.toggle_like, name='toggle_like'),
   path('add_reply/<int:comment_id>/', views.add_reply, name='add_reply'),
   path('delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
   path('edit_comment/<int:comment_id>/', views.edit_comment, name='edit_comment'),
   path('list_comment/', views.comment, name='comment'),
   path('update_status_comment/', views.update_status_comment, name='update_status_comment'),
   path('comment/delete/<int:comment_id>/', views.delete_comment2, name='delete_comment2'),
   
   
   
   path('handle_comment/<slug:notification_url>/', views.handle_comment, name='handle_comment'),
]+static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT )