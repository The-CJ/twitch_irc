import time
import asyncio
import traceback
import re
from .message import Message
from .channel import Channel
from .user import User
from ..Utils.traffic import addTraffic, trafficQuery
from ..Utils.errors import InvalidAuth, PingTimeout, EmptyPayload
from ..Utils.req import reqTags, reqCommands, reqMembership
from ..Utils.cmd import sendNick, sendPass, sendPong
from ..Utils.handler import (
	handleChannelUpdate, handleOnMemberJoin, handleOnMemberLeft,
	handleOnMessage
)
from ..Utils.regex import (
	RePing, ReWrongAuth, ReOnMessage, ReOnReady, ReChannelUpdate,
	ReOnMemberJoin, ReOnMemberLeft
)

class Client():
	"""
		Main class for everything.
		Init and call .run()
	"""
	def __init__(self, token:str=None, nickname:str=None, reconnect:bool=True, request_limit:int=19):

		self.running:bool = False
		self.auth_success:bool = False
		self.query_running:bool = False
		self.reconnect:bool = reconnect

		self.token:str = token
		self.nickname:str = nickname
		self.host:str = "irc.twitch.tv"
		self.port:int = 6667
		self.last_ping:int = time.time()

		self.ConnectionReader:asyncio.StreamReader = None
		self.ConnectionWriter:asyncio.StreamWriter = None
		self.channels:dict = dict()

		self.request_limit:int = request_limit
		self.traffic:int = 0
		self.stored_traffic:list = list()

	def stop(self) -> None:
		self.auth_success = False
		self.running = False
		self.query_running = False
		self.ConnectionWriter.close()

	def run(self, **kwargs:dict) -> None:
		"""
			start the bot, this function will wrap self.start() into a asyncio loop.
			- This function is blocking, it only returns after stop is called
		"""
		loop:asyncio.AbstractEventLoop = asyncio.new_event_loop()
		loop.run_until_complete( self.start(**kwargs) )

	async def start(self, **kwargs:dict) -> None:
		"""
			nearly the same as self.run()
			except its not going to create a loop.
			- This function is blocking, it only returns after stop is called
		"""
		if self.running:
			raise RuntimeError("already running")

		self.running = True
		self.query_running = True

		if not self.token:
			self.token = kwargs.get('token', None)
		if not self.nickname:
			self.nickname = kwargs.get('nickname', None)

		if self.token == None or self.nickname == None:
			raise AttributeError("'token' and 'nickname' must be provided")

		await self.main()

	async def main(self) -> None:
		"""
			a loop that creates the connections a and proceed all events
			if self.reconnect is active, it handles critical errors with a restart of the bot
			will run forever until self.stop() is called
			or a critical error without reconnect
		"""
		while self.running:

			#reset bot storage
			self.last_ping = time.time()
			self.traffic = 0
			self.channels = dict()
			# not resetting self.stored_traffic, maybe there is something inside

			try:
				#init connection
				self.ConnectionReader, self.ConnectionWriter = await asyncio.open_connection(host=self.host, port=self.port)

				#login
				await sendPass(self)
				await sendNick(self)

				#get infos
				await reqMembership(self)
				await reqCommands(self)
				await reqTags(self)

				#reset vars
				self.last_ping = time.time()
				self.query_running = True
				self.auth_success = False

				#start listen
				asyncio.ensure_future( trafficQuery(self) )
				await self.listen()

			except InvalidAuth as E:
				self.stop()
				await self.onError(E)

			except EmptyPayload as E:
				await self.onError(E)
				break

			except PingTimeout as E:
				await self.onError(E)
				break

			except KeyboardInterrupt as E:
				await self.onError(E)
				self.stop()
				break

			except Exception as E:
				await self.onError(E)
				if self.running:
					await asyncio.sleep(5)
				else:
					break

	async def listen(self) -> None:

		#listen to twitch
		while self.running:

			payload:bytes = await self.ConnectionReader.readline()
			asyncio.ensure_future( self.onRaw(payload) )
			payload:str = payload.decode('UTF-8').strip('\n').strip('\r')

			#just to be sure
			if payload in ["", " ", None] or not payload: raise EmptyPayload()

			# last ping is over 6min (way over twitch normal response)
			if (time.time() - self.last_ping) > 60*6:
				raise PingTimeout()

			#onMessage
			elif re.match(ReOnMessage, payload) != None:
				await handleOnMessage(self, payload)

			#response to PING
			elif re.match(RePing, payload) != None:
				self.last_ping = time.time()
				await sendPong(self)

			#channelUpdate
			elif re.match(ReChannelUpdate, payload) != None:
				await handleChannelUpdate(self, payload)

			#onMemberJoin
			elif re.match(ReOnMemberJoin, payload) != None:
				await handleOnMemberJoin(self, payload)

			#onMemberLeft
			elif re.match(ReOnMemberLeft, payload) != None:
				await handleOnMemberLeft(self, payload)

			#onReady, onReconnect
			elif re.match(ReOnReady, payload) != None:
				if self.auth_success:
					#means we got a reconnect
					asyncio.ensure_future( self.onReconnect() )
				self.auth_success = True
				asyncio.ensure_future( self.onReady() )

			#wrong_auth
			elif not self.auth_success:
				if re.match(ReWrongAuth, payload) != None:
					raise InvalidAuth( payload )

	async def sendContent(self, content:bytes or str, ignore_limit:bool=False) -> None:
		"""
			used to send content of any type to twitch

			default request limit 20 / 30sec | even doh you can send 100 in channel with mod status

			You can change the limit if needed:
			- offical bots may use: bot = twitch_irc.Client(request_limit=1000)
			- one channel mod bots: bot = twitch_irc.Client(request_limit=100)
			-- others are not recommended, even could bring u to a multi hour twitch timeout
		"""
		if type(content) != bytes:
			content = bytes(content, 'UTF-8')

		if (self.traffic <= self.request_limit) or ignore_limit:
			asyncio.ensure_future( addTraffic(self) )
			self.ConnectionWriter.write( content )

		else:
			asyncio.ensure_future( self.onLimit(content) )
			self.stored_traffic.append( content )

	def getChannel(self, **search:dict) -> Channel or None:
		"""
			get a channel based on the given kwargs,
			returns the first channel all kwargs are valid, or None if 0 valid
		"""
		for chan_id in self.channels:
			Chan:Channel = self.channels[chan_id]

			valid:bool = True

			for key in search:
				if getattr(Chan, key, object) != search[key]:
					valid = False
					break

			if valid: return Chan

		return None

	# commands
	from ..Utils.commands import sendMessage, joinChannel, partChannel

	#events
	async def onError(self, Ex:Exception) -> None:
		"""
			called every time something goes wrong
		"""
		print(Ex)
		traceback.print_exc()

	async def onLimit(self, payload:bytes) -> None:
		"""
			called every time a request was not send because it hit the twitch limit,
			the request is stored and send as soon as possible
		"""
		pass

	async def onRaw(self, raw:bytes) -> None:
		"""
			called every time some bytes of data get received by the client
		"""
		pass

	async def onReady(self) -> None:
		"""
			called when the client is connected to twitch and is ready to receive or send data
		"""
		pass

	async def onReconnect(self) -> None:
		"""
			called when the client was already connected but was/had to reconnect
			if already connected a onReconnect and onReady fire at the same time
		"""
		pass

	async def onMessage(self, Msg:Message) -> None:
		"""
			called when the client received a message in a channel
		"""
		pass

	async def onChannelUpdate(self, Chan:Channel) -> None:
		"""
			called when the bot joines a new channel or attributes on a channel are changed like slowmode etc...
		"""
		pass

	async def onMemberJoin(self, Us:User) -> None:
		"""
			called when a user joined a twitch channel
			[ issen't working on channel with more than 1000 user (twitch don't send normal events, only moderator joins) ]
		"""
		pass

	async def onMemberLeft(self, Us:User) -> None:
		"""
			called when a user left a twitch channel
			[ issen't working on channel with more than 1000 user (twitch don't send normal events, only moderator lefts) ]
		"""
		pass
