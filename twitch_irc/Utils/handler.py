from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..Classes.client import Client

import logging
Log:logging.Logger = logging.getLogger("twitch_irc")

import re
import asyncio
from ..Classes.channel import Channel
from ..Classes.user import User
from ..Classes.userstate import UserState
from ..Classes.message import Message
from ..Classes.timeout import Timeout, Ban
from ..Classes.sub import Sub, ReSub

from ..Utils.regex import (
	ReTargetMsgID, ReTMISendTS, ReLogin,
	ReContent, ReRoomName, ReMsgID,
	ReUserListData
)

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
		Chan:Channel = cls.channels.get(Detect.room_name, None)

		# no channel found, lets make a very minimalistic class, hopefully that never happens
		if not Chan:
			Chan = Channel(None)
			Chan._room_id = Detect.room_id

		Log.debug(f"Client launching: Client.onClearChat: {str(vars(Chan))}")
		asyncio.ensure_future( cls.onClearChat(Chan) )
		return True

	# its actully a ban
	if Detect.duration == 0: Detect:Ban = Ban(Detect)

	# get channel where that happens, lets hope, we always get one, because else its dudu
	Chan:Channel = cls.channels.get(Detect.room_name, None)
	if not Chan:
		Chan = Channel(None)
		Chan._room_id = Detect.room_id

	# get user that was ban/timeout, lets hope, we always get one, because else its dudu
	FoundUser:User = Chan.users.get(Detect.user_name, None)
	if not FoundUser:
		FoundUser = User(None)
		FoundUser._user_id = Detect.target_user_id
		FoundUser._name = Detect.user_name

	Detect.Channel = Chan
	Detect.User = FoundUser

	if type(Detect) is Ban:
		Log.debug(f"Client launching: Client.onBan: {str(vars(Detect))}")
		asyncio.ensure_future( cls.onBan(Detect) )
		return True
	else:
		Log.debug(f"Client launching: Client.onTimeout: {str(vars(Detect))}")
		asyncio.ensure_future( cls.onTimeout(Detect) )
		return True

	return False # will never be reached, but why not?

async def handleClearMsg(cls:"Client", payload:str) -> bool:
	"""
	handles all CLEARMSG events
	which... well near to never happend but whatever

	may calls the following events for custom code:
	- onClearMsg(Message)
	"""

	MehMessage:Message = Message(None)

	search:re.Match
	search = re.search(ReTargetMsgID, payload)
	if search != None:
		MehMessage._msg_id = search.group(1)

	search = re.search(ReTMISendTS, payload)
	if search != None:
		MehMessage._tmi_sent_ts = search.group(1)

	search = re.search(ReLogin, payload)
	if search != None:
		MehMessage._user_name = search.group(1)
		WeKnowTheUser:User = cls.users.get(MehMessage.user_name, None)
		if WeKnowTheUser:
			MehMessage.Author = WeKnowTheUser
			MehMessage._user_id = WeKnowTheUser.user_id
			MehMessage._user_name = WeKnowTheUser.name
			MehMessage._user_display_name = WeKnowTheUser.display_name

	search = re.search(ReContent, payload)
	if search != None:
		MehMessage._content = search.group(2)

	search = re.search(ReRoomName, payload)
	if search != None:
		MehMessage._room_name = search.group(2)
		WeKnowTheChan:Channel = cls.channels.get(MehMessage.room_name, None)
		if WeKnowTheChan:
			MehMessage.Channel = WeKnowTheChan
			MehMessage._room_id = WeKnowTheChan.room_id
			MehMessage._room_name = WeKnowTheChan.name

	# welp thats all we can get, if we even get it, so take it or die i guess
	Log.debug(f"Client launching: Client.onClearMsg: {str(vars(MehMessage))}")
	asyncio.ensure_future( cls.onClearMsg(MehMessage) )
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
	Chan:Channel = cls.channels.get(Msg.channel_name, None)
	if Chan:
		Msg.Channel = Chan
	else:
		# should never happen, but ok
		NewChan:Channel = Channel(None, emergency=True, Msg=Msg)
		cls.channels[NewChan.name] = NewChan
		Msg.Channel = NewChan
		Chan = NewChan
		del NewChan

	# get Author
	Author:User = cls.users.get(Msg.user_name, None)
	if Author:
		if Author.minimalistic:
			FullAuthor:User = User(None, emergency=False, Msg=Msg)
			Author.update(FullAuthor)
			Author.minimalistic = False

		Msg.Author = Author
	else:
		# get called when the user write a message before twitch tells us the he joined,
		# so we add it to viewer befor we get the join event
		Alternative:User = User(None, emergency=False, Msg=Msg)

		# add new user to client's user dict
		cls.users[Alternative.name] = Alternative

		Msg.Author = Alternative
		Log.debug(f"Client launching: Client.onMemberJoin: {str(vars(Chan))} {str(vars(Alternative))}")
		asyncio.ensure_future( cls.onMemberJoin(Chan, Alternative) )

	# safty step, add author to channels viewer list, and channel to viewer
	Msg.Channel.viewers[Msg.Author.name] = Msg.Author
	Msg.Author.found_in.add(Msg.channel_name)

	Log.debug(f"Client launching: Client.onMessage: {str(vars(Msg))}")
	asyncio.ensure_future( cls.onMessage(Msg) )
	return True

