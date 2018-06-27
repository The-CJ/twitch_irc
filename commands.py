import asyncio

async def send_message(self, channel, message):
	#need to made messages over 29, query to send later
	if self.traffic <= 29:
		self.connection_writer.write(bytes("PRIVMSG #{0} :{1}\r\n".format(channel.lower(), message), 'UTF-8'))
		asyncio.ensure_future(self.add_traffic())

async def add_traffic(self):
		self.traffic += 1
		await asyncio.sleep(20)
		self.traffic -= 1

async def join_channel(self, channel):
	self.connection_writer.write(bytes("JOIN #{0}\r\n".format(channel.lower()), 'UTF-8'))

async def part_channel(self, channel):
	self.connection_writer.write(bytes("PART #{0}\r\n".format(channel.lower()), 'UTF-8'))
