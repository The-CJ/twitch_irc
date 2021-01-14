from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
	from .channel import Channel as TwitchChannel
	from .user import User as TwitchUser

import re
from .sub import Sub
from .structure import UserNoticeStructure

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

	Example raw:
	```
	@badge-info=subscriber/4;badges=subscriber/3,premium/1;color=#696969;display-name=The__CJ;emotes=;flags=;id=1823ea14-c9b9-414b-b914-0106ed56b27b;login=the__cj;mod=0;msg-id=resub;msg-param-cumulative-months=4;msg-param-months=0;msg-param-should-share-streak=0;msg-param-sub-plan-name=Name;msg-param-sub-plan=Prime;msg-param-was-gifted=false;room-id=94638902;subscriber=1;system-msg=The__CJ\ssubscribed\swith\sTwitch\sPrime.\sThey've\ssubscribed\sfor\s4\smonths!;tmi-sent-ts=1598919683700;user-id=67664971;user-type= :tmi.twitch.tv USERNOTICE #phaazebot :o hello there
	```
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} channel='{self.room_name}' user='{self.login}' months='{self.cumulative_months}'>"

class GiftPaidUpgrade(UserNoticeStructure):
	"""
	This Class represents a notification from a gift sub, to a normal paid sub. (Its not a resub.)
	This happens whenever the person decides to upgrade, which might happen 2 hours after receiving the giftsub.
	The resub that followes will come at the next month.

	This class will also be used for `msg-id=anongiftpaidupgrade` if its anonym, sender_name and sender_login are always empty

	Example giftpaidupgrade:
	```
	@badge-info=subscriber/1;badges=subscriber/0;color=#696969;display-name=The__CJ;emotes=;flags=;id=f5e242bd-2932-464f-991b-8d07d155c616;login=the__cj;mod=0;msg-id=giftpaidupgrade;msg-param-sender-login=phaaze;msg-param-sender-name=Phaaze;room-id=94638902;subscriber=1;system-msg=The__CJ\sis\scontinuing\sthe\sGift\sSub\sthey\sgot\sfrom\sPhaaze!;tmi-sent-ts=1598923441090;user-id=67664971;user-type= :tmi.twitch.tv USERNOTICE #phaazebot
	```
	Example anongiftpaidupgrade:
	```
	@badge-info=subscriber/2;badges=subscriber/2,partner/1;color=#696969;display-name=The__CJ;emotes=;flags=;id=a063c384-0db6-4698-80b1-27e65fc08d50;login=the__cj;mod=0;msg-id=anongiftpaidupgrade;room-id=94638902;subscriber=1;system-msg=The__CJ\sis\scontinuing\sthe\sGift\sSub\sthey\sgot\sfrom\san\sanonymous\suser!;tmi-sent-ts=1599393085963;user-id=67664971;user-type= :tmi.twitch.tv USERNOTICE #phaazebot
	```
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} channel='{self.room_name}' user='{self.login}' old_gifter='{self.sender_login}'>"

	def __init__(self, raw:Optional[str]):
		# extra tags (ordered)
		self._msg_param_sender_login:Optional[str] = None
		self._msg_param_sender_name:Optional[str] = None

		# classes
		self.Channel:Optional["TwitchChannel"] = None
		self.Gifter:Optional["TwitchUser"] = None
		self.User:Optional["TwitchUser"] = None

		if raw:
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
		d["anonym"] = self.anonym
		d["Channel"] = self.Channel
		d["User"] = self.User
		d["Gifter"] = self.Gifter
		return d

	def giftPaidUpgradeBuild(self, raw:str):
		search:re.Match

		# _msg_param_sender_login
		search = re.search(ReMsgParamSenderLogin, raw)
		if search:
			self._msg_param_sender_login = search.group(1)

		# _msg_param_sender_name
		search = re.search(ReMsgParamSenderName, raw)
		if search:
			self._msg_param_sender_name = search.group(1)

	# extra props
	@property
	def sender_login(self) -> str:
		return str(self._msg_param_sender_login or "")

	@property
	def sender_name(self) -> str:
		return str(self._msg_param_sender_name or "")

	@property
	def anonym(self) -> bool:
		return not bool(self._msg_param_sender_login)

class PrimePaidUpgrade(UserNoticeStructure):
	"""
	Yeeeay another special case of sub.
	This Class comes up when a user subbed with prime once, and now decides to pais for the next month.
	This happens whenever the person decides to upgrade, which might happen 2 hours after subbing with prime.
	The resub that follows will come at the next month.

	Example:
	```
	@badge-info=subscriber/27;badges=subscriber/24,premium/1;color=#696969;display-name=The__CJ;emotes=;flags=;id=3ce2d100-c623-4695-b6db-63c15e125205;login=the__cj;mod=0;msg-id=primepaidupgrade;msg-param-sub-plan=1000;room-id=94638902;subscriber=1;system-msg=The__CJ\sconverted\sfrom\sa\sTwitch\sPrime\ssub\sto\sa\sTier\s1\ssub!;tmi-sent-ts=1599060360623;user-id=67664971;user-type= :tmi.twitch.tv USERNOTICE #phaazebot
	```
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} channel='{self.room_name}' user='{self.login}'>"

	def __init__(self, raw:Optional[str]):
		# tags (ordered)
		self._msg_param_sub_plan:Optional[str] = None

		# classes
		self.Channel:Optional["TwitchChannel"] = None
		self.User:Optional["TwitchUser"] = None

		if raw:
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
		if search:
			self._msg_param_sub_plan = search.group(1)

	# extra props
	@property
	def sub_plan(self) -> str:
		return str(self._msg_param_sub_plan or "")

