import re
from .undefined import UNDEFINED
from ..Utils.regex import ReBadgeParts

class Badge(object):
	"""
	There is a Badge class for every different badge a user currently shows in a message
	means a user can in theory have more badges, like Turbo and Prime, but only one is shown
	Example string:
		moderator/1

	There is a special case for Tier 2 and 3 Subs, the version will be something like 3024
	which means Tier 3, for 24 months, just split at the 0
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

	def compact(self) -> dict:
		d:dict = {}
		d["name"] = self.name
		d["version"] = self.version
		return d

	# utils
	def build(self, s:str) -> None:
		Match:re.Match = re.match(ReBadgeParts, s)
		if Match:
			self._name = Match.group(1) or ""
			self._version = Match.group(2) or ""

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
