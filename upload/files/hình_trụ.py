import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

# Tạo hình nón bằng cách tạo tọa độ của mặt đáy và điểm cao
radius = 1
height = 2
samples = 100  # Số điểm mẫu

theta = np.linspace(0, 2 * np.pi, samples)
z = np.linspace(0, height, samples)
Theta, Z = np.meshgrid(theta, z)
X = radius * np.cos(Theta)
Y = radius * np.sin(Theta)

# Tạo một subplot 3D
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Vẽ hình nón
ax.plot_surface(X, Y, Z, color='b', alpha=0.7)

# Cài đặt giới hạn trục
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.set_zlim(0, 2)

# Đặt nhãn trục
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

# Hiển thị đồ thị
plt.show()
