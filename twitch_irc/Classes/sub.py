from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
	from .channel import Channel as TwitchChannel
	from .user import User as TwitchUser

import re
from .structure import UserNoticeStructure

from ..Utils.regex import (
	ReMsgParamCumulativeMonths,	ReMsgParamStreakMonths,	ReMsgParamShouldShareStreak,
	ReMsgParamSubPlan, ReMsgParamSubPlanName, ReMsgParamSenderCount,
	ReMsgParamRecipientUserName, ReMsgParamRecipientID, ReMsgParamRecipientDisplayName,
	ReMsgParamMounths, ReMsgParamGiftMounths
)

class Sub(UserNoticeStructure):
	"""
	This Class represents a sub, a very normal sub where the user uses money or prime to subscribe...
	remember that, because oooo boi, resubs will be a fucking mess

	Example raw:
	```
	@badge-info=;badges=premium/1;color=#FF69B4;display-name=The__CJ;emotes=;flags=;id=fa1b33c6-0056-4cac-b7fd-dc1b2d5f2635;login=the__cj;mod=0;msg-id=sub;msg-param-cumulative-months=1;msg-param-months=0;msg-param-should-share-streak=0;msg-param-sub-plan-name=Name;msg-param-sub-plan=Prime;msg-param-was-gifted=false;room-id=94638902;subscriber=1;system-msg=The__CJ\ssubscribed\swith\sTwitch\sPrime.;tmi-sent-ts=1598919867774;user-id=67664971;user-type= :tmi.twitch.tv USERNOTICE #phaazebot
	```
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} channel='{self.room_name}' user='{self.login}'>"

	def __init__(self, raw:str or None):
		# extra tags (ordered)
		self._msg_param_cumulative_months:Optional[int] = None
		self._msg_param_streak_months:Optional[int] = None
		self._msg_param_should_share_streak:Optional[bool] = None
		self._msg_param_sub_plan:Optional[str] = None
		self._msg_param_sub_plan_name:Optional[str] = None

		# classes
		self.Channel:Optional["TwitchChannel"] = None
		self.User:Optional["TwitchUser"] = None

		if raw:
			try:
				super().__init__(raw)
				self.subBuild(raw)
			except:
				raise AttributeError(raw)

	# utils
	def compact(self) -> dict:
		d:dict = super().compact()
		d["cumulative_months"] = self.cumulative_months
		d["streak_months"] = self.streak_months
		d["should_share_streak"] = self.should_share_streak
		d["sub_plan"] = self.sub_plan
		d["sub_plan_name"] = self.sub_plan_name
		return d

	def subBuild(self, raw:str):
		search:re.Match

		# _msg_param_cumulative_months
		search = re.search(ReMsgParamCumulativeMonths, raw)
		if search:
			self._msg_param_cumulative_months = search.group(1)

		# _msg_param_streak_months
		search = re.search(ReMsgParamStreakMonths, raw)
		if search:
			self._msg_param_streak_months = search.group(1)

		# _msg_param_should_share_streak
		search = re.search(ReMsgParamShouldShareStreak, raw)
		if search:
			self._msg_param_should_share_streak = True if search.group(1) == "1" else False

		# _msg_param_sub_plan
		search = re.search(ReMsgParamSubPlan, raw)
		if search:
			self._msg_param_sub_plan = search.group(1)

		# _msg_param_sub_plan_name
		search = re.search(ReMsgParamSubPlanName, raw)
		if search:
			self._msg_param_sub_plan_name = self.removeTagChars(search.group(1))

	# extra props
	@property
	def cumulative_months(self) -> int:
		return int(self._msg_param_cumulative_months or 0)

	@property
	def streak_months(self) -> int:
		return int(self._msg_param_streak_months)

	@property
	def should_share_streak(self) -> bool:
		return bool(self._msg_param_should_share_streak)

	@property
	def sub_plan(self) -> str:
		return str(self._msg_param_sub_plan or "")

	@property
	def sub_plan_name(self) -> str:
		return str(self._msg_param_sub_plan_name or "")

class GiftSub(UserNoticeStructure):
	"""
	This Class represents a giftsub, aka the process of someone gifting a sub to someone (NOT A RESUB)

	Example raw:
	```
	@badge-info=;badges=;color=#696969;display-name=The__CJ;emotes=;flags=;id=aad1937c-2cce-44f3-9c90-a1d73d4fbd4d;login=the__cj;mod=0;msg-id=subgift;msg-param-gift-months=1;msg-param-months=1;msg-param-origin-id=da\s39\sa3\see\s5e\s6b\s4b\s0d\s32\s55\sbf\sef\s95\s60\s18\s90\saf\sd8\s07\s09;msg-param-recipient-display-name=Phaaze;msg-param-recipient-id=123456789;msg-param-recipient-user-name=phaaze;msg-param-sender-count=1;msg-param-sub-plan-name=Name;msg-param-sub-plan=1000;room-id=94638902;subscriber=0;system-msg=The__CJ\sgifted\sa\sTier\s1\ssub\sto\sPhaaze!\sThis\sis\stheir\sfirst\sGift\sSub\sin\sthe\schannel!;tmi-sent-ts=1598920507127;user-id=67664971;user-type= :tmi.twitch.tv USERNOTICE #phaazebot
	```
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} channel='{self.room_name}' from='{self.login}' to='{self.recipient_user_name}'>"

	def __init__(self, raw:str or None):
		# new tags (ordered)
		self._msg_param_gift_months:Optional[int] = None
		self._msg_param_months:Optional[int] = None
		self._msg_param_recipient_display_name:Optional[str] = None
		self._msg_param_recipient_id:Optional[str] = None
		self._msg_param_recipient_user_name:Optional[str] = None
		self._msg_param_sender_count:Optional[int] = None
		self._msg_param_sub_plan:Optional[str] = None
		self._msg_param_sub_plan_name:Optional[str] = None

		# classes
		self.Channel:Optional["TwitchChannel"] = None
		self.Gifter:Optional["TwitchUser"] = None
		self.Recipient:Optional["TwitchUser"] = None

		if raw:
			try:
				super().__init__(raw)
				self.giftSubBuild(raw)
			except:
				raise AttributeError(raw)

	# utils
	def compact(self) -> dict:
		d:dict = super().compact()
		d["gift_months"] = self.gift_months
		d["months"] = self.months
		d["recipient_display_name"] = self.recipient_display_name
		d["recipient_id"] = self.recipient_id
		d["recipient_user_name"] = self.recipient_user_name
		d["sender_count"] = self.sender_count
		d["sub_plan"] = self.sub_plan
		d["sub_plan_name"] = self.sub_plan_name
		d["Channel"] = self.Channel
		d["Gifter"] = self.Gifter
		d["Recipient"] = self.Recipient
		return d

	def giftSubBuild(self, raw:str):
		search:re.Match

		# _msg_param_gift_months
		search = re.search(ReMsgParamGiftMounths, raw)
		if search:
			self._msg_param_gift_months = search.group(1)

		# _msg_param_months
		search = re.search(ReMsgParamMounths, raw)
		if search:
			self._msg_param_months = search.group(1)

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

		# _msg_param_sender_count
		search = re.search(ReMsgParamSenderCount, raw)
		if search:
			self._msg_param_sender_count = search.group(1)

		# _msg_param_sub_plan
		search = re.search(ReMsgParamSubPlan, raw)
		if search:
			self._msg_param_sub_plan = search.group(1)

		# _msg_param_sub_plan_name
		search = re.search(ReMsgParamSubPlanName, raw)
		if search:
			self._msg_param_sub_plan_name = self.removeTagChars(search.group(1))

	@property
	def gift_months(self) -> int:
		return int(self._msg_param_gift_months or 0)

	@property
	def months(self) -> int:
		return int(self._msg_param_months or 0)

	@property
	def recipient_display_name(self) -> str:
		return str(self._msg_param_recipient_display_name or "")

	@property
	def recipient_id(self) -> str:
		return str(self._msg_param_recipient_id or "")

	@property
	def recipient_user_name(self) -> str:
		return str(self._msg_param_recipient_user_name or "")

	@property
	def sender_count(self) -> int:
		return int(self._msg_param_sender_count or 0)

	@property
	def sub_plan(self) -> str:
		return str(self._msg_param_sub_plan or "")

	@property
	def sub_plan_name(self) -> str:
		return str(self._msg_param_sub_plan_name or "")
