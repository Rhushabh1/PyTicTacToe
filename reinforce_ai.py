import numpy as np 
import pickle
# from grid_solver import minmax_ai_next_move


# 2 players = minmax, reinforce
class State:
	def __init__(self, p1, p2):
		self.p1 = p1 # 1
		self.p2 = p2 # 2
		self.boardHash = None
		self.board = np.zeros((3, 3))
		self.endGame = False
		self.playerSymbol = 1 # p1's turn

	def get_hash(self):
		self.boardHash = str(self.board.reshape(-1, 9))
		return self.boardHash

	def available_positions(self):
		positions = [[(i,j) for j in range(3) if self.board[i, j] == 0] for i in range(3)]
		positions = [item for sublist in positions for item in sublist]
		return positions

	def winner(self): # returns symbol of player
		# check rows
		for i in range(3):
			if self.board[i, 0] == self.board[i, 1] == self.board[i, 2] and self.board[i, 0] != 0:
				return self.board[i, 0]
		# check columns
		for i in range(3):
			if self.board[0, i] == self.board[1, i] == self.board[2, i] and self.board[0, i] != 0:
				return self.board[0, i]
		# check diagonals
		if self.board[0, 0] == self.board[1, 1] == self.board[2, 2] and self.board[0, 0] != 0:
			return self.board[0, 0]	
		if self.board[0, 2] == self.board[1, 1] == self.board[2, 0] and self.board[0, 2] != 0:
			return self.board[0, 2]
		# draw
		if len(self.available_positions()) == 0:
			self.endGame = True
			return 0

		self.endGame = False
		return None

	def update_state(self, position):
		self.board[position] = self.playerSymbol
		self.playerSymbol = 2 if self.playerSymbol == 1 else 1

	def give_reward(self):
		result = self.winner()
		if result == 1:
			self.p1.feed_reward(1)
			self.p2.feed_reward(-1)
		elif result == -1:
			self.p1.feed_reward(-1)
			self.p2.feed_reward(1)
		else:
			self.p1.feed_reward(0.1)
			self.p2.feed_reward(0.5)

	def reset(self):
		self.board = np.zeros((3, 3))
		self.endGame = False
		self.boardHash = None
		self.playerSymbol = 1

	def train_play(self, rounds=100, interval=10):
		results = {0:0, 1:0, 2:0}
		for i in range(1, rounds+1):
			if i % interval == 0:
				print("Played {} : 0 -> {}, 1 -> {}, 2 -> {}".format(i, results[0], results[1], results[2]))
				results = {0:0, 1:0, 2:0}
			while not self.endGame:

				# p1's turn
				positions = self.available_positions()
				p1_move = self.p1.choose_action(positions, self.board, self.playerSymbol)
				self.update_state(p1_move)
				self.p1.add_state(self.get_hash())

				win = self.winner()
				if win is not None:
					self.give_reward()
					self.p1.reset()
					self.p2.reset()
					self.reset()
					break

				# p2's turn
				positions = self.available_positions()
				p2_move = self.p2.choose_action(positions, self.board, self.playerSymbol)
				self.update_state(p2_move)
				self.p2.add_state(self.get_hash())			

				win = self.winner()
				if win is not None:
					self.give_reward()
					self.p1.reset()
					self.p2.reset()
					self.reset()
					break

			results[win] += 1

		self.p1.save_policy()
		self.p2.save_policy()

	def test_play(self, rounds=100, interval=10, trace=1):
		results = {0:0, 1:0, 2:0}
		for i in range(1, rounds+1):
			if i % interval == 0:
				print("Played {} : 0 -> {}, 1 -> {}, 2 -> {}".format(i, results[0], results[1], results[2]))
				results = {0:0, 1:0, 2:0}
			while not self.endGame:

				# p1's turn
				positions = self.available_positions()
				p1_move = self.p1.choose_action(positions, self.board, self.playerSymbol)
				self.update_state(p1_move)
				# self.p1.add_state(self.get_hash())

				win = self.winner()
				if win is not None:
					self.give_reward()
					self.p1.reset()
					self.p2.reset()
					self.reset()
					break

				# p2's turn
				positions = self.available_positions()
				p2_move = self.p2.choose_action(positions, self.board, self.playerSymbol)
				self.update_state(p2_move)
				# self.p2.add_state(self.get_hash())

				win = self.winner()
				if win is not None:
					self.give_reward()
					self.p1.reset()
					self.p2.reset()
					self.reset()
					break	

			self.p1, self.p2 = self.p2, self.p1
			if trace == win or win == 0:
				results[win] += 1
			trace = 1 if trace == 2 else 2

		self.p1.save_policy()
		self.p2.save_policy()


class Player:
	def __init__(self, name, exp_rate=0.3):
		self.name = name
		self.states = []
		self.state_values = {}
		self.lr = 0.2 # learning rate
		self.gamma_decay = 0.9 # decay of reward as we go further away from target
		self.exp_rate = exp_rate # exploration rate

	def get_hash(self, board):
		boardHash = str(board.reshape(-1, 9))		
		return boardHash

	def add_state(self, state):
		self.states.append(state)

	def choose_action(self, positions, curr_board, symbol):
		if np.random.uniform(0, 1) <= self.exp_rate:
			i = np.random.choice(len(positions))
			return positions[i]
		else:
			max_value = -99999
			for move in positions:
				next_board = curr_board.copy()
				next_board[move] = symbol
				boardHash = self.get_hash(next_board)
				value = 0 if self.state_values.get(boardHash) is None else self.state_values.get(boardHash)
				if value >= max_value:
					max_value = value
					action = move
			return action

	def feed_reward(self, reward):
		for p in reversed(self.states):
			if self.state_values.get(p) is None:
				self.state_values[p] = 0
			self.state_values[p] += self.lr*(self.gamma_decay*reward - self.state_values[p])
			reward = self.state_values[p]

	def reset(self):
		self.states = []

	def save_policy(self):
		fw = open("my_policy_"+str(self.name), 'wb')
		pickle.dump(self.state_values, fw)
		fw.close()

	def load_policy(self, files):
		for file in files:
			with open(file, 'rb') as fr:
				tmp = pickle.load(fr)
				self.state_values.update(tmp)


class Minmax_Player:
	def __init__(self, name, exp_rate=0.3):
		self.name = name
		self.exp_rate = exp_rate

	def get_hash(self, board):
		pass

	def add_state(self, state):
		pass

	def choose_action(self, positions, curr_board, symbol):
		new_board = curr_board.copy()
		# new_board[new_board == -1] = 2
		new_board = new_board.tolist()
		player = 1 if symbol == 1 else 2
		opponent = 2 if symbol == 1 else 1
		result = minmax_ai_next_move(new_board, player, opponent)
		return result[0]

	def feed_reward(self, reward):
		pass

	def reset(self):
		pass

	def save_policy(self):
		pass

	def load_policy(self, file):
		pass


if __name__ == "__main__":
	# training
	p1 = Player("p1")
	p2 = Player("p2")
	p1.load_policy(["my_policy_p1"])
	p2.load_policy(["my_policy_p2"])
	st = State(p1, p2)
	print("\nTraining")
	st.train_play(100000, 1000)

	# playing against minmax
	# p1 = Minmax_Player("minmax_ai")
	# p2 = Player("reinforce_ai", exp_rate=0)
	# p2.load_policy(["my_policy_p1", "my_policy_p2"])
	# st = State(p1, p2)
	# print("\nTesting against Minmax")
	# st.test_play(500, 10, 2)



