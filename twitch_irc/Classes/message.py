from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
	from .client import Client as TwitchClient
	from .channel import Channel as TwitchChannel
	from .user import User as TwitchUser

import re
from .structure import BasicEventStructure
from ..Utils.regex import (
	ReAction, ReUserName, ReBits,
	ReReplyParentDisplayName, ReReplyParentMsgBody, ReReplyParentMsgID,
	ReReplyParentUserID, ReReplyParentUserLogin, ReEmoteOnly,
	ReMsgID
)

class Message(BasicEventStructure):
	"""
	This class is generated when a user is sending a message to a channel,
	this message may also be a reply to someone, or a action. (You know, these /me things)

	Example raw:
	```
	@badge-info=subscriber/39;badges=broadcaster/1,subscriber/3012,premium/1;color=#696969;display-name=The__CJ;emotes=25:17-21;flags=;id=0b85e5f4-4720-45f0-9f05-8cfa4f1a0de4;mod=0;msg-id=highlighted-message;reply-parent-display-name=Phaazebot;reply-parent-msg-body=!\sKappa\sKeepo\sKappaHD;reply-parent-msg-id=ae046cec-718d-47aa-aac5-82cbf591d837;reply-parent-user-id=94638902;reply-parent-user-login=phaazebot;room-id=67664971;subscriber=1;tmi-sent-ts=1599346386783;turbo=0;user-id=67664971;user-type= :the__cj!the__cj@the__cj.tmi.twitch.tv PRIVMSG #the__cj :@Phaazebot Reeee Kappa
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} channel='{self.room_name}' author='{self.user_name}'>"

	def __str__(self):
		return self.content or ""

	def __init__(self, raw:Optional[str]):
		# new tags (ordered)
		self._bits:Optional[int] = None
		self._emote_only:Optional[bool] = None
		self._reply_parent_display_name:Optional[str] = None
		self._reply_parent_msg_body:Optional[str] = None
		self._reply_parent_msg_id:Optional[str] = None
		self._reply_parent_user_id:Optional[str] = None
		self._reply_parent_user_login:Optional[str] = None
		self._user_name:Optional[str] = None

		# other
		self.is_action:bool = False
		self.is_highlight:bool = False
		self.is_reply:bool = False

		# classes
		self.Channel:Optional["TwitchChannel"] = None
		self.Author:["TwitchUser"] = None

		if raw:
			try:
				super().__init__(raw)
				self.messageBuild(raw)
			except:
				raise AttributeError(raw)

	# utils
	def compact(self) -> dict:
		d:dict = super().compact()
		d["content"] = self.content
		d["bits"] = self.bits
		d["_emote_only"] = self._emote_only
		d["is_reply"] = self.is_reply
		d["is_action"] = self.is_action
		d["Channel"] = self.Channel
		d["Author"] = self.Author

		if self.is_reply:
			d["reply_parent_display_name"] = self.reply_parent_display_name
			d["reply_parent_msg_body"] = self.reply_parent_msg_body
			d["reply_parent_msg_id"] = self.reply_parent_msg_id
			d["reply_parent_user_id"] = self.reply_parent_user_id
			d["reply_parent_user_login"] = self.reply_parent_user_login

		return d

	def messageBuild(self, raw:str):
		search:re.Match

		# _bits
		search = re.search(ReBits, raw)
		if search:
			self._bits = search.group(1)

		# _emote_only
		search = re.search(ReEmoteOnly, raw)
		if search:
			self._emote_only = True if search.group(1) == '1' else False

		# _reply_parent_display_name
		search = re.search(ReReplyParentDisplayName, raw)
		if search:
			self._reply_parent_display_name = search.group(1)

		# _reply_parent_msg_body
		search = re.search(ReReplyParentMsgBody, raw)
		if search:
			self._reply_parent_msg_body = self.removeTagChars(search.group(1))

		# _reply_parent_msg_id
		search = re.search(ReReplyParentMsgID, raw)
		if search:
			self._reply_parent_msg_id = search.group(1)

		# _reply_parent_user_id
		search = re.search(ReReplyParentUserID, raw)
		if search:
			self._reply_parent_user_id = search.group(1)

		# _reply_parent_user_login
		search = re.search(ReReplyParentUserLogin, raw)
		if search:
			self._reply_parent_user_login = search.group(1)

		# _user_name
		search = re.search(ReUserName, raw)
		if search:
			self._user_name = search.group(2)

		# check some data other data
		self.checkAction()
		self.checkHighlight()
		self.checkReply()

	def checkAction(self) -> None:
		"""
		Checks if the message is a action,
		action means its a /me message. If it is, change content and set is_action true
		"""
		search:re.Match = re.search(ReAction, self.content)
		if search:
			self.is_action = True
			self._content = search.group(1)

	def checkHighlight(self) -> None:
		"""
		Checks if the message is a highlighted,
		a message is highlighted when the user uses channel points to redeem it.
		"""
		search:re.Match = re.search(ReMsgID, self.content)
		if search and search.group(1) == "highlighted-message":
			self.is_highlight = True

	def checkReply(self) -> None:
		"""
		Checks if the message is a reply to another message
		"""
		if self.reply_parent_msg_id:
			self.is_reply = True

	# funcs
	async def reply(self, cls:"TwitchClient", reply:str) -> None:
		"""
		Fast reply with content to a message,
		requires you to give this function the Client class, don't ask why...
		and a valid content you want to send.

		maybe you wanna add a @{user_name} at the start of the message?
		At least that how i respond to message, but do want you want
		"""
		return await cls.sendMessage(self.room_name, reply)

	# new props
	@property
	def bits(self) -> int:
		return int(self._bits or 0)

	@property
	def emote_only(self) -> bool:
		return bool(self._emote_only)

	@property
	def content(self) -> str:
		# actually not a new prop, but BasicEventStructure don't has a .content, since ._content is used by other classes as a different value
		return str(self._content or "")

	@property
	def reply_parent_display_name(self) -> str:
		return str(self._reply_parent_display_name or "")

	@property
	def reply_parent_msg_body(self) -> str:
		return str(self._reply_parent_msg_body or "")

	@property
	def reply_parent_msg_id(self) -> str:
		return str(self._reply_parent_msg_id or "")

	@property
	def reply_parent_user_id(self) -> str:
		return str(self._reply_parent_user_id or "")

	@property
	def reply_parent_user_login(self) -> str:
		return str(self._reply_parent_user_login or "")

	@property
	def user_name(self) -> str:
		return str(self._user_name or "")
