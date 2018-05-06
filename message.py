class Message(object):
	"""This class is generated when a user is sending a message, it turns raw data like:

		@badges=moderator/1,premium/1;color=#696969;display-name=The__CJ;emotes=;id=259fbe61-d216-46fc-98c3-f7e80dfed551;mod=1;room-id=94638902;subscriber=0;tmi-sent-ts=1525621898093;turbo=0;user-id=67664971;user-type=mod :the__cj!the__cj@the__cj.tmi.twitch.tv PRIVMSG #phaazebot :hello?

		into a usable class
	"""

	def __init__(self, raw_data):
		pass