from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..Classes.client import Client

import asyncio
from ..Classes.channel import Channel
from ..Classes.user import User
from ..Classes.message import Message
from .management import updateChannelInfos, updateChannelViewer

async def handleChannelUpdate(cls:"Client", payload:str) -> None:
	"""
		handles all channel update events,
		calls onChannelUpdate(Channel) for custom user code
	"""
	Chan:Channel = Channel(payload, emergency=True)
	Chan = updateChannelInfos(Chan)
	asyncio.ensure_future( cls.onChannelUpdate( Chan ) )

async def handleOnMemberJoin(cls:"Client", payload:str) -> None:
	"""
		handles all user joins in a channel,
		calls onMemberJoin(User) for custom user code
	"""
	JoinUser = User(payload, emergency=True)
	Chan:Channel = cls.getChannel(name=JoinUser.channel_name)
	if Chan:
		JoinUser.Channel = Chan
	updateChannelViewer(cls, JoinUser, add=True)
	asyncio.ensure_future( cls.onMemberJoin( JoinUser ) )

async def handleOnMemberLeft(cls:"Client", payload:str) -> None:
	"""
		handles all user leaves in a channel,
		calls onMemberLeft(User) for custom user code
	"""
	LeftUser:User = User(payload, emergency=True)
	Chan:Channel = cls.getChannel(name=LeftUser.channel_name)
	if Chan:
		LeftUser.Channel = Chan
	updateChannelViewer(cls, LeftUser, rem=True)
	asyncio.ensure_future( cls.onMemberLeft( LeftUser ) )

async def handleOnMessage(cls:"Client", payload:str) -> None:
	"""
		handles all messages
		calls onMessage(Message) for custom user code
	"""

	# generate message
	Msg:Message = Message(payload)

	#get Channel
	Chan = cls.channels.get(Msg.channel_id, None)
	if Chan:
		Msg.Channel = Chan
	else:
		Msg.Channel = Channel(None, emergency=True, Msg=Msg)

	# get Author
	Author:User = Msg.Channel.getUser(id=Msg.user_id)
	if Author:
		if Author.minimalistic:
			FullAuthor:User = User(None, emergency=False, Msg=Msg)
			Author.update(FullAuthor)

		Msg.Author = Author
	else:
		# get called when the user write a message before twitch tells us the he joined,
		# so we add it to viewer befor we get the join event
		Alternative:User = User(payload, emergency=True)
		cls.update_channel_viewer(Alternative, 'add')
		Msg.Author = Alternative

	asyncio.ensure_future( cls.onMessage(Msg) )