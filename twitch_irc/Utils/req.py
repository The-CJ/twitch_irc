from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..Classes.client import Client

async def reqMembership(cls:"Client"):
	await cls.sendContent( "CAP REQ :twitch.tv/membership\r\n", ignore_limit=True )

async def reqCommands(cls:"Client"):
	await cls.sendContent( "CAP REQ :twitch.tv/commands\r\n", ignore_limit=True )

async def reqTags(cls:"Client"):
	await cls.sendContent( "CAP REQ :twitch.tv/tags\r\n", ignore_limit=True )
