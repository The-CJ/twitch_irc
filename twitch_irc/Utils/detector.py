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
	handleUserState, handleUserList, handleUserNotice,
	handleNotice, handleHostTarget
)
from ..Utils.regex import (
	RePing, ReWrongAuth, RePrivMessage,
	ReOnReady, ReRoomState,	ReClearChat,
	ReJoin,	RePart, ReGarbage,
	ReClearMsg, ReUserState, ReUserList,
	ReUserNotice, ReNotice, ReHostTarget
)

async def garbageDetector(_cls:"Client", payload:str) -> bool:
	"""
	This detector is suppose to catch all known patterns that are also known as trash.
	Like this: `:tmi.twitch.tv 002 phaazebot :Your host is tmi.twitch.tv`
	"""
	if re.match(ReGarbage, payload) is not None:
		return True

	return False

async def mainEventDetector(cls:"Client", payload:str) -> bool:
	"""
	This detector is suppose to catch all events we can somehow process, if not, give back False.
	If that happens the Client `cls` makes additional handling
	"""

	# response to PING
	if re.match(RePing, payload) is not None:
		cls.last_ping = time.time()
		await sendPong(cls)
		return True

	# handles events: onMessage
	if re.match(RePrivMessage, payload) is not None:
		return await handlePrivMessage(cls, payload)

	# handles events: None
	if re.match(ReUserState, payload) is not None:
		return await handleUserState(cls, payload)

	# handles events: onBan, onTimeout, onClearChat
	if re.match(ReClearChat, payload) is not None:
		return await handleClearChat(cls, payload)

	# handles events: way to many
	if re.match(ReUserNotice, payload) is not None:
		return await handleUserNotice(cls, payload)

	# handles events: onChannelUpdate
	if re.match(ReRoomState, payload) is not None:
		return await handleRoomState(cls, payload)

	# handles events: onMemberJoin
	if re.match(ReJoin, payload) is not None:
		return await handleJoin(cls, payload)

	# handles events: onMemberPart
	if re.match(RePart, payload) is not None:
		return await handlePart(cls, payload)

	# handles events: onClearMsg
	if re.match(ReClearMsg, payload) is not None:
		return await handleClearMsg(cls, payload)

	# handles events: None
	if re.match(ReUserList, payload) is not None:
		return await handleUserList(cls, payload)

	# handles events: None
	if re.match(ReNotice, payload) is not None:
		return await handleNotice(cls, payload)

	# handles events: None
	if re.match(ReHostTarget, payload) is not None:
		return await handleHostTarget(cls, payload)

	# handles events: onReady, onReconnect
	if re.match(ReOnReady, payload) is not None:
		if cls.auth_success:
			# means we got a reconnect
			asyncio.ensure_future(cls.onReconnect())
		cls.auth_success = True
		asyncio.ensure_future(cls.onReady())
		return True

	# wrong_auth
	if not cls.auth_success:
		if re.match(ReWrongAuth, payload) is not None:
			raise InvalidAuth(payload)

	return False