async def handleRoomState(cls:"Client", payload:str) -> bool:
	"""
	handles all ROOMSTATE events

	may calls the following events for custom code:
	- onChannelUpdate(Channel, changes)
	"""
	ChannelUpdate:Channel = Channel(payload, emergency=False)
	CurrentChannel:Channel = cls.channels.get(ChannelUpdate.name, None)

	# should never happen
	if not CurrentChannel:
		cls.channels[ChannelUpdate.name] = ChannelUpdate
		Log.debug(f"Client launching: Client.onChannelUpdate: {str(vars(ChannelUpdate))}")
		asyncio.ensure_future( cls.onChannelUpdate(ChannelUpdate, {}) )
		return True

	changes:dict = CurrentChannel.update(ChannelUpdate)
	if CurrentChannel.minimalistic:
		CurrentChannel.minimalistic = False
		changes = {}

	Log.debug(f"Client launching: Client.onChannelUpdate: {str(vars(CurrentChannel))} {str(changes)}")
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

	# ignore self, but use it to update the clients channels
	if JoinUser.name.lower() == cls.nickname.lower():

		FreshChannel:Channel = Channel(None)
		FreshChannel.minimalistic = True
		FreshChannel._name = JoinUser._generated_via_channel

		# add new channel to clients known channels
		Log.debug(f"Client joined a channel, adding {JoinUser._generated_via_channel}")
		cls.channels[FreshChannel.name] = FreshChannel

		return True

	# let's see if we got this user already
	KnownUser:User = cls.users.get(JoinUser.name, None)
	if not KnownUser:
		# we never saw this user, add it
		cls.users[JoinUser.name] = JoinUser
		KnownUser = cls.users[JoinUser.name]

	Chan:Channel = cls.channels.get(JoinUser._generated_via_channel, None)
	if not Chan:
		# that should never happen... but if it does... well fuck
		Log.error(f"Could not find channel for {JoinUser._generated_via_channel}")
		return True

	# add User to viewer dict of channel
	Chan.viewers[KnownUser.name] = KnownUser
	# add add channel id to Users known channels
	KnownUser.found_in.add(Chan.name)

	Log.debug(f"Client launching: Client.onMemberJoin: {str(vars(Chan))} {str(vars(KnownUser))}")
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

	# ignore self but use it to update clients channel dict
	if PartUser.name.lower() == cls.nickname.lower():

		# if we got a part for our user... well guess we can delete the channel then, right?
		Log.debug(f"Client parted a channel, removing {PartUser._generated_via_channel}")
		cls.channels.pop(PartUser._generated_via_channel, None)

		return True

	# let's see if we got this user already
	KnownUser:User = cls.users.get(PartUser.name, None)
	if not KnownUser:
		# we never saw this user, even duh we got a leave.. twitch is strange issn't it?
		KnownUser = PartUser

	Chan:Channel = cls.channels.get(PartUser._generated_via_channel, None)
	if not Chan:
		# that should never happen... but if it does... well fuck
		Log.error(f"Could not find channel for {PartUser._generated_via_channel}")
		return True

	# remove User to viewer dict of channel
	Chan.viewers.pop(KnownUser.name, None)
	# and remove it from the Users known channels
	KnownUser.found_in.discard(Chan.name)

	# the user left the last channel we monitor, he now is useless for us
	if len(KnownUser.found_in) == 0:
		cls.users.pop(KnownUser, None)

	Log.debug(f"Client launching: Client.onMemberPart: {str(vars(Chan))} {str(vars(KnownUser))}")
	asyncio.ensure_future( cls.onMemberPart(Chan, KnownUser) )
	return True

