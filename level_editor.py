import pygame
import pickle
from os import path


pygame.init()

clock = pygame.time.Clock()
fps = 60

#game window
tile_size = 30
cols = 20
margin = 100
WIDTH = tile_size * cols + 420
HEIGHT = (tile_size * cols) + margin

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Level Editor')


#load images
bg_img = pygame.image.load('Assets/Background/Background1.png')
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT - margin))

dirt_img = pygame.image.load('Assets/Terrain/Dirt.png')
grass_img = pygame.image.load('Assets/Terrain/Grass.png')
slime_img = pygame.image.load('Assets/Enemies/Slime/1.png')
platform_x_img = pygame.image.load('Assets/Items/platform_x.png')
platform_y_img = pygame.image.load('Assets/Items/platform_y.png')
fire_img = pygame.image.load('Assets/Traps/Fire/1.png')
coin_img = pygame.image.load('Assets/Items/coin.png')
exit_img = pygame.image.load('Assets/Items/exit.png')
saw_left_img = pygame.image.load('Assets/Traps/Saw/saw_left.png')
saw_right_img = pygame.image.load('Assets/Traps/Saw/saw_right.png')
ghost_img = pygame.image.load('ASsets/Enemies/Ghost/5.png')
save_img = pygame.image.load('Assets/Menu/Buttons/save_btn.png')
load_img = pygame.image.load('Assets/Menu/Buttons/load_btn.png')


#define game variables
clicked = False
level = 0

#define colours
white = (255, 255, 255)
green = (144, 201, 120)

font = pygame.font.SysFont('Futura', 24)

#create empty tile list
world_data = []
for row in range(20):
	r = [0] * 34
	world_data.append(r)

# create horizontal boundary
for tile in range(0, 34):
	world_data[19][tile] = 2
	world_data[0][tile] = 1

# create vertical boundary
for tile in range(0, 20):
	world_data[tile][0] = 1
	world_data[tile][33] = 1


#function for outputting text onto the window
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	window.blit(img, (x, y))

def draw_grid():
	for c in range(35):
		#vertical lines
		pygame.draw.line(window, white, (c * tile_size, 0), (c * tile_size, HEIGHT - margin))
	for c in range(21):
		#horizontal lines
		pygame.draw.line(window, white, (0, c * tile_size), (WIDTH, c * tile_size))


def draw_world():
	for row in range(20):
		for col in range(34):
			if world_data[row][col] > 0:
				if world_data[row][col] == 1:
					#dirt blocks
					img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
					window.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 2:
					#grass blocks
					img = pygame.transform.scale(grass_img, (tile_size, tile_size))
					window.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 3:
					#enemy blocks
					img = pygame.transform.scale(slime_img, (tile_size, tile_size))
					window.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 4:
					#horizontally moving platform
					img = pygame.transform.scale(platform_x_img, (tile_size, tile_size))
					window.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 5:
					#vertically moving platform
					img = pygame.transform.scale(platform_y_img, (tile_size, tile_size))
					window.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 6:
					#fire
					img = pygame.transform.scale(fire_img, (tile_size, tile_size))
					window.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 7:
					#coin
					img = pygame.transform.scale(coin_img, (tile_size // 2, tile_size // 2))
					window.blit(img, (col * tile_size + (tile_size // 4), row * tile_size + (tile_size // 4)))
				if world_data[row][col] == 8:
					#exit door
					img = pygame.transform.scale(exit_img, (tile_size, int(tile_size * 1.5)))
					window.blit(img, (col * tile_size, row * tile_size - (tile_size // 2)))
				if world_data[row][col] == 9:
					# left saw
					img = pygame.transform.scale(saw_left_img, (tile_size, tile_size))
					window.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 10:
					# right saw
					img = pygame.transform.scale(saw_right_img, (tile_size, tile_size))
					window.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 11:
					# ghost
					img = pygame.transform.scale(ghost_img, (tile_size * 2, tile_size * 2))
					window.blit(img, (col * tile_size, row * tile_size))


class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button
		window.blit(self.image, (self.rect.x, self.rect.y))

		return action

#create load and save buttons
save_button = Button(WIDTH // 2 - 150, HEIGHT - 80, save_img)
load_button = Button(WIDTH // 2 + 50, HEIGHT - 80, load_img)

#main game loop
run = True
while run:

	clock.tick(fps)

	#draw background
	window.fill(green)
	window.blit(bg_img, (0, 0))

	#load and save level
	if save_button.draw():
		#save level data
		pickle_out = open(f'Levels/level{level}_data', 'wb')
		pickle.dump(world_data, pickle_out)
		pickle_out.close()
	if load_button.draw():
		#load in level data
		if path.exists(f'Levels/level{level}_data'):
			pickle_in = open(f'Levels/level{level}_data', 'rb')
			world_data = pickle.load(pickle_in)


	#show the grid and draw the level tiles
	draw_grid()
	draw_world()


	#text showing current level
	draw_text(f'Level: {level}', font, white, tile_size, HEIGHT - 60)
	draw_text('Press UP or DOWN to change level', font, white, tile_size, HEIGHT - 40)

	#event handler
	for event in pygame.event.get():
		#quit game
		if event.type == pygame.QUIT:
			run = False
		#mouseclicks to change tiles
		if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
			clicked = True
			pos = pygame.mouse.get_pos()
			x = pos[0] // tile_size
			y = pos[1] // tile_size
			#check that the coordinates are within the tile area
			if x < 34 and y < 20:
				#update tile value
				if pygame.mouse.get_pressed()[0] == 1:
					world_data[y][x] += 1
					if world_data[y][x] > 11:
						world_data[y][x] = 0
				elif pygame.mouse.get_pressed()[2] == 1:
					world_data[y][x] -= 1
					if world_data[y][x] < 0:
						world_data[y][x] = 11
		if event.type == pygame.MOUSEBUTTONUP:
			clicked = False
		#up and down key presses to change level number
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_UP:
				level += 1
			elif event.key == pygame.K_DOWN and level > 0:
				level -= 1

	#update game display window
	pygame.display.update()

pygame.quit()