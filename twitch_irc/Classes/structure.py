from typing import List, Optional

import re
from .badge import Badge
from .emote import Emote

from ..Utils.regex import (
	ReBadgeInfo, ReBadges, ReColor,
	ReDisplayName, ReEmotes, ReID,
	ReLogin, ReMod, ReRoomID,
	ReSystemMsg, ReTMISendTS, ReUserID,
	ReContent, ReRoomName
)

class GeneralTwitchTagUtils(object):
	"""
	This class contains some very basic tag-utils that are needed for most twitch stuff
	"""
	@staticmethod
	def removeTagChars(tag_value:str) -> str:
		"""
		removes all things that twitch replaces from tag values
		"""
		tag_value = tag_value.replace("\:", ';')
		tag_value = tag_value.replace("\s", ' ')
		tag_value = tag_value.replace("\\\\", '\\')
		return tag_value

	@staticmethod
	def buildEmotes(emotes_str:str, message_content:str) -> List[Emote]:
		# 25:0-4,6-10,12-16,24-28/1902:18-22,30-34

		if (not emotes_str) or (not message_content): return []
		detected_emotes:List[Emote] = []

		emote_str_list:List[str] = emotes_str.split("/")
		for emote_str in emote_str_list:
			Emo:Emote = Emote(emote_str, message_content)
			detected_emotes.append(Emo)

		return detected_emotes

	@staticmethod
	def buildBadges(badges_str:str) -> List[Badge]:
		# moderator/1,premium/1

		if not badges_str: return []
		detected_badges:List[Badge] = []

		badge_str_list:List[str] = badges_str.split(",")
		for badge_str in badge_str_list:
			Bad:Badge = Badge(badge_str)
			detected_badges.append(Bad)

		return detected_badges

	def buildBadgeInfo(self, badge_info_str:str) -> List[Badge]:
		# subscriber/15,somethingelse/5
		# pretty much the same as a normal badge, except it's more detailed
		# there is a badge for subscriber/24 and in info is the exact value like subscriber/26

		# good question why i made two of these function... i don't really know.
		# welp lets just reroute that and ignore it
		return self.buildBadges(badge_info_str)

	@staticmethod
	def hasBadge(badges:List[Badge], looking_for:str, min_version:int=0) -> bool:
		"""
		looks for a specific badge, might also ensure a minimum version of this badge if given.
		works for both, .badges and .badges_info
		```
		check_badges = [<Badge name='subscriber' version='9'>]
		hasBadge(check_badges, "subscriber") -> True
		hasBadge(check_badges, "subscriber", 6) -> True
		hasBadge(check_badges, "subscriber", 12) -> False
		hasBadge(check_badges, "premium") -> False
		```
		"""
		for Bad in badges:
			if Bad.name.lower() == looking_for.lower():
				if min_version: return bool(Bad.version >= min_version)
				return True

		return False

