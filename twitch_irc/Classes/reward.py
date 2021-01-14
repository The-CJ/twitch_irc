from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
	from .channel import Channel as TwitchChannel
	from .user import User as TwitchUser

import re
from .structure import UserNoticeStructure

from ..Utils.regex import (
	ReMsgParamSelectedCount, ReMsgParamTotalRewardCount, ReMsgParamTriggerAmount,
	ReMsgParamTriggerType, ReMsgParamDomain
)

class Reward(UserNoticeStructure):
	"""
	This Class represents a reward. Things like, unlocking emotes to random people when someone gifts subs or so.

	Example:
	```
	@badge-info=;badges=;color=#696969;display-name=The__CJ;emotes=;flags=;id=392fba88-487c-48ea-b642-4aa12dd6672d;login=the__cj;mod=0;msg-id=rewardgift;msg-param-domain=hyperscape_megacommerce;msg-param-selected-count=5;msg-param-total-reward-count=5;msg-param-trigger-amount=1;msg-param-trigger-type=SUBGIFT;room-id=94638902;subscriber=0;system-msg=The__CJ's\sGift\sshared\srewards\sto\s5\sothers\sin\sChat!;tmi-sent-ts=1598920508436;user-id=67664971;user-type= :tmi.twitch.tv USERNOTICE #phaazebot
	```
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} channel='{self.room_name}' user='{self.login}'>"

	def __init__(self, raw:Optional[str]):
		# new tags (ordered)
		self._msg_param_domain:Optional[str] = None
		self._msg_param_selected_count:Optional[int] = None
		self._msg_param_total_reward_count:Optional[int] = None
		self._msg_param_trigger_amount:Optional[int] = None
		self._msg_param_trigger_type:Optional[str] = None

		# classes
		self.Channel:Optional["TwitchChannel"] = None
		self.Gifter:Optional["TwitchUser"] = None

		if raw:
			try:
				super().__init__(raw)
				self.rewardBuild(raw)
			except:
				raise AttributeError(raw)

	# utils
	def compact(self) -> dict:
		d:dict = super().compact()
		d["domain"] = self.domain
		d["selected_count"] = self.selected_count
		d["total_reward_count"] = self.total_reward_count
		d["trigger_amount"] = self.trigger_amount
		d["trigger_type"] = self.trigger_type
		d["Channel"] = self.Channel
		d["Gifter"] = self.Gifter
		return d

	def rewardBuild(self, raw:str):
		search:re.Match

		# _msg_param_domain
		search = re.search(ReMsgParamDomain, raw)
		if search:
			self._msg_param_domain = search.group(1)

		# _msg_param_selected_count
		search = re.search(ReMsgParamSelectedCount, raw)
		if search:
			self._msg_param_selected_count = search.group(1)

		# _msg_param_total_reward_count
		search = re.search(ReMsgParamTotalRewardCount, raw)
		if search:
			self._msg_param_total_reward_count = search.group(1)

		# _msg_param_trigger_amount
		search = re.search(ReMsgParamTriggerAmount, raw)
		if search:
			self._msg_param_trigger_amount = search.group(1)

		# _msg_param_trigger_type
		search = re.search(ReMsgParamTriggerType, raw)
		if search:
			self._msg_param_trigger_type = search.group(1)

	# extra props
	@property
	def domain(self) -> str:
		return str(self._msg_param_domain or "")

	@property
	def selected_count(self) -> int:
		return int(self._msg_param_selected_count or 0)

	@property
	def total_reward_count(self) -> int:
		return int(self._msg_param_total_reward_count or 0)

	@property
	def trigger_amount(self) -> int:
		return int(self._msg_param_trigger_amount or 0)

	@property
	def trigger_type(self) -> str:
		return str(self._msg_param_trigger_type or "")
