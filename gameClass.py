import pygame
from Colors import *
import time
from grid_solver import *
from reinforce_ai import Player


pygame.font.init()
clock = pygame.time.Clock()
msgs = ["Player 1's Turn", "Player 2's Turn", "Computer's Turn", "Player 1 Won", "Player 2 Won", "Computer Won", "Match Draw"]
AI = "reinforce" # "minmax"


class Game:
	def __init__(self, game_width, game_height):
		self.game_width = game_width
		self.game_height = game_height
		self.player1turn = True
		self.start_with = 1
		self.player1Points = 0
		self.player2Points = 0
		self.round_count = 0
		self.winPoints = 2
		self.drawPoints = 1
		self.gameDisplay = pygame.display.set_mode((game_width, game_height))
		self.opponent = "PLAYER 2" # "COMPUTER"
	
		self.grid_size = int(game_width/3)
		self.ui_xs = [ (2*i+1)*(self.grid_size/2) for i in range(3)]
		self.ui_ys = [ game_width + i*(game_height-game_width)/5 for i in range(1, 5)]
		self.ui_ys[2] -= 20
		self.msg = msgs[0]

	def initialise_game(self):
		self.grid = [[0 for _ in range(3)] for _ in range(3)]
		self.ui_xs = [int(x) for x in self.ui_xs]
		self.ui_ys = [int(x) for x in self.ui_ys]
		self.halt = False
		if self.start_with == 1:
			self.player1turn = True
			self.msg = msgs[0]
			self.start_with = 2
		else:
			self.player1turn = False
			self.msg = msgs[1]
			self.start_with = 1
		self.round_count = 0

	def reset_game(self):
		self.player1Points = 0
		self.player2Points = 0
		self.grid = [[0 for _ in range(3)] for _ in range(3)]

	def set_player_opponent(self):
		self.reset_game()
		self.opponent = "PLAYER 2"

	def set_computer_opponent(self):
		self.reset_game()
		self.opponent = "COMPUTER"


class Button:
	def __init__(self, msg, x, y, w, h, inactive_color, active_color, text_color, action=None):
		self.msg = msg
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.inactive_color = inactive_color
		self.active_color = active_color
		self.text_color = text_color
		self.action = action

	def display_button(self, game):
		mouse = pygame.mouse.get_pos()
		click = pygame.mouse.get_pressed()

		if self.x+self.w>mouse[0]>self.x and self.y+self.h>mouse[1]>self.y:
			pygame.draw.rect(game.gameDisplay, self.active_color, (self.x, self.y, self.w, self.h))
			if click[0]==1 and self.action!=None:
				self.action()
		else:
			pygame.draw.rect(game.gameDisplay, self.inactive_color, (self.x, self.y, self.w, self.h))

		smalltext = pygame.font.SysFont("comicsansms",20)
		textSurf, textRect = text_objects(self.msg, smalltext, self.text_color)
		textRect.center = (self.x+(self.w/2), self.y+(self.h/2) )
		game.gameDisplay.blit(textSurf, textRect)	


def text_objects(msg, font, text_color):
	textSurf = font.render(msg, True, text_color)
	return textSurf, textSurf.get_rect()


# score and buttons
def display_ui(game, msg, scores, buttons):
	myfont = pygame.font.SysFont('Segoe UI', 20, True)
	bigfont = pygame.font.SysFont('Segoe UI', 40, True)
	# display msg
	text_msg = bigfont.render(msg, True, black[1])
	text_player = myfont.render("PLAYER 1", True, black[1])
	text_opponent = myfont.render(game.opponent, True, black[1])
	text_score = myfont.render("SCORE : ", True, black[1])
	score_p1 = myfont.render(str(game.player1Points), True, black[1])
	score_p2 = myfont.render(str(game.player2Points), True, black[1])

	game.gameDisplay.blit(text_msg, (game.ui_xs[0]-30, game.ui_ys[0]-10))
	game.gameDisplay.blit(text_player, (game.ui_xs[1]-30, game.ui_ys[1]))
	game.gameDisplay.blit(text_opponent, (game.ui_xs[2]-30, game.ui_ys[1]))
	game.gameDisplay.blit(text_score, (game.ui_xs[0]-30, game.ui_ys[2]))
	game.gameDisplay.blit(score_p1, (game.ui_xs[1], game.ui_ys[2]))
	game.gameDisplay.blit(score_p2, (game.ui_xs[2], game.ui_ys[2]))

	# display buttons
	for button in buttons:
		button.display_button(game)


def draw_cross(game, center, s):
	size = s-80
	pygame.draw.line(game.gameDisplay, red[1], (center[0]-size/2, center[1]-size/2), (center[0]+size/2, center[1]+size/2), int(size*0.15) )
	pygame.draw.line(game.gameDisplay, red[1], (center[0]-size/2, center[1]+size/2), (center[0]+size/2, center[1]-size/2), int(size*0.15) )


def draw_circle(game, center, radius):
	pygame.draw.circle(game.gameDisplay, blue[1], (int(center[0]), int(center[1])), 60, 10 )


