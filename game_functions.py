import sys
from time import sleep

import pygame
from bullet import Bullet
from alien import Alien

def check_keydown_events(event, ai_settings, screen, ship, bullets):
    """ 响应按键 """
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        fire_bullets(ai_settings, screen, ship, bullets)
    elif event.key == pygame.K_q:
        sys.exit()

def check_keyup_events(event, ship):
    """ 响应松开 """
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False

def check_play_button(ai_settings, screen, aliens, bullets, ship, play_button,
        stats, mouse_x, mouse_y):
    """ 在玩家单击Play按钮时开始新游戏 """
    if (not stats.game_active and 
            play_button.rect.collidepoint(mouse_x, mouse_y)):
        #重置游戏设置
        ai_settings.initialize_dynamic_settings()

        #隐藏光标
        pygame.mouse.set_visible(False)

        #重置游戏统计信息
        stats.reset_stats()
        stats.game_active = True

        #清空外星人列表和子弹列表
        aliens.empty()
        bullets.empty()

        #创建一群新的外星人并将飞船放到屏幕中间
        creat_fleet(ai_settings, screen, aliens, ship)

def check_events(ai_settings, screen, stats, ship, play_button, aliens,
        bullets):
    #响应键盘和鼠标事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, screen, ship, bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_settings, screen, aliens, bullets, ship,
                play_button, stats, mouse_x, mouse_y)

def update_screen(ai_settings, screen, ship, bullets, aliens, stats,
        play_button):
    """ 更新屏幕上的图像，并切换到新屏幕 """
    #每次循环都重新绘制屏幕
    screen.fill(ai_settings.bg_color)

    #在飞船和外星人后面重绘所有子弹
    for bullet in bullets.sprites():
        bullet.draw_bullet()

    ship.blitme()
    aliens.draw(screen)

    #如果游戏处于非活动状态，就绘制play按钮
    if not stats.game_active:
        play_button.draw_button()

    #让最近绘制的屏幕可见
    pygame.display.flip()


def update_bullets(ai_settings, screen, aliens, ship, bullets):
    """ 更新子弹的位置，并删除已消失的子弹 """
    #更新子弹的位置
    bullets.update()

    #删除已消失的子弹
    for bullet in bullets.copy():   #此处copy不知何意啊，删了也一样运行
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)
        # print(len(bullets))

    check_bullets_aliens_collisions(ai_settings, screen, aliens, ship, bullets)

def check_bullets_aliens_collisions(ai_settings, screen, aliens, ship, bullets):
    #检查是否有子弹和外星人的碰撞
    #删除发生碰撞的子弹和外星人
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)

    #如果外星人全部消失，删除现有子弹，并新建一群外星人
    if len(aliens) == 0:
        bullets.empty()
        ai_settings.increase_speed()
        creat_fleet(ai_settings, screen, aliens, ship)


def fire_bullets(ai_settings, screen, ship, bullets):
    """ 如果没有达到限制，就发射一颗子弹 """
    #创建一颗子弹，并将其加入编组bullets中
    if len(bullets) < ai_settings.bullets_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)


def get_number_aliens_x(ai_settings, alien_width):
    """ 计算每行可容纳多少个外星人 """
    available_space_x = ai_settings.screen_width - 2 * alien_width
    number_aliens_x = int(available_space_x / (2 * alien_width))
    return number_aliens_x

def get_number_rows(ai_settings, alien_height, ship_height):
    """ 计算屏幕能容纳多少行外星人 """
    ##注意此处计算式换行时的括号使用
    available_space_y = (ai_settings.screen_height -
                            3 * alien_height - ship_height)

    number_rows = int(available_space_y / (2 * alien_height))
    return number_rows 

def creat_alien(ai_settings, screen, aliens, alien_number, row_number):
    """ 创建一个外星人并将其放在放在当前行的当前列 """
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width
    alien_height = alien.rect.height
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.y = alien_height + 2 * alien_height * row_number
    alien.rect.y = alien.y 
    aliens.add(alien)

def creat_fleet(ai_settings, screen, aliens, ship):
    """ 创建外星人群 """
    #创建一个外星人，并计算一行可容纳多少个外星人
    #计算屏幕能容纳多少行外星人
    alien = Alien(ai_settings, screen)
    number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)
    number_rows = get_number_rows(ai_settings, alien.rect.height,
        ship.rect.height)

    #创建外星人群
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            creat_alien(ai_settings, screen, aliens, alien_number, row_number)

def check_fleet_edges(ai_settings, aliens):
    """ 有外星人到达边缘时次啊去相应的措施 """
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break

def change_fleet_direction(ai_settings, aliens):
    """ 将整群外星人下移，并改变他们的方向 """
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.drop_speed_factor
    ai_settings.fleet_direction *= -1

def ship_hit(ai_settings, screen, ship, aliens, bullets, stats):
    """ 响应被外星人撞到的飞船 """
    if stats.ships_left > 0:
        #将ship_left减1
        stats.ships_left -= 1

        #清空子弹和外星人
        bullets.empty()
        aliens.empty()

        #创建一群外星人并将飞船放到屏幕中间
        creat_fleet(ai_settings, screen, aliens, ship)
        ship.center = ship.screen_rect.centerx

        #暂停
        sleep(0.5)

    else:
        stats.game_active = False
        pygame.mouse.set_visible(True)

def check_aliens_bottom(ai_settings, screen, ship, aliens, bullets, stats):
    """ 检查是否有外星人到达了屏幕底部 """
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            #像飞船被撞到一样处理
            ship_hit(ai_settings, screen, ship, aliens, bullets, stats)
            break

def update_aliens(ai_settings, screen, ship, aliens, bullets, stats):
    """ 检查是否有外星人到达屏幕边缘
    更新所有外星人的位置 """
    check_fleet_edges(ai_settings, aliens)
    aliens.update()

    #检测外星人和飞船之间的碰撞
    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(ai_settings, screen, ship, aliens, bullets, stats)

    #检查是否有外星人到达屏幕底端
    check_aliens_bottom(ai_settings, screen, ship, aliens, bullets, stats)


