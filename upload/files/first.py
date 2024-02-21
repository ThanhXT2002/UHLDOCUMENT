print("Trần Xuân Thành_khmt_k6b")
name=input("mời bạn nhập tên:")
print("Xin chào:", name)
x = 5 
print(x +5)
cau_chao="Xin chào"
name2 ="trần xuân thành"
print(cau_chao + name2*4)

# mảng

mumbers = [1,2,3,4,5,6,76,8]
name3 =["trần xuân thành", "trần xuân minh"]

age = 15

if age < 18:
    print("cút mẹ mày đi")
else:
    print("học hay không thì tùy")


i = 0
while i < 20:
    print("trần xuân thành")
    i+=1

phim1080 = ["the  flash","super man","wonder woman"]

for phim in phim1080:
    print(phim)


# hàm


def tinh_tong(n):
    tong = 0
    i =1
    while i <=n:
        tong = tong +i
        i = i+1

    return tong

print(tinh_tong(10))
print(tinh_tong(20))
print(tinh_tong(30))


# kết thúc hàm

s = 'abcd xyz'
#Lấy các ký tự từ 1 đến 7 trong s với bước là 2
s1 = s[1: 7: 2]
print("s1 = ",s1) # s1 = "bdx"

a=1
b=2
c=3
x=4.5
#Định dạng chuỗi hiển thị 3 số ra màn hình
print("a={0}, b={1}, x={2}".format(a,b,x))