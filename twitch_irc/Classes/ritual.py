from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .channel import Channel as TwitchChannel
    from .user import User as TwitchUser

import re
from .structure import UserNoticeStructure
from .undefined import UNDEFINED

from ..Utils.regex import ReMsgParamRitualName

class Ritual(UserNoticeStructure):
	"""
	So rituals are a new(?) thing in twitch and they may appear on multiple channel and or user related events,
	however, currently its only used in one case, the 'new_chatter' event.
	More might come at some point.
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} channel='{self.room_name}' event='{self.ritual_name}' user='{self.login}'>"

	def __init__(self, raw:str or None):
		# new tags (ordered)
		self._msg_param_ritual_name:str = UNDEFINED

		# classes
		self.Channel:"TwitchChannel" = None
		self.User:"TwitchUser" = None

		if raw != None:
			try:
				super().__init__(raw)
				self.ritualBuild(raw)
			except:
				raise AttributeError(raw)

	# utils
	def compact(self) -> dict:
		d:dict = super().compact()
		d["ritual_name"] = self.ritual_name
		d["Channel"] = self.Channel
		d["User"] = self.User
		return d

	def ritualBuild(self, raw:str):
		search:re.Match

		# _msg_param_ritual_name
		search = re.search(ReMsgParamRitualName, raw)
		if search != None:
			self._msg_param_ritual_name = search.group(1)

	# extra props
	@property
	def ritual_name(self) -> str:
		return str(self._msg_param_ritual_name or "")
