from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..Classes.client import Client

import re
import time
import asyncio
from ..Utils.cmd import sendPong
from ..Utils.errors import InvalidAuth
from ..Utils.handler import (
	handleRoomState, handleJoin, handlePart,
	handlePrivMessage, handleClearChat
)
from ..Utils.regex import (
	RePing, ReWrongAuth, RePrivMessage,
	ReOnReady, ReRoomState,	ReClearChat,
	ReJoin,	RePart, ReGarbage
)

async def garbageDetector(cls:"Client", payload:str) -> bool:
	"""
	This detector is suppost to catch all known patterns that are also known as trash.
	Like this: :tmi.twitch.tv 002 phaazebot :Your host is tmi.twitch.tv
	"""
	if re.match(ReGarbage, payload) != None:
		return True

	return False

async def mainEventDetector(cls:"Client", payload:str) -> bool:
	"""
	This detector is suppost to catch all events we can somehow process, if not, give back False.
	If that happens the Client `cls` makes additional handling
	"""

	#response to PING
	if re.match(RePing, payload) != None:
		cls.last_ping = time.time()
		return await sendPong(cls)

	# onMessage
	if re.match(RePrivMessage, payload) != None:
		return await handlePrivMessage(cls, payload)

	# onBan, onTimeout, onClear
	if re.match(ReClearChat, payload) != None:
		return await handleClearChat(cls, payload)

	# onChannelUpdate
	if re.match(ReRoomState, payload) != None:
		return await handleRoomState(cls, payload)

	# onMemberJoin
	if re.match(ReJoin, payload) != None:
		return await handleJoin(cls, payload)

	# onMemberPart
	if re.match(RePart, payload) != None:
		return await handlePart(cls, payload)

	# onReady, onReconnect
	if re.match(ReOnReady, payload) != None:
		if cls.auth_success:
			#means we got a reconnect
			asyncio.ensure_future( cls.onReconnect() )
		cls.auth_success = True
		asyncio.ensure_future( cls.onReady() )
		return True

	# wrong_auth
	if not cls.auth_success:
		if re.match(ReWrongAuth, payload) != None:
			raise InvalidAuth( payload )

	return False
