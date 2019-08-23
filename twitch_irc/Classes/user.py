from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from .channel import Channel as TwitchChannel

import re
from .message import Message

ReName:"re.Pattern" = re.compile(r"^:(.+?)!")
ReChannelName:"re.Pattern" = re.compile(r"(JOIN|PART) #(\w+)")

class User(object):
	"""
		This class represents a user from a channel for a viewer list,
		aswell for join or left events,
		in a usable class for the bot channel users list

		if emergency is false a message must be given
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} name='{self.name}' channel='{self.channel_name}'>"

	def __str__(self):
		return self.name

	def __init__(self, raw:str, emergency:bool=False, Msg:Message=None):
		self.name:str = None
		self.display_name:str = None # *
		self.user_id:str = None # *
		self.user_type:str = None # *
		self.sub:bool = False # *
		self.mod:bool = False # *
		self.turbo:bool = False # *
		self.channel_name:str = None

		self.Channel:"TwitchChannel" = None # *
		self.minimalistic:bool = True

		# * = added at the first message of user (means it's not given on join/part)

		if emergency:
			self.buildFromEvent(raw)
		else:
			self.buildFromMessage(Msg)

	def buildFromEvent(self, raw:str) -> None:
		"""
			generated by a LEFT or JOIN Event like:

			:the__cj!the__cj@the__cj.tmi.twitch.tv JOIN #phaazebot

			but its not giving us all user infos
		"""

		#name
		search = re.search(ReName, raw)
		if search != None:
			self.name = search.group(1)

		#channel_name
		search = re.search(ReChannelName, raw)
		if search != None:
			self.channel_name = search.group(2)

		# has not mush data in it, will be completed with the first message
		self.minimalistic = True

	def buildFromMessage(self, Msg:Message) -> None:
		"""
		generated by a message
		and messages have all user informations so we use it to make a data full class and update it
		"""

		self.name = Msg.name
		self.display_name = Msg.display_name
		self.user_id = Msg.user_id
		self.user_type = Msg.user_type
		self.sub = Msg.sub
		self.mod = Msg.mod
		self.turbo = Msg.turbo
		self.channel_name = Msg.channel_name

		self.minimalistic = False

	def update(self, New:"User") -> None:
		"""
			together with a new user object, it updates all attributes that are not None
		"""
		if type(New) != User:
			raise AttributeError( f'user must be "{self.__class__.__name__}" not "{type(New)}"' )

		__all__ = dir(New)
		__all__ = [attr for attr in __all__ if not attr.startswith('__') and attr != "channel"]
		for attr in __all__:

			if not callable( getattr(self, attr) ):

				new_value:Any = getattr(New, attr, None)
				if new_value != None:
					setattr(self, attr, new_value)