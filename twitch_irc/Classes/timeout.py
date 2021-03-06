from typing import Optional
import re
from .channel import Channel
from .user import User

from ..Utils.regex import (
	ReBanDuration, ReRoomID, ReTargetUserID,
	ReTMISendTS, ReRoomName, ReContent
)

class Timeout(object):
	"""
	This class is is something like a "testing" class,
	on every CLEARCHAT event, we try to make a Timeout class,

	if this resulting class don't have a valid duration field, its a ban
	if there is no valid target_user_id it a Clear event.

	All of this should be handled by the handleClearChat() function in Utils/handler.py
	However a valid Timeout Class should have a user and a channel class attached to it.
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} channel='{self.room_id}' user='{self.target_user_id}' duration={self.duration}s>"

	def __init__(self, raw:Optional[str]):

		self._ban_duration:Optional[int] = None
		self._room_id:Optional[str] = None
		self._target_user_id:Optional[str] = None
		self._tmi_sent_ts:Optional[str] = None
		self._room_name:Optional[str] = None
		self._user_name:Optional[str] = None

		self.User:Optional[User] = None
		self.Channel:Optional[Channel] = None

		if raw:
			try:
				self.build(raw)
			except:
				raise AttributeError(raw)

	def compact(self) -> dict:
		d:dict = dict()
		d["ban_duration"] = self.ban_duration
		d["room_id"] = self.room_id
		d["target_user_id"] = self.target_user_id
		d["user_name"] = self.user_name
		d["tmi_sent_ts"] = self.tmi_sent_ts
		d["room_name"] = self.room_name
		d["User"] = self.User
		d["Channel"] = self.Channel
		return d

	# utils
	def build(self, raw:str) -> None:
		"""
		generated by a CLEARCHAT event, like this

		Ban: @room-id=94638902;target-user-id=67664971;tmi-sent-ts=1596404852076 :tmi.twitch.tv CLEARCHAT #phaazebot :the__cj
		Timeout: @ban-duration=600;room-id=94638902;target-user-id=67664971;tmi-sent-ts=1596404919791 :tmi.twitch.tv CLEARCHAT #phaazebot :the__cj
		Clear: @room-id=94638902;tmi-sent-ts=1596203495549 :tmi.twitch.tv CLEARCHAT #phaazebot
		"""

		# _ban_duration
		search:re.Match = re.search(ReBanDuration, raw)
		if search:
			self._ban_duration = int(search.group(1))

		# _room_id
		search = re.search(ReRoomID, raw)
		if search:
			self._room_id = search.group(1)

		# _target_user_id
		search = re.search(ReTargetUserID, raw)
		if search:
			self._target_user_id = search.group(1)

		# _tmi_sent_ts
		search = re.search(ReTMISendTS, raw)
		if search:
			self._tmi_sent_ts = search.group(1)

		# _room_name
		search = re.search(ReRoomName, raw)
		if search:
			self._room_name = search.group(1)

		# _user_name
		search = re.search(ReContent, raw)
		if search:
			self._user_name = search.group(1)

	# props
	@property
	def ban_duration(self) -> int:
		return int(self._ban_duration or 0)

	@property
	def duration(self) -> int:
		return int(self._ban_duration or 0)

	@property
	def room_id(self) -> str:
		return str(self._room_id or "")

	@property
	def channel_id(self) -> str:
		return str(self._room_id or "")

	@property
	def target_user_id(self) -> str:
		return str(self._target_user_id or "")

	@property
	def user_name(self) -> str:
		return str(self._user_name or "")

	@property
	def tmi_sent_ts(self) -> str:
		return str(self._tmi_sent_ts or "")

	@property
	def room_name(self) -> str:
		return str(self._room_name or "")

	@property
	def channel_name(self) -> str:
		return str(self._room_name or "")

class Ban(Timeout):
	"""
	A simple subclass of a timeout, because a timeout without duration, is indeed a ban
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} channel='{self.room_id}' user='{self.target_user_id}'>"

	def __init__(self, Out:Timeout):

		super().__init__(None)
		self._ban_duration:Optional[int] = None
		self._room_id:str = Out.room_id
		self._target_user_id:str = Out.target_user_id
		self._tmi_sent_ts:str = Out.tmi_sent_ts
		self._room_name:str = Out.room_name
		self._user_name:str = Out.user_name

	def compact(self) -> dict:
		d:dict = super().compact()
		d.pop("ban_duration", None)
		return d
