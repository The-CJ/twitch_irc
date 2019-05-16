

class Emote(object):
	""" There is a Emote class for every different emote in a message, so:

		`emote_str` = type :: str
		`message_content` :: str

		25:0-4,6-10,12-16,24-28

		would make 4 emotes into a classes:

	"""
	def __str__(self):
		return self.name

	def __init__(self, emote_str, message_content):
		self.emote_str = emote_str
		self.search_str = message_content

		self.id = None				# str
		self.count = 0				# int
		self.name = None			# str
		self.positions = list()		# list :: dict

		self.process()
		del self.emote_str
		del self.search_str

	def process(self):
		self.id, pos_str = self.emote_str.split(':', 1)

		for emote_str in pos_str.split(","):
			self.count += 1
			start, end = emote_str.split("-")
			self.positions.append(dict(start=start, end=end))

		first_emote_pos = self.positions[0]

		from_ = int(first_emote_pos["start"])
		to_ = int(first_emote_pos["end"])

		self.name = self.search_str[from_:to_+1]