async def handleUserState(cls:"Client", payload:str) -> bool:
	"""
	handles all USERSTATE events
	which is only needed for internal proccesses and for channel.Me
	that represents the Client's user state in a channel

	may calls the following events for custom code:
	- None
	"""

	BotState:UserState = UserState(payload)

	# get channel of event, thanks tiwtch for NOT giving me the room id,
	# who needs direct access when you can iterate over it
	StateChan:Channel = cls.channels.get(BotState.room_name, None)

	if StateChan:
		StateChan._me = BotState
		Log.debug(f"Updated UserState object for {StateChan}")

	return True

async def handleUserList(cls:"Client", payload:str) -> bool:
	"""
	User-List aka, IRC Event: 353
	which means a list of all users that already are in the channel when the Client joined.
	(only given when user list is less than 1000, because then twitch don't sends join/part)

	may calls the following events for custom code:
	- None
	"""

	# e.g.: :phaazebot.tmi.twitch.tv 353 phaazebot = #phaazebot :the__cj someone someoneelse
	search:re.Match = re.search(ReUserListData, payload)
	if search != None:
		room_name:str = search.group(1)
		ChannelToFill:Channel = cls.channels.get(room_name, None)
		if not ChannelToFill: return True

		full_user_list:str = search.group(2)
		for user_name in full_user_list.split(' '):

			if user_name.lower() == cls.nickname.lower(): continue

			KnownUser:User = cls.users.get(user_name, None)
			if not KnownUser:
				KnownUser:User = User(None)
				KnownUser._name = user_name
				KnownUser.minimalistic = True

				cls.users[KnownUser.name] = KnownUser

			Log.debug(f"New Entry to `already-known-user-list`: {ChannelToFill.name} - {KnownUser.name}")
			ChannelToFill.viewers[KnownUser.name] = KnownUser
			KnownUser.found_in.add(ChannelToFill.name)

	return True

async def handleUserNotice(cls:"Client", payload:str) -> bool:
	"""
	welcome to the bane of my existence, USERSTATE.
	twitch uses this event to send (gift-)subs, resubs, raids and rituals
	And we try to handle all of it... yeah

	may calls the following events for custom code:
	- onSub(Sub)
	"""

	found_event:str = None
	search:re.Match = re.search(ReMsgID, payload)
	if search != None:
		found_event = search.group(1)

	if not found_event: return False

	if found_event == "sub":
		NewSub:Sub = Sub(payload)

		NewSub.User = cls.users.get(NewSub.user_name, None)
		NewSub.Channel = cls.channels.get(NewSub.room_name, None)

		Log.debug(f"Client launching: Client.onSub: {str(vars(NewSub))}")
		asyncio.ensure_future( cls.onSub(NewSub) )
		return True

	if found_event == "resub":
		NewReSub:ReSub = ReSub(payload)

		NewReSub.User = cls.users.get(NewReSub.user_name, None)
		NewReSub.Channel = cls.channels.get(NewReSub.room_name, None)

		Log.debug(f"Client launching: Client.onReSub: {str(vars(NewReSub))}")
		asyncio.ensure_future( cls.onReSub(NewReSub) )
		return True

	if found_event == "resub": print("TODO: resub")
	if found_event == "subgift": print("TODO: subgift")
	if found_event == "anonsubgift": print("TODO: anonsubgift")
	if found_event == "submysterygift": print("TODO: submysterygift")
	if found_event == "giftpaidupgrade": print("TODO: giftpaidupgrade")
	if found_event == "rewardgift": print("TODO: rewardgift")
	if found_event == "anongiftpaidupgrade": print("TODO: anongiftpaidupgrade")
	if found_event == "raid": print("TODO: raid")
	if found_event == "unraid": print("TODO: unraid")
	if found_event == "ritual": print("TODO: ritual")
	if found_event == "bitsbadgetier": print("TODO: bitsbadgetier")
