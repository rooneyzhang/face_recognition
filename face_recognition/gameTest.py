# 导入pygame模块
import pygame

# 初始化pygame
pygame.init()
width = 250
height = 300
speed = 10
# 创建舞台,利用Pygame中的display模块，来创建窗口
screen = pygame.display.set_mode((width, height), pygame.NOFRAME, 32)
# 设置窗口标题
pygame.display.set_caption("Hello PyGame")


# 我的cat.png和cat.py文件在同一个文件夹下面
# 所以可以直接这样加载图片的
# laod函数加载图片
cat = pygame.image.load("./static/test.jpg")
print(cat)
cat_x, cat_y = 0, 0  # 猫的坐标
h_direction = 1  # 水平方向
i=1
while i<10000:
    for event in pygame.event.get():
        # 这段程序大家可能比较费解，实际上是检测quit事件，实际讲课中让学生直接模仿即可，时间足够也可以讲明白
        if event.type == pygame.QUIT:
            pygame.quit()

    # blit函数的作用是把加载的图片放到舞台的（cat_x, cat_y）坐标的位置
    screen.blit(cat, (cat_x, cat_y))
    # 这样就实现了会移动的猫
    cat_x += speed * h_direction
    # 如果猫的坐标超出了640，就让小猫反向
    # 如果猫的坐标小于了0，也让小猫反向，这样就实现了碰到墙壁反弹的效果
    if cat_x > width:
        h_direction = -h_direction
    elif cat_x < 0:
        h_direction = -h_direction
    pygame.display.update()
    i=i+1

pygame.display.quit()
print("over")