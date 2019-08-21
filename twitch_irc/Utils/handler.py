from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..Classes.client import Client

import asyncio
from ..Classes.channel import Channel
from ..Classes.user import User
from ..Classes.message import Message

async def handleChannelUpdate(cls:"Client", payload):
	"""
		handles all channel update events,
		calls onChannelUpdate(Channel) for custom user code
	"""
	chan = Channel(payload, generated_by="event")
	chan = cls.update_channel_infos(chan)
	asyncio.ensure_future( cls.on_channel_update( chan ) )

async def handleOnMemberJoin(cls:"Client", payload):
	"""
		handles all user joins in a channel,
		calls onMemberJoin(User) for custom user code
	"""
	user = User(payload, generated_by="event")
	c = cls.get_channel(name=user.channel_name)
	if c != None:
		user.channel = c
	cls.update_channel_viewer(user, 'add')
	asyncio.ensure_future( cls.on_member_join( user ) )

async def handleOnMemberLeft(cls:"Client", payload):
	"""
		handles all user leaves in a channel,
		calls onMemberLeft(User) for custom user code
	"""
	user = User(payload, generated_by="event")
	c = cls.get_channel(name=user.channel_name)
	if c != None:
		user.channel = c
	cls.update_channel_viewer(user, 'rem')
	asyncio.ensure_future( cls.on_member_left( user ) )

async def handleOnMessage(cls:"Client", payload):
	"""
		handles all messages
		calls onMessage(Message) for custom user code
	"""

	# generate message
	message = Message(payload)

	#get Channel
	c = cls.channels.get(message.channel_id, None)
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
		cls.update_channel_viewer(full_user, 'add')
		message.author = full_user

	asyncio.ensure_future( cls.on_message( message ) )
