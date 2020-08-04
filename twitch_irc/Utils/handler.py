from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..Classes.client import Client

import asyncio
from ..Classes.channel import Channel
from ..Classes.user import User
from ..Classes.message import Message
from ..Classes.timeout import Timeout, Ban
from .management import updateChannelInfos, updateChannelViewer

async def handleClearChat(cls:"Client", payload:str) -> bool:
	"""
	handles all CLEARCHAT events
	may calls the following events for custom code:
	- onClear(Channel)
	- onTimout(Timout)
	- onBan(Ban)
	"""

	# try getting a timeout class
	Detect:Timeout = Timeout(payload)

	# its a clear event
	if Detect.target_user_id == None:
		Chan:Channel = cls.channels.get(Detect.room_id, None)

		# no channel found, lets make a very minimalistic class, hopefully that never happens
		if not Chan:
			Chan = Channel("")
			Chan.room_id = Detect.room_id

		asyncio.ensure_future( cls.onClear(Chan) )
		return True

	# its actully a ban
	if Detect.duration == None: Detect:Ban = Ban(Detect)

	# get channel where that happens, lets hope, we always get one, because else its dudu
	Chan:Channel = cls.channels.get(Detect.room_id, None)
	if not Chan:
		Chan = Channel("")
		Chan.room_id = Detect.room_id

	# get user that was ban/timeout, lets hope, we always get one, because else its dudu
	FoundUser:User = Chan.users.get(Detect.target_user_id, None)
	if not FoundUser:
		FoundUser = User("", emergency=True)
		FoundUser.user_id = Detect.target_user_id

	Detect.Channel = Chan
	Detect.User = FoundUser

	if type(Detect) is Ban:
		asyncio.ensure_future( cls.onBan(Detect) )
		return True
	else:
		asyncio.ensure_future( cls.onTimeout(Detect) )
		return True

	return False # will never be reached, but why not?

async def handleReRoomState(cls:"Client", payload:str) -> bool:
	"""
	handles all ROOMSTATE events
	may calls the following events for custom code:
	- onChannelUpdate(Channel)
	"""
	Chan:Channel = Channel(payload, emergency=False)
	Chan = updateChannelInfos(cls, Chan)
	asyncio.ensure_future( cls.onChannelUpdate( Chan ) )
	return True

async def handleJoin(cls:"Client", payload:str) -> bool:
	"""
	handles all JOIN events
	because twitch is strange, it may happen that join is called twice,
	without a onLeft before

	may calls the following events for custom code:
	- onMemberJoin(User)

	"""
	JoinUser = User(payload, emergency=True)

	# ignore self
	if JoinUser.name.lower() == cls.nickname.lower():
		return False

	Chan:Channel = cls.getChannel(name=JoinUser.channel_name)
	if Chan:
		JoinUser.Channel = Chan
	updateChannelViewer(cls, JoinUser, add=True)
	asyncio.ensure_future( cls.onMemberJoin( JoinUser ) )
	return True

async def handlePart(cls:"Client", payload:str) -> bool:
	"""
	handles all PART events
	because twitch is strange, it may happen that left is called,
	without a onJoin before

	may calls the following events for custom code:
	- onMemberPart(User)

	"""
	LeftUser:User = User(payload, emergency=True)

	# ignore self
	if LeftUser.name.lower() == cls.nickname.lower():
		return False

	Chan:Channel = cls.getChannel(name=LeftUser.channel_name)
	if Chan:
		LeftUser.Channel = Chan
	updateChannelViewer(cls, LeftUser, rem=True)
	asyncio.ensure_future( cls.onMemberPart( LeftUser ) )
	return True

async def handlePrivMessage(cls:"Client", payload:str) -> bool:
	"""
	handles all PRIVMSG events
	may calls the following events for custom code:
	- onMessage(Message)
	"""

	# generate message
	Msg:Message = Message(payload)

	#get Channel
	Chan:Channel = cls.channels.get(Msg.channel_id, None)
	if Chan:
		Msg.Channel = Chan
	else:
		Msg.Channel = Channel(None, emergency=True, Msg=Msg)

	# get Author
	Author:User = Msg.Channel.users.get(Msg.user_id, None)
	if Author:
		if Author.minimalistic:
			FullAuthor:User = User(None, emergency=False, Msg=Msg)
			Author.update(FullAuthor)

		Author.Channel = Chan
		Msg.Author = Author
	else:
		# get called when the user write a message before twitch tells us the he joined,
		# so we add it to viewer befor we get the join event
		Alternative:User = User(None, emergency=False, Msg=Msg)
		updateChannelViewer(cls, Alternative, add=True)
		Alternative.Channel = Chan
		Msg.Author = Alternative
		asyncio.ensure_future( cls.onMemberJoin(Alternative) )

	asyncio.ensure_future( cls.onMessage(Msg) )
	return True
