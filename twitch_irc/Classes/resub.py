from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .channel import Channel as TwitchChannel
    from .user import User as TwitchUser

import re
from .sub import Sub
from .structure import UserNoticeStructure
from .undefined import UNDEFINED

from ..Utils.regex import (
	ReMsgParamPriorGifterAnonymous, ReMsgParamPriorGifterDisplayName,
	ReMsgParamPriorGifterID, ReMsgParamPriorGifterUserName, ReMsgParamRecipientID,
	ReMsgParamRecipientDisplayName,	ReMsgParamRecipientUserName,
	ReMsgParamSenderLogin, ReMsgParamSubPlan, ReMsgParamSenderName,
)

class ReSub(Sub):
	"""
	A very basic ReSub, where the user uses money or Prime to continue the sub on his own.
	That thing is so basic, that it has the exact same tags as a Sub.
	This case is the only nice thing, because there is a handful of "special" resub options.
	Buckle Up My Dude, the following classes with be dog feces. YEEEE-HAAAAA
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} channel='{self.room_name}' user='{self.login}' months='{self.cumulative_months}'>"

class GiftPaidUpgrade(UserNoticeStructure):
	"""
	This Class represents a upgrade from a gift sub, its like a normal resub... but special
	yeah... twitch stuff.
	It just means someone who got a giftsub, now subs normaly, but its not normal resub, because we get extra vars... duh

	Dev Note: soo.. twitch is not giving us a `msg-param-sub-plan` tag, which is strange,
	i mean what happens if you got gifted a tier 1 and then resub by yourself with tier 2?
	it will trigger a `msg-id=giftpaidupgrad` but will not show which tier... strange
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} channel='{self.room_name}' user='{self.login}' gifter='{self.sender_login}'>"

	def __init__(self, raw:str or None):
		# extra tags (ordered)
		self._msg_param_sender_login:str = UNDEFINED
		self._msg_param_sender_name:str = UNDEFINED

		# classes
		self.Channel:"TwitchChannel" = None
		self.User:"TwitchUser" = None
		self.Gifter:"TwitchUser" = None

		if raw != None:
			try:
				super().__init__(raw)
				self.giftPaidUpgradeBuild(raw)
			except:
				raise AttributeError(raw)

	# utils
	def compact(self) -> dict:
		d:dict = super().compact()
		d["sender_login"] = self.sender_login
		d["sender_name"] = self.sender_name
		d["Channel"] = self.Channel
		d["User"] = self.User
		d["Gifter"] = self.Gifter
		return d

	def giftPaidUpgradeBuild(self, raw:str):
		search:re.Match

		# _msg_param_sender_login
		search = re.search(ReMsgParamSenderLogin, raw)
		if search != None:
			self._msg_param_sender_login = search.group(1)

		# _msg_param_sender_name
		search = re.search(ReMsgParamSenderName, raw)
		if search != None:
			self._msg_param_sender_name = search.group(1)

	# extra props
	@property
	def sender_login(self) -> str:
		return str(self._msg_param_sender_login or "")

	@property
	def sender_name(self) -> str:
		return str(self._msg_param_sender_name or "")

