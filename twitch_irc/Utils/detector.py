from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..Classes.client import Client

import re
import time
import asyncio
from ..Utils.cmd import sendPong
from ..Utils.errors import InvalidAuth
from ..Utils.handler import (
	handleChannelUpdate, handleOnMemberJoin, handleOnMemberLeft,
	handleOnMessage
)
from ..Utils.regex import (
	RePing, ReWrongAuth, ReOnMessage,
	ReOnReady, ReRoomState,	ReOnMemberJoin,
	ReOnMemberLeft
)

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

	#onMessage
	if re.match(ReOnMessage, payload) != None:
		await handleOnMessage(cls, payload)
		return True

	#channelUpdate
	if re.match(ReRoomState, payload) != None:
		await handleChannelUpdate(cls, payload)
		return True

	#onMemberJoin
	if re.match(ReOnMemberJoin, payload) != None:
		await handleOnMemberJoin(cls, payload)
		return True

	#onMemberLeft
	if re.match(ReOnMemberLeft, payload) != None:
		await handleOnMemberLeft(cls, payload)
		return True

	#onReady, onReconnect
	if re.match(ReOnReady, payload) != None:
		if cls.auth_success:
			#means we got a reconnect
			asyncio.ensure_future( cls.onReconnect() )
		cls.auth_success = True
		asyncio.ensure_future( cls.onReady() )
		return True

	#wrong_auth
	if not cls.auth_success:
		if re.match(ReWrongAuth, payload) != None:
			raise InvalidAuth( payload )

	return False
