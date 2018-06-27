import asyncio

async def send_pong(self):
	self.connection_writer.write(bytes("PONG :tmi.twitch.tv\r\n", 'UTF-8'))

async def send_nick(self):
	self.connection_writer.write(bytes("NICK {0}\r\n".format(self.nickname), 'UTF-8'))

async def send_pass(self):
	self.connection_writer.write(bytes("PASS {0}\r\n".format(self.token), 'UTF-8'))

async def req_membership(self):
	self.connection_writer.write(bytes("CAP REQ :twitch.tv/membership\r\n", 'UTF-8'))

async def req_commands(self):
	self.connection_writer.write(bytes("CAP REQ :twitch.tv/commands\r\n", 'UTF-8'))

async def req_tags(self):
	self.connection_writer.write(bytes("CAP REQ :twitch.tv/tags\r\n", 'UTF-8'))

#

def update_channel_infos(self, channel):
	current_state = self.channels.get( channel.id, None )
	if current_state == None:
		self.channels[channel.id] = channel
		return self.channels[channel.id]

	for key, value in channel.items():
		if value == None: continue
		self.channels[channel.id][key] = value

	return self.channels[channel.id]

def update_channel_viewer(self, user, operation=None):
	if user.channel_name.lower() == self.nickname.lower(): return
	if operation not in ['add', 'rem']:
		raise AttributeError('only supports "add" and "rem"')

	if user.channel != None:
		chan = user.channel
	else:
		chan = self.get_channel(name = user.channel_name)

	if chan == None: return

	if operation == 'add':
		if chan.users.get(user.name, None) != None:
			raise LookupError('user already in users list')
		chan.users[user.name] = user

	if operation == 'rem':
		if chan.users.get(user.name, None) == None:
			raise LookupError('user not in users list')
		chan.users[user.name]


def get_channel(self, **search):
	for chan_id in self.channels:
		chan = self.channels[chan_id]

		for key in search:
			if getattr(chan, key, object) != search[key]:
				continue
		return chan

	return None