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
	Chan:Channel = Channel(payload, emergency=False)
	Chan = updateChannelInfos(cls, Chan)
	asyncio.ensure_future( cls.onChannelUpdate( Chan ) )

async def handleOnMemberJoin(cls:"Client", payload:str) -> None:
	"""
		handles all user joins in a channel,
		calls onMemberJoin(User) for custom user code

		because twitch is strange, it may happen that join is called twice,
		without a onLeft before
	"""
	JoinUser = User(payload, emergency=True)

	# ignore self
	if JoinUser.name.lower() == cls.nickname.lower(): return

	Chan:Channel = cls.getChannel(name=JoinUser.channel_name)
	if Chan:
		JoinUser.Channel = Chan
	updateChannelViewer(cls, JoinUser, add=True)
	asyncio.ensure_future( cls.onMemberJoin( JoinUser ) )

async def handleOnMemberLeft(cls:"Client", payload:str) -> None:
	"""
		handles all user leaves in a channel,
		calls onMemberLeft(User) for custom user code

		because twitch is strange, it may happen that left is called,
		without a onJoin before
	"""
	LeftUser:User = User(payload, emergency=True)

	# ignore self
	if LeftUser.name.lower() == cls.nickname.lower(): return

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
	Author:User = Msg.Channel.getUser(name=Msg.name)
	if Author:
		if Author.minimalistic:
			FullAuthor:User = User(None, emergency=False, Msg=Msg)
			Author.update(FullAuthor)

		Msg.Author = Author
	else:
		# get called when the user write a message before twitch tells us the he joined,
		# so we add it to viewer befor we get the join event
		Alternative:User = User(None, emergency=False, Msg=Msg)
		updateChannelViewer(cls, Alternative, add=True)
		Msg.Author = Alternative
		asyncio.ensure_future( cls.onMemberJoin(Alternative) )

	asyncio.ensure_future( cls.onMessage(Msg) )
