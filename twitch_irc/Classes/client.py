import time
import asyncio
import traceback
from ..utils import addTraffic, trafficQuery
from ..Utils.errors import InvalidAuth, PingTimeout, EmptyPayload
from ..Utils.req import reqTags, reqCommands, reqMembership
from ..Utils.cmd import sendNick, sendPass, sendPong

class Client():
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

	async def main(self):
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

	async def listen(self):

		#listen to twitch
		while self.running:

			payload = await self.ConnectionReader.readline()
			asyncio.ensure_future( self.on_raw_data(payload) )
			payload = payload.decode('UTF-8').strip('\n').strip('\r')

			#just to be sure
			if payload in ["", " ", None]: raise self.EmptyPayload()

			# last ping is over 6min (way over twitch normal response)
			if (time.time() - self.last_ping) > 60*6: raise self.PingTimeout()

			#response to PING
			elif re.match(Regex.ping, payload) != None:
				self.last_ping = time.time()
				await self.send_pong()

			#wrong_auth
			elif not self.auth_success and re.match(Regex.wrong_auth, payload) != None:
				raise self.InvalidAuth(str(payload))

			#on_ready on_reconnect
			elif re.match(Regex.on_ready, payload) != None:
				if self.auth_success: #means we got a reconnect
					asyncio.ensure_future( self.on_reconnect() )
				self.auth_success = True
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

	async def sendContent(self, content:bytes or str, ignore_limit:bool=False):
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

	#events
	async def onError(self, Ex:Exception):
		"""
			called every time something goes wrong
		"""
		print(Ex)
		traceback.print_exc()

	async def onLimit(self, payload):
		"""
			called every time a request was not send because it hit the twitch limit,
			the request is stored and send as soon as possible
		"""
		pass

	async def onRaw(self, raw:bytes):
		"""
			called every time some bytes of data get received by the client
		"""
		pass

	async def onReady(self):
		"""
			called when the client is connected to twitch and is ready to receive or send data
		"""
		pass

	async def on_reconnect(self):
		"""
			called when the client was already connected but was/had to reconnect
			always called with onReady
		"""
		pass

	async def on_message(self, message):
		"""
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
