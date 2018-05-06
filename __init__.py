# -*- coding: utf-8 -*-

"""
##################
Twitch IRC wrapper
##################

Simple to use IRC connection for Twitch optimited for the PhaazeOS project
but usable to any purpose

:copyright: (c) 2018-2018 The_CJ
:license: eee dunno, gonna first finish it

"""

import asyncio, time, re

class Client():
	from .utils import send_pong, send_nick, send_pass,	req_membership,	req_commands, req_tags
	from .commands import send_message,	join_channel, part_channel

	from .message import Message

	def __init__(self, token=None, nickname=None):

		self.running = False

		self.token = token
		self.nickname = nickname
		self.host = "irc.twitch.tv"
		self.port = 6667
		self.last_ping = time.time()

		self.connection_reader = None
		self.connection_writer = None
		self.channels = {}

		self.traffic = 0

	def stop(self):
		self.running = False
		self.connection.close()

	def run(self, **kwargs):

		self.token = kwargs.get('token', None)
		self.nickname = kwargs.get('nickname', None)

		if self.token == None or self.nickname == None:
			raise AttributeError("'token' and 'nickname' must be provided")

		loop = asyncio.get_event_loop()
		loop.run_until_complete(self.start())

	async def start(self):
		self.running = True
		self.last_ping = time.time()

		try:
			#init connection
			self.connection_reader, self.connection_writer = await asyncio.open_connection(host=self.host, port=self.port)
			#start listen
			asyncio.ensure_future( self.listen() )
			self.last_ping = time.time()

		except:
			self.connection.close()
			self.last_ping = time.time()
			await asyncio.sleep(10)

		#login
		await self.send_pass()
		await self.send_nick()

		#get infos
		await self.req_membership()
		await self.req_commands()
		await self.req_tags()

		#join main channel
		await self.join_channel(self.nickname)

		await self.send_message(self.nickname, "Jo")

	async def listen(self):

		#listen to twitch
		while self.running:

			payload = await self.connection_reader.readuntil()
			payload = payload.decode('UTF-8')
			print(payload+"\n")


			#just to be sure
			if payload in ["", " ", None]: continue

			#response to PING
			elif re.match(r'^PING', payload) != None:
				self.last_ping = time.time()
				await self.send_pong()

			#we are connected
			elif re.match(r"^:tmi\.twitch\.tv 001.*", payload) != None:
				asyncio.ensure_future( self.on_ready() )

			#on_message
			elif re.match(r'^@.+\.tmi\.twitch\.tv PRIVMSG #.+', payload) != None:
				asyncio.ensure_future( self.on_message( self.Message(payload) ) )

			#on_member_join
			elif re.match(r"^:tmi.+\.twitch\.tv JOIN #.+", payload) != None:
				name = payload.split("!")[1]
				name = name.split("@")[0]

				channel = payload.split("#")[1]

				asyncio.ensure_future( self.BASE.modules._Twitch_.Base.on_member_join(self.BASE, channel, name) )

	#events
	async def on_ready(self):
		print('Connected')

	async def on_message(self, message):
		pass