class PrimePaidUpgrade(UserNoticeStructure):
	"""
	Yeeeay another special case of sub.
	This Class comes up when a user subbed with prime once, and now resubbs to a normal paid sub.
	aaaa yes... twitch.
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} channel='{self.room_name}' user='{self.login}'>"

	def __init__(self, raw:str or None):
		# tags (ordered)
		self._msg_param_sub_plan:str = UNDEFINED

		# classes
		self.Channel:"TwitchChannel" = None
		self.User:"TwitchUser" = None

		if raw != None:
			try:
				super().__init__(raw)
				self.primePaidUpgradeBuild(raw)
			except:
				raise AttributeError(raw)

	# utils
	def compact(self) -> dict:
		d:dict = super().compact()
		d["sub_plan"] = self.sub_plan
		d["Channel"] = self.Channel
		d["User"] = self.User
		return d

	def primePaidUpgradeBuild(self, raw:str):
		search:re.Match

		# _msg_param_sub_plan
		search = re.search(ReMsgParamSubPlan, raw)
		if search != None:
			self._msg_param_sub_plan = search.group(1)

	# extra props
	@property
	def sub_plan(self) -> str:
		return str(self._msg_param_sub_plan or "")

class StandardPayForward(UserNoticeStructure):
	"""
	eeee yeah... whatever
	Happens when someone else is gifting a sub to somone who got a sub from somone else before... thanks twitch
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} channel='{self.room_name}' new_gifter='{self.login}' old_gifter={self.prior_gifter_user_name} to='{self.recipient_user_name}'>"

	def __init__(self, raw:str or None):
		# extra tags (ordered)
		self._msg_param_prior_gifter_anonymous:bool = UNDEFINED
		self._msg_param_prior_gifter_display_name:str = UNDEFINED
		self._msg_param_prior_gifter_id:str = UNDEFINED
		self._msg_param_prior_gifter_user_name:str = UNDEFINED
		self._msg_param_recipient_display_name:str = UNDEFINED
		self._msg_param_recipient_id:str = UNDEFINED
		self._msg_param_recipient_user_name:str = UNDEFINED

		# classes
		self.Channel:"TwitchChannel" = None
		self.User:"TwitchUser" = None
		self.Prior:"TwitchUser" = None
		self.Recipient:"TwitchUser" = None

		if raw != None:
			try:
				super().__init__(raw)
				self.standardPayForwardBuild(raw)
			except:
				raise AttributeError(raw)

	# utils
	def compact(self) -> dict:
		d:dict = super().compact()
		d["prior_gifter_anonymous"] = self.prior_gifter_anonymous
		d["prior_gifter_display_name"] = self.prior_gifter_display_name
		d["prior_gifter_id"] = self.prior_gifter_id
		d["prior_gifter_user_name"] = self.prior_gifter_user_name
		d["recipient_display_name"] = self.recipient_display_name
		d["recipient_id"] = self.recipient_id
		d["recipient_user_name"] = self.recipient_user_name
		d["Channel"] = self.Channel
		d["User"] = self.User
		d["Prior"] = self.Prior
		d["Recipient"] = self.Recipient
		return d

	def standardPayForwardBuild(self, raw:str):
		search:re.Match

		# _msg_param_prior_gifter_anonymous
		search = re.search(ReMsgParamPriorGifterAnonymous, raw)
		if search != None:
			self._msg_param_prior_gifter_anonymous = True if search.group(1) == "true" else False

		# _msg_param_prior_gifter_display_name
		search = re.search(ReMsgParamPriorGifterDisplayName, raw)
		if search != None:
			self._msg_param_prior_gifter_display_name =  search.group(1)

		# _msg_param_prior_gifter_id
		search = re.search(ReMsgParamPriorGifterID, raw)
		if search != None:
			self._msg_param_prior_gifter_id = search.group(1)

		# _msg_param_prior_gifter_user_name
		search = re.search(ReMsgParamPriorGifterUserName, raw)
		if search != None:
			self._msg_param_prior_gifter_user_name = search.group(1)

		# _msg_param_recipient_display_name
		search = re.search(ReMsgParamRecipientDisplayName, raw)
		if search != None:
			self._msg_param_recipient_display_name = search.group(1)

		# _msg_param_recipient_id
		search = re.search(ReMsgParamRecipientID, raw)
		if search != None:
			self._msg_param_recipient_id = search.group(1)

		# _msg_param_recipient_user_name
		search = re.search(ReMsgParamRecipientUserName, raw)
		if search != None:
			self._msg_param_recipient_user_name = search.group(1)

	# extra props
	@property
	def prior_gifter_anonymous(self) -> str:
		return str(self._msg_param_prior_gifter_anonymous or "")

	@property
	def prior_gifter_display_name(self) -> str:
		return str(self._msg_param_prior_gifter_display_name or "")

	@property
	def prior_gifter_id(self) -> str:
		return str(self._msg_param_prior_gifter_id or "")

	@property
	def prior_gifter_user_name(self) -> str:
		return str(self._msg_param_prior_gifter_user_name or "")

	@property
	def recipient_display_name(self) -> str:
		return str(self._msg_param_recipient_display_name or "")

	@property
	def recipient_id(self) -> str:
		return str(self._msg_param_recipient_id or "")

	@property
	def recipient_user_name(self) -> str:
		return str(self._msg_param_recipient_user_name or "")

class CommunityPayForward(UserNoticeStructure):
	"""
	U know... everytime i think im done, there is more...
	Sooo this Class comes up when someone resubs, who was hit with a MysteryGiftSub (aka. Mass Sub) before.
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} channel='{self.room_name}' user='{self.login}' old_massgifter='{self.prior_gifter_user_name}'>"

	def __init__(self, raw:str or None):
		# new tags (ordered)
		self._msg_param_prior_gifter_anonymous:bool = UNDEFINED
		self._msg_param_prior_gifter_display_name:str = UNDEFINED
		self._msg_param_prior_gifter_id:str = UNDEFINED
		self._msg_param_prior_gifter_user_name:str = UNDEFINED

		# classes
		self.Channel:"TwitchChannel" = None
		self.User:"TwitchUser" = None
		self.Prior:"TwitchUser" = None

		if raw != None:
			try:
				super().__init__(raw)
				self.communityPayForwardBuild(raw)
			except:
				raise AttributeError(raw)

	# utils
	def compact(self) -> dict:
		d:dict = super().compact()
		d["prior_gifter_anonymous"] = self.prior_gifter_anonymous
		d["prior_gifter_display_name"] = self.prior_gifter_display_name
		d["prior_gifter_id"] = self.prior_gifter_id
		d["prior_gifter_user_name"] = self.prior_gifter_user_name
		d["Channel"] = self.Channel
		d["User"] = self.User
		d["Prior"] = self.Prior
		return d

	def communityPayForwardBuild(self, raw:str):
		search:re.Match

		# _msg_param_prior_gifter_anonymous
		search = re.search(ReMsgParamPriorGifterAnonymous, raw)
		if search != None:
			self._msg_param_prior_gifter_anonymous = True if search.group(1) == "true" else False

		# _msg_param_prior_gifter_display_name
		search = re.search(ReMsgParamPriorGifterDisplayName, raw)
		if search != None:
			self._msg_param_prior_gifter_display_name =  search.group(1)

		# _msg_param_prior_gifter_id
		search = re.search(ReMsgParamPriorGifterID, raw)
		if search != None:
			self._msg_param_prior_gifter_id = search.group(1)

		# _msg_param_prior_gifter_user_name
		search = re.search(ReMsgParamPriorGifterUserName, raw)
		if search != None:
			self._msg_param_prior_gifter_user_name = search.group(1)

	# new props
	@property
	def prior_gifter_anonymous(self) -> str:
		return str(self._msg_param_prior_gifter_anonymous or "")

	@property
	def prior_gifter_display_name(self) -> str:
		return str(self._msg_param_prior_gifter_display_name or "")

	@property
	def prior_gifter_id(self) -> str:
		return str(self._msg_param_prior_gifter_id or "")

	@property
	def prior_gifter_user_name(self) -> str:
		return str(self._msg_param_prior_gifter_user_name or "")
