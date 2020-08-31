from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .channel import Channel as TwitchChannel
    from .user import User as TwitchUser

import re
from .structure import UserNoticeStructure
from .undefined import UNDEFINED

from ..Utils.regex import ReMsgParamProfileImageURL, ReMsgParamViewerCount


class Raid(UserNoticeStructure):
	"""
	So rituals are a new(?) thing in twitch and they may appear on multiple channel and or user related events,
	however, currently its only used in one case, the 'new_chatter' event.
	More might come at some point.
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} channel='{self.room_name}' event='{self.ritual_name}'>"

	def __init__(self, raw:str or None):
		# new tags (ordered)
		self._msg_param_profileImageURL:str = UNDEFINED
		self._msg_param_viewerCount:int = UNDEFINED

		# classes
		self.Channel:"TwitchChannel" = None
		self.User:"TwitchUser" = None

		if raw != None:
			try:
				super().__init__(raw)
				self.raidBuild(raw)
			except:
				raise AttributeError(raw)

	# utils
	def compact(self) -> dict:
		d:dict = super().compact()
		d["profile_image_url"] = self.profile_image_url
		d["viewer_count"] = self.viewer_count
		d["Channel"] = self.Channel
		d["User"] = self.User
		return d

	def raidBuild(self, raw:str):
		search:re.Match

		# _msg_param_profileImageURL
		search = re.search(ReMsgParamProfileImageURL, raw)
		if search != None:
			self._msg_param_profileImageURL = search.group(1)

		# _msg_param_viewerCount
		search = re.search(ReMsgParamViewerCount, raw)
		if search != None:
			self._msg_param_viewerCount = search.group(1)

	# extra props
	@property
	def profile_image_url(self) -> str:
		return str(self._msg_param_profileImageURL or "")

	@property
	def viewer_count(self) -> int:
		return int(self._msg_param_viewerCount or 0)
