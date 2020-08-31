from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .channel import Channel as TwitchChannel
    from .user import User as TwitchUser

import re
from .structure import UserNoticeStructure
from .undefined import UNDEFINED

from ..Utils.regex import ReMsgParamMassGiftCount, ReMsgParamSubPlan, ReMsgParamSenderCount

class MysteryGiftSub(UserNoticeStructure):
	"""
	This Class represents a submysterygift, u may also call this a: "Sub Bomb" or so
    (in this event is not tracked who got the subs, just the one who buyed the subs)
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} channel='{self.room_name}' gifter='{self.login}' amount='{self.mass_gift_count}'>"

	def __init__(self, raw:str or None):
		self._msg_param_mass_gift_count:int = UNDEFINED
		self._msg_param_sender_count:int = UNDEFINED
		self._msg_param_sub_plan:str = UNDEFINED

		# classes
		self.Channel:"TwitchChannel" = None
		self.Gifter:"TwitchUser" = None

		if raw != None:
			try:
				super().__init__(raw)
				self.mysteryGiftSubBuild(raw)
			except:
				raise AttributeError(raw)

	def compact(self) -> dict:
		d:dict = super().compact()
		d["mass_gift_count"] = self.mass_gift_count
		d["sender_count"] = self.sender_count
		d["sub_plan"] = self.sub_plan
		d["Channel"] = self.Channel
		d["Gifter"] = self.Gifter
		return d

	# utils
	def mysteryGiftSubBuild(self, raw:str):
		search:re.Match

		# _msg_param_mass_gift_count
		search = re.search(ReMsgParamMassGiftCount, raw)
		if search != None:
			self._msg_param_mass_gift_count = search.group(1)

		# _msg_param_sender_count
		search = re.search(ReMsgParamSenderCount, raw)
		if search != None:
			self._msg_param_sender_count = search.group(1)

		# _msg_param_sub_plan
		search = re.search(ReMsgParamSubPlan, raw)
		if search != None:
			self._msg_param_sub_plan = search.group(1)

	# new props
	@property
	def mass_gift_count(self) -> int:
		return int(self._msg_param_mass_gift_count or 0)

	@property
	def sender_count(self) -> int:
		return int(self._msg_param_sender_count or 0)

	@property
	def sub_plan(self) -> str:
		return str(self._msg_param_sub_plan or "")
