import pygame
import os
import time
import random
import settings

pygame.font.init()

if settings.full_screen:
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
else:
    screen = pygame.display.set_mode((settings.width, settings.height))

# Setting caption and icon
pygame.display.set_caption(settings.caption)
pygame.display.set_icon(pygame.image.load(settings.icon_image))

# Load images
PLAYER_IMAGE = pygame.image.load(settings.player_image)
ALIEN_IMAGE1 = pygame.image.load(settings.alien_image[0])
ALIEN_IMAGE2 = pygame.image.load(settings.alien_image[1])
ALIEN_IMAGE3 = pygame.image.load(settings.alien_image[2])
ALIEN_IMAGE4 = pygame.image.load(settings.alien_image[3])
ALIEN_IMAGE5 = pygame.image.load(settings.alien_image[4])
BULLET_IMAGE = pygame.image.load(settings.bullet_image)
BACKGROUND_IMAGE = pygame.transform.scale(pygame.image.load(settings.background_image),
                                          (screen.get_width(), screen.get_height()))


class Laser:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, window):
        window.blit(self.image, (self.x, self.y))

    def move(self, speed):
        self.y += speed

    def off_screen(self, height):
        return not (height >= self.y >= 0)

    def collision(self, obj):
        return collide(obj, self)


class Object:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.obj_image = None
        self.laser_image = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.obj_image, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, speed, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(speed)
            if laser.off_screen(screen.get_height()):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_image)
            self.lasers.append(laser)
            self.cool_down_counter = 1


class Player(Object):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.obj_image = PLAYER_IMAGE
        self.laser_image = BULLET_IMAGE
        self.mask = pygame.mask.from_surface(self.obj_image)
        self.max_health = health

    def move_lasers(self, speed, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(speed)
            if laser.off_screen(screen.get_height()):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        obj.health -= 10
                        self.lasers.remove(laser)

    def get_width(self):
        return self.obj_image.get_width()

    def get_height(self):
        return self.obj_image.get_height()


class Alien(Object):
    which_alien = {
        1: (ALIEN_IMAGE1, BULLET_IMAGE),
        2: (ALIEN_IMAGE2, BULLET_IMAGE),
        3: (ALIEN_IMAGE3, BULLET_IMAGE),
        4: (ALIEN_IMAGE4, BULLET_IMAGE),
        5: (ALIEN_IMAGE5, BULLET_IMAGE)
    }

    def __init__(self, x, y, index_of_alien, health=100):
        super().__init__(x, y, health)
        self.obj_image, self.laser_image = self.which_alien[index_of_alien]
        self.mask = pygame.mask.from_surface(self.obj_image)

    def move(self, speed):
        self.y += speed

    def get_width(self):
        return self.obj_image.get_width()

    def get_height(self):
        return self.obj_image.get_height()


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap_mask(obj2, (offset_x, offset_y)) is not None


def main():
    run = True
    FPS = settings.fps

    # level = settings.player_level
    level = 0
    lives = settings.player_lives
    player_speed = settings.player_speed
    laser_speed = 4
    main_font = pygame.font.SysFont("comics", 50)
    lost_font = pygame.font.SysFont("comics", 65)
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    lost = False
    lost_count = 0

    # Creating aliens
    aliens = []
    wave_length = 5
    alien_speed = 1

    # creating a player
    player = Player(screen_width / 2, screen_height * 3 / 4)

    clock = pygame.time.Clock()

    def redraw_screen():
        screen.blit(BACKGROUND_IMAGE, (0, 0))

        # Draw text
        level_label = main_font.render(f'Level: {level}', 1, (255, 255, 255))
        lives_label = main_font.render(f'Lives: {lives}', 1, (255, 255, 255))
        screen.blit(lives_label, (10, 10))
        screen.blit(level_label, (screen_width - level_label.get_width() - 10, 10))

        # Draw aliens
        for alien in aliens:
            Alien.draw(alien, screen)

        # Draw player
        player.draw(screen)

        if lost:
            lost_label = lost_font.render('You lost!!', 1, (255, 255, 255))
            screen.blit(lost_label, (screen_width / 2 - lost_label.get_width() / 2, screen_height / 2))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_screen()
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 5:
                run = False
            else:
                continue

        if len(aliens) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                alien = Alien(random.randrange(50, screen_width - 50 - 64), random.randrange(-1500, -100),
                              random.randint(1, 5))
                aliens.append(alien)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Checking all keys
        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            run = False
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and player.x > 0:
            player.x -= player_speed
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and player.x + player.get_width() < screen_width:
            player.x += player_speed
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and player.y > 0:
            player.y -= player_speed
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and player.y + player.get_height() < screen_height:
            player.y += player_speed
        if keys[pygame.K_SPACE]:
            player.shoot()

        for alien in aliens[:]:
            alien.move(alien_speed)
            alien.move_lasers(laser_speed, player)
            if alien.y + alien.get_height() > screen_height:
                lives -= 1
                aliens.remove(alien)
        player.move_lasers(-laser_speed, aliens)


if __name__ == '__main__':
    main()
