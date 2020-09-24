from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..Classes.client import Client

from ..Classes.channel import Channel

import logging
Log:logging.Logger = logging.getLogger("twitch_irc")

async def sendMessage(cls:"Client", Chan:Channel or str, content:str):
	"""
	This will send the content/message to a channel. (If you are not timed out, banned or otherwise, that not my fault duh)
	1st arg, `Chan` is the destination, provide a `Channel` object or a string like "the__cj", where you want to send your 2nd arg `content`.

	All IRC Channel-names start with a '#' you don't have to provide this, we will handle everything. ("#the__cj" == "the__cj")
	"""
	if isinstance(Chan, Channel):
		destination:str = Chan.name
	else:
		destination:str = str(Chan)

	destination = destination.lower().strip('#')
	Log.debug(f"Sending: PRIVMSG #{destination} - {content[:50]}")
	await cls.sendContent( f"PRIVMSG #{destination} :{content}\r\n" )

async def joinChannel(cls:"Client", Chan:Channel or str):
	"""
	Joining a channel allows the client to receive messages from this channel.
	`Chan` is the destination, provide a `Channel` object or a string like "the__cj" or "#phaazebot"

	All IRC Channel-names start with a '#' you don't have to provide this, we will handle everything. ("#phaazebot" == "phaazebot")
	"""
	if isinstance(Chan, Channel):
		destination:str = Chan.name
	else:
		destination:str = str(Chan)

	destination = destination.lower().strip('#')
	Log.debug(f"Sending: JOIN #{destination}")
	await cls.sendContent( f"JOIN #{destination}\r\n" )

async def partChannel(cls:"Client", Chan:Channel or str):
	"""
	Parting a channel disables receiving messages from this channel.
	`Chan` may is a `Channel` object or a string like "phaazebot" or "#the__cj"

	All IRC Channel-names start with a '#' you don't have to provide this, we will handle everything. ("#the__cj" == "the__cj")
	"""
	if isinstance(Chan, Channel):
		destination:str = Chan.name
	else:
		destination:str = str(Chan)

	destination = destination.lower().strip('#')
	Log.debug(f"Sending: PART #{destination}")
	await cls.sendContent( f"PART #{destination}\r\n" )
