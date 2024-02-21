import tkinter as tk
from tkinter import ttk
import pandas as pd
import os

class SanPham:
    san_pham_id_counter = 1

    def __init__(self, ten, gia, so_luong_ton_kho, loai_san_pham):
        self.san_pham_id = SanPham.san_pham_id_counter
        SanPham.san_pham_id_counter += 1
        self.ten = ten
        self.gia = gia
        self.so_luong_ton_kho = so_luong_ton_kho
        self.loai_san_pham = loai_san_pham

def doc_san_pham_tu_dataframe(df):
    san_pham_list = []
    for index, row in df.iterrows():
        san_pham_id = row["ID"]
        ten = row["Tên"]
        gia = row["Giá"]
        so_luong_ton_kho = row["Tồn kho"]
        loai_san_pham = row["Loại sản phẩm"]

        san_pham = SanPham(ten, gia, so_luong_ton_kho, loai_san_pham)
        san_pham.san_pham_id = san_pham_id
        san_pham_list.append(san_pham)
    return san_pham_list

def luu_danh_sach_san_pham(san_pham_list):
    data = [[sp.san_pham_id, sp.ten, sp.gia, sp.so_luong_ton_kho, sp.loai_san_pham] for sp in san_pham_list]
    df = pd.DataFrame(data, columns=["ID", "Tên", "Giá", "Tồn kho", "Loại sản phẩm"])
    df.to_csv('san_pham.csv', index=False)
    return "Lưu danh sách sản phẩm thành công."


def update_san_pham_listbox():
    san_pham_tree.delete(*san_pham_tree.get_children())
    for san_pham in san_pham_list:
        san_pham_tree.insert("", "end", values=(san_pham.san_pham_id, san_pham.ten, san_pham.gia, san_pham.so_luong_ton_kho, san_pham.loai_san_pham))

def them_san_pham(loai_san_pham, ten, gia, so_luong_ton_kho):
    san_pham = SanPham(ten, gia, so_luong_ton_kho, loai_san_pham)
    san_pham_list.append(san_pham)
    luu_danh_sach_san_pham(san_pham_list)
    return "Thêm sản phẩm thành công."


def ban_hang():
    def luu_hoa_don():
        san_pham_id = san_pham_var.get()
        so_luong = so_luong_entry.get()

        if not all([san_pham_id, so_luong]):
            result_label.config(text="Vui lòng nhập đầy đủ thông tin.", fg="red")
        else:
            try:
                san_pham_id = int(san_pham_id)
                so_luong = int(so_luong)
                san_pham = next((sp for sp in san_pham_list if sp.san_pham_id == san_pham_id), None)
                if san_pham and san_pham.so_luong_ton_kho >= so_luong:
                    san_pham.so_luong_ton_kho -= so_luong
                    luu_danh_sach_san_pham(san_pham_list)
                    result_label.config(text="Bán hàng thành công.", fg="green")
                    update_san_pham_listbox()
                else:
                    result_label.config(text="Sản phẩm không đủ tồn kho hoặc không tồn tại.", fg="red")
            except ValueError:
                result_label.config(text="Số lượng và ID sản phẩm phải là số nguyên.", fg="red")


    blue_frame = tk.Frame(frame2, width=500, height=300)
    blue_frame.grid(row=0, column=0, columnspan=2)

    ban_hang_label = tk.Label(blue_frame, text="Chức năng Bán hàng", font=("timesnewroman", 16, "bold"))
    ban_hang_label.pack()

    san_pham_label = tk.Label(blue_frame, text="ID Sản phẩm:")
    san_pham_label.pack()
    san_pham_var = tk.StringVar(value="1")
    
    san_pham_entry = tk.Entry(blue_frame, textvariable=san_pham_var)
    san_pham_entry.pack()

    so_luong_label = tk.Label(blue_frame, text="Số lượng:")
    so_luong_label.pack()

    so_luong_entry = tk.Entry(blue_frame)
    so_luong_entry.pack()

    ban_button = tk.Button(blue_frame, text="Bán hàng", command=luu_hoa_don)
    ban_button.pack()

    result_label = tk.Label(blue_frame, text="", fg="green")
    result_label.pack()

