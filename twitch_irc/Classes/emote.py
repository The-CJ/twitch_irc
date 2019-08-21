class Emote(object):
	""" There is a Emote class for every different emote in a message, so:

		25:0-4,6-10,12-16,24-28

		4 emotes whould make 1 same in 4 positions
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} name='{self.name}'>"

	def __str__(self):
		return self.name

	def __init__(self, emote_str:str, message_content:str):
		self.emote_id:str = None
		self.count:int = 0
		self.name:str = None
		self.positions:list = list()

		self.build(emote_str, message_content)

	def build(self, emote_str:str, message_content:str) -> None:
		self.emote_id, pos_str = self.emote_str.split(':', 1)

		for pos_str in pos_str.split(","):
			self.count += 1
			start, end = pos_str.split("-")
			self.positions.append( dict(start=start, end=end) )

		first_emote_pos:dict = self.positions[0]

		start:int = int(first_emote_pos["start"])
		end:int = int(first_emote_pos["end"])

		self.name = message_content[ start:end+1]
