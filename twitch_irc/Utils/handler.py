from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..Classes.client import Client

import re
import asyncio
from ..Classes.channel import Channel
from ..Classes.user import User
from ..Classes.message import Message
from ..Classes.timeout import Timeout, Ban

ReRoomName:"re.Pattern" = re.compile(r"[; ](JOIN|PART) #(\w*)")

async def handleClearChat(cls:"Client", payload:str) -> bool:
	"""
	handles all CLEARCHAT events

	may calls the following events for custom code:
	- onClearChat(Channel)
	- onTimout(Timout)
	- onBan(Ban)
	"""

	# try getting a timeout class
	Detect:Timeout = Timeout(payload)

	# its a clear event
	if not Detect.target_user_id:
		Chan:Channel = cls.channels.get(Detect.room_id, None)

		# no channel found, lets make a very minimalistic class, hopefully that never happens
		if not Chan:
			Chan = Channel("")
			Chan._room_id = Detect.room_id

		asyncio.ensure_future( cls.onClearChat(Chan) )
		return True

	# its actully a ban
	if Detect.duration == 0: Detect:Ban = Ban(Detect)

	# get channel where that happens, lets hope, we always get one, because else its dudu
	Chan:Channel = cls.channels.get(Detect.room_id, None)
	if not Chan:
		Chan = Channel("")
		Chan._room_id = Detect.room_id

	# get user that was ban/timeout, lets hope, we always get one, because else its dudu
	FoundUser:User = Chan.users.get(Detect.target_user_id, None)
	if not FoundUser:
		FoundUser = User("", emergency=True)
		FoundUser._user_id = Detect.target_user_id

	Detect.Channel = Chan
	Detect.User = FoundUser

	if type(Detect) is Ban:
		asyncio.ensure_future( cls.onBan(Detect) )
		return True
	else:
		asyncio.ensure_future( cls.onTimeout(Detect) )
		return True

	return False # will never be reached, but why not?

async def handleClearMsg(cls:"Client", payload:str) -> bool:
	"""
	handles all CLEARMSG events
	whitch... well near to never happend but whatever

	may calls the following events for custom code:
	- onClearMsg(Message)
	"""

	# lets try making a message of it...
	Deleted:Message = Message(payload)
	print(Deleted)
	print(vars(Deleted))

	# @login=the__cj;room-id=;target-msg-id=00960179-587a-496a-b5e5-1be4a166b7ad;tmi-sent-ts=1596558673781 :tmi.twitch.tv CLEARMSG #phaazebot :id

async def handlePrivMessage(cls:"Client", payload:str) -> bool:
	"""
	handles all PRIVMSG events

	may calls the following events for custom code:
	- onMessage(Message)
	"""

	# generate message
	Msg:Message = Message(payload)

	#get Channel
	Chan:Channel = cls.channels.get(Msg.room_id, None)
	if Chan:
		Msg.Channel = Chan
	else:
		# should never happen, but ok
		NewChan:Channel = Channel(None, emergency=True, Msg=Msg)
		cls.channels[NewChan.room_id] = NewChan
		Msg.Channel = NewChan
		Chan = NewChan
		del NewChan

	# get Author
	Author:User = cls.users.get(Msg.user_name, None)
	if Author:
		if Author.minimalistic:
			FullAuthor:User = User(None, emergency=False, Msg=Msg)
			Author.update(FullAuthor)

		Msg.Author = Author
	else:
		# get called when the user write a message before twitch tells us the he joined,
		# so we add it to viewer befor we get the join event
		Alternative:User = User(None, emergency=False, Msg=Msg)

		# add new user to client's user dict
		cls.users[Alternative.name] = Alternative

		Msg.Author = Alternative
		asyncio.ensure_future( cls.onMemberJoin(Chan, Alternative) )

	# safty step, add author to channels viewer list, and channel to viewer
	Msg.Channel.viewers[Msg.Author.name] = Msg.Author
	Msg.Author.found_in.add(Msg.Channel.room_id)

	asyncio.ensure_future( cls.onMessage(Msg) )
	return True

