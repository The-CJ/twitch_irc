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

	Example:
	```
	@badge-info=subscriber/16;badges=subscriber/12,bits-charity/1;color=#696969;display-name=The__CJ;emotes=;flags=;id=5bcf7520-4596-4494-9fea-41943783ccf8;login=the__cj;mod=0;msg-id=submysterygift;msg-param-mass-gift-count=3;msg-param-origin-id=123456789;msg-param-sender-count=27;msg-param-sub-plan=1000;room-id=94638902;subscriber=1;system-msg=The__CJ\sis\sgifting\s3\sTier\s1\sSubs\sto\sPhaazebot's\scommunity!\sThey've\sgifted\sa\stotal\sof\s27\sin\sthe\schannel!;tmi-sent-ts=1599059927291;user-id=67664971;user-type= :tmi.twitch.tv USERNOTICE #phaazebot
	```
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
