import re
from .undefined import UNDEFINED

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

	def __init__(self, badge_str:str or None):
		self._name:str = UNDEFINED
		self._version:str = UNDEFINED

		if badge_str != None:
			try:
				self.build(badge_str)
			except:
				raise AttributeError(badge_str)

	# utils
	def build(self, s:str) -> None:
		Match:re.Match = re.match(BadgeRe, s)
		if Match:
			self._name = Match.group("name") or ""
			self._version = Match.group("version") or ""

	# props
	@property
	def name(self) -> str:
		return str(self._name or "")

	@property
	def version(self) -> int:
		if not self._version:
			return 1

		if not self._version.isdigit():
			return 1

		return int(self._version)
