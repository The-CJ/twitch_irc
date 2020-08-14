from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from .channel import Channel as TwitchChannel
    from .user import User as TwitchUser

import re
from .emote import Emote
from .badge import Badge
from .undefined import UNDEFINED

ReBadgeInfo = re.compile(r"[@; ]badge-info=(\S*?)[; ]")
ReBadges:"re.Pattern" = re.compile(r"[@; ]badges=(\S*?)[; ]")
ReLogin:"re.Pattern" = re.compile(r"[@; ]login=(\S*?)[; ]")
ReColor:"re.Pattern" = re.compile(r"[@; ]color=#([0-9a-fA-F]*?)[; ]")
ReDisplayName:"re.Pattern" = re.compile(r"[@; ]display-name=(\S*?)[; ]")
ReEmotes:"re.Pattern" = re.compile(r"[@; ]emotes=([0-9:,-]*?)[; ]")
ReMsgID:"re.Pattern" = re.compile(r"[@; ]id=([A-Za-z0-9-]*?)[; ]")
ReMod:"re.Pattern" = re.compile(r"[@; ]mod=(0|1)[; ]")
ReCumulativeMonths:"re.Pattern" = re.compile(r"[@; ]msg-param-cumulative-months=(\d*?)[; ]")
ReMonths:"re.Pattern" = re.compile(r"[@; ]msg-param-months=(\d*?)[; ]")
ReShareStreak:"re.Pattern" = re.compile(r"[@; ]msg-param-should-share-streak=(\d*?)[; ]")
ReSubPlanName:"re.Pattern" = re.compile(r"[@; ]msg-param-sub-plan-name=(\S*?)[; ]")
ReSubPlan:"re.Pattern" = re.compile(r"[@; ]msg-param-sub-plan=(\S*?)[; ]")
ReRoomID:"re.Pattern" = re.compile(r"[@; ]room-id=(\d*?)[; ]")
ReSystemMsg:"re.Pattern" = re.compile(r"[@; ]system-msg=(\S*?)[; ]")
ReTMISendTS:"re.Pattern" = re.compile(r"[@; ]tmi-sent-ts=(\d*?)[; ]")
ReUserID:"re.Pattern" = re.compile(r"[@; ]user-id=(\d*?)[; ]")
ReUserType:"re.Pattern" = re.compile(r"[@; ]user-type=(\S*?)[; ]")
ReRoomName:"re.Pattern" = re.compile(r"[@; ]USERNOTICE #(\S*?)([; ]|$)")
ReContent:"re.Pattern" = re.compile(r"[@; ]USERNOTICE #(\S+?) :(.+)")

### Resub
# @badge-info=subscriber/3;
# badges=subscriber/3;
# color=;
# display-name=chischi90;
# emotes=;
# id=3cf1ea58-36c3-4350-8135-2e0b1bbf4590;
# login=chischi90;
# mod=0;
# msg-id=resub;
# msg-param-cumulative-months=3;
# msg-param-months=0;
# msg-param-should-share-streak=0;
# msg-param-sub-plan-name=Schnittchen;
# msg-param-sub-plan=1000;
# room-id=21991090;
# subscriber=1;
# system-msg=chischi90\ssubscribed\sat\sTier\s1.\sThey've\ssubscribed\sfor\s3\smonths!;
# tmi-sent-ts=1597401954859;
# user-id=492245103;
# user-type= :tmi.twitch.tv USERNOTICE #pietsmiet :hey leute

