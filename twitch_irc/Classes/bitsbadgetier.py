from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
	from .channel import Channel as TwitchChannel
	from .user import User as TwitchUser

import re
from .structure import UserNoticeStructure

from ..Utils.regex import ReMsgParamThreshold

class BitsBadgeTier(UserNoticeStructure):
	"""
	I don't know what this is, i don't really want to know it. I don't care.

	Example:
	```
	@badge-info=subscriber/9;badges=subscriber/3009,bits/75000;color=#696969;display-name=The__CJ;emotes=88:0-7;flags=;id=6f7bf2d9-c5fa-465c-8c03-88083a6c9f3d;login=the__cj;mod=0;msg-id=bitsbadgetier;msg-param-threshold=75000;room-id=1337;subscriber=1;system-msg=bits\sbadge\stier\snotification;tmi-sent-ts=1599071151453;user-id=696969;user-type= :tmi.twitch.tv USERNOTICE #phaazebot :PogChamp
	```
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} from='{self.room_name}' threshold='{self.threshold}'>"

	def __init__(self, raw:Optional[str]):
		# new tags (ordered)
		self._msg_param_threshold:int = 0

		# classes
		self.Channel:Optional["TwitchChannel"] = None
		self.User:Optional["TwitchUser"] = None

		if raw:
			try:
				super().__init__(raw)
				self.bitsBadgeTierBuild(raw)
			except:
				raise AttributeError(raw)

	# utils
	def compact(self) -> dict:
		d:dict = super().compact()
		d["threshold"] = self.threshold
		d["Channel"] = self.Channel
		d["User"] = self.User
		return d

	def bitsBadgeTierBuild(self, raw:str):
		search:re.Match

		# _msg_param_threshold
		search = re.search(ReMsgParamThreshold, raw)
		if search:
			self._msg_param_threshold = search.group(1)

	# extra props
	@property
	def threshold(self) -> int:
		return int(self._msg_param_threshold or 0)
