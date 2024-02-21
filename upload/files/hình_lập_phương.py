import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Tạo một đối tượng lập phương 3D
vertices = [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]
faces = [[vertices[0], vertices[1], vertices[2], vertices[3]],
         [vertices[4], vertices[5], vertices[6], vertices[7]], 
         [vertices[0], vertices[1], vertices[5], vertices[4]], 
         [vertices[2], vertices[3], vertices[7], vertices[6]], 
         [vertices[0], vertices[3], vertices[7], vertices[4]], 
         [vertices[1], vertices[2], vertices[6], vertices[5]]]

# Tạo đối tượng subplot 3D
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Vẽ hình lập phương
ax.add_collection3d(Poly3DCollection(faces, facecolors='cyan', linewidths=1, edgecolors='r', alpha=.25))

# Cài đặt các giới hạn trục
ax.set_xlim([-2, 2])
ax.set_ylim([-2, 2])
ax.set_zlim([-2, 2])

# Đặt nhãn trục
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

# Hiển thị đồ thị
plt.show()
