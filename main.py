import pygame
from pygame.locals import *
from pygame import mixer
import pickle
import random
from os import path

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60

WIDTH = 1020
HEIGHT = 600

# Caption and Icon
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Pixel Quest')
icon = pygame.image.load('Assets/Characters/Mask Dude/Idle/5.png')
pygame.display.set_icon(icon)

# Define font
font_score = pygame.font.SysFont('Bauhaus 93', 30)

# Define game variables
tile_size = 30
game_over = 0
main_menu = True
level = 0
max_level = 11
play_music = False

# Define colors
white  = (255, 255, 255)

# Load images
bg_img = pygame.image.load('Assets/Background/Background1.png').convert_alpha()
bg_img2 = pygame.image.load('Assets/Background/Background2.png').convert_alpha()
restart_img = pygame.image.load('Assets/Menu/Buttons/restart_btn.png').convert_alpha()
start_img = pygame.image.load('Assets/Menu/Main Menu/start_btn.png').convert_alpha()
quit_img = pygame.image.load('Assets/Menu/Main Menu/quit_btn.png').convert_alpha()
title_img = pygame.image.load('Assets/Menu/Main Menu/title.png').convert_alpha()
left_right_img = pygame.image.load('Assets/Other/left_right_keys.png').convert_alpha()
space_img = pygame.image.load('Assets/Other/space_key.png').convert_alpha()
coin_img = pygame.image.load('Assets/Items/coin.png').convert_alpha()
thank_you_img = pygame.image.load('Assets/Menu/Text/thank_you.png').convert_alpha()

# Scale image
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
bg_img2 = pygame.transform.scale(bg_img2, (WIDTH, HEIGHT))
start_img = pygame.transform.scale(start_img, (150, 50))
quit_img = pygame.transform.scale(quit_img, (150, 50))
title_img = pygame.transform.scale(title_img, (600, 400))

# Load sounds
coin_fx = pygame.mixer.Sound('Assets/Sounds/coin.wav')
coin_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound('Assets/Sounds/jump.wav')
jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound('Assets/Sounds/game_over.wav')
game_over_fx.set_volume(0.5)

# Music themes playlist
music = {
  'title_theme': 'Assets/Sounds/title_theme.wav',
  'minigame_theme': 'Assets/Sounds/minigame_theme.wav',
  'credits_theme': 'Assets/Sounds/credits_theme.wav',
  'battle_theme': 'Assets/Sounds/battle_theme.wav',
  'final_theme': 'Assets/Sounds/final_theme.wav',
  'credits_theme': 'Assets/Sounds/credits_theme.wav'
}

# Function to assign coins per level
def level_coin(level):
  levels = {
    0: 7,
    1: 5,
    2: 6,
    3: 6,
    4: 6,
    5: 12,
    6: 13,
    7: 16,
    8: 13,
    9: 14,
    10: 10,
    11: 0
  }

  return levels.get(level)

