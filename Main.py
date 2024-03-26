import pygame
import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from pygame.locals import *
from PIL import Image

# 初始化 Pygame
pygame.init()

# 屏幕尺寸
WIDTH, HEIGHT = 1200, 800

# 创建 Pygame 显示窗口
screen = pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
pygame.display.set_caption("3D Solar System Simulator")
pygame.display.init()
info = pygame.display.Info()

# 设置透视投影和相机位置
gluPerspective(65, (WIDTH / HEIGHT), 0.1, 2000.0)
gluLookAt(0, 40, 60, 0, 0, 0, 0, 1, 0)

# 启用深度测试和颜色材质
glEnable(GL_DEPTH_TEST)
glEnable(GL_COLOR_MATERIAL)
glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
glEnable(GL_LIGHT0)
glEnable(GL_LIGHTING)
glLightfv(GL_LIGHT0, GL_POSITION, (0, 0, 0, 1))
glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))

skybox_angle = 0

# 生成纹理
textures = {}

def load_textures():
    planets = ["Mercury", "Venus", "Earth", "Moon", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Sun", "New", "skybox"]
    for planet in planets:
        texture_file = planet + ".jpg"
        texture_surface = Image.open(texture_file)
        texture_data = texture_surface.tobytes("raw", "RGB", 0, -1)
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, texture_surface.width, texture_surface.height,
                    0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        textures[planet] = texture_id

load_textures()

class Planet:
    def __init__(self, distance, radius, color, speed, text, parent=None, ring=None):
        self.distance = distance
        self.radius = radius
        self.color = color
        self.speed = speed
        self.text = text
        self.angle = 0
        self.parent = parent
        self.ring = ring
        self.path = []

    def draw(self):
        glColor3fv(self.color)
        glPushMatrix()

        if self.parent:
            glRotatef(self.parent.angle, 0, -1, 0)
            glTranslatef(self.parent.distance, 0, 0)

            # 绘制轨道
            num_segments = 64
            glBegin(GL_LINE_LOOP)
            for i in range(num_segments):
                theta = 2.0 * math.pi * i / num_segments
                x = self.distance * math.cos(theta)
                z = self.distance * math.sin(theta)
                glVertex3f(x, 0, z)
            glEnd()
        
        # 绘制行星
        glRotatef(self.angle, 0, -1, 0)
        glTranslatef(self.distance, 0, 0)
        glRotatef(90, 1, 0, 0)


        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, textures[self.text])

        texture_able = gluNewQuadric()
        gluQuadricTexture(texture_able, GL_TRUE)
        gluSphere(texture_able, self.radius, 30, 30)

        gluDeleteQuadric(texture_able)

        # 禁用纹理映射
        glDisable(GL_TEXTURE_2D)

        glPopMatrix()

        # 绘制轨道路径
        if not self.parent:
            self.path.append((self.distance * math.cos(math.radians(self.angle)), 0, self.distance * math.sin(math.radians(self.angle))))

        max_path_length = 800
        if len(self.path) > max_path_length:
            self.path.pop(0)
        glBegin(GL_LINE_STRIP)
        for point in self.path:
            glVertex3fv(point)
        glEnd()

    def update(self):
        self.angle += self.speed
        
    def draw_ring(self):
        glPushMatrix()
        glRotatef(self.angle, 0, -1, 0)
        glTranslatef(self.distance, 0, 0)
        glRotatef(90, 1, 0, 0)

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, textures[self.text])

        texture_able = gluNewQuadric()
        gluQuadricTexture(texture_able, GL_TRUE)
        
        gluDisk(texture_able, self.radius + 0.5 , self.radius + 1.2, 32, 1)
        gluDisk(texture_able, self.radius + 1.3 , self.radius + 1.6, 32, 1)
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()


