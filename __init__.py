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

from .message import Message
from .channel import Channel
from .user import User

class Client():
	from .utils import send_pong, send_nick, send_pass,	req_membership,	req_commands, req_tags
	from .utils import update_channel_infos, get_channel, update_channel_viewer, send_content, add_traffic, send_query
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

		self.regex_PING=re.compile(r'^PING')
		self.regex_on_ready=re.compile(r"^:tmi\.twitch\.tv 001.*")
		self.regex_channel_update=re.compile(r"^@.+:tmi\.twitch\.tv ROOMSTATE #.+")
		self.regex_on_member_join=re.compile(r"^.+\.tmi\.twitch\.tv JOIN #.+")
		self.regex_on_member_left=re.compile(r"^.+\.tmi\.twitch\.tv LEFT #.+")
		self.regex_on_message=re.compile(r"^@.+\.tmi\.twitch\.tv PRIVMSG #.+")

	def stop(self):
		self.running = False
		self.query_running = False
		self.connection_reader.close()
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
		self.last_ping = time.time()

		while self.running:

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
				self.connection_reader.close()
				self.query_running = False
				await self.on_error(e)
				await asyncio.sleep(5)

	async def listen(self):

		#listen to twitch
		while self.running:

			payload = await self.connection_reader.readuntil(seperator='\r\n')
			asyncio.ensure_future( self.on_raw_data(payload) )
			payload = payload.decode('UTF-8')

			#just to be sure
			if payload in ["", " ", None]: raise ConnectionResetError()

			# last ping is over 6min (way over twitch normal response)
			if (time.time() - self.last_ping) > 60*6: raise ConnectionResetError()

			#response to PING
			elif re.match(self.regex_PING, payload) != None:
				self.last_ping = time.time()
				await self.send_pong()

			#on_ready
			elif re.match(self.regex_on_ready, payload) != None:
				asyncio.ensure_future( self.on_ready() )

			#channel_update
			elif re.match(self.regex_channel_update, payload) != None:
				chan = Channel(payload)
				chan = self.update_channel_infos(chan)
				asyncio.ensure_future( self.on_channel_update( chan ) )

			#on_member_join
			elif re.match(self.regex_on_member_join, payload) != None:
				user = User(payload)
				c = self.get_channel(name=user.channel_name)
				if c != None:
					user.channel = c
				self.update_channel_viewer(user, 'add')
				asyncio.ensure_future( self.on_member_join( user ) )

			#on_member_left
			elif re.match(self.regex_on_member_left, payload) != None:
				user = User(payload)
				c = self.get_channel(name=user.channel_name)
				if c != None:
					user.channel = c
				self.update_channel_viewer(user, 'rem')
				asyncio.ensure_future( self.on_member_left( user ) )

			#on_message
			elif re.match(self.regex_on_message, payload) != None:
				message = Message(payload)
				c = self.channels.get(message.channel_id, None)
				if c != None:
					message.channel = c

				asyncio.ensure_future( self.on_message( message ) )

	#events
	async def on_error(self, exeception):
		"""
		Attributes:
		`exeception`  =  type :: exeception

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

