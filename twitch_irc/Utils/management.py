from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..Classes.client import Client

from ..Classes.channel import Channel

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
		cls.channels[NewChannelInfo.room_id] = NewChannelInfo
		return cls.channels[NewChannelInfo.room_id]

	else:
		CurrentChannelInfo.update( NewChannelInfo )

	return cls.channels[NewChannelInfo.room_id]

def update_channel_viewer(self, user, operation=None):
	"""
	used to add or remove user in a channel.users object from self.channels
	- for some reason twitch sends joins double or don't send a leave
	  so it's not 100% clear that channel.users contains all viewers
	  #ThanksTwitch
	"""

	if operation not in ['add', 'rem']:
		raise AttributeError('only supports "add" and "rem"')

	if user.channel != None:
		chan = user.channel
	else:
		chan = self.get_channel(name = user.channel_name)

	if chan == None: return

	if operation == 'add':
		if chan.users.get(user.name, None) != None:
			return
		chan.users[user.name] = user

	if operation == 'rem':
		if chan.users.get(user.name, None) == None:
			return
		del chan.users[user.name]
