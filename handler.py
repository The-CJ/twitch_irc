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

	message = Message(payload)
	c = self.channels.get(message.channel_id, None)
	# Channel
	if c != None:
		message.channel = c
	else:
		message.channel = Channel(payload, generated_by="message")
	# Author
	u = message.channel.get_user(name=message.name)
	if u != None:
		message.author = u

	asyncio.ensure_future( self.on_message( message ) )

