import os
import pickle
import random
import pygame
from pygame import mixer
from pygame.locals import *

SIZE = WIDTH , HEIGHT= 1000, 650
tile_size = 50

pygame.font.init()
score_font = pygame.font.SysFont('Bauhaus 93', 30)

WHITE = (255,255,255)
BLUE = (30, 144, 255)

# load sounds
mixer.init()

pygame.mixer.music.load('sounds/Ballad for Olivia.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)

diamond_fx = pygame.mixer.Sound('sounds/341695__projectsu012__coins-1.wav')
diamond_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound('sounds/jump.wav')
jump_fx.set_volume(0.5)
dead_fx = pygame.mixer.Sound('sounds/406113__daleonfire__dead.wav')
dead_fx.set_volume(0.5)
sounds = [diamond_fx, ]


# loading images
dead_img = pygame.image.load('assets/ghost.png')
game_over_img = pygame.image.load('assets/gover.png')
game_over_img = pygame.transform.scale(game_over_img, (300,250))
game_over_rect = game_over_img.get_rect(center=(WIDTH//2, HEIGHT//2 - HEIGHT//6))

# creates background
class World:
	def __init__(self, win, data, groups):
		self.tile_list  = []
		self.win = win
		self.groups = groups

		tiles = []
		for t in sorted(os.listdir('tiles/'), key=lambda s: int(s[:-4])):
			tile = pygame.image.load('tiles/' + t)
			tiles.append(tile)

		row_count = 0
		for row in data:
			col_count = 0
			for col in row:
				if col > 0:
					if col in range(1,14) or col == 18:
						# dirt blocks
						img = pygame.transform.scale(tiles[col-1], (tile_size, tile_size))
						rect = img.get_rect()
						rect.x = col_count * tile_size
						rect.y = row_count * tile_size
						tile = (img, rect)
						self.tile_list.append(tile)

					if col == 14:
						# bush
						bush = Forest('bush',col_count * tile_size, row_count * tile_size + tile_size // 2)
						self.groups[2].add(bush)

					if col == 15:
						# lava
						lava = Fluid('lava_flow', col_count * tile_size, row_count * tile_size + tile_size // 2)
						self.groups[1].add(lava)
					if col == 16:
						lava = Fluid('lava_still', col_count * tile_size, row_count * tile_size)
						self.groups[1].add(lava)
					
					if col == 17:
						# diamond
						diamond = Diamond(col_count * tile_size, row_count * tile_size)
						self.groups[3].add(diamond)
					if col == 19:
						# water block
						water = Fluid('water_flow', col_count * tile_size, row_count * tile_size + tile_size // 2)
						self.groups[1].add(water)
					if col == 20:
						# water block
						water = Fluid('water_still', col_count * tile_size, row_count * tile_size)
						self.groups[1].add(water)
					if col == 21:
						# tree
						tree = Forest('tree', (col_count-1) * tile_size + 10, (row_count-2) * tile_size + 5)
						self.groups[2].add(tree)
					if col == 22:
						# mushroom
						mushroom = Forest('mushroom', col_count * tile_size, row_count * tile_size + tile_size // 4)
						self.groups[2].add(mushroom)
					if col == 23:
						# bee
						bee = Bee(col_count * tile_size, row_count * tile_size)
						self.groups[4].add(bee)
					if col == 24:
						#Gate blocks
						gate = ExitGate(col_count * tile_size - tile_size//4, row_count * tile_size - tile_size//4)
						self.groups[5].add(gate)
					if col == 25:
						#Side moving platform
						platform = MovingPlatform('side', col_count * tile_size, row_count * tile_size)
						self.groups[6].add(platform)
					if col == 26:
						#top moving platform
						platform = MovingPlatform('up', col_count * tile_size, row_count * tile_size)
						self.groups[6].add(platform)
					if col == 27:
						#flower
						flower = Forest('flower', (col_count) * tile_size, row_count * tile_size)
						self.groups[2].add(flower)
					if col == 28:
						# bridge
						bridge = Bridge((col_count-2) * tile_size + 10, row_count * tile_size + tile_size // 4)
						self.groups[7].add(bridge)
					if col == 29:
						#Slime
						slime = Slime(col_count * tile_size - 10, row_count * tile_size + tile_size // 4)
						self.groups[4].add(slime)


				col_count += 1
			row_count += 1

			diamond = Diamond((WIDTH//tile_size - 3) * tile_size, tile_size // 2)
			self.groups[3].add(diamond)

	def draw(self):
		for tile in self.tile_list:
			self.win.blit(tile[0], tile[1])

# -------------------------------------------------------------------------------------------------
#											 Creates Player
class Player:
	def __init__(self, win, pos, world, groups):
		self.reset(win, pos, world, groups)

	def update(self, pressed_keys, game_over, level_won, game_won):
		dx = 0
		dy = 0
		walk_cooldown = 3
		col_threshold = 20


		if not game_over and not game_won:
			if (pressed_keys[K_UP] or pressed_keys[K_SPACE]) and not self.jumped and not self.in_air:
				self.vel_y = -15
				jump_fx.play()
				self.jumped = True
			if (pressed_keys[K_UP] or pressed_keys[K_SPACE]) == False:
				self.jumped = False
			if pressed_keys[K_LEFT]:
				dx -= 5
				self.counter += 1
				self.direction = -1
			if pressed_keys[K_RIGHT]:
				dx += 5
				self.counter += 1
				self.direction = 1

			if pressed_keys[K_LEFT] == False and pressed_keys[K_RIGHT] == False:
				self.counter = 0
				self.index = 0
				self.image = self.img_right[self.index]

				if self.direction == 1:
					self.image = self.img_right[self.index]
				elif self.direction == -1:
					self.image = self.img_left[self.index]

			if self.counter > walk_cooldown:
				self.counter = 0
				self.index += 1
				if self.index >= len(self.img_right):
					self.index = 0

				if self.direction == 1:
					self.image = self.img_right[self.index]
				elif self.direction == -1:
					self.image = self.img_left[self.index]


			# add gravity
			self.vel_y += 1
			if self.vel_y > 10:
				self.vel_y = 10
			dy += self.vel_y

			# check for colision
			self.in_air = True
			for tile in self.world.tile_list:
				# check for collision in x direction
				if tile[1].colliderect(self.rect.x+dx, self.rect.y, self.width, self.height):
					dx = 0
					
				# check for collision in y direction
				if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					# check if below the ground
					if self.vel_y < 0:
						dy = tile[1].bottom - self.rect.top
						self.vel_y = 0
					elif self.vel_y >= 0:
						dy = tile[1].top - self.rect.bottom
						self.vel_y = 0
						self.in_air = False

			if pygame.sprite.spritecollide(self, self.groups[0], False):
				game_over  = True
			if pygame.sprite.spritecollide(self, self.groups[1], False):
				game_over  = True
			if pygame.sprite.spritecollide(self, self.groups[4], False):
				game_over = True

			# temp = self
			# temp = temp.rect.x + 20
			# if pygame.sprite.spritecollide(temp, self.groups[5], False):
			# 	level_won = True
			for gate in self.groups[5]:
				if gate.rect.colliderect(self.rect.x - tile_size//2, self.rect.y, self.width, self.height):
					level_won = True

			if game_over:
				dead_fx.play()

			# check for collision with moving platform
			for platform in self.groups[6]:
				# collision in x direction
				if platform.rect.colliderect(self.rect.x+dx, self.rect.y, self.width, self.height):
					dx = 0

				# collision in y direction
				if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					# check if below platform
					if abs((self.rect.top + dy) - platform.rect.bottom) < col_threshold:
						self.vel_y = 0
						dy = (platform.rect.bottom - self.rect.top)

					# check if above platform
					elif abs((self.rect.bottom + dy) - platform.rect.top) < col_threshold:
						self.rect.bottom = platform.rect.top - 1
						self.in_air = False
						dy = 0
					# move sideways with the platform
					if platform.move_x:
						self.rect.x += platform.move_direction

			for bridge in self.groups[7]:
				# collision in x direction
				if ( bridge.rect.colliderect(self.rect.x+dx, self.rect.y, self.width, self.height) and 
							( bridge.rect.bottom < self.rect.bottom + 5)):
					dx = 0

				# collision in y direction
				if bridge.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					if abs((self.rect.top + dy) - bridge.rect.bottom) < col_threshold:
						self.vel_y = 0
						dy = (bridge.rect.bottom - self.rect.top)

					# check if above platform
					elif abs((self.rect.bottom + dy) - bridge.rect.bottom) < 8:
						self.rect.bottom = bridge.rect.bottom - 12
						self.in_air = False
						dy = 0




			# updating player position
			self.rect.x += dx
			self.rect.y += dy
			# if self.rect.x == self.width:
			# 	self.rect.x = self.width
			if self.rect.x >= WIDTH - self.width:
				self.rect.x = WIDTH - self.width
			if self.rect.x <= 0:
				self.rect.x = 0


		elif game_over:
			self.image = dead_img
			if self.rect.top > 0:
				self.rect.y -= 5

			self.win.blit(game_over_img, game_over_rect)

		# displaying player on window
		self.win.blit(self.image, self.rect)
		# pygame.draw.rect(self.win, (255, 255, 255), self.rect, 1)
	
		return game_over, level_won


