from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..Classes.client import Client

import re
import time
import asyncio
from ..Utils.cmd import sendPong
from ..Utils.errors import InvalidAuth
from ..Utils.handler import (
	handleReRoomState, handleJoin, handlePart,
	handlePrivMessage
)
from ..Utils.regex import (
	RePing, ReWrongAuth, RePrivMessage,
	ReOnReady, ReRoomState,	ReJoin,
	RePart
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
	if re.match(RePrivMessage, payload) != None:
		await handlePrivMessage(cls, payload)
		return True

	#onChannelUpdate
	if re.match(ReRoomState, payload) != None:
		await handleReRoomState(cls, payload)
		return True

	#onMemberJoin
	if re.match(ReJoin, payload) != None:
		await handleJoin(cls, payload)
		return True

	#onMemberPart
	if re.match(RePart, payload) != None:
		await handlePart(cls, payload)
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