class StandardPayForward(UserNoticeStructure):
	"""
	eeee yeah... whatever
	Happens when someone else is gifting a sub to someone who got a sub from someone else before... thanks twitch

	Example:
	```
	@badge-info=subscriber/1;badges=subscriber/0,hype-train/2;color=#696969;display-name=The__CJ;emotes=;flags=;id=802d2f8e-99ea-4095-aa43-3cb6b72b403e;login=the__cj;mod=0;msg-id=standardpayforward;msg-param-prior-gifter-anonymous=false;msg-param-prior-gifter-display-name=Phaaze;msg-param-prior-gifter-id=123456;msg-param-prior-gifter-user-name=phaaze;msg-param-recipient-display-name=Phooze;msg-param-recipient-id=654321;msg-param-recipient-user-name=phooze;room-id=94638902;subscriber=1;system-msg=The__CJ\sis\spaying\sforward\sthe\sGift\sthey\sgot\sfrom\sPhaaze\sto\sPhooze!;tmi-sent-ts=1599426215104;user-id=67664971;user-type= :tmi.twitch.tv USERNOTICE #phaazebot
	```
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} channel='{self.room_name}' new_gifter='{self.login}' old_gifter={self.prior_gifter_user_name} to='{self.recipient_user_name}'>"

	def __init__(self, raw:Optional[str]):
		# extra tags (ordered)
		self._msg_param_prior_gifter_anonymous:Optional[bool] = None
		self._msg_param_prior_gifter_display_name:Optional[str] = None
		self._msg_param_prior_gifter_id:Optional[str] = None
		self._msg_param_prior_gifter_user_name:Optional[str] = None
		self._msg_param_recipient_display_name:Optional[str] = None
		self._msg_param_recipient_id:Optional[str] = None
		self._msg_param_recipient_user_name:Optional[str] = None

		# classes
		self.Channel:Optional["TwitchChannel"] = None
		self.Prior:Optional["TwitchUser"] = None
		self.User:Optional["TwitchUser"] = None
		self.Recipient:Optional["TwitchUser"] = None

		if raw:
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
		if search:
			self._msg_param_prior_gifter_anonymous = True if search.group(1) == "true" else False

		# _msg_param_prior_gifter_display_name
		search = re.search(ReMsgParamPriorGifterDisplayName, raw)
		if search:
			self._msg_param_prior_gifter_display_name = search.group(1)

		# _msg_param_prior_gifter_id
		search = re.search(ReMsgParamPriorGifterID, raw)
		if search:
			self._msg_param_prior_gifter_id = search.group(1)

		# _msg_param_prior_gifter_user_name
		search = re.search(ReMsgParamPriorGifterUserName, raw)
		if search:
			self._msg_param_prior_gifter_user_name = search.group(1)

		# _msg_param_recipient_display_name
		search = re.search(ReMsgParamRecipientDisplayName, raw)
		if search:
			self._msg_param_recipient_display_name = search.group(1)

		# _msg_param_recipient_id
		search = re.search(ReMsgParamRecipientID, raw)
		if search:
			self._msg_param_recipient_id = search.group(1)

		# _msg_param_recipient_user_name
		search = re.search(ReMsgParamRecipientUserName, raw)
		if search:
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

	Example:
	```
	@badge-info=subscriber/1;badges=subscriber/0;color=;display-name=The__CJ;emotes=;flags=;id=3ce64633-6bb1-4092-9f16-f1efaf1df6d8;login=the__cj;mod=0;msg-id=communitypayforward;msg-param-prior-gifter-anonymous=false;msg-param-prior-gifter-display-name=Phaaze;msg-param-prior-gifter-id=534374936;msg-param-prior-gifter-user-name=kage_ryu07;room-id=94638902;subscriber=1;system-msg=The__CJ\sis\spaying\sforward\sthe\sGift\sthey\sgot\sfrom\sPhaaze\sto\sthe\scommunity!;tmi-sent-ts=1599167980309;user-id=67664971;user-type= :tmi.twitch.tv USERNOTICE #phaazebot
	```
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} channel='{self.room_name}' user='{self.login}' old_massgifter='{self.prior_gifter_user_name}'>"

	def __init__(self, raw:Optional[str]):
		# new tags (ordered)
		self._msg_param_prior_gifter_anonymous:Optional[bool] = None
		self._msg_param_prior_gifter_display_name:Optional[str] = None
		self._msg_param_prior_gifter_id:Optional[str] = None
		self._msg_param_prior_gifter_user_name:Optional[str] = None

		# classes
		self.Channel:Optional["TwitchChannel"] = None
		self.Prior:Optional["TwitchUser"] = None
		self.User:Optional["TwitchUser"] = None

		if raw:
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
		if search:
			self._msg_param_prior_gifter_anonymous = True if search.group(1) == "true" else False

		# _msg_param_prior_gifter_display_name
		search = re.search(ReMsgParamPriorGifterDisplayName, raw)
		if search:
			self._msg_param_prior_gifter_display_name = search.group(1)

		# _msg_param_prior_gifter_id
		search = re.search(ReMsgParamPriorGifterID, raw)
		if search:
			self._msg_param_prior_gifter_id = search.group(1)

		# _msg_param_prior_gifter_user_name
		search = re.search(ReMsgParamPriorGifterUserName, raw)
		if search:
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
