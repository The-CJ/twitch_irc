from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..Classes.client import Client

from ..Classes.channel import Channel
from ..Classes.user import User

def updateChannelInfos(cls:"Client", NewChannelInfo:Channel) -> Channel:
	"""
	used to update channel infos in Client.channels
	it will update all non None attributes in a existing object or create a new entry in self.channels

	returns updated channel
	"""

	if type(NewChannelInfo) != Channel:
		raise AttributeError(f"channel must be '{str(Channel)}' not '{type(NewChannelInfo)}'")

	CurrentChannelInfo:Channel = cls.channels.get(NewChannelInfo.room_id, None)
	if not CurrentChannelInfo:
		cls.channels[str(NewChannelInfo.room_id)] = NewChannelInfo
		return cls.channels[str(NewChannelInfo.room_id)]

	else:
		CurrentChannelInfo.update( NewChannelInfo )

	return cls.channels[str(NewChannelInfo.room_id)]

def updateChannelViewer(cls:"Client", Viewer:User, add:bool=False, rem:bool=False) -> None:
	"""
	used to add or remove user/viewer in Channel.users object from Client.channels
	- for some reason twitch sends joins double or don't send a leave
	  so it's not 100% clear that Channel.users contains all viewers
	  #ThanksTwitch
	"""

	if not (add ^ rem):
		raise AttributeError("only one of 'add' or 'rem' must be True")

	if Viewer.Channel:
		CurrentChannel:Channel = Viewer.Channel
	else:
		CurrentChannel:Channel = cls.getChannel(name = Viewer.channel_name)

	if not CurrentChannel: return

	if add:
		if not CurrentChannel.users.get(Viewer.name, None):
			CurrentChannel.users[Viewer.name] = Viewer

	elif rem:
		CurrentChannel.users.pop(Viewer.name, None)
