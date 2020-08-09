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
	handlePrivMessage, handleClearChat, handleClearMsg,
	handleUserState
)
from ..Utils.regex import (
	RePing, ReWrongAuth, RePrivMessage,
	ReOnReady, ReRoomState,	ReClearChat,
	ReJoin,	RePart, ReGarbage,
	ReClearMsg, ReUserState
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
		await sendPong(cls)
		return True

	# handels events: onMessage
	if re.match(RePrivMessage, payload) != None:
		return await handlePrivMessage(cls, payload)

	# handels events: No
	if re.match(ReUserState, payload) != None:
		return await handleUserState(cls, payload)

	# handels events: onBan, onTimeout, onClearChat
	if re.match(ReClearChat, payload) != None:
		return await handleClearChat(cls, payload)

	# handels events: onChannelUpdate
	if re.match(ReRoomState, payload) != None:
		return await handleRoomState(cls, payload)

	# handels events: onMemberJoin
	if re.match(ReJoin, payload) != None:
		return await handleJoin(cls, payload)

	# handels events: onMemberPart
	if re.match(RePart, payload) != None:
		return await handlePart(cls, payload)

	# handels events: onClearMsg
	if re.match(ReClearMsg, payload) != None:
		return await handleClearMsg(cls, payload)

	# handels events: onReady, onReconnect
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
