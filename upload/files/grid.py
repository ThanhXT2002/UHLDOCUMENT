import tkinter as tk
from tkinter import ttk

top = tk.Tk()
top.title("Quản lý khách hàng")

# Tùy chỉnh kích thước cửa sổ
top.geometry("1000x500")  # Đặt kích thước cửa sổ thành 800x400 pixel
title_label = tk.Label(top, text="Quản lý thông tin khách hàng", font=("Helvetica", 16))
title_label.grid(column=3, row=0, pady=(20, 30))  # pady=(trên, dưới)

custom_font = ("Helvetica", 12)

lb_name = tk.Label(top, text="Tên", padx=20, font=custom_font)
lb_name.grid(column=0, row=1, pady=(10, 5))  # pady=(trên, dưới)
et_name = tk.Entry(top, width=30, font=custom_font)
et_name.grid(column=1, row=1, pady=(10, 5))  # pady=(trên, dưới)

lb_email = tk.Label(top, text="Email", padx=20, font=custom_font)
lb_email.grid(column=3, row=1, pady=(10, 5))  # pady=(trên, dưới)
et_email = tk.Entry(top, width=30, font=custom_font)
et_email.grid(column=4, row=1, pady=(10, 5))  # pady=(trên, dưới)

lb_gender = tk.Label(top, text="Địa chỉ", font=custom_font)
lb_gender.grid(column=0, row=2, pady=(10, 5))  # pady=(trên, dưới)
et_gender = tk.Entry(top, width=30, font=custom_font)
et_gender.grid(column=1, row=2, pady=(10, 5))  # pady=(trên, dưới)

lb_address = tk.Label(top, text="Giới tính", font=custom_font)
lb_address.grid(column=3, row=2, pady=(10, 5))  # pady=(trên, dưới)
gender_values = ["Male", "Female", "Other"]
et_gender = ttk.Combobox(top, values=gender_values, width=28, font=custom_font)
et_gender.grid(column=4, row=2, pady=(10, 5))  # pady=(trên, dưới)

# Tạo một lưới hiển thị (Treeview) để hiển thị danh sách khách hàng
tree = ttk.Treeview(top, columns=("Id","Name", "Email", "Address", "Gender"), show="headings", height=10)
tree.heading("Id", text="Id")
tree.heading("Name", text="Tên")
tree.heading("Email", text="Email")
tree.heading("Address", text="Địa chỉ")
tree.heading("Gender", text="Giới tính")
tree.grid(column=0, row=5, columnspan=5, padx=10, pady=10)

add_button = tk.Button(top, text="Thêm khách hàng", width=20, font=custom_font)
add_button.grid(column=1, row=4, pady=(10, 5))  # pady=(trên, dưới)
edit_button = tk.Button(top, text="Sửa khách hàng", width=20, font=custom_font)
edit_button.grid(column=3, row=4, pady=(10, 5))  # pady=(trên, dưới)
delete_button = tk.Button(top, text="Xóa khách hàng", width=20, font=custom_font)
delete_button.grid(column=4, row=4, pady=(10, 5))  # pady=(trên, dưới)

top.mainloop()
