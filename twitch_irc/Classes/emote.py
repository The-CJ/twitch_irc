from typing import List
from .undefined import UNDEFINED

class Emote(object):
	"""
	There is a Emote class for every different emote in a message, so:

	25:0-4,6-10,12-16,24-28

	4 emotes whould make 1 same in 4 positions
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} name='{self.name}'>"

	def __str__(self):
		return self.name

	def __init__(self, emote_str:str or None, message_content:str or None):
		self._emote_id:str = UNDEFINED
		self._count:int = 0
		self._name:str = UNDEFINED
		self._positions:List[dict] = []

		if (emote_str != None) and (message_content != None):
			try:
				self.build(emote_str, message_content)
			except:
				raise AttributeError(emote_str)

	def compact(self) -> dict:
		d:dict = {}
		d["emote_id"] = self.emote_id
		d["count"] = self.count
		d["name"] = self.name
		d["positions"] = self.positions
		return d

	# utils
	def build(self, emote_str:str, message_content:str) -> None:
		self._emote_id, position_str = emote_str.split(':', 1)

		for single_position_str in position_str.split(","):
			self._count += 1
			start, end = single_position_str.split("-")
			self._positions.append( {"start":start, "end":end} )

		first_emote_pos:dict = self.positions[0]

		start:int = int(first_emote_pos["start"])
		end:int = int(first_emote_pos["end"])

		self._name = message_content[ start:end+1 ]

	# props
	@property
	def id(self) -> str:
		return str(self._emote_id or "")
	@property
	def emote_id(self) -> str:
		return str(self._emote_id or "")

	@property
	def count(self) -> int:
		return int(self._count or 1)

	@property
	def name(self) -> str:
		return str(self._name or "")

	@property
	def pos(self) -> List[dict]:
		return self._positions
	@property
	def positions(self) -> List[dict]:
		return self._positions
