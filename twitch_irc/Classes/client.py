from typing import List, Dict, NewType, Optional, Union
import logging
import time
import asyncio
import traceback

from .message import Message
from .channel import Channel
from .stores import ChannelStore, UserStore
from .user import User
from .timeout import Timeout, Ban
from .sub import Sub, GiftSub
from .resub import ReSub, GiftPaidUpgrade, CommunityPayForward, StandardPayForward, PrimePaidUpgrade
from .mysterygiftsub import MysteryGiftSub
from .reward import Reward
from .ritual import Ritual
from .raid import Raid
from ..Utils.traffic import addTraffic, trafficQuery
from ..Utils.errors import InvalidAuth, PingTimeout, EmptyPayload, InvalidCredentials
from ..Utils.req import reqTags, reqCommands, reqMembership
from ..Utils.cmd import sendNick, sendPass
from ..Utils.detector import mainEventDetector, garbageDetector
from ..Utils.commands import sendMessage, joinChannel, partChannel

Log:logging.Logger = logging.getLogger("twitch_irc")
ChannelName = NewType("ChannelName", str)
UserName = NewType("UserName", str)

class Client(object):
	"""
	Main class for everything.
	Init and call .run()

	Optional Keyword Arguments
	--------------------------
	* `Loop` - asyncio.AbstractEventLoop : (Default: asyncio.get_event_loop()) [Main event loop, used for everything]
	* `reconnect` - bool : (Default: True) [Should the client automatically try to reconnect]
	* `nickname` - str : (Default: None) [User nickname, only lowercase]
	* `token` - str : (Default: None) [User oauth token]
	* `request_limit` - int : (Default: 19)

		* How many requests can be send before the client goes into rate limit protection (request_limit per 60 sec)

			* For normal accounts that's 20/60s
			* 1 channel moderator bots 100/60s
			* Official bots 5000/60s
	"""
	def __init__(self, Loop:Optional[asyncio.AbstractEventLoop]=None, **kwargs):

		# set vars
		self.Loop:asyncio.AbstractEventLoop = asyncio.get_event_loop() if Loop is None else Loop
		self.reconnect:bool = kwargs.get("reconnect", True)
		self.nickname:str = kwargs.get("nickname", None)
		self.token:str = kwargs.get("token", None)
		self.request_limit:int = kwargs.get("request_limit", 19)

		# static* vars
		self.host:str = "irc.chat.twitch.tv"
		self.port:int = 6667

		# runtime vars
		self.running:bool = False
		self.auth_success:bool = False
		self.query_running:bool = False
		self.last_ping:float = time.time()
		self.traffic:int = 0
		self.stored_traffic:List[Union[str, bytes]] = []

		# Connection objects
		self.ConnectionReader:Optional[asyncio.StreamReader] = None
		self.ConnectionWriter:Optional[asyncio.StreamWriter] = None

		self.channels:Dict[ChannelName, Channel] = ChannelStore()
		self.users:Dict[UserName, User] = UserStore()

	def stop(self, *_, **__) -> None:
		"""
		gracefully shuts down the bot, .start() and .run() will be no longer blocking
		"""
		Log.debug(f"Client.stop() has been called, shutting down")
		self.running = False
		self.ConnectionWriter.close()
		self.Loop.stop()

	def run(self) -> None:
		"""
		Blocking call that starts the bot, it will wrap .start() into a coroutine for you.

		### This function is blocking, it only returns after .stop() is called
		"""

		if self.running:
			raise RuntimeError("already running")

		Log.debug(f"Client.run() has been called, wrapping future")
		MainFuture:asyncio.Future = asyncio.ensure_future(self.start(), loop=self.Loop)
		MainFuture.add_done_callback(self.stop)

		try:
			Log.debug(f"Client.run() starting Client.start() future")
			self.Loop.run_forever()
		except KeyboardInterrupt:
			Log.debug(f"Client.run() stopped by KeyboardInterrupt")
		finally:
			# everything where should be run after Client.stop() or when something breaks the Client.Loop

			# Client.stop should be called once, if you break out via exceptions,
			# since Client.stop also called the Loop to stop, we do some cleanup now
			MainFuture.remove_done_callback(self.stop)
			Log.debug(f"Removing MainFuture callback")

			# gather all task of the loop (that will mostly be stuff like: addTraffic())
			Log.debug(f"Collecting all Client.Loop tasks")
			tasks:List[asyncio.Task] = [task for task in asyncio.Task.all_tasks(self.Loop) if not task.done()]
			Log.debug(f"Canceling {len(tasks)} tasks...")
			for task in tasks:
				task.cancel() # set all task to be cancelled

			Log.debug(f"Cancelled all tasks")

			# and now start the loop again, which will result that all tasks are instantly finished and done
			Log.debug(f"Restarting loop to discard tasks")
			self.Loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))

			# then close it... and i dunno, get a coffee or so
			Log.debug(f"All task discarded, closing loop")
			self.Loop.close()

	async def start(self) -> None:
		"""
		Blocking call that starts the bot, this function is a coroutine.

		### This function is blocking, it only returns after .stop() is called

		## Warning!
		This function should be ideally handled via .run()
		because else, there will be no cleanup of futures and task on .stop()
		Which actually is totally ok, but its messy and not really intended.
		If you don't add loop cleanup yourself,
		your console will be flooded by `addTraffic` coroutines waiting to be completed.
		"""
		if self.running:
			raise RuntimeError("already running")

		self.running = True
		self.query_running = True

		if (not self.token) or (not self.nickname):
			raise AttributeError("'token' and 'nickname' must be provided")

		Log.debug(f"Client.start() all required fields found, awaiting Client.main()")
		await self.main()

	async def main(self) -> None:
		"""
		a loop that creates the connections and processes all events
		if self.reconnect is active, it handles critical errors with a restart of the bot
		will run forever until self.stop() is called
		or a critical error without reconnect
		"""
		while self.running:

			# reset bot storage
			self.last_ping = time.time()
			self.traffic = 0
			self.channels = ChannelStore()
			self.users = UserStore()
			self.query_running = True
			self.auth_success = False
			if self.ConnectionWriter:
				self.ConnectionWriter.close()

			# not resetting self.stored_traffic, maybe there is something inside
			Log.debug("Client resettled main attributes")

			try:
				# init connection
				self.ConnectionReader, self.ConnectionWriter = await asyncio.open_connection(host=self.host, port=self.port)
				Log.debug("Client successful create connection Reader/Writer pair")

				# login
				await sendPass(self)
				await sendNick(self)

				# get info's
				await reqMembership(self)
				await reqCommands(self)
				await reqTags(self)

				# start listen
				asyncio.ensure_future(trafficQuery(self))
				Log.debug("Client sent base data, continue to listen for response...")
				await self.listen() # <- that processes stuff

			except InvalidAuth:
				Log.error("Invalid Auth for Twitch, please check `token` and `nickname`, not trying to reconnect")
				self.stop()
				continue

			except InvalidCredentials:
				Log.error("Twitch never send any response, check credentials for syntax, not trying to reconnect")
				self.stop()
				continue

			except EmptyPayload as E:
				Log.error("Empty payload from twitch, trying reconnect")
				await self.onError(E)
				continue

			except PingTimeout as E:
				Log.error("Twitch don't give ping response, trying reconnect")
				await self.onError(E)
				continue

			except KeyboardInterrupt as E:
				await self.onError(E)
				self.stop()
				continue

			except Exception as E:
				await self.onError(E)
				if self.running:
					await asyncio.sleep(5)
				else:
					continue

	async def listen(self) -> None:

		# listen to twitch
		while self.running:

			Log.debug("Client awaiting response...")
			payload:bytes = await self.ConnectionReader.readline()
			Log.debug(f"Client received {len(payload)} bytes of data.")
			asyncio.ensure_future(self.onRaw(payload))
			payload:str = payload.decode('UTF-8').strip('\n').strip('\r')

			# just to be sure
			if payload in ["", " ", None] or not payload:
				if self.auth_success:
					raise EmptyPayload()
				else:
					raise InvalidCredentials()

			# last ping is over 6min (way over twitch normal response)
			if (time.time() - self.last_ping) > 60 * 6:
				raise PingTimeout()

			# check if the content is known garbage
			garbage:bool = await garbageDetector(self, payload)
			if garbage:
				Log.debug("Client got garbage response, launching: Client.onGarbage")
				asyncio.ensure_future(self.onGarbage(payload))
				continue

			# check if there is something usefully we know
			processed:bool = await mainEventDetector(self, payload)
			if not processed:
				Log.debug("Client got unknown response, launching: Client.onUnknown")
				asyncio.ensure_future(self.onUnknown(payload))
				continue

	async def sendContent(self, content:Union[bytes, str], ignore_limit:bool=False) -> None:
		"""
		used to send content of any type to twitch

		default request limit 20 / 30sec | even doh you can send 100 in channel with mod status

		You can change the limit if needed:
		-----------------------------------
		* official bots may use: bot = twitch_irc.Client(request_limit=1000)
		* one channel mod bots: bot = twitch_irc.Client(request_limit=100)

			* others are not recommended

				* even could bring u to a multi hour twitch timeout
		"""
		if type(content) != bytes:
			content = bytes(content, 'UTF-8')

		if (self.traffic <= self.request_limit) or ignore_limit:
			asyncio.ensure_future(addTraffic(self))
			asyncio.ensure_future(self.onSend(content))
			Log.debug(f"Client sending {len(content)} bytes of content to the ConnectionWriter")
			self.ConnectionWriter.write(content)

		else:
			asyncio.ensure_future(self.onLimit(content))
			self.stored_traffic.append(content)

	def getChannel(self, **search) -> Optional[Channel]:
		"""
		get a channel based on the given kwargs,
		returns the first channel all kwargs are valid, or None if 0 valid
		"""
		for channel_name in self.channels:
			Check:Channel = self.channels[channel_name]

			valid:bool = True

			for key in search:
				if getattr(Check, key, object) != search[key]:
					valid = False
					break

			if valid: return Check

		return None

	def getUser(self, **search) -> Optional[User]:
		"""
		get a user based on the given kwargs,
		returns the first user all kwargs are valid, or None if 0 valid
		"""
		for user_name in self.users:
			Check:User = self.users[user_name]

			valid:bool = True

			for key in search:
				if getattr(Check, key, object) != search[key]:
					valid = False
					break

			if valid: return Check

		return None

	# commands
	# u might wonder why im doing this... well my IDE, PyCharm CAN'T FUCKING UNDERSTAND function import's into classes
	# so i wrap it, so the FUCKING TYPECHECKER is not showing errors.
	# For Protocol, yes:
	# from ..Utils.commands import sendMessage
	# Would totally work and does the same, but PyCharm don't get the cls/self Ref in the 1st arg. FUCK
	async def joinChannel(self, Chan:Union[Channel, str]) -> None:
		return await joinChannel(self, Chan)

	async def partChannel(self, Chan:Union[Channel, str]) -> None:
		return await partChannel(self, Chan)

	async def sendMessage(self, Chan:Union[Channel, str], content:str) -> None:
		return await sendMessage(self, Chan, content)

	# events
	# noinspection PyMethodMayBeStatic
	async def onError(self, Ex:BaseException) -> None:
		"""
		called every time something goes wrong
		"""
		Log.error(Ex)
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

	async def onSend(self, raw:bytes) -> None:
		"""
		called every time some bytes of data get send by the client
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

	async def onClearChat(self, Chan:Channel) -> None:
		"""
		called when the a moderator (or other) uses a /clear in a channel
		"""
		pass

	async def onClearMsg(self, Msg:Message) -> None:
		"""
		called when a moderator uses /delete <msg-id>
		which, random fact, close to never happens, because twitch isn't even giving the room-id REEEEEEEEEE
		"""
		pass

	async def onTimeout(self, Time:Timeout) -> None:
		"""
		called when a user get a purge/timeout
		"""
		pass

	async def onBan(self, Ba:Ban) -> None:
		"""
		called when a user gets banned
		Site-note: no there is not unban event
		"""
		pass

	async def onChannelUpdate(self, Chan:Channel, changes:dict) -> None:
		"""
		called when the bot joins a new channel or attributes on a channel are changed like slowmode etc...
		remind that`changes` is empty on initial join
		"""
		pass

	async def onMemberJoin(self, Chan:Channel, Us:User) -> None:
		"""
		called when a user joined a twitch channel
		[ isn't working on channel with more than 1000 user (twitch don't send normal events, only moderator joins) ]
		"""
		pass

	async def onMemberPart(self, Chan:Channel, Us:User) -> None:
		"""
		called when a user left a twitch channel
		[ isn't working on channel with more than 1000 user (twitch don't send normal events, only moderator lefts) ]
		"""
		pass

	async def onSub(self, SubEvent:Sub) -> None:
		"""
		called every time someone subs, has a .Channel and .User object attached to it
		please not that this is only triggered on a first time sub, everything else is a resub (or at least should be)
		"""
		pass

	async def onReSub(self, ReSubEvent:ReSub) -> None:
		"""
		called every time someone resubs, has a .Channel and .User object attached to it

		an alternative of this event may get fired, because twitch hates me
		- onGiftPaidUpgrade
		- onPrimePaidUpgrade
		- onStandardPayForward
		- onCommunityPayForward
		"""
		pass

	async def onGiftPaidUpgrade(self, GiftUpgrade:GiftPaidUpgrade) -> None:
		"""
		called every time someone resubs/upgrades from a gifted sub... yeah that's a extra case,
		has a .Channel .User and a .Gifter object attached to it
		"""
		pass

	async def onPrimePaidUpgrade(self, PrimeUpgrade:PrimePaidUpgrade) -> None:
		"""
		called every time someone resubs/upgrades from a prime sub... yeah that's a extra case,
		has a .Channel .User and a .Gifter object attached to it
		"""
		pass

	async def onStandardPayForward(self, StandardForward:StandardPayForward) -> None:
		"""
		called every time someone gifts to someone who got a gift before... yeah that's a extra case,
		has a .Channel .User a .Gifter and a .Recipient object attached to it
		"""
		pass

	async def onCommunityPayForward(self, CommunityForward:CommunityPayForward) -> None:
		"""
		called every time someone resubs, who got hit by a mass sub before... yeah that's a extra case,
		has a .Channel a .User and a .Prior attached to it
		"""
		pass

	async def onGiftSub(self, GiftSubEvent:GiftSub) -> None:
		"""
		called every time someone gifts a sub to someone, has a .Channel, .Gifter and .Recipient object attached to it
		"""
		pass

	async def onMysteryGiftSub(self, MysteryGiftSubEvent:MysteryGiftSub) -> None:
		"""
		called every time someone gifts sub(s) to random people in chat,
		u may wanna use .mass_gift_count to get the number on how many (.sub_plan) subs have been gifted
		has a .Channel and .Gifter object attached to it

		This event is followed by {MysteryGiftSubEvent.mass_gift_count} of self.onGiftSub
		"""
		pass

	async def onRitual(self, RitualEvent:Ritual) -> None:
		"""
		called every time someone starts any kind of ritual. (rituals are strange)
		has a .Channel and .User object attached to it
		"""
		pass

	async def onRaid(self, RaidEvent:Raid) -> None:
		"""
		called when another channel raids a channel
		has a .Channel and .User object attached to it
		.Channel is the target aka where the bot is in
		.User is the User (and also the channel) who is raiding
		"""
		pass

	async def onReward(self, RewardEvent:Reward) -> None:
		"""
		called every time someone gifts sub(s) to (random) people in chat.
		Twitch will then unlock emotes to random people in chat.
		has a .Channel and .Gifter object attached to it
		"""
		pass

	async def onGarbage(self, raw:str) -> None:
		"""
		called every time some bytes of data are known garbage that is no useful event
		"""
		pass

	async def onUnknown(self, raw:str) -> None:
		"""
		called every time some bytes of data could not be processed to another event
		"""
		pass
