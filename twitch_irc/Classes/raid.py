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
	Raiding means, a another channel just gone offline and brings the viewsers from there, to this channel.
	Raids are nearly the same as a host... but eee... i dunno.

	Example:
	```
	@badge-info=subscriber/8;badges=subscriber/6,partner/1;color=#696969;display-name=The__CJ;emotes=;flags=;id=4e016d38-6c1e-41ec-8775-5541a517d2a6;login=The__CJ;mod=1;msg-id=raid;msg-param-displayName=The__CJ;msg-param-login=the__cj;msg-param-profileImageURL=https://static-cdn.jtvnw.net/jtv_user_pictures/abcdefg.png;msg-param-viewerCount=1234;room-id=94638902;subscriber=1;system-msg=1234\sraiders\sfrom\sThe__CJ\shave\sjoined!;tmi-sent-ts=1598924134689;user-id=67664971;user-type= :tmi.twitch.tv USERNOTICE #phaazebot
	```
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} from='{self.login}' amount='{self.viewer_count}'>"

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
