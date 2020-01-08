import numpy as np 


def check_for_win(grid):
	# check rows
	for i in range(len(grid)):
		if grid[i][0] == grid[i][1] == grid[i][2] and grid[i][0] != 0:
			return True

	# check columns
	for i in range(len(grid[0])):
		if grid[0][i] == grid[1][i] == grid[2][i] and grid[0][i] != 0:
			return True	

	# check diagonals
	if grid[0][0] == grid[1][1] == grid[2][2] and grid[0][0] != 0:
		return True	
	if grid[0][2] == grid[1][1] == grid[2][0] and grid[0][2] != 0:
		return True	

	return False	


def available_positions(grid):
	choices = [[(i,j) for j in range(3) if grid[i][j] == 0] for i in range(3)]
	choices = [item for sublist in choices for item in sublist]
	return choices


#  args ::                    1,      2,
def minmax_ai_next_move(grid, player, opponent):
	results = []
	choices = available_positions(grid)

	if len(choices) == 0: # for complete grid condition
		return False

	for i in choices:
		grid[i[0]][i[1]] = player
		if check_for_win(grid): # win situation
			results.append(1)
		else:
			a = minmax_ai_next_move(grid, opponent, player)
			if a:
				results.append(-a[1]) # -ve because win for opponent is loss for player

		grid[i[0]][i[1]] = 0

	if len(results) == 0:
		results.append(0)
	i = results.index(max(results))
	return choices[i], max(results)


def reinforce_ai_grid(grid, player, opponent):
	g = np.array(grid)
	player_count = np.count_nonzero(g == player)
	opponent_count = np.count_nonzero(g == opponent)
	if player_count == opponent_count:
		g[g == player] = 1
		g[g == opponent] = 2
		next_move = 1
	else: # player_count < opponent_count
		g[g == player] = 2
		g[g == opponent] = 1
		next_move = 2

	return g, next_move





	