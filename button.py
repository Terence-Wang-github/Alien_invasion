import pygame.font

class Button():
    """ 创建带标签的实心矩形按钮 """
    def __init__(self, ai_settings, screen, msg):
        """ 初始化按钮的属性 """
        self.ai_settings = ai_settings
        self.screen = screen
        self.screen_rect = self.screen.get_rect()

        #按钮的尺寸和属性
        self.button_width, self.button_height = 200, 50
        self.button_color = (0, 255, 0)
        self.text_color = (255, 255, 255)
        self.font = pygame.font.SysFont(None, 48)

        #在(0, 0)处创建按钮的rect对象，并使其于屏幕居中
        self.rect = pygame.Rect(0, 0, self.button_width, self.button_height)
        self.rect.center = self.screen_rect.center

        #此按钮的标签只需创建一次
        self.prep_msg(msg)

    def prep_msg(self, msg):
        """ 将msg渲染为图像，并使其在按钮上居中 """
        self.msg_image = self.font.render(msg, True, self.text_color,
            self.button_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def draw_button(self):
        """ 绘制一个用颜色填充的按钮，再绘制文本 """
        self.screen.fill(self.button_color, self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)









