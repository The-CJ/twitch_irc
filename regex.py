import re

class Regex(object):
	""" Includes a precompiled re objects for every IRC event  """

	ping = re.compile(r'^PING')
	channel_update = re.compile(r"^@.+:tmi\.twitch\.tv ROOMSTATE #.+")

	on_ready = re.compile(r"^:tmi\.twitch\.tv 001.*")
	on_member_join = re.compile(r"^.+\.tmi\.twitch\.tv JOIN #.+")
	on_member_left = re.compile(r"^.+\.tmi\.twitch\.tv LEFT #.+")
	on_message = re.compile(r"^@.+\.tmi\.twitch\.tv PRIVMSG #.+")

	class Channel(object):
		broadcaster_lang = re.compile(r"broadcaster-lang=(.*?)[; ]")
		emote_only = re.compile(r"emote-only=(1|0)[; ]")
		folloers_only = re.compile(r"followers-only=(\d+?|-1)[; ]")
		r9k = re.compile(r"r9k=(1|0)[; ]")
		rituals = re.compile(r"rituals=(1|0)[; ]")
		room_id = re.compile(r"room-id=(\d+?)[; ]")
		slow = re.compile(r"slow=(\d+?)[; ]")
		subs_only = re.compile(r"subs-only=(1|0)[; ]")
		room_name = re.compile(r"ROOMSTATE #(\w+)")

