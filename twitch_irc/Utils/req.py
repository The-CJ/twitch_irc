from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..Classes.client import Client

import logging
Log:logging.Logger = logging.getLogger("twitch_irc")

async def reqMembership(cls:"Client"):
	"""
	Sends a a request to get full message to twitch, it also ignores the request limit
	- this should never be called by custom code
	"""
	Log.debug("Sending: CAP REQ membership")
	await cls.sendContent("CAP REQ :twitch.tv/membership\r\n", ignore_limit=True)

async def reqCommands(cls:"Client"):
	"""
	Sends a a request to get commands and events from chat to twitch, it also ignores the request limit
	- this should never be called by custom code
	"""
	Log.debug("Sending: CAP REQ commands")
	await cls.sendContent("CAP REQ :twitch.tv/commands\r\n", ignore_limit=True)

async def reqTags(cls:"Client"):
	"""
	Sends a a request to get full message to twitch, it also ignores the request limit
	- this should never be called by custom code
	"""
	Log.debug("Sending: CAP REQ tags")
	await cls.sendContent("CAP REQ :twitch.tv/tags\r\n", ignore_limit=True)
