import re

BadgeRe:"re.Pattern" = re.compile(r"^(?P<name>[^/]+)/?(?P<version>\d+)?$")

class Badge(object):
	"""
		There is a Badge class for every different emote in a message
		Example string:
			moderator/1
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} name='{self.name}' version='{self.version}'>"

	def __str__(self):
		return f"{self.name}/{self.version}"

	def __init__(self, badge_str:str):
		self.name:str = None
		self.version:int = 0

		self.build(badge_str)

	def build(self, s:str) -> None:
		Match:re.Match = re.match(BadgeRe, s)
		if Match:
			self.name = Match.group("name")
			self.version = int( Match.group("version") )
