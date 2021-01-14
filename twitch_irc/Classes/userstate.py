from typing import List, Optional

import re
from .badge import Badge

from ..Utils.regex import (
	ReBadgeInfo, ReBadges, ReColor,
	ReDisplayName, ReSubscriber, ReMod,
	ReTurbo, ReUserType, ReRoomName
)

class UserState(object):
	"""
	This class is generated when the bot join's a chat room and whenever a PRIVMSG is send,
	it's suppose to act as a permission class, so custom code can see that the client's user is a mod in in channel X
	or has a sub badge for XX months, etc.
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} for channel: '{self.room_name}'>"

	def __init__(self, raw:Optional[str]):
		# tags (ordered)
		self._badges_info:List[Badge] = []
		self._badges:List[Badge] = []
		self._color:Optional[str] = None
		self._display_name:Optional[str] = None
		self._mod:Optional[bool] = None
		self._subscriber:Optional[bool] = None
		self._turbo:Optional[bool] = None
		self._user_type:Optional[str] = None

		# other
		self._room_name:Optional[str] = None

		# raw data / utils
		self._badge_str:Optional[str] = None
		self._badge_info_str:Optional[str] = None

		if raw:
			try:
				self.build(raw)
			except:
				raise AttributeError(raw)

	def compact(self) -> dict:
		d:dict = dict()
		d["badges_info"] = self.badges_info
		d["badges"] = self.badges
		d["color"] = self.color
		d["display_name"] = self.display_name
		d["mod"] = self.mod
		d["subscriber"] = self.subscriber
		d["turbo"] = self.turbo
		d["room_name"] = self.room_name
		return d

	# utils
	def build(self, raw:str) -> None:
		"""
		```
		@badge-info=;badges=broadcaster/1;color=#1E90FF;display-name=Phaazebot;emote-sets=0,472873131;mod=0;subscriber=0;user-type= :tmi.twitch.tv USERSTATE #phaazebot
		```
		"""
		# _badge_info_str
		search = re.search(ReBadgeInfo, raw)
		if search:
			self._badge_info_str = search.group(1)

		# _badge_str
		search = re.search(ReBadges, raw)
		if search:
			self._badge_str = search.group(1)

		# _color
		search = re.search(ReColor, raw)
		if search:
			self._color = search.group(1)

		# _user_display_name
		search = re.search(ReDisplayName, raw)
		if search:
			self._display_name = search.group(1)

		# _mod
		search = re.search(ReMod, raw)
		if search:
			self._mod = True if search.group(1) == "1" else False

		# _subscriber
		search = re.search(ReSubscriber, raw)
		if search:
			self._subscriber = True if search.group(1) == "1" else False

		# _turbo
		search = re.search(ReTurbo, raw)
		if search:
			self._turbo = True if search.group(1) == "1" else False

		# _user_type
		search = re.search(ReUserType, raw)
		if search:
			self._user_type = search.group(1)

		# _room_name
		search = re.search(ReRoomName, raw)
		if search:
			self._room_name = search.group(1)

		# generate other data
		self.buildBadges(self._badge_str)
		self.buildBadgeInfo(self._badge_info_str)

	def buildBadges(self, badges_str:str) -> None:
		# moderator/1,premium/1

		if not badges_str: return

		badge_str_list:List[str] = badges_str.split(",")
		for badge_str in badge_str_list:
			Bad:Badge = Badge(badge_str)
			self._badges.append(Bad)

	def buildBadgeInfo(self, badge_info_str:str) -> None:
		# subscriber/15,somethingelse/5
		# pretty much the same as a normal badge, except it's more detailed
		# there is a badge for subscriber/24 and in info is the exact value like subscriber/26

		if not badge_info_str: return

		badge_str_list:List[str] = badge_info_str.split(",")
		for badge_str in badge_str_list:
			Bad:Badge = Badge(badge_str)
			self._badges_info.append(Bad)

	# props
	@property
	def badges_info(self) -> List[Badge]:
		return self._badges_info

	@property
	def badges(self) -> List[Badge]:
		return self._badges

	@property
	def color(self) -> str or None:
		return str(self._color or "")

	@property
	def user_display_name(self) -> str:
		return str(self._display_name or "")

	@property
	def display_name(self) -> str:
		return str(self._display_name or "")

	@property
	def mod(self) -> bool:
		return bool(self._mod)

	@property
	def subscriber(self) -> bool:
		return bool(self._subscriber)

	@property
	def turbo(self) -> bool:
		return bool(self._turbo)

	@property
	def user_type(self) -> str:
		return str(self._user_type or "")

	@property
	def room_name(self) -> str:
		return str(self._room_name or "")

	@property
	def channel_name(self) -> str:
		return str(self._room_name or "")
