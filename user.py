class User(object):
	"""This class represents a user like on a event on join or left,

		`raw_data` = type :: str

		:phaazebot!phaazebot@phaazebot.tmi.twitch.tv JOIN #phaazebot

		into a usable class and adds it to the bots self.channel list
	"""

	def __init__(self, raw_data):
		self.raw = raw_data				# str

		self.name = None 				# str
		self.channel = None				# str

