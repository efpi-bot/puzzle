import chess
import chess.svg
import discord
import csv
import random
import io
from cairosvg import svg2png


#TU CHESS TESTING


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


	async def send(self):

		svg = chess.svg.board(self.board, size = 350, lastmove = self.move)
		puzzle_png = svg2png(svg)

		data = io.BytesIO(puzzle_png)
		await self.message.channel.send(file=discord.File(data, 'puzzle.png'))

	async def run(self, message):
		self.message = message
		if message.content.startswith('puzzle '):

			content = message.content.replace('puzzle ', '')

			if self.state == 'idle' and content == 'start':

				await self.getRandPuzzle()
				await self.send()

				self.state = 'playing'


			elif self.state == 'playing':

				if content == self.moves[0]:
					await self.doMove()
					if len(self.moves) != 0:
						await self.doMove()
					await self.send()

				elif content == 'cheat':
					await message.channel.send(self.moves[0])

				elif content == 'give up':
					await message.channel.send('przykro mi jestes cipom')
					self.state = 'idle'

				elif content == 'rating':
					await message.channel.send(self.rating)

				else:
					await message.channel.send('to nie jest najlepszy ruch')

				if len(self.moves) == 0:
					await message.channel.send('brawo umiesz w szachy')
					self.state = 'idle'






#TU BOT JUZ JEST
puzzle = puzzle()

client = discord.Client()
KEY = open('key').read()

@client.event
async def on_ready():
	print('[ ! ] READY')

@client.event
async def on_message(message):

	if message.author == client.user:
		return

	await puzzle.run(message)


client.run(KEY)