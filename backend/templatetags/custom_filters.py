from django import template
import base64
from datetime import datetime

register = template.Library()

@register.filter(name='base64_encode')
def base64_encode(value, length=8):
    value_bytes = str(value).encode('utf-8')
    encoded = base64.urlsafe_b64encode(value_bytes).rstrip(b'=').decode('utf-8')
    
    # Replace padding character '=' with 'x'
    encoded = encoded.replace('=', 'x')

    # Truncate or pad the string to the specified length
    encoded = encoded[:length].ljust(length, 'x')

    return encoded

@register.filter(name='get_item')
def get_item(value, arg):
    return value[arg]

@register.filter
def custom_date_format(value):
    if value:
        day_of_week = value.strftime("%A")
        day_of_month = value.strftime("%d")
        month = value.strftime("%m")
        year = value.strftime("%Y")
        day_mapping = {
            'Monday': 'Thứ 2',
            'Tuesday': 'Thứ 3',
            'Wednesday': 'Thứ 4',
            'Thursday': 'Thứ 5',
            'Friday': 'Thứ 6',
            'Saturday': 'Thứ 7',
            'Sunday': 'Chủ nhật',
        }
        # Ánh xạ ngày từ tiếng Anh sang tiếng Việt
        day_of_week = day_mapping.get(day_of_week, day_of_week) 
        return f"{day_of_week} ngày {day_of_month} tháng {month} năm {year}"
    return ""

@register.filter(name='get_range')
def get_range(value):
    return range(1, value + 1)
