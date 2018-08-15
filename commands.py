import asyncio
from .channel import Channel as tpl_channel

async def send_message(self, channel, message):
	f = isinstance(channel, tpl_channel)
	if f: channel = channel.name

	channel = channel.lower().strip('#')
	await self.send_content( "PRIVMSG #{0} :{1}\r\n".format(channel, message) )

async def join_channel(self, channel):
	channel = channel.lower().strip('#')
	await self.send_content( "JOIN #{0}\r\n".format(channel) )

async def part_channel(self, channel):
	channel = channel.lower().strip('#')
	await self.send_content( "PART #{0}\r\n".format(channel) )