# Function to reset level
def reset_level(level):
  player.reset(60, HEIGHT - 60)
  slime_group.empty()
  platform_x_group.empty()
  platform_y_group.empty()
  fire_group.empty()
  exit_group.empty()
  saw_left_group.empty()
  saw_right_group.empty()
  ghost_group.empty()

  # Load in level data and create world
  if path.exists(f'Levels/level{level}_data'):
    pickle_in = open(f'Levels/level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
  world = World(world_data)

  return world


# Draw text 
def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  window.blit(img, (x, y))

# Draw text image
def draw_image(image, x, y):
  window.blit(image, (x, y))

# Draw image for tutorial
def draw_tutorial(image, x, y):
  img = pygame.transform.scale(image, (60, 45))
  window.blit(img, (x, y))

# Draw level indicator
def draw_level(level):
  img = pygame.image.load(f'Assets/Menu/Levels/{level}.png')
  img = pygame.transform.scale(img, (30, 30))
  window.blit(img, (60, HEIGHT - 90))

# Restart interface
class Restart():
  def __init__(self, x, y, image):
    self.image = image
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y

  def draw(self):
    window.blit(self.image, self.rect)
    key = pygame.key.get_pressed()
    if key[pygame.K_r]:
      return True

# Button interface
class Button():
  def __init__(self, x, y, image):
    self.image = image
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y
    self.clicked = False
     
  def draw(self):
    action = False
    # Get mouse position
    pos = pygame.mouse.get_pos()

    # Check mouseover and click condition
    if self.rect.collidepoint(pos):
      if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
        action = True
        self.clicked = True
    
    if pygame.mouse.get_pressed()[0] == 0:
      self.clicked = False      


    # Draw button
    window.blit(self.image, self.rect)
    return action


class Player():
  def __init__(self, x, y):
    self.reset(x, y)

  def update(self, game_over): 
    dx = 0
    dy = 0
    idle_cooldown = 8
    run_cooldown = 6
    dead_cooldown = 8
    col_thresh = 10
  
    if game_over == 0:
      # Get keypresses
      key = pygame.key.get_pressed()
      if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
        jump_fx.play()
        self.vel_y = -13
        self.jumped = True
      if key[pygame.K_SPACE] == False:
        self.jumped = False
      if key[pygame.K_LEFT]:
        dx -= 3
        self.counter_run += 1
        self.direction = -1
        self.image = self.images_left_run[self.index_run]
      if key[pygame.K_RIGHT]:
        dx += 3
        self.counter_run += 1
        self.direction = 1
        self.image = self.images_right_run[self.index_run]
      if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
        self.counter_run = 0
        self.index_run = 0
        self.image = self.images_right[self.index]
        if self.direction == 1:
          self.image = self.images_right[self.index]
        if self.direction == -1:
          self.image = self.images_left[self.index]
      
      # Handle idle animation
      self.counter += 1
      if self.counter > idle_cooldown:
        self.counter = 0
        self.index += 1
        if self.index >= len(self.images_right):
          self.index = 0
        if self.direction == 1:
          self.image = self.images_right[self.index]
        if self.direction == -1:
          self.image = self.images_left[self.index]

      # Handle run animation
      self.counter_run += 1
      if self.counter_run > run_cooldown:
        self.counter_run = 0
        self.index_run += 1
      if self.index_run >= len(self.images_right_run):
        self.index_run = 0
      if self.direction == 1:
        self.image_run = self.images_right_run[self.index_run]
      if self.direction == -1:
        self.image_run = self.images_left_run[self.index_run]

      # Add gravity
      self.vel_y += 1
      if self.vel_y > 6:
        self.vel_y = 6
      dy += self.vel_y

      # Check for collision
      self.in_air = True
      for tile in world.tile_list:
        # Check for collision in x direction
        if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
          dx = 0

        # Check for collision in y direction
        if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
          # Check if below the ground i.e. Jumping
          if self.vel_y < 0:
            dy = tile[1].bottom - self.rect.top
            self.vel_y = 0
          # Check if above the ground i.e. Falling
          elif self.vel_y >= 0:
            dy = tile[1].top - self.rect.bottom
            self.vel_y = 0
            self.in_air = False
      
      # Check for collision with enemies
      if pygame.sprite.spritecollide(self, slime_group, False):
        game_over = -1
        game_over_fx.play()

      # Check for collision with fire
      if pygame.sprite.spritecollide(self, fire_group, False):
        game_over = -1
        game_over_fx.play()

      # Check for collision with left and right saw
      if pygame.sprite.spritecollide(self, saw_left_group, False):
        game_over = -1
        game_over_fx.play()

      if pygame.sprite.spritecollide(self, saw_right_group, False):
        game_over = -1
        game_over_fx.play()

      # Check for collision with ghost
      if pygame.sprite.spritecollide(self, ghost_group, False):
        game_over = -1
        game_over_fx.play()

      # Check for collision with door
      if pygame.sprite.spritecollide(self, exit_group, False) and coins == 0:
        game_over = 1



      # Check for collision with platform X and Y
      for platform in platform_x_group:
      # Check for collision with platfrom in y direction
        if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
          # Check if above platform
          if abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
            self.rect.bottom = platform.rect.top
            self.in_air = False
            dy = 0
            # Move sideways with the platform
            self.rect.x += platform.move_direction
            
      for platform in platform_y_group:
      # Check for collision with platfrom in y direction
        if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
          # Check if above platform
          if abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
            self.rect.bottom = platform.rect.top
            self.in_air = False
            dy = 0


      # Update player coordinates
      self.rect.x += dx
      self.rect.y += dy

    elif game_over == -1:
      self.counter_dead += 1
      if self.counter_dead > dead_cooldown:
        self.counter_dead = 0
        self.index_dead += 1
      if self.index_dead >= len(self.images_dead):
        self.index_dead = 0
      if self.rect.y > 200:
        self.rect.y -= 5
        self.image = self.images_dead[self.index_dead]
      else:
        self.image = self.images_dead[-1]

    # Draw player onto screen
    window.blit(self.image, self.rect)

    return game_over
  
  def reset(self, x, y):
    self.images_right = []
    self.images_left = []
    self.index = 0
    self.counter = 0

    self.images_right_run = []
    self.images_left_run = []
    self.index_run = 0
    self.counter_run = 0

    self.images_dead = []
    self.index_dead = 0
    self.counter_dead = 0
    self.in_air = True

    # Loading idle sprite animation
    for num in range(1, 12):
      img_right = pygame.image.load(f'Assets/Characters/Mask Dude/Idle/{num}.png')
      img_right = pygame.transform.scale(img_right, (30, 30))
      img_left = pygame.transform.flip(img_right, True, False)
      self.images_right.append(img_right)
      self.images_left.append(img_left)

    # Loading run sprite animation
    for num in range(1, 13):
      img_right_run = pygame.image.load(f'Assets/Characters/Mask Dude/Run/{num}.png')
      img_right_run = pygame.transform.scale(img_right_run, (30, 30))
      img_left_run = pygame.transform.flip(img_right_run, True, False)
      self.images_right_run.append(img_right_run)
      self.images_left_run.append(img_left_run)

    for num in range(1, 8):
      img_dead = pygame.image.load(f'Assets/Characters/Dead/{num}.png')
      img_dead = pygame.transform.scale(img_dead, (30, 30))
      self.images_dead.append(img_dead)

    self.image = self.images_right[self.index]
    self.image_run = self.images_right_run[self.index_run]
    self.image_dead = self.images_dead[self.index_dead]

    self.rect = self.image.get_rect()
    self.rect = self.image_run.get_rect()
    self.rect.x = x
    self.rect.y = y
    self.width = self.image.get_width()
    self.height = self.image.get_height()

    self.vel_y = 0
    self.jumped = False
    self.direction = 0



class World():
  def __init__(self, data):
    self.tile_list = []
    
    # Load images
    dirt_img = pygame.image.load('Assets/Terrain/Dirt.png')
    grass_img = pygame.image.load('Assets/Terrain/Grass.png')

    row_count = 0
    for row in data:
      col_count = 0
      for tile in row: 
        if tile == 1:
          img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
          img_rect = img.get_rect()
          img_rect.x = col_count * tile_size
          img_rect.y = row_count * tile_size
          tile = (img, img_rect)
          self.tile_list.append(tile)
        if tile == 2:
          img = pygame.transform.scale(grass_img, (tile_size, tile_size))
          img_rect = img.get_rect()
          img_rect.x = col_count * tile_size
          img_rect.y = row_count * tile_size
          tile = (img, img_rect)
          self.tile_list.append(tile)
        if tile == 3:
          slime = Slime(col_count * tile_size, row_count * tile_size)
          slime_group.add(slime)
        if tile == 4:
          platform_x = Platform_x(col_count * tile_size, row_count * tile_size)
          platform_x_group.add(platform_x)
        if tile == 5:
          platform_y = Platform_y(col_count * tile_size, row_count * tile_size)
          platform_y_group.add(platform_y)  
        if tile == 6:
          fire = Fire(col_count * tile_size, row_count * tile_size)
          fire_group.add(fire)
        if tile == 7:
          coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
          coin_group.add(coin)
        if tile == 8:
          exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
          exit_group.add(exit)
        if tile == 9:
          saw_left = Saw_left(col_count * tile_size, row_count * tile_size)
          saw_left_group.add(saw_left)
        if tile == 10:
          saw_right = Saw_right(col_count * tile_size + (tile_size * 2), row_count * tile_size - (tile_size))
          saw_right_group.add(saw_right)
        if tile == 11:
          ghost = Ghost(col_count * tile_size, row_count * tile_size)
          ghost_group.add(ghost)
        col_count += 1
      row_count += 1

  def draw(self):
    for tile in self.tile_list:
      window.blit(tile[0], tile[1])

class Slime(pygame.sprite.Sprite):
  def __init__(self, x, y):
    pygame.sprite.Sprite.__init__(self)
    
    self.images_right = []
    self.images_left = []
    self.index = 0
    self.counter = 0

    for num in range(1, 11):
      img_right = pygame.image.load(f'Assets/Enemies/Slime/{num}.png')
      img_right = pygame.transform.scale(img_right, (tile_size, tile_size))
      img_left = pygame.transform.flip(img_right, True, False)
      self.images_right.append(img_right)
      self.images_left.append(img_left)

    self.image = self.images_left[self.index]
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y
    self.move_direction = 1
    self.move_counter = 0

  def update(self):
    idle_cooldown = 10
    
    self.rect.x += self.move_direction
    self.move_counter += 1
    if abs(self.move_counter) > 30:
      self.move_direction *= -1
      self.move_counter *= -1

    self.counter += 1
    if self.counter > idle_cooldown:
      self.counter = 0
      self.index += 1
      if self.index >= len(self.images_right):
        self.index = 0
      if self.move_direction == 1:
        self.image = self.images_left[self.index]
      if self.move_direction == -1:
        self.image = self.images_right[self.index]

class Platform_x(pygame.sprite.Sprite):
  def __init__(self, x, y):
    pygame.sprite.Sprite.__init__(self)
    img = pygame.image.load('Assets/Items/Platform X/1.png')
    self.image = pygame.transform.scale(img, (tile_size, tile_size))
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y
    self.move_direction = 1
    self.move_counter = 0

  def update(self):
    self.rect.x += self.move_direction
    self.move_counter += 1
    if abs(self.move_counter) > 30:
      self.move_direction *= -1
      self.move_counter *= -1

class Platform_y(pygame.sprite.Sprite):
  def __init__(self, x, y):
    pygame.sprite.Sprite.__init__(self)
    img = pygame.image.load('Assets/Items/Platform Y/1.png')
    self.image = pygame.transform.scale(img, (tile_size, tile_size))
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y
    self.move_direction = 1
    self.move_counter = 0

  def update(self):
    self.rect.y += self.move_direction
    self.move_counter += 1
    if abs(self.move_counter) > 30:
      self.move_direction *= -1
      self.move_counter *= -1

class Fire(pygame.sprite.Sprite):
  def __init__(self, x, y):
    pygame.sprite.Sprite.__init__(self)
    
    self.images = []
    self.index = 0
    self.counter = 0

    for num in range(1, 4):
      img = pygame.image.load(f'Assets/Traps/Fire/{num}.png')
      img = pygame.transform.scale(img, (tile_size, tile_size))
      self.images.append(img)

    self.image = self.images[self.index]
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y
       
  def update(self):
    cooldown = 15

    self.counter += 1
    if self.counter > cooldown:
      self.counter = 0
      self.index += 1
      if self.index >= len(self.images):
        self.index = 0
      self.image = self.images[self.index]

class Coin(pygame.sprite.Sprite):
  def __init__(self, x, y):
    pygame.sprite.Sprite.__init__(self)
    img = pygame.image.load("Assets/Items/coin.png")
    self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
    self.rect = self.image.get_rect()
    self.rect.center = (x, y)      
  
class Exit(pygame.sprite.Sprite):
  def __init__(self, x, y):
    pygame.sprite.Sprite.__init__(self)
    img = pygame.image.load("Assets/Items/exit.png")
    self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y

class Saw_left(pygame.sprite.Sprite):
  def __init__(self, x, y):
    pygame.sprite.Sprite.__init__(self)
    
    self.images = []
    self.index = 0
    self.counter = 0

    for num in range(1, 9):
      img = pygame.image.load(f'Assets/Traps/Saw/{num}.png')
      img = pygame.transform.scale(img, (tile_size, tile_size))
      self.images.append(img)

    self.image = self.images[self.index]
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y
    self.move_direction = -2
    self.move_counter = 0
       
  def update(self):
    cooldown = 3

    self.rect.x += self.move_direction
    self.move_counter += 1
    if abs(self.move_counter) > 200:
      self.move_direction *= -1
      self.move_counter *= -1

    self.counter += 1
    if self.counter > cooldown:
      self.counter = 0
      self.index += 1
      if self.index >= len(self.images):
        self.index = 0
      self.image = self.images[self.index]

class Saw_right(pygame.sprite.Sprite):
  def __init__(self, x, y):
    pygame.sprite.Sprite.__init__(self)
    
    self.images = []
    self.index = 0
    self.counter = 0

    for num in range(1, 9):
      img = pygame.image.load(f'Assets/Traps/Saw/{num}.png')
      img = pygame.transform.scale(img, (tile_size, tile_size))
      self.images.append(img)

    self.image = self.images[self.index]
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y
    self.move_direction = 2
    self.move_counter = 0
       
  def update(self):
    cooldown = 3

    self.rect.x += self.move_direction
    self.move_counter += 1
    if abs(self.move_counter) > 200:
      self.move_direction *= -1
      self.move_counter *= -1

    self.counter += 1
    if self.counter > cooldown:
      self.counter = 0
      self.index += 1
      if self.index >= len(self.images):
        self.index = 0
      self.image = self.images[self.index]

class Ghost(pygame.sprite.Sprite):
  def __init__(self, x, y):
    pygame.sprite.Sprite.__init__(self)
    
    self.images_right = []
    self.images_left = []
    self.index = 0
    self.counter = 0

    for num in range(1, 19):
      img_right = pygame.image.load(f'Assets/Enemies/Ghost/{num}.png')
      img_right = pygame.transform.scale(img_right, (tile_size * 2, tile_size * 2))
      img_left = pygame.transform.flip(img_right, True, False)
      self.images_right.append(img_right)
      self.images_left.append(img_left)
    

    self.image = self.images_left[self.index]
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y
    self.move_direction = 1
    self.move_counter = 0

  def update(self):
    idle_cooldown = 8

    self.rect.x += self.move_direction
    self.move_counter += 1
    if abs(self.move_counter) > 300:
      self.move_direction *= -1
      self.move_counter *= -1

    self.counter += 1
    if self.counter > idle_cooldown:
      self.counter = 0
      self.index += 1
      if self.index == 18:
        random_x = random.randint(-WIDTH // 4, WIDTH // 4)
        random_y = random.randint(-HEIGHT // 2, HEIGHT // 2)
        self.rect.x += random_x
        self.rect.y += random_y
        if self.rect.x >= WIDTH - 90 or self.rect.x <= 90:
          self.rect.x = WIDTH // 2
        if self.rect.y >= HEIGHT - 90 or self.rect.y <= 90:
          self.rect.y = HEIGHT // 2
      

      if self.index >= len(self.images_right):
        self.index = 0
      if self.move_direction == 1:
        self.image = self.images_left[self.index]
      if self.move_direction == -1:
        self.image = self.images_right[self.index]
      





player = Player(60, HEIGHT - 60)

slime_group = pygame.sprite.Group()
platform_x_group = pygame.sprite.Group()
platform_y_group = pygame.sprite.Group()
fire_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
saw_left_group = pygame.sprite.Group()
saw_right_group = pygame.sprite.Group()
ghost_group = pygame.sprite.Group()


# Load in level data and create world
if path.exists(f'Levels/level{level}_data'):
  pickle_in = open(f'Levels/level{level}_data', 'rb')
  world_data = pickle.load(pickle_in)
world = World(world_data)


# Create restart button
restart_button = Restart(WIDTH // 2 - 65, HEIGHT // 2 + 60, restart_img)

# Create button
start_button = Button(WIDTH // 2 - 80, HEIGHT // 2 + 120, start_img)
exit_button = Button(WIDTH // 2 - 80, HEIGHT // 2 + 70 + 120, quit_img)

coins = level_coin(level)


# Main Game Loop
run = True
while run:

  clock.tick(fps)
  window.blit(bg_img, (0, 0))

  if main_menu == True:
    window.blit(bg_img2, (0, 0))
    window.blit(title_img, (205, 40))

    # Play the opening music
    if play_music == False and main_menu == True:
      pygame.mixer.music.load(music['title_theme'])
      pygame.mixer.music.set_volume(0.5)
      pygame.mixer.music.play(0, 0.0, 0)
      play_music = True

    # Stop the opening music and proceed to game
    if start_button.draw():
      pygame.mixer.music.stop()
      play_music = False
      main_menu = False
    if exit_button.draw():
      run = False
      
  else:
    world.draw()
    if game_over == 0:
      slime_group.update()
      fire_group.update()
      platform_x_group.update()
      platform_y_group.update()
      saw_left_group.update()
      saw_right_group.update()
      ghost_group.update()

      if pygame.sprite.spritecollide(player, coin_group, True):
        coins -= 1
        coin_fx.play()

      # Music for specific level i.e boss fight
      if level == 5 and play_music == False:
        pygame.mixer.music.load(music['minigame_theme'])
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(0, 0.0, 0)
        play_music = True
      elif level == 9 and play_music == False:
        pygame.mixer.music.load(music['battle_theme'])
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(0, 0.0, 0)
        play_music = True
      elif level == 10 and play_music == False:
        pygame.mixer.music.load(music['final_theme'])
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(0, 0.0, 0)
        play_music = True
      elif level == 11 and play_music == False:
        pygame.mixer.music.load(music['credits_theme'])
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(0, 0.0, 0)
        play_music = True
      elif level != 5 and level != 9 and level != 10 and level != 11:
        play_music = False
        pygame.mixer.music.stop()
      
      # Restart the level prematurely
      key = pygame.key.get_pressed()
      if key[pygame.K_r]:
        world_data = []
        world = reset_level(level)
        game_over = 0

    slime_group.draw(window)
    platform_x_group.draw(window)
    platform_y_group.draw(window)
    fire_group.draw(window)
    exit_group.draw(window)
    coin_group.draw(window)
    saw_left_group.draw(window)
    saw_right_group.draw(window)
    ghost_group.draw(window)

    game_over = player.update(game_over)

    # If player has died
    if game_over == -1:
      coins = level_coin(level)
      if restart_button.draw():
        world_data = []
        world = reset_level(level)
        game_over = 0

    # If player has completed the level
    if game_over == 1:
      # reset game and go to next level
      level += 1
      coins = level_coin(level)
      if level <= max_level:
        # reset level
        world_data = []
        world = reset_level(level)
        game_over = 0
      else:
        # restart the game from the beginning
        if restart_button.draw():
          pygame.mixer.music.stop()
          play_music = False
          main_menu = True          
          level = 0
          world_data = []
          world = reset_level(0)
          coins = level_coin(level)
          game_over = 0


    # Level adjustmentS
    if level == 0:
      draw_text('Press         to move', font_score, white, 100, 500)
      draw_text('Press R to restart', font_score, white, 600, 500)
      draw_text('Press ', font_score, white, 700, 310)
      draw_text('to Jump', font_score, white, 835, 310)
      draw_text('Collect all coins to proceed to the next level', font_score, white, 250, 120)
      draw_tutorial(left_right_img, 170, 495)
      draw_tutorial(space_img, 770, 310)
    elif level >= 1 and level < max_level:
      draw_level(level)
    else:
      draw_image(thank_you_img, 254, 200)
        
  # Handle events
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      run = False

  # Update the display
  pygame.display.update()

pygame.quit()