def draw_skybox():
    global skybox_angle
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (1, 1, 1, 1))
    glMaterialfv(GL_FRONT, GL_EMISSION, (1, 1, 1, 1))  # 设置自发光颜色
    glPushMatrix()
    glRotatef(skybox_angle, 0, 1, 0)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, textures["skybox"])

    texture_able = gluNewQuadric()
    gluQuadricTexture(texture_able, GL_TRUE)
    gluSphere(texture_able, 200, 32, 32)

    gluDeleteQuadric(texture_able)
    glPopMatrix()

    # 禁用纹理映射
    glDisable(GL_TEXTURE_2D)

    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (0, 0, 0, 1))
    glMaterialfv(GL_FRONT, GL_EMISSION, (0, 0, 0, 1))  # 设置自发光颜色
    skybox_angle += 0.05

def draw_sun():
    # 绘制太阳
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (1, 1, 0, 1))
    glMaterialfv(GL_FRONT, GL_EMISSION, (1, 1, 0, 1))  # 设置自发光颜色
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, textures["Sun"])

    texture_able = gluNewQuadric()
    gluQuadricTexture(texture_able, GL_TRUE)
    gluSphere(texture_able, 1, 32, 32)

    gluDeleteQuadric(texture_able)

    # 禁用纹理映射
    glDisable(GL_TEXTURE_2D)

    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (0, 0, 0, 1))
    glMaterialfv(GL_FRONT, GL_EMISSION, (0, 0, 0, 1))  # 设置自发光颜色

def draw_axes():
    # 绘制坐标轴
    glBegin(GL_LINES)

    glColor3f(1, 0, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(20, 0, 0)

    glColor3f(0, 1, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 20, 0)

    glColor3f(0, 0, 1)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, 20)

    glEnd()

def main():
    mercury = Planet(2, 0.4879/2, (1, 1, 1), 0.43, "Mercury")
    venus = Planet(5, 1.2104/2, (1, 1, 1), 1.04, "Venus")
    earth = Planet(7, 1.2756/2, (1, 1, 1), 1.12, "Earth")
    moon = Planet(1.584/2, 0.3475/2, (0.8, 0.8, 0.8), 0.24/2, "Moon", earth)
    mars = Planet(11, 0.6792/2, (1, 1, 1), 0.50, "Mars")
    jupiter = Planet(30.85, 3.2984, (1, 1, 1), 5.95/2, "Jupiter")
    saturn = Planet(40.20, 2.0536, (1, 1, 1), 3.55/2, "Saturn")
    uranus = Planet(60.70, 1.1118, (1, 1, 1), 2.13/2, "Uranus")
    neptune = Planet(70.50, 0.9528, (1, 1, 1), 2.35/2, "Neptune")
    New = Planet(23, 0.9528, (1, 1, 1), 1.5/2, "New")
    
    clock = pygame.time.Clock()
    
    running = True

    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            glRotatef(-1, 0, -1, 0)
        if keys[pygame.K_RIGHT]:
            glRotatef(1, 0, -1, 0)
        if keys[pygame.K_UP]:
            glTranslatef(0, -1, 0)
            glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (1, 1, 1, 0.2))
            glLightfv(GL_LIGHT0, GL_DIFFUSE, (0, 0, 0, 0.1))
        if keys[pygame.K_DOWN]:
            glTranslatef(0, 1, 0)
            glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (0, 0, 0, 1))
            glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))
        if keys[pygame.K_w]:
            glTranslatef(0, 0, 1)
        if keys[pygame.K_s]:
            glTranslatef(0, 0, -1)
        if keys[pygame.K_a]:
            glTranslatef(1, 0, 0)
        if keys[pygame.K_d]:
            glTranslatef(-1, 0, 0)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        draw_axes()
        
        draw_skybox()
        
        mercury.update()
        mercury.draw()

        venus.update()
        venus.draw()

        earth.update()
        earth.draw()

        moon.update()
        moon.draw()

        mars.update()
        mars.draw()

        jupiter.update()
        jupiter.draw()

        saturn.update()
        saturn.draw()
        saturn.draw_ring()

        uranus.update()
        uranus.draw()

        neptune.update()
        neptune.draw()
        
        New.update()
        New.draw()
        
        draw_sun()

        pygame.display.flip()
        pygame.time.wait(60) 

    pygame.quit()

if __name__ == "__main__":
    main()


