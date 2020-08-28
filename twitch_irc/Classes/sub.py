from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .channel import Channel as TwitchChannel
    from .user import User as TwitchUser

import re
from .structure import UserNoticeStructure
from .undefined import UNDEFINED

from ..Utils.regex import (
	ReMsgParamCumulativeMonths,	ReMsgParamStreakMonths, ReMsgParamShouldShareStreak,
	ReMsgParamSubPlan, ReMsgParamSubPlanName
)

class Sub(UserNoticeStructure):
	"""
	This Class represents a sub, a very normal sub where the user uses money or prime to subscribe...
	remember that, because oooo boi, resubs will be a fucking mess
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} channel='{self.room_name}' user='{self.login}'>"

	def __init__(self, raw:str or None):
		# extra tags (ordered)
		self._msg_param_cumulative_months:int = UNDEFINED
		self._msg_param_streak_months:int = UNDEFINED
		self._msg_param_should_share_streak:bool = UNDEFINED
		self._msg_param_sub_plan:str = UNDEFINED
		self._msg_param_sub_plan_name:str = UNDEFINED

		# classes
		self.Channel:"TwitchChannel" = None
		self.User:"TwitchUser" = None

		if raw != None:
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
		if search != None:
			self._msg_param_cumulative_months = search.group(1)

		# _msg_param_streak_months
		search = re.search(ReMsgParamStreakMonths, raw)
		if search != None:
			self._msg_param_streak_months = search.group(1)

		# _msg_param_should_share_streak
		search = re.search(ReMsgParamShouldShareStreak, raw)
		if search != None:
			self._msg_param_should_share_streak = True if search.group(1) == "1" else False

		# _msg_param_sub_plan
		search = re.search(ReMsgParamSubPlan, raw)
		if search != None:
			self._msg_param_sub_plan = search.group(1)

		# _msg_param_sub_plan_name
		search = re.search(ReMsgParamSubPlanName, raw)
		if search != None:
			self._msg_param_sub_plan_name = self.removeTagChars( search.group(1) )

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
