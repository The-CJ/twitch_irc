import re

class User(object):
	"""This class represents a user like on a event on join or left,

		`raw_data` = type :: str

		:phaazebot!phaazebot@phaazebot.tmi.twitch.tv JOIN #phaazebot

		into a usable class and adds it to the bots self.channel list
	"""

	def __init__(self, raw_data, main_data=None):
		self.raw = raw_data			# str

		self.name = None 			# str
		self.id = None				# str | added at the first message of user (is not given on join/part)
		self.channel_name = None	# str
		self.channel = None			# object :: Channel

		self.process()
		del self.raw

	def process(self):

		#name
		search = re.search(r'^:(.+?)!', self.raw)
		if search != None:
			self.name = str( search.group(1) )

		search = re.search(r' (JOIN|LEFT) #(\w+)', self.raw)
		if search != None:
			self.channel_name = str( search.group(2) )

