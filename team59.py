import sys
import random
import time
from copy import deepcopy
#replace every 23.97 with 0.95
class Team59():
	def __init__(self):
		self.pos_weight = ((3,2,3),(2,4,2),(3,2,3))
		self.draw_weight = ((4,6,4),(6,3,6),(4,6,4))
		self.big_board_heuristic_store = {}
		self.small_board_heuristic_store = {}
		self.rand_table1 = [[[long(0) for a in range(2)]for b in range(9)]for c in range(9)]#This is the random table that would be used for hashing for board1
		self.rand_table2 = [[[long(0) for a in range(2)]for b in range(9)]for c in range(9)]#This is the random table that would be used for hashing for board2
		self.big_board_hash = long(0) #big_board_hash=big_board_hash1^big_board_hash2
		self.small_board_hash1 = [[long(0) for b in range(3)]for c in range(3)]
		self.small_board_hash2 = [[long(0) for b in range(3)]for c in range(3)]
		self.won_small_board_points = 200
		self.infinity=100000000
		self.curr_time=0
		self.whichBoard=random.randint(1,2)
		self.abhi=0
		patterns = []
		patterns.append( ( (0,0),(1,1),(2,2) ) )
		patterns.append( ( (0,2),(1,1),(2,0) ) )
		for i in range(3):
			row_array = [] # ith row
			col_array = [] # ith column
			for j in range(3):
				row_array.append((i,j))
				col_array.append((j,i))
			patterns.append(tuple(row_array))
			patterns.append(tuple(col_array))
		self.patterns = tuple(patterns)
		self.hash_init()

	def hash_init(self):
		for a in range(9):
			for b in range(9):
				for c in range(2):
						self.rand_table1[a][b][c] = long(random.randint(1,2**64))
						self.rand_table2[a][b][c] = long(random.randint(1,2**64))

	def opp_flag(self,flag):
		if flag == 'o':
			return 'x'
		else:
			return 'o'

	def add_move_to_hash(self,new_move,player):
		b=new_move[0]
		x=new_move[1]
		y=new_move[2]
		if(b==1):
			self.big_board_hash^=self.rand_table1[x][y][player]
			self.small_board_hash1[x/3][y/3]^=self.rand_table1[x][y][player]
		else:
			self.big_board_hash^=self.rand_table2[x][y][player]
			self.small_board_hash2[x/3][y/3]^=self.rand_table2[x][y][player]	

	def small_board_heuristic_func(self,flag,block):
		ret=0
		for pos in self.patterns:
			ret+=self.pattern_checker(flag,block,pos)

		for i in range(3):
			for j in range(3):
				if block[i][j]==flag:
					ret+=0.1*self.pos_weight[i][j]

		return ret

	def pattern_checker(self,flag,block,pos):
		count=0
		counto=0
		for p in pos:
			if block[ p[0] ][ p[1] ] == flag:
				count+=1
			elif block[p[0]][p[1]] ==self.opp_flag(flag):
				counto+=1
		if count==2:
			return 50
		if count==0 and counto==2:
			return 40
		return 0			

	def big_board_pattern_func(self,pos_arr,heur):
		playercount=0
		patternheur=0

		for pos in pos_arr:
			val = heur[pos[0]][pos[1]]
			patternheur+=val
			if val<0:
				return 0 
			elif val == self.won_small_board_points:
				playercount+=1

		if playercount == 2:
			return patternheur*2
		elif playercount == 3:
			return patternheur*1000
		return patternheur
		
	def big_board_heuristic_func(self,blockheur):
		ret=0
		for i in range(3):
			for j in range(3):
				if blockheur[i][j]>0:
					ret+=0.1*self.pos_weight[i][j]*blockheur[i][j]
		return ret

	def heuristic(self,flag,board):
		if (self.big_board_hash,flag) in self.big_board_heuristic_store:
			return self.big_board_heuristic_store[(self.big_board_hash,flag)]

		total = 0
		total1 = 0 #for board 1
		total2 = 0 #for board 2
		smallboard1 = board.small_boards_status[0]
		smallboard2 = board.small_boards_status[0]
		bigboard1 = board.big_boards_status[0]#for board 1
		bigboard2 = board.big_boards_status[1]#for board 2

		small_board1_heuristic = [ [0,0,0], [0,0,0], [0,0,0] ]
		small_board2_heuristic = [ [0,0,0], [0,0,0], [0,0,0] ]

		for i in range(3):
			for j in range(3):
				if smallboard1[i][j]==flag:
					small_board1_heuristic[i][j]=self.won_small_board_points
				elif smallboard1[i][j]==self.opp_flag(flag) or smallboard1[i][j]=='d':
					small_board1_heuristic[i][j]=-1
				else:
					if(self.small_board_hash1[i][j],flag) in self.small_board_heuristic_store:
						small_board1_heuristic[i][j]=self.small_board_heuristic_store[(self.small_board_hash1[i][j],flag)]
					else:
						block = tuple( [ tuple(bigboard1[3*i+x][3*j:3*(j+1)]) for x in range(3) ] )
						small_board1_heuristic[i][j]=self.small_board_heuristic_func(flag,block)
						self.small_board_heuristic_store[(self.small_board_hash1[i][j],flag)]=small_board1_heuristic[i][j]

		for pos_arr in self.patterns:
			total1+= self.big_board_pattern_func(pos_arr,small_board1_heuristic)
		total1+=self.big_board_heuristic_func(small_board1_heuristic)
		self.big_board_heuristic_store[(self.big_board_hash,flag)]=total1

		for i in range(3):
			for j in range(3):
				if smallboard2[i][j]==flag:
					small_board2_heuristic[i][j]=self.won_small_board_points
				elif smallboard2[i][j]==self.opp_flag(flag) or smallboard2[i][j]=='d':
					small_board2_heuristic[i][j]=-1
				else:
					if(self.small_board_hash2[i][j],flag) in self.small_board_heuristic_store:
						small_board2_heuristic[i][j]=self.small_board_heuristic_store[(self.small_board_hash2[i][j],flag)]
					else:
						block = tuple( [ tuple(bigboard2[3*i+x][3*j:3*(j+1)]) for x in range(3) ] )
						small_board2_heuristic[i][j]=self.small_board_heuristic_func(flag,block)
						self.small_board_heuristic_store[(self.small_board_hash2[i][j],flag)]=small_board2_heuristic[i][j]

		for pos_arr in self.patterns:
			total2+= self.big_board_pattern_func(pos_arr,small_board2_heuristic)
		total2+=self.big_board_heuristic_func(small_board2_heuristic)
		self.big_board_heuristic_store[(self.big_board_hash,flag)]=total2

		return (total1+total2)
							

	def minimax(self,board,flag,depth,max_depth,alpha,beta,old_move):
		check_goal = board.find_terminal_state()
		if(check_goal[1]=='WON'):
			if check_goal[0] == self.who:
				return self.infinity,"placeholder"
			else:
				return self.infinity*-1,"placeholder"
		elif check_goal[1]=='DRAW':
			return (self.infinity/10)*-1,"placeholder"

		if depth == max_depth:
			return ( self.heuristic(self.who,board) - self.heuristic(self.opp_flag(self.who),board ) ) , "placeholder"

		valid_cells = board.find_valid_move_cells(old_move)
		is_max = (flag==self.who)
		#if board.big_boards_status[old_move[0]][old_move[1]][old_move[2]] == self.who:
		#	is_max=True
		if is_max:
			max_val = self.infinity*-1
			max_index = 0
			for i in range(len(valid_cells)):
				new_move = valid_cells[i]
				board.update(old_move,new_move,flag)
				self.add_move_to_hash(new_move,1)#means I am playing
				val = self.minimax(board,self.opp_flag(flag),depth+1,max_depth,alpha,beta,new_move)[0]

				if val>max_val:
					max_val=val
					max_index=i

				if max_val>alpha:
					alpha=max_val

				board.big_boards_status[new_move[0]][new_move[1]][new_move[2]]='-'
				board.small_boards_status[new_move[0]][new_move[1]/3][new_move[2]/3]='-'
				self.add_move_to_hash(new_move,1)
				if beta<=alpha:
					break
				if time.time()-self.curr_time >= 23.97:
					return max_val,valid_cells[max_index]
			#print valid_cells[max_index]		
			d = max_val,valid_cells[max_index]					
			return max_val,valid_cells[max_index]
		else:
			min_val = self.infinity
			min_index = 0
			for i in range(len(valid_cells)):
				new_move = valid_cells[i]
				board.update(old_move,new_move,flag)
				self.add_move_to_hash(new_move,0)
				val = self.minimax(board,self.opp_flag(flag),depth+1,max_depth,alpha,beta,new_move)[0]
				if val<min_val:
					min_val = val
				if min_val<beta:
					beta=min_val
				board.big_boards_status[new_move[0]][new_move[1]][new_move[2]]='-'
				board.small_boards_status[new_move[0]][new_move[1]/3][new_move[2]/3]='-'
				self.add_move_to_hash(new_move,0)
				if beta<=alpha:
					break
				if time.time()-self.curr_time >= 23.97:
					return min_val,"placeholder"
			return min_val,"placeholder"	



		
	def move(self,board,old_move,flag):	
		if old_move == (-1,-1,-1):
			self.add_move_to_hash((0,4,4),1)
			return (0,4,4)

		else:
			pass

		if board.big_boards_status[old_move[0]][old_move[1]][old_move[2]] == self.opp_flag(flag):
			self.add_move_to_hash(old_move, 0)
		self.who = 	flag #flag stores whether we are x or 0, it is a character
		depth = 1 #depth for iterative deepening
		valid_cells=board.find_valid_move_cells(old_move)
		best_move = valid_cells[0]
		self.curr_time=time.time()
		while True:
			self.big_board_hash_original=self.big_board_hash
			self.small_board_hash1_original=deepcopy(self.small_board_hash1)
			self.small_board_hash2_original=deepcopy(self.small_board_hash2)
			b = deepcopy(board)
			move = self.minimax(b,flag,0,depth,self.infinity*-1,self.infinity,old_move)[1]
			best_move=move
			depth+=1
			del b
			if time.time()-self.curr_time >= 23.97:
				break

		self.big_board_hash = self.big_board_hash_original
		self.small_board_hash1 = deepcopy(self.small_board_hash1_original)
		self.small_board_hash2 = deepcopy(self.small_board_hash1_original)

		#print best_move[0]#, valid_cells[0]
		return best_move
