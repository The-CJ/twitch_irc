import re

# Includes a precompiled re objects for every IRC event

RePing:"re.Pattern" = re.compile(r"^PING.*")
ReWrongAuth:"re.Pattern" = re.compile(r'^:tmi\.twitch\.tv NOTICE \* :Login authentication failed.*')
ReChannelUpdate:"re.Pattern" = re.compile(r"^@.+:tmi\.twitch\.tv ROOMSTATE #.+")

ReOnReady:"re.Pattern" = re.compile(r"^:tmi\.twitch\.tv 001.*")
ReOnMemberJoin:"re.Pattern" = re.compile(r"^.+\.tmi\.twitch\.tv JOIN #.+")
ReOnMemberLeft:"re.Pattern" = re.compile(r"^.+\.tmi\.twitch\.tv PART #.+")
ReOnMessage:"re.Pattern" = re.compile(r"^@.+\.tmi\.twitch\.tv PRIVMSG #.+")

class User(object):
	name = re.compile(r"^:(.+?)!")
	channel_name = re.compile(r"(JOIN|PART) #(\w+)")

class Message(object):
	badges_str = re.compile(r"badges=(.*?)[; ]")
	color = re.compile(r"color=#(.*?)[; ]")
	display_name = re.compile(r"display-name=(.+?)[; ]")
	name = re.compile(r"!(.+?)@")
	emotes_str = re.compile(r"emotes=(.*?)[; ]")
	room_id = re.compile(r"room-id=(.+?)[; ]")
	room_name = re.compile(r"PRIVMSG #(.+?) :")
	user_id = re.compile(r"user-id=(.+?)[; ]")
	user_type = re.compile(r"user-type=(.*?)[; ]")
	sub = re.compile(r"subscriber=(0|1)[; ]")
	mod = re.compile(r"mod=(0|1)[; ]")
	turbo = re.compile(r"turbo=(0|1)[; ]")
	content = re.compile(r"PRIVMSG #.+? :(.+)")