# everything on gameDisplay
def display(game, msg, buttons):
	game.gameDisplay.fill(white[1])

	display_ui(game, msg, (game.player1Points, game.player1Points), buttons)
	pygame.draw.line(game.gameDisplay, gray[1], (0, game.game_width), (game.game_width, game.game_width), 2)

	# draw grid lines
	pygame.draw.line(game.gameDisplay, gray[1], (game.grid_size, 0+30), (game.grid_size, game.game_width-30), 6)
	pygame.draw.line(game.gameDisplay, gray[1], (game.grid_size*2, 0+30), (game.grid_size*2, game.game_width-30), 6)

	pygame.draw.line(game.gameDisplay, gray[1], (0+30, game.grid_size), (game.game_width-30, game.grid_size), 6)
	pygame.draw.line(game.gameDisplay, gray[1], (0+30, game.grid_size*2), (game.game_width-30, game.grid_size*2), 6)	

	# draw symbols
	for i in range(3): # i row - along y
		for j in range(3): # j column - along x
			if game.grid[i][j] == 1:
				draw_cross(game, ((2*j+1)*game.grid_size/2, (2*i+1)*game.grid_size/2), game.grid_size)
			elif game.grid[i][j] == 2:
				draw_circle(game, ((2*j+1)*game.grid_size/2, (2*i+1)*game.grid_size/2), game.grid_size/2)

	pygame.display.update()


def quitGame():
	pygame.quit()
	quit()


def evaluator(game):
	if check_for_win(game.grid):
		if game.player1turn:                         # player 1 won
			game.player1Points += game.winPoints
			game.msg = msgs[3]
			winner = 1
		elif game.opponent == "PLAYER 2":            # player 2 won
			game.player2Points += game.winPoints
			game.msg = msgs[4]
			winner = 2
		else:                                        # computer won
			game.player2Points += game.winPoints
			game.msg = msgs[5]
			winner = 2
		game.halt = True
	elif game.round_count == 9:                      # game draw
		game.player1Points += game.drawPoints
		game.player2Points += game.drawPoints
		game.msg = msgs[6]
		game.halt = True
		winner = 0
	else:
		winner = None
		game.player1turn = not game.player1turn
		if game.player1turn:
			game.msg = msgs[0]
		elif game.opponent == "PLAYER 2":
			game.msg = msgs[1]
		else:
			game.msg = msgs[2]

	return winner


def run():
	pygame.init()
	game = Game(600, 800)
	game.initialise_game()
	# msg, x, y, w, h, inactive_color, active_color, text_color, action=None
	reset_button = Button("RESET", game.ui_xs[0]-50, game.ui_ys[3]-15, 100, 30, peru[1], burly_wood[1], black[1], game.reset_game)
	player2_button = Button("2 PLAYER", game.ui_xs[1]-50, game.ui_ys[3]-15, 100, 30, peru[1], burly_wood[1], black[1], game.set_player_opponent)
	computer_button = Button("COMPUTER", game.ui_xs[2]-50, game.ui_ys[3]-15, 100, 30, peru[1], burly_wood[1], black[1], game.set_computer_opponent)

	# AI class
	ai = Player("reinforce_ai", exp_rate=0.1)
	ai.load_policy(["my_policy_p1", "my_policy_p2"])

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				if AI == "reinforce":
					ai.save_policy()
				quitGame()

		if not game.player1turn and game.opponent == "COMPUTER":
			if AI == "reinforce":
				npgrid, next_symbol = reinforce_ai_grid(game.grid, 2, 1)
				positions = [[(i,j) for j in range(3) if game.grid[i][j] == 0] for i in range(3)]
				positions = [item for sublist in positions for item in sublist]
				move = ai.choose_action(positions, npgrid, 2)
				npgrid[move] = next_symbol
				ai.add_state(ai.get_hash(npgrid))

			elif AI == "minmax":
				move, result = minmax_ai_next_move(game.grid, 2, 1)

			game.grid[move[0]][move[1]] = 2
			game.round_count += 1
			winner = evaluator(game)

			if AI == "reinforce":
				if winner is not None:
					if winner == 0:
						ai.feed_reward(0.2)
					elif winner == 1:
						ai.feed_reward(-1)
					elif winner == 2:
						ai.feed_reward(1)
					ai.reset()

		else:
			mouse = pygame.mouse.get_pos()
			click = pygame.mouse.get_pressed()

			if click[0] == 1:
				box_x = int(mouse[1]//game.grid_size) # y comes along rows
				box_y = int(mouse[0]//game.grid_size) # x comes along columns
				if box_x<3 and box_y<3 and game.grid[box_x][box_y] == 0:
					if game.player1turn:
						game.grid[box_x][box_y] = 1
					else:
						game.grid[box_x][box_y] = 2
					game.round_count += 1
					# print(box_x, box_y, game.grid)
					evaluator(game)

		display(game, game.msg, [reset_button, player2_button, computer_button])
		if game.halt:
			# print("halt now")
			time.sleep(5)
			game.initialise_game()
		clock.tick(60)


run()