class Sub(object):
	"""
	This Class represents a sub, for simpler use there is also a GiftSub and a ReSub class, because duh
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} channel='{self.room_name}' user='{self.user_name}'>"

	def __init__(self, raw:str or None):
		self._badges_info:List[Badge] = []
		self._badges:List[Badge] = []
		self._color:str = UNDEFINED
		self._user_display_name:str = UNDEFINED
		self._emotes:List[Emote] = []
		self._msg_id:str = UNDEFINED
		self._mod:bool = UNDEFINED
		self._cumulative_months:int = UNDEFINED
		self._months:int = UNDEFINED
		self._should_share_streak:bool = UNDEFINED
		self._sub_plan_name:str = UNDEFINED
		self._sub_plan:str = UNDEFINED
		self._room_id:str = UNDEFINED
		self._system_msg:str = UNDEFINED
		self._tmi_sent_ts:str = UNDEFINED
		self._user_id:str = UNDEFINED
		self._user_type:str = UNDEFINED
		self._user_name:str = UNDEFINED
		self._room_name:str = UNDEFINED
		self._content:str = UNDEFINED

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

	# utils
	def build(self, raw:str):
		"""
		That runs all the regex
		we start with content because some things need content for a ref
		"""
		search:re.Match

		# _room_name
		search = re.search(ReRoomName, raw)
		if search != None:
			self._room_name = search.group(1)

		# _user_name
		search = re.search(ReLogin, raw)
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

		# _tmi_sent_ts
		search = re.search(ReTMISendTS, raw)
		if search != None:
			self._tmi_sent_ts = search.group(1)

		# _mod
		search = re.search(ReMod, raw)
		if search != None:
			self._mod = True if search.group(1) == "1" else False

		# _cumulative_months
		search = re.search(ReCumulativeMonths, raw)
		if search != None:
			self._cumulative_months = search.group(1)

		# _months
		search = re.search(ReMonths, raw)
		if search != None:
			self._months = search.group(1)

		# _should_share_streak
		search = re.search(ReShareStreak, raw)
		if search != None:
			self._should_share_streak = True if search.group(1) == "1" else False

		# _sub_plan_name
		search = re.search(ReSubPlanName, raw)
		if search != None:
			self._sub_plan_name = search.group(1)

		# _sub_plan
		search = re.search(ReSubPlan, raw)
		if search != None:
			self._sub_plan = search.group(1)

		# _system_msg
		search = re.search(ReSystemMsg, raw)
		if search != None:
			self._system_msg = search.group(1)
			self._system_msg = self._system_msg.replace("\:", ';')
			self._system_msg = self._system_msg.replace("\s", ' ')
			self._system_msg = self._system_msg.replace("\\\\", '\\')

		# _emotes
		search = re.search(ReEmotes, raw)
		if search != None:
			self.buildEmotes( search.group(1) )

		# _badges
		search:re.Match = re.search(ReBadges, raw)
		if search != None:
			self.buildBadges( search.group(1) )

		# _badges_info
		search:re.Match = re.search(ReBadgeInfo, raw)
		if search != None:
			self.buildBadgeInfo( search.group(1) )

	def buildEmotes(self, emotes_str:str) -> None:
		# 25:0-4,6-10,12-16,24-28/1902:18-22,30-34

		if not emotes_str: return
		self._emote_str = emotes_str

		emote_str_list:List[str] = emotes_str.split("/")
		for emote_str in emote_str_list:
			Emo:Emote = Emote(emote_str, self.content)
			self._emotes.append( Emo )

	def buildBadges(self, badges_str:str) -> None:
		# moderator/1,premium/1

		if not badges_str: return
		self._badge_str = badges_str

		badge_str_list:List[str] = badges_str.split(",")
		for badge_str in badge_str_list:
			Bad:Badge = Badge( badge_str )
			self._badges.append( Bad )

	def buildBadgeInfo(self, badge_info_str:str) -> None:
		# subscriber/15,somethingelse/5
		# pretty much the same as a normal badge, except it's more detailed
		# there is a badge for subscriber/24 and in info is the exact value like subscriber/26

		if not badge_info_str: return
		self._badge_info_str = badge_info_str

		badge_str_list:List[str] = badge_info_str.split(",")
		for badge_str in badge_str_list:
			Bad:Badge = Badge( badge_str )
			self._badges_info.append( Bad )

	# props
	@property
	def badges_info(self) -> List[Badge]:
		return self._badges_info

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
	def cumulative_months(self) -> int:
		return int(self._cumulative_months or 0)

	@property
	def months(self) -> int:
		return int(self._months or 0)

	@property
	def should_share_streak(self) -> bool:
		return bool(self._should_share_streak)

	@property
	def sub_plan_name(self) -> str:
		return str(self._sub_plan_name or "")

	@property
	def sub_plan(self) -> str:
		return str(self._sub_plan or "")

	@property
	def room_id(self) -> str:
		return str(self._room_id or "")
	@property
	def channel_id(self) -> str:
		return str(self._room_id or "")

	@property
	def system_msg(self) -> str:
		return str(self._system_msg or "")

	@property
	def tmi_sent_ts(self) -> str:
		return str(self._tmi_sent_ts or "")

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
	def login(self) -> str:
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

class ReSub(Sub):
	def __init__(self):
		super().__init__()

class GiftSub(Sub):
	def __init__(self):
		super().__init__()
