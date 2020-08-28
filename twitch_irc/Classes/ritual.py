from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from .channel import Channel as TwitchChannel
    from .user import User as TwitchUser

import re
from .emote import Emote
from .badge import Badge
from .undefined import UNDEFINED

from ..Utils.regex import (
	ReBadgeInfo, ReBadges, ReColor,
	ReDisplayName, ReEmotes, ReID,
	ReLogin, ReMod, ReMsgParamRitualName,
	ReRoomID, ReSubscriber, ReSystemMsg,
	ReTMISendTS, ReTurbo, ReUserID,
	ReUserType, ReRoomName, ReContent
)

class Ritual(object):
	"""
	So rituals are a new(?) thing in twitch and they may appear on multiple channel and or user related events,
	however, currently its only used in one case, the 'new_chatter' event.
	More might come at some point.
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} channel='{self.room_name}' event='{self.ritual_name}'>"

	def __init__(self, raw:str or None):
		# tags (ordered)
		self._badges_info:List[Badge] = []
		self._badges:List[Badge] = []
		self._color:str = UNDEFINED
		self._display_name:str = UNDEFINED
		self._emotes:List[Emote] = []
		self._id:str = UNDEFINED
		self._login:str = UNDEFINED
		self._mod:bool = UNDEFINED
		self._msg_param_ritual_name:str = UNDEFINED
		self._room_id:str = UNDEFINED
		self._subscriber:bool = UNDEFINED
		self._system_msg:str = UNDEFINED
		self._tmi_sent_ts:str = UNDEFINED
		self._turbo:bool = UNDEFINED
		self._user_id:str = UNDEFINED
		self._user_type:str = UNDEFINED

		# others
		self._room_name:str = UNDEFINED

		# classes
		self.Channel:"TwitchChannel" = None
		self.User:"TwitchUser" = None

		# raw data / utils
		self._emote_str:str = UNDEFINED
		self._badge_str:str = UNDEFINED
		self._badge_info_str:str = UNDEFINED

		if raw != None:
			try:
				self.build(raw)
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
		d["ritual_name"] = self.ritual_name
		d["room_id"] = self.room_id
		d["subscriber"] = self.subscriber
		d["system_msg"] = self.system_msg
		d["tmi_sent_ts"] = self.tmi_sent_ts
		d["turbo"] = self.turbo
		d["user_id"] = self.user_id
		d["user_type"] = self.user_type
		d["room_name"] = self.room_name
		d["Channel"] = self.Channel
		d["User"] = self.User
		return d

	# utils
	def build(self, raw:str):
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

		# _mod
		search = re.search(ReMod, raw)
		if search != None:
			self._mod = True if search.group(1) == "1" else False

		# _msg_param_ritual_name
		search = re.search(ReMsgParamRitualName, raw)
		if search != None:
			self._msg_param_ritual_name = search.group(1)

		# _room_id
		search = re.search(ReRoomID, raw)
		if search != None:
			self._room_id = search.group(1)

		# _subscriber
		search = re.search(ReSubscriber, raw)
		if search != None:
			self._subscriber = True if search.group(1) == "1" else False

		# _system_msg
		search = re.search(ReSystemMsg, raw)
		if search != None:
			self._system_msg = self.removeTagChars( search.group(1) )

		# _tmi_sent_ts
		search = re.search(ReTMISendTS, raw)
		if search != None:
			self._tmi_sent_ts = search.group(1)

		# _turbo
		search = re.search(ReTurbo, raw)
		if search != None:
			self._turbo = True if search.group(1) == "1" else False

		# _user_id
		search = re.search(ReUserID, raw)
		if search != None:
			self._user_id = search.group(1)

		# _user_type
		search = re.search(ReUserType, raw)
		if search != None:
			self._user_type = search.group(1)

		# _room_name
		search = re.search(ReRoomName, raw)
		if search != None:
			self._room_name = search.group(1)

		# _content
		search = re.search(ReContent, raw)
		if search != None:
			self._content = search.group(2)

		# generate other data
		self.buildEmotes(self._emote_str)
		self.buildBadges(self._badge_str)
		self.buildBadgeInfo(self._badge_info_str)

	def buildEmotes(self, emotes_str:str) -> None:
		# 25:0-4,6-10,12-16,24-28/1902:18-22,30-34

		if not emotes_str: return

		emote_str_list:List[str] = emotes_str.split("/")
		for emote_str in emote_str_list:
			Emo:Emote = Emote(emote_str, self.content)
			self._emotes.append( Emo )

	def buildBadges(self, badges_str:str) -> None:
		# moderator/1,premium/1

		if not badges_str: return

		badge_str_list:List[str] = badges_str.split(",")
		for badge_str in badge_str_list:
			Bad:Badge = Badge( badge_str )
			self._badges.append( Bad )

	def buildBadgeInfo(self, badge_info_str:str) -> None:
		# subscriber/15,somethingelse/5
		# pretty much the same as a normal badge, except it's more detailed
		# there is a badge for subscriber/24 and in info is the exact value like subscriber/26

		if not badge_info_str: return

		badge_str_list:List[str] = badge_info_str.split(",")
		for badge_str in badge_str_list:
			Bad:Badge = Badge( badge_str )
			self._badges_info.append( Bad )

	def removeTagChars(self, tag_value:str) -> str:
		"""
		removes all things that twitch replaces from tag values
		"""
		tag_value = tag_value.replace("\:", ';')
		tag_value = tag_value.replace("\s", ' ')
		tag_value = tag_value.replace("\\\\", '\\')
		return tag_value

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
		return str(self._display_name or "")

	@property
	def emotes(self) -> List[Emote]:
		return self._emotes

	@property
	def id(self) -> str:
		return str(self._id or "")
	@property
	def msg_id(self) -> str:
		return str(self._id or "")

	@property
	def login(self) -> str:
		return str(self._login or "")
	@property
	def user_name(self) -> str:
		return str(self._login or "")

	@property
	def mod(self) -> bool:
		return bool(self._mod)

	@property
	def ritual_name(self) -> str:
		return str(self._msg_param_ritual_name or "")

	@property
	def room_id(self) -> str:
		return str(self._room_id or "")
	@property
	def channel_id(self) -> str:
		return str(self._room_id or "")

	@property
	def subscriber(self) -> bool:
		return bool(self._subscriber)

	@property
	def system_msg(self) -> str:
		return str(self._system_msg or "")

	@property
	def tmi_sent_ts(self) -> str:
		return str(self._tmi_sent_ts or "")

	@property
	def turbo(self) -> bool:
		return bool(self._turbo)

	@property
	def user_id(self) -> str:
		return str(self._user_id or "")

	@property
	def user_type(self) -> str:
		return str(self._user_type or "")

	@property
	def room_name(self) -> str:
		return str(self._room_name or "")
	@property
	def channel_name(self) -> str:
		return str(self._room_name or "")