def them_san_pham_gui():
    def luu_san_pham():
        loai_san_pham = loai_san_pham_var.get()
        ten = ten_entry.get()
        gia = gia_entry.get()
        so_luong_ton_kho = so_luong_ton_kho_entry.get()
        
        if not all([ten, gia, so_luong_ton_kho]):
            result_label.config(text="Vui lòng nhập đầy đủ thông tin sản phẩm.", fg="red")
        else:
            if loai_san_pham == "1":
                loai_san_pham_str = "Sách"
            elif loai_san_pham == "2":
                loai_san_pham_str = "Văn phòng phẩm"
            else:
                loai_san_pham_str = "Khác"

            result = them_san_pham(loai_san_pham_str, ten, gia, so_luong_ton_kho)
            result_label.config(text=result, fg="green")
            update_san_pham_listbox()
    green_frame = tk.Frame(frame3, width=500, height=300)
    green_frame.grid(row=0, column=0, columnspan=2)

    them_san_pham_label = tk.Label(green_frame, text="Chức năng Thêm sản phẩm", font=("Helvetica", 16, "bold"))
    them_san_pham_label.pack(pady=10)

    loai_san_pham_label = tk.Label(green_frame, text="Loại sản phẩm (1 - Sách, 2 - Văn phòng phẩm):")
    loai_san_pham_label.pack()

    loai_san_pham_var = tk.StringVar(value="1")
    loai_san_pham_entry = tk.Entry(green_frame, textvariable=loai_san_pham_var,  width=30)
    loai_san_pham_entry.pack()

    ten_label = tk.Label(green_frame, text="Tên sản phẩm:")
    ten_label.pack()

    ten_entry = tk.Entry(green_frame, width=30)
    ten_entry.pack()

    gia_label = tk.Label(green_frame, text="Giá:")
    gia_label.pack()

    gia_entry = tk.Entry(green_frame,  width=30)
    gia_entry.pack()

    so_luong_ton_kho_label = tk.Label(green_frame, text="Số lượng tồn kho:")
    so_luong_ton_kho_label.pack()

    so_luong_ton_kho_entry = tk.Entry(green_frame,  width=30)
    so_luong_ton_kho_entry.pack()

    luu_button = tk.Button(green_frame, text="Lưu sản phẩm", command=luu_san_pham,  width=20)
    luu_button.pack()

    result_label = tk.Label(green_frame, text="", fg="green")
    result_label.pack()

if __name__ == "__main__":
    san_pham_list = []

    csv_file = 'san_pham.csv'
    if os.path.isfile(csv_file):
        df = pd.read_csv(csv_file)
        san_pham_list = doc_san_pham_tu_dataframe(df)
        SanPham.san_pham_id_counter = max(san_pham_list, key=lambda x: x.san_pham_id).san_pham_id + 1

    root = tk.Tk()
    root.title("Quản lý sản phẩm")

    frame1 = tk.Frame(root, bg="red", width=1000, height=400)
    frame2 = tk.Frame(root, bg="blue", width=500, height=300)
    frame3 = tk.Frame(root, bg="green", width=500, height=300)

    frame1.grid(row=0, column=0, columnspan=2)
    frame2.grid(row=1, column=0)
    frame3.grid(row=1, column=1)

    red_frame = tk.Frame(frame1, width=1200, height=400)
    red_frame.grid(row=0, column=0, columnspan=2)

    danh_sach_san_pham_label = tk.Label(red_frame, text="Danh sách sản phẩm", font=("Helvetica", 16))
    danh_sach_san_pham_label.pack(pady=10)

    san_pham_tree = ttk.Treeview(red_frame, columns=["ID", "Tên", "Giá", "Tồn kho", "Loại sản phẩm"], show="headings")
    san_pham_tree.heading("ID", text="ID")
    san_pham_tree.heading("Tên", text="Tên")
    san_pham_tree.heading("Giá", text="Giá")
    san_pham_tree.heading("Tồn kho", text="Tồn kho")
    san_pham_tree.heading("Loại sản phẩm", text="Loại sản phẩm")
    san_pham_tree.pack(fill=tk.BOTH, expand=True)

    update_san_pham_listbox()

    ban_hang()
    them_san_pham_gui()

    root.mainloop()