async def handleRoomState(cls:"Client", payload:str) -> bool:
	"""
	handles all ROOMSTATE events

	may calls the following events for custom code:
	- onChannelUpdate(Channel, changes)
	"""
	ChannelUpdate:Channel = Channel(payload, emergency=False)
	CurrentChannel:Channel = cls.channels.get(ChannelUpdate.room_id, None)

	# should never happen, except on the initial join event
	if not CurrentChannel:
		cls.channels[ChannelUpdate.room_id] = ChannelUpdate
		asyncio.ensure_future( cls.onChannelUpdate(ChannelUpdate, {}) )
		return True

	changes:dict = CurrentChannel.update(ChannelUpdate)
	asyncio.ensure_future( cls.onChannelUpdate(CurrentChannel, changes) )
	return True

async def handleJoin(cls:"Client", payload:str) -> bool:
	"""
	handles all JOIN events
	because twitch is strange, it may happen that join is called twice,
	without a onLeft before

	may calls the following events for custom code:
	- onMemberJoin(Channel, User)
	"""
	JoinUser = User(payload, emergency=True)

	# ignore self
	if JoinUser.name.lower() == cls.nickname.lower():
		return True # even duh, nothing happend, we proccessed the data successful

	# let's see if we got this user already
	KnownUser:User = cls.users.get(JoinUser.name, None)
	if not KnownUser:
		# we never saw this user, add it
		cls.users[JoinUser.name] = JoinUser
		KnownUser = cls.users[JoinUser.name]
	del JoinUser

	# k then, lets get the channel user just joined
	ReHit:re.Match = re.search(ReRoomName, payload)
	if ReHit: room_name:str = ReHit.group(2)
	else: room_name:str = ""

	Chan:Channel = cls.getChannel(name=room_name)
	# to my later self: yes, it must be done via a .getChannel
	# because we don't get the id for cls.channels.get(id)

	if not Chan:
		# that should never happen... but if it does... well fuck
		return True

	# add User to viewer dict of channel
	Chan.viewers[KnownUser.name] = KnownUser
	# add add channel id to Users known channels
	KnownUser.found_in.add(Chan.room_id)

	asyncio.ensure_future( cls.onMemberJoin(Chan, KnownUser) )
	return True

async def handlePart(cls:"Client", payload:str) -> bool:
	"""
	handles all PART events
	because twitch is strange, it may happen that left is called,
	without a onJoin before

	may calls the following events for custom code:
	- onMemberPart(User)

	"""
	PartUser:User = User(payload, emergency=True)

	# ignore self
	if PartUser.name.lower() == cls.nickname.lower():
		return True # even duh, nothing happend, we proccessed the data successful

	# let's see if we got this user already
	KnownUser:User = cls.users.get(PartUser.name, None)
	if not KnownUser:
		# we never saw this user, even duh we got a leave.. twitch is strange issn't it?
		KnownUser = PartUser
	del PartUser

	ReHit:re.Match = re.search(ReRoomName, payload)
	if ReHit: room_name:str = ReHit.group(2)
	else: room_name:str = ""
	Chan:Channel = cls.getChannel(name=room_name)
	# to my later self: yes, it must be done via a .getChannel
	# because we don't get the id for cls.channels.get(id)

	if not Chan:
		# that should never happen... but if it does... well fuck
		return True

	# remove User to viewer dict of channel
	Chan.viewers.pop(KnownUser.name, None)
	# and remove it from the Users known channels
	KnownUser.found_in.discard(Chan.room_id)

	# the user left the last channel we monitor, he now is useless for us
	if len(KnownUser.found_in) == 0:
		cls.users.pop(KnownUser, None)

	asyncio.ensure_future( cls.onMemberPart(Chan, KnownUser) )
	return True

# USERNOTICE

# USERSTATE
