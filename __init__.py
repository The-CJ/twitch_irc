# -*- coding: utf-8 -*-

"""
##################
Twitch IRC wrapper
##################

Simple to use IRC connection for Twitch optimited for the PhaazeOS project
but usable to any purpose

:copyright: (c) 2018-2018 The_CJ
:license: MIT License

- Inspired by the code of Rapptz's Discord library (function names and usage)

"""

import asyncio, time, re, traceback

from .regex import Regex

class Client():
	# CAP requests
	from .utils import send_pong, send_nick, send_pass,	req_membership,	req_commands, req_tags

	# update functions
	from .utils import update_channel_infos, update_channel_viewer

	# get functions
	from .utils import get_channel

	# system utils
	from .utils import add_traffic, send_query, send_content

	# event handler
	from .handler import handle_channel_update, handle_on_member_join, handle_on_member_left, handle_on_message

	# commands
	from .commands import send_message,	join_channel, part_channel

	# TODO: Add Subs, resubs, raids and more events

	def __init__(self, token=None, nickname=None):

		self.running = False
		self.query_running = False

		self.token = token
		self.nickname = nickname
		self.host = "irc.twitch.tv"
		self.port = 6667
		self.last_ping = time.time()

		self.connection_reader = None
		self.connection_writer = None
		self.channels = dict()

		self.traffic = 0
		self.stored_traffic = list()

	def stop(self):
		self.running = False
		self.query_running = False
		self.connection_writer.close()

	def run(self, **kwargs):
		self.running = True
		self.query_running = True

		self.token = kwargs.get('token', None)
		self.nickname = kwargs.get('nickname', None)

		if self.token == None or self.nickname == None:
			raise AttributeError("'token' and 'nickname' must be provided")

		loop = asyncio.get_event_loop()
		loop.run_until_complete(self.start())

	async def start(self):

		while self.running:

			#reset bot storage
			self.last_ping = time.time()
			self.traffic = 0
			self.channels = dict()
			# NOTE: not resetting self.stored_traffic | maybe there is something important insite

			try:
				#init connection
				self.connection_reader, self.connection_writer = await asyncio.open_connection(host=self.host, port=self.port)

				#login
				await self.send_pass()
				await self.send_nick()

				#get infos
				await self.req_membership()
				await self.req_commands()
				await self.req_tags()

				#start listen
				self.last_ping = time.time()
				self.query_running = True
				asyncio.ensure_future(self.send_query())
				await self.listen()

			except Exception as e:
				self.connection_writer.close()
				self.query_running = False
				await self.on_error(e)
				await asyncio.sleep(5)

	async def listen(self):

		#listen to twitch
		while self.running:

			payload = await self.connection_reader.readuntil(separator=b'\n')
			asyncio.ensure_future( self.on_raw_data(payload) )
			payload = payload.decode('UTF-8').strip('\n').strip('\r')

			#just to be sure
			if payload in ["", " ", None]: raise ConnectionResetError()

			# last ping is over 6min (way over twitch normal response)
			if (time.time() - self.last_ping) > 60*6: raise ConnectionResetError()

			#response to PING
			elif re.match(Regex.ping, payload) != None:
				self.last_ping = time.time()
				await self.send_pong()

			#on_ready
			elif re.match(Regex.on_ready, payload) != None:
				asyncio.ensure_future( self.on_ready() )

			#channel_update
			elif re.match(Regex.channel_update, payload) != None:
				await self.handle_channel_update(payload)

			#on_member_join
			elif re.match(Regex.on_member_join, payload) != None:
				await self.handle_on_member_join(payload)

			#on_member_left
			elif re.match(Regex.on_member_left, payload) != None:
				await self.handle_on_member_left(payload)

			#on_message
			elif re.match(Regex.on_message, payload) != None:
				await self.handle_on_message(payload)

	#events
	async def on_error(self, exeception):
		"""
		Attributes:
		`exeception`  =  type :: Exeception

		called every time something goes wrong
		"""
		print(exeception)
		traceback.print_exc()

	async def on_limit(self):
		"""
		Attributes:
		None

		called every time a request was not send because it hit the twitch limit,
		the request is stored and send as soon as possible
		"""
		pass

	async def on_raw_data(self, raw):
		"""
		Attributes:
		`raw`  =  type :: bytes

		called every time some bytes of data get received by the client
		"""
		pass

	async def on_ready(self):
		"""
		Attributes:
		None

		called when the client is connected to twitch and is ready to receive or send data
		"""
		pass

	async def on_message(self, message):
		"""
		Attributes:
		`message` = object :: Message

		called when the client received a message in a channel
		"""
		pass

	async def on_channel_update(self, channel):
		"""
		Attributes:
		`channel` = object :: Channel

		called when the bot joines a new channel or attributes on a channel are changed like slowmode etc...
		"""
		pass

	async def on_member_join(self, user):
		"""
		Attributes:
		`user` = object :: User

		called when a user joined a twitch channel
		[ issen't working on channel with more than 1000 user (twitch don't send normal events, only moderator joins) ]
		"""
		pass

	async def on_member_left(self, user):
		"""
		Attributes:
		`user` = object :: User

		called when a user left a twitch channel
		[ issen't working on channel with more than 1000 user (twitch don't send normal events, only moderator lefts) ]
		"""
		pass

