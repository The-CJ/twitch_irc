from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..Classes.client import Client

import logging
Log:logging.Logger = logging.getLogger("twitch_irc")

async def sendPong(cls:"Client"):
	"""
	Sends a PONG back to twitch, it also ignores the request limit
	- this should never be called by custom code
	"""
	Log.debug("Sending: PONG")
	await cls.sendContent( "PONG :tmi.twitch.tv\r\n", ignore_limit=True )

async def sendNick(cls:"Client"):
	"""
	Sends a NICK together with the nickname to twitch, it also ignores the request limit
	- this should never be called by custom code
	"""
	Log.debug("Sending: NICK: " + cls.nickname[:10])
	await cls.sendContent( f"NICK {cls.nickname}\r\n", ignore_limit=True )

async def sendPass(cls:"Client"):
	"""
	Sends a PASS together with the token to twitch, it also ignores the request limit
	- this should never be called by custom code
	"""
	Log.debug("Sending: PASS: *****")
	await cls.sendContent( f"PASS {cls.token}\r\n", ignore_limit=True )
