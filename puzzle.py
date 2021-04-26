import chess
import chess.svg
import discord
import csv
import random
import io
from cairosvg import svg2png




class puzzle:

	def __init__(self):

		with open('lichess_db_puzzle.csv', newline='') as db_puzzle:
			reader = csv.reader(db_puzzle)

			self.puzzle_list = list(reader)

		self.board = None
		self.moves = []
		self.state = 'idle'
		self.move = None
		self.rating = None
		self.ranking = []

		self.csvRead()


	def csvRead(self):
		with open('ranking.csv', newline='') as f:
			reader = csv.reader(f)
			self.ranking = list(reader)
		for i in self.ranking:
			i[1]=int(i[1])


	def csvWrite(self):
		with open('ranking.csv', 'w') as f:
			writer = csv.writer(f)
			writer.writerows(self.ranking)


	async def getRandPuzzle(self):

		rand_puzzle = random.choice(self.puzzle_list)
		print(rand_puzzle)
		self.board = chess.Board(rand_puzzle[1])
		self.moves = rand_puzzle[2].split(' ')
		self.rating = rand_puzzle[3]

		print(self.moves)

		await self.doMove()

		self.state = 'playing'


	async def doMove(self):

		self.move = chess.Move.from_uci(self.moves[0])
		self.board.push(self.move)
		self.moves.pop(0)

		print(self.moves)


	async def send(self, message):

		svg = chess.svg.board(self.board, size = 350, lastmove = self.move)
		puzzle_png = svg2png(svg)

		data = io.BytesIO(puzzle_png)
		await self.message.channel.send(message, file=discord.File(data, 'puzzle.png'))


	def transferCoins(self, user, amount, add):
		new_user = True
		for i in self.ranking:

			if i[0] == str(user):

				if add == True:
					i[1] += amount
				elif add == False:
					i[1] -= amount

					if i[1] < 1:
						i[1] = 0

				new_user = False
				break

		if new_user == True:
			self.ranking.append([str(user), amount])

		self.csvWrite()

	def getRanking(self):

		embed = discord.Embed(colour=discord.Colour.random())
		self.ranking = sorted(self.ranking,key=lambda l:l[1], reverse=True)
		
		for i in range(len(self.ranking)):
			embed.add_field(name=self.ranking[i][0],value='\ud83e\ude99 '+str(self.ranking[i][1]),inline=False)

		return embed


	async def run(self, message):
		self.message = message
		mention = message.author.mention

		if message.content.startswith('puzzle '):

			content = message.content.replace('puzzle ', '')

			if content == 'top':
				await message.channel.send(embed=self.getRanking())

			elif self.state == 'idle' and content == 'start':

				await self.getRandPuzzle()
				#await message.channel.send('**Wartość: **'+'\ud83e\ude99 '+self.rating)
				await self.send('**Wartość: **'+'\ud83e\ude99 '+self.rating)

				self.state = 'playing'


			elif self.state == 'playing':

				if content == self.moves[0]:
					await self.doMove()
					if len(self.moves) != 0:
						await self.doMove()

					await self.send('To był super ruch \ud83e\udde9')

				# elif content == 'cheat':
				# 	await message.channel.send('||'+self.moves[0]+'||')

				elif content == 'give up':
					await message.channel.send('Przykro mi jestes cipom. (- \ud83e\ude99 '+self.rating+')')
					self.transferCoins(message.author, int(self.rating), False)
					self.state = 'idle'

				elif content == 'rating':
					await message.channel.send(self.rating)

				elif content == 'start':
					#await message.channel.send()
					await self.send('Najpierw skończ te puzzle! (albo sie poddaj)')

				else:
					await message.channel.send('To nie jest najlepszy ruch. (- \ud83e\ude99 500)')
					self.transferCoins(message.author, 500, False)

				if len(self.moves) == 0:
					await message.channel.send(f'Brawo {mention} rozwiązałeś puzzle! (+ \ud83e\ude99 '+self.rating+')')
					self.transferCoins(message.author, int(self.rating), True)
					self.state = 'idle'

			else:
				await message.channel.send('Aby zagrać napisz **puzzle start**.')




#YOUR DISCORD BOT
client = discord.Client()
KEY = open('key').read()

puzzle = puzzle()

@client.event
async def on_ready():
	print('[ ! ] READY')

@client.event
async def on_message(message):

	if message.author == client.user:
		return

	await puzzle.run(message)


client.run(KEY)