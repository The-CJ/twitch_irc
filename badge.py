

class Badge(object):
	"""
	There is a Emote class for every different emote in a message, so:

	`badge_str` = type :: str

	moderator/1
	"""
	def __str__(self):
		return str(self.name) + "/" + str(self.version)

	def __init__(self, badge_str):
		self.badge_str = badge_str

		self.name = None			# str
		self.version = 0			# int

		self.process()
		del self.badge_str

	def process(self):
		splited = self.badge_str.split('/')

		self.name = str(splited[0]) if len(splited) > 0 else None
		self.version = int(splited[1]) if len(splited) > 1 else None
