from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from .channel import Channel as TwitchChannel
    from .user import User as TwitchUser

import re
from .emote import Emote
from .badge import Badge
from .undefined import UNDEFINED

# odered by twitch tag list (string position, which is also alphabetical)
ReBadgeInfo:"re.Pattern" = re.compile(r"") # maybe TODO
ReBadges:"re.Pattern" = re.compile(r"[@; ]badges=(\S*?)[; ]")
ReBits:"re.Pattern" = re.compile(r"") # TODO
ReColor:"re.Pattern" = re.compile(r"[@; ]color=#([0-9a-fA-F]*?)[; ]")
ReDisplayName:"re.Pattern" = re.compile(r"[@; ]display-name=(\S*?)[; ]")
ReEmotes:"re.Pattern" = re.compile(r"[@; ]emotes=([0-9:,-]*?)[; ]")
ReMsgID:"re.Pattern" = re.compile(r"[@; ]id=([A-Za-z0-9-]*?)[; ]")
ReMod:"re.Pattern" = re.compile(r"[@; ]mod=(0|1)[; ]")
ReRoomID:"re.Pattern" = re.compile(r"[@; ]room-id=(\d*?)[; ]")
ReSub:"re.Pattern" = re.compile(r"[@; ]subscriber=(0|1)[; ]")
ReTMISendTS:"re.Pattern" = re.compile(r"[@; ]tmi-sent-ts=(\d*?)[; ]")
ReTurbo:"re.Pattern" = re.compile(r"[@; ]turbo=(0|1)[; ]")
ReUserID:"re.Pattern" = re.compile(r"[@; ]user-id=(\d*?)[; ]")
ReUserType:"re.Pattern" = re.compile(r"[@; ]user-type=(\S*?)[; ]")

# the rest values we also get out of the message, but its not via twitch tags
ReName:"re.Pattern" = re.compile(r"[@; ]:(\S*?)!(\S*?)@(\S*?)\.tmi\.twitch\.tv[; ]")
ReContent:"re.Pattern" = re.compile(r"[@; ]PRIVMSG #(\S+?) :(.+)")

class Message(object):
	"""
	This class is generated when a user is sending a message, it turns raw data like:

	@badges=moderator/1,premium/1;color=#696969;display-name=The__CJ;emotes=25:6-10;id=13e484e8-1d0d-44c0-8b1e-03d76b636688;mod=1;room-id=94638902;subscriber=0;tmi-sent-ts=1525706672840;turbo=0;user-id=67664971;user-type=mod :the__cj!the__cj@the__cj.tmi.twitch.tv	PRIVMSG #phaazebot :Hello Kappa /

	into a usable class
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} channel='{self.channel_name}' author='{self.user_name}'>"

	def __str__(self):
		return self.content or ""

	def __init__(self, raw:str):
		# self.badge_info:str = None
		self._badge_str:str = UNDEFINED
		self._badges:List[Badge] = []
		# self._bits:int = 0
		self._color:str = UNDEFINED
		self._user_display_name:str = UNDEFINED
		self._emote_str:str = UNDEFINED
		self._emotes:List[Emote] = []
		self._msg_id:str = UNDEFINED
		self._mod:bool = False
		self._room_id:str = UNDEFINED
		self._sub:bool = False
		self._turbo:bool = False
		self._user_id:str = UNDEFINED
		self._user_type:str = UNDEFINED
		self._user_name:str = UNDEFINED
		self._room_name:str = UNDEFINED
		self._content:str = UNDEFINED

		self.Channel:"TwitchChannel" = None
		self.Author:"TwitchUser" = None

		# raw data / utils
		self._badge_str:str = UNDEFINED

		try: self.build(raw)
		except: raise AttributeError(raw[:10])

	# utils
	def build(self, raw:str):
		"""
		That runs all the regex
		we start with content because some things need content for a ref
		"""
		search:re.Match

		# _content & _room_name
		search = re.search(ReContent, raw)
		if search != None:
			self._room_name = search.group(1)
			self._content = search.group(2).strip('\r')

		# _user_name
		search = re.search(ReName, raw)
		if search != None:
			self._user_name = search.group(1)

		# _color
		search = re.search(ReColor, raw)
		if search != None:
			self._color = search.group(1)

		# _msg_id
		search = re.search(ReMsgID, raw)
		if search != None:
			self._msg_id = search.group(1)

		# _user_display_name
		search = re.search(ReDisplayName, raw)
		if search != None:
			self._user_display_name = search.group(1)

		# _room_id
		search = re.search(ReRoomID, raw)
		if search != None:
			self._room_id = search.group(1)

		# _user_id
		search = re.search(ReUserID, raw)
		if search != None:
			self._user_id = search.group(1)

		# _user_type
		search = re.search(ReUserType, raw)
		if search != None:
			self._user_type = search.group(1)

		# _sub
		search = re.search(ReSub, raw)
		if search != None:
			self._sub = True if search.group(1) == "1" else False

		# _mod
		search = re.search(ReMod, raw)
		if search != None:
			self._mod = True if search.group(1) == "1" else False

		# _turbo
		search = re.search(ReTurbo, raw)
		if search != None:
			self._turbo = True if search.group(1) == "1" else False

		# _emotes
		search = re.search(ReEmotes, raw)
		if search != None:
			self.getEmotes( search.group(1) )

		# _badges
		search:re.Match = re.search(ReBadges, raw)
		if search != None:
			self.getBadges( search.group(1) )

	def getEmotes(self, emotes_str:str) -> None:
		# 25:0-4,6-10,12-16,24-28/1902:18-22,30-34

		if not emotes_str: return
		self._emote_str = emotes_str

		emote_str_list:List[str] = emotes_str.split("/")
		for emote_str in emote_str_list:
			Emo:Emote = Emote(emote_str, self.content)
			self._emotes.append( Emo )

	def getBadges(self, badges_str:str) -> None:
		# moderator/1,premium/1

		if not badges_str: return
		self._badge_str = badges_str

		badge_str_list:List[str] = badges_str.split(",")
		for badge_str in badge_str_list:
			Bad:Badge = Badge( badge_str )
			self._badges.append( Bad )

	# props
	@property
	def badges(self) -> List[Badge]:
		return self._badges

	@property
	def color(self) -> str or None:
		if self._color is not UNDEFINED:
			return str(self._color)
		else:
			return None

	@property
	def user_display_name(self) -> str:
		return str(self._user_display_name or "")
	@property
	def display_name(self) -> str:
		return str(self._user_display_name or "")

	@property
	def emotes(self) -> List[Emote]:
		return self._emotes

	@property
	def msg_id(self) -> str:
		return str(self._msg_id or "")
	@property
	def id(self) -> str:
		return str(self._msg_id or "")

	@property
	def mod(self) -> bool:
		return bool(self._mod)

	@property
	def room_id(self) -> str:
		return str(self._room_id or "")
	@property
	def channel_id(self) -> str:
		return str(self._room_id or "")

	@property
	def sub(self) -> bool:
		return bool(self._sub)

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
	def user_name(self) -> str:
		return str(self._user_name or "")

	@property
	def room_name(self) -> str:
		return str(self._room_name or "")
	@property
	def channel_name(self) -> str:
		return str(self._room_name or "")

	@property
	def content(self) -> str:
		return str(self._content or "")
