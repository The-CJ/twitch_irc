from typing import List

import re
from .badge import Badge
from .emote import Emote
from .undefined import UNDEFINED

from ..Utils.regex import (
	ReBadgeInfo, ReBadges, ReColor,
	ReDisplayName, ReEmotes, ReID,
	ReLogin, ReRoomID, ReSystemMsg,
	ReTMISendTS, ReUserID, ReContent,
	ReRoomName
)

class GeneralTwitchTagUtils(object):
	"""
	This class contains some very basic tag-utils that are needed for most twitch stuff
	"""
	def removeTagChars(self, tag_value:str) -> str:
		"""
		removes all things that twitch replaces from tag values
		"""
		tag_value = tag_value.replace("\:", ';')
		tag_value = tag_value.replace("\s", ' ')
		tag_value = tag_value.replace("\\\\", '\\')
		return tag_value

	def buildEmotes(self, emotes_str:str, message_content:str) -> List[Emote]:
		# 25:0-4,6-10,12-16,24-28/1902:18-22,30-34

		if (not emotes_str) or (not message_content): return []
		detected_emotes:List[Emote] = []

		emote_str_list:List[str] = emotes_str.split("/")
		for emote_str in emote_str_list:
			Emo:Emote = Emote(emote_str, message_content)
			detected_emotes.append( Emo )

		return detected_emotes

	def buildBadges(self, badges_str:str) -> List[Badge]:
		# moderator/1,premium/1

		if not badges_str: return []
		detected_badges:List[Badge] = []

		badge_str_list:List[str] = badges_str.split(",")
		for badge_str in badge_str_list:
			Bad:Badge = Badge( badge_str )
			detected_badges.append( Bad )

		return detected_badges

	def buildBadgeInfo(self, badge_info_str:str) -> List[Badge]:
		# subscriber/15,somethingelse/5
		# pretty much the same as a normal badge, except it's more detailed
		# there is a badge for subscriber/24 and in info is the exact value like subscriber/26

		# good question why i made two of these function... i don't really know.
		# welp lets just reroute that and ignore it
		return self.buildBadges(badge_info_str)

	def hasBadge(self, badges:List[Badge], looking_for:str, min_version:int=0) -> bool:
		"""
		looks for a specific badge, might also enshure a minimum version of this badge if given.
		works for both, .badges and .badges_info
		```
		check_badges = [<Badge name='subscriber' version='12'>]
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

class UserNoticeStructure(GeneralTwitchTagUtils):
	"""
	Every USERNOTICE has a set array of twitch-tags that are alway given,
	this class is suppost to cover the basic tags and also the prop functions attached to it,
	It will make a basic process in .build and call .extraBuild after basic proccess is done,
	.extraBuild should be overwritten by all subclasses
	"""
	def __init__(self, raw:str or None):
		# tags (ordered)
		self._badges_info:List[Badge] = []
		self._badges:List[Badge] = []
		self._color:str = UNDEFINED
		self._display_name:str = UNDEFINED
		self._emotes:List[Emote] = []
		self._id:str = UNDEFINED
		self._login:str = UNDEFINED
		self._room_id:str = UNDEFINED
		self._system_msg:str = UNDEFINED
		self._tmi_sent_ts:str = UNDEFINED
		self._user_id:str = UNDEFINED
		self._content:str = UNDEFINED

		# others
		self._room_name:str = UNDEFINED

		# raw data / utils
		self._emote_str:str = UNDEFINED
		self._badge_str:str = UNDEFINED
		self._badge_info_str:str = UNDEFINED

		if raw != None:
			try:
				self.build(raw)
				self.extraBuild(raw)
			except:
				raise AttributeError(raw)

	def compact(self) -> dict:
		d:dict = {}
		d["badges_info"] = self.badges_info
		d["badges"] = self.badges
		d["color"] = self.color
		d["display_name"] = self.display_name
		d["emotes"] = self.emotes
		d["msg_id"] = self.msg_id
		d["login"] = self.login
		d["mod"] = self.mod
		d["partner"] = self.partner
		d["room_id"] = self.room_id
		d["subscriber"] = self.subscriber
		d["system_msg"] = self.system_msg
		d["tmi_sent_ts"] = self.tmi_sent_ts
		d["turbo"] = self.turbo
		d["user_id"] = self.user_id
		d["vip"] = self.vip
		d["room_name"] = self.room_name
		return d

	# utils
	def build(self, raw:str) -> None:
		search:re.Match

		# _badge_info_str
		search = re.search(ReBadgeInfo, raw)
		if search != None:
			self._badge_info_str = search.group(1)

		# _badge_str
		search = re.search(ReBadges, raw)
		if search != None:
			self._badge_str = search.group(1)

		# _color
		search = re.search(ReColor, raw)
		if search != None:
			self._color = search.group(1)

		# _display_name
		search = re.search(ReDisplayName, raw)
		if search != None:
			self._display_name = search.group(1)

		# _emote_str
		search = re.search(ReEmotes, raw)
		if search != None:
			self._emote_str = search.group(1)

		# _id
		search = re.search(ReID, raw)
		if search != None:
			self._id = search.group(1)

		# _login
		search = re.search(ReLogin, raw)
		if search != None:
			self._login = search.group(1)

		# _room_id
		search = re.search(ReRoomID, raw)
		if search != None:
			self._room_id = search.group(1)

		# _system_msg
		search = re.search(ReSystemMsg, raw)
		if search != None:
			self._system_msg = self.removeTagChars( search.group(1) )

		# _tmi_sent_ts
		search = re.search(ReTMISendTS, raw)
		if search != None:
			self._tmi_sent_ts = search.group(1)

		# _user_id
		search = re.search(ReUserID, raw)
		if search != None:
			self._user_id = search.group(1)

		# _content
		search = re.search(ReContent, raw)
		if search != None:
			self._content = search.group(1)

		# _room_name
		search = re.search(ReRoomName, raw)
		if search != None:
			self._room_name = search.group(1)

		# generate other data
		self._badges_info = self.buildBadgeInfo(self._badge_info_str)
		self._badges = self.buildBadges(self._badge_str)
		self._emotes = self.buildEmotes(self._emote_str, self._content)

	def extraBuild(self, raw:str) -> None:
		pass

	# props
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
	def user_display_name(self) -> str:
		return self.display_name

	@property
	def emotes(self) -> List[Emote]:
		return self._emotes

	@property
	def id(self) -> str:
		return str(self._id or "")
	@property
	def msg_id(self) -> str:
		return self.id

	@property
	def login(self) -> str:
		return str(self._login or "")
	@property
	def user_name(self) -> str:
		return str(self._login or "")

	@property
	def mod(self) -> bool:
		if self.hasBadge(self.badges, "moderator"): return True
		if self.hasBadge(self.badges, "broadcaster"): return True
		if self.hasBadge(self.badges, "admin"): return True
		if self.hasBadge(self.badges, "staff"): return True
		return False

	@property
	def partner(self) -> bool:
		if self.hasBadge(self.badges, "partner"): return True
		return False

	@property
	def room_id(self) -> str:
		return str(self._room_id or "")
	@property
	def channel_id(self) -> str:
		return self.room_id

	@property
	def subscriber(self) -> bool:
		if self.hasBadge(self.badges, "subscriber"): return True
		if self.hasBadge(self.badges_info, "subscriber"): return True
		if self.hasBadge(self.badges, "founder"): return True
		return False

	@property
	def system_msg(self) -> str:
		return str(self._system_msg or "")

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
	def vip(self) -> bool:
		if self.hasBadge(self.badges, "vip"): return True
		return False

	@property
	def room_name(self) -> str:
		return str(self._room_name or "")
	@property
	def channel_name(self) -> str:
		return self.room_name
