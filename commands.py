import asyncio

async def send_message(self, channel, message):
	if self.traffic <= 29:
		self.connection_writer.write(bytes("PRIVMSG #{0} :{1}\r\n".format(channel.lower(), message), 'UTF-8'))
		self.traffic += 1
		await asyncio.sleep(20)
		self.traffic -= 1

async def join_channel(self, channel):
	self.connection_writer.write(bytes("JOIN #{0}\r\n".format(channel.lower()), 'UTF-8'))
	#if not channel.lower() in [c.name for c in self.channels]:
	#	self.channels.append(channel_class(self.BASE, channel))

async def part_channel(self, channel):
	self.connection_writer.write(bytes("PART #{0}\r\n".format(channel.lower()), 'UTF-8'))
	#if channel in [c.name for c in self.channels]:
	#	for c in self.channels:
	#		if c.name.lower() == channel.lower():
	#			self.channels.remove(c)

