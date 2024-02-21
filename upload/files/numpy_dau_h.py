"""
sử dụng thư viện numpy để quản lý một dãy số nguyên có các yêu cầu sau:
1. cập nhật một dãy số nguyên và sắp xếp theo chiều giảm dần
2. tạo một dãy số có 10 phần tử đều có giá trị là 0
3. tạo một dãy số có 5 phần tử đều có giá trị là 1
4. tạo một dãy số có giá trị trong đoạn tử 5 đến 10 mà mỗi phần tử cách nhau một 1 đơn vị
5. tạo dãy số có giá trị trong đoạn từ 1 đến 99 mà mỗi phần từ cách nhau 2 đơn vị
6. lấy 3 phần tử cuối cùng từ dãy được tạo từ yêu cầu 5 
7. thực hiện đảo ngược dãy số đc tạo từ mục 4
8. lấy kích thước (số lượng phần tử) của dãy được tạo từ mục 5
9. lấy giá trị nhỏ nhất, lớn nhất,  trung bình của dãy ở mục 5.
10. nhập vào từ bàn phím một số nguyên k, thực hiền chèn số nguyên k vào vị trí số 5 trong dãy được tạo từ mục 5.
11. nhập vào từ bàn phím một số nguyên k, thực hiện xóa phần tử ỏ vị trí k trong dãy được tạo ở mục 5
12.  tăng đồng thời các giá trị phần tử ở dãy được tạo ở mục 4 lên 2 đơn vị
"""

import numpy as np
#yêu cầu 1
n = int(input("Nhập vào phần tử: "))
arr1 = np.array([])
for i in range(n):
    phan_tu = int(input(f"Nhập phần tử thứ {i + 1}: "))
    arr1 = np.append(arr1, phan_tu)

arr1 = np.sort(arr1)[::-1]
arr1_2 = -np.sort(-arr1)

print("Sắp xếp dãy theo chiều giảm dần: ", arr1)
print("Sắp xếp dãy theo chiều giảm dần: ", arr1_2)
#yêu cầu 2
arr2 = np.zeros(10, dtype=int)
print("Dãy có 10 phần tử là 0: ", arr2)
#yêu cầu 3
arr3 = np.ones(5, dtype=int)

print("Dãy có 5 phần tử là 1: ", arr3)
#yêu cầu 4
arr4 = np.arange(5, 11)
print("Dãy có giá trị từ 5 đến 10 cách nhau 1 đơn vị : ", arr4)
#yêu cầu 5
arr5 = np.arange(1, 100, 2)
print("Dãy có giá trị trong đoạn từ 1 - 99 cách nhau 2 đơn vị: ", arr5)
#yêu cầu 6
arr6 = arr5[-3:]
print("Lấy 3 phần tử cuối cùng từ dãy 5 : ", arr6)

#yêu cầu 7
arr7 = arr4[::-1]
arr7_1 = np.flip(arr4)
print("Đảo ngược dãy 4: ", arr7)
#yêu cầu 8
yeu_cau_8 = len(arr5)
yeu_cau_8_1 = arr5.size
print(f"dãy 5 có {yeu_cau_8} phần tử  ")
#yêu cầu 9
min_value = np.min(arr5)
max_value = np.max(arr5)
mean_value = np.mean(arr5)

print(f"Giá trị lớn nhất {max_value}, giá trị nhỏ nhất {min_value}, giá trị trung bình {mean_value} của dãy 5")
#yêu cầu 10
k = int(input("Nhập số nguyên k: "))
arr10 = np.insert(arr5, 4, k)
print("Dãy mới sau khi chèn : ", arr10)
#yêu cầu 11
k = int(input("Nhập số nguyên k để xóa: "))
arr11 = np.delete(arr5, k - 1)
print("Dãy mới sau khi xóa: ", arr11)

#yêu cầu 12
arr4 += 2
print("Dãy mới sau khi tăng 2 đơn vị : ", arr4)



