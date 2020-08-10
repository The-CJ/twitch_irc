from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..Classes.client import Client

from ..Classes.channel import Channel

import logging
Log:logging.Logger = logging.getLogger("twitch_irc")

async def sendMessage(cls:"Client", Chan:Channel or str, content:str):
	if isinstance(Chan, Channel):
		destination:str = Chan.name
	else:
		destination:str = str(Chan)

	destination = destination.lower().strip('#')
	Log.debug(f"Sending: PRIVMSG #{destination} - {content[:50]}")
	await cls.sendContent( f"PRIVMSG #{destination} :{content}\r\n" )

async def joinChannel(cls:"Client", Chan:Channel or str):
	if isinstance(Chan, Channel):
		destination:str = Chan.name
	else:
		destination:str = str(Chan)

	destination = destination.lower().strip('#')
	Log.debug(f"Sending: JOIN #{destination}")
	await cls.sendContent( f"JOIN #{destination}\r\n" )

async def partChannel(cls:"Client", Chan:Channel or str):
	if isinstance(Chan, Channel):
		destination:str = Chan.name
	else:
		destination:str = str(Chan)

	destination = destination.lower().strip('#')
	Log.debug(f"Sending: PART #{destination}")
	await cls.sendContent( f"PART #{destination}\r\n" )