class BasicEventStructure(GeneralTwitchTagUtils):
	"""
	A big amount of events has a real basic array of tags.
	of course there are some that have even less.
	But at least PRIVMSG and USERNOTICE share most of them
	"""
	def __init__(self, raw:Optional[str]):
		# base tags (ordered)
		self._badges_info:List[Badge] = []
		self._badges:List[Badge] = []
		self._color:Optional[str] = None
		self._display_name:Optional[str] = None
		self._emotes:List[Emote] = []
		self._id:Optional[str] = None
		self._mod:Optional[bool] = None
		self._room_id:Optional[str] = None
		self._tmi_sent_ts:Optional[str] = None
		self._user_id:Optional[str] = None
		self._content:Optional[str] = None

		# others
		self._room_name:Optional[str] = None

		# raw data / utils
		self._emote_str:Optional[str] = None
		self._badge_str:Optional[str] = None
		self._badge_info_str:Optional[str] = None

		if raw:
			try:
				self.basicEventStructureBuild(raw)
			except:
				raise AttributeError(raw)

	# utils
	def compact(self) -> dict:
		d:dict = dict()
		d["badges_info"] = self.badges_info
		d["badges"] = self.badges
		d["color"] = self.color
		d["display_name"] = self.display_name
		d["emotes"] = self.emotes
		d["msg_id"] = self.msg_id
		d["mod"] = self.mod
		d["partner"] = self.partner
		d["room_id"] = self.room_id
		d["subscriber"] = self.subscriber
		d["tmi_sent_ts"] = self.tmi_sent_ts
		d["turbo"] = self.turbo
		d["user_id"] = self.user_id
		d["vip"] = self.vip
		d["room_name"] = self.room_name
		return d

	def basicEventStructureBuild(self, raw:str) -> None:
		search:re.Match

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

		# _display_name
		search = re.search(ReDisplayName, raw)
		if search:
			self._display_name = search.group(1)

		# _emote_str
		search = re.search(ReEmotes, raw)
		if search:
			self._emote_str = search.group(1)

		# _id
		search = re.search(ReID, raw)
		if search:
			self._id = search.group(1)

		# _mod
		search = re.search(ReMod, raw)
		if search:
			self._mod = True if search.group(1) == '1' else False

		# _room_id
		search = re.search(ReRoomID, raw)
		if search:
			self._room_id = search.group(1)

		# _tmi_sent_ts
		search = re.search(ReTMISendTS, raw)
		if search:
			self._tmi_sent_ts = search.group(1)

		# _user_id
		search = re.search(ReUserID, raw)
		if search:
			self._user_id = search.group(1)

		# _content
		search = re.search(ReContent, raw)
		if search:
			self._content = search.group(1)

		# _room_name
		search = re.search(ReRoomName, raw)
		if search:
			self._room_name = search.group(1)

		# generate other data
		self._badges_info = self.buildBadgeInfo(self._badge_info_str)
		self._badges = self.buildBadges(self._badge_str)
		self._emotes = self.buildEmotes(self._emote_str, self._content)

	# base props
	@property
	def badges_info(self) -> List[Badge]:
		return self._badges_info

	@property
	def badges(self) -> List[Badge]:
		return self._badges

	@property
	def color(self) -> str:
		return str(self._color or "")

	@property
	def display_name(self) -> str:
		return str(self._display_name or "")

	@property
	def emotes(self) -> List[Emote]:
		return self._emotes

	@property
	def emote_count(self) -> int:
		return sum(Emo.count for Emo in self.emotes)

	@property
	def id(self) -> str:
		return str(self._id or "")

	@property
	def msg_id(self) -> str:
		return self.id

	@property
	def mod(self) -> bool:
		if self.hasBadge(self.badges, "moderator"): return True
		if self.hasBadge(self.badges, "broadcaster"): return True
		if self.hasBadge(self.badges, "admin"): return True
		if self.hasBadge(self.badges, "staff"): return True
		if self._mod: return True
		return False

	@property
	def partner(self) -> bool:
		if self.hasBadge(self.badges, "partner"): return True
		return False

	@property
	def room_id(self) -> str:
		return str(self._room_id or "")

	@property
	def subscriber(self) -> bool:
		if self.hasBadge(self.badges, "subscriber"): return True
		if self.hasBadge(self.badges_info, "subscriber"): return True
		if self.hasBadge(self.badges, "founder"): return True
		return False

	@property
	def tmi_sent_ts(self) -> str:
		return str(self._tmi_sent_ts or "")

	@property
	def turbo(self) -> bool:
		if self.hasBadge(self.badges, "turbo"): return True
		return False

	@property
	def user_id(self) -> str:
		return str(self._user_id or "")

	@property
	def room_name(self) -> str:
		return str(self._room_name or "")

	@property
	def vip(self) -> bool:
		if self.hasBadge(self.badges, "vip"): return True
		return False

class UserNoticeStructure(BasicEventStructure):
	"""
	Every USERNOTICE has a set array of twitch-tags that are always given,
	this class is suppose to cover the basic tags and also the extra prop functions attached to it.
	"""
	def __init__(self, raw:Optional[str]):
		# new tags (ordered)
		self._login:Optional[str] = None
		self._system_msg:Optional[str] = None

		if raw:
			try:
				super().__init__(raw)
				self.userNoticeStructureBuild(raw)
			except:
				raise AttributeError(raw)

	def compact(self) -> dict:
		d:dict = super().compact()
		d["login"] = self.login
		d["system_msg"] = self.system_msg
		return d

	# utils
	def userNoticeStructureBuild(self, raw:str) -> None:
		search:re.Match

		# _login
		search = re.search(ReLogin, raw)
		if search:
			self._login = search.group(1)

		# _system_msg
		search = re.search(ReSystemMsg, raw)
		if search:
			self._system_msg = self.removeTagChars(search.group(1))

	# props
	@property
	def login(self) -> str:
		return str(self._login or "")

	@property
	def system_msg(self) -> str:
		return str(self._system_msg or "")
