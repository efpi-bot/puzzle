import chess
import chess.svg
import discord
import csv
import random
import io
from cairosvg import svg2png
import matplotlib.colors



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
		self.user = ''

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
			self.ranking = sorted(self.ranking,key=lambda l:l[1], reverse=True)
			writer.writerows(self.ranking)



	async def getRandPuzzle(self):

		rand_puzzle = random.choice(self.puzzle_list)
		#print(rand_puzzle)
		self.board = chess.Board(rand_puzzle[1])
		self.moves = rand_puzzle[2].split(' ')
		self.rating = rand_puzzle[3]

		#print(self.moves)

		await self.doMove()

		self.state = 'playing'


	async def doMove(self):

		self.move = chess.Move.from_uci(self.moves[0])
		self.board.push(self.move)
		self.moves.pop(0)

		#print(self.moves)

	async def setUserColors(self, content):

		content = content.split(' ')
		if len(content) != 3:
			await self.message.channel.send('Niepoprawne użycie')
			return
		try:
			colors = {'square light':matplotlib.colors.cnames[content[1]], 'square dark':matplotlib.colors.cnames[content[2]]}	
		except:
			await self.message.channel.send('Niepoprawne kolory')
			return

		for i in self.ranking:
			if self.user == i[0]:
				if i[1] < 10000:
					await self.message.channel.send('Nie masz wystarczającej liczby monet! (\ud83e\ude99 10000)')
					return

				if len(i) != 4:
					i.append(colors['square light'])
					i.append(colors['square dark'])
				else:
					i[2] = colors['square light']
					i[3] = colors['square dark']

				self.transferCoins(self.user, 10000, False)
				await self.message.channel.send('swag (- \ud83e\ude99 10000)')


	def getUserColors(self):

		for i in self.ranking:
			if self.user == i[0]:
				try:
					colors = {'square light':i[2], 'square dark':i[3]}
					return colors
				except:
					return {}
		return {}

	async def sendBoardPreview(self, content):

		content = content.split(' ')
		if len(content) != 3:
			await self.message.channel.send('Niepoprawne użycie')
			return
		try:
			prev_colors = {'square light':matplotlib.colors.cnames[content[1]], 'square dark':matplotlib.colors.cnames[content[2]]}	
		except:
			await self.message.channel.send('Niepoprawne kolory')
			return

		svg = chess.svg.board(chess.BaseBoard(), size = 350, colors=prev_colors)
		puzzle_png = svg2png(svg)

		data = io.BytesIO(puzzle_png)
		await self.message.channel.send(file=discord.File(data, 'preview.png'))


	async def send(self, message):

		svg = chess.svg.board(self.board, size = 350, lastmove = self.move, colors=self.getUserColors())
		puzzle_png = svg2png(svg)

		data = io.BytesIO(puzzle_png)
		await self.message.channel.send(message, file=discord.File(data, 'puzzle.png'))


	def transferCoins(self, user, amount, add):
		new_user = True
		for i in self.ranking:

			if i[0] == user:

				if add == True:
					i[1] += amount
				elif add == False:
					i[1] -= amount

					if i[1] < 1:
						i[1] = 0

				new_user = False
				break

		if new_user == True:
			if add == True:
				self.ranking.append([str(user), amount])
			else:
				self.ranking.append([str(user), 0])

		self.csvWrite()

	def getRanking(self):

		self.csvRead()

		embed = discord.Embed(colour=discord.Colour.random())
		self.ranking = sorted(self.ranking,key=lambda l:l[1], reverse=True)
		
		for i in range(len(self.ranking)):
			embed.add_field(name=self.ranking[i][0],value='\ud83e\ude99 '+str(self.ranking[i][1]),inline=False)

		return embed

	def getScore(self, user):

		self.csvRead()

		embed = discord.Embed(colour=discord.Colour.random())
		for i in range(len(self.ranking)):
			if user == str(self.ranking[i][0]):
				embed.add_field(name=self.ranking[i][0],value='\ud83e\ude99 '+str(self.ranking[i][1]),inline=False)
				break
		return embed


	async def run(self, message):
		self.message = message
		mention = message.author.mention
		self.user = str(message.author)

		if message.content.startswith('puzzle '):

			content = message.content.replace('puzzle ', '')

			if content == 'top':
				await message.channel.send(embed=self.getRanking())

			elif content == 'score':
				await message.channel.send(embed=self.getScore(self.user))

			elif content.startswith('preview'):

				await self.sendBoardPreview(content)

			elif content.startswith('skin'):

				await self.setUserColors(content)

			elif content.startswith('colors'):
				await message.channel.send(file=discord.File('colors.png'))
				
			elif self.state == 'idle' and content == 'start':

				await self.getRandPuzzle()

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
					self.transferCoins(self.user, int(self.rating), False)
					self.state = 'idle'


				elif content == 'start':
					await self.send('Najpierw skończ te puzzle! (albo sie poddaj)')

				elif len(content) == 4:
					await message.channel.send('To nie jest najlepszy ruch. (- \ud83e\ude99 500)')
					self.transferCoins(self.user, 500, False)

				else:
					await message.channel.send('Nie ma takiej komendy, try again.')

				if len(self.moves) == 0:
					await message.channel.send(f'Brawo {mention} rozwiązałeś puzzle! (+ \ud83e\ude99 '+self.rating+')')
					self.transferCoins(self.user, int(self.rating), True)
					self.state = 'idle'

			else:
				await message.channel.send('Aby zagrać napisz **puzzle start**')




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