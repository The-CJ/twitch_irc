from typing import TYPE_CHECKING, Any, List, Set, Dict, Optional
if TYPE_CHECKING:
	from .client import Client
	from .channel import Channel

import re
from .message import Message
from .undefined import UNDEFINED

from ..Utils.regex import (
	ReUserName, ReRoomName
)

class User(object):
	"""
	This class represents a twitch user, the same user object might be found in multiple Channel.viewer dict's.
	A user is not bound to a channel, look to the users message to get .sub .mod or other

	if emergency is false a message must be given
	"""
	def __repr__(self):
		if self.minimalistic:
			return f"<{self.__class__.__name__} (minimalistic) name='{self.name}'>"
		else:
			return f"<{self.__class__.__name__} name='{self.name}' user_id={self.user_id}>"

	def __str__(self):
		return self.name or ""

	def __init__(self, raw:Optional[str], emergency:bool=False, Msg:Optional[Message]=None):
		self._name:Optional[str] = None
		self._display_name:Optional[str] = None # *
		self._user_id:Optional[str] = None # *
		self._generated_via_channel:Optional[str] = None

		self.minimalistic:bool = True
		self.found_in:Set[str] = set()

		# * = added at the first message of user (means it's not given on join/part)

		if raw or Msg:
			try:
				if emergency: self.buildFromEvent(raw)
				else: self.buildFromMessage(Msg)

			except:
				raise AttributeError(raw)

	def compact(self) -> dict:
		d:dict = dict()
		d["name"] = self.name
		d["display_name"] = self.display_name
		d["user_id"] = self.user_id
		d["found_in"] = self.found_in
		d["minimalistic"] = self.minimalistic
		return d

	# utils
	def buildFromEvent(self, raw:str) -> None:
		"""
		generated by a LEFT or JOIN Event like:

		```
		:the__cj!the__cj@the__cj.tmi.twitch.tv JOIN #phaazebot
		```

		but its not giving us all user info's
		"""

		# _name
		search = re.search(ReUserName, raw)
		if search:
			self._name = search.group(1)

		# _generated_via_channel
		search = re.search(ReRoomName, raw)
		if search:
			self._generated_via_channel = search.group(1)

		# has not many data in it, will be completed with the first message
		self.minimalistic = True

	def buildFromMessage(self, Msg:Message) -> None:
		"""
		generated by a message
		and messages have all user information's so we use it to make a data full class and update it
		"""

		self._name = Msg.user_name
		self._display_name = Msg.display_name
		self._user_id = Msg.user_id
		self._generated_via_channel = Msg.room_name

		self.minimalistic = False

	def update(self, New:"User") -> Dict[str, Any]:
		"""
		together with a new user object, it updates all attributes that are not None
		"""
		if type(New) != User:
			raise AttributeError(f'new user must be "{self.__class__.__name__}" not "{type(New)}"')

		changes:Dict[str, Any] = {}
		changeable:List[str] = [attr for attr in dir(New) if attr.startswith('_') and not attr.startswith("__")]
		for attr in changeable:

			new_value:Any = getattr(New, attr, None)
			if (new_value is None) or (new_value == UNDEFINED): continue
			old_value:Any = getattr(self, attr, None)

			if new_value == old_value: continue

			setattr(self, attr, new_value)
			changes[attr.lstrip('_')] = new_value

		return changes

	# func
	def foundInChannels(self, cls:"Client") -> List["Channel"]:
		"""
		Returns a list of channels this user is currently in,
		requires you to give this function the Client class, don't ask why...
		Like this:
		```
		async def onUserJoin(self, NewChan, SomeUser):
			channels_a_user_is_in = SomeUser.foundInChannels(self)
			print(f"{SomeUser.name} is now in {len(channels_a_user_is_in)} different channels")
		```
		"""

		ret:List["Channel"] = []

		for channel_name in self.found_in:

			Ch:"Channel" = cls.channels.get(channel_name, None)
			if Ch: ret.append(Ch)

		return ret

	# props
	@property
	def name(self) -> str:
		return str(self._name or "")

	@property
	def display_name(self) -> str:
		return str(self._display_name or "")

	@property
	def id(self) -> str:
		return str(self._user_id or "")

	@property
	def user_id(self) -> str:
		return str(self._user_id or "")
