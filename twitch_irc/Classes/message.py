from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .channel import Channel as TwitchChannel
    from .user import User as TwitchUser

import re
from .emote import Emote
from .badge import Badge

ReBadges:"re.Pattern" = re.compile(r"badges=(.*?)[; ]")
ReColor:"re.Pattern" = re.compile(r"color=#(.*?)[; ]")
ReDisplayName:"re.Pattern" = re.compile(r"display-name=(.+?)[; ]")
ReName:"re.Pattern" = re.compile(r"!(.+?)@")
ReEmotes:"re.Pattern" = re.compile(r"emotes=(.*?)[; ]")
ReRoomID:"re.Pattern" = re.compile(r"room-id=(.+?)[; ]")
ReRoomName:"re.Pattern" = re.compile(r"PRIVMSG #(.+?) :")
ReUserID:"re.Pattern" = re.compile(r"user-id=(.+?)[; ]")
ReUserType:"re.Pattern" = re.compile(r"user-type=(.*?)[; ]")
ReSub:"re.Pattern" = re.compile(r"subscriber=(0|1)[; ]")
ReMod:"re.Pattern" = re.compile(r"mod=(0|1)[; ]")
ReTurbo:"re.Pattern" = re.compile(r"turbo=(0|1)[; ]")
ReContent:"re.Pattern" = re.compile(r"PRIVMSG #.+? :(.+)")

class Message(object):
	"""
		This class is generated when a user is sending a message, it turns raw data like:

		@
		badges=moderator/1,premium/1;
		color=#696969;
		display-name=The__CJ;
		emotes=25:6-10;
		id=13e484e8-1d0d-44c0-8b1e-03d76b636688;
		mod=1;
		room-id=94638902;
		subscriber=0;
		tmi-sent-ts=1525706672840;
		turbo=0;
		user-id=67664971;
		user-type=mod
		:the__cj!the__cj@the__cj.tmi.twitch.tv
		PRIVMSG #phaazebot :Hello Kappa /

		into a usable class
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} channel='{self.channel_name}' user='{self.user_name}'>"

	def __str__(self):
		return self.content

	def __init__(self, raw:str):
		self.badges:list = list()
		self.color:str = None
		self.user_name:str = None
		self.user_display_name:str = None
		self.emotes:list = list()
		self.mod:bool = False
		self.sub:bool = False
		self.channel_id:str = None
		self.channel_name:str = None
		self.user_id:str = None
		self.user_type:str = None
		self.turbo:bool = False
		self.content:str = None

		self.Channel:"TwitchChannel" = None
		self.Author:"TwitchUser" = None

		self.build(raw)

	def build(self, raw:str):
		# badges
		search = re.search(ReBadges, raw)
		if search != None:
			self.getBadges( search.group(1) )

		#color
		search = re.search(ReColor, raw)
		if search != None:
			self.color = search.group(1)

		#user_display_name
		search = re.search(ReDisplayName, raw)
		if search != None:
			self.user_display_name = search.group(1)

		#user_name
		search = re.search(ReName, raw)
		if search != None:
			self.user_name = search.group(1)

		#emotes
		search = re.search(ReEmotes, raw)
		if search != None:
			self.getEmotes( search.group(1) )

		#room_id | channel_id
		search = re.search(ReRoomID, raw)
		if search != None:
			self.channel_id = search.group(1)

		#room_name | channel_name
		search = re.search(ReRoomName, raw)
		if search != None:
			self.channel_name = search.group(1)

		#user_id
		search = re.search(ReUserID, raw)
		if search != None:
			self.user_id = search.group(1)

		#user_type
		search = re.search(ReUserType, raw)
		if search != None:
			self.user_type = search.group(1)

		#sub
		search = re.search(ReSub, raw)
		if search != None:
			self.sub = True if search.group(1) == "1" else False

		#mod
		search = re.search(ReMod, raw)
		if search != None:
			self.mod = True if search.group(1) == "1" else False

		#turbo
		search = re.search(ReTurbo, raw)
		if search != None:
			self.turbo = True if search.group(1) == "1" else False

		#content
		search = re.search(ReContent, raw)
		if search != None:
			self.content = search.group(1).strip('\r')

	def getEmotes(self, emotes_str:str) -> None:
		# 25:0-4,6-10,12-16,24-28/1902:18-22,30-34

		if not emotes_str: return

		emote_str_list:list = emotes_str.split("/")
		for emote_str in emote_str_list:
			Emo = Emote(emote_str, self.content)
			self.emotes.append( Emo )

	def getBadges(self, badges_str:str) -> None:
		# moderator/1,premium/1

		if not badges_str: return

		badge_str_list:list = badges_str.split(",")
		for badge_str in badge_str_list:
			Bad = Badge( badge_str )
			self.badges.append(Bad)



