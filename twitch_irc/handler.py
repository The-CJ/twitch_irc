import asyncio

from .channel import Channel
from .user import User
from .message import Message

async def handle_channel_update(self, payload):
	"""
	handles all channel update events and calls
	`self.on_channel_update(channel)` for custom user code
	"""
	chan = Channel(payload, generated_by="event")
	chan = self.update_channel_infos(chan)
	asyncio.ensure_future( self.on_channel_update( chan ) )

async def handle_on_member_join(self, payload):
	"""
	handles all user joins in a channel and calls
	`self.on_member_join(user)` for custom user code
	"""
	user = User(payload, generated_by="event")
	c = self.get_channel(name=user.channel_name)
	if c != None:
		user.channel = c
	self.update_channel_viewer(user, 'add')
	asyncio.ensure_future( self.on_member_join( user ) )

async def handle_on_member_left(self, payload):
	"""
	handles all user leaves in a channel and calls
	`self.on_member_left(user)` for custom user code
	"""
	user = User(payload, generated_by="event")
	c = self.get_channel(name=user.channel_name)
	if c != None:
		user.channel = c
	self.update_channel_viewer(user, 'rem')
	asyncio.ensure_future( self.on_member_left( user ) )

async def handle_on_message(self, payload):
	"""
	handles all messages and calls
	`self.on_message(message)` for custom user code
	"""

	# generate message
	message = Message(payload)

	#get Channel
	c = self.channels.get(message.channel_id, None)
	if c != None:
		message.channel = c
	else:
		message.channel = Channel(None, generated_by="message", message=message)

	# get Author
	user = message.channel.get_user(name=message.name)
	if user != None:
		if user.minimalistic:
			full_user = User(message, generated_by="message", message=message)
			user.update(full_user)

		message.author = user
	else:
		# get called when the user write a message befor twitch tells us the he joined, so we add it to viewer befor we get the join event
		full_user = User(message, generated_by="message", message=message)
		self.update_channel_viewer(full_user, 'add')
		message.author = full_user

	asyncio.ensure_future( self.on_message( message ) )

