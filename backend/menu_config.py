# menu_config.py
from django import template

register = template.Library()

MENU_CONFIG = [
    {
        'title': 'QL Nhóm Thành Viên',
        'icon': 'fa fa-th-large',
        'name': 'user',
        'url': '/user',  # Thay đổi thành đường dẫn phản ánh menu chính
        'submenu': [
            {'title': 'QL Thành Viên', 'url': '/user_account'},
            {'title': 'QL Loại Thành Viên', 'url': '/user_group'},
            {'title': 'QL Phòng Ban', 'url': '/user_department'},
            {'title': 'QL Chức Vụ', 'url': '/user_position'},
        ]
    },
    {
        'title': 'QL Thông Báo',
        'icon': 'fa fa-bell',
        'name': 'notify',
        'url': '/notify',  # Thay đổi thành đường dẫn phản ánh menu chính
        'submenu': [
            {'title': 'QL Thông Báo', 'url': '/notify_notification'},
            {'title': 'QL Lượt Xem', 'url': '/notify_readrecord'},
        ]
    },
    {
        'title': 'QL Văn bản',
        'icon': 'fa fa-file-text',
        'name': 'docu',
        'url': '/docu',  # Thay đổi thành đường dẫn phản ánh menu chính
        'submenu': [
            {'title': 'QL Văn Bản Mẫu', 'url': '/docu_tem'},
            {'title': 'QL Văn Bản Đến', 'url': '/docu_income'},
            {'title': 'QL Văn Bản Đi', 'url': '/docu_outgoing'},
            {'title': 'QL Loại Văn Bản', 'url': '/docu_cate'},
            {'title': 'QL Mức Độ Văn Bản', 'url': '/docu_level'},
            {'title': 'QL Trạng Thái Xử Lý', 'url': '/docu_status'},
        ]
    },
    {
        'title': 'QL Công việc',
        'icon': 'fa fa-area-chart',
        'name': 'work_',
        'url': '/work_', 
        'submenu': [
            {'title': 'QL Lịch Công Tác', 'url': '/work_schedule'},
            {'title': 'QL Tuần Công Tác', 'url': '/work_week'},
            {'title': 'QL Tiến Trình Công Việc', 'url': '/work_task'},
        ]
    },
    {
        'title': 'QL Phản Hồi',
        'icon': 'fa fa-file-archive-o',
        'name': 'list',
        'url': '/list',  # Thay đổi thành đường dẫn phản ánh menu chính
        'submenu': [
            {'title': 'QL Bình Luận', 'url': '/list_comment'},
            {'title': 'QL File Văn Bản', 'url': '/notification'},
            {'title': 'QL Hình Ảnh', 'url': '/readrecord'},
        ]
    },    
]


MENU_CONFIG_2 = [
    {
        'title': 'Thông Báo',
        'icon': 'fa fa-bell',
        'name': 'notify',
        'url': '/list_notification', 
    },
    {
        'title': 'Công việc',
        'icon': 'fa fa-area-chart',
        'name': 'work_',
        'url': '/list_task',     
    },
]